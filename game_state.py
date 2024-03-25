import math
from datetime import datetime, timedelta
from typing import Any, Optional
from animation_frame import AnimationFrame
from building import Building
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from camp import Camp
from collections import defaultdict
from city import City, generate_random_city_name
from civ import Civ
from civ_template import CivTemplate
from civ_templates_list import BARBARIAN_CIV, CIVS, ANCIENT_CIVS
from game_player import GamePlayer
from hex import Hex
from map import generate_decline_locations, is_valid_decline_location
from redis_utils import rget_json, rlock, rset_json, rdel, rset, rget
from settings import STARTING_CIV_VITALITY, GAME_END_SCORE, SURVIVAL_BONUS, EXTRA_GAME_END_SCORE_PER_PLAYER, MULLIGAN_PENALTY
from tech_template import TechTemplate
from tech_templates_list import TECHS
from unit import Unit
import random
from unit_templates_list import UNITS_BY_BUILDING_NAME, UNITS
from unit_template import UnitTemplate
from utils import dream_key, staged_moves_key

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
        self.game_over = False  # TODO delete
        self.announcements = []
        self.fresh_cities_for_decline: dict[str, City] = {}
        self.unhappiness_threshold: float = 0.0

        self.highest_existing_frame_num_by_civ_id: defaultdict[str, int] = defaultdict(int)

    def midturn_update(self):
        print("midturn update triggered")
        for city in self.cities_by_id.values():
            city.midturn_update(self)
        for unit in self.units:
            unit.midturn_update(self)
        for civ in self.civs_by_id.values():
            civ.midturn_update(self)

    def add_announcement(self, content):
        self.announcements.append(f'[T {self.turn_num}] {content}')

    def set_unit_and_city_hexes(self) -> None:
        for hex in self.hexes.values():
            for unit in hex.units:
                unit.hex = hex
            if hex.city:
                hex.city.hex = hex
            if hex.camp:
                hex.camp.hex = hex
        for coords, city in self.fresh_cities_for_decline.items():
            city.hex = self.hexes[coords]

    def pick_random_hex(self) -> Hex:
        return random.choice(list(self.hexes.values()))

    def register_city(self, city):
        city.hex.city = city
        self.cities_by_id[city.id] = city

    def new_city(self, civ: Civ, hex: Hex, city_id: Optional[str] = None) -> City:
        city_name = generate_random_city_name(game_state=self)
        city = City(civ, name=city_name, id=city_id)
        city.hex = hex
        city.populate_terrains_dict(self)
        return city

    def found_city_for_civ(self, civ: Civ, hex: Hex, city_id: str) -> None:
        civ.city_power -= 100
        city = self.new_city(civ, hex, city_id)
        self.register_city(city)

        if civ.has_ability('IncreaseYieldsForTerrainNextToSecondCity'):
            if len([city for city in self.cities_by_id.values() if city.civ.id == civ.id]) == 2:
                assert city.hex
                numbers = civ.numbers_of_ability('IncreaseYieldsForTerrainNextToSecondCity')
                for hex in [city.hex, *city.hex.get_neighbors(self.hexes)]:
                    if hex.terrain == numbers[1]:
                        new_value = getattr(hex.yields, numbers[0]) + numbers[2]
                        setattr(hex.yields, numbers[0], new_value)

        if civ.has_ability('IncreaseYieldsForTerrain'):
            assert city.hex
            numbers = civ.numbers_of_ability('IncreaseYieldsForTerrain')
            for hex in [city.hex, *city.hex.get_neighbors(self.hexes)]:
                if hex.terrain == numbers[1]:
                    new_value = getattr(hex.yields, numbers[0]) + numbers[2]
                    setattr(hex.yields, numbers[0], new_value)
    
        for wonder in self.wonders_built_to_civ_id:
            if self.wonders_built_to_civ_id[wonder] == civ.id and (abilities := BUILDINGS[wonder]["abilities"]):
                for ability in abilities:
                    if ability["name"] == "IncreasePopulationOfNewCities":
                        for _ in range(ability["numbers"][0]):
                            city.grow_inner(self)

        self.refresh_foundability_by_civ()
        self.midturn_update()     

    def enter_decline_for_civ(self, civ: Civ, game_player: GamePlayer) -> None:
        self.add_announcement(f'The {civ.moniker()} have entered decline!')                
        civ.game_player = None
        civ.in_decline = True
        game_player.civ_id = None

        for other_civ in self.civs_by_id.values():
            if other_civ.id != civ.id:
                if other_civ.game_player:
                    other_civ.game_player.score += SURVIVAL_BONUS
                    other_civ.game_player.score_from_survival += SURVIVAL_BONUS

    def choose_techs_for_new_civ(self, city: City):
        print("Calculating starting techs!")
        assert city.hex is not None
        # Make this function deterministic across staging and rolling
        random.seed(hash(f"{self.game_id} {self.turn_num} {city.name} {city.hex.coords}"))
        chosen_techs_names = set()
        chosen_techs_by_advancement = defaultdict(int)

        # Start with prereqs for the buildings we have
        for building in city.buildings:
            prereq = building.template.prereq
            if prereq is not None:
                chosen_techs_names.add(prereq)
                chosen_techs_by_advancement[TECHS[prereq]['advancement_level']] += 1

        print(f"Starting with prereqs for buildings: {chosen_techs_names}")

        # Calculate mean tech amount at each level
        civs_to_compare_to: list[Civ] = [civ for civ in self.civs_by_id.values() if civ.game_player and civ != city.civ]
        if len(civs_to_compare_to) == 0:
            civs_to_compare_to = [civ for civ in self.civs_by_id.values()]

        print(f"  Comparing to civs: {civs_to_compare_to}")
        # Make a dict of {tech: num civs that know it} for each level
        tech_counts_by_adv_level = defaultdict(dict)
        for tech_name, tech in TECHS.items():
            num = len([civ for civ in civs_to_compare_to if civ.has_tech(tech_name)])
            lvl = tech['advancement_level']
            tech_counts_by_adv_level[lvl][tech_name] = num

        excess_techs = 0
        for level in sorted(list(tech_counts_by_adv_level.keys()), reverse=True):
            tech_counts = tech_counts_by_adv_level[level]
            total = sum(tech_counts.values())
            target_num = total / len(civs_to_compare_to) - excess_techs
            print(f"Level {level}; excess {excess_techs}; target: {target_num}")
            if chosen_techs_by_advancement[level] > target_num:
                excess_techs = chosen_techs_by_advancement[level] - target_num
                continue
            else:
                num_needed = target_num - chosen_techs_by_advancement[level]
                available = [tech for tech in tech_counts_by_adv_level[level] if tech not in chosen_techs_names]
                available.sort(key=lambda tech: (tech_counts_by_adv_level[level][tech], random.random()), reverse=True)
                choose = available[:math.ceil(num_needed)]
                print(f"  chose: {choose}")
                for tech in choose:
                    chosen_techs_names.add(tech)
                excess_techs = len(choose) - num_needed

        return chosen_techs_names
        

    def make_new_civ_from_the_ashes(self, city: City) -> None:
        chosen_techs = self.choose_techs_for_new_civ(city)
        civ = city.civ
        civ.initialize_techs(chosen_techs)

        self.refresh_foundability_by_civ()
        self.refresh_visibility_by_civ()

        for civ in self.civs_by_id.values():
            civ.fill_out_available_buildings(self)

        if civ.has_ability('ExtraCityPower'):
            civ.city_power += civ.numbers_of_ability('ExtraCityPower')[0]


        city.refresh_available_buildings()
        city.refresh_available_units()
        self.midturn_update()

        self.add_announcement(f'The {civ.moniker()} have been founded in {city.name}!')        

    def decline_priority(self, first_player_num: int, new_player_num: int) -> bool:
        """
        Returns true if we should continue with the decline.
        """
        # During the turn, this is executed from the staged game_state of the new_player.
        # Therefore, no one's scores have changed since the start of the turn and we can just compare them raw.
        # During turn end, this should never be called.
        def priority(player_num):
            # Priority is first by score, then by civ_id as a determinstic-but-random tiebreak.
            game_player: GamePlayer = self.game_player_by_player_num[player_num]
            return (-game_player.score, game_player.civ_id)
        return priority(first_player_num) < priority(new_player_num)

    def execute_decline(self, coords: str, game_player: GamePlayer) -> list[Civ]:
        """
        Actually enter decline for real (not just for the imaginary decline options view GameState)
        """
        assert game_player.civ_id
        civ: Civ = self.civs_by_id[game_player.civ_id]
        self.enter_decline_for_civ(civ, game_player)

        from_civ_perspectives = []
        city: City = self.process_decline_option(coords, from_civ_perspectives)
        
        # Remove it from the set of choices
        if coords in self.fresh_cities_for_decline:
            self.fresh_cities_for_decline.pop(coords)

        if len(from_civ_perspectives) > 1:
            from_civ_perspectives = from_civ_perspectives[:1]
        assert city is not None

        civ = from_civ_perspectives[0]

        civ.game_player = game_player
        game_player.civ_id = civ.id
        game_player.decline_this_turn = True
        self.make_new_civ_from_the_ashes(city)
        return from_civ_perspectives


    def process_decline_option(self, coords: str, from_civ_perspectives: list[Civ]) -> City:
        """
        The parts of entering decline that happen both when you do it for real,
        and when the special decline options view GameState is produced.
        """
        hex = self.hexes[coords]
        if hex.city:
            # This is not a fresh city , it's a pre-existing one.
            print(f"Declining to existing city at {coords}")
            assert hex.city.civ_to_revolt_into is not None, f"Trying to revolt into a city {hex.city.name} with no city.civ_to_revolt_into"
            hex.city.civ = Civ(hex.city.civ_to_revolt_into, game_player=None)
        else:
            # This is a fake city, now it is becoming a real city.
            print(f"Declining to fresh city at {coords}")
            self.register_city(self.fresh_cities_for_decline[coords])
        assert hex.city is not None, "Failed to register city!"
        hex.city.capitalize(self)
        hex.city.population = max(hex.city.population, self.turn_num // 7)
        hex.city.wood = hex.city.metal = hex.city.unhappiness = 0
        hex.city.civ_to_revolt_into = None
        hex.city.buildings = [b for b in hex.city.buildings if not b.is_national_wonder]

        new_civ: Civ = hex.city.civ
        new_civ.vitality = hex.city.revolting_starting_vitality
        self.civs_by_id[new_civ.id] = new_civ
        from_civ_perspectives.append(new_civ)

        unit_count = 0
        for neighbor_hex in [hex, *hex.get_neighbors(self.hexes)]:
            for unit in neighbor_hex.units:
                old_unit_civ: Civ = unit.civ
                unit.civ = new_civ
                stack_size: int = unit.get_stack_size()
                unit_count += stack_size
                
                if old_unit_civ.game_player:
                    old_unit_civ.game_player.score += stack_size
                    old_unit_civ.game_player.score_from_revolting_cities += stack_size

            neighbor_hex.camp = None
        hex.city.revolt_unit_count = unit_count

        hex.city.midturn_update(self)

        return hex.city


    def update_from_player_moves(self, player_num: int, moves: list[dict], speculative: bool = False, 
                                 city_owner_by_city_id: Optional[dict] = None) -> tuple[Optional[list[Civ]], dict, dict, bool, Optional[int]]:
        """
        Returns:
          - from_civ_perspectives: the set of players from whose perspectives the game state should be seen
          - game_state_to_return: game_state to send to the client
          - game_state_to_store: game_state to put in redis
          - should_stage_moves: should we add these moves to the player's staged moves?
          - decline_eviction_player: if not None, we need to evict this player number from the decline choice they've already taken.
        """
        game_player_to_return: Optional[GamePlayer] = None
        from_civ_perspectives: Optional[list[Civ]] = None
        game_state_to_return_json: Optional[dict] = None
        game_state_to_store_json: Optional[dict] = None
        should_stage_moves = True
        decline_eviction_player: Optional[int] = None
        
        # This has to be deterministic to allow speculative and non-speculative calls to agree
        seed_value = hash(f"{self.game_id} {player_num} {self.turn_num}")
        random.seed(seed_value)

        for move_index, move in enumerate(moves):
            if ((city_id := move.get('city_id')) is not None 
                    and (city_owner := (city_owner_by_city_id or {}).get(city_id)) is not None 
                    and city_owner != player_num):
                continue
            if move['move_type'] == 'choose_starting_city':
                city_id = move['city_id']
                self.special_mode_by_player_num[player_num] = None

                for city in self.cities_by_id.values():
                    if (game_player := city.civ.game_player) and game_player.player_num == player_num:
                        if city.id == city_id:
                            game_player.decline_this_turn = True
                            game_player_to_return = game_player
                            game_player_to_return.civ_id = city.civ.id
                            self.game_player_by_player_num[player_num].civ_id = city.civ.id
                            city.civ.vitality = STARTING_CIV_VITALITY

                            city.capitalize(self)
                            self.midturn_update()

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

                rdel(dream_key(self.game_id, player_num, self.turn_num))

            if move['move_type'] == 'choose_tech':
                tech_name = move['tech_name']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.select_tech(tech_name)
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

            if move['move_type'] == 'select_infinite_queue':
                unit_name = move['unit_name']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]

                if unit_name == "":
                    unit = None
                else:
                    unit = UnitTemplate.from_json(UNITS[unit_name])

                city.infinite_queue_unit = unit
                self.midturn_update()
                game_player_to_return = game_player


            if move['move_type'] == 'set_civ_primary_target':
                target_coords = move['target_coords']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.target1_coords = target_coords
                civ.target1 = self.hexes[target_coords]                
                game_player_to_return = game_player
                self.midturn_update()

            if move['move_type'] == 'set_civ_secondary_target':
                target_coords = move['target_coords']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.target2_coords = target_coords
                civ.target2 = self.hexes[target_coords]
                game_player_to_return = game_player
                self.midturn_update()

            if move['move_type'] == 'remove_civ_primary_target':
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.target1_coords = None
                civ.target1 = None
                game_player_to_return = game_player
                self.midturn_update()

            if move['move_type'] == 'remove_civ_secondary_target':
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.target2_coords = None
                civ.target2 = None
                game_player_to_return = game_player
                self.midturn_update()

            if move['move_type'] == 'choose_focus':
                game_player = self.game_player_by_player_num[player_num]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]
                city.focus = move['focus']
                game_player_to_return = game_player
                self.midturn_update()

            if move['move_type'] == 'trade_hub':
                game_player = self.game_player_by_player_num[player_num]
                city_id = move['city_id']
                assert game_player.civ_id is not None
                civ: Civ = self.civs_by_id[game_player.civ_id]
                if civ.trade_hub_id == city_id:
                    civ.trade_hub_id = None
                else:
                    civ.trade_hub_id = city_id
                game_player_to_return = game_player
                self.midturn_update()

            if move['move_type'] == 'found_city':
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                self.found_city_for_civ(self.civs_by_id[game_player.civ_id], self.hexes[move['coords']], move['city_id'])
                game_player_to_return = game_player
                self.midturn_update()

            if move['move_type'] == 'choose_decline_option':
                print(f'player {player_num} is choosing a decline option')

                game_player = self.game_player_by_player_num[player_num]
                game_player_to_return = game_player

                if 'preempted' in move:
                    game_player.failed_to_decline_this_turn = True
                    continue

                coords = move['coords']

                assert not game_player.decline_this_turn, f"Player {player_num} is trying to decline twice in one turn."

                # If speculative is False, then there should be no collisions
                # We could be less strict here and not even check, but that seems dangerous
                with rlock(f'decline-claimed-{self.game_id}-{self.turn_num}-lock'):
                    redis_key = f"decline-claimed-{self.game_id}-{self.turn_num}-{coords}"
                    already_claimed_by = rget(redis_key)
                    print(f"{already_claimed_by=}")
                    proceed = False
                    if not speculative:
                        # End turn roll; there should be no collisions here.
                        assert already_claimed_by is not None and int(already_claimed_by) == game_player.player_num, f"During end turn roll, trying to execute a decline that wasn't claimed during the turn. {self.game_id} {self.turn_num} {coords} {already_claimed_by} {game_player.player_num}"
                        proceed = True
                    elif speculative and already_claimed_by is None:
                        # Non collision
                        proceed = True
                    elif speculative and already_claimed_by is not None:
                        # Collision
                        proceed: bool = self.decline_priority(first_player_num=int(already_claimed_by), new_player_num=game_player.player_num)
                        if proceed:
                            decline_eviction_player = int(already_claimed_by)
                        else:
                            # The client figures out the action failed based on the fact that I'm still the same civ.
                            # That isn't super robust.
                            move['preempted'] = True
                            game_player.failed_to_decline_this_turn = True

                    else:
                        raise ValueError("There are no other logical possibilities.")
                    print(f"{proceed=}")
                    if proceed:
                        rset(redis_key, game_player.player_num)
                        from_civ_perspectives = self.execute_decline(coords, game_player)


        if game_player_to_return is not None and (game_player_to_return.civ_id is not None or from_civ_perspectives is not None):
            if from_civ_perspectives is None and game_player_to_return.civ_id is not None:
                from_civ_perspectives = [self.civs_by_id[game_player_to_return.civ_id]]
            return (from_civ_perspectives, game_state_to_return_json or self.to_json(from_civ_perspectives=from_civ_perspectives), game_state_to_store_json or self.to_json(), should_stage_moves, decline_eviction_player)

        return (None, self.to_json(), self.to_json(), should_stage_moves, decline_eviction_player)

    def sync_advancement_level(self) -> None:
        tech_levels = [0]

        for civ in self.civs_by_id.values():
            for tech in civ.researched_techs:
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
        if self.game_over:
            return

        # Defaults to being permissive; city_ids that exist will cause it to be the case that
        # only commands from that player's player num get respected
        city_owner_by_city_id: dict[str, int] = {}

        for player_num in self.game_player_by_player_num.keys():
            staged_moves = rget_json(staged_moves_key(self.game_id, player_num, self.turn_num)) or []

            for move in staged_moves:
                if move['move_type'] == 'choose_decline_option' and 'preempted' not in move:
                    if (city := self.hexes[move['coords']].city):
                        city_owner_by_city_id[city.id] = player_num

        for player_num in self.game_player_by_player_num.keys():
            staged_moves = rget_json(staged_moves_key(self.game_id, player_num, self.turn_num)) or []
            self.update_from_player_moves(player_num, staged_moves, city_owner_by_city_id=city_owner_by_city_id)

        civs = list(self.civs_by_id.values())[:]

        for civ in civs:
            if (not civ.game_player or civ.game_player.is_bot) and not civ.template.name == 'Barbarians':
                civ.bot_move(self)

        for player_num, game_player in self.game_player_by_player_num.items():
            if game_player.civ_id is None:
                game_player.score -= MULLIGAN_PENALTY
                game_player.score_from_survival -= MULLIGAN_PENALTY

        print('ending turn')

        self.roll_turn(sess)

        print("committing changes")
        sess.commit()

        self.add_animation_frame(sess, {
            "type": "StartOfNewTurn",
        })
        sess.commit()

        print("Creating decline view")
        self.create_decline_view(sess)   

        print("roll complete")

    def game_end_score(self):
        return GAME_END_SCORE + EXTRA_GAME_END_SCORE_PER_PLAYER * len(self.game_player_by_player_num)

    def roll_turn(self, sess) -> None:
        self.turn_num += 1

        self.barbarians.target1 = self.pick_random_hex()
        self.barbarians.target2 = self.pick_random_hex()
        self.barbarians.target1_coords = self.barbarians.target1.coords
        self.barbarians.target2_coords = self.barbarians.target2.coords

        for civ in self.civs_by_id.values():
            civ.fill_out_available_buildings(self)

        print("precommit")
        sess.commit()

        print("moving units 1")
        units_copy = self.units[:]
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.move(sess, self)
            unit.attack(sess, self)

        print("moving units 1: commit")
        sess.commit()

        print("moving units 2")
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.move(sess, self, sensitive=True)
            unit.attack(sess, self)

        print("moving units 2: commit")
        sess.commit()

        print("Merging units")
        # New units could have appeared in self.units due to splits
        # But that's ok, they've all acted by definition, so they don't need to be in this loop
        random.shuffle(units_copy)
        for unit in units_copy:
            if not unit.has_moved and unit.attacks_used == 0 and unit.friendly_neighboring_unit_count(self) >= 4 and not unit.currently_sieging():
                unit.merge_into_neighboring_unit(sess, self)

        print("Acting cities & civs")
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

        print("Final refresh")
        for unit in units_copy:
            unit.has_moved = False
            unit.attacks_used = 0

        for game_player in self.game_player_by_player_num.values():
            game_player.decline_this_turn = False
            game_player.failed_to_decline_this_turn = False

        self.midturn_update()      

        self.sync_advancement_level()

        self.refresh_visibility_by_civ()
        self.refresh_foundability_by_civ()

        for civ in self.civs_by_id.values():
            civ.fill_out_available_buildings(self)

        for city in self.cities_by_id.values():
            city.refresh_available_buildings()       

        for game_player in self.game_player_by_player_num.values():
            if game_player.score >= self.game_end_score():
                self.game_over = True
                break

        self.handle_decline_options()
        for city in self.fresh_cities_for_decline.values():
            city.roll_turn(sess, self, fake=True)

    def handle_decline_options(self):
        self.populate_fresh_cities_for_decline()
        cities_to_revolt = sorted([(city.unhappiness, id, city) for id, city in self.cities_by_id.items() if city.unhappiness >= 1], reverse=True)
        revolt_choices = cities_to_revolt[:3]
        if len(cities_to_revolt) > 0:
            self.unhappiness_threshold = revolt_choices[-1][0]
        print(f"revolt choices: {[city.name for _, _, city in revolt_choices]}; threshold: {self.unhappiness_threshold}")
        revolt_ids = set(id for _, id, _ in revolt_choices)
        for _, _, city in revolt_choices:
            if city.civ_to_revolt_into is None:
                civ_name = self.sample_new_civs(1).pop(0)
                civ_template: CivTemplate = CivTemplate.from_json(CIVS[civ_name])
                city.civ_to_revolt_into = civ_template
                print(f"{city.name} => {city.civ_to_revolt_into=}")
        for id, city in self.cities_by_id.items():
            if id not in revolt_ids:
                city.civ_to_revolt_into = None

    def sample_new_civs(self, n):
        decline_choice_big_civ_pool = []

        advancement_level_to_use = max(self.advancement_level, 1)
        civs_already_in_game = [civ.template.name for civ in self.civs_by_id.values()] + \
            [city.civ.template.name for city in self.fresh_cities_for_decline.values()] + \
            [city.civ_to_revolt_into.name for city in self.cities_by_id.values() if city.civ_to_revolt_into is not None]
        for min_advancement_level in range(advancement_level_to_use, -1, -1):
            decline_choice_big_civ_pool = [civ['name'] for civ in ANCIENT_CIVS.values() 
                                           if civ['advancement_level'] <= advancement_level_to_use and civ['advancement_level'] >= min_advancement_level
                                           and civ['name'] not in civs_already_in_game]

            if len(decline_choice_big_civ_pool) >= n:
                break
        result = random.sample(decline_choice_big_civ_pool, n)       
        print(f"Sampling new civs ({n}). {advancement_level_to_use=}; \n Already present: {civs_already_in_game}\n Chose from: {decline_choice_big_civ_pool}\n Chose {result}")
        return result
    
    def retire_fresh_city_option(self, coords):
        print(f"retiring option at {coords}")
        self.fresh_cities_for_decline.pop(coords)
        camp_level: int = max(0, self.advancement_level - 2)
        print(f"Making camp at {coords} at level {camp_level}")
        self.hexes[coords].camp = Camp(self.barbarians, advancement_level=camp_level)

    def populate_fresh_cities_for_decline(self) -> None:
        self.fresh_cities_for_decline = {coords: city for coords, city in self.fresh_cities_for_decline.items()
                                             if is_valid_decline_location(self.hexes[coords], self.hexes, [self.hexes[other_coords] for other_coords in self.fresh_cities_for_decline if other_coords != coords])}
        new_locations_needed = max(2 - len(self.fresh_cities_for_decline), 0)
        if new_locations_needed == 0 and random.random() < 0.2 * len(self.game_player_by_player_num):  # Make one new camp per player per 5 turns.
            # randomly retire one of them
            coords: str = random.choice(list(self.fresh_cities_for_decline.keys()))
            self.retire_fresh_city_option(coords)
            new_locations_needed += 1
        print(f"Generating {new_locations_needed} fresh cities for decline.")
        new_hexes = generate_decline_locations(self.hexes, new_locations_needed, [self.hexes[coord] for coord in self.fresh_cities_for_decline])

        decline_choice_civ_pool = self.sample_new_civs(new_locations_needed)
        for hex, civ_name in zip(new_hexes, decline_choice_civ_pool):
            assert hex.city is None, f"Attempting to put a fresh decline city on an existing city! {hex.city.name} @ {hex.coords}; {new_hexes}"
            new_civ = Civ(CivTemplate.from_json(CIVS[civ_name]), game_player=None)

            city = self.new_city(new_civ, hex)
            city.unhappiness = 40
            # Note that city is NOT registered; i.e. hex.city is not this city, since this is a fake city.
            self.fresh_cities_for_decline[hex.coords] = city

    def create_decline_view(self, sess) -> None:
        from_civ_perspectives = []

        for coords in self.fresh_cities_for_decline:
            assert self.hexes[coords].city is None, f"City already exists at {coords}"
            city: City = self.process_decline_option(coords, from_civ_perspectives)
            city.is_decline_view_option = True
        
        for city in self.cities_by_id.values():
            if city.civ_to_revolt_into is not None:
                print(f"decline view for city {city.name}")
                assert city.hex is not None, "Somehow got a city with no hex registered."
                self.process_decline_option(city.hex.coords, from_civ_perspectives)
                city.is_decline_view_option = True
        
        self.refresh_foundability_by_civ()
        self.refresh_visibility_by_civ(short_sighted=True)

        sess.add(AnimationFrame(
            game_id=self.game_id,
            turn_num=self.turn_num,
            frame_num=0,
            player_num=100,
            is_decline=True,
            game_state=self.to_json(from_civ_perspectives=from_civ_perspectives),
        ))

        sess.commit()
 
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
            
            self.add_announcement(f'{civ.moniker()} built the {building_template.name}!')

    def add_animation_frame_for_civ(self, sess, data: dict[str, Any], civ: Optional[Civ], no_commit: bool = False) -> None:
        if data['type'] not in ['UnitAttack', 'UnitMovement', 'StartOfNewTurn']:
            # Get rid of this when we handle other animations
            return

        if civ is not None and (game_player := civ.game_player) is not None:
            highest_existing_frame_num = self.highest_existing_frame_num_by_civ_id[civ.id]

            frame = AnimationFrame(
                game_id=self.game_id,
                turn_num=self.turn_num,
                frame_num=highest_existing_frame_num + 1,
                player_num=game_player.player_num,
                data=data,
                game_state=self.to_json(from_civ_perspectives=[civ]),
            )

            sess.add(frame)
            if not no_commit:
                sess.commit()

            self.highest_existing_frame_num_by_civ_id[civ.id] += 1

        elif civ is None:
            highest_existing_frame_num = self.highest_existing_frame_num_by_civ_id['none']

            frame = AnimationFrame(
                game_id=self.game_id,
                turn_num=self.turn_num,
                frame_num=highest_existing_frame_num + 1,
                player_num=None,
                data=data,
                game_state=self.to_json(),
            )

            sess.add(frame)
            if not no_commit:
                sess.commit()

            self.highest_existing_frame_num_by_civ_id['none'] += 1

    def add_animation_frame(self, sess, data: dict[str, Any], hexes_must_be_visible: Optional[list[Hex]] = None, no_commit: bool = True) -> None:
        self.add_animation_frame_for_civ(sess, data, None, no_commit=True)

        for civ in self.civs_by_id.values():
            if hexes_must_be_visible is None or any(hex.visible_to_civ(civ) for hex in hexes_must_be_visible) and civ.game_player is not None:
                self.add_animation_frame_for_civ(sess, data, civ, no_commit=True)

        if not no_commit:
            sess.commit()


    def get_civ_by_name(self, civ_name: str) -> Civ:
        for civ in self.civs_by_id.values():
            if civ.template.name == civ_name:
                return civ
        raise Exception(f"Civ not found: {civ_name}, {self.civs_by_id}")
    
    def to_json(self, from_civ_perspectives: Optional[list[Civ]] = None, include_city_civ_details: bool = False) -> dict:
        if self.game_over:
            from_civ_perspectives = None

        return {
            "game_id": self.game_id,
            "hexes": {key: hex.to_json(from_civ_perspectives=from_civ_perspectives) for key, hex in self.hexes.items()},
            "civs_by_id": {civ_id: civ.to_json() for civ_id, civ in self.civs_by_id.items()},
            "cities_by_id": {city_id: city.to_json(include_civ_details=include_city_civ_details) for city_id, city in self.cities_by_id.items()},
            "game_player_by_player_num": {player_num: game_player.to_json() for player_num, game_player in self.game_player_by_player_num.items()},
            "turn_num": self.turn_num,
            "wonders_built_to_civ_id": self.wonders_built_to_civ_id.copy(),
            "national_wonders_built_by_civ_id": {k: v[:] for k, v in self.national_wonders_built_by_civ_id.items()},
            "special_mode_by_player_num": self.special_mode_by_player_num.copy(),
            "barbarians": self.barbarians.to_json(),
            "advancement_level": self.advancement_level,
            "game_over": self.game_over,
            "game_end_score": self.game_end_score(),
            "announcements": self.announcements[:],
            "fresh_cities_for_decline": {coords: city.to_json(include_civ_details=True) for coords, city in self.fresh_cities_for_decline.items()},
            "unhappiness_threshold": self.unhappiness_threshold,
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
        # game_state.cities_by_id set from the other entries, to ensure references are all good.
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
        game_state.fresh_cities_for_decline = {coords: City.from_json(city_json) for coords, city_json in json["fresh_cities_for_decline"].items()}
        game_state.set_unit_and_city_hexes()
        game_state.set_civ_targets(hexes)
        game_state.game_over = json["game_over"]
        game_state.announcements = json["announcements"][:]
        game_state.unhappiness_threshold = float(json["unhappiness_threshold"])
        game_state.midturn_update()
        return game_state
