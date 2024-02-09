from typing import Any, Optional
from animation_frame import AnimationFrame
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from camp import Camp
from city import City
from civ import Civ
from civ_template import CivTemplate
from civ_templates_list import BARBARIAN_CIV, CIVS, ANCIENT_CIVS
from game_player import GamePlayer
from hex import Hex
from map import generate_decline_locations
from redis_utils import rget_json, rlock, rset_json, rdel
from settings import STARTING_CIV_VITALITY, GAME_END_SCORE, SURVIVAL_BONUS
from tech_template import TechTemplate
from tech_templates_list import TECHS
from unit import Unit
import random
from unit_templates_list import UNITS_BY_BUILDING_NAME, UNITS
from unit_template import UnitTemplate
from utils import swap_two_elements_of_list, generate_unique_id

from sqlalchemy import func

def get_all_units(hexes: dict[str, Hex]) -> list[Unit]:
    units = []
    for hex in hexes.values():
        units.extend(hex.units)
    return units


def get_all_cities(hexes: dict[str, Hex]) -> dict[str, City]:
    cities_by_id = {}
    for hex in hexes.values():
        if hex.city:
            cities_by_id[hex.city.id] = hex.city
    return cities_by_id


def get_all_camps(hexes: dict[str, Hex]) -> list[Camp]:
    camps = []
    for hex in hexes.values():
        if hex.camp:
            camps.append(hex.camp)
    return camps


def get_turn_ended_by_player_num(game_id: str) -> dict[int, bool]:
    return rget_json(f'turn_ended_by_player_num:{game_id}') or {}


def set_turn_ended_by_player_num(game_id: str, player_num, value: bool) -> None:
    turn_ended = get_turn_ended_by_player_num(game_id)
    turn_ended[player_num] = value
    rset_json(f'turn_ended_by_player_num:{game_id}', turn_ended)


class GameState:
    def __init__(self, game_id: str, hexes: dict[str, Hex]):
        self.hexes: dict[str, Hex] = hexes
        self.game_id = game_id
        self.units: list[Unit] = get_all_units(hexes)
        self.cities_by_id: dict[str, City] = get_all_cities(hexes)
        self.camps: list[Camp] = get_all_camps(hexes)
        self.barbarians: Civ = Civ(CivTemplate.from_json(BARBARIAN_CIV["Barbarians"]), None)  
        self.civs_by_id: dict[str, Civ] = {self.barbarians.id: self.barbarians}
        self.turn_num = 1
        self.game_player_by_player_num: dict[int, GamePlayer] = {}
        self.wonders_built_to_civ_id: dict[str, str] = {}
        self.national_wonders_built_by_civ_id: dict[str, list[str]] = {}
        self.special_mode_by_player_num: dict[int, Optional[str]] = {}
        self.advancement_level = 0
        self.game_over = False
        self.announcements = []
        self.turn_ended_by_player_num: dict[int, bool] = {}

    def turn_should_end(self, turn_ended_by_player_num: dict[int, bool]) -> bool:
        for player_num, game_player in self.game_player_by_player_num.items():
            if not game_player.is_bot and not turn_ended_by_player_num.get(player_num):
                return False
        return True

    def set_unit_and_city_hexes(self) -> None:
        for hex in self.hexes.values():
            for unit in hex.units:
                unit.hex = hex
            if hex.city:
                hex.city.hex = hex
            if hex.camp:
                hex.camp.hex = hex

    def pick_random_hex(self) -> Hex:
        return random.choice(list(self.hexes.values()))

    def process_decline_option(self, decline_option: tuple[str, str, str], game_player: GamePlayer, from_civ_perspectives: list[Civ]) -> tuple[GamePlayer, City]:
        coords, civ_name, city_id = decline_option
        hex = self.hexes[coords]
        if hex.city:
            old_civ = hex.city.civ

            if old_civ.game_player:
                old_civ.game_player.score += 5
                old_civ.game_player.score_from_revolting_cities += 5

                total_city_yields = sum([x for x in hex.city.get_projected_yields(self).values()]) / old_civ.vitality

                points_from_yields = int(total_city_yields / (10 * 1.03 ** (self.turn_num - 1)))

                old_civ.game_player.score += points_from_yields
                old_civ.game_player.score_from_revolting_cities += points_from_yields

        new_civ = Civ(CivTemplate.from_json(CIVS[civ_name]), game_player)
        new_civ.vitality = min(2.0 + self.turn_num * 0.1, 4.0)

        if new_civ.has_ability('ExtraCityPower'):
            new_civ.city_power += new_civ.numbers_of_ability('ExtraCityPower')[0]

        if hex.city is None:
            city = City(new_civ, id=city_id)
            city.hex = hex
            hex.city = city
            self.cities_by_id[city_id] = city
        else:
            hex.city.civ = new_civ
        game_player_to_return = game_player
        self.civs_by_id[new_civ.id] = new_civ
        from_civ_perspectives.append(new_civ)

        for neighbor_hex in [hex, *hex.get_neighbors(self.hexes)]:
            for unit in neighbor_hex.units:
                unit.civ = new_civ
            neighbor_hex.camp = None

        return game_player_to_return, hex.city


    # Returns (from_civ_perspectives, game state to pass to frontend, game state to store)
    def update_from_player_moves(self, player_num: int, moves: list[dict], speculative: bool = False) -> tuple[Optional[list[Civ]], dict, dict]:
        game_player_to_return: Optional[GamePlayer] = None
        from_civ_perspectives: Optional[list[Civ]] = None
        game_state_to_return_json: Optional[dict] = None
        game_state_to_store_json: Optional[dict] = None
        for move_index, move in enumerate(moves):
            if move['move_type'] == 'choose_starting_city':
                city_id = move['city_id']
                self.special_mode_by_player_num[player_num] = None

                for city in self.cities_by_id.values():
                    if (game_player := city.civ.game_player) and game_player.player_num == player_num:
                        if city.id == city_id:
                            game_player_to_return = game_player
                            game_player_to_return.civ_id = city.civ.id
                            self.game_player_by_player_num[player_num].civ_id = city.civ.id
                            city.civ.vitality = STARTING_CIV_VITALITY

                            city.capitalize()
                            city.adjust_projected_yields(self)
                            city.civ.adjust_projected_yields(self)

                        else:
                            if city.hex:
                                camp = Camp(self.barbarians)
                                camp.hex = city.hex
                                city.hex.camp = camp
                                self.camps.append(camp)

                                city.hex.city = None
                                city.hex = None
                                self.cities_by_id = {c_id: c for c_id, c in self.cities_by_id.items() if city.id != c.id}

                            del self.civs_by_id[city.civ.id]

                self.refresh_visibility_by_civ()

                for civ in self.civs_by_id.values():
                    civ.fill_out_available_buildings(self)                

            if move['move_type'] == 'choose_tech':
                tech_name = move['tech_name']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                tech = TechTemplate.from_json(TECHS[tech_name])
                civ.tech_queue.append(tech)
                game_player_to_return = game_player

            if move['move_type'] == 'choose_building':
                building_name = move['building_name']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]


                if building_name in UNITS_BY_BUILDING_NAME:
                    building = UnitTemplate.from_json(UNITS_BY_BUILDING_NAME[building_name])
                else:
                    building = BuildingTemplate.from_json(BUILDINGS[building_name])
                city.buildings_queue.append(building)
                game_player_to_return = game_player

                city.refresh_available_buildings()

            if move['move_type'] == 'cancel_building':
                building_name = move['building_name']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]

                for i, building in enumerate(city.buildings_queue):
                    if building.name == building_name or hasattr(building, 'building_name') and building.building_name == building_name:  # type: ignore
                        city.buildings_queue.pop(i)
                        break

                game_player_to_return = game_player

                city.refresh_available_buildings()

            if move['move_type'] == 'choose_unit':
                unit_name = move['unit_name']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]

                unit = UnitTemplate.from_json(UNITS[unit_name])
                city.units_queue.append(unit)
                game_player_to_return = game_player

            if move['move_type'] == 'cancel_unit':
                unit_index_in_queue = move['unit_index_in_queue']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]

                city.units_queue.pop(unit_index_in_queue)

                game_player_to_return = game_player

            if move['move_type'] == 'set_civ_primary_target':
                target_coords = move['target_coords']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.target1_coords = target_coords
                civ.target1 = self.hexes[target_coords]                
                game_player_to_return = game_player

            if move['move_type'] == 'set_civ_secondary_target':
                target_coords = move['target_coords']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.target2_coords = target_coords
                civ.target2 = self.hexes[target_coords]
                game_player_to_return = game_player

            if move['move_type'] == 'remove_civ_primary_target':
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.target1_coords = None
                civ.target1 = None
                game_player_to_return = game_player

            if move['move_type'] == 'remove_civ_secondary_target':
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.target2_coords = None
                civ.target2 = None
                game_player_to_return = game_player

            if move['move_type'] == 'choose_focus':
                game_player = self.game_player_by_player_num[player_num]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]
                city.focus = move['focus']
                game_player_to_return = game_player

                city.adjust_projected_yields(self)
                city.civ.adjust_projected_yields(self)

            if move['move_type'] == 'found_city':
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.city_power -= 100
                city_id = move['city_id']
                city = City(civ, id=city_id)
                city.hex = self.hexes[move['coords']]
                city.hex.city = city
                self.cities_by_id[city_id] = city

                if civ.has_ability('IncreaseYieldsForTerrainNextToSecondCity'):
                    if len([city for city in self.cities_by_id.values() if city.civ.id == civ.id]) == 2:
                        assert city.hex
                        numbers = civ.numbers_of_ability('IncreaseYieldsForTerrainNextToSecondCity')
                        for hex in [city.hex, city.hex.get_neighbors(self.hexes)]:
                            if hex.terrain == numbers[2]:
                                new_value = getattr(hex.yields, numbers[0]) + numbers[1]
                                setattr(hex.yields, numbers[0], new_value)

                if civ.has_ability('IncreaseYieldsForTerrain'):
                    assert city.hex
                    numbers = civ.numbers_of_ability('IncreaseYieldsForTerrain')
                    for hex in [city.hex, city.hex.get_neighbors(self.hexes)]:
                        if hex.terrain == numbers[2]:
                            new_value = getattr(hex.yields, numbers[0]) + numbers[1]
                            setattr(hex.yields, numbers[0], new_value)
            
                for wonder in self.wonders_built_to_civ_id:
                    if self.wonders_built_to_civ_id[wonder] == civ.id and (abilities := BUILDINGS[wonder]["abilities"]):
                        for ability in abilities:
                            if ability["name"] == "IncreasePopulationOfNewCities":
                                for _ in range(ability["numbers"][0]):
                                    city.grow_inner(self)

                self.refresh_foundability_by_civ()
                city.adjust_projected_yields(self)
                city.civ.adjust_projected_yields(self)                
                game_player_to_return = game_player

            if move['move_type'] == 'enter_decline':                
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                self.announcements.append(f'The civilization of {civ.moniker()} has entered decline!')                
                civ.game_player = None
                game_player.civ_id = None
                game_player_to_return = game_player
                self.special_mode_by_player_num[player_num] = 'choose_decline_option'
                game_state_to_store_json = self.to_json()

                if move_index == len(moves) - 1 and speculative:
                    from_civ_perspectives = []
                    for decline_option in self.game_player_by_player_num[player_num].decline_options:
                        self.process_decline_option(decline_option, game_player, from_civ_perspectives)
                        self.refresh_foundability_by_civ()
                        self.refresh_visibility_by_civ(short_sighted=True)
                        game_state_to_return_json = self.to_json(from_civ_perspectives=from_civ_perspectives)

                for other_civ in self.civs_by_id.values():
                    if other_civ.id != civ.id:
                        if other_civ.game_player:
                            other_civ.game_player.score += SURVIVAL_BONUS
                            other_civ.game_player.score_from_survival += SURVIVAL_BONUS

            if move['move_type'] == 'choose_decline_option':
                game_player = self.game_player_by_player_num[player_num]
                city_id = move['city_id']
                self.special_mode_by_player_num[player_num] = None
                game_player_to_return = game_player

                from_civ_perspectives = []
                city: Optional[City] = None
                for decline_option in self.game_player_by_player_num[player_num].decline_options:
                    if decline_option[2] == city_id:
                        game_player_to_return, city = self.process_decline_option(decline_option, game_player, from_civ_perspectives)

                assert len(from_civ_perspectives) == 1
                assert city is not None

                civ = from_civ_perspectives[0]

                civ.game_player = game_player
                game_player.civ_id = civ.id

                for tech in TECHS.values():
                    if tech['advancement_level'] <= self.advancement_level:
                        num_civs_with_tech = len([other_civ for other_civ in self.civs_by_id.values() if tech['name'] in other_civ.techs])

                        if num_civs_with_tech >= (len(self.civs_by_id) - 1) / 2:
                            civ.techs[tech['name']] = True

                self.refresh_foundability_by_civ()
                self.refresh_visibility_by_civ()                        

                for civ in self.civs_by_id.values():
                    civ.fill_out_available_buildings(self)

                self.announcements.append(f'The civilization of {civ.moniker()} has been founded in {city.name}!')


        if game_player_to_return is not None and (game_player_to_return.civ_id is not None or from_civ_perspectives is not None):
            if from_civ_perspectives is None and game_player_to_return.civ_id is not None:
                from_civ_perspectives = [self.civs_by_id[game_player_to_return.civ_id]]
            
            return (from_civ_perspectives, game_state_to_return_json or self.to_json(from_civ_perspectives=from_civ_perspectives), game_state_to_store_json or self.to_json())

        return (None, self.to_json(), self.to_json())

    def sync_advancement_level(self) -> None:
        tech_levels = [0]

        for civ in self.civs_by_id.values():
            for tech in civ.techs:
                if civ.techs[tech]:
                    tech_levels.append(TECHS[tech]['advancement_level'])
        
        max_advancement_level = 0

        for tech_level in range(max(tech_levels) + 1):
            if len([tech for tech in tech_levels if tech >= tech_level]) >= len(self.civs_by_id) / 2:
                max_advancement_level = tech_level

        self.advancement_level = max_advancement_level

    def refresh_visibility_by_civ(self, short_sighted: bool = False) -> None:
        for hex in self.hexes.values():
            hex.visibility_by_civ.clear()

        for unit in self.units:
            unit.update_nearby_hexes_visibility(self, short_sighted=short_sighted)

        for city in self.cities_by_id.values():
            city.update_nearby_hexes_visibility(self, short_sighted=short_sighted)

    def refresh_foundability_by_civ(self) -> None:
        for hex in self.hexes.values():
            hex.is_foundable_by_civ.clear()

        for unit in self.units:
            unit.update_nearby_hexes_friendly_foundability()

        for unit in self.units:
            unit.update_nearby_hexes_hostile_foundability(self.hexes)

        for city in self.cities_by_id.values():
            city.update_nearby_hexes_hostile_foundability(self.hexes)

        for camp in self.camps:
            camp.update_nearby_hexes_hostile_foundability(self.hexes)

    def end_turn(self, sess) -> None:
        for player_num in self.game_player_by_player_num.keys():
            staged_moves = rget_json(f'staged_moves:{self.game_id}:{player_num}') or []
            self.update_from_player_moves(player_num, staged_moves)

        for civ in self.civs_by_id.values():
            if (not civ.game_player or civ.game_player.is_bot) and not civ.template.name == 'Barbarians':
                civ.bot_move(self)

        print('ending turn')

        self.roll_turn(sess)

        for player_num in self.game_player_by_player_num.keys():
            rdel(f'staged_moves:{self.game_id}:{player_num}')
            rdel(f'staged_game_state:{self.game_id}:{player_num}')

        rdel(f'turn_ended_by_player_num:{self.game_id}')

    def roll_turn(self, sess) -> None:
        self.turn_num += 1

        self.barbarians.target1 = self.pick_random_hex()
        self.barbarians.target2 = self.pick_random_hex()
        self.barbarians.target1_coords = self.barbarians.target1.coords
        self.barbarians.target2_coords = self.barbarians.target2.coords

        for civ in self.civs_by_id.values():
            civ.fill_out_available_buildings(self)

        units_copy = self.units[:]
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.move(sess, self)
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.move(sess, self, sensitive=True)
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.attack(sess, self)

        cities_copy = list(self.cities_by_id.values())
        random.shuffle(cities_copy)

        camps_copy = self.camps[:]
        random.shuffle(camps_copy)

        for city in cities_copy:
            city.roll_turn(sess, self)

        for camp in camps_copy:
            camp.roll_turn(sess, self)

        for civ in self.civs_by_id.values():
            civ.roll_turn(sess, self)

        for unit in units_copy:
            unit.has_moved = False

        for city in self.cities_by_id.values():
            city.adjust_projected_yields(self)

        for civ in self.civs_by_id.values():
            civ.adjust_projected_yields(self)

        self.sync_advancement_level()

        self.prepare_decline_choices()

        # print([game_player.to_json() for key, game_player in self.game_player_by_player_num.items()])

        self.refresh_visibility_by_civ()
        self.refresh_foundability_by_civ()

        for game_player in self.game_player_by_player_num.values():
            if game_player.score >= GAME_END_SCORE:
                self.game_over = True
                break

        self.add_animation_frame(sess, {
            "type": "StartOfNewTurn",
        })


    def prepare_decline_choices(self) -> None:
        advancement_level_to_use = max(self.advancement_level, 1)

        num_players = len(self.game_player_by_player_num)

        num_civs_to_sample = 3 * num_players

        decline_choice_big_civ_pool = []

        for min_advancement_level in range(advancement_level_to_use, 0, -1):
            decline_choice_big_civ_pool = [civ['name'] for civ in ANCIENT_CIVS.values() 
                                           if civ['advancement_level'] <= advancement_level_to_use and civ['advancement_level'] >= min_advancement_level]

            if len(decline_choice_big_civ_pool) >= num_civs_to_sample:
                break

        decline_choice_civ_pool = random.sample(decline_choice_big_civ_pool, num_civs_to_sample)

        cities_by_civ = {civ.id: [city for city in self.cities_by_id.values() if city.civ.id == civ.id] for civ in self.civs_by_id.values()}

        eligible_cities_for_declining = [city for city in self.cities_by_id.values() if len(cities_by_civ[city.civ.id]) > 1]

        eligible_locations_for_declining = generate_decline_locations(self.hexes, max(num_civs_to_sample - len(eligible_cities_for_declining) + num_players, 0))

        all_location_options: list[str] = [*[city.hex.coords for city in eligible_cities_for_declining if city.hex is not None], 
                                  *[hex.coords for hex in eligible_locations_for_declining]]

        min_options_per_player = min(len(all_location_options) // num_players, 3)

        num_options_by_player = [min_options_per_player] * num_players

        for i in range(len(all_location_options) % num_players):
            if num_options_by_player[i] < 3:
                num_options_by_player[i] += 1

        random.shuffle(all_location_options)

        counter = 0

        for i, player_num in enumerate(self.game_player_by_player_num.keys()):
            game_player = self.game_player_by_player_num[player_num]
            decline_options: list[tuple[str, str, str]] = []
            for _ in range(num_options_by_player[i]):
                location = ''
                index_to_swap_with = counter + 1
                is_good_location = False
                while True:
                    location = all_location_options[counter]
                    hex_at_location = self.hexes[location]
                    city_at_location = hex_at_location.city
                    if city_at_location is None or city_at_location.civ.id != game_player.civ_id:
                        is_good_location = True
                        break
                    swap_two_elements_of_list(all_location_options, counter, index_to_swap_with)
                    index_to_swap_with += 1
                    if index_to_swap_with >= len(all_location_options):
                        break
                if is_good_location:
                    city_id = city_at_location.id if city_at_location else generate_unique_id()
                    decline_options.append((all_location_options[counter], decline_choice_civ_pool[counter], city_id))
                counter += 1
            game_player.decline_options = decline_options
    

    def handle_wonder_built(self, sess, civ: Civ, building_template: BuildingTemplate, national: bool = False) -> None:
        if national:
            if civ.id not in self.national_wonders_built_by_civ_id:
                self.national_wonders_built_by_civ_id[civ.id] = [building_template.name]
            else:
                self.national_wonders_built_by_civ_id[civ.id].append(building_template.name)
        else:
            self.wonders_built_to_civ_id[building_template.name] = civ.id

        
        if (game_player := civ.game_player) is not None:
            if civ.has_ability('ExtraVpsPerWonder'):
                game_player.score += civ.numbers_of_ability('ExtraVpsPerWonder')[0]
                game_player.score_from_abilities += civ.numbers_of_ability('ExtraVpsPerWonder')[0]

        for city in self.cities_by_id.values():
            for i, building in enumerate(city.buildings_queue):
                if building.name == building_template.name:
                    if city.civ.id == civ.id or not national:
                        city.buildings_queue = [building for building in city.buildings_queue if building.name != building_template.name]
                        break

        if not national:
            for civ_to_announce in self.civs_by_id.values():
                self.add_animation_frame_for_civ(sess, {
                    'type': 'WonderBuilt',
                    'civ': civ.template.name,
                    'wonder': building_template.name,
                }, civ_to_announce)
            
            self.announcements.append(f'{civ.moniker()} has built the {building_template.name}!')

    def add_animation_frame_for_civ(self, sess, data: dict[str, Any], civ: Optional[Civ]) -> None:
        if civ is not None and (game_player := civ.game_player) is not None:
            highest_existing_frame_num = (
                sess.query(func.max(AnimationFrame.frame_num))
                .filter(AnimationFrame.game_id == self.game_id)
                .filter(AnimationFrame.turn_num == self.turn_num)
                .filter(AnimationFrame.player_num == game_player.player_num)
                .scalar()
            ) or 0

            frame = AnimationFrame(
                game_id=self.game_id,
                turn_num=self.turn_num,
                frame_num=highest_existing_frame_num + 1,
                player_num=game_player.player_num,
                data=data,
                game_state=self.to_json(from_civ_perspectives=[civ]),
            )

            sess.add(frame)
            sess.commit()

        elif civ is None:
            highest_existing_frame_num = (
                sess.query(func.max(AnimationFrame.frame_num))
                .filter(AnimationFrame.game_id == self.game_id)
                .filter(AnimationFrame.turn_num == self.turn_num)
                .filter(AnimationFrame.player_num == None)
                .scalar()
            ) or 0

            frame = AnimationFrame(
                game_id=self.game_id,
                turn_num=self.turn_num,
                frame_num=highest_existing_frame_num + 1,
                player_num=None,
                data=data,
                game_state=self.to_json(),
            )

            sess.add(frame)
            sess.commit()

    def add_animation_frame(self, sess, data: dict[str, Any], hexes_must_be_visible: Optional[list[Hex]] = None) -> None:
        self.add_animation_frame_for_civ(sess, data, None)

        for civ in self.civs_by_id.values():
            if hexes_must_be_visible is None or any(hex.visibility_by_civ.get(civ.id) for hex in hexes_must_be_visible):
                self.add_animation_frame_for_civ(sess, data, civ)


    def get_civ_by_name(self, civ_name: str) -> Civ:
        for civ in self.civs_by_id.values():
            if civ.template.name == civ_name:
                return civ
        raise Exception(f"Civ not found: {civ_name}, {self.civs_by_id}")
    
    def to_json(self, from_civ_perspectives: Optional[list[Civ]] = None) -> dict:
        return {
            "game_id": self.game_id,
            "hexes": {key: hex.to_json(from_civ_perspectives=from_civ_perspectives) for key, hex in self.hexes.items()},
            "civs_by_id": {civ_id: civ.to_json() for civ_id, civ in self.civs_by_id.items()},
            "game_player_by_player_num": {player_num: game_player.to_json() for player_num, game_player in self.game_player_by_player_num.items()},
            "turn_num": self.turn_num,
            "wonders_built_to_civ_id": self.wonders_built_to_civ_id.copy(),
            "national_wonders_built_by_civ_id": {k: v[:] for k, v in self.national_wonders_built_by_civ_id.items()},
            "special_mode_by_player_num": self.special_mode_by_player_num.copy(),
            "barbarians": self.barbarians.to_json(),
            "advancement_level": self.advancement_level,
            "game_over": self.game_over,
            "announcements": self.announcements[:],
            "turn_ended_by_player_num": rget_json('turn_ended_by_player_num') or {},
        }
    
    def set_civ_targets(self, hexes: dict[str, Hex]) -> None:
        for civ in self.civs_by_id.values():
            if civ.target1_coords:
                civ.target1 = hexes[civ.target1_coords]
            if civ.target2_coords:
                civ.target2 = hexes[civ.target2_coords]

    @staticmethod
    def from_json(json: dict) -> "GameState":
        hexes = {key: Hex.from_json(hex_json) for key, hex_json in json["hexes"].items()}
        game_state = GameState(game_id=json["game_id"], hexes=hexes)
        game_state.game_player_by_player_num = {int(player_num): GamePlayer.from_json(game_player_json) for player_num, game_player_json in json["game_player_by_player_num"].items()}        
        game_state.civs_by_id = {civ_id: Civ.from_json(civ_json) for civ_id, civ_json in json["civs_by_id"].items()}
        game_state.barbarians = [civ for civ in game_state.civs_by_id.values() if civ.template.name == 'Barbarians'][0]
        game_state.advancement_level = json["advancement_level"]
        for civ in game_state.civs_by_id.values():
            civ.update_game_player(game_state.game_player_by_player_num)
        for hex in game_state.hexes.values():
            hex.update_civ_by_id(game_state.civs_by_id)
        game_state.turn_num = json["turn_num"]
        game_state.wonders_built_to_civ_id = json["wonders_built_to_civ_id"].copy()
        game_state.national_wonders_built_by_civ_id = {k: v[:] for k, v in json["national_wonders_built_by_civ_id"].items()}
        game_state.special_mode_by_player_num = {int(k): v for k, v in json["special_mode_by_player_num"].items()}
        game_state.set_unit_and_city_hexes()
        game_state.set_civ_targets(hexes)
        game_state.game_over = json["game_over"]
        game_state.announcements = json["announcements"][:]
        return game_state


def get_most_recent_game_state_json(sess, game_id: str) -> dict:
    most_recent_game_state_animation_frame = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.player_num == None)
        .order_by(AnimationFrame.turn_num.desc())
        .order_by(AnimationFrame.frame_num.desc())
        .first()
    )

    assert most_recent_game_state_animation_frame is not None

    most_recent_game_state = most_recent_game_state_animation_frame.game_state

    return most_recent_game_state


def get_most_recent_game_state(sess, game_id: str) -> GameState:
    return GameState.from_json(get_most_recent_game_state_json(sess, game_id))


def update_staged_moves(sess, game_id: str, player_num: int, moves: list[dict]) -> tuple[GameState, Optional[list[Civ]], dict]:
    with rlock(f'staged_moves_lock:{game_id}:{player_num}'):
        staged_moves = rget_json(f'staged_moves:{game_id}:{player_num}') or []
        game_state_json = rget_json(f'staged_game_state:{game_id}:{player_num}') or get_most_recent_game_state_json(sess, game_id)
        game_state = GameState.from_json(game_state_json)
        from_civ_perspectives, game_state_to_return_json, game_state_to_store_json = game_state.update_from_player_moves(player_num, moves, speculative=True)

        staged_moves.extend(moves)

        rset_json(f'staged_moves:{game_id}:{player_num}', staged_moves, ex=7 * 24 * 60 * 60)
        rset_json(f'staged_game_state:{game_id}:{player_num}', game_state_to_store_json, ex=7 * 24 * 60 * 60)

        return game_state, from_civ_perspectives, game_state_to_return_json
