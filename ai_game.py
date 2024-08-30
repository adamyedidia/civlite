from game_player import GamePlayer
from new_game_state import new_game_state

import copy
import random

def ai_game(id, num_players):
    random.seed(id)
    game_id = id
    players = [GamePlayer(player_num=i, username=f"AI Player {i} in game {id}", is_bot=True, vitality_multiplier=1) for i in range(num_players)]
    game_state, _ = new_game_state(game_id, players)
    game_state.no_db = True
    states = []
    while not game_state.game_over and game_state.turn_num < 100:
        game_state.all_bot_moves()
        game_state.midturn_update()
        states.append(copy.deepcopy(game_state.to_json()))
        game_state.roll_turn(None)
        game_state.midturn_update()
    return states