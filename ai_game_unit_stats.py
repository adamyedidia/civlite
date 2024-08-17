from collections import Counter
from multiprocessing import freeze_support

from game_state import GameState
from new_game_state import new_game_state
from game_player import GamePlayer

import argparse
import copy
import os
import pickle
import random
import time
import numpy as np
from unit_template import UnitTag

from unit_templates_list import UNITS
from concurrent.futures import ProcessPoolExecutor
import logging
import timeit

logger = logging.getLogger()
logger.setLevel(logging.WARNING)  # This will suppress INFO level logs

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

def ai_game_count_units(id, num_players):
    data = ai_game(id, num_players)
    unit_counts = [{unit: 0 for unit in UNITS.all()} for _ in range(num_players)]
    for json_state in data:
        state = GameState.from_json(json_state)
        for city in state.cities_by_id.values():
            if city.civ.game_player is not None:
                for unit_building in city.unit_buildings:
                    unit_counts[city.civ.game_player.player_num][unit_building.template] += unit_building.projected_unit_count
    final_scores: dict[int, int] = {i: player.score for i, player in state.game_player_by_player_num.items()}  # type: ignore
    winner = max(range(num_players), key=lambda i: final_scores[i])
    winner_units = unit_counts.pop(winner)
    return winner_units, unit_counts

def accumulate_list(data):
    counter = Counter(data)
    return [counter[i] for i in range(0, max(data)+1)]

def bin_counts(counts):
    return {unit: accumulate_list(data) for unit, data in counts.items()}

def process_game(i):
    if (i < 100 and i % 10 == 0) or i % 100 == 0: print(i)
    try:
        winner_game, losers_game = ai_game_count_units(i, 4)
        local_winner_counts = {unit: [winner_game[unit]] for unit in UNITS.all()}
        local_loser_counts = {unit: [g[unit] for g in losers_game] for unit in UNITS.all()}
    except Exception as e:
        with open(f"scripts/errors/error_log_{i}.txt", "a") as f:
            f.write(f"Error processing game {i}: {str(e)}\n")
            import traceback
            traceback.print_exc(file=f)
        return None
    return i, local_winner_counts, local_loser_counts
    
def accumulate_unit_info(num_games, cache_file, offset=0):
    winner_counts = {unit: list() for unit in UNITS.all()}
    loser_counts = {unit: list() for unit in UNITS.all()}

    with ProcessPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_game, range(offset, offset+num_games)))
    results = [r for r in results if r is not None]
    for i, local_winner_counts, local_loser_counts in results:
        for unit in UNITS.all():
            winner_counts[unit].extend(local_winner_counts[unit])
            loser_counts[unit].extend(local_loser_counts[unit])
    winner_counts = bin_counts(winner_counts)
    loser_counts = bin_counts(loser_counts)
    if cache_file is not None:
        pickle.dump((winner_counts, loser_counts), open(cache_file, "wb"))


def add_counter_arrays(arr1, arr2):
    """
    Takes two arrays which are understood to be zero for all indices higher than the array
    And adds them together.
    """
    max_length = max(len(arr1), len(arr2))
    arr1 = np.pad(arr1, (0, max_length - len(arr1)), 'constant')
    arr2 = np.pad(arr2, (0, max_length - len(arr2)), 'constant')
    return arr1 + arr2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Game Unit Stats')
    parser.add_argument('--generate', action='store_true', help='Generate game data')
    parser.add_argument('--analyze', action='store_true', help='Analyze generated data')
    parser.add_argument('--chunks', type=int, default=3, help='Number of chunks to process')
    parser.add_argument('--games_per_chunk', type=int, default=20, help='Number of games per chunk')
    parser.add_argument('--metal_binning', action='store_true', help='Use metal binning')
    parser.add_argument('--output_dir', type=str, default="scripts/output", help='Output directory')
    args = parser.parse_args()

    if not args.generate and not args.analyze:
        parser.error('At least one of --generate or --analyze must be specified.')

    chunks = args.chunks
    games_per_chunk = args.games_per_chunk

    if args.generate:
        freeze_support()
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        for i in range(chunks):
            offset = i*games_per_chunk
            elapsed_time = timeit.timeit(
                lambda: accumulate_unit_info(games_per_chunk, f"{args.output_dir}/ai_game_cache_{offset}_{offset + games_per_chunk - 1}.pkl", offset=offset),
                number=1
            )
            print(f"Processing chunk {i} took {elapsed_time:.2f} seconds")
            time.sleep(5)

    if args.analyze:
        winner_counts = {unit: np.array([0]) for unit in UNITS.all()}
        loser_counts = {unit: np.array([0]) for unit in UNITS.all()}
        for i in range(chunks):
            print(f"===== {i} =====")
            offset = i*games_per_chunk
            winner_raw_counts, loser_raw_counts = pickle.load(open(f"{args.output_dir}/ai_game_cache_{offset}_{offset+games_per_chunk-1}.pkl", "rb"))
            # print(f"{winner_raw_counts[UNITS.CHARIOT]=}")
            # print(f"{loser_raw_counts[UNITS.CHARIOT]=}")
            for unit in UNITS.all():
                new_winner_data = np.array(winner_raw_counts[unit])
                winner_counts[unit] = add_counter_arrays(winner_counts[unit], new_winner_data)
                new_loser_data = np.array(loser_raw_counts[unit])
                loser_counts[unit] = add_counter_arrays(loser_counts[unit], new_loser_data)
                
                # if unit == UNITS.CHARIOT:
                #     print(f"{winner_counts[unit]=}")
                #     print(f"{loser_counts[unit]=}")

        def conditional_win_prob(unit):
            total_players = sum(winner_counts[unit]) + sum(loser_counts[unit])
            won_and_teched = sum(winner_counts[unit][1:])
            lost_and_teched = sum(loser_counts[unit][1:])
            teched = won_and_teched + lost_and_teched
            conditional_win_prob = won_and_teched / teched  

            dwon_and_teched = np.sqrt(won_and_teched * (total_players - won_and_teched) / total_players)
            dteched = np.sqrt(teched * (total_players - teched) / total_players)

            dconditional_win_prob = np.linalg.norm([dwon_and_teched / teched, dteched * won_and_teched/teched**2]) 
            return conditional_win_prob, dconditional_win_prob

        def conditional_win_prob_str(unit):
            prob, error = conditional_win_prob(unit)
            return f"{prob:.1%} ± {error:.1%}"

        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # Create a figure with subplots for each unit
        units = [u for u in UNITS.all() if not u.has_tag(UnitTag.WONDROUS) and u.movement > 0]
        units.sort(key=lambda u: (u.advancement_level(), u.name))
        num_units = len(units)
        fig = make_subplots(
            rows=max(1, num_units//2), cols=2,
            subplot_titles=[f"{unit.name} [{conditional_win_prob_str(unit)}]" for unit in units]  # Optional: adds titles to each subplot
        )

        # Set the bar mode to overlay for histograms
        fig.update_layout(
            height=150*num_units, width=1200, title_text="Unit Histograms",
            barmode='overlay',
            bargap=0,
        )

        x_max = 20
        for i, unit in enumerate(units, start=0):
            winner_data = winner_counts[unit]
            winner_sum = sum(winner_data)
            loser_data = loser_counts[unit]
            loser_sum = sum(loser_data)
            winner_data = winner_data/winner_sum
            loser_data = loser_data/loser_sum

            if unit == UNITS.WARRIOR:
                max_metal = 300
            elif unit == UNITS.SLINGER:
                max_metal = 100
            else:
                max_metal = {
                    1: 200,
                    2: 250,
                    3: 400,
                    4: 500,
                    5: 700,
                    6: 800,
                    7: 800,
                    8: 800,
                    9: 1000,
                }[unit.advancement_level()]
            metal_bins = 10
            metal_bin_size = max_metal//metal_bins

            binned_winner_data = [0]*metal_bins
            for num_built, hist_val in enumerate(winner_data[1:]):
                bin_idx = num_built * unit.metal_cost//metal_bin_size
                if bin_idx < metal_bins:
                    binned_winner_data[bin_idx] += hist_val
            binned_loser_data = [0]*metal_bins
            for num_built, hist_val in enumerate(loser_data[1:]):
                bin_idx = num_built * unit.metal_cost//metal_bin_size
                if bin_idx < metal_bins:
                    binned_loser_data[bin_idx] += hist_val

            row = i//2 + 1
            col = i%2 + 1
            if args.metal_binning:
                x = np.array(range(1, metal_bins + 1)) * metal_bin_size
                y = binned_winner_data, binned_loser_data
            else:
                x_max = max_metal//unit.metal_cost
                x = np.array(range(1, x_max))
                y = winner_data[1:], loser_data[1:]
            fig.add_trace(
                go.Bar(x=x, y=y[0], marker_color='green', opacity=0.5, name="Winner", legendgroup="winner", showlegend=(i == 1)), 
                row=row, col=col
            )
            fig.add_trace(
                go.Bar(x=x, y=y[1], marker_color='red', opacity=0.5, name="Loser", legendgroup="loser", showlegend=(i == 1)),
                row=row, col=col
            )

            max_winner = max(y[0])
            max_loser = max(y[1])
            max_ymax = max(max_winner, max_loser) * 1.1  # 10% more than the maximum value
            fig.update_yaxes(range=[0, max_ymax], row=row, col=col)
        fig.show()


