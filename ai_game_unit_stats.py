from collections import Counter, defaultdict
from multiprocessing import freeze_support
from typing import Any
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS

from game_state import GameState
from great_person import GreatEngineer, GreatGeneral, GreatMerchant, GreatScientist, great_people_by_age
from new_game_state import new_game_state
from game_player import GamePlayer

import argparse
import copy
import os
import pickle
import random
import re
import time
import numpy as np
from numpy.typing import NDArray
from unit_template import UnitTag

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from unit_templates_list import UNITS
from concurrent.futures import ProcessPoolExecutor
from logging_setup import logger
import logging
import timeit
from wonder_template import WonderTemplate

from wonder_templates_list import WONDERS

logger.disabled = True

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

def ai_game_count_units(id, num_players) -> dict[str, list[list[dict[Any, int]]]]:
    data = ai_game(id, num_players)
    unit_counts = [{unit.name: 0 for unit in UNITS.all()} for _ in range(num_players)]
    great_person_counts = [{person.name: 0 for i in range(10) for person in great_people_by_age(i)} for _ in range(num_players)]
    wonders = [{wonder.name: 0 for wonder in WONDERS.all()} for _ in range(num_players)]
    buildings = [{building.name: 0 for building in BUILDINGS.all()} for _ in range(num_players)]
    for json_state in data:
        state = GameState.from_json(json_state)
        for city in state.cities_by_id.values():
            if city.civ.game_player is not None:
                for unit_building in city.unit_buildings:
                    unit_counts[city.civ.game_player.player_num][unit_building.template.name] += unit_building.projected_unit_count
                for item in city.buildings_queue[:city.projected_build_queue_depth]:
                    if isinstance(item.template, WonderTemplate):
                        wonders[city.civ.game_player.player_num][item.template.name] += 1
                    elif isinstance(item.template, BuildingTemplate):
                        buildings[city.civ.game_player.player_num][item.template.name] += 1
    final_state: GameState = GameState.from_json(data[-1])
    final_scores: dict[int, int] = {i: player.score for i, player in final_state.game_player_by_player_num.items()}
    winner = max(range(num_players), key=lambda i: final_scores[i])
    winner_units = unit_counts.pop(winner)
    winner_wonders = wonders.pop(winner)
    winner_buildings = buildings.pop(winner)

    # get great people from announcements
    # Announcements look like: f"{great_person.name} will lead <civ id={self.id}>{self.moniker()}</civ> to glory."
    # Where id is in hex, and name and moniker are strings
    for item in final_state.announcements:
        match = re.match(r"\[T \d+\] (.+) will lead <civ id=(\w+)>.+</civ> to glory.", item)
        if match is not None:
            great_person_name = match.group(1)
            civ_id = match.group(2)
            game_player = [p for p in final_state.game_player_by_player_num.values() if civ_id in p.all_civ_ids].pop()
            great_person_counts[game_player.player_num][great_person_name] += 1
    winner_great_people = great_person_counts.pop(winner)
    return {
        'units': [[winner_units], unit_counts],
        'wonders': [[winner_wonders], wonders],
        'buildings': [[winner_buildings], buildings],
        'great_people': [[winner_great_people], great_person_counts],
    }

def accumulate_list(data):
    counter = Counter(data)
    return [counter[i] for i in range(0, max(data)+1)]

def add_defaultdicts(d1: defaultdict[Any, int], d2: defaultdict[Any, int]) -> defaultdict[Any, int]:
    d = defaultdict(int)
    combined_keys = set(d1.keys()) | set(d2.keys())
    for key in combined_keys:
        d[key] = d1[key] + d2[key]
    return d

def bin_counts(counts):
    return {unit: accumulate_list(data) for unit, data in counts.items()}

def process_game(i: int) -> dict[str, list[list[dict[Any, int]]]] | None:
    if (i < 100 and i % 10 == 0) or i % 100 == 0: print(i)
    try:
        return ai_game_count_units(i, 4)
    except Exception as e:
        with open(f"scripts/errors/error_log_{i}.txt", "a") as f:
            f.write(f"Error processing game {i}: {str(e)}\n")
            import traceback
            traceback.print_exc(file=f)
        return None
    
def accumulate_unit_info(num_games, cache_file, offset=0):
    winner_data = {
        'units': {unit.name: defaultdict(int) for unit in UNITS.all()},
        'wonders': {wonder.name: defaultdict(int) for wonder in WONDERS.all()},
        'buildings': {building.name: defaultdict(int) for building in BUILDINGS.all()},
        'great_people': {person.name: defaultdict(int) for i in range(10) for person in great_people_by_age(i)},
    }
    loser_data = {
        'units': {unit.name: defaultdict(int) for unit in UNITS.all()},
        'wonders': {wonder.name: defaultdict(int) for wonder in WONDERS.all()},
        'buildings': {building.name: defaultdict(int) for building in BUILDINGS.all()},
        'great_people': {person.name: defaultdict(int) for i in range(10) for person in great_people_by_age(i)},
    }

    with ProcessPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_game, range(offset, offset+num_games)))
    results = [r for r in results if r is not None]
    for result in results:
        for key in result:
            local_winner_data, local_loser_data = result[key]
            for game in local_winner_data:
                for item, amount in game.items():
                    winner_data[key][item][amount] += 1
            for game in local_loser_data:
                for item, amount in game.items():
                    loser_data[key][item][amount] += 1
    if cache_file is not None:
        pickle.dump((winner_data, loser_data), open(cache_file, "wb"))


def add_counter_arrays(arr1, arr2):
    """
    Takes two arrays which are understood to be zero for all indices higher than the array
    And adds them together.
    """
    max_length = max(len(arr1), len(arr2))
    arr1 = np.pad(arr1, (0, max_length - len(arr1)), 'constant')
    arr2 = np.pad(arr2, (0, max_length - len(arr2)), 'constant')
    return arr1 + arr2

def plot_rates(winner_data, loser_data, items, title, cond_prob_range, name_fn=lambda x: x.name, fig=None, fig_offset=0):
    # Create dictionaries for building completion rates
    winner_counts = {
        item.name: sum(winner_data[item.name][1:]) / sum(winner_data[item.name])
        for item in items
    }
    loser_counts = {
        item.name: sum(loser_data[item.name][1:]) / sum(loser_data[item.name])
        for item in items
    }

    # Create a new figure for building counts
    if fig is None:
        show_fig = True
        fig = make_subplots(rows=2, cols=1)
        fig.update_layout(
            title=title,
            barmode='overlay',
            height=1200,
            width=1200,
        )
    else:
        show_fig = False

    items = [item for item in items if winner_counts[item.name] > 0 or loser_counts[item.name] > 0]
    x: list[str] = [name_fn(item) for item in items]
    y_winner = [winner_counts[item.name] for item in items]
    y_loser = [loser_counts[item.name] for item in items]

    fig.add_trace(
        go.Bar(x=x, y=y_winner, name="Winner", marker_color='green', opacity=0.5),
        row=1 + 2 * fig_offset, col=1
    )
    fig.add_trace(
        go.Bar(x=x, y=y_loser, name="Loser", marker_color='red', opacity=0.5),
        row=1 + 2 * fig_offset, col=1
    )

    cond_win_prob = []
    cond_win_prob_errors = []
    for item in items:
        prob, error = conditional_win_prob(winner_data[item.name], loser_data[item.name])
        cond_win_prob.append(prob)
        cond_win_prob_errors.append(error)

    fig.add_trace(
        go.Bar(
            x=x, 
            y=cond_win_prob, 
            name="Conditional Win Prob", 
            marker_color='blue', 
            opacity=0.5,
            error_y=dict(
                type='data',
                array=cond_win_prob_errors,
                visible=True
            )
        ),
        row=2 + 2 * fig_offset, col=1
    )
    fig.add_shape(
        type="line",
        x0=0,
        y0=0.25,
        x1=1,
        y1=0.25,
        line=dict(color="black", width=2, dash="dash"),
        xref="paper",
        yref=f"y{2+2*fig_offset}"
    )

    fig.update_xaxes(tickangle=45, categoryorder='array', categoryarray=x, row=1 + 2 * fig_offset, col=1)
    fig.update_xaxes(tickangle=45, categoryorder='array', categoryarray=x, row=2 + 2 * fig_offset, col=1)
    fig.update_yaxes(title_text="Completion Rate", row=1 + 2 * fig_offset, col=1)
    fig.update_yaxes(title_text="Conditional Win Prob", range=cond_prob_range, row=2 + 2 * fig_offset, col=1)
    if show_fig:
        fig.show()

def conditional_win_prob(winner_data: NDArray[np.int_], loser_data: NDArray[np.int_]) -> tuple[float, float]:
    total_players = sum(winner_data) + sum(loser_data)
    won_and_teched = sum(winner_data[1:])
    lost_and_teched = sum(loser_data[1:])
    teched = won_and_teched + lost_and_teched
    if teched == 0: return 0, 0
    conditional_win_prob = won_and_teched / teched  

    dwon_and_teched = np.sqrt(won_and_teched * (total_players - won_and_teched) / total_players)
    dteched = np.sqrt(teched * (total_players - teched) / total_players)

    dconditional_win_prob: float = np.linalg.norm([dwon_and_teched / teched, dteched * won_and_teched/teched**2]) 
    return conditional_win_prob, dconditional_win_prob

def conditional_win_prob_str(winner_data: NDArray[np.int_], loser_data: NDArray[np.int_]) -> str:
    prob, error = conditional_win_prob(winner_data, loser_data)
    return f"{prob:.1%} ± {error:.1%}"

def gp_name(great_person) -> str:
    if isinstance(great_person, GreatGeneral):
        return f"{great_person.name} ({great_person.number} {great_person.unit_template.name})"
    elif isinstance(great_person, GreatMerchant):
        return f"{great_person.name} ({great_person.amount} {great_person.resource})"
    elif isinstance(great_person, GreatEngineer):
        return f"{great_person.name} ({great_person.unit_template.name} building)"
    elif isinstance(great_person, GreatScientist):
        return f"{great_person.name} ({great_person.tech_template.name})"
    else:
        return great_person.name + " (????)"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Game Unit Stats')
    parser.add_argument('--generate', action='store_true', help='Generate game data')
    parser.add_argument('--analyze', action='store_true', help='Analyze generated data')
    parser.add_argument('--chunks', type=int, default=3, help='Number of chunks to process')
    parser.add_argument('--games_per_chunk', type=int, default=20, help='Number of games per chunk')
    parser.add_argument('--metal_binning', action='store_true', help='Use metal binning')
    parser.add_argument('--output_dir', type=str, default="scripts/output", help='Output directory')
    parser.add_argument('--offset_chunks', type=int, default=0, help='Chunks offset')
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
            offset = (i + args.offset_chunks) * games_per_chunk
            elapsed_time = timeit.timeit(
                lambda: accumulate_unit_info(games_per_chunk, f"{args.output_dir}/ai_game_cache_{offset}_{offset + games_per_chunk - 1}.pkl", offset=offset),
                number=1
            )
            print(f"Processing chunk {i} took {elapsed_time:.2f} seconds")
            time.sleep(5)

    if args.analyze:
        winner_data_raw = {
            'units': {unit.name: defaultdict(int) for unit in UNITS.all()},
            'wonders': {wonder.name: defaultdict(int) for wonder in WONDERS.all()},
            'buildings': {building.name: defaultdict(int) for building in BUILDINGS.all()},
            'great_people': {person.name: defaultdict(int) for i in range(10) for person in great_people_by_age(i)},
        }
        loser_data_raw = {
            'units': {unit.name: defaultdict(int) for unit in UNITS.all()},
            'wonders': {wonder.name: defaultdict(int) for wonder in WONDERS.all()},
            'buildings': {building.name: defaultdict(int) for building in BUILDINGS.all()},
            'great_people': {person.name: defaultdict(int) for i in range(10) for person in great_people_by_age(i)},
        }
        for i in range(chunks):
            offset = i*games_per_chunk
            winner_raw_counts, loser_raw_counts = pickle.load(open(f"{args.output_dir}/ai_game_cache_{offset}_{offset+games_per_chunk-1}.pkl", "rb"))
            for key in winner_data_raw:
                for item in winner_data_raw[key]:
                    winner_data_raw[key][item] = add_defaultdicts(winner_data_raw[key][item], winner_raw_counts[key][item])
                    loser_data_raw[key][item] = add_defaultdicts(loser_data_raw[key][item], loser_raw_counts[key][item])
                # Convert them from defaultdicts to arrays.
        winner_data: dict[str, dict[str, NDArray[np.int_]]] = {}
        loser_data: dict[str, dict[str, NDArray[np.int_]]] = {}
        for key in winner_data_raw:
            winner_data[key] = {}
            loser_data[key] = {}
            for item in winner_data_raw[key]:
                winner_data[key][item] = np.array([winner_data_raw[key][item][i] for i in range(max(winner_data_raw[key][item].keys())+1)])
                loser_data[key][item] = np.array([loser_data_raw[key][item][i] for i in range(max(loser_data_raw[key][item].keys())+1)])

        # Create a figure with subplots for each unit
        units = [u for u in UNITS.all() if not u.has_tag(UnitTag.WONDROUS) and u.movement > 0]
        units.sort(key=lambda u: (u.advancement_level(), u.name))
        num_units = len(units)
        fig = make_subplots(
            rows=max(1, num_units//2), cols=2,
            subplot_titles=[f"{unit.name} [{conditional_win_prob_str(winner_data['units'][unit.name], loser_data['units'][unit.name])}]" for unit in units]  # Optional: adds titles to each subplot
        )

        # Set the bar mode to overlay for histograms
        fig.update_layout(
            height=150*num_units, width=1200, title_text="Unit Histograms",
            barmode='overlay',
            bargap=0,
        )

        x_max = 20
        for i, unit in enumerate(units, start=0):
            winner_unit_data = winner_data['units'][unit.name]
            winner_sum = sum(winner_unit_data)
            loser_unit_data = loser_data['units'][unit.name]
            loser_sum = sum(loser_unit_data)
            winner_unit_data = winner_unit_data/winner_sum
            loser_unit_data = loser_unit_data/loser_sum

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
            for num_built, hist_val in enumerate(winner_unit_data[1:]):
                bin_idx = num_built * unit.metal_cost//metal_bin_size
                if bin_idx < metal_bins:
                    binned_winner_data[bin_idx] += hist_val
            binned_loser_data = [0]*metal_bins
            for num_built, hist_val in enumerate(loser_unit_data[1:]):
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
                y = winner_unit_data[1:], loser_unit_data[1:]

            fig.add_trace(
                go.Bar(x=x, y=y[0], marker_color='green', opacity=0.5, name="Winner", legendgroup="winner", showlegend=(i == 1)), 
                row=row, col=col
            )
            fig.add_trace(
                go.Bar(x=x, y=y[1], marker_color='red', opacity=0.5, name="Loser", legendgroup="loser", showlegend=(i == 1)),
                row=row, col=col
            )

            max_winner = max(y[0]) if len(y[0]) > 0 else 1
            max_loser = max(y[1]) if len(y[1]) > 0 else 1
            max_ymax = max(max_winner, max_loser) * 1.1  # 10% more than the maximum value
            fig.update_yaxes(range=[0, max_ymax], row=row, col=col)
        fig.show()

        for wonder in WONDERS.all():
            assert len(winner_data['wonders'][wonder.name]) <= 2
            assert len(loser_data['wonders'][wonder.name]) <= 2

        sorted_units = sorted(UNITS.all(), key=lambda u: (u.advancement_level(), u.name))
        plot_rates(winner_data['units'], loser_data['units'], sorted_units, "Unit Completion Rates", cond_prob_range=[0.23, 0.3])
        sorted_wonders = sorted(WONDERS.all(), key=lambda w: (w.age, w.name))
        plot_rates(winner_data['wonders'], loser_data['wonders'], sorted_wonders, "Wonder Completion Rates", cond_prob_range=[0.2, 0.4])
        sorted_buildings = sorted(BUILDINGS.all(), key=lambda b: (b.advancement_level(), b.name))
        plot_rates(winner_data['buildings'], loser_data['buildings'], sorted_buildings, "Building Completion Rates", cond_prob_range=[0.23, 0.3])

        fig = make_subplots(rows=20, cols=1)
        fig.update_layout(
            title="Great People",
            barmode='overlay',
            height=12000,
            width=1200,
        )
        for i in range(10):
            sorted_people = sorted(great_people_by_age(i), key=lambda p: (p.__class__.__name__, p.name))
            plot_rates(winner_data['great_people'], loser_data['great_people'], sorted_people, f"Great Person Age {i}", cond_prob_range=[0.1, 0.3], name_fn=gp_name, fig=fig, fig_offset=i)
        fig.show()