from game import Game

from game_state import GameState

from animation_frame import AnimationFrame

import matplotlib.pyplot as plt

from collections import defaultdict


def make_game_statistics_plots(sess, game_id: str):
    animation_frames = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.player_num == None)
        .filter(AnimationFrame.frame_num == 1)
        .order_by(AnimationFrame.turn_num)
        .all()
    )

    scores_by_turn = defaultdict(list)

    for frame in animation_frames:
        game_state = GameState.from_json(frame.game_state)
        for player_num in game_state.game_player_by_player_num:
            player = game_state.game_player_by_player_num[player_num]
            scores_by_turn[player.username].append(player.score)

    print('Plotting: ', scores_by_turn)

    for username, scores in scores_by_turn.items():
        plt.plot(scores, label=username)
        plt.legend()
        plt.savefig(f"plots/{game_id}.png")

