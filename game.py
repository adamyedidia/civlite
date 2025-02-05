from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.types import Enum as SQLEnum
from sqlalchemy.orm import reconstructor

from database import Base, SessionLocal
from datetime import datetime, timedelta
from threading import Timer
from typing import Optional, TYPE_CHECKING
from flask_socketio import SocketIO

from enum import Enum as PyEnum
from game_state import GameState
from civ import Civ
from animation_frame import AnimationFrame
from utils import moves_processing_key, staged_moves_key
from redis_utils import rset, rget, rdel, await_empty_counter, rlock, rget_json, rset_json, rkeys

if TYPE_CHECKING:
    from player import Player

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
       
    def player_by_num(self, player_num: int) -> 'Player':
        return [p for p in self.players if p.player_num == player_num].pop()

    def roll_turn_lock_key(self, turn_num):
        return f"roll_turn_lock:{self.id}:{turn_num}"
    
    def _turn_over_key(self, turn_num):
        return f"turn_over_key:{self.id}:{turn_num}"
    
    def accepting_moves(self, turn_num) -> bool:
        """
        Check if this game is accepting client moves.
        i.e. the turn_num is correct and the turn roll has not started
        """
        if self.turn_num != turn_num:
            # Wrong turn number
            print(f"Game {self.id} is not accepting moves for turn_num {turn_num} because we're on turn_num {self.turn_num}")
            return False
        
        lock = rlock(self.roll_turn_lock_key(turn_num), expire=60 * 60)
        if lock.locked():
            print(f"Game {self.id} is not accepting moves because turn {turn_num} is already rolling or over")
            return False
        if rget(self._turn_over_key(turn_num)) == "true":
            # Done rolling
            print(f"Game {self.id} is not accepting moves because turn {turn_num} is already over")
            return False
        return True
    
    def turn_ended_by_player_key(self, player_num):
        return f"turn_ended_by_player:{self.id}:{player_num}"

    def turn_ended_by_player(self, player_num) -> bool:
        if self.player_by_num(player_num).is_bot:
            return True
        ended: str | None = rget(self.turn_ended_by_player_key(player_num))
        assert ended is not None, f"turn_ended_by_player_key {self.turn_ended_by_player_key(player_num)} not set"
        assert ended in ["true", "false"], f"turn_ended_by_player_key {self.turn_ended_by_player_key(player_num)} not set"
        return ended == "true"
    
    def get_turn_ended_all_players(self) -> dict[int, bool]:   
        return {player.player_num: self.turn_ended_by_player(player.player_num) for player in self.players}

    def set_turn_ended_by_player_num(self, player_num, ended: bool, broadcast=True, via_player_input=False) -> None:
        # Don't let manual turn sets go through in mid-roll
        if via_player_input and rlock(self.roll_turn_lock_key(self.turn_num)).locked():
            print(f"Can't set end turn status while turn is rolling {self.id}.")
            return

        rset(self.turn_ended_by_player_key(player_num), "true" if ended else "false")
        if broadcast:
            self.broadcast('turn_end_change', {'player_num': player_num, 'turn_ended': ended})

    def roll_turn_if_needed(self, sess):
        print(f"roll_turn_if_needed {self.id}")
        for player in self.players:
            if not self.turn_ended_by_player(player.player_num):
                print(f"roll_turn_if_needed {self.id}: player {player.player_num} has not ended turn")
                return
        print(f"roll_turn_if_needed {self.id}: all players have ended turn")
        self.roll_turn(sess)

    @property
    def timer_paused(self) -> bool:
        return self.timer_status == TimerStatus.PAUSED
    
    def pause(self, sess):
        if rlock(self.roll_turn_lock_key(self.turn_num)).locked():
            print(f"Another thread is already rolling turn {self.turn_num} for game {self.id}.")
            return

        # TODO something weird could probably happen if the turn starts rolling in the middle of this function.
        print(f"Pausing game {self.id} turn {self.turn_num}")
        self.timer_status = TimerStatus.PAUSED
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
            room=self.id,  # type: ignore
        )

    def get_overtime_decline_civs(self) -> list[int]:
        return [player.player_num for player in self.players if self.has_player_declined(player.player_num, self.turn_num)]

    def _enter_overtime_if_needed(self, sess) -> bool:
        declined_players: set[int] = {player_num for player_num in self.get_overtime_decline_civs() if not self.turn_ended_by_player(player_num)}
        if declined_players:
            print(f"Not rolling turn {self.turn_num} in game {self.id} because player(s) {', '.join(map(str, declined_players))} have declined and not ended turn")
            self.timer_status = TimerStatus.OVERTIME
            sess.commit()
            self.broadcast("overtime", {"turn_num": self.turn_num})
            for player in self.players:
                if player.player_num not in declined_players and not self.turn_ended_by_player(player.player_num):
                    self.set_turn_ended_by_player_num(player.player_num, True)
            return True
        return False

    def roll_turn(self, sess) -> None:
        if self.game_over:
            return
        print(f"rolling turn {self.turn_num} in game {self.id}")

        # Don't roll if there's a person who has declined and not ended turn
        if self._enter_overtime_if_needed(sess):
            return


        lock = rlock(self.roll_turn_lock_key(self.turn_num), expire=60 * 60)
        if lock.acquire(blocking=False):
            try:
                if rget(self._turn_over_key(self.turn_num)) == "true":
                    print(f"not rolling game {self.id} turn {self.turn_num} because it has already rolled.")
                    return

                self.broadcast('start_turn_roll')


                # Wait till all active threads have finished, up to 5s
                await_empty_counter(moves_processing_key(self.id, self.turn_num), 5, 0.1)

                # Conceivably a move in the queue caused overtime
                if self._enter_overtime_if_needed(sess):
                    # Release the lock so we can roll the turn again.
                    lock.release()
                    return

                print(f"Game.roll_turn (game {self.id} turn {self.turn_num}): Reprocessing all moves")
                # need to load the game state here, after await_empty_counter on the moves in flight.
                # or else we'll have a stale version.
                game_state: GameState = self.get_turn_start_game_state(sess)
                player_moves_by_player_num: dict[int, list] = {}
                for player in self.players:
                    player_moves_by_player_num[player.player_num] = rget_json(staged_moves_key(self.id, player.player_num, self.turn_num)) or []
                game_state.load_and_update_from_player_moves(player_moves_by_player_num)

                print(f"Game.roll_turn (game {self.id} turn {self.turn_num}, {game_state.turn_num}): Calling all_bot_moves()")
                game_state.all_bot_moves()

                print(f'Game.roll_turn (game {self.id} turn {self.turn_num}, {game_state.turn_num}): Calling end_turn()')
                game_state.end_turn(sess)

                print(f'Game.roll_turn (game {self.id} turn {self.turn_num}): Setting next_forced_roll_at')
                if self.seconds_per_turn is not None and not self.game_over and self.turn_num < 200:
                    seconds_until_next_forced_roll: float = int(self.seconds_per_turn) + min(self.turn_num, 30)
                    next_forced_roll_at: float = (datetime.now() + timedelta(seconds=seconds_until_next_forced_roll)).timestamp()

                    self.next_forced_roll_at = next_forced_roll_at
                    Timer(next_forced_roll_at - datetime.now().timestamp(), 
                        load_and_roll_turn_in_game, 
                        args=[sess, self.socketio, self.id, self.turn_num + 1]).start()
                else:
                    self.next_forced_roll_at = None
                rset(self._turn_over_key(self.turn_num), "true", ex=7 * 60 * 60)

                self.turn_num = self.turn_num + 1
                if game_state.game_over:
                    self.game_over = True
                    # TODO should we not even have game_state.game_over?
                self.timer_status = TimerStatus.NORMAL
                sess.commit()
                print(f"Game {self.id} finished rolling turn, starting turn {self.turn_num}")
                self.start_turn()

            finally:
                lock.release()
        else:
            print(f"Another thread is already rolling turn {self.turn_num} for game {self.id}.")


    def start_turn(self) -> None:
        self.broadcast('update')
        for player in self.players:
            if not player.is_bot:
                self.set_turn_ended_by_player_num(player.player_num, False, broadcast=False)

    def reset_to_turn(self, turn_num: int, sess):
        for turn in range(turn_num, self.turn_num + 1):
            rlock(self._turn_over_key(turn)).reset()
            for player in self.players:
                rdel(staged_moves_key(self.id, player.player_num, turn))
                rdel(self._staged_game_state_key(player.player_num, turn))
            decline_claimed_lock_key = f"decline-claimed-{self.id}-{turn}-lock"
            rlock(decline_claimed_lock_key).reset()
            decline_claimed_keys_pattern = f"decline-claimed-{self.id}-{turn}-coords-*"
            for key in rkeys(decline_claimed_keys_pattern):
                rdel(key.decode('utf-8'))
        for player in self.players:
            if not player.is_bot:
                self.set_turn_ended_by_player_num(player.player_num, False, broadcast=False)
        self.turn_num = turn_num
        self.next_forced_roll_at = None
        self.timer_status = TimerStatus.PAUSED
        self.game_over = False


        # Now we need to remove all later animation frames from the database

        sess.query(AnimationFrame).filter(AnimationFrame.game_id == self.id).filter(AnimationFrame.turn_num > turn_num).delete()
        sess.commit()



    def has_player_declined(self, player_num, turn_num, count_preempted=True) -> bool:
        staged_moves = rget_json(staged_moves_key(self.id, player_num, turn_num)) or []
        for move in staged_moves:
            if move['move_type'] == 'choose_decline_option':
                if count_preempted or not 'preempted' in move:
                    return True
        return False
    
    def get_turn_start_game_state(self, sess) -> GameState:
        most_recent_game_state_animation_frame = (
            sess.query(AnimationFrame)
            .filter(AnimationFrame.game_id == self.id)
            .filter(AnimationFrame.player_num == None)
            .filter(AnimationFrame.turn_num == self.turn_num)
            .order_by(AnimationFrame.frame_num.desc())
            .first()
        )

        assert most_recent_game_state_animation_frame is not None

        most_recent_game_state = most_recent_game_state_animation_frame.game_state

        return GameState.from_json(most_recent_game_state)

    def _staged_game_state_key(self, player_num: int, turn_num: int) -> str:
        return f'staged_game_state:{self.id}:{player_num}:{turn_num}'

    def _staged_game_state(self, player_num: int) -> GameState | None:
            game_state_json = rget_json(self._staged_game_state_key(player_num, self.turn_num))
            if game_state_json is not None:
                return GameState.from_json(game_state_json)
            else:
                return None

    def update_staged_moves(self, sess, player_num: int, moves: list[dict]) -> tuple[dict, Optional[int]]:
        """
        Returns
        - game_state_to_return_json: game state to give to the client
        - decline_eviction_player: if a player was evicted from a decline.
        """
        with rlock(f'staged_moves_lock:{self.id}:{player_num}'):
            decline_eviction_player = None

            staged_moves = rget_json(staged_moves_key(self.id, player_num, self.turn_num)) or []
            game_state = self._staged_game_state(player_num)
            if game_state is None:
                game_state = self.get_turn_start_game_state(sess)
            game_state_to_return_json, decline_eviction_player = game_state.update_from_player_moves(player_num, moves, speculative=True)

            print("Done processing, commiting staged moves")
            staged_moves.extend(moves)

            rset_json(staged_moves_key(self.id, player_num, self.turn_num), staged_moves, ex=7 * 24 * 60 * 60)
            rset_json(self._staged_game_state_key(player_num, self.turn_num), game_state.to_json(), ex=7 * 24 * 60 * 60)
        print(f"Move staged {moves[0]}")
        if decline_eviction_player is not None:
            print(f"evicting player {decline_eviction_player}")
            # Find the "choose_decline_option" move in their moves, and trim back to that spot.

            with rlock(f'staged_moves_lock:{self.id}:{decline_eviction_player}'):
                staged_moves = rget_json(staged_moves_key(self.id, decline_eviction_player, self.turn_num)) or []
                for move_index, move in enumerate(staged_moves):
                    if move['move_type'] == 'choose_decline_option':
                        staged_moves = staged_moves[:move_index + 1]
                        staged_moves[-1]['preempted'] = True
                        break
                rset_json(staged_moves_key(self.id, decline_eviction_player, self.turn_num), staged_moves)
                # Now recalculate their game state
                recalc_game_state: GameState = self.get_turn_start_game_state(sess)
                recalc_game_state.update_from_player_moves(decline_eviction_player, staged_moves, speculative=True)
                rset_json(self._staged_game_state_key(decline_eviction_player, self.turn_num), recalc_game_state.to_json(), ex=7 * 24 * 60 * 60)

        return game_state_to_return_json, decline_eviction_player

def load_and_roll_turn_in_game(sess, socketio, game_id: str, turn_num: int):
    with SessionLocal() as sess:
        full_game = Game.get(sess, socketio, game_id)

        if not full_game:
            raise ValueError(f"Turn Timer expired on nonexistent game id={game_id}")
        
        if turn_num == full_game.turn_num and not full_game.game_over and not full_game.timer_paused:
            full_game.roll_turn(sess)

