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

    for frame in animation_frames:
        game_state = GameState.from_json(frame.game_state)
        for player_num in game_state.game_player_by_player_num:
            player = game_state.game_player_by_player_num[player_num]
            player_score_excluding_survival = player.score - player.score_from_survival
            scores_by_turn[player.username].append(player_score_excluding_survival - (cum_scores_by_turn[player.username][-1] if cum_scores_by_turn[player.username] else 0))
            cum_scores_by_turn[player.username].append(player_score_excluding_survival)

    print('Plotting: ', scores_by_turn)

    # Apply some smoothing to scores_by_turn
    for username, scores in scores_by_turn.items():
        for i in range(1, len(scores) - 1):
            scores[i] = (scores[i - 1] + scores[i] + scores[i + 1]) / 3



    for username, scores in scores_by_turn.items():
        plt.plot(scores, label=username)
        plt.legend()
        plt.savefig(f"plots/scores_by_player_{game_id}.png")

    plt.clf()

    for username, scores in cum_scores_by_turn.items():
        plt.plot(scores, label=username)
        plt.legend()
        plt.savefig(f"plots/cum_scores_by_player_{game_id}.png")


