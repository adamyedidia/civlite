from collections import Counter, defaultdict
from multiprocessing import freeze_support
from typing import Any
from ai_game import ai_game
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from civ_templates_list import CIVS
from effects_list import GainResourceEffect
from game_player import GamePlayer

from game_state import GameState
from great_person import GreatEngineer, GreatGeneral, GreatMerchant, GreatPerson, GreatScientist, _target_value_by_age, great_people_by_age

import argparse
import os
import pickle
import re
import time
import numpy as np
from numpy.typing import NDArray
from tech_templates_list import TECHS
from tenet_template_list import TENETS, tenets_by_level
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

import settings

assert not settings.GOD_MODE

def ai_game_count_units(id, num_players) -> tuple[dict[str, list[list[dict[Any, int]]]], dict[str, int]]:
    data = ai_game(id, num_players)
    unit_counts = [{unit.name: 0 for unit in UNITS.all()} for _ in range(num_players)]
    great_person_counts = [{person.name: 0 for i in range(10) for person in great_people_by_age(i)} for _ in range(num_players)]
    wonders = [{wonder.name: 0 for wonder in WONDERS.all()} for _ in range(num_players)]
    buildings = [{building.name: 0 for building in BUILDINGS.all()} for _ in range(num_players)]
    civ_turn_counts = [{civ.name: 0 for civ in CIVS.all()} for _ in range(num_players)]
    researching_tech_turns = [{tech.name: 0 for tech in TECHS.all()} for _ in range(num_players)]
    researching_frontier_tech_turns = [{tech.name: 0 for tech in TECHS.all()} for _ in range(num_players)]
    _civ_lifetimes_counter = {civ.name: 0 for civ in CIVS.all()}
    civ_lifetimes = [{i: 0 for i in range(100)} for _ in range(num_players)]
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
        for civ in state.civs_by_id.values():
            if civ.game_player is not None:
                _civ_lifetimes_counter[civ.template.name] += 1
                civ_turn_counts[civ.game_player.player_num][civ.template.name] += 1
                if civ.researching_tech is not None:
                    researching_tech_turns[civ.game_player.player_num][civ.researching_tech.name] += 1
                    if civ.researching_tech.advancement_level == civ.get_advancement_level():
                        researching_frontier_tech_turns[civ.game_player.player_num][civ.researching_tech.name] += 1
    final_state: GameState = GameState.from_json(data[-1])
    final_scores: dict[int, int] = {i: player.score for i, player in final_state.game_player_by_player_num.items()}
    sorted_game_players: list[GamePlayer] = sorted(final_state.game_player_by_player_num.values(), key=lambda p: p.player_num)
    score_sources = [player.score_dict for player in sorted_game_players]
    tenets = [{t.name: int(t in game_player.tenets) for t in TENETS.all()} for game_player in sorted_game_players]
    for i, game_player in enumerate(sorted_game_players):
        for civ_id in game_player.all_civ_ids:
            lifetime = _civ_lifetimes_counter[final_state.civs_by_id[civ_id].template.name]
            civ_lifetimes[i][lifetime] += 1
        if (t := game_player.tenet_at_level(3)) is not None:
            complete = game_player.tenets[t]["complete"]
            tenets[i][t.name + " Complete"] = int(complete)
            tenets[i][t.name + " Incomplete"] = int(not complete)
        if (t := game_player.tenet_at_level(6)) is not None:
            for j in range(3):
                tenets[i][t.name + f" {j}"] = 0
            score_key: str = [k for k in game_player.score_dict.keys() if k.startswith(t.name)][0]
            score_civ_name = score_key.split(" ", 2)[-1]
            player_civ_names = [final_state.civs_by_id[id].template.name for id in game_player.all_civ_ids]
            score_civ_idx = player_civ_names.index(score_civ_name)
            tenets[i][t.name + f" {score_civ_idx}"] += 1
            score_sources[i][t.name + f" {score_civ_idx}"] = game_player.score_dict[score_key]
            del score_sources[i][score_key]


    winner = max(range(num_players), key=lambda i: final_scores[i])
    winner_units = unit_counts.pop(winner)
    winner_wonders = wonders.pop(winner)
    winner_buildings = buildings.pop(winner)
    winner_civ_turn_counts = civ_turn_counts.pop(winner)
    winner_score_sources = score_sources.pop(winner)
    winner_researching_tech_turns = researching_tech_turns.pop(winner)
    winner_researching_frontier_tech_turns = researching_frontier_tech_turns.pop(winner)
    winner_tenets = tenets.pop(winner)
    winner_civ_lifetimes = civ_lifetimes.pop(winner)

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
        'civs': [[winner_civ_turn_counts], civ_turn_counts],
        'score_sources': [[winner_score_sources], score_sources],
        'techs': [[winner_researching_tech_turns], researching_tech_turns],
        'frontier_techs': [[winner_researching_frontier_tech_turns], researching_frontier_tech_turns],
        "tenets": [[winner_tenets], tenets],
        'lifetimes': [[winner_civ_lifetimes], civ_lifetimes]
    }, {
        'turns': final_state.turn_num,
        'age': final_state.advancement_level,
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

def process_game(i: int) -> tuple[dict[str, list[list[dict[Any, int]]]], dict[str, int]] | None:
    if (i < 100 and i % 10 == 0) or i % 100 == 0: print(i)
    try:
        return ai_game_count_units(i, 4)
    except Exception as e:
        with open(f"scripts/errors/error_log_{i}.txt", "a") as f:
            f.write(f"Error processing game {i}: {str(e)}\n")
            import traceback
            traceback.print_exc(file=f)
        return None
    
def blank_defaultdict():
    return defaultdict(int)

class DummyThingWithName:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

def augmented_tenets_list() -> list[DummyThingWithName]:
    l = list([(t.name, t.advancement_level) for t in TENETS.all()])
    for tenet in tenets_by_level[3]:
        for state in [" Complete", " Incomplete"]:
            l.append((tenet.name + state, 3))
    for tenet in tenets_by_level[6]:
        for index in range(3):
            l.append((tenet.name + f" {index}", 6))
    l.sort(key=lambda x: (x[1], x[0]))
    return [DummyThingWithName(x[0]) for x in l]

def accumulate_unit_info(num_games, cache_file, offset=0, max_workers=10):
    winner_data = {
        'units': {unit.name: defaultdict(int) for unit in UNITS.all()},
        'wonders': {wonder.name: defaultdict(int) for wonder in WONDERS.all()},
        'buildings': {building.name: defaultdict(int) for building in BUILDINGS.all()},
        'great_people': {person.name: defaultdict(int) for i in range(10) for person in great_people_by_age(i)},
        'civs': {civ.name: defaultdict(int) for civ in CIVS.all()},
        'score_sources': defaultdict(blank_defaultdict),
        'techs': {tech.name: defaultdict(int) for tech in TECHS.all()},
        'frontier_techs': {tech.name: defaultdict(int) for tech in TECHS.all()},
        'tenets': {tenet.name: defaultdict(int) for tenet in augmented_tenets_list()},
        'lifetimes': {i: defaultdict(int) for i in range(100)},
    }
    loser_data = {
        'units': {unit.name: defaultdict(int) for unit in UNITS.all()},
        'wonders': {wonder.name: defaultdict(int) for wonder in WONDERS.all()},
        'buildings': {building.name: defaultdict(int) for building in BUILDINGS.all()},
        'great_people': {person.name: defaultdict(int) for i in range(10) for person in great_people_by_age(i)},
        'civs': {civ.name: defaultdict(int) for civ in CIVS.all()},
        'score_sources': defaultdict(blank_defaultdict),
        'techs': {tech.name: defaultdict(int) for tech in TECHS.all()},
        'frontier_techs': {tech.name: defaultdict(int) for tech in TECHS.all()},
        'tenets': {tenet.name: defaultdict(int) for tenet in augmented_tenets_list()},
        'lifetimes': {i: defaultdict(int) for i in range(100)},
    }
    game_data = {
        'turns': defaultdict(int),
        'age': defaultdict(int),
    }

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_game, range(offset, offset+num_games)))
    results = [r for r in results if r is not None]
    for player_results, game_results in results:
        for key in player_results:
            local_winner_data, local_loser_data = player_results[key]
            for game in local_winner_data:
                for item, amount in game.items():
                    winner_data[key][item][amount] += 1
            for game in local_loser_data:
                for item, amount in game.items():
                    loser_data[key][item][amount] += 1
        for key, value in game_results.items():
            game_data[key][value] += 1
    if cache_file is not None:
        pickle.dump((winner_data, loser_data, game_data), open(cache_file, "wb"))


def add_counter_arrays(arr1, arr2):
    """
    Takes two arrays which are understood to be zero for all indices higher than the array
    And adds them together.
    """
    max_length = max(len(arr1), len(arr2))
    arr1 = np.pad(arr1, (0, max_length - len(arr1)), 'constant')
    arr2 = np.pad(arr2, (0, max_length - len(arr2)), 'constant')
    return arr1 + arr2

def plot_rates(winner_data, loser_data, items, title, cond_prob_range, name_fn=lambda x: x.name, fig=None, fig_offset=0, color_fn=None, magic_yref_thingy=2):
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

    if color_fn is None:
        color_fn = lambda x: "blue"
    
    colors = [color_fn(item) for item in items]
    # Get the number of columns in the figure
    columns = 2
    # TODO THIS columns THING IS WRONG
    yref = f"y{magic_yref_thingy+2*fig_offset * columns}"
    fig.add_trace(
        go.Bar(
            x=x, 
            y=cond_win_prob, 
            name="Conditional Win Prob", 
            marker_color=colors, 
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
        xref="x domain",
        yref=yref,
        row=2 + 2 * fig_offset, col=1,
    )

    if len(items) > 0 and hasattr(items[0], "advancement_level"):
        for age in range(10):
            probs = [p for item, p in zip(items, cond_win_prob) if item.advancement_level == age]
            if len(probs) > 0:
                average_this_age = np.mean(probs)
                x0 = x[next(i for i, item in enumerate(items) if item.advancement_level == age)]
                x1 = x[len(x) - 1 - next(i for i, item in enumerate(reversed(items)) if item.advancement_level == age)]
                fig.add_shape(
                    type="line",
                    x0=x0,
                    y0=average_this_age,
                    x1=x1,
                    y1=average_this_age,
                    line=dict(color="black", width=1, dash="dot"),
                    xref="x",
                    yref=yref,
                    row=2 + 2 * fig_offset, col=1,
                )

    # Make the plots span both columns
    fig.update_xaxes(tickangle=45, categoryorder='array', categoryarray=x, row=1 + 2 * fig_offset, col=1, domain=[0, 1])
    fig.update_xaxes(tickangle=45, categoryorder='array', categoryarray=x, row=2 + 2 * fig_offset, col=1, domain=[0, 1])
    fig.update_yaxes(title_text=f"{title} Completion Rate", row=1 + 2 * fig_offset, col=1)
    fig.update_yaxes(title_text=f"{title} Conditional Win Prob", range=cond_prob_range, row=2 + 2 * fig_offset, col=1)

    if show_fig:
        fig.show()

    return items, x, y_winner, y_loser, cond_win_prob, cond_win_prob_errors

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

def gives_science(civ) -> bool:
    return any('science' in ability.numbers for ability in civ.abilities)

assert gives_science(CIVS.ATHENS)
assert not gives_science(CIVS.AZTECS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AI Game Unit Stats')
    parser.add_argument('--generate', action='store_true', help='Generate game data')
    parser.add_argument('--analyze', action='store_true', help='Analyze generated data')
    parser.add_argument('--chunks', type=int, default=3, help='Number of chunks to process')
    parser.add_argument('--games_per_chunk', type=int, default=20, help='Number of games per chunk')
    parser.add_argument('--metal_binning', action='store_true', help='Use metal binning')
    parser.add_argument('--output_dir', type=str, default="scripts/output", help='Output directory')
    parser.add_argument('--offset_chunks', type=int, default=0, help='Chunks offset')
    parser.add_argument('--workers', type=int, default=10, help='Number of workers')
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
                lambda: accumulate_unit_info(games_per_chunk, f"{args.output_dir}/ai_game_cache_{offset}_{offset + games_per_chunk - 1}.pkl", offset=offset, max_workers=args.workers),
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
            'civs': {civ.name: defaultdict(int) for civ in CIVS.all()},
            'score_sources': defaultdict(blank_defaultdict),
            'techs': {tech.name: defaultdict(int) for tech in TECHS.all()},
            'frontier_techs': {tech.name: defaultdict(int) for tech in TECHS.all()},
            'tenets': {tenet.name: defaultdict(int) for tenet in augmented_tenets_list()},
            'lifetimes': {i: defaultdict(int) for i in range(100)},
        }
        loser_data_raw = {
            'units': {unit.name: defaultdict(int) for unit in UNITS.all()},
            'wonders': {wonder.name: defaultdict(int) for wonder in WONDERS.all()},
            'buildings': {building.name: defaultdict(int) for building in BUILDINGS.all()},
            'great_people': {person.name: defaultdict(int) for i in range(10) for person in great_people_by_age(i)},
            'civs': {civ.name: defaultdict(int) for civ in CIVS.all()},
            'score_sources': defaultdict(blank_defaultdict),
            'techs': {tech.name: defaultdict(int) for tech in TECHS.all()},
            'frontier_techs': {tech.name: defaultdict(int) for tech in TECHS.all()},
            'tenets': {tenet.name: defaultdict(int) for tenet in augmented_tenets_list()},
            'lifetimes': {i: defaultdict(int) for i in range(100)},
        }
        game_data_raw = {
            'turns': defaultdict(int),
            'age': defaultdict(int),
        }
        for i in range(chunks):
            offset = i*games_per_chunk
            winner_raw_counts, loser_raw_counts, local_game_data = pickle.load(open(f"{args.output_dir}/ai_game_cache_{offset}_{offset+games_per_chunk-1}.pkl", "rb"))
            for key in winner_data_raw:
                print(f"Processing {key}")
                for item in list(winner_raw_counts[key].keys()):
                    winner_data_raw[key][item] = add_defaultdicts(winner_data_raw[key][item], winner_raw_counts[key][item])
                for item in list(loser_raw_counts[key].keys()):
                    loser_data_raw[key][item] = add_defaultdicts(loser_data_raw[key][item], loser_raw_counts[key][item])
            for key in local_game_data:
                game_data_raw[key] = add_defaultdicts(game_data_raw[key], local_game_data[key])
        # Convert them from defaultdicts to arrays.
        winner_data: dict[str, dict[str, NDArray[np.int_]]] = {}
        loser_data: dict[str, dict[str, NDArray[np.int_]]] = {}
        game_data: dict[str, NDArray[np.int_]] = {}
        for key in winner_data_raw:
            print(f"Processing {key}")
            winner_data[key] = {}
            loser_data[key] = {}
            for item in winner_data_raw[key]:
                if item not in loser_data_raw[key]:
                    continue
                print(f"   => {item}")
                winner_data[key][item] = np.array([winner_data_raw[key][item][i] for i in range(max(winner_data_raw[key][item].keys(), default=0)+1)])
                loser_data[key][item] = np.array([loser_data_raw[key][item][i] for i in range(max(loser_data_raw[key][item].keys(), default=0)+1)])
        for key in game_data_raw:
            game_data[key] = np.array([game_data_raw[key][i] for i in range(max(game_data_raw[key].keys())+1)])

        # # Create a figure with subplots for each unit
        # units = [u for u in UNITS.all() if not u.has_tag(UnitTag.WONDROUS) and u.movement > 0]
        # units.sort(key=lambda u: (u.advancement_level, u.name))
        # num_units = len(units)
        # fig = make_subplots(
        #     rows=max(1, num_units//2), cols=2,
        #     subplot_titles=[f"{unit.name} [{conditional_win_prob_str(winner_data['units'][unit.name], loser_data['units'][unit.name])}]" for unit in units]  # Optional: adds titles to each subplot
        # )

        # # Set the bar mode to overlay for histograms
        # fig.update_layout(
        #     height=150*num_units, width=1200, title_text="Unit Histograms",
        #     barmode='overlay',
        #     bargap=0,
        # )

        # x_max = 20
        # for i, unit in enumerate(units, start=0):
        #     winner_unit_data = winner_data['units'][unit.name]
        #     winner_sum = sum(winner_unit_data)
        #     loser_unit_data = loser_data['units'][unit.name]
        #     loser_sum = sum(loser_unit_data)
        #     winner_unit_data = winner_unit_data/winner_sum
        #     loser_unit_data = loser_unit_data/loser_sum

        #     if unit == UNITS.WARRIOR:
        #         max_metal = 300
        #     elif unit == UNITS.SLINGER:
        #         max_metal = 100
        #     else:
        #         max_metal = {
        #             1: 200,
        #             2: 250,
        #             3: 400,
        #             4: 500,
        #             5: 700,
        #             6: 800,
        #             7: 800,
        #             8: 800,
        #             9: 1000,
        #         }[unit.advancement_level]
        #     metal_bins = 10
        #     metal_bin_size = max_metal//metal_bins

        #     binned_winner_data = [0]*metal_bins
        #     for num_built, hist_val in enumerate(winner_unit_data[1:]):
        #         bin_idx = num_built * unit.metal_cost//metal_bin_size
        #         if bin_idx < metal_bins:
        #             binned_winner_data[bin_idx] += hist_val
        #     binned_loser_data = [0]*metal_bins
        #     for num_built, hist_val in enumerate(loser_unit_data[1:]):
        #         bin_idx = num_built * unit.metal_cost//metal_bin_size
        #         if bin_idx < metal_bins:
        #             binned_loser_data[bin_idx] += hist_val

        #     row = i//2 + 1
        #     col = i%2 + 1
        #     if args.metal_binning:
        #         x = np.array(range(1, metal_bins + 1)) * metal_bin_size
        #         y = binned_winner_data, binned_loser_data
        #     else:
        #         x_max = max_metal//unit.metal_cost
        #         x = np.array(range(1, x_max))
        #         y = winner_unit_data[1:], loser_unit_data[1:]

        #     fig.add_trace(
        #         go.Bar(x=x, y=y[0], marker_color='green', opacity=0.5, name="Winner", legendgroup="winner", showlegend=(i == 1)), 
        #         row=row, col=col
        #     )
        #     fig.add_trace(
        #         go.Bar(x=x, y=y[1], marker_color='red', opacity=0.5, name="Loser", legendgroup="loser", showlegend=(i == 1)),
        #         row=row, col=col
        #     )

        #     max_winner = max(y[0]) if len(y[0]) > 0 else 1
        #     max_loser = max(y[1]) if len(y[1]) > 0 else 1
        #     max_ymax = max(max_winner, max_loser) * 1.1  # 10% more than the maximum value
        #     fig.update_yaxes(range=[0, max_ymax], row=row, col=col)
        # fig.show()

        for wonder in WONDERS.all():
            assert len(winner_data['wonders'][wonder.name]) <= 2
            assert len(loser_data['wonders'][wonder.name]) <= 2

        def civs_color_fn(civ):
            colors = {'wood': 'peru', 'metal': 'darkgray', 'food': 'yellowGreen', 'science': 'skyblue'}

            for ability in civ.abilities:
                for thingy in ability.numbers:
                    if thingy in colors:
                        return colors[thingy]
                    if isinstance(thingy, GainResourceEffect):
                        return colors[thingy.resource]
            return "blue"
        
        def gp_color_fn(gp: GreatPerson):
            if isinstance(gp, GreatGeneral):
                if gp.advancement_level > gp.unit_template.advancement_level:
                    return "black"
                elif gp.advancement_level == gp.unit_template.advancement_level:
                    return "dimgrey"
                else:
                    return "darkgrey"
            if isinstance(gp, GreatScientist):
                return "blue"
            if isinstance(gp, GreatMerchant):
                return {'wood': 'peru', 'metal': 'darkgray', 'food': 'yellowGreen', 'science': 'skyblue'}[gp.resource]
            if isinstance(gp, GreatEngineer):
                return "saddlebrown"
            return ""


        fig = make_subplots(rows=20, cols=2)
        fig.update_layout(
            height=6000,
            width=1200,
            barmode='overlay',
            showlegend=False,
        )

        # Plot of turn counts
        fig.add_trace(
            go.Bar(y=game_data['turns'] / np.sum(game_data['turns']), name="Turn Counts"),
            row=1, col=1
        )
        # Plot of age counts
        fig.add_trace(
            go.Bar(y=game_data['age'] / np.sum(game_data['age']), name="Age Counts"),
            row=1, col=2
        )
        # Zoom the x-axis minimum to the min value of the y that's nonzero
        min_turn_count = np.sum(np.cumsum(game_data['turns']) > 0)
        min_age = np.sum(np.cumsum(game_data['age']) > 0)
        fig.update_xaxes(range=[min_turn_count, None], row=1, col=1)
        fig.update_xaxes(range=[min_age, None], row=1, col=2)   
        fig.update_xaxes(title_text="Turn Count", row=1, col=1)
        fig.update_yaxes(title_text="Fraction", row=1, col=1)
        fig.update_xaxes(title_text="Age", row=1, col=2)
        fig.update_yaxes(title_text="Fraction", row=1, col=2)
        fig.update_layout(title_text=f"Run: {args.output_dir.split('/')[-1]} (N={args.games_per_chunk * args.chunks} games)")

        magic_yref_thingy = 3
        offset = 1
        sorted_units = sorted([u for u in UNITS.all() if u.movement > 0], key=lambda u: (u.advancement_level, u.name))
        units, x, y_winner, y_loser, units_cond_win_prob, units_cond_win_prob_errors = plot_rates(winner_data['units'], loser_data['units'], sorted_units, "Unit", cond_prob_range=[0.23, 0.3], fig=fig, fig_offset=offset, magic_yref_thingy=magic_yref_thingy)
        offset += 1

        sorted_lifetimes = [DummyThingWithName(i) for i in range(100)]
        plot_rates(winner_data['lifetimes'], loser_data['lifetimes'], sorted_lifetimes, "Civ Lifetimes", cond_prob_range=[0.1, 0.4], fig=fig, fig_offset=offset, magic_yref_thingy=magic_yref_thingy)
        offset += 1
        sorted_wonders = sorted(WONDERS.all(), key=lambda w: (w.advancement_level, w.name))
        plot_rates(winner_data['wonders'], loser_data['wonders'], sorted_wonders, "Wonder", cond_prob_range=[0.2, 0.4], fig=fig, fig_offset=offset, magic_yref_thingy=magic_yref_thingy)
        offset += 1
        sorted_buildings = sorted(BUILDINGS.all(), key=lambda b: (b.advancement_level, b.type.name, b.name))
        plot_rates(winner_data['buildings'], loser_data['buildings'], sorted_buildings, "Building", cond_prob_range=[0.23, 0.4], fig=fig, fig_offset=offset, magic_yref_thingy=magic_yref_thingy)
        offset += 1
        sorted_civs = sorted(CIVS.all(), key=lambda c: (c.advancement_level, c.region.value, c.name))
        plot_rates(winner_data['civs'], loser_data['civs'], sorted_civs, "Civ", cond_prob_range=[0.1, 0.35], color_fn=civs_color_fn, fig=fig, fig_offset=offset, magic_yref_thingy=magic_yref_thingy)
        offset += 1
        sorted_people = sorted([p for i in range(10) for p in great_people_by_age(i)], key=lambda p: (p.advancement_level, p.__class__.__name__, p.name))
        plot_rates(winner_data['great_people'], loser_data['great_people'], sorted_people, f"Great People", cond_prob_range=[0.1, 0.3], name_fn=gp_name, color_fn=gp_color_fn, fig=fig, fig_offset=offset, magic_yref_thingy=magic_yref_thingy)
        offset += 1
        sorted_techs = sorted(TECHS.all(), key=lambda t: (t.advancement_level, t.cost, t.name))
        plot_rates(winner_data['techs'], loser_data['techs'], sorted_techs, "Tech", cond_prob_range=[0.23, 0.3], fig=fig, fig_offset=offset, magic_yref_thingy=magic_yref_thingy)
        offset += 1
        sorted_frontier_techs = sorted_techs
        plot_rates(winner_data['frontier_techs'], loser_data['frontier_techs'], sorted_frontier_techs, "Frontier Tech", cond_prob_range=[0.23, 0.3], fig=fig, fig_offset=offset, magic_yref_thingy=magic_yref_thingy)
        offset += 1
        sorted_tenets = augmented_tenets_list()
        plot_rates(winner_data['tenets'], loser_data['tenets'], sorted_tenets, "Tenet", cond_prob_range=[0.15, 0.35], fig=fig, fig_offset=offset, magic_yref_thingy=magic_yref_thingy)
        offset += 1
        fig.show()

        fig = make_subplots(rows=22, cols=2)
        fig.update_layout(
            title="Great People",
            barmode='overlay',
            height=12000,
            width=1200,
        )
        great_general_unit_condp = []
        great_general_unit_condp_errors = []
        great_general_condp = []
        great_general_condp_errors = []
        great_generals: list[GreatGeneral] = []
        for i in range(10):
            sorted_people = sorted(great_people_by_age(i), key=lambda p: (p.__class__.__name__, ((p.unit_template.advancement_level, p.unit_template.wood_cost) if isinstance(p, GreatGeneral) else 0), p.name))
            items, x, y_winner, y_loser, cond_win_prob, cond_win_prob_errors = plot_rates(winner_data['great_people'], loser_data['great_people'], sorted_people, f"Great Person Age {i}", cond_prob_range=[0.1, 0.3], name_fn=gp_name, fig=fig, fig_offset=i)
            for p, condp, dcondp in zip(items, cond_win_prob, cond_win_prob_errors):
                if isinstance(p, GreatGeneral) and p.unit_template in units:
                    index = units.index(p.unit_template)
                    unit_dcondp = units_cond_win_prob_errors[index]
                    if unit_dcondp < 0.01:
                        great_general_unit_condp.append(units_cond_win_prob[index])
                        great_general_unit_condp_errors.append(unit_dcondp)
                        great_general_condp.append(condp)
                        great_general_condp_errors.append(dcondp)
                        great_generals.append(p)

        # Add scatter plot for Great Generals
        def get_advancedness(gg: GreatGeneral) -> int:
            return gg.advancement_level - gg.unit_template.advancement_level
        
        def get_target_metal(gg: GreatGeneral) -> float:
            return {-1: 0.4, 0: 0.65, 1: 1.0}.get(get_advancedness(gg), 1e-4) * _target_value_by_age(gg.advancement_level)

        advancednesses = [gg.advancement_level - gg.unit_template.advancement_level for gg in great_generals]

        fig.add_trace(
            go.Scatter(
                x=great_general_unit_condp,
                y=great_general_condp,
                mode='markers',
                name='Great Generals',
                marker=dict(
                    size=20,
                    color=[units.index(gg.unit_template) for gg in great_generals],
                    symbol=[
                        'circle' if adv == 0 else
                        'triangle-up' if adv == 1 else
                        'triangle-down' if adv == -1 else
                        'square' for adv in advancednesses
                    ],                    colorscale='Viridis',
                    showscale=False,
                ),
                error_y=dict(
                    type='data',
                    array=great_general_condp_errors,
                    visible=True
                ),
                error_x=dict(
                    type='data',
                    array=great_general_unit_condp_errors,
                    visible=True
                ),
                hovertext=[f"{gg.name} ({gg.unit_template.name} a{gg.advancement_level}): ({gen_condp:.2f}, {unit_condp:.2f})" 
                           for gg, gen_condp, unit_condp in zip(great_generals, great_general_condp, great_general_unit_condp)]
            ),
            row=21, col=1
        )
        fig.update_xaxes(title_text="Unit Conditional Win Probability", row=21, col=1, range=(0.25, 0.27))
        fig.update_yaxes(title_text="Great Person Conditional Win Probability", row=21, col=1)

        fig.add_trace(
            go.Scatter(
                x=[1 - gg.unit_template.metal_cost * gg.number / get_target_metal(gg) for gg in great_generals],
                y=great_general_condp,
                mode='markers',
                name='Great Generals',
                marker=dict(
                    size=10,
                    color=[gg.unit_template.advancement_level for gg in great_generals],
                    symbol=[
                        'circle' if adv == 0 else
                        'triangle-up' if adv == 1 else
                        'triangle-down' if adv == -1 else
                        'square' for adv in advancednesses
                    ],
                    colorscale='Viridis',
                    showscale=False,
                ),
                error_y=dict(
                    type='data',
                    array=great_general_condp_errors,
                    visible=True
                ),
                hovertext=[f"{gg.name} ({gg.unit_template.name} a{gg.advancement_level}): ({gen_condp:.2f})" 
                           for gg, gen_condp in zip(great_generals, great_general_condp)]
            ),
            row=22, col=1
        )

        fig.update_xaxes(title_text="Metal Fraction Lost To Rounding", row=22, col=1, range=(-0.02, 0.33))
        fig.update_yaxes(title_text="Great Person Conditional Win Probability", row=22, col=1)
        fig.update_layout(height=13000)  # Increase height to accommodate new plot

        fig.show()

        all_score_sources = sorted(set(winner_data['score_sources'].keys()) | set(loser_data['score_sources'].keys()), key=lambda x: (-sum(winner_data['score_sources'][x]), x))
        fig = make_subplots(rows=(len(all_score_sources) // 2 + 2), cols=2)
        total_games_winner = max(sum(winner_data['score_sources'][score_source]) for score_source in all_score_sources)
        total_games_loser = max(sum(loser_data['score_sources'][score_source]) for score_source in all_score_sources)
        predictiveness = {}
        for i, score_source in enumerate(all_score_sources):
            # First pad them both out to the same length
            xmax = max(len(winner_data['score_sources'][score_source]), len(loser_data['score_sources'][score_source]))
            winner_local_data = np.pad(winner_data['score_sources'][score_source], (0, xmax - len(winner_data['score_sources'][score_source])), 'constant')
            loser_local_data = np.pad(loser_data['score_sources'][score_source], (0, xmax - len(loser_data['score_sources'][score_source])), 'constant')
            x = np.where(np.logical_or(winner_local_data > 0, loser_local_data > 0))[0]
            y_winner = winner_local_data[x] / total_games_winner
            y_loser = loser_local_data[x] / total_games_loser

            mean_winner = np.sum(winner_data['score_sources'][score_source] * np.arange(len(winner_data['score_sources'][score_source]))) / total_games_winner
            stddev_winner = np.sqrt(np.sum(winner_data['score_sources'][score_source] * (np.arange(len(winner_data['score_sources'][score_source])) - mean_winner)**2) / total_games_winner)
            mean_loser = np.sum(loser_data['score_sources'][score_source] * np.arange(len(loser_data['score_sources'][score_source]))) / total_games_loser
            stddev_loser = np.sqrt(np.sum(loser_data['score_sources'][score_source] * (np.arange(len(loser_data['score_sources'][score_source])) - mean_loser)**2) / total_games_loser)
            predictiveness[score_source] = (mean_winner - mean_loser) / stddev_loser
            

            fig.add_trace(
                go.Bar(x=x, y=y_winner, name="Winner", marker_color='green', opacity=0.5),
                row=i // 2 + 2, col=i % 2 + 1
            )
            fig.add_trace(
                go.Bar(x=x, y=y_loser, name="Loser", marker_color='red', opacity=0.5),
                row=i // 2 + 2, col=i % 2 + 1
            )
            fig.update_xaxes(title_text=score_source, row=i // 2 + 2, col=i % 2 + 1)
            fig.update_yaxes(title_text="Fraction of Games", row=i // 2 + 2, col=i % 2 + 1)
        
        sources = sorted(predictiveness.keys(), key=lambda x: predictiveness[x], reverse=True)
        fig.add_trace(
            go.Bar(x=sources, y=[predictiveness[source] for source in sources], name='Predictiveness'),
            row=1, col=1
        )
        fig.update_layout(
            xaxis=dict(domain=[0, 1]),  # Span the x-axis across both columns for the first plot
        )
        fig.update_xaxes(title_text="Score Source", row=1, col=1)
        fig.update_yaxes(title_text="stddevs separation winner mean vs loser mean", row=1, col=1)
        fig.update_layout(height=len(all_score_sources)*200, barmode='overlay',)
        fig.show()