from datetime import datetime, timedelta
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import traceback
from typing import Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from animation_frame import AnimationFrame
from city import City, generate_random_city_name
from civ import Civ, create_starting_civ_options_for_players
from civ_template import CivTemplate
from civ_templates_list import CIVS
from database import SessionLocal
from game import Game
from game_player import GamePlayer
from game_state import GameState, update_staged_moves, get_most_recent_game_state, get_most_recent_game_state_json, get_turn_ended_by_player_num, set_turn_ended_by_player_num
from map import create_hex_map, generate_starting_locations, infer_map_size_from_num_players
from player import Player


from settings import (
    LOCAL, STARTING_CIV_VITALITY, CITY_CAPTURE_REWARD, UNIT_KILL_REWARD, CAMP_CLEAR_VP_REWARD, CAMP_CLEAR_CITY_POWER_REWARD, 
    BASE_FOOD_COST_OF_POP, ADDITIONAL_PER_POP_FOOD_COST, FAST_VITALITY_DECAY_RATE, VITALITY_DECAY_RATE, MAP_HOMOGENEITY_LEVEL, 
    NUM_STARTING_LOCATION_OPTIONS, PER_PLAYER_AREA, GOOD_HEX_PROBABILITY, TECH_VP_REWARD, GAME_END_SCORE, BASE_CITY_POWER_INCOME, 
    SURVIVAL_BONUS, EXTRA_GAME_END_SCORE_PER_PLAYER, MULLIGAN_PENALTY
)
from tech_template import TechTemplate
from tech_templates_list import TECHS
from unit_template import UnitTemplate
from unit_templates_list import UNITS
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from user import User, add_or_get_user, add_bot_users, BOT_USERNAMES
from utils import generate_unique_id
from redis_utils import rget_json, rset_json
from threading import Timer

# Create a logger
logger = logging.getLogger('__name__')
logger.setLevel(logging.DEBUG if LOCAL else logging.INFO)

# Create a handler that writes log messages to a file, with a max size of 1MB, and keep 3 backup logs
handler = RotatingFileHandler('app.log', maxBytes=1_000_000, backupCount=10)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
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


def broadcast(game_id):
    socketio.emit(
        'update', 
        room=game_id,
    )


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


def load_and_roll_turn_in_game(sess, game_id: str, turn_num: int, roll_id: str):
    with SessionLocal() as sess:
        game = sess.query(Game).filter(Game.id == game_id).first()

        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        game_state = get_most_recent_game_state(sess, game_id)
        game_state_copy = get_most_recent_game_state(sess, game_id)

        for player_num in game_state_copy.game_player_by_player_num.keys():
            staged_moves = rget_json(f'staged_moves:{game_id}:{player_num}') or []

            for move in staged_moves:
                if move.get('move_type') == 'enter_decline':
                    return

            game_state_copy.update_from_player_moves(player_num, staged_moves)

        for game_player in game_state_copy.game_player_by_player_num.values():
            if not game_player.civ_id:
                return

        if turn_num == game_state.turn_num and roll_id == game_state.roll_id and not game_state.game_over:
            if game.seconds_per_turn and not game_state.game_over and game_state.turn_num < 200:
                seconds_until_next_forced_roll = game.seconds_per_turn + min(game_state.turn_num, 30)
                next_forced_roll_at = (datetime.now() + timedelta(seconds=seconds_until_next_forced_roll)).timestamp()
                new_roll_id = generate_unique_id()

                Timer(seconds_until_next_forced_roll, load_and_roll_turn_in_game, args=[sess, game_id, turn_num + 1, new_roll_id]).start()
                game_state.next_forced_roll_at = next_forced_roll_at
                game_state.roll_id = new_roll_id
             
            game_state.end_turn(sess)
           
            print('Broadcasting: ', game_id)
            socketio.emit('update', room=game_id)  # type: ignore



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


@app.route('/api/set_turn_timer/<game_id>', methods=['POST'])
@api_endpoint
def set_turn_timer(sess, game_id: str):
    data = request.json

    seconds_per_turn = None
    if data:    
        seconds_per_turn = data.get('seconds_per_turn')

    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    game.seconds_per_turn = seconds_per_turn

    sess.commit()

    socketio.emit('update', room=game.id)  # type: ignore

    return jsonify(game.to_json())


@app.route('/api/add_bot_to_game/<game_id>', methods=['POST'])
@api_endpoint
def add_bot_to_game(sess, game_id: str):
    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    num_players_in_game = (
        sess.query(func.count(Player.id))
        .filter(Player.game_id == game_id)
        .scalar()
    ) or 0

    user = None
    for username in BOT_USERNAMES:
        if not (
            sess.query(Player)
            .join(User)
            .filter(User.username == username)
            .filter(Player.game_id == game_id)
            .first()
        ):
            user = add_or_get_user(sess, username)
            break

    bot_player = Player(
        user=user,
        game=game,
        player_num=num_players_in_game,
        is_bot=True,
    )

    sess.add(bot_player)
    sess.commit()

    socketio.emit('update', room=game.id)

    return jsonify({'game': game.to_json(), 'player_num': num_players_in_game})


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

    game_players = [GamePlayer(player_num=player.player_num, username=player.user.username, is_bot=player.is_bot) for player in players]

    starting_civ_options_for_players = create_starting_civ_options_for_players(game_players, starting_locations)

    starting_civs_for_players = {}

    game_state.game_player_by_player_num = {game_player.player_num: game_player for game_player in game_players}

    for player_num, civ_options_tups in starting_civ_options_for_players.items():
        game_player = game_state.game_player_by_player_num[player_num]
        if game_player.is_bot:
            civ_option_tup = civ_options_tups[0]
            civ, starting_location = civ_option_tup
            starting_city_name = generate_random_city_name(game_state)
            starting_city = City(civ, name=starting_city_name)
            starting_location.city = starting_city
            starting_city.hex = starting_location
            starting_city.populate_terrains_dict(game_state)
            game_state.cities_by_id[starting_city.id] = starting_city
            game_state.civs_by_id[civ.id] = civ
            civ.vitality = STARTING_CIV_VITALITY
            starting_city.hex.city = starting_city
            starting_civs_for_players[player_num] = [civ]
            game_player.civ_id = civ.id

        else:
            starting_civs_for_players[player_num] = []
            for civ_options_tup in civ_options_tups:
                civ, starting_location = civ_options_tup
                starting_civs_for_players[player_num].append(civ)
                starting_city_name = generate_random_city_name(game_state)
                starting_city = City(civ, name=starting_city_name)
                starting_location.city = starting_city
                starting_city.hex = starting_location
                starting_city.populate_terrains_dict(game_state)
                game_state.cities_by_id[starting_city.id] = starting_city
                game_state.civs_by_id[civ.id] = civ
                civ.vitality = STARTING_CIV_VITALITY

    game_state.special_mode_by_player_num = {game_player.player_num: 'starting_location' if not game_player.is_bot else None for game_player in game_players}

    game_state.midturn_update()
    game_state.refresh_visibility_by_civ(short_sighted=True)

    animation_frame = AnimationFrame(
        game_id=game_id,
        turn_num=1,
        frame_num=0,
        player_num=None,
        game_state=game_state.to_json(),
    )
    sess.add(animation_frame)

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

            return jsonify({'players': [player.user.username for player in players],
                            "turn_timer": game.seconds_per_turn,})

        return jsonify({"error": "Animation frame not found"}), 404
    

    game_state_json = rget_json(f'staged_game_state:{game_id}:{player_num}') or get_most_recent_game_state_json(sess, game_id)
    game_state = GameState.from_json(game_state_json)

    if game_state is None:
        return jsonify({"error": "Game state not found"}), 404
    
    return {'game_state': {
        **game_state.to_json(),
        "turn_ended_by_player_num": rget_json(f'turn_ended_by_player_num:{game_id}') or {},
    }}


@app.route('/api/movie/<game_id>', methods=['GET'])
@api_endpoint
def get_latest_turn_movie(sess, game_id):
    player_num = request.args.get('player_num')

    if player_num is None:
        return jsonify({"error": "Player number is required"}), 400

    turn_num = (
        sess.query(func.max(AnimationFrame.turn_num))
        .filter(AnimationFrame.game_id == game_id)
        .scalar()
    )

    animation_frames = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == turn_num)
        .filter(AnimationFrame.player_num == player_num)
        .order_by(AnimationFrame.frame_num)
        .all()
    )
    
    dream_game_state_json = rget_json(f'dream_game_state:{game_id}:{player_num}')
    dream_game_state_json_from_civ_perspectives = rget_json(f'dream_game_state_from_civ_perspectives:{game_id}:{player_num}') or []

    # Dream game state is the fake game state that gets sent to people who are in decline and haven't selected a civ

    staged_game_state_json = rget_json(f'staged_game_state:{game_id}:{player_num}')
    game_state = GameState.from_json(dream_game_state_json) if dream_game_state_json else GameState.from_json(staged_game_state_json) if staged_game_state_json else None

    game_state_json = None
    if game_state:
        game_player = game_state.game_player_by_player_num.get(int(player_num))
        if game_player:
            player_civ = game_state.civs_by_id.get(game_player.civ_id or '')
            if player_civ:
                game_state_json = game_state.to_json(from_civ_perspectives=[player_civ])
            else:

                if dream_game_state_json:
                    from_civ_perspectives = [game_state.civs_by_id[civ_id] for civ_id in dream_game_state_json_from_civ_perspectives]
                    game_state_json = game_state.to_json(from_civ_perspectives=from_civ_perspectives)

                else:
                    from_civ_perspectives = []

                    for decline_option in game_player.decline_options:
                        for civ in game_state.civs_by_id.values():
                            if civ.template.name == decline_option[1]:
                                from_civ_perspectives.append(civ)

                    game_state_json = game_state.to_json(from_civ_perspectives=from_civ_perspectives)

    return jsonify({
        'animation_frames': [*[{'game_state': {**animation_frame.game_state, "turn_ended_by_player_num": rget_json(f'turn_ended_by_player_num:{game_id}') or {}}, 'data': animation_frame.data} for animation_frame in animation_frames], 
                             *([{'game_state': {**game_state_json, "turn_ended_by_player_num": rget_json(f'turn_ended_by_player_num:{game_id}') or {},}, 'data': {}}] if game_state_json else [])], 
        'turn_num': turn_num,
    })

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

    games = (
        sess.query(Game)
        .join(Player)
        .filter(*user_filters)
        .filter(~Game.launched)
        .filter(Game.created_at > datetime.now() - timedelta(hours=3))
        .all()
    )

    return jsonify([game.to_json() for game in games])


@app.route('/api/starting_location/<game_id>', methods=['POST'])
@api_endpoint
def choose_initial_civ(sess, game_id):
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    player_num = data.get('player_num')

    if player_num is None:
        return jsonify({"error": "Username is required"}), 400
    
    city_id = data.get('city_id')

    if not city_id:
        return jsonify({"error": "City ID is required"}), 400
    
    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    game_state, from_civ_perspectives, _ = update_staged_moves(sess, game_id, player_num, [{'move_type': 'choose_starting_city', 'city_id': city_id}])

    city_list_one = [city for city in game_state.cities_by_id.values() if city.id == city_id]

    if len(city_list_one) == 0:
        return jsonify({"error": "City not found"}), 404
    
    city = city_list_one[0]

    civ = city.civ

    return jsonify({'game_state': game_state.to_json(from_civ_perspectives=from_civ_perspectives)})


@app.route('/api/player_input/<game_id>', methods=['POST'])
@api_endpoint
def enter_player_input(sess, game_id):
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    player_num = data.get('player_num')

    if player_num is None:
        return jsonify({"error": "Username is required"}), 400
    
    player_input = data.get('player_input')

    if not player_input:
        return jsonify({"error": "Player input is required"}), 400

    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    _, from_civ_perspectives, game_state_to_return_json = update_staged_moves(sess, game_id, player_num, [player_input])

    if player_input.get('move_type') == 'enter_decline':
        socketio.emit('mute_timer', {'turn_num': game_state_to_return_json['turn_num']}, room=game_id)  # type: ignore

    return jsonify({'game_state': game_state_to_return_json})
    # return jsonify({'game_state': game_state.to_json()})


@app.route('/api/end_turn/<game_id>', methods=['POST'])
@api_endpoint
def end_turn(sess, game_id):
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    player_num = data.get('player_num')

    if player_num is None:
        return jsonify({"error": "Username is required"}), 400
    
    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404

    game_state = get_most_recent_game_state(sess, game_id)

    turn_ended_by_player_num = get_turn_ended_by_player_num(game_id)

    turn_ended_by_player_num[player_num] = True

    socketio.emit('turn_end_change', {'player_num': player_num, 'turn_ended': True}, room=game_id)

    if game_state.turn_should_end(turn_ended_by_player_num):
        print("starting turn roll")
        socketio.emit('start_turn_roll', {}, room=game_id)
        if game.seconds_per_turn and not game_state.game_over and game_state.turn_num < 200:
            seconds_until_next_forced_roll = game.seconds_per_turn + min(game_state.turn_num, 30)
            next_forced_roll_at = (datetime.now() + timedelta(seconds=seconds_until_next_forced_roll)).timestamp()
            new_roll_id = generate_unique_id()

            Timer(seconds_until_next_forced_roll, load_and_roll_turn_in_game, args=[sess, game_id, game_state.turn_num + 1, new_roll_id]).start()
            game_state.next_forced_roll_at = next_forced_roll_at
            game_state.roll_id = new_roll_id

        game_state.end_turn(sess)

        print("sending update signal")
        broadcast(game_id)
    else:
        rset_json(f'turn_ended_by_player_num:{game_id}', turn_ended_by_player_num)

    return jsonify({})


@app.route('/api/pause/<game_id>', methods=['POST'])
@api_endpoint
def pause_game(sess, game_id):
    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    most_recent_game_state_animation_frame = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.player_num == None)
        .order_by(AnimationFrame.turn_num.desc())
        .order_by(AnimationFrame.frame_num.desc())
        .first()
    )

    game_state = GameState.from_json(most_recent_game_state_animation_frame.game_state)

    game_state.roll_id = None
    game_state.next_forced_roll_at = None

    most_recent_game_state_animation_frame.game_state = game_state.to_json()

    sess.commit()

    socketio.emit('mute_timer', {'turn_num': game_state.turn_num}, room=game_id)  # type: ignore

    return jsonify({})


@app.route('/api/unend_turn/<game_id>', methods=['POST'])
@api_endpoint
def unend_turn(sess, game_id):
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    player_num = data.get('player_num')

    if player_num is None:
        return jsonify({"error": "Username is required"}), 400
    
    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404

    set_turn_ended_by_player_num(game_id, player_num, False)

    socketio.emit('turn_end_change', {'player_num': player_num, 'turn_ended': False}, room=game_id)

    return jsonify({})


@app.route('/api/building_choices/<game_id>/<city_id>', methods=['GET'])
@api_endpoint
def get_building_choices(sess, game_id, city_id):
    game = sess.query(Game).filter(Game.id == game_id).first()

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    game_state = get_most_recent_game_state(sess, game_id)

    city = game_state.cities_by_id.get(city_id)

    if not city:
        return jsonify({"error": "City not found"}), 404

    building_choices = city.get_available_buildings()

    print('choices', building_choices)

    return jsonify({'building_choices': [building_choice.to_json() for building_choice in building_choices]})


@app.route('/api/game_constants', methods=['GET'])
@api_endpoint
def get_game_constants(sess):
    return jsonify({
        'city_capture_reward': CITY_CAPTURE_REWARD,
        'unit_kill_reward': UNIT_KILL_REWARD,
        'camp_clear_reward': CAMP_CLEAR_VP_REWARD,
        'camp_clear_city_power_reward': CAMP_CLEAR_CITY_POWER_REWARD,
        'base_food_cost_of_pop': BASE_FOOD_COST_OF_POP,
        'additional_per_pop_food_cost': ADDITIONAL_PER_POP_FOOD_COST,
        'fast_vitality_decay_rate': FAST_VITALITY_DECAY_RATE,
        'vitality_decay_rate': VITALITY_DECAY_RATE,
        'map_homogeneity_level': MAP_HOMOGENEITY_LEVEL,
        'num_starting_location_options': NUM_STARTING_LOCATION_OPTIONS,
        'per_player_area': PER_PLAYER_AREA,
        'starting_civ_vitality': STARTING_CIV_VITALITY,
        'good_hex_probability': GOOD_HEX_PROBABILITY,
        'tech_vp_reward': TECH_VP_REWARD,
        'game_end_score': GAME_END_SCORE,
        'extra_game_end_score_per_player': EXTRA_GAME_END_SCORE_PER_PLAYER,
        'base_city_power_income': BASE_CITY_POWER_INCOME,
        'survival_bonus': SURVIVAL_BONUS,
        'mulligan_penalty': MULLIGAN_PENALTY,
    })


@app.route('/api/civ_templates', methods=['GET'])
@api_endpoint
def get_civ_templates(sess):
    return jsonify({civ_template['name']: CivTemplate.from_json(civ_template).to_json() for civ_template in CIVS.values()})


@app.route('/api/unit_templates', methods=['GET'])
@api_endpoint
def get_unit_templates(sess):
    return jsonify({unit_template['name']: UnitTemplate.from_json(unit_template).to_json() for unit_template in UNITS.values()})


@app.route('/api/tech_templates', methods=['GET'])
@api_endpoint
def get_tech_templates(sess):
    return jsonify({tech_template['name']: {**TechTemplate.from_json(tech_template).to_json()} for tech_template in TECHS.values()})


@app.route('/api/building_templates', methods=['GET'])
@api_endpoint
def get_building_templates(sess):
    return jsonify({building_template['name']: BuildingTemplate.from_json(building_template).to_json() for building_template in BUILDINGS.values()})


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
    with SessionLocal() as sess:
        add_bot_users(sess)
    if LOCAL:
        socketio.run(app, host='0.0.0.0', port=5002, debug=True)  # type: ignore
    else:
        socketio.run(app, host='0.0.0.0', port=5023)  # type: ignore
