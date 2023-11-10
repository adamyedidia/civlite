from datetime import datetime, timedelta
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from animation_frame import AnimationFrame
from city import City
from civ import Civ, create_starting_civ_options_for_players
from civ_template import CivTemplate
from civ_templates_list import CIVS
from database import SessionLocal
from game import Game
from game_player import GamePlayer
from game_state import GameState
from map import create_hex_map, generate_starting_locations, infer_map_size_from_num_players
from player import Player

from settings import LOCAL
from user import User, add_or_get_user
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
    
    user = add_or_get_user(sess, username)

    game = Game(
        id=generate_unique_id(),
        name=f'{username}\'s game',
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

    socketio.emit('updateGames', room='lobby')  # type: ignore

    return jsonify(game.to_json())


@app.route('/api/join_game/<game_id>', methods=['POST'])
@api_endpoint
def join_game(sess, game_id: str):
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

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

    socketio.emit('update', room=game.id)  # type: ignore

    return jsonify({'game': game.to_json(), 'player_num': player.player_num})


def _launch_game_inner(sess, game: Game) -> None:
    game_id: str = game.id  # type: ignore

    players = (
        sess.query(Player)
        .filter(Player.game_id == game_id)
        .all()
    )

    num_players = len(players)

    map_size = infer_map_size_from_num_players(num_players)

    hexes = create_hex_map(map_size)  # type: ignore

    game_state = GameState(game_id, hexes)  # type: ignore

    assert num_players <= 8

    starting_locations = generate_starting_locations(hexes, 3 * num_players)

    game_players = [GamePlayer(player_num=player.player_num, username=player.user.username) for player in players]

    starting_civ_options_for_players = create_starting_civ_options_for_players(game_players, starting_locations)

    starting_civs_for_players = {}

    for player_num, civ_options_tups in starting_civ_options_for_players.items():
        starting_civs_for_players[player_num] = []
        for civ_options_tup in civ_options_tups:
            civ, starting_location = civ_options_tup
            starting_civs_for_players[player_num].append(civ)
            starting_city = City(civ)
            starting_location.city = starting_city
            starting_city.hex = starting_location
            game_state.cities.append(starting_city)
            game_state.civs.append(civ)

    game_state.refresh_visibility_by_civ()

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
            game_state=game_state.to_json(from_civ_perspectives=starting_civs_for_players[player.player_num]),
        )

        sess.add(animation_frame)

    game.launched = True  # type: ignore

    sess.commit()


@app.route('/api/launch_game/<game_id>', methods=['POST'])
@api_endpoint
def launch_game(sess, game_id):
    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    _launch_game_inner(sess, game)

    socketio.emit('update', room=game.id)  # type: ignore
    socketio.emit('updateGames', room='lobby')  # type: ignore

    return jsonify(game.to_json())


@app.route('/api/players_in_game/<game_id>', methods=['GET'])
@api_endpoint
def get_players_in_game(sess, game_id: str):
    players = (
        sess.query(Player)
        .options(joinedload(Player.user))
        .filter(Player.game_id == game_id)
        .all()
    )

    return jsonify([player.user.username for player in players])


@app.route('/api/game_state/<game_id>', methods=['GET'])
@api_endpoint
def get_game_state(sess, game_id):

    player_num = request.args.get('player_num')

    if player_num is None:
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
        game = (
            sess.query(Game)
            .filter(Game.id == game_id)
            .one_or_none()
        )

        if game is None:
            return jsonify({"error": "Game not found"}), 404
        
        if not game.launched:
            players = (
                sess.query(Player)
                .options(joinedload(Player.user))
                .filter(Player.game_id == game_id)
                .all()
            )

            return jsonify({'players': [player.user.username for player in players]})

        return jsonify({"error": "Animation frame not found"}), 404
    
    game_state = animation_frame.game_state

    if game_state is None:
        return jsonify({"error": "Game state not found"}), 404
    
    return {'game_state': game_state}


@app.route('/api/open_games', methods=['GET'])
@api_endpoint
def get_open_games(sess):
    username = request.args.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    user = (
        sess.query(User)
        .filter(User.username == username)
        .one_or_none()
    )

    if user:
        user_filters = [Player.user_id != user.id]
    else:
        user_filters = []

    print(user)

    games = (
        sess.query(Game)
        .join(Player)
        .filter(*user_filters)
        .filter(~Game.launched)
        .filter(Game.created_at > datetime.now() - timedelta(hours=3))
        .all()
    )

    return jsonify([game.to_json() for game in games])


@app.route('/api/civ_templates', methods=['GET'])
@api_endpoint
def get_civ_templates(sess):
    return jsonify({civ_template['name']: CivTemplate.from_json(civ_template).to_json() for civ_template in CIVS.values()})


@socketio.on('connect')
def on_connect():
    pass

@socketio.on('join')
def on_join(data):
    print(data)
    username = data['username'] if 'username' in data else 'anonymous'
    room = data['room']
    join_room(room)
    logger.info(f'{username} joined {room}')
    
@socketio.on('leave')
def on_leave(data):
    print(data)
    username = data['username'] if 'username' in data else 'anonymous'
    room = data['room']
    leave_room(room)
    logger.info(f'{username} left {room}') 


if __name__ == '__main__':
    if LOCAL:
        socketio.run(app, host='0.0.0.0', port=5001, debug=True)  # type: ignore
    else:
        socketio.run(app, host='0.0.0.0', port=5015)  # type: ignore
