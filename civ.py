import random
from typing import TYPE_CHECKING, Any, Generator, Literal, Optional, Dict
from collections import defaultdict
from TechStatus import TechStatus
from move_type import MoveType
from unit import Unit
from settings import GOD_MODE
from wonder_templates_list import WONDERS
from great_person import GreatGeneral, GreatPerson, great_people_by_age, great_people_by_name
from civ_template import CivTemplate
from civ_templates_list import player_civs, CIVS
from game_player import GamePlayer
from settings import AI, NUM_STARTING_LOCATION_OPTIONS, STRICT_MODE, VITALITY_DECAY_RATE, BASE_CITY_POWER_INCOME, TECH_VP_REWARD, RENAISSANCE_VITALITY_BOOST, MAX_PLAYERS
from tech_template import TechTemplate
from building_template import BuildingTemplate, BuildingType
from unit_template import UnitTemplate
from unit_templates_list import UNITS
from utils import generate_unique_id
from building_templates_list import BUILDINGS
from tech_templates_list import TECHS

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
        self.id = generate_unique_id()
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
        self.target1: Optional['Hex'] = None
        self.target2: Optional['Hex'] = None
        self.target1_coords: Optional[str] = None
        self.target2_coords: Optional[str] = None
        self.projected_science_income = 0.0
        self.projected_city_power_income = 0.0
        self.in_decline = False
        self.trade_hub_id: Optional[str] = None
        self.great_people_choices: list[GreatPerson] = []
        self._great_people_choices_city_id: Optional[str] = None
        self._great_people_choices_queue: list[tuple[int, str]] = []  # age, city_id
        self.max_territories: int = 3
        self.vandetta_civ_id: Optional[str] = None
        self.unique_units_built: int = 0
        self.renaissances: int = 0

        self.score_dict: dict[str, float] = {}

    def __eq__(self, other: 'Civ') -> bool:
        # TODO(dfarhi) clean up all remaining instances of (civ1.id == civ2.id)
        return other is not None and self.id == other.id

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

    def adjust_projected_yields(self, game_state: 'GameState') -> None:
        self.projected_science_income = 0.0
        self.projected_city_power_income = BASE_CITY_POWER_INCOME

        for city in game_state.cities_by_id.values():
            if city.civ.id == self.id:
                self.projected_science_income += city.projected_income.science
                self.projected_city_power_income += city.projected_income.city_power

    def has_tech(self, tech: TechTemplate) -> bool:
        return self.techs_status[tech] == TechStatus.RESEARCHED

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

    def initialize_techs(self, start_techs: set[TechTemplate]):
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
        if len(techs_to_offer) < num_techs_to_offer and self.game_player is not None:
            # We've teched to too many things, time for a Renaissance
            self.techs_status[TECHS.RENAISSANCE] = TechStatus.AVAILABLE

    def get_advancement_level(self, fractional=False) -> float:
        num_techs = len(self.researched_techs)
        if num_techs == 0:
            age = 0
            techs_progress_towards_next_age = 0
            needed_for_next_age = 1
        elif num_techs <=2:
            age = 1
            techs_progress_towards_next_age = num_techs - 1
            needed_for_next_age = 2
        else:
            age = 1 + num_techs // 3
            techs_progress_towards_next_age = num_techs % 3
            needed_for_next_age = 3
        age = min(age, 10)
        
        if not fractional:
            return age
        else:
            available_techs = [t for t in self._available_techs() if t is not TECHS.RENAISSANCE]
            average_available_tech_cost = sum([tech.cost for tech in available_techs]) / len(available_techs) if len(available_techs) > 0 else 1
            partial_tech_progress: float = self.science / average_available_tech_cost
            clipped_partial_tech_progress: float = min(partial_tech_progress, 0.9)

            partial_age_progress = (techs_progress_towards_next_age + clipped_partial_tech_progress) / needed_for_next_age

            return age + partial_age_progress

    def get_my_cities(self, game_state: 'GameState') -> list['City']:
        return [city for city in game_state.cities_by_id.values() if city.civ == self]

    def update_max_territories(self, game_state: 'GameState'):
        base: int = 3
        bonuses: int = len([ability for ability, _ in self.passive_building_abilities_of_name('ExtraTerritory', game_state)])
        self.max_territories = base + bonuses

    def _available_techs(self) -> list[TechTemplate]:
        return [tech for tech, status in self.techs_status.items() if status in (TechStatus.AVAILABLE, TechStatus.RESEARCHING)]

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "game_player": self.game_player.to_json() if self.game_player else None,
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
            "target1": self.target1.coords if self.target1 else None,
            "target2": self.target2.coords if self.target2 else None,
            "projected_science_income": self.projected_science_income,
            "projected_city_power_income": self.projected_city_power_income,
            "in_decline": self.in_decline,
            "advancement_level": self.get_advancement_level(),
            "renaissance_cost": self.renaissance_cost() if self.game_player is not None else None,
            "trade_hub_id": self.trade_hub_id,
            "great_people_choices": [great_person.to_json() for great_person in self.great_people_choices],
            "great_people_choices_queue": [(age, city_id) for age, city_id in self._great_people_choices_queue],
            "great_people_choices_city_id": self._great_people_choices_city_id,
            "max_territories": self.max_territories,
            "vandetta_civ_id": self.vandetta_civ_id,
            "score_dict": self.score_dict,
            "unique_units_built": self.unique_units_built,
            "renaissances": self.renaissances,
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

        # Don't decline within 2 turns of finishing renaissance
        if self.projected_science_income > 0 and self.techs_status[TECHS.RENAISSANCE] == TechStatus.RESEARCHING and (self.renaissance_cost() - self.science) / self.projected_science_income <= 2:
            logger.info(f"{self.moniker()} deciding not to decline because I'm almost done with a renaissance.")

        # Don't decline if I have above average army size.
        all_army_sizes: dict[str, float] = defaultdict(float)
        for unit in game_state.units:
            all_army_sizes[unit.civ.id] += unit.template.metal_cost
        active_army_sizes: dict[str, float] = {
            game_player.civ_id: all_army_sizes[game_player.civ_id] 
            for game_player in game_state.game_player_by_player_num.values() 
            if game_player.civ_id is not None}
        my_rank: int = sum(active_army_sizes[self.id] <= other for other in active_army_sizes.values())
        total_players: int = len(game_state.game_player_by_player_num)
        if my_rank <= total_players / 2:
            logger.info(f"{self.moniker()} deciding not to decline because I'm rank {my_rank} of {total_players}")
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
            [city.projected_income['food'] +city.projected_income['wood'] + city.projected_income['metal'] +city.projected_income['science'] 
             for city in my_cities])
        
        option_total_yields: dict[str, float] = {}
        for city in game_state.cities_by_id.values():
            if city.civ_to_revolt_into is None:
                continue

            if city.civ == self:
                continue

            current_total_yields = city.projected_income['food'] +city.projected_income['wood'] + city.projected_income['metal'] +city.projected_income['science'] 
            option_total_yields[city.hex.coords] = current_total_yields / city.civ.vitality
            option_total_yields[city.hex.coords] += AI.RURAL_SLOT_VALUE * city.rural_slots + city.population * city.urban_slots
            option_total_yields[city.hex.coords] *= city.revolting_starting_vitality

        for coords, city in game_state.fresh_cities_for_decline.items():
            option_total_yields[coords] = city.projected_income['food'] +city.projected_income['wood'] + city.projected_income['metal'] +city.projected_income['science']
            option_total_yields[coords] += (AI.RURAL_SLOT_VALUE * city.rural_slots + city.population * city.urban_slots) * city.revolting_starting_vitality

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

    def bot_move(self, game_state: 'GameState') -> None:
        if  len(self.great_people_choices) > 0:
            choice: GreatPerson = max(self.great_people_choices, key=lambda g: (isinstance(g, GreatGeneral), random.random()))
            game_state.resolve_move(MoveType.SELECT_GREAT_PERSON, {'great_person_name': choice.name}, civ=self)
        # Choose trade hub:
        unhappy_cities = [city for city in self.get_my_cities(game_state) if city.unhappiness + city.projected_income["unhappiness"] > 0]
        def trade_hub_priority(city: 'City'):
            income = sum(city.projected_income[x] for x in ['wood', 'metal', 'science'])
            on_leaderboard = city.civ_to_revolt_into is not None
            unhappiness = city.unhappiness + city.projected_income["unhappiness"]
            close_to_leaderboard = unhappiness >= game_state.unhappiness_threshold
            return on_leaderboard, close_to_leaderboard, income
        if len(unhappy_cities) > 0:
            game_state.resolve_move(MoveType.TRADE_HUB, {'city_id': max(unhappy_cities, key=trade_hub_priority).id}, civ=self)

        if WONDERS.UNITED_NATIONS in game_state.built_wonders:
            un_owner_ids: list[str] = [civ_id for _, civ_id in game_state.built_wonders[WONDERS.UNITED_NATIONS].infos]
            if len(un_owner_ids) > 1:
                # If lots fo people have UN, follow a random one for first flag and a random one for second flag
                random.shuffle(un_owner_ids)
                un_owner_ids = un_owner_ids[:2]
            else:
                # If only one person has UN, follow them for first and second flag
                un_owner_ids = [un_owner_ids[0], un_owner_ids[0]]
            un_owner_civs: list[Civ] = [game_state.civs_by_id[civ_id] for civ_id in un_owner_ids]
            target1_coords = un_owner_civs[0].target1_coords
            target2_coords = un_owner_civs[1].target2_coords
            if target1_coords is not None:
                game_state.resolve_move(MoveType.SET_CIV_PRIMARY_TARGET, {'target_coords': target1_coords}, civ=self)
            else:
                game_state.resolve_move(MoveType.REMOVE_CIV_PRIMARY_TARGET, {}, civ=self)
            if target2_coords is not None:
                game_state.resolve_move(MoveType.SET_CIV_SECONDARY_TARGET, {'target_coords': target2_coords}, civ=self)
            else:
                game_state.resolve_move(MoveType.REMOVE_CIV_SECONDARY_TARGET, {}, civ=self)
        elif random.random() < AI.CHANCE_MOVE_FLAG or self.target1 is None or self.target2 is None or \
            (self.target1.city is not None and self.target1.city.civ == self) or (self.target2.city is not None and self.target2.city.civ == self):
            enemy_cities: list[City] = [city for city in game_state.cities_by_id.values() if city.civ.id != self.id]
            vandetta_cities: list[City] = [city for city in enemy_cities if city.civ.id == self.vandetta_civ_id]
            if len(vandetta_cities) > 0:
                possible_target_hexes: list[Hex] = [city.hex for city in vandetta_cities]
            else:
                possible_target_hexes: list[Hex] = [*[city.hex for city in enemy_cities], *[camp.hex for camp in game_state.camps]]

            random.shuffle(possible_target_hexes)

            if len(possible_target_hexes) > 0:
                game_state.resolve_move(MoveType.SET_CIV_PRIMARY_TARGET, {'target_coords': possible_target_hexes[0].coords}, civ=self)
            if len(possible_target_hexes) > 1:
                game_state.resolve_move(MoveType.SET_CIV_SECONDARY_TARGET, {'target_coords': possible_target_hexes[1].coords}, civ=self)

        if self.researching_tech is None:
            special_tech = None
            if self.unique_unit is not None:
                special_tech = self.unique_unit.prereq

            available_techs: list[TechTemplate] = [tech for tech, status in self.techs_status.items() if status == TechStatus.AVAILABLE]

            if special_tech and self.techs_status[special_tech] == TechStatus.AVAILABLE:
                chosen_tech = special_tech
            else:
                if len(available_techs) > 0:
                    # Pick randomly, avoiding renaissance if possibhle.
                    chosen_tech = sorted(available_techs, key=lambda t: (t == TECHS.RENAISSANCE, random.random()))[0]
                else:
                    logger.info(f"{self.moniker()} has no available techs")
                    chosen_tech = None
            if chosen_tech is not None:
                game_state.resolve_move(MoveType.CHOOSE_TECH, {'tech_name': chosen_tech.name}, civ=self)
                logger.info(f"  {self.moniker()} chose tech {chosen_tech} from {available_techs}")

        self.bot_found_cities(game_state)

        my_production_cities = [city for city in self.get_my_cities(game_state) if city.is_territory_capital]

        for city in sorted(my_production_cities, key=lambda c: c.population, reverse=True):
            city.bot_move(game_state)

    def bot_found_cities(self, game_state: 'GameState') -> None:
        while not self.in_decline and self.city_power >= 100 and not self.template.name == 'Barbarians':
            choices = [hex for hex in game_state.hexes.values() if hex.is_foundable_by_civ.get(self.id)]
            if len(choices) == 0:
                break
            hex = max(choices, key=lambda h: (sum([n.yields for n in h.get_neighbors(game_state.hexes, include_self=True)], start=Yields()).total(), random.random()))
            game_state.resolve_move(MoveType.FOUND_CITY, {'coords': hex.coords, 'city_id': generate_unique_id()}, civ=self)

    def renaissance_cost(self) -> float:
        return 50 * self.get_advancement_level() * (1 + self.renaissances)

    def gain_tech(self, game_state: 'GameState', tech: TechTemplate) -> None:
        self.techs_status[tech] = TechStatus.RESEARCHED
        self.fill_out_available_buildings(game_state)

        if tech != TECHS.RENAISSANCE:
            self.gain_vps(TECH_VP_REWARD * tech.advancement_level, f"Research ({TECH_VP_REWARD}/tech level)")

            for ability, building in self.passive_building_abilities_of_name("ExtraVpPerAgeOfTechResearched", game_state):
                amount = ability.numbers[0] * tech.advancement_level
                self.gain_vps(amount, building.building_name)

    def complete_research(self, tech: TechTemplate, game_state: 'GameState'):

        for other_tech, status in self.techs_status.items():
            if status == TechStatus.AVAILABLE and other_tech != TECHS.RENAISSANCE and other_tech.name != tech.name:
                self.techs_status[other_tech] = TechStatus.DISCARDED

        if tech == TECHS.RENAISSANCE:
            logger.info(f"Renaissance for civ {self.moniker()}")
            game_state.add_announcement(f"The <civ id={self.id}>{self.moniker()}</civ> have completed a Renaissance.")
            cost: float = self.renaissance_cost()
            self.science -= cost
            for other_tech, status in self.techs_status.items():
                if status == TechStatus.DISCARDED:
                    self.techs_status[other_tech] = TechStatus.UNAVAILABLE
            self.vitality *= RENAISSANCE_VITALITY_BOOST
            self.renaissances += 1
        else:
            self.science -= tech.cost
            self.gain_tech(game_state, tech)

        # Never discard renaissance
        self.techs_status[TECHS.RENAISSANCE] = TechStatus.UNAVAILABLE

        self.get_new_tech_choices()

    def roll_turn_pre_harvest(self) -> None:
        self.city_power += self.projected_city_power_income
        self.science += self.projected_science_income

    def roll_turn_post_harvest(self, sess, game_state: 'GameState') -> None:
        self.fill_out_available_buildings(game_state)

        if self.researching_tech:
            researching_tech = self.researching_tech
            cost = self.renaissance_cost() if researching_tech == TECHS.RENAISSANCE else researching_tech.cost
            if researching_tech and cost <= self.science:
                self.complete_research(researching_tech, game_state)

                game_state.add_animation_frame_for_civ(sess, {
                    "type": "TechResearched",
                    "tech": researching_tech.name,
                }, self)

        self.vitality *= VITALITY_DECAY_RATE        
        self.update_max_territories(game_state)

    def from_json_postprocess(self, game_state: 'GameState') -> None:
        if self.game_player is not None:
            self.game_player = game_state.game_player_by_player_num[self.game_player.player_num]

        if self.target1_coords:
            self.target1 = game_state.hexes[self.target1_coords]
        if self.target2_coords:
            self.target2 = game_state.hexes[self.target2_coords]

    def capital_city(self, game_state) -> 'City | None':
        lst = [city for city in game_state.cities_by_id.values() if city.civ == self and city.capital]
        if len(lst) > 1 and STRICT_MODE:
            raise ValueError(f"Civ {self.moniker()} has multiple capital cities: {lst}")
        if len(lst) > 0:
            return lst[0]
        else:
            return None

    def get_great_person(self, age: int, city: 'City', game_state: 'GameState'):
        self._great_people_choices_queue.append((age, city.id))
        self._pop_great_people_choices_queue_if_needed(game_state)

    def _pop_great_people_choices_queue_if_needed(self, game_state):
        if len(self.great_people_choices) == 0 and len(self._great_people_choices_queue) > 0:
            age, city_id = self._great_people_choices_queue.pop(0)
            city = game_state.cities_by_id[city_id]
            all_great_people = great_people_by_age(age)
            valid_great_people = [great_person for great_person in all_great_people if great_person.valid_for_city(city, civ=self)]
            random.shuffle(valid_great_people)
            self.great_people_choices = valid_great_people[:3]
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
        self.great_people_choices = []
        self._great_people_choices_city_id = None
        self._pop_great_people_choices_queue_if_needed(game_state)

    def spawn_unit_on_hex(self, game_state: 'GameState', unit_template: 'UnitTemplate', hex: 'Hex', bonus_strength: int=0, stack_size=1) -> 'Unit | None':
        unit = Unit(unit_template, civ=self, hex=hex)
        unit.health *= stack_size
        hex.units.append(unit)
        game_state.units.append(unit)
        unit.strength += bonus_strength
        game_state.refresh_visibility_by_civ()
        return unit

    @staticmethod
    def from_json(json: dict) -> "Civ":
        civ = Civ(
            civ_template=CIVS.by_name(json["name"]),
            game_player=GamePlayer.from_json(json["game_player"]) if json["game_player"] else None,
        )
        civ.id = json["id"]
        civ.science = json["science"]
        civ.techs_status = {tech: TechStatus(json["techs_status"][tech.name]) for tech in TECHS.all()}
        civ.vitality = json["vitality"]
        civ.city_power = json["city_power"]
        civ.available_city_buildings = [BUILDINGS.by_name(b) for b in json["available_buildings"]]
        civ.available_unit_buildings = [UNITS.by_name(u) for u in json["available_unit_buildings"]]
        civ.buildings_in_all_queues = json["buildings_in_all_queues"]
        civ.target1_coords = json["target1"]
        civ.target2_coords = json["target2"]
        civ.projected_science_income = json["projected_science_income"]
        civ.projected_city_power_income = json["projected_city_power_income"]
        civ.in_decline = json["in_decline"]
        civ.trade_hub_id = json.get("trade_hub_id")
        civ.great_people_choices = [GreatPerson.from_json(great_person_json) for great_person_json in json.get("great_people_choices", [])]
        civ._great_people_choices_queue = [(age, city_id) for age, city_id in json.get("great_people_choices_queue", [])]
        civ._great_people_choices_city_id = json.get("great_people_choices_city_id")
        civ.max_territories = json.get("max_territories", 3)
        civ.vandetta_civ_id = json.get("vandetta_civ_id")
        civ.score_dict = json["score_dict"]
        civ.unique_units_built = json["unique_units_built"]
        civ.renaissances = json["renaissances"]

        return civ

    def __repr__(self) -> str:
        return f"<Civ {self.id}: {self.template.name}>"

def create_starting_civ_options_for_players(game_players: list[GamePlayer], starting_locations: list['Hex']) -> dict[int, list[tuple[Civ, 'Hex']]]:
    assert len(game_players) <= MAX_PLAYERS

    starting_civ_template_options = random.sample(list(player_civs(max_advancement_level=0)), NUM_STARTING_LOCATION_OPTIONS * len(game_players))

    starting_civ_options = {}

    counter = 0

    for game_player in game_players:
        starting_civ_options[game_player.player_num] = []
        for _ in range(NUM_STARTING_LOCATION_OPTIONS):
            civ = Civ(starting_civ_template_options[counter], game_player)
            civ.get_new_tech_choices()
            if civ.has_ability('ExtraCityPower'):
                civ.city_power += civ.numbers_of_ability('ExtraCityPower')[0]

            starting_civ_options[game_player.player_num].append((civ, starting_locations[counter]))
            counter += 1

    return starting_civ_options
