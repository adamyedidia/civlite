import copy
import pickle
import random
from typing import TYPE_CHECKING

from game_player import GamePlayer
from new_game_state import new_game_state

if TYPE_CHECKING:
    from game_state import GameState

# def game_state_roll_turn(game_state: 'GameState'):
#         sess = None
#         intermediate_states = []
#         def add_intermediate_state():
#             intermediate_states.append(copy.deepcopy(game_state.to_json()))

#         print(f"GameState incrementing turn {game_state.turn_num} -> {game_state.turn_num + 1}")
#         game_state.turn_num += 1

#         game_state.barbarians.target1 = game_state.pick_random_hex()
#         game_state.barbarians.target2 = game_state.pick_random_hex()
#         game_state.barbarians.target1_coords = game_state.barbarians.target1.coords
#         game_state.barbarians.target2_coords = game_state.barbarians.target2.coords

#         for civ in game_state.civs_by_id.values():
#             civ.fill_out_available_buildings(game_state)

#         # add_intermediate_state()  # 2
#         if not game_state.no_db:
#             print("precommit")
#             sess.commit()

#         print("moving units 1")
#         units_copy = game_state.units[:]
#         random.shuffle(units_copy)
#         for unit in units_copy:
#             if not unit.dead:
#                 unit.move(sess, game_state)
#                 unit.attack(sess, game_state)

#         # add_intermediate_state()  # 3
#         if not game_state.no_db:
#             print("moving units 1: commit")
#             sess.commit()

#         # add_intermediate_state()  # 4
#         print("moving units 2")
#         random.shuffle(units_copy)
#         for unit in units_copy:
#             if not unit.dead:
#                 unit.move(sess, game_state, sensitive=True)
#                 unit.attack(sess, game_state)


#         # add_intermediate_state()  # 5
#         if not game_state.no_db:
#             print("moving units 2: commit")
#             sess.commit()

#         print("Merging units")
#         # New units could have appeared in game_state.units due to splits
#         # But that's ok, they've all acted by definition, so they don't need to be in this loop
#         random.shuffle(units_copy)
#         for unit in units_copy:
#             if not unit.has_moved and unit.attacks_used == 0 and unit.friendly_neighboring_unit_count(game_state) >= 4 and not unit.currently_sieging():
#                 unit.merge_into_neighboring_unit(sess, game_state)


#         # add_intermediate_state()  # 6
#         print("Acting cities & civs")
#         cities_copy = list(game_state.cities_by_id.values())
#         random.shuffle(cities_copy)

#         camps_copy = game_state.camps[:]
#         random.shuffle(camps_copy)
#         # add_intermediate_state()  # 7
#         for city in cities_copy:
#             city.roll_turn_pre_harvest(game_state)
#         add_intermediate_state()  # 8
#         for civ in game_state.civs_by_id.values():
#             civ.roll_turn_pre_harvest()
#         add_intermediate_state()  # 9
#         for city in cities_copy:
#             city.roll_turn_post_harvest(sess, game_state)

#         add_intermediate_state()  # 10
#         for camp in camps_copy:
#             camp.roll_turn(sess, game_state)

#         add_intermediate_state()  # 11
#         for civ in game_state.civs_by_id.values():
#             civ.roll_turn_post_harvest(sess, game_state)

#         add_intermediate_state()  # 12
#         print("Final refresh")
#         for unit in units_copy:
#             unit.turn_end(game_state)

#         for game_player in game_state.game_player_by_player_num.values():
#             game_player.decline_this_turn = False
#             game_player.failed_to_decline_this_turn = False

#         add_intermediate_state()  # 13
#         game_state.sync_advancement_level()

#         game_state.refresh_visibility_by_civ()
#         game_state.refresh_foundability_by_civ()

#         for civ in game_state.civs_by_id.values():
#             civ.fill_out_available_buildings(game_state)

#         add_intermediate_state()  # 14
#         print("Checking for game over")
#         print([game_player.score for game_player in game_state.game_player_by_player_num.values()], game_state.game_end_score())
#         for game_player in game_state.game_player_by_player_num.values():
#             if game_player.score >= game_state.game_end_score():
#                 game_state.game_over = True
#                 break

#         add_intermediate_state()  # 15
#         game_state.handle_decline_options()
#         for city in game_state.fresh_cities_for_decline.values():
#             city.roll_turn_post_harvest(sess, game_state, fake=True)
#         for city in game_state.cities_by_id.values():
#             city.already_harvested_this_turn = False

#         game_state.midturn_update()
        
#         game_state.civ_ids_with_game_player_at_turn_start = [civ.id for civ in game_state.civs_by_id.values() if civ.game_player is not None]

#         add_intermediate_state()  # 16
#         return intermediate_states
def ai_game(id, num_players):
    random.seed(id)
    game_id = id
    players = [GamePlayer(player_num=i, username=f"AI Player {i} in game {id}", is_bot=True, vitality_multiplier=1) for i in range(num_players)]
    game_state, _ = new_game_state(game_id, players)
    game_state.no_db = True
    states = []
    while not game_state.game_over and game_state.turn_num < 100:
        turn_states = []
        game_state.all_bot_moves()
        turn_states.append(copy.deepcopy(game_state.to_json()))  # 0
        game_state.midturn_update()
        turn_states.append(copy.deepcopy(game_state.to_json()))  # 1
        game_state.roll_turn(None)
        turn_states.append(copy.deepcopy(game_state.to_json()))  # 2
        game_state.midturn_update()
        turn_states.append(copy.deepcopy(game_state.to_json()))
        states.append(turn_states)

    return states

def compare_dicts(obj1, obj2, path=[]) -> list[str]:
    issues = []
    
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        for key in set(obj1.keys()) | set(obj2.keys()):
            if key not in obj1:
                issues.append(f"Key {'.'.join(path + [str(key)])} missing in first dict")
            elif key not in obj2:
                issues.append(f"Key {'.'.join(path + [str(key)])} missing in second dict")
            else:
                issues.extend(compare_dicts(obj1[key], obj2[key], path + [str(key)]))
    elif isinstance(obj1, list) and isinstance(obj2, list):
        if len(obj1) != len(obj2):
            issues.append(f"List length mismatch at {'.'.join(path)}: {len(obj1)} != {len(obj2)}")
        else:
            for i, (item1, item2) in enumerate(zip(obj1, obj2)):
                issues.extend(compare_dicts(item1, item2, path + [f"[{i}]"]))
    elif obj1 != obj2:
        issues.append(f"Mismatch at {'.'.join(path)}: {obj1} != {obj2}")
    
    return issues

def verify_equal(gameA, gameB):
    for state1, state2 in zip(gameA, gameB):
        issues = compare_dicts(state1, state2)
        if issues:
            print(f"========= MISMATCH TURN {state1[0]['turn_num']}/{len(gameA)} {state2[0]['turn_num']}/{len(gameB)} ==========")
            for issue in issues:
                print(issue)
            return False
    return True

def check_in_process(id):
    gameA = ai_game(id, 2)
    gameB = ai_game(id, 2)
    return verify_equal(gameA, gameB)

def store_n_games(n):
    for i in range(n):
        pickle.dump(ai_game(i, 2), open(f"scripts/output/game{i}.pkl", "wb"))

def check_n_games(n):
    for i in range(n):
        gameA = pickle.load(open(f"scripts/output/game{i}.pkl", "rb"))
        gameB = ai_game(i, 2)
        print(f"Checking game {i}")
        if not verify_equal(gameA, gameB):
            return False
    return True

# store_n_games(10)
check_n_games(10)
# check_in_process(0)