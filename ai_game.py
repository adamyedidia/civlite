from game_player import GamePlayer
from new_game_state import new_game_state
import argparse

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


import cProfile

def profile_ai_game(id, num_players):
    pr = cProfile.Profile()
    pr.enable()
    
    states = ai_game(id, num_players)
    
    pr.disable()
    # Save profiling data to a file
    profile_filename = 'profile_data.prof'
    pr.dump_stats(profile_filename)
    
    # Use snakeviz to visualize the profiling data
    import subprocess
    subprocess.run(['snakeviz', profile_filename])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, default=0)
    parser.add_argument("--num_players", type=int, default=4)
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()

    # Example usage:
    if args.profile:
        profile_ai_game(args.id, args.num_players)
    else:
        ai_game(args.id, args.num_players)
