from civ import create_starting_civ_options_for_players
from game_player import GamePlayer
from game_state import GameState
from map import create_hex_map, generate_starting_locations
from settings import MAX_PLAYERS, STARTING_CIV_VITALITY
from logging_setup import logger


def new_game_state(game_id: str, game_players: list[GamePlayer]):
    logger.info(f"Creating game state for game {game_id} with {len(game_players)} players")

    num_players = len(game_players)

    logger.info(f"Creating hex map for {num_players} players")
    hexes = create_hex_map(num_players)

    logger.info(f"Creating game state for game {game_id} with {num_players} players")
    game_state = GameState(game_id, hexes)

    assert num_players <= MAX_PLAYERS

    logger.info(f"Generating starting locations for {num_players} players")
    starting_locations = generate_starting_locations(hexes, 3 * num_players)
    logger.info(f"Generating starting civs for {num_players} players")
    starting_civ_options_for_players = create_starting_civ_options_for_players(game_players, starting_locations)

    starting_civs_for_players = {}

    game_state.game_player_by_player_num = {game_player.player_num: game_player for game_player in game_players}

    logger.info(f"Initializing wonders")
    game_state.initialize_wonders()

    logger.info(f"Creating starting civs")
    for player_num, civ_options_tups in starting_civ_options_for_players.items():
        game_player = game_state.game_player_by_player_num[player_num]
        if game_player.is_bot:
            civ_option_tup = civ_options_tups[0]
            civ, starting_location = civ_option_tup
            starting_city = game_state.new_city(civ, starting_location)
            game_state.register_city(starting_city)
            starting_city.capitalize(game_state)

            game_state.civs_by_id[civ.id] = civ
            civ.vitality = STARTING_CIV_VITALITY * game_player.vitality_multiplier
            starting_civs_for_players[player_num] = [civ]
            game_player.civ_id = civ.id
            game_player.all_civ_ids.append(civ.id)

        else:
            starting_civs_for_players[player_num] = []
            for civ_options_tup in civ_options_tups:
                civ, starting_location = civ_options_tup
                starting_civs_for_players[player_num].append(civ)
                starting_city = game_state.new_city(civ, starting_location)
                game_state.register_city(starting_city)
                game_state.civs_by_id[civ.id] = civ
                civ.vitality = STARTING_CIV_VITALITY * game_player.vitality_multiplier

    logger.info(f"Final game setup")
    game_state.special_mode_by_player_num = {game_player.player_num: 'starting_location' if not game_player.is_bot else None for game_player in game_players}

    game_state.midturn_update()
    game_state.refresh_visibility_by_civ(short_sighted=True)

    logger.info(f"Game state created")
    return game_state, starting_civs_for_players