from datetime import datetime, timedelta
from functools import wraps
from logging_setup import logger
import traceback
from typing import Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from animation_frame import AnimationFrame
from civ_templates_list import CIVS
from database import SessionLocal
from game import Game, TimerStatus
from game_player import GamePlayer
from game_state import GameState, make_game_statistics_plots
from new_game_state import new_game_state
from player import Player
from tenet_template_list import TENETS
from utils import dream_key, dream_key_from_civ_perspectives, generate_unique_id, moves_processing_key


from settings import (
    LOCAL, STARTING_CIV_VITALITY, CITY_CAPTURE_REWARD, UNIT_KILL_REWARD, CAMP_CLEAR_VP_REWARD, CAMP_CLEAR_CITY_POWER_REWARD, 
    BASE_FOOD_COST_OF_POP, ADDITIONAL_PER_POP_FOOD_COST, VITALITY_DECAY_RATE, MAP_HOMOGENEITY_LEVEL, 
    NUM_STARTING_LOCATION_OPTIONS, GOOD_HEX_PROBABILITY, TECH_VP_REWARD, GAME_END_SCORE, BASE_CITY_POWER_INCOME, 
    BASE_SURVIVAL_BONUS, SURVIVAL_BONUS_PER_AGE, EXTRA_GAME_END_SCORE_PER_PLAYER, MAX_PLAYERS
)
from tech_template import TechTemplate
from tech_templates_list import TECHS
from unit_template import UnitTemplate
from unit_templates_list import UNITS
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from wonder_templates_list import WONDERS
from user import User, add_or_get_user, add_bot_users, BOT_USERNAMES
from redis_utils import rget_json, rset_json, rset, rget, CodeBlockCounter, await_empty_counter


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
    
    players_in_game = (
        sess.query(Player)
        .filter(Player.game_id == game_id)
        .all()
    )

    # If the player is already in the game, direct them to the lobby.
    matching_player = next((player for player in players_in_game if player.user.username == username), None)
    if matching_player is not None:
        player = matching_player
    else:
        num_players_in_game = len(players_in_game)

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
    game = Game.get(sess, socketio, game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404

    data = request.json
    
    if not data:    
        return jsonify({"error": "Invalid data"}), 400

    seconds_per_turn = data.get('seconds_per_turn')

    game.seconds_per_turn = seconds_per_turn

    sess.commit()

    socketio.emit('update', room=game.id)  # type: ignore

    return jsonify(game.to_json())


@app.route('/api/set_vitality_multiplier/<game_id>', methods=['POST'])
@api_endpoint
def set_vitality_multiplier(sess, game_id: str):
    game = Game.get(sess, socketio, game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    data: dict[str, float] = request.json  # type: ignore

    vitality_multiplier = data['vitality_multiplier']
    player_num = int(data['player_num'])
    player = game.player_by_num(player_num)
    player.vitality_multiplier = vitality_multiplier
    sess.commit()
    socketio.emit('update', room=game.id)  # type: ignore
    return jsonify(game.to_json())


@app.route('/api/add_bot_to_game/<game_id>', methods=['POST'])
@api_endpoint
def add_bot_to_game(sess, game_id: str):
    game = Game.get(sess, socketio, game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    # Fetch all current player numbers in the game to find the first available slot
    existing_player_nums = {player.player_num for player in sess.query(Player.player_num).filter(Player.game_id == game_id).all()}

    # Find the smallest non-negative integer not in the existing player numbers
    new_player_num = 0
    while new_player_num in existing_player_nums:
        new_player_num += 1

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
        player_num=new_player_num,
        is_bot=True,
        vitality_multiplier=1.25,
    )

    sess.add(bot_player)
    sess.commit()

    socketio.emit('update', room=game.id)  # type: ignore

    return jsonify({'game': game.to_json(), 'player_num': new_player_num})


@app.route('/api/delete_player/<game_id>/<username>', methods=['DELETE'])
@api_endpoint
def delete_player(sess, game_id: str, username: str):
    game = Game.get(sess, socketio, game_id)

    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    player = (
        sess.query(Player)
        .join(User)  # Explicitly join the User table
        .filter(Player.game_id == game_id)
        .filter(User.username == username)  # Use User.username instead of Player.user.username
        .one_or_none()
    )

    if not player:
        return jsonify({"error": "Player not found"}), 404

    sess.delete(player)
    sess.commit()
    socketio.emit('update', room=game.id)  # type: ignore
    return jsonify({"success": True})

def _launch_game_inner(sess, game: Game) -> None:
    game_id: str = game.id

    players = (
        sess.query(Player)
        .filter(Player.game_id == game_id)
        .all()
    )

    game_players = [GamePlayer(player_num=player.player_num, username=player.user.username, is_bot=player.is_bot, vitality_multiplier=player.vitality_multiplier) for player in players]

    game_state, starting_civs_for_players = new_game_state(game_id, game_players)

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

            return jsonify({
                'game_name': game.name,
                'players': [player.to_json() for player in players],
                "turn_timer": game.seconds_per_turn,})

        return jsonify({"error": "Animation frame not found"}), 404
     
    return jsonify({'game_started': True})


@app.route('/api/movie/frame/<game_id>/<frame_num>', methods=['GET'])
@api_endpoint
def get_movie_frame(sess, game_id, frame_num):
    game = Game.get(sess, socketio, game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    player_num = request.args.get('player_num')

    if player_num is None:
        return jsonify({"error": "Player number is required"}), 400

    animation_frame: Optional[AnimationFrame] = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == game.turn_num)
        .filter(AnimationFrame.player_num == player_num)
        .filter(AnimationFrame.frame_num == frame_num)
        .one_or_none()
    )

    if animation_frame is None:
        return jsonify({"error": "Animation frame not found"}), 404
    
    return jsonify({
        'game_state': animation_frame.game_state,
        'turn_num': game.turn_num,
        'data': animation_frame.data,
    })


@app.route('/api/final_movie/<game_id>/<turn_num>', methods=['GET'])
@api_endpoint
def get_final_movie(sess, game_id, turn_num):
    game = Game.get(sess, socketio, game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    animation_frame: Optional[AnimationFrame] = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.player_num == None)
        .filter(AnimationFrame.frame_num == 1)
        .filter(AnimationFrame.turn_num == turn_num)
        .one_or_none()
    )

    if animation_frame is None:
        return jsonify({"error": "Animation frame not found"}), 404
    
    return jsonify({
        'game_state': animation_frame.game_state,
        'turn_num': game.turn_num,
        'data': animation_frame.data,
    })


@app.route('/api/reset_game/', methods=['POST'])
@api_endpoint
def reset_game(sess):
    data = request.json
    print(f"reset_game {data}")
    if not data:
        print("no data")
        return jsonify({"error": "Invalid data"}), 400


    game_id = data.get('game_id')
    turn_num = int(data.get('turn_num'))

    if not game_id or not turn_num:
        print("no game id or turn num")
        return jsonify({"error": "Game ID and turn number are required"}), 400

    game = Game.get(sess, socketio, game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    game.reset_to_turn(turn_num, sess)
    return jsonify({"success": True})

@app.route('/api/movie/last_frame/<game_id>', methods=['GET'])
@api_endpoint
def get_most_recent_state(sess, game_id):
    player_num = request.args.get('player_num')

    if player_num is None:
        return jsonify({"error": "Player number is required"}), 400
    
    game = Game.get(sess, socketio, game_id)
    if game is None:
        return jsonify({"error": "Game not found"}), 404

    last_animation_frame = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == game.turn_num)
        .filter(AnimationFrame.player_num == None)
        .order_by(AnimationFrame.frame_num.desc())
        .first()
    )

    num_animation_frames_for_player = (
        sess.query(func.count(AnimationFrame.id))
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.turn_num == game.turn_num)
        .filter(AnimationFrame.player_num == player_num)
        .scalar()
    )
    
    dream_game_state_json = rget_json(dream_key(game_id, int(player_num), game.turn_num))
    dream_game_state_json_from_civ_perspectives = rget_json(dream_key_from_civ_perspectives(game_id, int(player_num), game.turn_num)) or []

    # Dream game state is the fake game state that gets sent to people who are in decline and haven't selected a civ
    # TODO(dfarhi) clean this up and vastly simplify dream states now that they are only for the first turn.

    staged_game_state_json = rget_json(game._staged_game_state_key(int(player_num), game.turn_num))
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
        'turn_num': game.turn_num,
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

    game_state_json = game_state.to_json()

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
    
    game_state_to_return_json, _ = game.update_staged_moves(sess, player_num, [{'move_type': 'choose_starting_city', 'city_id': city_id}])
  
    return jsonify({'game_state': game_state_to_return_json})


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
        
        # Now do the actual update.
        game_state_to_return_json, decline_eviction_player = game.update_staged_moves(sess, player_num, [player_input])      

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
        "status": game.timer_status.value,  # type: ignore
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

@app.route('/api/postgame_stats/<game_id>', methods=['GET'])
@api_endpoint
def get_postgame_stats(sess, game_id):
    game = Game.get(sess, socketio, game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    assert game.game_over
    
    civ_infos, stats, movie_frames = make_game_statistics_plots(sess, game.id)
    return jsonify({
        'civ_infos': civ_infos,
        'stats': stats,
        'movie_frames': movie_frames,
    })


@app.route('/final_graphs/<game_id>', methods=['GET'])
@api_endpoint
def final_graphs(sess, game_id):
    game = Game.get(sess, socketio, game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    return jsonify({})


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
        'vitality_decay_rate': VITALITY_DECAY_RATE,
        'map_homogeneity_level': MAP_HOMOGENEITY_LEVEL,
        'num_starting_location_options': NUM_STARTING_LOCATION_OPTIONS,
        'starting_civ_vitality': STARTING_CIV_VITALITY,
        'good_hex_probability': GOOD_HEX_PROBABILITY,
        'tech_vp_reward': TECH_VP_REWARD,
        'game_end_score': GAME_END_SCORE,
        'extra_game_end_score_per_player': EXTRA_GAME_END_SCORE_PER_PLAYER,
        'base_city_power_income': BASE_CITY_POWER_INCOME,
        'base_survival_bonus': BASE_SURVIVAL_BONUS,
        'survival_bonus_per_age': SURVIVAL_BONUS_PER_AGE,
        'max_players': MAX_PLAYERS,
    })


@app.route('/api/templates', methods=['GET'])
@api_endpoint
def get_all_templates(sess):
    return jsonify({
        'CIVS': {civ_template.name: civ_template.to_json() for civ_template in CIVS.all()},
        'UNITS': {unit_template.name: unit_template.to_json() for unit_template in UNITS.all()},
        'TECHS': {tech.name: tech.to_json() for tech in TECHS.all()},
        'BUILDINGS': {building_template.name: building_template.to_json() for building_template in BUILDINGS.all()},
        'WONDERS': {wonder_template.name: wonder_template.to_json() for wonder_template in WONDERS.all()},
        'TENETS': {tenet_template.name: tenet_template.to_json() for tenet_template in TENETS.all()}
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
