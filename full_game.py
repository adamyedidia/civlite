from database import SessionLocal
from datetime import datetime, timedelta
from threading import Timer
from typing import Optional

from utils import moves_processing_key, staged_moves_key

from game import Game, TimerStatus
from game_state import GameState, get_most_recent_game_state
from redis_utils import rset, rget, await_empty_counter, rlock, rget_json

class FullGame():
    """
    A wrapper around the db Game class which knows about all the other stuff
    """
    def __init__(self, game: Game, socketio):
        self.game: Game = game
        self.socketio = socketio

    @property
    def game_id(self) -> str:
        return self.game.id  # type: ignore
    
    @property
    def turn_num(self) -> int:
        return self.game.turn_num  # type: ignore
    
    @property
    def seconds_per_turn(self) -> Optional[int]:
        return self.game.seconds_per_turn  # type: ignore
  
    @property
    def next_forced_roll_at(self) -> Optional[int]:
        return self.game.next_forced_roll_at  # type: ignore
    
    @property
    def game_over(self) -> bool:
        return self.game.game_over  # type: ignore
    
    @property
    def timer_status(self) -> TimerStatus:
        return self.game.timer_status  # type: ignore
    
    def roll_turn_lock_key(self, turn_num):
        return f"roll_turn_lock:{self.game_id}:{turn_num}"
    
    def accepting_moves(self, turn_num) -> bool:
        """
        Check if this game is accepting client moves.
        i.e. the turn_num is correct and the turn roll has not started
        """
        if self.turn_num != turn_num:
            # Wrong turn number
            print(f"Game {self.game_id} is not accepting moves for turn_num {turn_num} because we're on turn_num {self.turn_num}")
            return False

        lock_key = self.roll_turn_lock_key(turn_num)
        if rlock(lock_key).locked():
            # Turn is already rolling
            print(f"Game {self.game_id} is not accepting moves because turn {turn_num} is already rolling")
            return False

        return True
    
    def turn_ended_by_player_key(self, player_num):
        return f"turn_ended_by_player:{self.game_id}:{player_num}"

    def turn_ended_by_player(self, player_num) -> bool:
        if self.game.players[player_num].is_bot:
            return True
        ended: str | None = rget(self.turn_ended_by_player_key(player_num))
        assert ended is not None, f"turn_ended_by_player_key {self.turn_ended_by_player_key(player_num)} not set"
        assert ended in ["true", "false"], f"turn_ended_by_player_key {self.turn_ended_by_player_key(player_num)} not set"
        return ended == "true"
    
    def set_turn_ended_by_player_num(self, player_num, ended: bool):
        rset(self.turn_ended_by_player_key(player_num), "true" if ended else "false")
        self.broadcast('turn_end_change', {'player_num': player_num, 'turn_ended': ended})

    def roll_turn_if_needed(self, sess):
        for player_num in range(len(self.game.players)):
            if not self.turn_ended_by_player(player_num):
                return
        self.roll_turn(sess)

    @property
    def timer_paused(self) -> bool:
        return self.game.timer_status == TimerStatus.PAUSED  # type: ignore
    
    def pause(self, sess):
        if rlock(self.roll_turn_lock_key(self.turn_num)).locked:
            print(f"Another thread is already rolling turn {self.turn_num} for game {self.game_id}.")
            return

        # TODO something weird could probably happen if the turn starts rolling in the middle of this function.

        self.game.timer_status = TimerStatus.PAUSED  # type: ignore
        sess.commit()
        self.socketio.emit('mute_timer', {'turn_num': self.turn_num}, room=self.game_id)

    @staticmethod
    def get(sess, socketio, game_id: str) -> Optional["FullGame"]:
        game: Game | None = sess.query(Game).filter(Game.id == game_id).first()
        if game is None:
            return None
        else:
            return FullGame(game, socketio)

    def broadcast(self, signal, data=None):
        print(f"broadcasting {signal} to {self.game_id}")

        self.socketio.emit(
            signal, 
            data or {},
            room=self.game.id,  # type: ignore
        )

    def roll_turn(self, sess):
        print(f"rolling turn {self.turn_num} in game {self.game_id}")

        # Don't roll if there's a person who has declined and not ended turn
        declined_players: set[int] = {player_num for player_num in range(len(self.game.players)) if self.has_player_declined(player_num, self.turn_num) and not self.turn_ended_by_player(player_num)}
        if declined_players:
            print(f"Not rolling turn {self.turn_num} in game {self.game_id} because player(s) {', '.join(map(str, declined_players))} have declined and not ended turn")
            self.broadcast("mute_timer", {"turn_num": self.turn_num})
            self.game.timer_status = TimerStatus.OVERTIME  # type: ignore
            sess.commit()
            self.broadcast("overtime", {"turn_num": self.turn_num, "declined_players": list(declined_players)})
            for player in range(len(self.game.players)):
                if player not in declined_players and not self.turn_ended_by_player(player):
                    self.set_turn_ended_by_player_num(player, True)
            return


        lock = rlock(self.roll_turn_lock_key(self.turn_num), expire=60 * 60)
        if lock.acquire(blocking=False):
            try:
                self.broadcast('start_turn_roll')

                # Wait till all active threads have finished, up to 5s
                await_empty_counter(moves_processing_key(self.game_id, self.turn_num), 5, 0.1)
                
                # need to load the game state here, after await_empty_counter on the moves in flight.
                # or else we'll have a stale version.
                game_state: GameState = get_most_recent_game_state(sess, self.game_id)

                game_state.end_turn(sess)

                if self.seconds_per_turn is not None and not self.game_over and self.turn_num < 200:
                    seconds_until_next_forced_roll: float = int(self.seconds_per_turn) + min(self.turn_num, 30)
                    next_forced_roll_at: float = (datetime.now() + timedelta(seconds=seconds_until_next_forced_roll)).timestamp()

                    self.game.next_forced_roll_at = next_forced_roll_at  # type: ignore
                    Timer(next_forced_roll_at - datetime.now().timestamp(), 
                        load_and_roll_turn_in_game, 
                        args=[sess, self.socketio, self.game_id, self.turn_num + 1]).start()
                else:
                    self.game.next_forced_roll_at = None  # type: ignore

                self.game.turn_num = self.turn_num + 1  # type: ignore
                if game_state.game_over:
                    self.game.game_over = True  # type: ignore
                    # TODO should we not even have game_state.game_over?
                self.game.timer_status = TimerStatus.NORMAL  # type: ignore
                sess.commit()
                self.broadcast('update', {"next_forced_roll_at": self.game.next_forced_roll_at})
                for player_num, player in enumerate(self.game.players):
                    if not player.is_bot:
                        self.set_turn_ended_by_player_num(player_num, False)
            except Exception as e:
                # Note we only relesae the lock if there's an exception
                # Otherwise we just hold the lock forever
                # Since we only ever want to roll turn once.
                lock.release()
                raise e
        else:
            print(f"Another thread is already rolling turn {self.turn_num} for game {self.game_id}.")

    def has_player_declined(self, player_num, turn_num) -> bool:
        staged_moves = rget_json(staged_moves_key(self.game_id, player_num, turn_num)) or []
        for move in staged_moves:
            if move['move_type'] == 'choose_decline_option':
                return True
        return False

def load_and_roll_turn_in_game(sess, socketio, game_id: str, turn_num: int):
    with SessionLocal() as sess:
        full_game = FullGame.get(sess, socketio, game_id)

        if not full_game:
            raise ValueError(f"Turn Timer expired on nonexistent game id={game_id}")
        
        if turn_num == full_game.turn_num and not full_game.game_over and not full_game.timer_paused:
            full_game.roll_turn(sess)

