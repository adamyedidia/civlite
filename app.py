from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from sqlalchemy import func
from animation_frame import AnimationFrame
from database import SessionLocal
from game import Game
from game_state import GameState
from map import create_hex_map
from player import Player

from settings import LOCAL
from user import add_or_get_user
from utils import generate_unique_id

# Create a logger
logger = logging.getLogger('__name__')
logger.setLevel(logging.DEBUG if LOCAL else logging.INFO)

# Create a handler that writes log messages to a file, with a max size of 1MB, and keep 3 backup logs
handler = RotatingFileHandler('app.log', maxBytes=1_000_000, backupCount=10)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

def recurse_to_json(obj):
    if isinstance(obj, dict):
        return {k: recurse_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recurse_to_json(v) for v in obj]
    elif hasattr(obj, 'to_json'):
        return obj.to_json()
    else:
        return obj


# decorator that takes in an api endpoint and calls recurse_to_json on its result
def api_endpoint(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try: 
            with SessionLocal() as sess:
                kwargs['sess'] = sess
                try:
                    response = func(*args, **kwargs)
                except Exception as e:
                    sess.rollback()
                    raise e
                finally:
                    sess.close()
            return recurse_to_json(response)
        except Exception as e:
            logger.error(traceback.print_exc())
            return jsonify({"error": "Unexpected error"}), 500

    return wrapper


@app.route('/api/host_game', methods=['POST'])
@api_endpoint
def host_game(sess):
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    map_size = data.get('map_size')

    if not map_size:
        return jsonify({"error": "Map size is required"}), 400
    
    user = add_or_get_user(sess, username)

    game = Game(
        id=generate_unique_id(),
        map_size=map_size,
    )

    sess.add(game)
    sess.commit()

    player = Player(
        user=user,
        game=game,
        player_num=0,
    )

    sess.add(player)
    sess.commit()

    return jsonify(game.to_json())


@app.route('/api/join_game', methods=['POST'])
@api_endpoint
def join_game(sess):
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    game_id = data.get('game_id')

    if not game_id:
        return jsonify({"error": "Game ID is required"}), 400

    user = add_or_get_user(sess, username)

    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    num_players_in_game = (
        sess.query(func.count(Player.id))
        .filter(Player.game_id == game_id)
        .scalar()
    ) or 0

    player = Player(
        user=user,
        game=game,
        player_num=num_players_in_game,
    )

    sess.add(player)
    sess.commit()

    return jsonify(game.to_json())


def _launch_game_inner(sess, game: Game) -> None:
    hexes = create_hex_map(game.map_size)  # type: ignore

    game_id: str = game.id  # type: ignore
    game_state = GameState(game_id, hexes)  # type: ignore

    players = (
        sess.query(Player)
        .filter(Player.game_id == game_id)
        .all()
    )

    animation_frame = AnimationFrame(
        game_id=game_id,
        turn_num=1,
        frame_num=0,
        player_num=None,
        game_state=game_state.to_json(),
    )

    for player in players:
        animation_frame = AnimationFrame(
            game_id=game_id,
            turn_num=1,
            frame_num=0,
            player_num=player.player_num,
            game_state=game_state.to_json(),
        )

        sess.add(animation_frame)

    game.launched = True  # type: ignore

    sess.commit()


@app.route('/api/launch_game', methods=['POST'])
@api_endpoint
def launch_game(sess):
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    game_id = data.get('game_id')

    if not game_id:
        return jsonify({"error": "Game ID is required"}), 400

    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    _launch_game_inner(sess, game)

    return jsonify(game.to_json())


@app.route('/api/game_state', methods=['GET'])
@api_endpoint
def get_game_state(sess):
    game_id = request.args.get('game_id')

    if not game_id:
        return jsonify({"error": "Game ID is required"}), 400

    player_num = request.args.get('player_num')

    if not player_num:
        return jsonify({"error": "Player number is required"}), 400

    turn_num = request.args.get('turn_num')

    if turn_num is None:
        return jsonify({"error": "Turn number is required"}), 400

    frame_num = request.args.get('frame_num')

    if frame_num is None:
        return jsonify({"error": "Frame number is required"}), 400

    animation_frame = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == turn_num)
        .filter(AnimationFrame.player_num == player_num)
        .filter(AnimationFrame.frame_num == frame_num)
        .one_or_none()
    )

    if animation_frame is None:
        return jsonify({"error": "Animation frame not found"}), 404
    
    game_state = animation_frame.game_state

    if game_state is None:
        return jsonify({"error": "Game state not found"}), 404
    
    return GameState.from_json(game_state).to_json()

