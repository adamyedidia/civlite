import itertools
import numpy as np
import random
from typing import TYPE_CHECKING, Any, Generator, Literal, Optional, Dict
from collections import defaultdict
from TechStatus import TechStatus
from assign_starting_locations import assign_starting_locations
from detailed_number import DetailedNumber
from effects_list import PointsEffect
from move_type import MoveType
from tenet_template import TenetTemplate
from tenet_template_list import TENETS, tenets_by_level
from terrain_templates_list import TERRAINS
from unit import Unit
from settings import AGE_THRESHOLDS, GOD_MODE
from wonder_templates_list import WONDERS
from great_person import GreatGeneral, GreatPerson, great_people_by_age, great_people_by_name
from civ_template import CivTemplate
from civ_templates_list import player_civs, CIVS
from game_player import GamePlayer
from settings import AI, NUM_STARTING_LOCATION_OPTIONS, STRICT_MODE, VITALITY_DECAY_RATE, BASE_CITY_POWER_INCOME, TECH_VP_REWARD, MAX_PLAYERS
from tech_template import TechTemplate
from building_template import BuildingTemplate, BuildingType
from unit_template import UnitTag, UnitTemplate
from unit_templates_list import UNITS
from utils import generate_unique_id
from building_templates_list import BUILDINGS
from tech_templates_list import TECHS
import score_strings

import random
from logging_setup import logger

from yields import Yields

if TYPE_CHECKING:
    from game_state import GameState
    from hex import Hex
    from city import City
    from ability import Ability
    from building import Building


class Civ:
    def __init__(self, civ_template: CivTemplate, game_player: Optional[GamePlayer]):
        self.id = generate_unique_id("CIV")
        self.game_player = game_player
        self.template = civ_template
        self.science = 0.0
        if GOD_MODE:
            self.techs_status: Dict[TechTemplate, TechStatus] = {tech: TechStatus.RESEARCHED for tech in TECHS.all()}
        else:
            self.techs_status: Dict[TechTemplate, TechStatus] = {tech: TechStatus.UNAVAILABLE for tech in TECHS.all()}
        self.vitality = 1.0
        self.city_power = 0.0
        self.available_city_buildings: list[BuildingTemplate] = []
        self.available_unit_buildings: list[UnitTemplate] = []
        self.buildings_in_all_queues: list[str] = []
        self.targets: list['Hex'] = []
        self.target_coords: list[str] = []
        self.projected_science_income: DetailedNumber = DetailedNumber()
        self.projected_city_power_income: DetailedNumber = DetailedNumber()
        self.vitality_decay_rate = DetailedNumber()
        self.in_decline = False
        self.trade_hub_id: Optional[str] = None
        self.trade_hub_city_power_consumption: float = 0.0
        self.great_people_choices: list[GreatPerson] = []
        self._great_people_choices_city_id: Optional[str] = None
        self._great_people_choices_queue: list[tuple[int, str]] = []  # age, city_id
        self.max_territories: int = 3
        self.vandetta_civ_id: Optional[str] = None
        self.unique_units_built: int = 0
        self._game_player_num: Optional[int] = self.game_player.player_num if self.game_player else None
        self.vps_per_tech_level: list[DetailedNumber] = [DetailedNumber() for _ in range(10)]

        self.score_dict: dict[str, float] = {}

    def __eq__(self, other: 'Civ') -> bool:
        # TODO(dfarhi) clean up all remaining instances of (civ1.id == civ2.id)
        return other is not None and self.id == other.id

    def get_target_from_hex(self, hex: 'Hex') -> 'Hex':
        """
        Returns the target closest to the given hex. If there are multiple targets at the same distance, returns one at random.
        """
        targets_copy = self.targets[:]
        random.shuffle(targets_copy)
        return min(targets_copy, key=lambda target: hex.distance_to(target))

    def moniker(self) -> str:
        game_player_parenthetical = f' ({self.game_player.username})' if self.game_player else ''
        return f"{self.template.name}{game_player_parenthetical}"

    def has_ability(self, ability_name: str) -> bool:
        return any([ability.name == ability_name for ability in self.template.abilities])

    def numbers_of_ability(self, ability_name: str) -> list:
        return [ability.numbers for ability in self.template.abilities if ability.name == ability_name][0]

    @property
    def score(self) -> float:
        return sum(self.score_dict.values())

    def gain_vps(self, vps: float, type: str):
        if self.game_player is None:
            return
        if type not in self.score_dict:
            self.score_dict[type] = 0
        self.score_dict[type] += vps
        if type not in self.game_player.score_dict:
            self.game_player.score_dict[type] = 0
        self.game_player.score_dict[type] += vps

    def passive_building_abilities_of_name(self, ability_name: str, game_state: 'GameState') -> Generator[tuple['Ability', 'Building'], Any, None]:
        for city in self.get_my_cities(game_state):
            for ability, building in city.passive_building_abilities_of_name(ability_name):
                yield ability, building

    def midturn_update(self, game_state):
        self.adjust_projected_yields(game_state)
        self.refresh_queues_cache(game_state)
        self._update_vps_per_tech_level(game_state)

    def adjust_projected_yields(self, game_state: 'GameState') -> None:
        self.projected_science_income = DetailedNumber()
        self.projected_city_power_income = DetailedNumber({"Base": BASE_CITY_POWER_INCOME})

        for city in game_state.cities_by_id.values():
            if city.civ.id == self.id:
                self.projected_science_income.add(city.name, city.projected_income.science)
                self.projected_city_power_income.add(city.name, city.projected_income.city_power)

        if self.trade_hub_id is not None and self.trade_hub_id in game_state.cities_by_id:
            # The trade hub has set civ.trade_hub_city_power_consumption in its own update.
            trade_hub = game_state.cities_by_id[self.trade_hub_id]
            self.projected_city_power_income.add(f"Trade Hub ({trade_hub.name})", -self.trade_hub_city_power_consumption)
        else:
            # There is no trade hub, make sure to clear it.
            self.trade_hub_city_power_consumption = 0.0

        for player in game_state.game_player_by_player_num.values():
            if player.has_tenet(TENETS.RISE_OF_EQUALITY) and player.get_current_civ(game_state).get_advancement_level() > self.get_advancement_level():
                self.projected_city_power_income.add(f"{TENETS.RISE_OF_EQUALITY.name} ({player.username})", -10)
            if self.has_tenet(TENETS.RISE_OF_EQUALITY) and player.get_current_civ(game_state).get_advancement_level() < self.get_advancement_level():
                self.projected_city_power_income.add(TENETS.RISE_OF_EQUALITY.name, 10)

    def has_tech(self, tech: TechTemplate) -> bool:
        return self.techs_status[tech] == TechStatus.RESEARCHED

    def has_tenet(self, tenet: TenetTemplate, check_complete_quest: bool = False) -> bool:
        return self.game_player is not None and self.game_player.has_tenet(tenet, check_complete_quest)
    
    def tenet_at_level(self, level: int) -> TenetTemplate | None:
        if self.game_player is None:
            return None
        return self.game_player.tenet_at_level(level)

    @property
    def researching_tech(self) -> TechTemplate | None:
        all_researching_techs = [tech for tech, status in self.techs_status.items() if status == TechStatus.RESEARCHING]
        assert len(all_researching_techs) <= 1
        return all_researching_techs[0] if all_researching_techs else None

    @property
    def researched_techs(self) -> list[TechTemplate]:
        return [tech for tech, status in self.techs_status.items() if status == TechStatus.RESEARCHED]

    def select_tech(self, tech: TechTemplate | None):
        if STRICT_MODE:
            assert tech is None or self.techs_status[tech] in (TechStatus.AVAILABLE, TechStatus.RESEARCHING), f"Civ {self} tried to research {tech.name} which is in status {self.techs_status[tech]}; all statuses were: {self.techs_status}"
        if self.researching_tech:
            self.techs_status[self.researching_tech] = TechStatus.AVAILABLE
        if tech is not None:
            self.techs_status[tech] = TechStatus.RESEARCHING 

    def initialize_techs(self, start_techs: list[TechTemplate]):
        for tech in start_techs:
            self.techs_status[tech] = TechStatus.RESEARCHED
        self.get_new_tech_choices()

    @property
    def unique_unit(self) -> UnitTemplate | None:
        if self.has_ability('IncreasedStrengthForUnit'):
            return UNITS.by_name(self.numbers_of_ability('IncreasedStrengthForUnit')[0])
        if self.has_ability('IncreasedStrengthForNthUnit') and self.unique_units_built < self.numbers_of_ability('IncreasedStrengthForNthUnit')[0]:
            return UNITS.by_name(self.numbers_of_ability('IncreasedStrengthForNthUnit')[1])
        return None

    def get_new_tech_choices(self):
        logger.info(f"getting new techs for {self.moniker()}.")
        max_advancement_level = max(1, self.get_advancement_level())

        characteristic_tech_offered = False


        if self.unique_unit is not None:
            if (characteristic_tech := self.unique_unit.prereq):
                if characteristic_tech.advancement_level <= max_advancement_level and self.techs_status[characteristic_tech] == TechStatus.UNAVAILABLE:
                    characteristic_tech_offered = True
                    self.techs_status[characteristic_tech] = TechStatus.AVAILABLE

        num_techs_to_offer = 2 if characteristic_tech_offered else 3
        techs_to_sample_from = [tech for tech in TECHS.all() 
                                if (tech.advancement_level <= max_advancement_level 
                                    and self.techs_status[tech] == TechStatus.UNAVAILABLE)]

        if len(techs_to_sample_from) < num_techs_to_offer:
            techs_to_offer = techs_to_sample_from

        else:
            techs_to_offer = random.sample(techs_to_sample_from, num_techs_to_offer)

        for choice in techs_to_offer:
            self.techs_status[choice] = TechStatus.AVAILABLE
        if len(techs_to_offer) == 0 and self.game_player is not None:
            # We've teched to too many things, time for a Renaissance
            self.techs_status[TECHS.RENAISSANCE] = TechStatus.AVAILABLE

    def next_age_progress(self) -> dict[str, int]:
        total_tech_levels = sum([tech.advancement_level for tech in self.researched_techs])
        age = max((age for age, threshold in AGE_THRESHOLDS.items() if threshold <= total_tech_levels), default=0)
        return {
            "age": age,
            "partial": total_tech_levels - AGE_THRESHOLDS[age],
            "needed": AGE_THRESHOLDS[age + 1] - AGE_THRESHOLDS[age],
        }

    def get_advancement_level(self, fractional=False) -> float:
        progress = self.next_age_progress()
        age = progress["age"]
        progress_levels = progress["partial"]
        total_levels_needed = progress["needed"]
        if not fractional:
            return age
        else:
            missing_levels = total_levels_needed - progress_levels
            available_techs = [t for t in self._available_techs() if t is not TECHS.RENAISSANCE]
            average_available_tech_cost: float = sum([tech.cost for tech in available_techs]) / len(available_techs) if len(available_techs) > 0 else 1
            average_available_tech_level: float = sum([min(tech.advancement_level, missing_levels) for tech in available_techs]) / len(available_techs) if len(available_techs) > 0 else 1
            partial_tech_progress: float = self.science / average_available_tech_cost * average_available_tech_level
            
            # Need to clip to (0, 90% of missing levels), since you can have negative science or tons of science.
            clipped_partial_tech_progress: float = np.clip(partial_tech_progress, 0, missing_levels * 0.9)

            # Need max(0, x) since you can have negative science.
            partial_age_progress = max(0, (progress_levels + clipped_partial_tech_progress) / total_levels_needed)
            if STRICT_MODE:
                assert 0 <= partial_age_progress <= 1

            return age + partial_age_progress

    def get_my_cities(self, game_state: 'GameState') -> list['City']:
        return [city for city in game_state.cities_by_id.values() if city.civ == self]

    def update_max_territories(self, game_state: 'GameState'):
        base: int = 3
        bonuses: int = len([ability for ability, _ in self.passive_building_abilities_of_name('ExtraTerritory', game_state)])
        if self.has_tenet(TENETS.EL_DORADO, check_complete_quest=True):
            bonuses -= 1
        self.max_territories = base + bonuses

    def _available_techs(self) -> list[TechTemplate]:
        return sorted([tech for tech, status in self.techs_status.items() if status in (TechStatus.AVAILABLE, TechStatus.RESEARCHING)], 
                      key=lambda t:(t.advancement_level, t.cost, t.name))

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "game_player_num": self.game_player.player_num if self.game_player else None,
            "name": self.template.name,
            "science": self.science,
            "techs_status": {tech.name: status.value for tech, status in self.techs_status.items()},
            "num_researched_techs": len(self.researched_techs),
            "researching_tech_name": self.researching_tech.name if self.researching_tech is not None else None,
            "current_tech_choices": [tech.name for tech in self._available_techs()],
            "vitality": self.vitality,
            "city_power": self.city_power,
            "available_buildings": [b.name for b in self.available_city_buildings],
            "available_unit_buildings": [u.name for u in self.available_unit_buildings],
            "buildings_in_all_queues": self.buildings_in_all_queues,
            "targets": [target.coords for target in self.targets],
            "projected_science_income": self.projected_science_income.to_json(),
            "projected_city_power_income": self.projected_city_power_income.to_json(),
            "in_decline": self.in_decline,
            "advancement_level": self.get_advancement_level(),
            "next_age_progress": self.next_age_progress(),
            "trade_hub_id": self.trade_hub_id,
            "trade_hub_city_power_consumption": self.trade_hub_city_power_consumption,
            "great_people_choices": [great_person.to_json() for great_person in self.great_people_choices],
            "great_people_choices_queue": [(age, city_id) for age, city_id in self._great_people_choices_queue],
            "great_people_choices_city_id": self._great_people_choices_city_id,
            "max_territories": self.max_territories,
            "vandetta_civ_id": self.vandetta_civ_id,
            "score_dict": self.score_dict,
            "unique_units_built": self.unique_units_built,
            "has_tenet_choice": self.game_player is not None and self.game_player.active_tenet_choice_level is not None,
            "vitality_decay_rate": self.vitality_decay_rate.to_json(),
            "vps_per_tech_level": [vps.to_json() for vps in self.vps_per_tech_level],
        }

    def fill_out_available_buildings(self, game_state: 'GameState') -> None:
        self.available_city_buildings = [building for building in BUILDINGS.all() if (
            (building.prereq is None or self.has_tech(building.prereq))
            and (not building.name in game_state.one_per_civs_built_by_civ_id.get(self.id, []))
        )]
        self.available_unit_buildings: list[UnitTemplate] = [
            unit for unit in UNITS.all() 
            if unit.buildable and (unit.prereq is None or self.has_tech(unit.prereq))
            and (not unit.name in game_state.one_per_civs_built_by_civ_id.get(self.id, []))
            and unit != UNITS.WARRIOR
            ]
        
    def refresh_queues_cache(self, game_state: 'GameState'):
        self.buildings_in_all_queues = [entry.template.name for city in self.get_my_cities(game_state) for entry in city.buildings_queue]

    def bot_predecline_moves(self, game_state: 'GameState') -> None:
        all_cities = self.get_my_cities(game_state)
        all_develops: list[tuple[BuildingType, City]] = [(type, city) for city in all_cities for type in BuildingType if city.can_develop(type)]
        while all_develops:
            type, city = min(all_develops, key=lambda x: (x[1].develop_cost(x[0]), random.random()))
            city.bot_single_move(game_state, MoveType.DEVELOP, {'type': type.value})
            all_develops = [(type, city) for city in all_cities for type in BuildingType if city.can_develop(type)]
        self.bot_found_cities(game_state)

    def bot_decide_decline(self, game_state: 'GameState') -> str | None:
        """
        Returns the coords of the location to decline to, or None if I shouldn't decline.
        """
        # Don't decline if I'm sieging a city
        if any([city.under_siege_by_civ == self for city in game_state.cities_by_id.values()]):
            logger.info(f"{self.moniker()} deciding not to decline because I'm seiging a city.")
            return None

        # Don't decline if I'm sieging a camp
        if any([camp.under_siege_by_civ == self for camp in game_state.camps]):
            logger.info(f"{self.moniker()} deciding not to decline because I'm seiging a camp.")
            return None

        # Don't decline if I have above average army size.
        all_army_sizes: dict[str, float] = defaultdict(float)
        for unit in game_state.units:
            all_army_sizes[unit.civ.id] += unit.template.metal_cost * unit.get_stack_size()
        active_army_sizes: dict[str, float] = {
            game_player.civ_id: all_army_sizes[game_player.civ_id] 
            for game_player in game_state.game_player_by_player_num.values() 
            if game_player.civ_id is not None}
        my_rank: int = sum(active_army_sizes[self.id] <= other for other in active_army_sizes.values())
        total_players: int = len(game_state.game_player_by_player_num)
        if my_rank <= total_players / 2:
            logger.info(f"{self.moniker()} deciding not to decline because I'm rank {my_rank} of {total_players}. {active_army_sizes=}")
            return None
        
        # Don't decline if it would let someone else win
        assert self.game_player is not None
        other_players = [player for player in game_state.game_player_by_player_num.values() if player.player_num != self.game_player.player_num]
        max_player_score = max(other_players, key=lambda player: player.score).score
        if game_state.game_end_score() - max_player_score < 25:
                logger.info(f"{self.moniker()} deciding not to decline because opponent would win.")
                return None

        my_cities: list[City] = self.get_my_cities(game_state)
        my_total_yields: float = sum(
            [city.projected_income['food'] +city.projected_income['wood'] + city.projected_income['metal'] +city.projected_income['science'] \
             + (city.empty_slots(BuildingType.RURAL) * AI.RURAL_SLOT_VALUE + AI.URBAN_SLOT_VALUE(city.population) * city.empty_slots(BuildingType.URBAN)) * self.vitality
             for city in my_cities])
        
        option_total_yields: dict[str, float] = {}
        options: list[tuple[str, City]] = [(c.hex.coords, c) for c in game_state.cities_by_id.values() if c.civ_to_revolt_into is not None and c.civ != self] + list(game_state.fresh_cities_for_decline.items())
        for coords, city in options:
            current_total_yields = sum([hex.terrain.yields for hex in city.hex.get_neighbors(game_state.hexes, include_self=True)], city.projected_income_city_center)
            option_total_yields[coords] = current_total_yields.total()
            option_total_yields[coords] += city.population  # focus
            option_total_yields[coords] += AI.RURAL_SLOT_VALUE * city.rural_slots + AI.URBAN_SLOT_VALUE(city.population) * city.urban_slots
            option_total_yields[coords] *= city.revolting_starting_vitality * self.game_player.vitality_multiplier

        if len(option_total_yields) == 0:
            logger.info(f"{self.moniker()} deciding not to decline because there are no options.")
            return None
        best_option_yields, best_option = max((yields, coords) for coords, yields in option_total_yields.items())
        logger.info(f"{self.moniker()} deciding whether to revolt. My yields are: {my_total_yields}; options have: {option_total_yields}")
        if best_option_yields <= my_total_yields * AI.DECLINE_YIELD_RATIO_THRESHOLD:
            logger.info(f"{self.moniker()} deciding not to decline because I have {my_total_yields} and the best option has {best_option_yields}")
            return None

        logger.info(f"{self.moniker()} deciding to decline at {best_option} because I have {my_total_yields} and the best option has {best_option_yields}")     
        return best_option

    def bot_score_tech(self, game_state: 'GameState', tech: TechTemplate) -> list[float]:
        score = []
        # Prefer unique tech
        score.append(self.unique_unit is not None and tech == self.unique_unit.prereq)
        # Prefer progress towards Fountain
        if self.game_player is not None and self.game_player.has_tenet(TENETS.FOUNTAIN_OF_YOUTH) \
            and not self.game_player.tenets[TENETS.FOUNTAIN_OF_YOUTH]["complete"]:
            score.append(tech.name in self.game_player.tenets[TENETS.FOUNTAIN_OF_YOUTH]["unclaimed_techs"])
        # Ignore techs that unlock units that are obsolete.
        obsolete = len(tech.unlocks_buildings) == 0 and tech.advancement_level < self.get_advancement_level() - 1
        score.append(not obsolete)
        # If we're stuck with an obsolete tech, prefer the cheapest to move on quickly
        if obsolete:
            score.append(-tech.cost)
        else:
            score.append(0)
        # break ties
        score.append(random.random())
        return score

    def bot_move(self, game_state: 'GameState') -> None:
        while len(self.great_people_choices) > 0:
            choice: GreatPerson = max(self.great_people_choices, key=lambda g: (isinstance(g, GreatGeneral), random.random()))
            game_state.resolve_move(MoveType.SELECT_GREAT_PERSON, {'great_person_name': choice.name}, civ=self)

        if self.game_player is not None and self.game_player.active_tenet_choice_level is not None:
            choices: list[TenetTemplate] = tenets_by_level[self.game_player.active_tenet_choice_level]
            choices = [t for t in choices if game_state.tenets_claimed_by_player_nums[t] == []]
            if choices:
                if self.game_player.active_tenet_choice_level in (1, 2, 3, 4, 7):
                    chosen_tenet = random.choice(choices)
                elif self.game_player.active_tenet_choice_level == 5:
                    my_units = [u for u in game_state.units if u.civ == self]
                    scores = {tenet: 0 for tenet in choices}
                    for unit in my_units:
                        for tenet in scores.keys():
                            if tenet.a5_unit_types is None: continue
                            if any(unit.template.has_tag(tag) for tag in tenet.a5_unit_types):
                                scores[tenet] += unit.get_stack_size() * unit.template.metal_cost
                    chosen_tenet = max(scores, key=lambda x: scores[x])
                elif self.game_player.active_tenet_choice_level == 6:
                    assert self.game_player.a6_tenet_info is not None
                    a6_tenet_info = self.game_player.a6_tenet_info
                    chosen_tenet = max(choices, key=lambda t: a6_tenet_info[t.name]["score"])
                else:
                    raise ValueError(f"Bot choosing tenet for unknown level: {self.game_player.active_tenet_choice_level}")
                target_city = self.game_player.get_tenet_target_city(game_state)
                points_from_tenet = lambda t: (
                    self.game_player.a6_tenet_info[t.name]['score'] if self.game_player is not None and self.game_player.a6_tenet_info is not None and t.name in self.game_player.a6_tenet_info else
                    t.instant_effect.calculate_points(target_city, game_state) if target_city is not None and isinstance(t.instant_effect, PointsEffect) else
                    0
                )

                chosen_tenet = max(choices, key=lambda t: (points_from_tenet(t), random.random()))
                game_state.resolve_move(MoveType.CHOOSE_TENET, {'tenet_name': chosen_tenet.name}, civ=self, game_player=self.game_player)

        my_cities = self.get_my_cities(game_state)
        my_territory_capitals = [city for city in my_cities if city.is_territory_capital]
        my_puppets = [city for city in my_cities if not city.is_territory_capital]
        if len(my_puppets) > 0:
            largest_puppet = max(my_puppets, key=lambda c: c.population)
            smallest_territory_capital = min(my_territory_capitals, key=lambda c: c.population)
            if len(my_territory_capitals) < self.max_territories:
                game_state.resolve_move(MoveType.MAKE_TERRITORY, {'city_id': largest_puppet.id, 'other_city_id': None}, civ=self)
            elif largest_puppet.population > smallest_territory_capital.population:
                game_state.resolve_move(MoveType.MAKE_TERRITORY, {'city_id': largest_puppet.id, 'other_city_id': smallest_territory_capital.id}, civ=self)
        # Choose trade hub:
        if self.tenet_at_level(7) is None:
            unhappy_cities = [city for city in self.get_my_cities(game_state) if city.unhappiness + city.projected_income["unhappiness"] > 0]
            def trade_hub_priority(city: 'City'):
                income = sum(city.projected_income[x] for x in ['wood', 'metal', 'science'])
                on_leaderboard = city.civ_to_revolt_into is not None
                unhappiness = city.unhappiness + city.projected_income["unhappiness"]
                close_to_leaderboard = unhappiness >= game_state.unhappiness_threshold
                return on_leaderboard, close_to_leaderboard, income
            if len(unhappy_cities) > 0:
                target = max(unhappy_cities, key=trade_hub_priority)
            else:
                target = None
        else:
            target = self.capital_city(game_state)
            if target is None:
                my_cities = [c for c in self.get_my_cities(game_state) if c.is_territory_capital]
                if my_cities:
                    target = max(my_cities, key=lambda c: c.population)
            logger.info(f"  {self.moniker()} choosing trade hub {target} based on {self.tenet_at_level(7)}")
        if target is not None:
            game_state.resolve_move(MoveType.TRADE_HUB, {'city_id': target.id}, civ=self)

        if WONDERS.UNITED_NATIONS in game_state.built_wonders and self.game_player is None:
            un_owner_ids: list[str] = [civ_id for _, civ_id in game_state.built_wonders[WONDERS.UNITED_NATIONS].infos]
            if len(un_owner_ids) > 1:
                # If lots fo people have UN, follow a random one for first flag and a random one for second flag
                random.shuffle(un_owner_ids)
                un_owner_ids = un_owner_ids[:2]
            else:
                # If only one person has UN, follow them for first and second flag
                un_owner_ids = [un_owner_ids[0], un_owner_ids[0]]
            un_owner_civs: list[Civ] = [game_state.civs_by_id[civ_id] for civ_id in un_owner_ids]
            target_coords = un_owner_civs[0].target_coords
            game_state.resolve_move(MoveType.SET_ALL_TARGETS, {'target_coords': target_coords}, civ=self, do_midturn_update=False)
        elif random.random() < AI.CHANCE_MOVE_FLAG or not self.target_coords:
            enemy_cities: list[City] = [city for city in game_state.cities_by_id.values() if city.civ.id != self.id]
            vandetta_cities: list[City] = [city for city in enemy_cities if city.civ.id == self.vandetta_civ_id]
            if len(vandetta_cities) > 0:
                possible_target_hexes: list[Hex] = [city.hex for city in vandetta_cities]
            else:
                possible_target_hexes: list[Hex] = [*[city.hex for city in enemy_cities], *[camp.hex for camp in game_state.camps]]

            random.shuffle(possible_target_hexes)

            if self.game_player \
                and self.game_player.has_tenet(TENETS.HOLY_GRAIL) \
                and not self.game_player.tenets[TENETS.HOLY_GRAIL]["complete"] \
                and self.game_player.tenets[TENETS.HOLY_GRAIL]["holy_city_id"] in game_state.cities_by_id \
                and game_state.cities_by_id[self.game_player.tenets[TENETS.HOLY_GRAIL]["holy_city_id"]].civ != self:
                grail_hex = game_state.cities_by_id[self.game_player.tenets[TENETS.HOLY_GRAIL]["holy_city_id"]].hex
                if grail_hex in possible_target_hexes:
                    possible_target_hexes.remove(grail_hex)
                possible_target_hexes.insert(0, grail_hex)

            possible_target_hex_coords: list[str] = [h.coords for h in possible_target_hexes]

            if self.game_player \
                and self.game_player.has_tenet(TENETS.EL_DORADO) \
                and not self.game_player.tenets[TENETS.EL_DORADO]["complete"]:
                possible_target_hex_coords = self.game_player.tenets[TENETS.EL_DORADO]["hexes"]
            if len(possible_target_hex_coords) > 0:
                game_state.resolve_move(MoveType.SET_ALL_TARGETS, {'target_coords': possible_target_hex_coords}, civ=self, do_midturn_update=False)

        if self.researching_tech is None:
            available_techs = self._available_techs()

            if len(available_techs) > 0:
                chosen_tech = max(available_techs, key=lambda t: self.bot_score_tech(game_state, t))
                game_state.resolve_move(MoveType.CHOOSE_TECH, {'tech_name': chosen_tech.name}, civ=self, do_midturn_update=False)
                logger.info(f"  {self.moniker()} chose tech {chosen_tech} from {available_techs}")
                if STRICT_MODE:
                    assert self.techs_status[chosen_tech] == TechStatus.RESEARCHING and self.researching_tech == chosen_tech
            else:
                logger.info(f"{self.moniker()} has no available techs")

        self.bot_found_cities(game_state)

        my_production_cities = [city for city in self.get_my_cities(game_state) if city.is_territory_capital]

        for city in sorted(my_production_cities, key=lambda c: c.population, reverse=True):
            if city.hex.city is not None:
                # Conceivably the city can have been destroyed by our own moves by previous cities.
                # As of this writing this can happen with the United States unique ability.
                city.bot_move(game_state)

    def bot_found_cities(self, game_state: 'GameState') -> None:
        while not self.in_decline and self.city_power >= 100 and not self.template.name == 'Barbarians':
            choices = [hex for hex in game_state.hexes.values() if hex.is_foundable_by_civ.get(self.id)]
            if len(choices) == 0:
                break
            hex = max(choices, key=lambda h: (sum([n.yields for n in h.get_neighbors(game_state.hexes, include_self=True)], start=Yields()).total(), random.random()))
            game_state.resolve_move(MoveType.FOUND_CITY, {'coords': hex.coords, 'city_id': generate_unique_id("CITY")}, civ=self)

    def gain_tech(self, game_state: 'GameState', tech: TechTemplate) -> None:
        if self.game_player and self.game_player.has_tenet(TENETS.FOUNTAIN_OF_YOUTH) and tech.name in self.game_player.tenets[TENETS.FOUNTAIN_OF_YOUTH]["unclaimed_techs"]:
            self.game_player.increment_tenet_progress(TENETS.FOUNTAIN_OF_YOUTH)

        self.techs_status[tech] = TechStatus.RESEARCHED
        self.fill_out_available_buildings(game_state)

        if tech != TECHS.RENAISSANCE:
            vps = self.vps_per_tech_level[tech.advancement_level]
            for source, amount in vps.items():
                self.gain_vps(amount, source)

    def _update_vps_per_tech_level(self, game_state: 'GameState'):
        if self.game_player is None:
            return DetailedNumber()

        for lvl in range(10):
            self.vps_per_tech_level[lvl] = DetailedNumber()
            self.vps_per_tech_level[lvl].add(score_strings.TECH, TECH_VP_REWARD * lvl)
            if self.has_tenet(TENETS.RATIONALISM):
                self.vps_per_tech_level[lvl].add(TENETS.RATIONALISM.name, max(0, lvl - 3))
            for ability, building in self.passive_building_abilities_of_name("ExtraVpPerAgeOfTechResearched", game_state):
                self.vps_per_tech_level[lvl].add(building.building_name, ability.numbers[0] * lvl)

    def complete_research(self, tech: TechTemplate, game_state: 'GameState'):

        for other_tech, status in self.techs_status.items():
            if status == TechStatus.AVAILABLE and other_tech != TECHS.RENAISSANCE and other_tech.name != tech.name:
                self.techs_status[other_tech] = TechStatus.DISCARDED

        if tech == TECHS.RENAISSANCE:
            logger.info(f"Renaissance for civ {self.moniker()}")
            self.science -= tech.cost
            for other_tech, status in self.techs_status.items():
                if status == TechStatus.DISCARDED:
                    self.techs_status[other_tech] = TechStatus.UNAVAILABLE
        else:
            self.science -= tech.cost
            self.gain_tech(game_state, tech)

        # Never discard renaissance
        self.techs_status[TECHS.RENAISSANCE] = TechStatus.UNAVAILABLE

        self.get_new_tech_choices()

    def roll_turn_pre_harvest(self, game_state: 'GameState') -> None:
        self.city_power += self.projected_city_power_income.value
        self.science += self.projected_science_income.value

        if self.has_tenet(TENETS.PROMISE_OF_FREEDOM):
            my_age = self.get_advancement_level()
            for civ in game_state.civs_by_id.values():
                if civ.get_advancement_level() < my_age:
                    civ.gain_vps(-1, "Promise of Freedom")
            if my_age > game_state.advancement_level:
                self.gain_vps(1, "Promise of Freedom")

    def update_vitality_decay_rate(self, game_state: 'GameState') -> None:
        vitality_decay_rate = DetailedNumber()
        vitality_decay_rate.add("Base", VITALITY_DECAY_RATE)
        if self.has_tenet(TENETS.FOUNTAIN_OF_YOUTH, check_complete_quest=True):
            vitality_decay_rate.add("Fountain of Youth", -0.01)
        for city in self.get_my_cities(game_state):
            for ability, building in city.passive_building_abilities_of_name("DecreaseVitalityDecayPerAdjacentOcean"):
                vitality_decay_rate.add(building.building_name, -ability.numbers[0] * city.terrains_dict.get(TERRAINS.OCEAN, 0))
        self.vitality_decay_rate = vitality_decay_rate

    def roll_turn_post_harvest(self, sess, game_state: 'GameState') -> None:
        self.fill_out_available_buildings(game_state)

        if self.researching_tech:
            researching_tech = self.researching_tech
            cost = researching_tech.cost
            if researching_tech and cost <= self.science:
                self.complete_research(researching_tech, game_state)

                game_state.add_animation_frame_for_civ(sess, {
                    "type": "TechResearched",
                    "tech": researching_tech.name,
                }, self)

        self.vitality *= (1 - self.vitality_decay_rate.value)
        self.update_max_territories(game_state)
        if self.city_power <= 0:
            self.trade_hub_id = None

    def from_json_postprocess(self, game_state: 'GameState') -> None:
        if self._game_player_num is not None:
            self.game_player = game_state.game_player_by_player_num[self._game_player_num]

        if self.target_coords:
            self.targets = [game_state.hexes[target_coord] for target_coord in self.target_coords]

    def capital_city(self, game_state) -> 'City | None':
        lst = [city for city in game_state.cities_by_id.values() if city.civ == self and city.capital]
        if len(lst) > 1 and STRICT_MODE:
            raise ValueError(f"Civ {self.moniker()} has multiple capital cities: {lst}")
        if len(lst) > 0:
            return lst[0]
        else:
            return None
        
    def largest_city(self, game_state: 'GameState') -> 'City | None':
        return max(game_state.cities_by_id.values(), key=lambda c: c.population, default=None)

    def get_great_person(self, age: int, city: 'City', game_state: 'GameState'):
        self._great_people_choices_queue.append((age, city.id))
        self._pop_great_people_choices_queue_if_needed(game_state)

    def _sample_great_people(self, valid_great_people: list[GreatPerson]):
        for _ in range(5):
            random.shuffle(valid_great_people)
            choices = valid_great_people[:3]
            # try to avoid all the same type
            if len({gp.__class__ for gp in choices}) == 1:
                continue
            return choices
        return valid_great_people[:3]

    def _pop_great_people_choices_queue_if_needed(self, game_state):
        if len(self.great_people_choices) == 0 and len(self._great_people_choices_queue) > 0:
            age, city_id = self._great_people_choices_queue.pop(0)
            city = game_state.cities_by_id[city_id]
            age = min(age, 9)  # There aren't any great people for age 10.
            all_great_people = great_people_by_age(age)
            valid_great_people = [great_person for great_person in all_great_people if great_person.valid_for_city(city, civ=self)]
            if len(valid_great_people) == 0:
                str = f"Civ {self.moniker()} earned a great person, but no valid options. Age: {age}, city: {city.name}"
                if STRICT_MODE:
                    raise ValueError(str)
                else:
                    logger.warning(str)
                    return []
            self.great_people_choices = self._sample_great_people(valid_great_people)
            self._great_people_choices_city_id = city_id
            logger.info(f"Civ {self.moniker()} earned a great person. Chose {self.great_people_choices} from valid options: {valid_great_people}")

    def select_great_person(self, game_state: 'GameState', great_person_name):
        if STRICT_MODE:
            assert great_person_name in [great_person.name for great_person in self.great_people_choices], f"{great_person_name, self.great_people_choices}"
        assert self._great_people_choices_city_id is not None
        assert self._great_people_choices_city_id in game_state.cities_by_id, f"Chose a great person in a nonexistent city id: {self._great_people_choices_city_id}"
        city = game_state.cities_by_id[self._great_people_choices_city_id]
        great_person: GreatPerson = great_people_by_name[great_person_name]
        great_person.apply(city=city, civ=self, game_state=game_state)
        game_state.add_announcement(f"{great_person.name} will lead <civ id={self.id}>{self.moniker()}</civ> to glory.")
        game_state.add_to_message_of_existing_parsed_announcement(game_state.turn_num, "decline", self.game_player.player_num if self.game_player else None, f" {great_person.name} will lead {self.moniker()} to glory.")
        game_state.add_to_message_of_existing_parsed_announcement(game_state.turn_num, "revolt", self.game_player.player_num if self.game_player else None, f" The {self.moniker()} are led by a charismatic and unscrupulous individual known to us only as \"{great_person.name}\".")
        if self.has_tenet(TENETS.HOLY_GRAIL, check_complete_quest=True):
            assert self.game_player is not None
            if self.game_player.tenets[TENETS.HOLY_GRAIL].get("second_great_person_choice", False):
                self.great_people_choices = []
                self._great_people_choices_city_id = None
                self.game_player.tenets[TENETS.HOLY_GRAIL]["second_great_person_choice"] = False
                self.science -= 100
            else:
                self.great_people_choices = [person for person in self.great_people_choices if person != great_person and person.valid_for_city(city, civ=self)]
                if len(self.great_people_choices) == 0:
                    raise ValueError(f"No valid great people choices left for {self.moniker()} after selecting {great_person.name}.")
                self.game_player.tenets[TENETS.HOLY_GRAIL]["second_great_person_choice"] = True
        else:
            self.great_people_choices = []
            self._great_people_choices_city_id = None
        self._pop_great_people_choices_queue_if_needed(game_state)

    def spawn_unit_on_hex(self, game_state: 'GameState', unit_template: 'UnitTemplate', hex: 'Hex', bonus_strength: int=0, stack_size=1) -> 'Unit | None':
        assert not hex.is_occupied(self, allow_enemy_city=True, allow_allied_unit=False, allow_enemy_unit=False)
        unit = Unit(unit_template, civ=self, hex=hex)
        unit.health *= stack_size
        hex.append_unit(unit, game_state)
        game_state.units.append(unit)
        unit.strength += bonus_strength
        game_state.refresh_visibility_by_civ()
        return unit

    @staticmethod
    def from_json(json: dict) -> "Civ":
        civ = Civ(
            civ_template=CIVS.by_name(json["name"]),
            game_player=None,
        )
        civ._game_player_num = json["game_player_num"]
        civ.id = json["id"]
        civ.science = json["science"]
        civ.techs_status = {tech: TechStatus(json["techs_status"][tech.name]) for tech in TECHS.all()}
        civ.vitality = json["vitality"]
        civ.city_power = json["city_power"]
        civ.available_city_buildings = [BUILDINGS.by_name(b) for b in json["available_buildings"]]
        civ.available_unit_buildings = [UNITS.by_name(u) for u in json["available_unit_buildings"]]
        civ.buildings_in_all_queues = json["buildings_in_all_queues"]
        civ.target_coords = json["targets"][:]
        civ.projected_science_income = DetailedNumber.from_json(json["projected_science_income"])
        civ.projected_city_power_income = DetailedNumber.from_json(json["projected_city_power_income"])
        civ.in_decline = json["in_decline"]
        civ.trade_hub_id = json.get("trade_hub_id")
        civ.trade_hub_city_power_consumption = json.get("trade_hub_city_power_consumption", 0.0)
        civ.great_people_choices = [GreatPerson.from_json(great_person_json) for great_person_json in json.get("great_people_choices", [])]
        civ._great_people_choices_queue = [(age, city_id) for age, city_id in json.get("great_people_choices_queue", [])]
        civ._great_people_choices_city_id = json.get("great_people_choices_city_id")
        civ.max_territories = json.get("max_territories", 3)
        civ.vandetta_civ_id = json.get("vandetta_civ_id")
        civ.score_dict = json["score_dict"]
        civ.unique_units_built = json["unique_units_built"]
        civ.vps_per_tech_level = [DetailedNumber.from_json(vps_json) for vps_json in json.get("vps_per_tech_level", [])]

        return civ

    def __repr__(self) -> str:
        return f"<Civ {self.id}: {self.template.name}>"

def create_starting_civ_options_for_players(game_players: list[GamePlayer], starting_locations: list['Hex']) -> dict[int, list[tuple[Civ, 'Hex']]]:
    assert len(game_players) <= MAX_PLAYERS

    starting_civ_template_options = random.sample(list(player_civs(max_advancement_level=0)), NUM_STARTING_LOCATION_OPTIONS * len(game_players))
    location_map = assign_starting_locations(starting_civ_template_options, starting_locations)

    civs = []
    for civ_template, game_player in zip(starting_civ_template_options, itertools.cycle(game_players)):
        civ = Civ(civ_template, game_player)
        civ.get_new_tech_choices()
        if civ.has_ability('ExtraCityPower'):
            civ.city_power += civ.numbers_of_ability('ExtraCityPower')[0]
        civs.append(civ)

    game_players_to_civs = {game_player.player_num: [] for game_player in game_players}
    for civ in civs:
        game_players_to_civs[civ.game_player.player_num].append((civ, location_map[civ.template]))
    return game_players_to_civs
