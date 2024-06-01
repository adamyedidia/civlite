import math
from typing import Any, Optional
from animation_frame import AnimationFrame
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from camp import Camp
from collections import defaultdict
from city import City, generate_random_city_name
from civ import Civ
from civ_template import CivTemplate
from civ_templates_list import CIVS, player_civs
from wonder_templates_list import WONDERS
from wonder_built_info import WonderBuiltInfo
from wonder_template import WonderTemplate
from game_player import GamePlayer
from hex import Hex
from map import generate_decline_locations, is_valid_decline_location
from redis_utils import rget_json, rlock, rset_json, rdel, rset, rget
from settings import STARTING_CIV_VITALITY, GAME_END_SCORE, SURVIVAL_BONUS, EXTRA_GAME_END_SCORE_PER_PLAYER, MULLIGAN_PENALTY, BASE_WONDER_COST
from tech_template import TechTemplate
from tech_templates_list import TECHS
from unit import Unit
import random
from unit_templates_list import UNITS_BY_BUILDING_NAME, UNITS
from unit_template import UnitTag, UnitTemplate
from utils import dream_key, staged_moves_key, deterministic_hash

from sqlalchemy import and_, func

from animation_frame import AnimationFrame

from collections import defaultdict


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

# TODO this shouldn't be in game_state.py
def make_game_statistics_plots(sess, game_id: str):
    # Find the last frame for each turn. GPT4 wrote these queries
    # Subquery to find the maximum frame_num for each turn_num
    max_frame_subquery = (
        sess.query(
            AnimationFrame.turn_num,
            func.max(AnimationFrame.frame_num).label('max_frame_num')
        )
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.player_num == None)
        .group_by(AnimationFrame.turn_num)
        .subquery()
    )

    # Main query to fetch the frames with the highest frame_num for each turn_num
    animation_frames = (
        sess.query(AnimationFrame)
        .join(
            max_frame_subquery,
            and_(
                AnimationFrame.turn_num == max_frame_subquery.c.turn_num,
                AnimationFrame.frame_num == max_frame_subquery.c.max_frame_num
            )
        )
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.player_num == None)
        .filter(AnimationFrame.turn_num > 1)  # Exclude the first turn which has hallucinated state
        .order_by(AnimationFrame.turn_num)
        .all()
    )

    scores_by_turn = defaultdict(list)
    cum_scores_by_turn = defaultdict(list)
    actual_cum_scores_by_turn = defaultdict(list)

    civ_ids_by_player = None

    turn_nums = []
    decline_turns = defaultdict(list)
    decline_turns_for_civs: dict[str, int] = {}
    start_turns_for_civs = defaultdict(lambda: 1)
    dead_turns: dict[str, int] = {}

    # In all the following, we initialize to a list with one entry.
    # Because the first time we notice you is the start of the turn AFTER you were born
    # So the plots are more intuitive if we prepend one tur of data from the turn you were born.
    total_yields_by_turn = defaultdict(lambda: [0.0])
    military_strength_by_turn = defaultdict(lambda: [0.0])
    civ_scores_by_turn = defaultdict(lambda: [0.0])
    civ_cumulative_scores_by_turn = defaultdict(list)
    vitality = defaultdict(list)
    population = defaultdict(lambda: [0.0])
    movie_frames = []

    civs_that_have_ever_had_game_player = {}

    for frame in animation_frames:
        game_state = GameState.from_json(frame.game_state)
        for player_num in game_state.game_player_by_player_num:
            player = game_state.game_player_by_player_num[player_num]
            player_score_excluding_survival = player.score - player.score_from_survival
            scores_by_turn[player.username].append(player_score_excluding_survival - (cum_scores_by_turn[player.username][-1] if cum_scores_by_turn[player.username] else 0))
            cum_scores_by_turn[player.username].append(player_score_excluding_survival)
            actual_cum_scores_by_turn[player.username].append(player.score)

        turn_nums.append(frame.turn_num)

        old_civ_ids_by_player = (civ_ids_by_player or {}).copy()

        civ_ids_by_player = {
            player_num: game_state.game_player_by_player_num[player_num].civ_id
            for player_num in game_state.game_player_by_player_num
        }

        for player_num in game_state.game_player_by_player_num:
            game_player = game_state.game_player_by_player_num[player_num]
            if old_civ_ids_by_player and old_civ_ids_by_player[player_num] != game_player.civ_id:
                decline_turns[game_player.username].append(frame.turn_num - 1)
                decline_turns_for_civs[old_civ_ids_by_player[player_num]] = frame.turn_num - 1


        yields_by_civ = defaultdict(float)
        total_metal_value_by_civ = defaultdict(int)
        pop_by_civ = defaultdict(int)


        for civ_id, civ in game_state.civs_by_id.items():
            if civ_id not in start_turns_for_civs and civ_id != game_state.barbarians.id:
                start_turns_for_civs[civ_id] = frame.turn_num - 1
                # Add vitality for the previous turn when we appeared
                vitality[civ_id].append(civ.vitality / 0.92)
                if not civ.game_player:
                    # Rebels start declined
                    decline_turns_for_civs[civ_id] = frame.turn_num - 1
                else:
                    # Add cum score for the previous turn when we appeared
                    if frame.turn_num > 2:
                        civ_cumulative_scores_by_turn[civ_id].append(actual_cum_scores_by_turn[civ.game_player.username][-2])
                    else:
                        civ_cumulative_scores_by_turn[civ_id].append(0)

            vitality[civ_id].append(civ.vitality)

            if civ.game_player:
                civs_that_have_ever_had_game_player[civ_id] = civ.game_player.player_num
                civ_scores_by_turn[civ_id].append(scores_by_turn[civ.game_player.username][-1])
                civ_cumulative_scores_by_turn[civ_id].append(actual_cum_scores_by_turn[civ.game_player.username][-1])

        for city_id in game_state.cities_by_id:
            city = game_state.cities_by_id[city_id]
            city.adjust_projected_yields(game_state)
            total_yields = city.projected_income['food'] + city.projected_income['wood'] + city.projected_income['metal'] + city.projected_income['science']
            yields_by_civ[city.civ_id] += total_yields
            pop_by_civ[city.civ_id] += city.population

        for unit in game_state.units:
            total_metal_value_by_civ[unit.civ_id] += unit.template.metal_cost

        for civ_id, civ in game_state.civs_by_id.items():
            total_yields_by_turn[civ_id].append(yields_by_civ[civ_id])
            military_strength_by_turn[civ_id].append(total_metal_value_by_civ[civ_id])
            population[civ_id].append(pop_by_civ[civ_id])
            if yields_by_civ[civ_id] == 0 and total_metal_value_by_civ[civ_id] == 0 and civ_id not in dead_turns:
                dead_turns[civ_id] = frame.turn_num

        def civ_color(hex) -> str | None:
            if hex.city:
                return hex.city.civ_id
           
            neighbor_city_civs = {n.city.civ_id for n in hex.get_neighbors(game_state.hexes) if n.city}
            if len(neighbor_city_civs) == 1:
                return neighbor_city_civs.pop()
            if len(neighbor_city_civs) > 1:
                if len(hex.units) > 0 and hex.units[0].civ_id in neighbor_city_civs:
                    return hex.units[0].civ_id

            return None

        movie_frames.append({
            'turn_num': frame.turn_num,
            'hexes': [{
                'coords': {'q': hex.q, 'r': hex.r, 's': hex.s},
                'civ': civ_color(hex), 
                'city': hex.city is not None,
                'puppet': hex.city is not None and not hex.city.is_territory_capital,
                'camp': hex.camp is not None,
                }
                for hex in game_state.hexes.values()],
        })

    civ_infos = {
        civ_id: {
            'start_turn': start_turns_for_civs[civ_id],
            'decline_turn': decline_turns_for_civs.get(civ_id, None),
            'dead_turn': dead_turns.get(civ_id, None),
            'player_num': civs_that_have_ever_had_game_player.get(civ_id, None),
        }
        for civ_id in start_turns_for_civs
    }

    stats = {
        'score_per_turn': civ_scores_by_turn,
        'cumulative_score': civ_cumulative_scores_by_turn,
        'total_yields': total_yields_by_turn,
        'military_strength': military_strength_by_turn,
        'population': population,
        'vitality': vitality,
    }

    return civ_infos, stats, movie_frames

class GameState:
    def __init__(self, game_id: str, hexes: dict[str, Hex]):
        self.hexes: dict[str, Hex] = hexes
        self.game_id = game_id
        self.units: list[Unit] = get_all_units(hexes)
        self.cities_by_id: dict[str, City] = get_all_cities(hexes)
        self.camps: list[Camp] = get_all_camps(hexes)
        self.barbarians: Civ = Civ(CIVS.BARBARIAN, None)  
        self.civs_by_id: dict[str, Civ] = {self.barbarians.id: self.barbarians}
        self.turn_num = 1
        self.game_player_by_player_num: dict[int, GamePlayer] = {}
        self.wonders_built_to_civ_id: dict[str, str] = {}  # TODO remove
        self.wonders_by_age: dict[int, list[WonderTemplate]] = {}
        self.built_wonders: dict[WonderTemplate, WonderBuiltInfo] = {}
        self.wonder_cost_by_age: dict[int, int] = BASE_WONDER_COST.copy()
        self.national_wonders_built_by_civ_id: dict[str, list[str]] = {}
        self.special_mode_by_player_num: dict[int, Optional[str]] = {}
        self.advancement_level = 0
        self.game_over = False  # TODO delete
        self.announcements = []
        self.fresh_cities_for_decline: dict[str, City] = {}
        self.unhappiness_threshold: float = 0.0
        self.civ_ids_with_game_player_at_turn_start: list[str] = []

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

    def fresh_cities_from_json_postprocess(self) -> None:
        for coords, city in self.fresh_cities_for_decline.items():
            city.hex = self.hexes[coords]

    def pick_random_hex(self) -> Hex:
        return random.choice(list(self.hexes.values()))

    def register_city(self, city):
        city.hex.city = city
        city.founded_turn = self.turn_num
        self.cities_by_id[city.id] = city

    def new_city(self, civ: Civ, hex: Hex, city_id: Optional[str] = None) -> City:
        city_name = generate_random_city_name(game_state=self)
        city = City(civ, name=city_name, id=city_id)
        city.hex = hex
        city.populate_terrains_dict(self)
        city.refresh_available_wonders(self)
        return city

    def register_camp(self, camp, hex):
        camp.hex = hex
        hex.camp = camp
        self.camps.append(camp)

    def unregister_camp(self, camp):
        camp.hex.camp = None
        self.camps.remove(camp)

    def initialize_wonders(self):
        assert len(self.game_player_by_player_num) > 0, "Cannot initialize wonders without players"
        wonders_per_age: int = len(self.game_player_by_player_num) - 1
        self.wonders_by_age: dict[int, list[WonderTemplate]] = {
            age: sorted(random.sample(list(WONDERS.all_by_age(age)), wonders_per_age), key=lambda w: w.name) for age in range(0, 10)}

    def update_wonder_cost_by_age(self) -> None:
        for age in self.wonders_by_age.keys():
            self.wonder_cost_by_age[age] = self._wonder_cost(age)

    def _wonder_cost(self, age: int) -> int:
        base: int = BASE_WONDER_COST[age]
        num_built: int = len([w for w in self.built_wonders if w.age == age])
        total_num: int = len(self.wonders_by_age[age])
        # The first one costs base, the last one 2 * base
        cost = int(base * (1 + num_built / max(total_num - 1, 1)))
        return cost

    def found_city_for_civ(self, civ: Civ, hex: Hex, city_id: str | None) -> City:
        civ.city_power -= 100
        city = self.new_city(civ, hex, city_id)
        self.register_city(city)
        city.set_territory_parent_if_needed(game_state=self)

        if civ.game_player:
            civ.game_player.score += 2
            civ.game_player.score_from_capturing_cities_and_camps += 2
            civ.score += 2

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
    
        self.refresh_foundability_by_civ()
        self.midturn_update() 
        city.hide_bad_buildings()
        return city

    def enter_decline_for_civ(self, civ: Civ, game_player: GamePlayer) -> None:
        self.add_announcement(f'The <civ id={civ.id}>{civ.moniker()}</civ> have entered decline!')                
        civ.game_player = None
        civ.in_decline = True
        game_player.civ_id = None

        for other_civ in self.civs_by_id.values():
            if other_civ.id != civ.id:
                if other_civ.game_player:
                    other_civ.game_player.score += SURVIVAL_BONUS
                    other_civ.game_player.score_from_survival += SURVIVAL_BONUS

    def choose_techs_for_new_civ(self, city: City) -> set[TechTemplate]:
        print("Calculating starting techs!")
        assert city.hex is not None
        # Make this function deterministic across staging and rolling
        random.seed(deterministic_hash(f"{self.game_id} {self.turn_num} {city.name} {city.hex.coords}"))
        chosen_techs: set[TechTemplate] = set()
        chosen_techs_by_advancement = defaultdict(int)

        # Start with prereqs for the buildings we have
        for building in city.buildings:
            prereq = building.prereq
            if prereq is not None:
                chosen_techs.add(prereq)
                chosen_techs_by_advancement[prereq.advancement_level] += 1

        print(f"Starting with prereqs for buildings: {chosen_techs}")

        # Calculate mean tech amount at each level
        civs_to_compare_to: list[Civ] = [civ for civ in self.civs_by_id.values() if civ.id in self.civ_ids_with_game_player_at_turn_start and civ != city.civ]
        if len(civs_to_compare_to) == 0:
            civs_to_compare_to = [civ for civ in self.civs_by_id.values()]

        print(f"  Comparing to civs: {civs_to_compare_to}")
        # Make a dict of {tech: num civs that know it} for each level
        tech_counts_by_adv_level = defaultdict(dict[TechTemplate, int])
        for tech in TECHS.all():
            num = len([civ for civ in civs_to_compare_to if civ.has_tech(tech)])
            lvl = tech.advancement_level
            tech_counts_by_adv_level[lvl][tech] = num

        excess_techs = 0
        for level in sorted(list(tech_counts_by_adv_level.keys()), reverse=True):
            tech_counts: dict[TechTemplate, int] = tech_counts_by_adv_level[level]
            total = sum(tech_counts.values())
            target_num = total / len(civs_to_compare_to) - excess_techs
            print(f"Level {level}; excess {excess_techs}; target: {target_num}")
            if chosen_techs_by_advancement[level] > target_num:
                excess_techs = chosen_techs_by_advancement[level] - target_num
                continue
            else:
                num_needed = target_num - chosen_techs_by_advancement[level]
                available = [tech for tech in tech_counts_by_adv_level[level] if tech not in chosen_techs]
                available.sort(key=lambda tech: (tech_counts_by_adv_level[level][tech], random.random()), reverse=True)
                choose = available[:math.floor(num_needed)]
                print(f"  chose: {choose}")
                for tech in choose:
                    chosen_techs.add(tech)
                excess_techs = len(choose) - num_needed

        return chosen_techs
        

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
        city.refresh_available_wonders(self)
        self.midturn_update()

        self.add_announcement(f'The <civ id={civ.id}>{civ.moniker()}</civ> have been founded in <city id={city.id}>{city.name}</city>!')        

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
        civ.get_great_person(self.advancement_level, city)
        print(f"New civ {civ} great people choices: {civ.great_people_choices}")

        return from_civ_perspectives


    def process_decline_option(self, coords: str, from_civ_perspectives: list[Civ], is_game_player: bool=True) -> City:
        """
        The parts of entering decline that happen both when you do it for real,
        and when the special decline options view GameState is produced.
        """
        hex = self.hexes[coords]
        if hex.city:
            # This is not a fresh city , it's a pre-existing one.
            old_civ: Optional[Civ] = hex.city.civ
            print(f"Declining to existing city at {coords}")
            assert hex.city.civ_to_revolt_into is not None, f"Trying to revolt into a city {hex.city.name} with no city.civ_to_revolt_into"
            hex.city.change_owner(Civ(hex.city.civ_to_revolt_into, game_player=None), game_state=self)
            hex.city.civ.vandetta_civ_id = old_civ.id
        else:
            # This is a fake city, now it is becoming a real city.
            old_civ: Optional[Civ] = None
            print(f"Declining to fresh city at {coords}")
            self.register_city(self.fresh_cities_for_decline[coords])
        assert hex.city is not None, "Failed to register city!"
        hex.city.wood = hex.city.metal = hex.city.unhappiness = 0
        hex.city.capitalize(self)
        hex.city.population = max(hex.city.population, self.advancement_level + 1)
        hex.city.civ_to_revolt_into = None
        hex.city.buildings = [b for b in hex.city.buildings if not b.is_national_wonder]

        new_civ: Civ = hex.city.civ
        new_civ.vitality = hex.city.revolting_starting_vitality
        self.civs_by_id[new_civ.id] = new_civ
        from_civ_perspectives.append(new_civ)

        unit_count = 0
        hexes_to_steal_from: list[Hex] = [hex, *hex.get_neighbors(self.hexes)] if is_game_player else [hex]
        print(f"Stealing units from {hexes_to_steal_from}")
        for neighbor_hex in hexes_to_steal_from:
            for unit in neighbor_hex.units:
                if unit.civ == old_civ or unit.civ.template == CIVS.BARBARIAN:
                    unit.civ = new_civ
                    stack_size: int = unit.get_stack_size()
                    unit_count += stack_size
        for neighbor_hex in [hex, *hex.get_neighbors(self.hexes)]:
            if neighbor_hex.camp is not None:
                self.unregister_camp(neighbor_hex.camp)
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

        for move_index, move in enumerate(moves):
            # This has to be deterministic to allow speculative and non-speculative calls to agree
            seed_value = deterministic_hash(f"{self.game_id} {player_num} {self.turn_num}")
            random.seed(seed_value)
            if ('city_id' in move and (city_id := move['city_id']) is not None 
                    and (city_owner := (city_owner_by_city_id or {}).get(city_id)) is not None 
                    and city_owner != player_num):
                continue
            if move['move_type'] == 'choose_starting_city':
                city_id = move['city_id']
                self.special_mode_by_player_num[player_num] = None

                for city in self.cities_by_id.values():
                    if city.civ.game_player is not None and (game_player := city.civ.game_player) and game_player.player_num == player_num:
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
                                self.register_camp(Camp(self.barbarians), city.hex)

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
                tech = TECHS.by_name(tech_name)
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                civ.select_tech(tech)
                game_player_to_return = game_player

            if move['move_type'] == 'choose_building':
                building_name = move['building_name']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]


                if building_name in UNITS_BY_BUILDING_NAME:
                    building = UNITS_BY_BUILDING_NAME[building_name]
                elif building_name in {b.name for b in BUILDINGS.all()}:
                    building = BUILDINGS.by_name(building_name)
                elif building_name in {w.name for w in WONDERS.all()}:
                    building = WONDERS.by_name(building_name)
                else:
                    raise ValueError(f"Unknown building name {building_name}")
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

            if move['move_type'] == 'hide_building':
                building_name = move['building_name']
                hidden = move['hidden']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]
                city.toggle_discard(building_name, hidden)
                game_player_to_return = game_player
                city.midturn_update(self)

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
                    unit = UNITS.by_name(unit_name)

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
                print(f"{move=}")
                game_player = self.game_player_by_player_num[player_num]
                city_id = move['city_id']
                city = self.cities_by_id[city_id]
                city.focus = move['focus']
                if move.get('with_puppets'):
                    for puppet in city.get_puppets(self):
                        puppet.focus = move['focus']
                        
                game_player_to_return = game_player
                self.midturn_update()

            if move['move_type'] == 'make_territory':
                game_player = self.game_player_by_player_num[player_num]
                city_id: str = move['city_id']
                city: City = self.cities_by_id[city_id]
                previous_parent: City | None = city.get_territory_parent(self)
                civ = city.civ
                if civ.city_power > 100:
                    civ.city_power -= 100
                    city.make_territory_capital(self)

                    instead_of_city_id: str = move['other_city_id']
                    print(f"{instead_of_city_id=}")
                    if instead_of_city_id is not None:
                        instead_of_city: City = self.cities_by_id[instead_of_city_id]
                        instead_of_city.set_territory_parent_if_needed(self)
                        instead_of_city.orphan_territory_children(self, make_new_territory=False)
                        print(f"{instead_of_city._territory_parent_id=}")
                    if previous_parent is not None and previous_parent.id != instead_of_city_id:
                        previous_parent.orphan_territory_children(self, make_new_territory=False)

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

            if move['move_type'] == 'select_great_person':
                game_player: GamePlayer = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ: Civ = self.civs_by_id[game_player.civ_id]
                civ.select_great_person(self, move['great_person_name'])
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
        # Population-wieghted average civ advancement level.
        weighted_levels = [(c.population, c.civ.get_advancement_level()) for c in self.cities_by_id.values()]
        total_population = sum(level[0] for level in weighted_levels)
        weighted_average = sum(level[0] / total_population * level[1] for level in weighted_levels)
        self.advancement_level = math.ceil(weighted_average)

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

        civs: list[Civ] = list(self.civs_by_id.values())

        for civ in civs:
            game_player: GamePlayer | None = civ.game_player
            if (game_player is None or game_player.is_bot) and not civ.template.name == 'Barbarians':
                # decline if they want to
                if game_player and not civ.in_decline and (decline_coords := civ.bot_decide_decline(self)):
                    self.execute_decline(decline_coords, game_player)
                    new_civ_id = game_player.civ_id
                    assert new_civ_id is not None
                    assert new_civ_id != civ.id, f"Bot player {game_player.player_num} is trying to decline but somehow failed? {civ.id=} {new_civ_id=}"
                    self.civs_by_id[new_civ_id].bot_move(self)
                else:
                    civ.bot_move(self)

        for player_num, game_player in self.game_player_by_player_num.items():
            if game_player.civ_id is None:
                game_player.score -= MULLIGAN_PENALTY
                game_player.score_from_survival -= MULLIGAN_PENALTY

        print(f'GameState ending turn {self.turn_num}')

        self.roll_turn(sess)

        print("committing changes")
        sess.commit()

        self.civ_ids_with_game_player_at_turn_start = [civ.id for civ in self.civs_by_id.values() if civ.game_player is not None]

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
        print(f"GameState incrementing turn {self.turn_num} -> {self.turn_num + 1}")

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
            unit.turn_end(self)

        for game_player in self.game_player_by_player_num.values():
            game_player.decline_this_turn = False
            game_player.failed_to_decline_this_turn = False

        self.midturn_update()      

        self.sync_advancement_level()

        self.refresh_visibility_by_civ()
        self.refresh_foundability_by_civ()
        self.update_wonder_cost_by_age()

        for civ in self.civs_by_id.values():
            civ.fill_out_available_buildings(self)

        for city in self.cities_by_id.values():
            city.refresh_available_buildings()     
            city.refresh_available_wonders(self)

        for game_player in self.game_player_by_player_num.values():
            if game_player.score >= self.game_end_score():
                self.game_over = True

                break

        self.handle_decline_options()
        for city in self.fresh_cities_for_decline.values():
            city.roll_turn(sess, self, fake=True)

    def handle_decline_options(self):
        self.populate_fresh_cities_for_decline()
        needed_revolt_choices: int = 5 - len(self.fresh_cities_for_decline)
        cities_to_revolt: list[tuple[float, str, City]] = sorted([(city.unhappiness, id, city) for id, city in self.cities_by_id.items() if city.unhappiness >= 1 and city.under_siege_by_civ is None], reverse=True)
        revolt_choices: list[tuple[float, str, City]] = cities_to_revolt[:needed_revolt_choices]
        if len(revolt_choices) > 0:
            self.unhappiness_threshold = revolt_choices[-1][0]
        else:
            self.unhappiness_threshold = 0
        print(f"revolt choices: {[city.name for _, _, city in revolt_choices]}; threshold: {self.unhappiness_threshold}")
        revolt_ids = set(id for _, id, _ in revolt_choices)
        for _, _, city in revolt_choices:
            if city.civ_to_revolt_into is None:
                civ_template = self.sample_new_civs(1).pop(0)
                city.civ_to_revolt_into = civ_template
                print(f"{city.name} => {city.civ_to_revolt_into=}")
        for id, city in self.cities_by_id.items():
            if id not in revolt_ids:
                city.civ_to_revolt_into = None

    def sample_new_civs(self, n) -> list[CivTemplate]:
        decline_choice_big_civ_pool = []

        advancement_level_to_use = max(self.advancement_level, 1)
        civs_already_in_game: list[CivTemplate] = [civ.template for civ in self.civs_by_id.values()] + \
            [city.civ.template for city in self.fresh_cities_for_decline.values()] + \
            [city.civ_to_revolt_into for city in self.cities_by_id.values() if city.civ_to_revolt_into is not None]
        for min_advancement_level in range(advancement_level_to_use, -1, -1):
            decline_choice_big_civ_pool: list[CivTemplate] = [civ for civ in player_civs(min_advancement_level=min_advancement_level, max_advancement_level=advancement_level_to_use) 
                                           if civ not in civs_already_in_game]

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
        self.register_camp(Camp(self.barbarians, advancement_level=camp_level), self.hexes[coords])

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
        for hex, civ_template in zip(new_hexes, decline_choice_civ_pool):
            assert hex.city is None, f"Attempting to put a fresh decline city on an existing city! {hex.city.name} @ {hex.coords}; {new_hexes}"
            new_civ = Civ(civ_template, game_player=None)

            city = self.new_city(new_civ, hex)
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

    def handle_wonder_built(self, civ: Civ, wonder: WonderTemplate) -> None:
        self.wonders_built_to_civ_id[wonder.name] = civ.id
        player_num: int | None = civ.game_player.player_num if civ.game_player is not None else None
        if wonder in self.built_wonders:
            self.built_wonders[wonder].player_nums.append(player_num)
            self.built_wonders[wonder].civs.append(civ)
        else:
            self.built_wonders[wonder] = WonderBuiltInfo([player_num], [civ], self.turn_num)
        
        if (game_player := civ.game_player) is not None:
            if civ.has_ability('ExtraVpsPerWonder'):
                game_player.score += civ.numbers_of_ability('ExtraVpsPerWonder')[0]
                game_player.score_from_abilities += civ.numbers_of_ability('ExtraVpsPerWonder')[0]
                civ.score += civ.numbers_of_ability('ExtraVpsPerWonder')[0]

        self.add_announcement(f'<civ id={civ.id}>{civ.moniker()}</civ> built the <wonder name={wonder.name}>{wonder.name}<wonder>!')

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

    def wonder_buildable(self, wonder) -> bool:
        if wonder.age > self.advancement_level:
            # Can't build it yet
            return False
        if wonder in self.built_wonders:
            return False
        return True

    def available_wonders(self) -> list[WonderTemplate]:
        # This only gets called after the game has fully rolled, so it wont' prevent the 2nd player building the wonder in the same turn
        # To make ties be generous.
        return [wonder for wonders in self.wonders_by_age.values() for wonder in wonders if self.wonder_buildable(wonder)]

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
            "wonders_by_age": {age: [wonder.name for wonder in wonders] for age, wonders in self.wonders_by_age.items()},
            "built_wonders": {wonder.name: built_wonder.to_json() for wonder, built_wonder in self.built_wonders.items()},
            "available_wonders": [w.name for w in self.available_wonders()],
            "national_wonders_built_by_civ_id": {k: v[:] for k, v in self.national_wonders_built_by_civ_id.items()},
            "special_mode_by_player_num": self.special_mode_by_player_num.copy(),
            "barbarians": self.barbarians.to_json(),
            "advancement_level": self.advancement_level,
            "game_over": self.game_over,
            "game_end_score": self.game_end_score(),
            "announcements": self.announcements[:],
            "fresh_cities_for_decline": {coords: city.to_json(include_civ_details=True) for coords, city in self.fresh_cities_for_decline.items()},
            "unhappiness_threshold": self.unhappiness_threshold,
            "civ_ids_with_game_player_at_turn_start": self.civ_ids_with_game_player_at_turn_start,
            "wonder_cost_by_age": self.wonder_cost_by_age,
        }

    @staticmethod
    def from_json(json: dict) -> "GameState":
        hexes = {key: Hex.from_json(hex_json) for key, hex_json in json["hexes"].items()}
        game_state = GameState(game_id=json["game_id"], hexes=hexes)
        game_state.game_player_by_player_num = {int(player_num): GamePlayer.from_json(game_player_json) for player_num, game_player_json in json["game_player_by_player_num"].items()}        
        game_state.civs_by_id = {civ_id: Civ.from_json(civ_json) for civ_id, civ_json in json["civs_by_id"].items()}
        game_state.civ_ids_with_game_player_at_turn_start = json["civ_ids_with_game_player_at_turn_start"]
        # game_state.cities_by_id set from the other entries, to ensure references are all good.
        game_state.barbarians = [civ for civ in game_state.civs_by_id.values() if civ.template == CIVS.BARBARIAN][0]
        game_state.advancement_level = json["advancement_level"]

        game_state.turn_num = json["turn_num"]
        game_state.wonders_built_to_civ_id = json["wonders_built_to_civ_id"].copy()
        game_state.wonders_by_age = {int(age): [WONDERS.by_name(wonder_name) for wonder_name in wonder_names] for age, wonder_names in json["wonders_by_age"].items()}
        game_state.built_wonders = {WONDERS.by_name(wonder_name): WonderBuiltInfo.from_json(wonder_json, game_state) for wonder_name, wonder_json in json["built_wonders"].items()}
        game_state.wonder_cost_by_age = {int(age): cost for age, cost in json["wonder_cost_by_age"].items()}
        game_state.national_wonders_built_by_civ_id = {k: v[:] for k, v in json["national_wonders_built_by_civ_id"].items()}
        game_state.special_mode_by_player_num = {int(k): v for k, v in json["special_mode_by_player_num"].items()}
        game_state.fresh_cities_for_decline = {coords: City.from_json(city_json) for coords, city_json in json["fresh_cities_for_decline"].items()}
        game_state.game_over = json["game_over"]
        game_state.announcements = json["announcements"][:]
        game_state.unhappiness_threshold = float(json["unhappiness_threshold"])

        for civ in game_state.civs_by_id.values():
            civ.from_json_postprocess(game_state)
        for hex in game_state.hexes.values():
            hex.from_json_postprocess(game_state)
            # That sets game_state.units and game_state.cities_by_id
        game_state.fresh_cities_from_json_postprocess()
        game_state.midturn_update()
        return game_state
