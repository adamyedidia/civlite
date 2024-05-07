from game import Game

from game_state import GameState

from animation_frame import AnimationFrame

from collections import defaultdict


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

        turn_nums.append(frame.turn_num)

        old_civ_ids_by_player = (civ_ids_by_player or {}).copy()

        civ_ids_by_player = {
            player_num: game_state.game_player_by_player_num[player_num].civ_id
            for player_num in game_state.game_player_by_player_num
        }

        for player_num in game_state.game_player_by_player_num:
            if old_civ_ids_by_player and old_civ_ids_by_player[player_num] != civ_ids_by_player[player_num]:
                decline_turns[player_num].append(frame.turn_num)


    print('Plotting: ', scores_by_turn)

    # Apply some smoothing to scores_by_turn
    for username, scores in scores_by_turn.items():
        for i in range(1, len(scores) - 1):
            scores[i] = (scores[i - 1] + scores[i] + scores[i + 1]) / 3

    print("Decline turns: ", decline_turns)

    for username, scores in scores_by_turn.items():
        line, = plt.plot(scores, label=username)  # Store the Line2D object returned by plt.plot
        plt.legend()
        line_color = line.get_color()  # Get the color of the line
        for decline_turn in decline_turns[username]:
            plt.axvline(decline_turn, color=line_color, linestyle='--')  # Use the same color for the vertical line
        plt.savefig(f"plots/scores_by_player_{game_id}.png")

    plt.clf()

    for username, scores in cum_scores_by_turn.items():
        line, = plt.plot(scores, label=username)  # Store the Line2D object returned by plt.plot
        plt.legend()
        line_color = line.get_color()  # Get the color of the line
        for decline_turn in decline_turns[username]:
            plt.axvline(decline_turn, color=line_color, linestyle='--')  # Use the same color for the vertical line
        plt.savefig(f"plots/cum_scores_by_player_{game_id}.png")

