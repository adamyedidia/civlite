from game import Game

from game_state import GameState

from animation_frame import AnimationFrame

from collections import defaultdict
from itertools import cycle


def make_game_statistics_plots(sess, game_id: str):
    import matplotlib.pyplot as plt
    animation_frames = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.player_num == None)
        .filter(AnimationFrame.frame_num == 1)
        .order_by(AnimationFrame.turn_num)
        .all()
    )

    scores_by_turn = defaultdict(list)
    cum_scores_by_turn = defaultdict(list)
    actual_cum_scores_by_turn = defaultdict(list)

    civ_ids_by_player = None

    turn_nums = []
    decline_turns = defaultdict(list)

    for frame in animation_frames:
        game_state = GameState.from_json(frame.game_state)
        for player_num in game_state.game_player_by_player_num:
            player = game_state.game_player_by_player_num[player_num]
            player_score_excluding_survival = player.score - player.score_from_survival
            scores_by_turn[player.username].append(player_score_excluding_survival - (cum_scores_by_turn[player.username][-1] if cum_scores_by_turn[player.username] else 0))
            cum_scores_by_turn[player.username].append(player_score_excluding_survival)
            actual_cum_scores_by_turn[player.username].append(player.score)

        turn_nums.append(frame.turn_num)

        old_civ_ids_by_player = (civ_ids_by_player or {}).copy()

        civ_ids_by_player = {
            player_num: game_state.game_player_by_player_num[player_num].civ_id
            for player_num in game_state.game_player_by_player_num
        }

        for player_num in game_state.game_player_by_player_num:
            game_player = game_state.game_player_by_player_num[player_num]
            if old_civ_ids_by_player and old_civ_ids_by_player[player_num] != game_player.civ_id:
                decline_turns[game_player.username].append(frame.turn_num)


    print('Plotting: ', scores_by_turn)

    # Apply some smoothing to scores_by_turn
    for username, scores in scores_by_turn.items():
        for i in range(1, len(scores) - 1):
            scores[i] = (scores[i - 1] + scores[i] + scores[i + 1]) / 3

    print("Decline turns: ", decline_turns)

    # Define a list of different dash styles for up to 8 players
    dash_styles = cycle([
        '--',  # Dashed
        '-.',  # Dash-dot
        ':',   # Dotted
        (0, (1, 2)),  # Very long dash, long space
        (0, (5, 1)),   # Long dash, short space
        (0, (3, 2, 1, 2)),  # Dash, long space, dot, long space
        (0, (3, 3, 1, 3)),    # Dash, space, dot, space
        (0, (3, 1, 1, 1, 1, 1))  # Dash, dot, dot-dot-dot
    ])

    for username, scores in scores_by_turn.items():
        line, = plt.plot(turn_nums, scores, label=username)  # Store the Line2D object returned by plt.plot
        plt.legend()
        line_color = line.get_color()  # Get the color of the line
        dash_style = next(dash_styles)  # Get the next dash style from the cycle
        for decline_turn in decline_turns[username]:
            plt.axvline(decline_turn, color=line_color, linestyle=dash_style)  # Use the same color but different dash style for the vertical line
        plt.savefig(f"plots/scores_by_player_{game_id}.png")

    plt.clf()

    # Reset the dash styles for cumulative scores
    dash_styles = cycle([
        '--', '-.', ':', 
        (0, (1, 2)), (0, (5, 1)), 
        (0, (3, 2, 1, 2)), (0, (3, 3, 1, 3)), 
        (0, (3, 1, 1, 1, 1, 1))
    ])

    for username, scores in actual_cum_scores_by_turn.items():
        line, = plt.plot(turn_nums, scores, label=username)  # Store the Line2D object returned by plt.plot
        plt.legend()
        line_color = line.get_color()  # Get the color of the line
        dash_style = next(dash_styles)  # Get the next dash style from the cycle
        for decline_turn in decline_turns[username]:
            plt.axvline(decline_turn, color=line_color, linestyle=dash_style)  # Use the same color but different dash style for the vertical line
        plt.savefig(f"plots/cum_scores_by_player_{game_id}.png")
