import math
from typing import Any, Generator, Optional
from animation_frame import AnimationFrame
from building import QueueEntry
from camp import Camp
from collections import defaultdict
from city import City, get_city_name_for_civ
from civ import Civ
from civ_template import CivTemplate
from civ_templates_list import CIVS, find_civ_pool
from map_object import MapObject
from move_type import MoveType
from region import Region
from settings import GOD_MODE
from terrain_templates_list import TERRAINS
from unit_building import UnitBuilding
from wonder_templates_list import WONDERS
from wonder_built_info import WonderBuiltInfo
from wonder_template import WonderTemplate
from game_player import GamePlayer
from hex import Hex
from map import generate_decline_locations, is_valid_decline_location
from redis_utils import rget_json, rlock, rdel, rset, rget
from settings import STARTING_CIV_VITALITY, GAME_END_SCORE, BASE_SURVIVAL_BONUS, STRICT_MODE, SURVIVAL_BONUS_PER_AGE, EXTRA_GAME_END_SCORE_PER_PLAYER, BASE_WONDER_COST, WONDER_COUNT_FOR_PLAYER_NUM
from tech_template import TechTemplate
from tech_templates_list import TECHS
from unit import Unit
import random
from unit_templates_list import UNITS
from utils import dream_key, staged_moves_key, deterministic_hash

from sqlalchemy import and_, func

from animation_frame import AnimationFrame

from collections import defaultdict
from logging_setup import logger



SURVIVAL_SCORE_LABEL = f"Survival"

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

    game_ages = [None, 0]  # No age on turn 0, age 0 on turn 1
    decline_turns = defaultdict(list)
    decline_turns_for_civs: dict[str, int] = {}
    start_turns_for_civs = defaultdict(lambda: 1)
    dead_turns: dict[str, int] = {}

    # In all the following, we initialize to a list with one entry.
    # Because the first time we notice you is the start of the turn AFTER you were born
    # So the plots are more intuitive if we prepend one turn of data from the turn you were born.
    total_yields_by_turn = defaultdict(lambda: [0.0])
    military_strength_by_turn = defaultdict(lambda: [0.0])
    civ_scores_by_turn = defaultdict(lambda: [0.0])
    civ_cumulative_scores_by_turn = defaultdict(list)
    civ_cumulative_scores_wo_survival_by_turn = defaultdict(list)
    civ_ages = defaultdict(list)
    vitality = defaultdict(list)
    population = defaultdict(lambda: [0.0])
    movie_frames = []

    civs_that_have_ever_had_game_player = {}

    for frame in animation_frames:
        game_state = GameState.from_json(frame.game_state)
        for player_num in game_state.game_player_by_player_num:
            player = game_state.game_player_by_player_num[player_num]
            player_score_excluding_survival = player.score - player.score_dict.get(SURVIVAL_SCORE_LABEL, 0)
            scores_by_turn[player.username].append(player_score_excluding_survival - (cum_scores_by_turn[player.username][-1] if cum_scores_by_turn[player.username] else 0))
            cum_scores_by_turn[player.username].append(player_score_excluding_survival)
            actual_cum_scores_by_turn[player.username].append(player.score)

        assert game_state.turn_num == len(game_ages), f"Turn num {frame.turn_num} != game_ages length {len(game_ages)}"
        game_ages.append(game_state.advancement_level)

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
                # Add vitality and age for the previous turn when we appeared
                vitality[civ_id].append(civ.vitality / 0.92)
                civ_ages[civ_id].append(civ.get_advancement_level())
                if not civ.game_player:
                    # Rebels start declined
                    decline_turns_for_civs[civ_id] = frame.turn_num - 1
                else:
                    # Add cum score for the previous turn when we appeared
                    if frame.turn_num > 2:
                        civ_cumulative_scores_by_turn[civ_id].append(actual_cum_scores_by_turn[civ.game_player.username][-2])
                        civ_cumulative_scores_wo_survival_by_turn[civ_id].append(cum_scores_by_turn[civ.game_player.username][-2])
                    else:
                        civ_cumulative_scores_by_turn[civ_id].append(0)
                        civ_cumulative_scores_wo_survival_by_turn[civ_id].append(0)

            vitality[civ_id].append(civ.vitality)
            civ_ages[civ_id].append(civ.get_advancement_level())

            if civ.game_player:
                civs_that_have_ever_had_game_player[civ_id] = civ.game_player.player_num
                civ_scores_by_turn[civ_id].append(scores_by_turn[civ.game_player.username][-1])
                civ_cumulative_scores_by_turn[civ_id].append(actual_cum_scores_by_turn[civ.game_player.username][-1])
                civ_cumulative_scores_wo_survival_by_turn[civ_id].append(cum_scores_by_turn[civ.game_player.username][-1])

        for city_id in game_state.cities_by_id:
            city = game_state.cities_by_id[city_id]
            city.adjust_projected_yields(game_state)
            total_yields = city.projected_income['food'] + city.projected_income['wood'] + city.projected_income['metal'] + city.projected_income['science']
            yields_by_civ[city.civ.id] += total_yields
            pop_by_civ[city.civ.id] += city.population

        for unit in game_state.units:
            total_metal_value_by_civ[unit.civ.id] += unit.template.metal_cost * unit.get_stack_size()

        for civ_id, civ in game_state.civs_by_id.items():
            total_yields_by_turn[civ_id].append(yields_by_civ[civ_id])
            military_strength_by_turn[civ_id].append(total_metal_value_by_civ[civ_id])
            population[civ_id].append(pop_by_civ[civ_id])
            if yields_by_civ[civ_id] == 0 and total_metal_value_by_civ[civ_id] == 0 and civ_id not in dead_turns:
                dead_turns[civ_id] = frame.turn_num

        def civ_color(hex: Hex) -> str | None:
            if hex.city:
                return hex.city.civ.id
           
            neighbor_city_civs = {n.city.civ.id for n in hex.get_neighbors(game_state.hexes) if n.city}
            if len(neighbor_city_civs) == 1:
                return neighbor_city_civs.pop()
            if len(neighbor_city_civs) > 1:
                if len(hex.units) > 0 and hex.units[0].civ.id in neighbor_city_civs:
                    return hex.units[0].civ.id

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
                for hex in game_state.hexes.values() if hex.terrain != TERRAINS.OCEAN],
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
        'cumulative_score_wo_survival': civ_cumulative_scores_wo_survival_by_turn,
        'total_yields': total_yields_by_turn,
        'military_strength': military_strength_by_turn,
        'population': population,
        'vitality': vitality,
        'game_ages': game_ages,
        'civ_ages': civ_ages,
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
        self.wonders_by_age: dict[int, list[WonderTemplate]] = {}
        self.built_wonders: dict[WonderTemplate, WonderBuiltInfo] = {}
        self.wonder_cost_by_age: dict[int, int] = BASE_WONDER_COST.copy()
        self.available_wonders: list[WonderTemplate] = []
        self.one_per_civs_built_by_civ_id: dict[str, dict[str, str]] = {}  # civ_id: {building_name: city_id}
        self.special_mode_by_player_num: dict[int, Optional[str]] = {}
        self.advancement_level = 0
        self.advancement_level_progress = 0.0
        self.game_over = False  # TODO delete
        self.announcements = []
        self.fresh_cities_for_decline: dict[str, City] = {}
        self.unhappiness_threshold: float = 0.0
        self.civ_ids_with_game_player_at_turn_start: list[str] = []
        self.no_db = False  # For headless games in scripts

        self.highest_existing_frame_num_by_civ_id: defaultdict[str, int] = defaultdict(int)

    def midturn_update(self):
        for city in self.cities_by_id.values():
            if city.is_territory_capital:
                city.midturn_update(self)
            # Puppet updates are triggered by their parent's midturn_update() function.
        for unit in self.units:
            unit.midturn_update(self)
        for civ in self.civs_by_id.values():
            civ.midturn_update(self)

    def add_announcement(self, content):
        self.announcements.append(f'[T {self.turn_num}] {content}')

    def fresh_cities_from_json_postprocess(self) -> None:
        for city in self.fresh_cities_for_decline.values():
            city._finish_loading_hex(self.hexes)

    def pick_random_hex(self) -> Hex:
        return random.choice(list(self.hexes.values()))

    def register_city(self, city):
        city.hex.city = city
        city.founded_turn = self.turn_num
        self.cities_by_id[city.id] = city

    def new_city(self, civ: Civ, hex: Hex, city_id: Optional[str] = None) -> City:
        city_name = get_city_name_for_civ(civ=civ, game_state=self)
        city = City(civ=civ, hex=hex, name=city_name, id=city_id, region=civ.template.region)
        assert hex.city is None, f"Creting city at {hex.coords} but it already has a city {hex.city.name}!"
        for h in hex.get_neighbors(self.hexes):
            assert h.city is None, f"Creating city at {hex.coords} but its neighbor already has a city {h.city.name} at {h.coords}!"
        city.populate_terrains_dict(self)
        return city

    def register_camp(self, camp: 'Camp'):
        camp.hex.camp = camp
        self.camps.append(camp)

    def unregister_camp(self, camp):
        camp.hex.camp = None
        self.camps.remove(camp)

    def _sample_wonders_for_age(self, age: int, target_number) -> list[WonderTemplate]:
        all = list(WONDERS.all_by_age(age))
        if len(all) <= target_number:
            result = all
        else:
            result = random.sample(all, target_number)
        return sorted(result, key=lambda w: w.name)

    def initialize_wonders(self):
        assert len(self.game_player_by_player_num) > 0, "Cannot initialize wonders without players"
        wonders_per_age: int = WONDER_COUNT_FOR_PLAYER_NUM[len(self.game_player_by_player_num)]
        logger.info(f"For {len(self.game_player_by_player_num)} players, sampling wonders to {wonders_per_age} per age.")
        self.wonders_by_age: dict[int, list[WonderTemplate]] = {age: self._sample_wonders_for_age(age, wonders_per_age) for age in range(0, 10)}
        self._refresh_available_wonders()
        logger.info(f"Wonders by age: {self.wonders_by_age}")

    def update_wonder_cost_by_age(self) -> None:
        for age in self.wonders_by_age.keys():
            self.wonder_cost_by_age[age] = self._wonder_cost(age)

    def _wonder_cost(self, age: int) -> int:
        base: int = BASE_WONDER_COST[age]
        num_built: int = len([w for w in self.built_wonders if w.advancement_level == age])
        total_num: int = len(self.wonders_by_age[age])
        # The first one costs base, the last one 2 * base
        cost = int(base * (1 + num_built / max(total_num - 1, 1)))
        return cost

    def found_city_for_civ(self, civ: Civ, hex: Hex, city_id: str | None) -> City:
        civ.city_power -= 100
        city = self.new_city(civ, hex, city_id)
        self.register_city(city)
        city.set_territory_parent_if_needed(game_state=self, adopt_focus=True)

        civ.gain_vps(2, "Founded Cities (2/city)")
    
        self.refresh_foundability_by_civ()
        return city

    def enter_decline_for_civ(self, civ: Civ, game_player: GamePlayer) -> None:
        self.add_announcement(f'The <civ id={civ.id}>{civ.moniker()}</civ> have entered decline!')                
        civ.game_player = None
        civ.in_decline = True
        game_player.civ_id = None

        for other_civ in self.civs_by_id.values():
            if other_civ.id != civ.id:
                other_civ.gain_vps(min(BASE_SURVIVAL_BONUS + SURVIVAL_BONUS_PER_AGE * (self.advancement_level), 24), SURVIVAL_SCORE_LABEL)

    def choose_techs_for_new_civ(self, city: City) -> set[TechTemplate]:
        logger.info("Calculating starting techs!")
        # Make this function deterministic across staging and rolling
        random.seed(deterministic_hash(f"{self.game_id} {self.turn_num} {city.name} {city.hex.coords}"))
        chosen_techs: set[TechTemplate] = set()
        chosen_techs_by_advancement = defaultdict(int)

        # Calculate mean tech amount at each level
        civs_to_compare_to: list[Civ] = [civ for civ in self.civs_by_id.values() if civ.id in self.civ_ids_with_game_player_at_turn_start and civ != city.civ]
        if len(civs_to_compare_to) == 0:
            civs_to_compare_to = [civ for civ in self.civs_by_id.values()]

        logger.info(f"  Comparing to civs: {civs_to_compare_to}")
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
            logger.info(f"Level {level}; excess {excess_techs}; target: {target_num}")
            if chosen_techs_by_advancement[level] > target_num:
                excess_techs = chosen_techs_by_advancement[level] - target_num
                continue
            else:
                num_needed = target_num - chosen_techs_by_advancement[level]
                available = [tech for tech in tech_counts_by_adv_level[level] if tech not in chosen_techs]
                available.sort(key=lambda tech: (tech_counts_by_adv_level[level][tech], random.random()), reverse=True)
                choose = available[:math.floor(num_needed)]
                logger.info(f"  chose: {choose}")
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
        game_player.all_civ_ids.append(civ.id)
        game_player.decline_this_turn = True
        civ.vitality *= game_player.vitality_multiplier
        self.make_new_civ_from_the_ashes(city)
        civ.get_great_person(self.advancement_level, city, self)
        logger.info(f"New civ {civ} great people choices: {civ.great_people_choices}")

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
            logger.info(f"Declining to existing city at {coords}")
            assert hex.city.civ_to_revolt_into is not None, f"Trying to revolt into a city {hex.city.name} with no city.civ_to_revolt_into"
            hex.city.change_owner(Civ(hex.city.civ_to_revolt_into, game_player=None), game_state=self)
            hex.city.civ.vandetta_civ_id = old_civ.id
        else:
            # This is a fake city, now it is becoming a real city.
            old_civ: Optional[Civ] = None
            logger.info(f"Declining to fresh city at {coords}")
            city = self.fresh_cities_for_decline[coords]
            self.register_city(city)
            city.seen_by_players = {p for p in self.game_player_by_player_num.keys()}
        assert hex.city is not None, "Failed to register city!"
        hex.city.capitalize(self)
        hex.city.civ_to_revolt_into = None
        hex.city.buildings = [b for b in hex.city.buildings if not b.destroy_on_owner_change]
        bldg_to_start_with = {
            0: UNITS.WARRIOR,
            1: UNITS.WARRIOR,
            2: UNITS.GARRISON,
            3: UNITS.GARRISON,
            4: UNITS.MILITIA,
            5: UNITS.MILITIA,
            6: UNITS.MILITIA,
            7: UNITS.RAMPARTS,
            8: UNITS.RAMPARTS,
            9: UNITS.RAMPARTS,
            10: UNITS.RAMPARTS,
        }[self.advancement_level]
        hex.city.unit_buildings = [UnitBuilding(bldg_to_start_with)]

        new_civ: Civ = hex.city.civ
        new_civ.vitality = hex.city.revolting_starting_vitality
        self.civs_by_id[new_civ.id] = new_civ
        from_civ_perspectives.append(new_civ)

        unit_count = 0
        hexes_to_steal_from = hex.get_neighbors(self.hexes, include_self=True) if is_game_player else [hex]
        for neighbor_hex in hexes_to_steal_from:
            for unit in neighbor_hex.units:
                if unit.civ == old_civ or unit.civ.template == CIVS.BARBARIAN:
                    unit.update_civ(new_civ)
                    stack_size: int = unit.get_stack_size()
                    unit_count += stack_size
        for neighbor_hex in hex.get_neighbors(self.hexes, include_self=True):
            if neighbor_hex.camp is not None:
                self.unregister_camp(neighbor_hex.camp)
        hex.city.revolt_unit_count = unit_count

        return hex.city

    def resolve_game_player_move(self, move_type: MoveType, move_data: dict, speculative: bool, game_player: GamePlayer) -> int | None:
        if move_type == MoveType.CHOOSE_STARTING_CITY:
            assert game_player is not None
            city_id = move_data['city_id']
            self.special_mode_by_player_num[game_player.player_num] = None

            for city in self.cities_by_id.values():
                if city.civ.game_player == game_player:
                    if city.id == city_id:
                        game_player.decline_this_turn = True
                        game_player.civ_id = city.civ.id
                        game_player.all_civ_ids.append(city.civ.id)
                        city.civ.vitality = (STARTING_CIV_VITALITY if not GOD_MODE else 10) * game_player.vitality_multiplier

                        city.capitalize(self)

                    else:
                        self.register_camp(Camp(self.barbarians, hex=city.hex))

                        city.hex.city = None
                        self.cities_by_id = {c_id: c for c_id, c in self.cities_by_id.items() if city.id != c.id}

                        del self.civs_by_id[city.civ.id]

            self.refresh_visibility_by_civ()

            for civ in self.civs_by_id.values():
                civ.fill_out_available_buildings(self)

            rdel(dream_key(self.game_id, game_player.player_num, self.turn_num))
            return None

        elif move_type == MoveType.CHOOSE_DECLINE_OPTION:
            logger.info(f'player {game_player.player_num} is choosing a decline option')
            if 'preempted' in move_data:
                game_player.failed_to_decline_this_turn = True
                return

            coords = move_data['coords']

            if STRICT_MODE:
                assert not game_player.decline_this_turn, f"Player {game_player.player_num} is trying to decline twice in one turn."

            # If speculative is False, then there should be no collisions
            # We could be less strict here and not even check, but that seems dangerous
            with rlock(f'decline-claimed-{self.game_id}-{self.turn_num}-lock'):
                redis_key = f"decline-claimed-{self.game_id}-{self.turn_num}-{coords}"
                already_claimed_by = rget(redis_key)
                logger.info(f"{already_claimed_by=}")
                proceed = False
                if not speculative:
                    # End turn roll; there should be no collisions here.
                    assert already_claimed_by is not None and int(already_claimed_by) == game_player.player_num, f"During end turn roll, trying to execute a decline that wasn't claimed during the turn. {self.game_id} {self.turn_num} {coords} {already_claimed_by} {game_player.player_num}"
                    proceed = True
                    decline_eviction_player = None
                elif speculative and already_claimed_by is None:
                    # Non collision
                    proceed = True
                    decline_eviction_player = None
                elif speculative and already_claimed_by is not None:
                    # Collision
                    proceed: bool = self.decline_priority(first_player_num=int(already_claimed_by), new_player_num=game_player.player_num)
                    if proceed:
                        decline_eviction_player = int(already_claimed_by)
                    else:
                        # The client figures out the action failed based on the fact that I'm still the same civ.
                        # That isn't super robust.
                        move_data['preempted'] = True
                        game_player.failed_to_decline_this_turn = True
                        decline_eviction_player = None

                else:
                    raise ValueError("There are no other logical possibilities.")
                logger.info(f"{proceed=}")
                if proceed:
                    rset(redis_key, game_player.player_num)
                    self.execute_decline(coords, game_player)
                return decline_eviction_player
        else:
            raise ValueError(f"Invalid move type: {move_type}")

    def resolve_move(self,
                     move_type: MoveType, 
                     move_data: dict, 
                     speculative: bool = False, 
                     game_player: GamePlayer | None = None, 
                     civ: Civ | None = None,
                     do_midturn_update: bool = True) -> int | None:
        """
        Can be submitted by GamePlayer (for things like choose starting city or decline)
        or by Civ (for normal moves submitted by declined civs)
        """
        logger.info(f"GameState.resolve_move {self.game_id} {self.turn_num} {game_player.player_num if game_player else 'None'}: {move_type} {move_data}")
        if move_type in (MoveType.CHOOSE_STARTING_CITY, MoveType.CHOOSE_DECLINE_OPTION):
            assert game_player is not None, f"GamePlayer is required for move type {move_type}"
            return self.resolve_game_player_move(move_type, move_data, speculative, game_player)

        if civ is None:
            assert game_player is not None, f"Must set GamePlayer or Civ for move type {move_type}"
            assert game_player.civ_id is not None, f"GamePlayer {game_player.player_num} has no civ_id"
            civ = self.civs_by_id[game_player.civ_id]

        if move_type == MoveType.CHOOSE_TECH:
            tech_name = move_data['tech_name']
            tech = TECHS.by_name(tech_name)
            civ.select_tech(tech)

        if move_type == MoveType.CHOOSE_BUILDING:
            building_name = move_data['building_name']
            city_id = move_data['city_id']
            city = self.cities_by_id[city_id]

            building = QueueEntry.find_queue_template_by_name(building_name)
            if city.validate_building_queueable(building):
                city.enqueue_build(building)
                for other_city in city.civ.get_my_cities(self):
                    if other_city != city:
                        other_city.buildings_queue = [b for b in other_city.buildings_queue if not b.template == building]

        if move_type == MoveType.CANCEL_BUILDING:
            building_name = move_data['building_name']
            city_id = move_data['city_id']
            city = self.cities_by_id[city_id]

            for i, entry in enumerate(city.buildings_queue):
                if entry.template.name == building_name:
                    # TODO could check it has the right delete/build type
                    city.buildings_queue.pop(i)
                    break

        if move_type == MoveType.SELECT_INFINITE_QUEUE:
            unit_name = move_data['unit_name']
            city_id = move_data['city_id']
            city = self.cities_by_id[city_id]

            unit = UNITS.by_name(unit_name)

            city.toggle_unit_build(unit)

        if move_type == MoveType.DEVELOP:
            city_id = move_data['city_id']
            city = self.cities_by_id[city_id]

            if move_data['type'] == 'rural':
                city.expand(self)
            elif move_data['type'] == 'urban':
                city.urbanize(self)
            elif move_data['type'] == 'unit':
                city.militarize(self)
            else:
                raise ValueError(f"Invalid type: {move_data['type']}")

        if move_type == MoveType.SET_CIV_PRIMARY_TARGET:
            target_coords = move_data['target_coords']
            civ.target1_coords = target_coords
            civ.target1 = self.hexes[target_coords]

        if move_type == MoveType.SET_CIV_SECONDARY_TARGET:
            target_coords = move_data['target_coords']
            civ.target2_coords = target_coords
            civ.target2 = self.hexes[target_coords]

        if move_type == MoveType.REMOVE_CIV_PRIMARY_TARGET:
            civ.target1_coords = None
            civ.target1 = None

        if move_type == MoveType.REMOVE_CIV_SECONDARY_TARGET:
            civ.target2_coords = None
            civ.target2 = None

        if move_type == MoveType.CHOOSE_FOCUS:
            city_id = move_data['city_id']
            city = self.cities_by_id[city_id]
            city.focus = move_data['focus']
            if move_data.get('with_puppets'):
                for puppet in city.get_puppets(self):
                    puppet.focus = move_data['focus']

        if move_type == MoveType.MAKE_TERRITORY:
            city_id: str = move_data['city_id']
            city: City = self.cities_by_id[city_id]
            previous_parent: City | None = city.get_territory_parent(self)
            city.make_territory_capital(self)

            instead_of_city_id: str = move_data['other_city_id']
            if instead_of_city_id is not None:
                instead_of_city: City = self.cities_by_id[instead_of_city_id]
                instead_of_city.set_territory_parent_if_needed(self, adopt_focus=False, force=True)
                # I think this force=True can conceivably crash if I somehow control no other territory capitals,
                # Which in theory can happen if people declined into all of my territory capitals on the same turn.
                instead_of_city.orphan_territory_children(self, make_new_territory=False)
                # Transfer the expansion costs.
                city.develops_this_civ = instead_of_city.develops_this_civ
                instead_of_city.develops_this_civ = {key: 0 for key in instead_of_city.develops_this_civ}

                # Take all the wood and metal over.
                new_parent = instead_of_city.get_territory_parent(self)
                assert new_parent is not None
                new_parent.wood += instead_of_city.wood
                instead_of_city.wood = 0
                for bldg in new_parent.unit_buildings:
                    new_parent.metal += bldg.metal
                    bldg.metal = 0
                new_parent.metal += instead_of_city.metal
                instead_of_city.metal = 0
            if previous_parent is not None and previous_parent.id != instead_of_city_id:
                previous_parent.orphan_territory_children(self, make_new_territory=False)


        if move_type == MoveType.TRADE_HUB:
            city_id = move_data['city_id']
            if civ.trade_hub_id == city_id:
                civ.trade_hub_id = None
            else:
                civ.trade_hub_id = city_id

        if move_type == MoveType.SELECT_GREAT_PERSON:
            civ.select_great_person(self, move_data['great_person_name'])

        if move_type == MoveType.FOUND_CITY:
            self.found_city_for_civ(civ, self.hexes[move_data['coords']], move_data['city_id'])

        # Processing to do regardless of move.
        if do_midturn_update:
            self.midturn_update()

    def update_from_player_moves(self, player_num: int, moves: list[dict], speculative: bool = False, 
                                 city_owner_by_city_id: Optional[dict] = None) -> tuple[dict, Optional[int]]:
        """
        Returns:
          - game_state_to_return: game_state to send to the client
          - decline_eviction_player: if not None, we need to evict this player number from the decline choice they've already taken.
        """
        decline_eviction_player: Optional[int] = None
        game_player = self.game_player_by_player_num[player_num]

        for move_index, move in enumerate(moves):
            # This has to be deterministic to allow speculative and non-speculative calls to agree
            seed_value = deterministic_hash(f"{self.game_id} {player_num} {self.turn_num}")
            random.seed(seed_value)
            if city_owner_by_city_id is not None \
                and 'city_id' in move \
                and move['city_id'] in city_owner_by_city_id \
                and city_owner_by_city_id[move['city_id']] != player_num:
                continue

            move_type = MoveType(move['move_type'])
            decline_eviction_player = self.resolve_move(move_type, move, speculative, game_player=game_player)
        
        assert game_player.civ_id is not None
        from_civ_perspectives = [self.civs_by_id[game_player.civ_id]]
        return (self.to_json(from_civ_perspectives=from_civ_perspectives), decline_eviction_player)

    def sync_advancement_level(self) -> None:
        # Population-weighted average civ advancement level.
        weighted_levels = [(c.population, c.civ.get_advancement_level(fractional=True)) for c in self.cities_by_id.values()]
        total_population = sum(level[0] for level in weighted_levels)
        weighted_average = sum(level[0] / total_population * level[1] for level in weighted_levels)
        self.advancement_level = math.floor(weighted_average)
        self.advancement_level_progress = weighted_average - self.advancement_level

    def all_map_objects(self) -> Generator[MapObject, Any, None]:
        yield from self.cities_by_id.values()
        yield from self.units
        yield from self.camps

    def refresh_visibility_by_civ(self, short_sighted: bool = False) -> None:
        for hex in self.hexes.values():
            hex.visibility_by_civ.clear()

        for obj in self.all_map_objects():
            obj.update_nearby_hexes_visibility(self, short_sighted=short_sighted)

    def refresh_foundability_by_civ(self) -> None:
        for hex in self.hexes.values():
            hex.is_foundable_by_civ.clear()

        for unit in self.units:
            unit.update_nearby_hexes_friendly_foundability()

        for obj in self.all_map_objects():
            obj.update_nearby_hexes_hostile_foundability(self.hexes)


    def load_and_update_from_player_moves(self, moves_by_player_num: dict[int, list]) -> None:
        # Defaults to being permissive; city_ids that exist will cause it to be the case that
        # only commands from that player's player num get respected
        city_owner_by_city_id: dict[str, int] = {}

        for player_num in self.game_player_by_player_num.keys():
            staged_moves = moves_by_player_num.get(player_num, [])

            for move in staged_moves:
                if move['move_type'] == 'choose_decline_option' and 'preempted' not in move:
                    if (city := self.hexes[move['coords']].city):
                        city_owner_by_city_id[city.id] = player_num

        for city in self.cities_by_id.values():
            if city.id in city_owner_by_city_id:
                # Don't revolt to rebels if we're already revolting to a player.
                continue
            if city.revolting_to_rebels_this_turn:
                city.revolt_to_rebels(self)
                self.midturn_update()
                city_owner_by_city_id[city.id] = -1

        for player_num in self.game_player_by_player_num.keys():
            staged_moves = moves_by_player_num.get(player_num, [])
            self.update_from_player_moves(player_num, staged_moves, city_owner_by_city_id=city_owner_by_city_id)

    def all_bot_moves(self):
        civs: list[Civ] = list(self.civs_by_id.values())

        for civ in civs:
            game_player: GamePlayer | None = civ.game_player
            if (game_player is None or game_player.is_bot) and not civ.template.name == 'Barbarians':
                # decline if they want to
                if game_player and not civ.in_decline and (decline_coords := civ.bot_decide_decline(self)):
                    civ.bot_predecline_moves(self)
                    self.execute_decline(decline_coords, game_player)
                    self.midturn_update()
                    new_civ_id = game_player.civ_id
                    assert new_civ_id is not None
                    assert new_civ_id != civ.id, f"Bot player {game_player.player_num} is trying to decline but somehow failed? {civ.id=} {new_civ_id=}"
                    self.civs_by_id[new_civ_id].bot_move(self)
                else:
                    civ.bot_move(self)

    def end_turn(self, sess) -> None:
        logger.info(f'GameState.end_turn(): ending turn {self.turn_num}')

        self.roll_turn(sess)

        logger.info("GameState.end_turn(): committing changes")
        sess.commit()

        logger.info("GameState.end_turn(): Creating StartOfNewTurn AnimationFrame")
        self.add_animation_frame(sess, {
            "type": "StartOfNewTurn",
        })
        sess.commit()

        logger.info("GameState.end_turn(): Creating decline view")
        self.create_decline_view(sess)   

        logger.info("GameState.end_turn() complete")

    def game_end_score(self):
        return GAME_END_SCORE + EXTRA_GAME_END_SCORE_PER_PLAYER * len(self.game_player_by_player_num)

    def roll_turn(self, sess) -> None:
        logger.info(f"GameState incrementing turn {self.turn_num} -> {self.turn_num + 1}")
        self.turn_num += 1

        self.barbarians.target1 = self.pick_random_hex()
        self.barbarians.target2 = self.pick_random_hex()
        self.barbarians.target1_coords = self.barbarians.target1.coords
        self.barbarians.target2_coords = self.barbarians.target2.coords

        for civ in self.civs_by_id.values():
            civ.fill_out_available_buildings(self)

        if not self.no_db:
            logger.info("precommit")
            sess.commit()

        logger.info("moving units 1")
        units_copy = self.units[:]
        random.shuffle(units_copy)
        for unit in units_copy:
            if not unit.dead:
                unit.move(sess, self)
                unit.attack(sess, self)

        if not self.no_db:
            logger.info("moving units 1: commit")
            sess.commit()

        logger.info("moving units 2")
        random.shuffle(units_copy)
        for unit in units_copy:
            if not unit.dead:
                unit.move(sess, self, sensitive=True)
                unit.attack(sess, self)

        if not self.no_db:
            logger.info("moving units 2: commit")
            sess.commit()

        logger.info("Merging units")
        # New units could have appeared in self.units due to splits
        # But that's ok, they've all acted by definition, so they don't need to be in this loop
        random.shuffle(units_copy)
        for unit in units_copy:
            if not unit.has_moved and unit.attacks_used == 0 and unit.friendly_neighboring_unit_count(self) >= 4 and not unit.currently_sieging():
                unit.merge_into_neighboring_unit(sess, self)

        logger.info("Acting cities & civs")
        cities_copy = list(self.cities_by_id.values())
        random.shuffle(cities_copy)

        camps_copy = self.camps[:]
        random.shuffle(camps_copy)

        for city in cities_copy:
            city.roll_turn_pre_harvest(self)
        for civ in self.civs_by_id.values():
            civ.roll_turn_pre_harvest()
        for city in cities_copy:
            city.roll_turn_post_harvest(sess, self)

        for camp in camps_copy:
            camp.roll_turn(sess, self)

        for civ in self.civs_by_id.values():
            civ.roll_turn_post_harvest(sess, self)

        logger.info("Final refresh")
        for unit in units_copy:
            unit.turn_end(self)

        for game_player in self.game_player_by_player_num.values():
            game_player.decline_this_turn = False
            game_player.failed_to_decline_this_turn = False

        self.sync_advancement_level()

        self.refresh_visibility_by_civ()
        self.refresh_foundability_by_civ()
        self._refresh_available_wonders()
        self.update_wonder_cost_by_age()

        for civ in self.civs_by_id.values():
            civ.fill_out_available_buildings(self)

        logger.info("Checking for game over")
        for game_player in self.game_player_by_player_num.values():
            if game_player.score >= self.game_end_score():
                self.game_over = True
                break

        self.handle_decline_options()
        for city in self.fresh_cities_for_decline.values():
            city.roll_turn_post_harvest(sess, self, fake=True)
        for city in self.cities_by_id.values():
            city.already_harvested_this_turn = False

        self.midturn_update()
        
        self.civ_ids_with_game_player_at_turn_start = [civ.id for civ in self.civs_by_id.values() if civ.game_player is not None]

    def handle_decline_options(self):
        self.populate_fresh_cities_for_decline()
        needed_revolt_choices: int = 5 - len(self.fresh_cities_for_decline)
        cities_to_revolt: list[tuple[float, str, City]] = sorted([(city.unhappiness, id, city) for id, city in self.cities_by_id.items() if city.unhappiness >= 1 and city.under_siege_by_civ is None], reverse=True)
        revolt_choices: list[tuple[float, str, City]] = cities_to_revolt[:needed_revolt_choices]
        if len(revolt_choices) > 0:
            self.unhappiness_threshold = revolt_choices[-1][0]
        else:
            self.unhappiness_threshold = 0
        logger.info(f"revolt choices: {[city.name for _, _, city in revolt_choices]}; threshold: {self.unhappiness_threshold}")
        revolt_ids = set(id for _, id, _ in revolt_choices)
        for _, _, city in revolt_choices:
            if city.civ_to_revolt_into is None:
                civ_template = self.sample_new_civs(1, city.region).pop(0)
                city.civ_to_revolt_into = civ_template
        for id, city in self.cities_by_id.items():
            if id not in revolt_ids:
                city.civ_to_revolt_into = None

        # Update seen_by_players to include anything visible in the fog via the decline view.
        for city in list(self.fresh_cities_for_decline.values()) + [city for city in self.cities_by_id.values() if city.civ_to_revolt_into is not None]:
            for neighbor in city.hex.get_hexes_within_range(self.hexes, 2):
                if neighbor.city is not None:
                    neighbor.city.seen_by_players = {p for p in self.game_player_by_player_num.keys()}

    def sample_new_civs(self, n, region: Region | None = None) -> list[CivTemplate]:
        advancement_level_to_use = max(self.advancement_level, 1)
        civs_already_in_game: list[CivTemplate] = [civ.template for civ in self.civs_by_id.values()] + \
            [city.civ.template for city in self.fresh_cities_for_decline.values()] + \
            [city.civ_to_revolt_into for city in self.cities_by_id.values() if city.civ_to_revolt_into is not None]
        if region is not None:
            target_regions: set[Region] = {region}
        else:
            target_regions = set(Region) - set(civ.region for civ in civs_already_in_game)

        decline_choice_big_civ_pool = find_civ_pool(n, advancement_level_to_use, target_regions, civs_already_in_game)
        result = random.sample(decline_choice_big_civ_pool, n)       
        logger.info(f"Sampling new civs ({n}). {advancement_level_to_use=}; \n Already present: {civs_already_in_game}\n Chose from: {decline_choice_big_civ_pool}\n Chose {result}")
        return result
    
    def retire_fresh_city_option(self, coords):
        logger.info(f"retiring option at {coords}")
        self.fresh_cities_for_decline.pop(coords)
        camp_level: int = max(0, self.advancement_level - 2)
        logger.info(f"Making camp at {coords} at level {camp_level}")
        self.register_camp(Camp(self.barbarians, advancement_level=camp_level, hex=self.hexes[coords]))

    def populate_fresh_cities_for_decline(self) -> None:
        self.fresh_cities_for_decline = {coords: city for coords, city in self.fresh_cities_for_decline.items()
                                             if is_valid_decline_location(self.hexes[coords], self.hexes, [self.hexes[other_coords] for other_coords in self.fresh_cities_for_decline if other_coords != coords])}
        new_locations_needed = max(2 - len(self.fresh_cities_for_decline), 0)
        if new_locations_needed == 0 and random.random() < 0.2 * len(self.game_player_by_player_num):  # Make one new camp per player per 5 turns.
            # randomly retire one of them
            coords: str = random.choice(list(self.fresh_cities_for_decline.keys()))
            self.retire_fresh_city_option(coords)
            new_locations_needed += 1
        logger.info(f"Generating {new_locations_needed} fresh cities for decline.")
        new_hexes = generate_decline_locations(self, new_locations_needed, [self.hexes[coord] for coord in self.fresh_cities_for_decline])

        decline_choice_civ_pool = self.sample_new_civs(new_locations_needed)
        for hex, civ_template in zip(new_hexes, decline_choice_civ_pool):
            assert hex.city is None, f"Attempting to put a fresh decline city on an existing city! {hex.city.name} @ {hex.coords}; {new_hexes}"
            new_civ = Civ(civ_template, game_player=None)

            city = self.new_city(new_civ, hex)

            # Give it some minimal stuff
            city.population = self.advancement_level + 1
            city.rural_slots = {0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 6}[self.advancement_level]

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
                logger.info(f"decline view for city {city.name}")
                self.process_decline_option(city.hex.coords, from_civ_perspectives)
                city.is_decline_view_option = True
        
        self.refresh_foundability_by_civ()
        self.refresh_visibility_by_civ(short_sighted=True)
        self.midturn_update()

        sess.add(AnimationFrame(
            game_id=self.game_id,
            turn_num=self.turn_num,
            frame_num=0,
            player_num=100,
            is_decline=True,
            game_state=self.to_json(from_civ_perspectives=from_civ_perspectives),
        ))

        sess.commit()

    def handle_wonder_built(self, city: City, wonder: WonderTemplate) -> None:
        civ = city.civ
        if wonder not in self.built_wonders:
            self.built_wonders[wonder] = WonderBuiltInfo(self.turn_num)
        self.built_wonders[wonder].infos.append((city.id, civ.id))
            
        
        if civ.has_ability('ExtraVpsPerWonder'):
            civ.gain_vps(civ.numbers_of_ability('ExtraVpsPerWonder')[0], civ.template.name)

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
        if self.no_db: return
        self.add_animation_frame_for_civ(sess, data, None, no_commit=True)

        for civ in self.civs_by_id.values():
            if hexes_must_be_visible is None or any(hex.visible_to_civ(civ) for hex in hexes_must_be_visible) and civ.game_player is not None:
                self.add_animation_frame_for_civ(sess, data, civ, no_commit=True)

        if not no_commit:
            sess.commit()

    def wonder_buildable(self, wonder) -> bool:
        if wonder.advancement_level > self.advancement_level:
            # Can't build it yet
            return False
        if wonder in self.built_wonders:
            return False
        return True

    def _refresh_available_wonders(self) -> None:
        # This only gets called after the game has fully rolled, so it wont' prevent the 2nd player building the wonder in the same turn
        # To make ties be generous.
        self.available_wonders = [wonder for wonders in self.wonders_by_age.values() for wonder in wonders if self.wonder_buildable(wonder)]

    def get_civ_by_name(self, civ_name: str) -> Civ:
        for civ in self.civs_by_id.values():
            if civ.template.name == civ_name:
                return civ
        raise Exception(f"Civ not found: {civ_name}, {self.civs_by_id}")
    
    def to_json(self, from_civ_perspectives: Optional[list[Civ]] = None) -> dict:
        if self.game_over:
            from_civ_perspectives = None

        return {
            "game_id": self.game_id,
            "hexes": {key: hex.to_json(from_civ_perspectives=from_civ_perspectives) for key, hex in self.hexes.items()},
            "civs_by_id": {civ_id: civ.to_json() for civ_id, civ in self.civs_by_id.items()},
            "cities_by_id": {city_id: city.to_json() for city_id, city in self.cities_by_id.items()},
            "game_player_by_player_num": {player_num: game_player.to_json() for player_num, game_player in self.game_player_by_player_num.items()},
            "turn_num": self.turn_num,
            "wonders_by_age": {age: [wonder.name for wonder in wonders] for age, wonders in self.wonders_by_age.items()},
            "built_wonders": {wonder.name: built_wonder.to_json() for wonder, built_wonder in self.built_wonders.items()},
            "available_wonders": [w.name for w in self.available_wonders],
            "one_per_civs_built_by_civ_id": {civ_id: {building_name: city_id for building_name, city_id in v.items()} for civ_id, v in self.one_per_civs_built_by_civ_id.items()},
            "special_mode_by_player_num": self.special_mode_by_player_num.copy(),
            "barbarians": self.barbarians.to_json(),
            "advancement_level": self.advancement_level,
            "advancement_level_progress": self.advancement_level_progress,
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
        game_state.advancement_level_progress = json["advancement_level_progress"]

        game_state.turn_num = json["turn_num"]
        game_state.wonders_by_age = {int(age): [WONDERS.by_name(wonder_name) for wonder_name in wonder_names] for age, wonder_names in json["wonders_by_age"].items()}
        game_state.built_wonders = {WONDERS.by_name(wonder_name): WonderBuiltInfo.from_json(wonder_json) for wonder_name, wonder_json in json["built_wonders"].items()}
        game_state.wonder_cost_by_age = {int(age): cost for age, cost in json["wonder_cost_by_age"].items()}
        game_state.available_wonders = [WONDERS.by_name(wonder_name) for wonder_name in json["available_wonders"]]
        game_state.one_per_civs_built_by_civ_id = {civ_id: {building_name: city_id for building_name, city_id in v.items()} for civ_id, v in json["one_per_civs_built_by_civ_id"].items()}
        game_state.special_mode_by_player_num = {int(k): v for k, v in json["special_mode_by_player_num"].items()}
        game_state.fresh_cities_for_decline = {coords: City.from_json(city_json) for coords, city_json in json["fresh_cities_for_decline"].items()}
        game_state.game_over = json["game_over"]
        game_state.announcements = json["announcements"][:]
        game_state.unhappiness_threshold = float(json["unhappiness_threshold"])

        for civ in game_state.civs_by_id.values():
            civ.from_json_postprocess(game_state)
        for obj in game_state.all_map_objects():
            obj.from_json_postprocess(game_state)
        game_state.fresh_cities_from_json_postprocess()
        game_state.midturn_update()
        return game_state
