from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.types import Enum as SQLEnum
from sqlalchemy.orm import reconstructor

from database import Base, SessionLocal
from datetime import datetime, timedelta
from threading import Timer
from typing import Optional
from flask_socketio import SocketIO

from enum import Enum as PyEnum
from game_state import GameState, get_most_recent_game_state
from utils import moves_processing_key, staged_moves_key
from redis_utils import rset, rget, await_empty_counter, rlock, rget_json


class TimerStatus(PyEnum):
    NORMAL = "NORMAL"
    OVERTIME = "OVERTIME"
    PAUSED = "PAUSED"

class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    name = Column(String, nullable=False)

    launched = Column(Boolean, nullable=False, default=False, server_default='f')
    game_over = Column(Boolean, nullable=False, default=False, server_default='f')

    seconds_per_turn = Column(Integer, nullable=True)
    timer_status = Column(SQLEnum(TimerStatus), nullable=False, default=TimerStatus.NORMAL, server_default='NORMAL')
    turn_num = Column(Integer, nullable=False, default=1, server_default='1')
    next_forced_roll_at = Column(Integer, nullable=True)

    @reconstructor
    def init_on_load(self):
        # This method will be called for instances loaded from the database
        # Just here to declare the socketio property.
        self.socketio: SocketIO = None  #type: ignore

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.timestamp(),
        }
       
    def roll_turn_lock_key(self, turn_num):
        return f"roll_turn_lock:{self.id}:{turn_num}"
    
    def accepting_moves(self, turn_num) -> bool:
        """
        Check if this game is accepting client moves.
        i.e. the turn_num is correct and the turn roll has not started
        """
        if self.turn_num != turn_num:
            # Wrong turn number
            print(f"Game {self.id} is not accepting moves for turn_num {turn_num} because we're on turn_num {self.turn_num}")
            return False

        lock_key = self.roll_turn_lock_key(turn_num)
        if rlock(lock_key).locked():
            # Turn is already rolling
            print(f"Game {self.id} is not accepting moves because turn {turn_num} is already rolling")
            return False

        return True
    
    def turn_ended_by_player_key(self, player_num):
        return f"turn_ended_by_player:{self.id}:{player_num}"

    def turn_ended_by_player(self, player_num) -> bool:
        if self.players[player_num].is_bot:
            return True
        ended: str | None = rget(self.turn_ended_by_player_key(player_num))
        assert ended is not None, f"turn_ended_by_player_key {self.turn_ended_by_player_key(player_num)} not set"
        assert ended in ["true", "false"], f"turn_ended_by_player_key {self.turn_ended_by_player_key(player_num)} not set"
        return ended == "true"
    
    def get_turn_ended_all_players(self) -> dict[int, bool]:   
        return {player_num: self.turn_ended_by_player(player_num) for player_num in range(len(self.players))}

    def set_turn_ended_by_player_num(self, player_num, ended: bool, broadcast=True, via_player_input=False) -> None:
        # Don't let manual turn sets go through in mid-roll
        if via_player_input and rlock(self.roll_turn_lock_key(self.turn_num)).locked():
            print(f"Can't set end turn status while turn is rolling {self.id}.")
            return

        rset(self.turn_ended_by_player_key(player_num), "true" if ended else "false")
        if broadcast:
            self.broadcast('turn_end_change', {'player_num': player_num, 'turn_ended': ended})

    def roll_turn_if_needed(self, sess):
        for player_num in range(len(self.players)):
            if not self.turn_ended_by_player(player_num):
                return
        self.roll_turn(sess)

    @property
    def timer_paused(self) -> bool:
        return self.timer_status == TimerStatus.PAUSED  # type: ignore
    
    def pause(self, sess):
        if rlock(self.roll_turn_lock_key(self.turn_num)).locked():
            print(f"Another thread is already rolling turn {self.turn_num} for game {self.id}.")
            return

        # TODO something weird could probably happen if the turn starts rolling in the middle of this function.
        print(f"Pausing game {self.id} turn {self.turn_num}")
        self.timer_status = TimerStatus.PAUSED  # type: ignore
        sess.commit()
        self.broadcast('mute_timer', {'turn_num': self.turn_num})

    @staticmethod
    def get(sess, socketio, game_id: str) -> Optional["Game"]:
        game = sess.query(Game).filter(Game.id == game_id).first()
        if game is None:
            return None
        else:
            game.socketio = socketio
            return game

    def broadcast(self, signal, data=None):
        print(f"broadcasting {signal} to {self.id}")

        self.socketio.emit(
            signal, 
            data or {},
            room=self.id,
        )

    def get_overtime_decline_civs(self) -> list[int]:
        return [player_num for player_num in range(len(self.players)) if self.has_player_declined(player_num, self.turn_num)]

    def _enter_overtime_if_needed(self, sess) -> bool:
        declined_players: set[int] = {player_num for player_num in self.get_overtime_decline_civs() if not self.turn_ended_by_player(player_num)}
        if declined_players:
            print(f"Not rolling turn {self.turn_num} in game {self.id} because player(s) {', '.join(map(str, declined_players))} have declined and not ended turn")
            self.timer_status = TimerStatus.OVERTIME  # type: ignore
            sess.commit()
            self.broadcast("overtime", {"turn_num": self.turn_num})
            for player in range(len(self.players)):
                if player not in declined_players and not self.turn_ended_by_player(player):
                    self.set_turn_ended_by_player_num(player, True)
            return True
        return False

    def roll_turn(self, sess) -> None:
        print(f"rolling turn {self.turn_num} in game {self.id}")

        # Don't roll if there's a person who has declined and not ended turn
        if self._enter_overtime_if_needed(sess):
            return


        lock = rlock(self.roll_turn_lock_key(self.turn_num), expire=60 * 60)
        if lock.acquire(blocking=False):
            try:
                self.broadcast('start_turn_roll')

                # Wait till all active threads have finished, up to 5s
                await_empty_counter(moves_processing_key(self.id, self.turn_num), 5, 0.1)

                # Conceivably a move in the queue caused overtime
                if self._enter_overtime_if_needed(sess):
                    # Release the lock so we can roll the turn again.
                    lock.release()
                    return

                # need to load the game state here, after await_empty_counter on the moves in flight.
                # or else we'll have a stale version.
                game_state: GameState = get_most_recent_game_state(sess, self.id)

                game_state.end_turn(sess)

                if self.seconds_per_turn is not None and not self.game_over and self.turn_num < 200:
                    seconds_until_next_forced_roll: float = int(self.seconds_per_turn) + min(self.turn_num, 30)
                    next_forced_roll_at: float = (datetime.now() + timedelta(seconds=seconds_until_next_forced_roll)).timestamp()

                    self.next_forced_roll_at = next_forced_roll_at  # type: ignore
                    Timer(next_forced_roll_at - datetime.now().timestamp(), 
                        load_and_roll_turn_in_game, 
                        args=[sess, self.socketio, self.id, self.turn_num + 1]).start()
                else:
                    self.next_forced_roll_at = None  # type: ignore

                self.turn_num = self.turn_num + 1  # type: ignore
                if game_state.game_over:
                    self.game_over = True  # type: ignore
                    # TODO should we not even have game_state.game_over?
                self.timer_status = TimerStatus.NORMAL
                sess.commit()
                self.start_turn()
            except Exception as e:
                # Note we only relesae the lock if there's an exception
                # Otherwise we just hold the lock forever
                # Since we only ever want to roll turn once.
                lock.release()
                raise e
        else:
            print(f"Another thread is already rolling turn {self.turn_num} for game {self.game_id}.")

    def start_turn(self) -> None:
        self.broadcast('update')
        for player_num, player in enumerate(self.players):
            if not player.is_bot:
                self.set_turn_ended_by_player_num(player_num, False, broadcast=False)

    def has_player_declined(self, player_num, turn_num) -> bool:
        staged_moves = rget_json(staged_moves_key(self.id, player_num, turn_num)) or []
        for move in staged_moves:
            if move['move_type'] == 'choose_decline_option':
                return True
        return False

def load_and_roll_turn_in_game(sess, socketio, game_id: str, turn_num: int):
    with SessionLocal() as sess:
        full_game = Game.get(sess, socketio, game_id)

        if not full_game:
            raise ValueError(f"Turn Timer expired on nonexistent game id={game_id}")
        
        if turn_num == full_game.turn_num and not full_game.game_over and not full_game.timer_paused:
            full_game.roll_turn(sess)

