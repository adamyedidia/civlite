from collections import Counter
from multiprocessing import freeze_support

from game_state import GameState
from new_game_state import new_game_state
from game_player import GamePlayer

import numpy as np
import pickle
import random
from unit_template import UnitTag

from unit_templates_list import UNITS
from concurrent.futures import ProcessPoolExecutor

def ai_game(id, num_players):
    random.seed(id)
    game_id = id
    players = [GamePlayer(player_num=i, username=f"AI Player {i} in game {id}", is_bot=True, vitality_multiplier=1) for i in range(num_players)]
    game_state, _ = new_game_state(game_id, players)
    game_state.no_db = True
    states = []
    print([building.projected_metal_income for city in game_state.cities_by_id.values() for building in city.unit_buildings])
    while not game_state.game_over and game_state.turn_num < 100:
        game_state.all_bot_moves()
        game_state.midturn_update()
        states.append(game_state.to_json())
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
    final_scores: dict[int, int] = {i: player.score for i, player in state.game_player_by_player_num.items()}
    winner = max(range(num_players), key=lambda i: final_scores[i])
    winner_units = unit_counts.pop(winner)
    return winner_units, unit_counts


def process_game(i):
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
    
def accumulate_unit_info(num_games, cache_file):
    winner_counts = {unit: list() for unit in UNITS.all()}
    loser_counts = {unit: list() for unit in UNITS.all()}

    with ProcessPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_game, range(num_games)))
    results = [r for r in results if r is not None]
    for i, local_winner_counts, local_loser_counts in results:
        for unit in UNITS.all():
            winner_counts[unit].extend(local_winner_counts[unit])
            loser_counts[unit].extend(local_loser_counts[unit])
        print(f"\rProcessed {len(results)}/{num_games} ({i})")
        if cache_file is not None:
            pickle.dump((winner_counts, loser_counts), open(cache_file, "wb"))

if __name__ == "__main__":
    freeze_support()
    accumulate_unit_info(50000, "scripts/output/ai_game_cache_50k.pkl")

    winner_raw_counts, loser_raw_counts = pickle.load(open("scripts/output/ai_game_cache_50k.pkl", "rb"))

    def accumulate_list(data):
        counter = Counter(data)
        return [counter[i]/len(data) for i in range(0, max(data)+1)]

    def bin_counts(counts):
        return {unit: accumulate_list(data) for unit, data in counts.items()}
    winner_counts = bin_counts(winner_raw_counts)
    loser_counts = bin_counts(loser_raw_counts)

    def conditional_win_prob(unit):
        total_players = len(winner_raw_counts[unit]) + len(loser_raw_counts[unit])
        won_and_teched = len([x for x in winner_raw_counts[unit] if x > 0])
        lost_and_teched = len([x for x in loser_raw_counts[unit] if x > 0])
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
        rows=num_units//2, cols=2,
        subplot_titles=[f"Histogram for {unit.name} [{conditional_win_prob_str(unit)}]" for unit in units]  # Optional: adds titles to each subplot
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
        loser_data = loser_counts[unit]

        row = i//2 + 1
        col = i%2 + 1

        fig.add_trace(
            go.Bar(x=list(range(1, x_max)), y=winner_data[1:x_max], marker_color='green', opacity=0.5, name="Winner", legendgroup="winner", showlegend=(i == 1)),
            row=row, col=col
        )
        fig.add_trace(
            go.Bar(x=list(range(1, x_max)), y=loser_data[1:x_max], marker_color='red', opacity=0.5, name="Loser", legendgroup="loser", showlegend=(i == 1)),
            row=row, col=col
        )

        max_winner = max(winner_data[1:x_max])
        max_loser = max(loser_data[1:x_max])
        max_ymax = max(max_winner, max_loser) * 1.1  # 10% more than the maximum value
        fig.update_yaxes(range=[0, max_ymax], row=row, col=col)
    fig.show()


