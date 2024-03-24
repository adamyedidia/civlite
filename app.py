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
from game import Game, TimerStatus
from game_player import GamePlayer
from game_state import GameState, update_staged_moves, get_most_recent_game_state
from map import create_hex_map, generate_starting_locations, infer_map_size_from_num_players
from player import Player

from utils import dream_key, staged_game_state_key, staged_moves_key, dream_key_from_civ_perspectives, generate_unique_id, moves_processing_key


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
from redis_utils import rget_json, rset_json, rset, rget, CodeBlockCounter, await_empty_counter

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

    game = Game.get(sess, socketio, game_id)

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

    seconds_per_turn: int | None = None
    if data:    
        seconds_per_turn = data.get('seconds_per_turn')

    game = Game.get(sess, socketio, game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    game.seconds_per_turn = seconds_per_turn

    sess.commit()

    socketio.emit('update', room=game.id)  # type: ignore

    return jsonify(game.to_json())


@app.route('/api/add_bot_to_game/<game_id>', methods=['POST'])
@api_endpoint
def add_bot_to_game(sess, game_id: str):
    game = Game.get(sess, socketio, game_id)

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

    socketio.emit('update', room=game.id)  # type: ignore

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
            starting_city = game_state.new_city(civ, starting_location)
            game_state.register_city(starting_city)
            starting_city.capitalize(game_state)

            game_state.civs_by_id[civ.id] = civ
            civ.vitality = STARTING_CIV_VITALITY
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

        rset_json(dream_key(game_id, player.player_num, 1), game_state.to_json())
        rset_json(dream_key_from_civ_perspectives(game_id, player.player_num, 1), [civ.id for civ in starting_civs_for_players[player.player_num]])

        sess.add(animation_frame)

    game.start_turn()
    game.launched = True  # type: ignore

    sess.commit()


@app.route('/api/launch_game/<game_id>', methods=['POST'])
@api_endpoint
def launch_game(sess, game_id):
    game = Game.get(sess, socketio, game_id)

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


@app.route('/api/game_status/<game_id>', methods=['GET'])
@api_endpoint
def get_game_state(sess, game_id):
    animation_frame = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == 1)
        .filter(AnimationFrame.player_num == 0)
        .filter(AnimationFrame.frame_num == 0)
        .one_or_none()
    )

    if animation_frame is None:
        game = Game.get(sess, socketio, game_id)

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
     
    return jsonify({'game_started': True})


@app.route('/api/movie/frame/<game_id>/<frame_num>', methods=['GET'])
@api_endpoint
def get_movie_frame(sess, game_id, frame_num):
    player_num = request.args.get('player_num')

    if player_num is None:
        return jsonify({"error": "Player number is required"}), 400

    turn_num = (
        sess.query(func.max(AnimationFrame.turn_num))
        .filter(AnimationFrame.game_id == game_id)
        .scalar()
    )

    animation_frame: Optional[AnimationFrame] = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == turn_num)
        .filter(AnimationFrame.player_num == player_num)
        .filter(AnimationFrame.frame_num == frame_num)
        .one_or_none()
    )

    if animation_frame is None:
        return jsonify({"error": "Animation frame not found"}), 404
    
    return jsonify({
        'game_state': animation_frame.game_state,
        'turn_num': turn_num,
        'data': animation_frame.data,
    })


@app.route('/api/movie/last_frame/<game_id>', methods=['GET'])
@api_endpoint
def get_most_recent_state(sess, game_id):
    player_num = request.args.get('player_num')

    if player_num is None:
        return jsonify({"error": "Player number is required"}), 400
    
    game = Game.get(sess, socketio, game_id)
    if game is None:
        return jsonify({"error": "Game not found"}), 404

    turn_num = (
        sess.query(func.max(AnimationFrame.turn_num))
        .filter(AnimationFrame.game_id == game_id)
        .scalar()
    )
    
    assert turn_num == game.turn_num

    last_animation_frame = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == turn_num)
        .filter(AnimationFrame.player_num == None)
        .order_by(AnimationFrame.frame_num.desc())
        .first()
    )

    num_animation_frames_for_player = (
        sess.query(func.count(AnimationFrame.id))
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == turn_num)
        .filter(AnimationFrame.player_num == player_num)
        .scalar()
    )
    
    dream_game_state_json = rget_json(dream_key(game_id, int(player_num), turn_num))
    dream_game_state_json_from_civ_perspectives = rget_json(dream_key_from_civ_perspectives(game_id, int(player_num), turn_num)) or []

    # Dream game state is the fake game state that gets sent to people who are in decline and haven't selected a civ
    # TODO(dfarhi) clean this up and vastly simplify dream states now that they are only for the first turn.

    staged_game_state_json = rget_json(staged_game_state_key(game_id, int(player_num), turn_num))
    game_state = (
        GameState.from_json(dream_game_state_json) if dream_game_state_json 
        else GameState.from_json(staged_game_state_json) if staged_game_state_json 
        else GameState.from_json(last_animation_frame.game_state) if last_animation_frame else None
    )

    game_state_json = None
    if game_state:
        game_player = game_state.game_player_by_player_num.get(int(player_num))
        if game_player:
            player_civ = game_state.civs_by_id.get(game_player.civ_id or '')
            if player_civ:
                game_state_json = game_state.to_json(from_civ_perspectives=[player_civ])
            else:
                from_civ_perspectives = [game_state.civs_by_id[civ_id] for civ_id in dream_game_state_json_from_civ_perspectives]
                game_state_json = game_state.to_json(from_civ_perspectives=from_civ_perspectives)

    return jsonify({
        'game_state': game_state_json,
        'turn_num': turn_num,
        'num_frames': num_animation_frames_for_player,
    })


@app.route('/api/decline_view/<game_id>', methods=['GET'])
@api_endpoint
def get_decline_view(sess, game_id):
    turn_num = (
        sess.query(func.max(AnimationFrame.turn_num))
        .filter(AnimationFrame.game_id == game_id)
        .scalar()
    )

    animation_frame = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == turn_num)
        .filter(AnimationFrame.is_decline == True)
        .one_or_none()
    )

    game_state = GameState.from_json(animation_frame.game_state)

    game_state_json = game_state.to_json(include_city_civ_details=True)

    return jsonify({
        'game_state': game_state_json,
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
    
    game = Game.get(sess, socketio, game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    game_state, from_civ_perspectives, _, _ = update_staged_moves(sess, game_id, player_num, [{'move_type': 'choose_starting_city', 'city_id': city_id}])
  
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

    turn_num = data.get('turn_num')

    if not turn_num:
        return jsonify({"error": "Turn number is required"}), 400

    game = Game.get(sess, socketio, game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    if not game.accepting_moves(turn_num=turn_num):
        return jsonify({"error": "Turn is over"}), 400
    
    # This block counts how many threads are currently running turns.
    # We won't roll the turn until they are done.
    with CodeBlockCounter(moves_processing_key(game_id, turn_num)):
        # Conceivably, the turn could have rolled while we were incrementing the counter
        if not game.accepting_moves(turn_num=turn_num):
            return jsonify({"error": "Turn is over"}), 400
        
        # Now do the actual roll.
        _, _, game_state_to_return_json, decline_eviction_player = update_staged_moves(sess, game_id, player_num, [player_input])      

        if decline_eviction_player is not None:
            print(f"app.py evicting player {decline_eviction_player}")
            game.set_turn_ended_by_player_num(decline_eviction_player, False)
            socketio.emit("decline_evicted", {'player_num': decline_eviction_player}, room=game_id)  # type: ignore

    return jsonify({'game_state': game_state_to_return_json})
    # return jsonify({'game_state': game_state.to_json()})


@app.route('/api/turn_timer_status/<game_id>/<turn_num>', methods=['GET'])
@api_endpoint
def turn_ended_status(sess, game_id, turn_num):
    game = Game.get(sess, socketio, game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    if int(turn_num) != game.turn_num:
        print(f"Turn num mismatch in game {game_id}: {turn_num} != {game.turn_num}")
        return jsonify({"error": f"Wrong turn {turn_num}; game is on {game.turn_num}"}), 404

    return jsonify({
        "turn_ended_by_player_num": game.get_turn_ended_all_players(),
        "overtime_decline_civs": game.get_overtime_decline_civs(),
        "next_forced_roll_at": game.next_forced_roll_at,
        "status": game.timer_status.value,
        })

@app.route('/api/end_turn/<game_id>', methods=['POST'])
@api_endpoint
def end_turn(sess, game_id):
    data = request.json

    if not data:
        return jsonify({"error": "Invalid data"}), 400
    
    player_num = data.get('player_num')

    if player_num is None:
        return jsonify({"error": "Username is required"}), 400
    
    game = Game.get(sess, socketio, game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404

    game.set_turn_ended_by_player_num(player_num, True, via_player_input=True)
    game.roll_turn_if_needed(sess)

    return jsonify({})


@app.route('/api/pause/<game_id>', methods=['POST'])
@api_endpoint
def pause_game(sess, game_id):
    game = Game.get(sess, socketio, game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    game.pause(sess)   

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
    
    game = Game.get(sess, socketio, game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    if game.timer_status == TimerStatus.OVERTIME and not game.has_player_declined(player_num, game.turn_num):
        return jsonify({"error": "Can't unend turn after time"}), 400

    game.set_turn_ended_by_player_num(player_num, False, via_player_input=True)

    return jsonify({})


@app.route('/api/building_choices/<game_id>/<city_id>', methods=['GET'])
@api_endpoint
def get_building_choices(sess, game_id, city_id):
    game = Game.get(sess, socketio, game_id)

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


@app.route('/api/templates', methods=['GET'])
@api_endpoint
def get_all_templates(sess):
    return jsonify({
        'CIVS': {civ_template['name']: CivTemplate.from_json(civ_template).to_json() for civ_template in CIVS.values()},
        'UNITS': {unit_template['name']: UnitTemplate.from_json(unit_template).to_json() for unit_template in UNITS.values()},
        'TECHS': {tech_template['name']: {**TechTemplate.from_json(tech_template).to_json()} for tech_template in TECHS.values()},
        'BUILDINGS': {building_template['name']: BuildingTemplate.from_json(building_template).to_json() for building_template in BUILDINGS.values()},
    })

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
