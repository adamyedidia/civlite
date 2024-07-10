import itertools
import math
from typing import TYPE_CHECKING, Any, Generator, Iterable, Literal, Optional, Union
from building import Building, QueueEntry
from building_template import BuildingTemplate, BuildingType
from building_templates_list import BUILDINGS
from civ_template import CivTemplate
from civ import Civ
from camp import Camp
from local_settings import GOD_MODE
from terrain_templates_list import TERRAINS
from terrain_template import TerrainTemplate
from settings import AI, ADDITIONAL_PER_POP_FOOD_COST, BASE_FOOD_COST_OF_POP, CITY_CAPTURE_REWARD, DEVELOP_VPS, FRESH_CITY_VITALITY_PER_TURN, REVOLT_VITALITY_PER_TURN, REVOLT_VITALITY_PER_UNHAPPINESS, STRICT_MODE, VITALITY_DECAY_RATE, UNIT_BUILDING_BONUSES, MAX_SLOTS, DEVELOP_COST, MAX_SLOTS_OF_TYPE
from unit import Unit
from unit_building import UnitBuilding
from unit_template import UnitTemplate
from unit_templates_list import UNITS, UNITS_BY_BUILDING_NAME
from wonder_template import WonderTemplate
from wonder_templates_list import WONDERS
from civ_templates_list import CIVS
from utils import generate_unique_id
import random
from typing import Dict
import traceback
from city_names import CITY_NAMES_BY_CIV
from yields import Yields

if TYPE_CHECKING:
    from hex import Hex
    from game_state import GameState
    from ability import Ability

TRADE_HUB_CITY_POWER_PER_TURN = 20

_DEVELOPMENT_VPS_STR = f"Development ({DEVELOP_VPS} each)"

class City:
    def __init__(self, civ: Civ, name: str, id: Optional[str] = None):
        # civ actually can be None very briefly before GameState.from_json() is done, 
        # but I don't want to tell the type-checker so we don't have to put a million asserts everywhere

        self.id = id or generate_unique_id()
        self.civ: Civ = civ
        self.civ_id: str = civ.id if civ else None  # type: ignore
        self.ever_controlled_by_civ_ids: dict[str, bool] = {civ.id: True} if civ else {}
        self.name = name
        self.population = 1
        self.food = 0.0
        self.metal = 0.0
        self.wood = 0.0
        self.food_demand = 0
        self.focus: str = 'food'
        self.rural_slots = 1
        self.urban_slots = 1
        self.military_slots = 1
        self.under_siege_by_civ: Optional[Civ] = None
        self.hex: Optional['Hex'] = None
        self.buildings_queue: list[QueueEntry] = []
        self.buildings: list[Building] = []
        self.unit_buildings: list[UnitBuilding] = [UnitBuilding(UNITS.WARRIOR)]
        self.available_city_buildings: list[BuildingTemplate] = []
        self.available_wonders: list[WonderTemplate] = []
        self.available_unit_buildings: list[UnitTemplate] = []
        self.available_buildings_to_descriptions: dict[str, dict[str, Union[str, float, int]]] = {}
        self.building_yields: dict[str, Yields] = {}
        self.available_buildings_payoff_times: dict[str, int] = {}
        self.capital = False
        self._territory_parent_id: Optional[str] = None
        self._territory_parent_coords: Optional[str] = None
        self.available_units: list[UnitTemplate] = []
        self.projected_income = Yields()
        self.projected_income_base = Yields()  # income without focus
        self.projected_income_focus = Yields()  # income from focus
        self.projected_income_puppets: dict[str, dict[str, tuple[float, int]]] = {'wood': {}, 'metal': {}} # (amount, distance)
        self.projected_build_queue_depth: int = 0
        self.projected_bulldozes: list[UnitTemplate] = []
        self.terrains_dict: dict[TerrainTemplate, int] = {}
        self.founded_turn: int | None = None
        self.expanded_by_civ_ids: list[str] = []

        # Revolt stuff
        self.civ_to_revolt_into: Optional[CivTemplate] = None
        self.revolting_starting_vitality: float = 1.0
        self.unhappiness: float = 0.0
        self.is_decline_view_option: bool = False
        self.revolt_unit_count: int = 0

    def __repr__(self):
        return f"<City {self.name} @ {self.hex.coords if self.hex else None}>"
    
    def __hash__(self):
        return hash(self.id)

    def has_building(self, template: BuildingTemplate | UnitTemplate | WonderTemplate) -> bool:
        if isinstance(template, UnitTemplate):
            return any(b.template == template for b in self.unit_buildings)
        else:
            return any(b._template == template for b in self.buildings)

    def orphan_territory_children(self, game_state: 'GameState', make_new_territory=True):
        """
        Call before changing ownership of a city to clear any puppets who have it as parent.
        """
        children: list[City] = [city for city in game_state.cities_by_id.values() if city.get_territory_parent(game_state) == self]
        if len(children) == 0:
            return
        if make_new_territory:
            new_territory_capital: City | None = max(children, key=lambda c: (c.population, c.id))
            new_territory_capital.make_territory_capital(game_state)
        else:
            new_territory_capital = None
        for child in children:
            if child != new_territory_capital:
                child.set_territory_parent_if_needed(game_state, adopt_focus=False)

    def _remove_income_from_parent(self, game_state: 'GameState') -> None:
        parent: City | None = self.get_territory_parent(game_state)
        if parent:
            for resource, data in parent.projected_income_puppets.items():
                if self.name in data:
                    del data[self.name]

    def make_territory_capital(self, game_state: 'GameState') -> None:
        self._remove_income_from_parent(game_state)
        self._territory_parent_id = None
        self._territory_parent_coords = None

    def set_territory_parent_if_needed(self, game_state: 'GameState', adopt_focus: bool) -> None:
        my_territories: list[City] = [city for city in game_state.cities_by_id.values() if city.civ == self.civ and city.is_territory_capital and city != self]
        choices: list[City] = [city for city in my_territories]
        if len(my_territories) < self.civ.max_territories:
            # Room for another territory capital.
            self.make_territory_capital(game_state)
        else:
            # Pick the closest one to be my parent.
            choice: City = min(choices, key=lambda c: (self.hex.distance_to(c.hex), c.capital, -c.population, c.id))  # type: ignore
            self._remove_income_from_parent(game_state)
            self._territory_parent_id = choice.id
            self._territory_parent_coords = choice.hex.coords  # type: ignore
            if adopt_focus:
                self.focus = choice.focus

    @property
    def is_territory_capital(self) -> bool:
        return self._territory_parent_id is None
    
    def get_puppets(self, game_state: 'GameState') -> list['City']:
        return [city for city in game_state.cities_by_id.values() if city.get_territory_parent(game_state) == self]

    def get_territory_parent(self, game_state: 'GameState') -> Optional['City']:
        if self._territory_parent_id is None:
            return None
        elif self._territory_parent_id in game_state.cities_by_id:
            return game_state.cities_by_id[self._territory_parent_id]
        else:
            # This can happen if the parent isn't visible to the viewing civ.
            return None

    def midturn_update(self, game_state: 'GameState') -> None:
        """
        Update things that could have changed due to the controlling player fiddling with focus etc.
        """
        if self.is_territory_capital:
            for puppet in self.get_puppets(game_state):
                puppet.midturn_update(game_state)
        self.adjust_projected_yields(game_state)
        self.adjust_projected_builds(game_state)
        self.adjust_projected_unit_builds()
        self._refresh_available_buildings_and_units(game_state)

    def is_trade_hub(self):
        return self.civ.trade_hub_id == self.id
    
    def is_fake_city(self) -> bool:
        assert self.hex is not None
        return self.hex.city != self

    def puppet_distance_penalty(self) -> float:
        bldg_factors = [ability.numbers[0] for ability, _ in self.passive_building_abilities_of_name('ReducePuppetDistancePenalty')]
        return min([.1] + bldg_factors)

    def unit_building_from_template(self, template: UnitTemplate):
        for bldg in self.unit_buildings:
            if bldg.template == template:
                return bldg
        raise KeyError(f"No unit building for {template}")

    def toggle_unit_build(self, unit: UnitTemplate):
        if STRICT_MODE:
            assert self.is_territory_capital, f"{self.name} tried to toggle unit build while a puppet"
            assert unit in self.available_units, f"{self.name} trying to build unit {unit} but only have {self.available_units}."
        unit_bldg = self.unit_building_from_template(unit)
        unit_bldg.active = not unit_bldg.active
        self.adjust_projected_unit_builds()

    def clear_unit_builds(self):
        for bldg in self.unit_buildings:
            bldg.active = False

    def adjust_projected_unit_builds(self):
        units_active = [u for u in self.unit_buildings if u.active]
        if len(units_active) == 0: return

        units_active.sort(key=lambda u: u.template.advancement_level())
        for bldg, bonus in zip(units_active, reversed(UNIT_BUILDING_BONUSES[len(units_active)])):
            bldg.production_rate = bonus

        total_metal = self.metal + self.projected_income['metal']
        for unit_building in units_active:
            # print(f"{self.name} projecting {unit_building.template} {total_metal}")
            unit_building.adjust_projected_unit_builds(total_metal=total_metal)

    def adjust_projected_builds(self, game_state):
        wood_available = self.wood + self.projected_income["wood"]
        costs = [entry.get_cost(game_state) for entry in self.buildings_queue]
        cumsum_cost = [sum(costs[:i + 1]) for i in range(len(costs))]
        self.projected_build_queue_depth = sum([c < wood_available for c in cumsum_cost])

        unit_buildings_to_bulldoze = max(0, self.num_buildings_of_type("unit", include_in_queue=True) - self.military_slots)
        if STRICT_MODE:
            assert unit_buildings_to_bulldoze <= self.num_buildings_of_type("unit", include_in_queue=True)
        targets = self.unit_buildings_ranked_for_bulldoze()
        for t in targets[:unit_buildings_to_bulldoze]:
            t.delete_queued = True
        for t in targets[unit_buildings_to_bulldoze:]:
            t.delete_queued = False

    def adjust_projected_yields(self, game_state: 'GameState') -> None:
        if self.hex is None:
            self.projected_income = Yields()
            self.projected_income_base = Yields()
            self.projected_income_focus = Yields()
        self.projected_income_base = self._get_projected_yields_without_focus(game_state)
        self.projected_income_focus = self._get_projected_yields_from_focus(game_state)
        self.food_demand: float = self._calculate_food_demand(game_state)

        self.projected_income = self.projected_income_base + {self.focus: self.projected_income_focus[self.focus]}
 
        self.projected_income.unhappiness = max(0, self.food_demand - self.projected_income.food)
        self.projected_income.city_power = max(0, self.projected_income.food - self.food_demand)

        if self.is_trade_hub():
            city_power_to_consume: float = min(
                TRADE_HUB_CITY_POWER_PER_TURN, 
                self.civ.city_power, 
                2 * (self.unhappiness + self.projected_income.unhappiness))
            self.projected_income.unhappiness -= 0.5 * city_power_to_consume
            self.projected_income.city_power -= city_power_to_consume

        # If I'm a puppet, give my yields to my parent.
        parent: City | None = self.get_territory_parent(game_state)
        if parent:
            assert self.hex is not None
            assert parent.hex is not None
            distance: int = self.hex.distance_to(parent.hex)
            distance_penalty: float = parent.puppet_distance_penalty() * distance
            parent.projected_income_puppets['wood'][self.name] = (self.projected_income.wood * (1 - distance_penalty), distance)
            parent.projected_income_puppets['metal'][self.name] = (self.projected_income.metal * (1 - distance_penalty), distance)
            parent.adjust_projected_yields(game_state)
        else:
            self.projected_income += {key: sum(amnt for amnt, distance in puppet_vals.values()) for key, puppet_vals in self.projected_income_puppets.items()}

    def _get_projected_yields_without_focus(self, game_state) -> Yields:
        yields = Yields(food=2, science=self.population)

        assert self.hex is not None

        for hex in self.hex.get_neighbors(game_state.hexes, include_self=True):
            yields += hex.yields

        for bldg in self.buildings:
            yields += bldg.calculate_yields(self, game_state)

        if self.civ.has_ability("IncreaseCapitalYields") and self.capital:
            resource, amount = self.civ.numbers_of_ability("IncreaseCapitalYields")
            yields += {resource: amount}

        return yields * self.civ.vitality

    def _get_projected_yields_from_focus(self, game_state) -> Yields:
        yields = Yields(metal=1, wood=1, science=1, food=1) * self.population

        if self.civ.has_ability('IncreaseFocusYields'):
            bonus_resource, count = self.civ.numbers_of_ability('IncreaseFocusYields')
            yields += {bonus_resource: count}
        for ability, _ in self.passive_building_abilities_of_name('IncreaseFocusYieldsPerPopulation'):
            focus, amount_per_pop = ability.numbers
            yields += {focus: amount_per_pop * self.population}

        return yields * self.civ.vitality

    def harvest_yields(self, game_state: 'GameState') -> None:
        self.adjust_projected_yields(game_state)  # TODO(dfarhi) this probably shouldn't be neessary since it should be called whenever the state changes?
        self.food += self.projected_income.food
        # Science and city power are harvested by the Civ instance.
        self.unhappiness += self.projected_income.unhappiness

        if self.is_territory_capital:
            self.wood += self.projected_income.wood
            self.metal += self.projected_income.metal
            if len(self.active_unit_buildings) > 0:
                for b in self.active_unit_buildings:
                    # print(f"{self.name} harvesting {b.template} {self.metal}")
                    b.harvest_yields(self.metal)
                self.metal = 0

    def update_nearby_hexes_visibility(self, game_state: 'GameState', short_sighted: bool = False) -> None:
        if self.hex is None:
            return
        # Always let cities have sight 2, even in decline mode (short_sighted = True)
        neighbors = self.hex.get_hexes_within_range(game_state.hexes, 2)

        for nearby_hex in neighbors:
            nearby_hex.visibility_by_civ[self.civ.id] = True

    def update_nearby_hexes_hostile_foundability(self, hexes: dict[str, 'Hex']) -> None:
        if self.hex is None:
            return

        for hex in self.hex.get_neighbors(hexes, include_self=True):
            for key in hex.is_foundable_by_civ:
                hex.is_foundable_by_civ[key] = False            

    def roll_turn_pre_harvest(self, game_state):
        """ All the turn roll stuff up to and including harvesting yields"""
        self.revolt_to_rebels_if_needed(game_state)
        self.harvest_yields(game_state)

    def roll_turn_post_harvest(self, sess, game_state: 'GameState', fake: bool = False) -> None:
        """
        All the turn roll stuff after harvest.
        They are split out so that we can make sure all cities harvest before any cities do stuff that could change another city's yields

        Fake: is this just a fake city for decline view?
        """
        if not fake:
            self.grow(game_state)
            if self.is_territory_capital:
                self.build_units(game_state)
                self.build_buildings(game_state)
            self.roll_wonders(game_state)
            self.handle_siege(sess, game_state)

        self.handle_unhappiness(game_state)
        self.midturn_update(game_state)

    def roll_wonders(self, game_state: 'GameState') -> None:
        for bldg in self.buildings:
            bldg.update_ruined_status(self, game_state)
            if not bldg.ruined:
                for effect in bldg.per_turn:
                    effect.apply(self, game_state)

    def age(self, game_state) -> int:
        assert self.founded_turn is not None, "Can't get age of a fake city."
        return game_state.turn_num - self.founded_turn

    def _calculate_food_demand(self, game_state: 'GameState') -> float:
        if self.founded_turn is None: return 0  # Not sure why we're even calculating this.
        result: float = 1.0 * self.age(game_state)
        if self.capital:
            result *= 0.25

        if self.is_territory_capital:
            result -= 2 * len(self.get_puppets(game_state))

        for ability, _ in self.civ.passive_building_abilities_of_name('DecreaseFoodDemand', game_state):
            result -= ability.numbers[1]
        for ability, _ in self.passive_building_abilities_of_name('DecreaseFoodDemand'):
            result -= ability.numbers[0] + ability.numbers[1]
        parent = self.get_territory_parent(game_state)
        if parent is not None:
            for ability, _ in parent.passive_building_abilities_of_name('DecreaseFoodDemandPuppets'):
                result -= ability.numbers[0]
        result = max(result, 0)
        return result

    def handle_unhappiness(self, game_state: 'GameState') -> None:
        if self.is_fake_city():
            self.revolting_starting_vitality = 1.0 + FRESH_CITY_VITALITY_PER_TURN * game_state.turn_num
        else:
            self.revolting_starting_vitality = 1.0 + REVOLT_VITALITY_PER_TURN * game_state.turn_num + REVOLT_VITALITY_PER_UNHAPPINESS * self.unhappiness

        if GOD_MODE:
            self.revolting_starting_vitality *= 10

    def revolt_to_rebels_if_needed(self, game_state: 'GameState') -> None:
        if self.unhappiness >= 100 and self.civ_to_revolt_into is not None and self.under_siege_by_civ is None:
            # Revolt to AI
            assert self.hex is not None
            game_state.process_decline_option(self.hex.coords, [], is_game_player=False)
            game_state.make_new_civ_from_the_ashes(self)
            # Rebel civs have no great person
            self.civ.great_people_choices = []

    def grow_inner(self, game_state: 'GameState') -> None:
        self.population += 1

    def grow(self, game_state: 'GameState') -> None:
        while self.food >= self.growth_cost():
            self.food -= self.growth_cost()
            self.grow_inner(game_state)

    def growth_cost(self) -> float:
        total_growth_cost_reduction = 0.0

        for ability, _ in self.passive_building_abilities_of_name('CityGrowthCostReduction'):
            total_growth_cost_reduction += ability.numbers[0]

        return (BASE_FOOD_COST_OF_POP + self.population * ADDITIONAL_PER_POP_FOOD_COST) * max(1 - total_growth_cost_reduction, 0.3)

    def handle_siege(self, sess, game_state: 'GameState') -> None:
        siege_state = self.get_siege_state(game_state)

        if self.under_siege_by_civ is None:
            self.under_siege_by_civ = siege_state
        else:
            if siege_state is None or siege_state.id != self.under_siege_by_civ.id:
                self.under_siege_by_civ = siege_state
            else:
                self.capture(sess, siege_state, game_state)

    def populate_terrains_dict(self, game_state: 'GameState') -> None:
        if self.hex is None:
            return

        for hex in self.hex.get_neighbors(game_state.hexes, include_self=True):
            if not hex.terrain in self.terrains_dict:
                self.terrains_dict[hex.terrain] = 1
            else:
                self.terrains_dict[hex.terrain] += 1

    def _refresh_available_buildings_and_units(self, game_state):
        if self.civ is None or self.hex is None:
            return
        self.available_units = sorted([unit for unit in UNITS.all() if unit.building_name is None or self.has_production_building_for_unit(unit)])
        
        min_level = min([u.advancement_level() for u in self.available_units])
        self.available_unit_buildings: list[UnitTemplate] = sorted([u for u in self.civ.available_unit_buildings if u.advancement_level() >= min_level and not self.has_building(u)], reverse=True)
        self.available_wonders: list[WonderTemplate] = sorted(game_state.available_wonders())
        self.available_city_buildings = self.civ.available_city_buildings

        self._update_city_building_descriptions()

        # Remove totally useless ones
        self.available_city_buildings = [b for b in self.available_city_buildings if not (b.useless_if_zero_yields and b.name not in self.building_yields)]

        self.available_city_buildings.sort(key=lambda b: (
            -self.building_yields[b.name].total() if b.name in self.building_yields else 0,
            b.name
        ))

        # Validate queue
        self.buildings_queue = [entry for entry in self.buildings_queue if 
                                entry.template in self.available_city_buildings + self.available_unit_buildings + self.available_wonders]

    def calculate_payoff_time(self, yields, cost) -> int:
        if yields == 0:
            return 99
        # How much will it produce next turn?
        actual_yields = yields * (self.civ.vitality * VITALITY_DECAY_RATE)
        yield_to_cost_ratio = actual_yields / cost
        # need to find time t such that 1 = yield_to_cost_ratio * (1 - VITALITY_DECAY_RATE ^ t) / (1 - VITALITY_DECAY_RATE)
        payoff_vitality = 1 - (1 - VITALITY_DECAY_RATE) / yield_to_cost_ratio
        if payoff_vitality <= 0:
            return 99
        payoff_turns = math.ceil(math.log(payoff_vitality, VITALITY_DECAY_RATE))
        # Add 1 to account for the first turn (when it makes no yields since we're building it).
        payoff_turns += 1
        return payoff_turns

    def _update_city_building_descriptions(self) -> None:
        for building_template in self.available_city_buildings + [b._template for b in self.buildings_of_type("rural") + self.buildings_of_type("urban")]:
            assert isinstance(building_template, BuildingTemplate)
            total_pseudoyields: float = 0
            is_economic_building = False
            building_yields = building_template.calculate_yields.calculate(self) if building_template.calculate_yields is not None else Yields()

            for ability in building_template.abilities:
                if ability.name == "IncreaseFocusYieldsPerPopulation":
                    is_economic_building = True
                    resource: str = ability.numbers[0]
                    amount: int = ability.numbers[1]
                    building_yields += Yields(**{resource: self.population * amount})

                if ability.name == "CityGrowthCostReduction":
                    is_economic_building = True
                    ratio = ability.numbers[0]
                    effective_income_multiplier = 1 / ratio
                    effective_income_bonus = self.projected_income_base['food'] * (effective_income_multiplier - 1)
                    total_pseudoyields += int(effective_income_bonus / self.civ.vitality)

                if ability.name == "DecreaseFoodDemand":
                    unhappiness_saved: float = min(ability.numbers[0], self.food_demand)
                    building_yields.unhappiness = unhappiness_saved

                    # Decide how much AI cares
                    if self.civ_to_revolt_into is not None:
                        # Count the unhappiness as full resources
                        pass
                    elif self.unhappiness == 0 and self.projected_income["unhappiness"] == 0:
                        # This ability is pretty useless if there's no unhappiness, cancel out its yields
                        total_pseudoyields -= unhappiness_saved
                    else:
                        # Count the unhappiness as half resources
                        total_pseudoyields -= 0.5 * unhappiness_saved

                if ability.name == "ReducePuppetDistancePenalty":
                    building_yields += {
                        resource: sum(
                            amount / (1 - self.puppet_distance_penalty() * distance) * (self.puppet_distance_penalty() - ability.numbers[0]) * distance
                            for amount, distance in puppet_infos.values()
                        )
                        for resource, puppet_infos in self.projected_income_puppets.items()}
                    
            total_yields = building_yields.total()
            is_economic_building = total_yields > 0 or is_economic_building
            if building_template.vp_reward is not None and building_template.vp_reward > 0:
                self.available_buildings_to_descriptions[building_template.name] = {
                    "type": "vp",
                    "value": building_template.vp_reward,
                    "value_for_ai": building_template.vp_reward * 3 + total_yields + total_pseudoyields,
                }

            elif is_economic_building:
                self.available_buildings_to_descriptions[building_template.name] = {
                    "type": "yield",
                    "value": total_yields,
                    "value_for_ai": total_yields + total_pseudoyields,
                }
            
            else:
                self.available_buildings_to_descriptions[building_template.name] = {
                    "type": "???",
                    "value": 0,
                }

            if building_yields.total() > 0:
                self.building_yields[building_template.name] = building_yields
                self.available_buildings_payoff_times[building_template.name] = self.calculate_payoff_time(building_yields.total(), building_template.cost)
            else:
                if building_template.name in self.building_yields:
                    del self.building_yields[building_template.name]

    def has_production_building_for_unit(self, unit: UnitTemplate) -> bool:
        return self.has_building(unit)

    @property
    def active_unit_buildings(self):
        return [u for u in self.unit_buildings if u.active]

    def build_units(self, game_state: 'GameState') -> None:
        build_dict = {u: u.projected_unit_count for u in self.active_unit_buildings}
        max_units = max(build_dict.values()) if len(build_dict) > 0 else 0
        # Interleave them for better diversity
        for i in range(max_units):
            for bldg, target_num in build_dict.items():
                if i < target_num:
                    print(f"{self.name} building {bldg.template.name} {i}/{target_num}, has {bldg.metal}")
                    if self.build_unit(game_state, bldg.template) is not None:
                        bldg.metal -= bldg.template.metal_cost

    def get_closest_target(self) -> Optional['Hex']:
        if not self.hex:
            return None

        target1 = self.civ.target1
        target2 = self.civ.target2

        if target1 is None and target2 is None:
            return None
        
        if target1 is None:
            return target2
        
        if target2 is None:
            return target1
        
        if self.hex.distance_to(target1) <= self.hex.distance_to(target2):
            return target1
        else:
            return target2


    def build_unit(self, game_state: 'GameState', unit: UnitTemplate, give_up_if_still_impossible: bool = False, stack_size=1) -> Unit | None:
        if not self.hex:
            return None
        
        spawn_hex = self.hex
        for _ in self.passive_building_abilities_of_name('Deployment Center'):
            spawn_hex = self.civ.target1 if self.civ.target1 is not None else spawn_hex

        if not spawn_hex.is_occupied(unit.type, self.civ, allow_enemy_city=False):
            return self.spawn_unit_on_hex(game_state, unit, spawn_hex, stack_size=stack_size)

        best_hex = None
        best_hex_distance_from_target = 10000

        for hex in spawn_hex.get_neighbors(game_state.hexes):
            if not hex.is_occupied(unit.type, self.civ, allow_enemy_city=False):    
                distance_from_target = hex.distance_to(self.get_closest_target() or spawn_hex)
                if distance_from_target < best_hex_distance_from_target:
                    best_hex = hex
                    best_hex_distance_from_target = distance_from_target

        best_unit_to_reinforce = None
        if best_hex is None:

            best_unit_penalty = 10000          
            for hex in spawn_hex.get_neighbors(game_state.hexes, include_self=True):
                if hex.is_occupied(unit.type, self.civ, allow_enemy_city=False):
                    unit_to_possibly_reinforce = hex.units[0]
                    if unit_to_possibly_reinforce.civ.id == self.civ.id and unit_to_possibly_reinforce.template.name == unit.name and unit_to_possibly_reinforce.hex:
                        unit_penalty = unit_to_possibly_reinforce.health * 10 + unit_to_possibly_reinforce.hex.distance_to(self.get_closest_target() or spawn_hex)
                        if unit_penalty < best_unit_penalty:
                            best_unit_to_reinforce = unit_to_possibly_reinforce
                            best_unit_penalty = unit_penalty            

        if best_hex is None:
            if best_unit_to_reinforce:
                self.reinforce_unit(best_unit_to_reinforce, stack_size=stack_size)
                return best_unit_to_reinforce
            
            else:
                if give_up_if_still_impossible:
                    return None
                num_merges = 0

                # Try merging friendly units
                for hex in spawn_hex.get_neighbors(game_state.hexes, include_self=True):
                    if hex.units and hex.units[0].civ.id == self.civ.id:
                        if hex.units[0].merge_into_neighboring_unit(None, game_state, always_merge_if_possible=True):
                            num_merges += 1
                    if num_merges >= 2:
                        break

                # If that doesn't work, try merging enemy units, so long as they aren't on the city itself
                if num_merges == 0:
                    for hex in spawn_hex.get_neighbors(game_state.hexes, include_self=True):
                        if hex.units and not hex.city:
                            if hex.units[0].merge_into_neighboring_unit(None, game_state, always_merge_if_possible=True):
                                num_merges += 1
                                break
                        if num_merges >= 2:
                            break

                # If that doesn't work, and we have a lot of metal to spend, try removing friendly units altogether
                if num_merges == 0 and self.metal > 75:
                    for hex in spawn_hex.get_neighbors(game_state.hexes, include_self=True):
                        if hex.units and hex.units[0].civ.id == self.civ.id and hex.units[0].health < 300:
                            hex.units[0].remove_from_game(game_state)
                            break

                return self.build_unit(game_state, unit, give_up_if_still_impossible=True, stack_size=stack_size)

        return self.spawn_unit_on_hex(game_state, unit, best_hex, stack_size=stack_size)

    def spawn_unit_on_hex(self, game_state: 'GameState', unit_template: UnitTemplate, hex: 'Hex', stack_size=1) -> Unit | None:
        unit = Unit(unit_template, self.civ)
        unit.health *= stack_size
        unit.hex = hex
        hex.units.append(unit)
        game_state.units.append(unit)

        if self.civ.has_ability('IncreasedStrengthForUnit'):
            if self.civ.numbers_of_ability('IncreasedStrengthForUnit')[0] == unit_template.name:
                unit.strength += self.civ.numbers_of_ability('IncreasedStrengthForUnit')[1]

        for ability, _ in self.civ.passive_building_abilities_of_name('NewUnitsGainBonusStrength', game_state):
            unit.strength += ability.numbers[0]

        for ability, _ in self.passive_building_abilities_of_name('UnitsExtraStrengthByTag'):
            if unit.template.has_tag(ability.numbers[0]):
                unit.strength += ability.numbers[1]
        for ability, _ in self.passive_building_abilities_of_name('UnitsExtraStrengthByAge'):
            if unit.template.advancement_level() >= ability.numbers[0]:
                unit.strength += ability.numbers[1]

        return unit

    def reinforce_unit(self, unit: Unit, stack_size=1) -> None:
        unit.health += 100 * stack_size

    def validate_building_queueable(self, building_template: UnitTemplate | BuildingTemplate | WonderTemplate) -> bool:
        if self.has_building(building_template):
            return False
        if isinstance(building_template, UnitTemplate):
            if building_template not in self.available_unit_buildings:
                return False
        if isinstance(building_template, BuildingTemplate):
            if building_template not in self.available_city_buildings:
                return False
            if building_template.type == BuildingType.URBAN and self.urban_slots <= self.num_buildings_of_type("urban", include_in_queue=True):
                return False
            if building_template.type == BuildingType.RURAL and self.rural_slots <= self.num_buildings_of_type("rural", include_in_queue=True):
                return False
        if isinstance(building_template, WonderTemplate):
            if building_template not in self.available_wonders:
                return False
        return True

    def build_buildings(self, game_state: 'GameState') -> None:
        while self.buildings_queue:
            entry = self.buildings_queue[0]
            building: UnitTemplate | BuildingTemplate | WonderTemplate = entry.template
            cost = entry.get_cost(game_state)
            if self.wood >= cost:
                self.buildings_queue.pop(0)
                self.build_building(game_state, building)
                self.wood -= cost
            else:
                break

    def buildings_of_type(self, type: Literal["rural", "urban", "wonder"]) -> list[Building]:
        return [b for b in self.buildings if b.type == type]

    def num_buildings_of_type(self, type: Literal['wonder', 'unit', 'rural', 'urban'], include_in_queue=False):
        def type_from_template(t: WonderTemplate | UnitTemplate | BuildingTemplate) -> Literal['wonder', 'unit', 'rural', 'urban']:
            if isinstance(t, WonderTemplate): return "wonder"
            if isinstance(t, UnitTemplate): return "unit"
            if isinstance(t, BuildingTemplate): return t.type.value
        if type == "unit":
            bldgs = len(self.unit_buildings)
        else:
            bldgs = len(self.buildings_of_type(type))
        if include_in_queue:
            bldgs += len([b for b in self.buildings_queue if type_from_template(b.template) == type])
        return bldgs

    @property
    def can_expand(self):
        return (self.civ.id not in self.expanded_by_civ_ids) \
            and self.num_buildings_of_type("rural", include_in_queue=False) >= self.rural_slots \
            and self.military_slots + self.urban_slots + self.rural_slots < MAX_SLOTS \
            and self.civ.game_player is not None

    def expand(self, game_state):
        # TODO merge this with _develop()
        if STRICT_MODE:
            assert self.can_expand
        self.rural_slots += 1
        self.expanded_by_civ_ids.append(self.civ.id)
        self.civ.city_power -= DEVELOP_COST['rural']
        self.civ.gain_vps(DEVELOP_VPS, _DEVELOPMENT_VPS_STR)
        if self.civ.has_ability("OnDevelop"):
            civ_type, effect = self.civ.numbers_of_ability("OnDevelop")
            if civ_type == 'rural':
                effect.apply(self, game_state)

    def _can_develop(self, type: Literal['unit', 'urban']):
        if self.civ.develop_used[type]:
            return False
        slots_of_type = self.urban_slots if type == 'urban' else self.military_slots
        if self.num_buildings_of_type(type, include_in_queue=False) < slots_of_type:
            return False
        if slots_of_type == MAX_SLOTS_OF_TYPE[type]:
            return False
        if self.num_buildings_of_type("rural", include_in_queue=True) == self.rural_slots:
            return False
        if self.civ.game_player is None:
            return False
        if not self.is_territory_capital:
            return False
        return True

    @property
    def can_urbanize(self):
        return self._can_develop('urban')
    @property
    def can_militarize(self):
        return self._can_develop('unit')
    
    def _develop(self, type: Literal['urban', 'unit'], game_state):
        if STRICT_MODE:
            assert self._can_develop(type)
        self.rural_slots -= 1
        if type == 'urban':
            self.urban_slots += 1
        if type == 'unit':
            self.military_slots += 1
        print(f"=========================== {self.military_slots} {type}")
        self.civ.develop_used[type] = True
        self.civ.city_power -= DEVELOP_COST[type]
        self.civ.gain_vps(DEVELOP_VPS, _DEVELOPMENT_VPS_STR)    
        if self.civ.has_ability("OnDevelop"):
            civ_type, effect = self.civ.numbers_of_ability("OnDevelop")
            if civ_type == type:
                effect.apply(self, game_state)
    
    def urbanize(self, game_state):
        self._develop('urban', game_state)

    def militarize(self, game_state):
        self._develop('unit', game_state)

    def unit_buildings_ranked_for_bulldoze(self) -> list[UnitBuilding]:
        targets = self.unit_buildings.copy()
        targets.sort(key=lambda b: b.template.advancement_level())
        return targets

    def building_in_queue(self, template) -> bool:
        return any(b.template == template for b in self.buildings_queue)

    def enqueue_build(self, template: Union[BuildingTemplate, UnitTemplate, WonderTemplate]) -> None:
        print(f"enqueuing {template}")
        if STRICT_MODE:
            assert self.is_territory_capital, f"{self.name} tried to enqueue a building while a puppet"
            assert not self.has_building(template), (template, self.buildings_queue, self.building_in_queue(template))
        order = QueueEntry(template)
        self.buildings_queue.append(order)

    def build_building(self, game_state: 'GameState', building: Union[BuildingTemplate, UnitTemplate, WonderTemplate], free: bool = False) -> None:
        if isinstance(building, UnitTemplate):
            new_building = UnitBuilding(building)
            self.unit_buildings.append(new_building)
            if len(self.unit_buildings) > self.military_slots:
                bulldoze: UnitBuilding = self.unit_buildings_ranked_for_bulldoze()[0]
                self.unit_buildings = [b for b in self.unit_buildings if b != bulldoze]
                self.metal += bulldoze.metal
            self.clear_unit_builds()
            self._refresh_available_buildings_and_units(game_state)
            self.toggle_unit_build(building)
        
        else:
            new_building = Building(building)
            self.buildings.append(new_building)
            if new_building.vp_reward > 0:
                self.civ.gain_vps(new_building.vp_reward, "Buildings and Wonders")

            for effect in new_building.on_build:
                effect.apply(self, game_state)

            if isinstance(building, WonderTemplate):
                game_state.handle_wonder_built(self, building)

        if new_building.one_per_civ_key and not free:
            if self.civ.id not in game_state.one_per_civs_built_by_civ_id:
                game_state.one_per_civs_built_by_civ_id[self.civ.id] = {new_building.one_per_civ_key: self.id}
            else:
                game_state.one_per_civs_built_by_civ_id[self.civ.id][new_building.one_per_civ_key] = self.id

            # Clear it from any other cities immediately; you can't build two in one turn.
            for city in self.civ.get_my_cities(game_state):
                city.buildings_queue = [b for b in city.buildings_queue if b.template != building]

    def get_siege_state(self, game_state: 'GameState') -> Optional[Civ]:
        if self.hex is None:
            return None

        for unit in self.hex.units:
            if unit.civ.id != self.civ.id and unit.template.type == 'military':
                return unit.civ

        return None
    
    def passive_building_abilities_of_name(self, ability_name: str) -> Generator[tuple['Ability', 'Building'], None, None]:
        for building in self.buildings:
            for ability in building.passive_building_abilities_of_name(ability_name):
                yield ability, building

    def change_owner(self, civ: Civ, game_state: 'GameState') -> None:
        """
        Called when an existing city changes owner; called by capture() and process_decline_option().
        """
        # Remove trade hub
        if self.is_trade_hub():
            self.civ.trade_hub_id = None

        for building in self.buildings:
            if building.one_per_civ_key and game_state.one_per_civs_built_by_civ_id.get(self.civ.id, {}).get(building.building_name) == self.id:
                del game_state.one_per_civs_built_by_civ_id[self.civ.id][building.building_name]
        self.buildings = [b for b in self.buildings if not b.destroy_on_owner_change]

        # Change the civ
        self.civ = civ

        # Fix territory parent lines
        self.orphan_territory_children(game_state)
        self.set_territory_parent_if_needed(game_state, adopt_focus=True)

        # Reset various properties
        self.under_siege_by_civ = None
        self.buildings_queue = []
        self.clear_unit_builds()
        self.ever_controlled_by_civ_ids[civ.id] = True

        # Update available stuff
        self.midturn_update(game_state)

    def barbarian_capture(self, game_state: 'GameState') -> None:
        """Barbarians replace the city with a camp."""
        
        # Call change_owner to do the cleanup on the previous civ ownership
        self.change_owner(game_state.barbarians, game_state)

        best_unit: UnitTemplate = max(self.available_units, key=lambda x: (x.advancement_level(), random.random()))

        assert self.hex and self.hex.city

        # Also build a handful of units out of the ruins of the city
        for u in self.available_units:
            self.hex.city.build_unit(game_state, u)

        self.hex.city = None
        game_state.register_camp(Camp(game_state.barbarians, unit=best_unit), self.hex)

        del game_state.cities_by_id[self.id]

    def capture(self, sess, civ: Civ, game_state: 'GameState') -> None:
        if civ == game_state.barbarians:
            self.barbarian_capture(game_state)
            return

        print(f"****Captured {self.name}****")
        self.capital = False
        self.unhappiness = 0
        self.wood = 0
        self.metal = 0

        if civ.id not in self.ever_controlled_by_civ_ids:
            civ.gain_vps(CITY_CAPTURE_REWARD, "City Capture (5/city)")

            if civ.has_ability('ExtraVpsPerCityCaptured'):
                civ.gain_vps(civ.numbers_of_ability('ExtraVpsPerCityCaptured')[0], civ.template.name)

            for ability, building in civ.passive_building_abilities_of_name("ExtraVpsForCityCapture", game_state):
                amount = ability.numbers[0]
                civ.gain_vps(amount, building.building_name)

        self.change_owner(civ, game_state)

        if self.hex:
            game_state.add_animation_frame(sess, {
                "type": "CityCapture",
                "civ": civ.template.name,
                "city": self.name,
                "vpReward": CITY_CAPTURE_REWARD,
            }, hexes_must_be_visible=[self.hex])

    def capitalize(self, game_state: 'GameState') -> None:
        civ = self.civ
        self.capital = True
                
        if civ.has_ability('StartWithResources'):
            if civ.numbers_of_ability('StartWithResources')[0] == 'food':
                self.food += civ.numbers_of_ability('StartWithResources')[1]
                self.civ.city_power += civ.numbers_of_ability('StartWithResources')[1]

            if civ.numbers_of_ability('StartWithResources')[0] == 'metal':
                self.metal += civ.numbers_of_ability('StartWithResources')[1]

            if civ.numbers_of_ability('StartWithResources')[0] == 'wood':
                self.wood += civ.numbers_of_ability('StartWithResources')[1]
            
            if civ.numbers_of_ability('StartWithResources')[0] == 'science':
                self.civ.science += civ.numbers_of_ability('StartWithResources')[1]

                
    def update_civ_by_id(self, civs_by_id: dict[str, Civ]) -> None:
        self.civ = civs_by_id[self.civ_id]
        self.under_siege_by_civ = civs_by_id[self.under_siege_by_civ] if self.under_siege_by_civ else None  # type: ignore

    def bot_pick_wonder(self, choices: list[WonderTemplate], game_state: 'GameState') -> Optional[WonderTemplate]:
        affordable_ages: set[int] = {age for age in game_state.wonders_by_age.keys() if game_state.wonder_cost_by_age[age] <= self.wood + self.projected_income['wood']}
        affordable_choices: list[WonderTemplate] = [choice for choice in choices if choice.age in affordable_ages]
        if len(affordable_choices) == 0:
            return None
        # Build the highest age one we can afford
        return max(affordable_choices, key=lambda x: (x.age, random.random()))

    def bot_pick_economic_building(self, choices: list[BuildingTemplate], remaining_wood: float) -> Optional[BuildingTemplate]:
        if self.num_buildings_of_type("rural", include_in_queue=True) >= self.rural_slots:
            choices = [b for b in choices if b.type != BuildingType.RURAL]
        if self.num_buildings_of_type("urban", include_in_queue=True) >= self.urban_slots:
            choices = [b for b in choices if b.type != BuildingType.URBAN]

        # Don't build libraries
        if self.civ.get_advancement_level() > 2:
            choices = [b for b in choices if b != BUILDINGS.LIBRARY]
        # Don't build husbandry centers by themself
        if self.focus != "food" and self.urban_slots < 2:
            choices = [b for b in choices if b != BUILDINGS.HUSBANDRY_CENTER]
        # Only one of these per city
        if any([len(building.passive_building_abilities_of_name("IncreaseFocusYieldsPerPopulation")) > 0 for building in self.buildings]):
            choices = [b for b in choices if not any (a.name == "IncreaseFocusYieldsPerPopulation" for a in b.abilities)]

        if len(choices) > 0:
            ACCEPTABLE_PAYOFF_TURNS = 6
            payoff_turns: dict[BuildingTemplate, float] = {
                building: self.calculate_payoff_time(yields=self.available_buildings_to_descriptions[building.name].get('value_for_ai', 0), cost=building.cost)
                for building in choices
                if building.name in self.available_buildings_to_descriptions and 'value_for_ai' in self.available_buildings_to_descriptions[building.name]
            }
            if len(payoff_turns) > 0:
                # calulcate the argmin of the payoff turns
                best_building = min(payoff_turns, key=lambda x: (x.cost > remaining_wood, payoff_turns.get(x, 99), -x.cost))
                if payoff_turns[best_building] < ACCEPTABLE_PAYOFF_TURNS:
                    return best_building

        return None

    def is_threatened_city(self, game_state: 'GameState') -> bool:
        assert self.hex is not None
        return self.hex.is_threatened_city(game_state)

    def bot_move(self, game_state: 'GameState') -> None:
        def effective_advancement_level(unit: UnitTemplate, slingers_better_than_warriors=False) -> float:
            # treat my civ's unique unit as +1 adv level.
            if self.civ.has_ability('IncreasedStrengthForUnit'):
                special_unit_name = self.civ.numbers_of_ability('IncreasedStrengthForUnit')[0]
                if unit.name == special_unit_name:
                    return unit.advancement_level() + 1
            if unit == UNITS.SLINGER and slingers_better_than_warriors:
                return 0.5
            return unit.advancement_level()

        print(f"{self.name} -- City planning AI move.")
        self.midturn_update(game_state)
        if self.can_urbanize and random.random() < AI.CHANCE_URBANIZE:
            self.urbanize(game_state)
        if self.can_militarize and random.random() < AI.CHANCE_MILITARIZE:
            self.militarize(game_state)
        if self.can_expand and random.random() < AI.CHANCE_EXPAND:
            self.expand(game_state)
        self.midturn_update(game_state)

        # Don't build stationary units
        available_units = [unit for unit in self.available_units if unit.movement > 0]
        highest_level = max([effective_advancement_level(unit, slingers_better_than_warriors=True) for unit in available_units])
        self.clear_unit_builds()
        if highest_level < self.civ.get_advancement_level() - 2 and not self.is_threatened_city(game_state):
            print(f"  not building units because the best I can built is level {highest_level} units and I'm at tech level {self.civ.get_advancement_level()}")
        elif highest_level < self.civ.get_advancement_level() - 4:
            print(f"  not building units even though threatened, because the best I can built is level {highest_level} units and I'm at tech level {self.civ.get_advancement_level()}")
        else:
            high_tier_units = [unit for unit in available_units if effective_advancement_level(unit, slingers_better_than_warriors=True) >= highest_level - 1]
            for u in high_tier_units:
                self.toggle_unit_build(u)

        # Never steal from another city's queue
        wonders: list[WonderTemplate] = [w for w in self.available_wonders if w.name not in self.civ.buildings_in_all_queues]
        economic_buildings: list[BuildingTemplate] = [b for b in self.available_city_buildings if b.name not in self.civ.buildings_in_all_queues]
        military_buildings: list[UnitTemplate] = [u for u in self.available_unit_buildings if u.movement > 0 and u.name not in self.civ.buildings_in_all_queues]

        lotsa_wood: bool = self.projected_income_base['wood'] > self.projected_income_base['metal'] * 2
        if len(military_buildings) > 0:
            # Choose buildings first by effective advancement level, then randomly
            best_military_building = max(military_buildings, key=lambda building: (
                effective_advancement_level(building, slingers_better_than_warriors=lotsa_wood), 
                random.random()
                ))
            best_military_building_age = effective_advancement_level(best_military_building, slingers_better_than_warriors=lotsa_wood)
        else:
            best_military_building = None
            best_military_building_age = -1
        
        remaining_wood_budget = self.wood + self.projected_income['wood']
        best_current_available_unit_age = max([effective_advancement_level(u, slingers_better_than_warriors=lotsa_wood) for u in self.available_units]) if len(self.available_units) > 0 else -1
        if best_military_building is not None \
                and best_military_building_age > best_current_available_unit_age \
                and remaining_wood_budget > best_military_building.wood_cost:
            self.buildings_queue = []
            self.enqueue_build(best_military_building)
            print(f"  overwrote building queue because of new military unit (lvl {effective_advancement_level(best_military_building, slingers_better_than_warriors=lotsa_wood)}): {self.buildings_queue}")
            if not self.is_threatened_city(game_state):
                print(f"  not building units to wait for new military building.")
                self.clear_unit_builds()
        while len(wonders) > 0 and (wonder_choice := self.bot_pick_wonder(wonders, game_state)) is not None and remaining_wood_budget > (cost := game_state.wonder_cost_by_age[wonder_choice.age]):
            self.enqueue_build(wonder_choice)
            wonders.remove(wonder_choice)
            remaining_wood_budget -= cost
            print(f"  adding wonder to buildings queue: {self.buildings_queue}")
        while len(economic_buildings) > 0 and (choice := self.bot_pick_economic_building(economic_buildings, remaining_wood_budget)) is not None and remaining_wood_budget > choice.cost:
            self.enqueue_build(choice)
            economic_buildings.remove(choice)
            remaining_wood_budget -= choice.cost
            print(f"  adding economic building to buildings queue: {self.buildings_queue}")
        
        i_want_wood = len([b for b in economic_buildings if b.type == BuildingType.URBAN and b.cost > remaining_wood_budget]) > 0
        self.bot_choose_focus(game_state, parent_wants_wood=i_want_wood)
        for city in self.get_puppets(game_state):
            city.bot_choose_focus(game_state, parent_wants_wood=i_want_wood)
        game_state.midturn_update()

    def bot_choose_focus(self, game_state, parent_wants_wood: bool):
        if self.civ_to_revolt_into is not None or self.unhappiness + self.projected_income['unhappiness'] > game_state.unhappiness_threshold:
            self.focus = 'food'
            print(f"  chose focus: {self.focus} to prevent revolt")
            return
        parent = self.get_territory_parent(game_state)
        production_city: City = self if parent is None else parent

        plausible_focuses = {"food", "wood", "metal", "science"}
        if self.growth_cost() >= 30:
            # At some point it's time to use our pop
            plausible_focuses.remove('food')
        if self.civ.researching_tech is None:
            plausible_focuses.remove('science')
        if production_city.wood >= 150:
            plausible_focuses.remove('wood')
            
        max_yields = max(self.projected_income_focus[focus] for focus in plausible_focuses)
        focuses_with_best_yields = [focus for focus in plausible_focuses if max_yields - self.projected_income_focus[focus] < 2]
        if len(production_city.active_unit_buildings) > 0 and 'metal' in focuses_with_best_yields and production_city.is_threatened_city(game_state):
            self.focus = 'metal'
        elif 'wood' in focuses_with_best_yields and self.num_buildings_of_type("urban", include_in_queue=True) < production_city.urban_slots and parent_wants_wood:
            self.focus = 'wood'
        else:
            self.focus = random.choice(list(focuses_with_best_yields))

        print(f"  chose focus: {self.focus} (max yield choices were {focuses_with_best_yields})")

    def to_json(self, include_civ_details: bool = False) -> dict:
        return {
            "id": self.id,
            "civ_id": self.civ.id,
            **({"civ": self.civ.to_json()} if include_civ_details else {}),
            "ever_controlled_by_civ_ids": self.ever_controlled_by_civ_ids,
            "name": self.name,
            "population": self.population,
            "food": self.food,
            "metal": self.metal,
            "wood": self.wood,
            "focus": self.focus,
            "rural_slots": self.rural_slots,
            "urban_slots": self.urban_slots,
            "military_slots": self.military_slots,
            "under_siege_by_civ_id": self.under_siege_by_civ.id if self.under_siege_by_civ else None,
            "hex": self.hex.coords if self.hex else None,
            "icon_unit_name": sorted(self.active_unit_buildings, key=lambda u: u.template.advancement_level(), reverse=True)[0].template.name if len(self.active_unit_buildings) > 0 else None,
            "buildings_queue": [building.to_json() for building in self.buildings_queue],
            "buildings": [building.to_json() for building in self.buildings],
            "unit_buildings": [building.to_json() for building in self.unit_buildings],
            "available_buildings_to_descriptions": self.available_buildings_to_descriptions.copy(),
            "available_buildings_payoff_times": self.available_buildings_payoff_times,
            "building_yields": {name: yields.to_json() for name, yields in self.building_yields.items()},
            "available_wonders": [w.name for w in self.available_wonders if not self.building_in_queue(w)],
            "available_unit_building_names": [template.name for template in self.available_unit_buildings if not self.building_in_queue(template)],
            "available_urban_building_names": [template.name for template in self.available_city_buildings if not self.building_in_queue(template) and template.type==BuildingType.URBAN],
            "available_rural_building_names": [template.name for template in self.available_city_buildings if not self.building_in_queue(template) and template.type==BuildingType.RURAL],
            "building_slots_full": {
                "rural": self.num_buildings_of_type("rural", include_in_queue=True) >= self.rural_slots,
                "urban": self.num_buildings_of_type("urban", include_in_queue=True) >= self.urban_slots,
                "military": self.num_buildings_of_type("unit", include_in_queue=True) >= self.military_slots,
            },
            "capital": self.capital,
            "available_units": [u.name for u in self.available_units],
            "projected_income": self.projected_income.to_json(),
            "projected_income_base": self.projected_income_base.to_json(),
            "projected_income_focus": self.projected_income_focus.to_json(),
            "projected_income_puppets": self.projected_income_puppets,
            "projected_build_queue_depth": self.projected_build_queue_depth,
            "max_units_in_build_queue": self.military_slots <= len([entry for entry in self.buildings_queue if isinstance(entry.template, UnitTemplate)]),
            "growth_cost": self.growth_cost(),
            "terrains_dict": {terrain.name: count for terrain, count in self.terrains_dict.items()},
            "expanded_by_civ_ids": self.expanded_by_civ_ids,
            "can_expand": self.can_expand,
            "can_militarize": self.can_militarize,
            "can_urbanize": self.can_urbanize,

            "territory_parent_id": self._territory_parent_id,
            "territory_parent_coords": self._territory_parent_coords,

            "revolting_starting_vitality": self.revolting_starting_vitality,
            "unhappiness": self.unhappiness,
            "civ_to_revolt_into": self.civ_to_revolt_into.name if self.civ_to_revolt_into else None,
            "is_decline_view_option": self.is_decline_view_option,
            "food_demand": self.food_demand,
            "revolt_unit_count": self.revolt_unit_count,
            "founded_turn": self.founded_turn,

            "is_trade_hub": self.is_trade_hub(),
        }

    @staticmethod
    def from_json(json: dict) -> "City":
        city = City(
            civ=Civ.from_json(json.get('civ')) if 'civ' in json else None,  # type: ignore
            name=json["name"],
        )
        city.id = json["id"]
        city.civ_id = json["civ_id"]
        city.ever_controlled_by_civ_ids = json["ever_controlled_by_civ_ids"].copy()
        city.population = json["population"]
        city.buildings = [Building.from_json(building) for building in json["buildings"]]
        city.unit_buildings = [UnitBuilding.from_json(building) for building in json["unit_buildings"]]
        city.food = json["food"]
        city.metal = json["metal"]
        city.wood = json["wood"]
        city.rural_slots = json["rural_slots"]
        city.urban_slots = json["urban_slots"]
        city.military_slots = json["military_slots"]
        city.under_siege_by_civ = json["under_siege_by_civ_id"]
        city.capital = json["capital"]
        city.buildings_queue = [QueueEntry.from_json(entry) for entry in json["buildings_queue"]]
        city.available_buildings_to_descriptions = (json.get("available_buildings_to_descriptions") or {}).copy()
        city.available_buildings_payoff_times = json["available_buildings_payoff_times"]
        city.building_yields = {name: Yields(**yields) for name, yields in json["building_yields"].items()}
        city.available_units = [UNITS.by_name(unit) for unit in json["available_units"]]
        city.focus = json["focus"]
        city.projected_income = Yields(**json["projected_income"])
        city.projected_income_base = Yields(**json["projected_income_base"])
        city.projected_income_focus = Yields(**json["projected_income_focus"])
        city.projected_build_queue_depth = json["projected_build_queue_depth"]
        city.terrains_dict = {TERRAINS.by_name(terrain): count for terrain, count in json["terrains_dict"].items()}
        city.expanded_by_civ_ids = json["expanded_by_civ_ids"]
        city.civ_to_revolt_into = CIVS.by_name(json["civ_to_revolt_into"]) if json["civ_to_revolt_into"] else None
        city.revolting_starting_vitality = json["revolting_starting_vitality"]
        city.unhappiness = json["unhappiness"]
        city.is_decline_view_option = json["is_decline_view_option"]
        city.revolt_unit_count = json["revolt_unit_count"]
        city._territory_parent_id = json["territory_parent_id"]
        city._territory_parent_coords = json["territory_parent_coords"]
        city.founded_turn = json["founded_turn"]

        return city

    def from_json_postprocess(self, game_state: 'GameState'):
        self.under_siege_by_civ = game_state.civs_by_id[self.under_siege_by_civ] if self.under_siege_by_civ else None  # type: ignore
        self.midturn_update(game_state)

CITY_NAMES = {
    "Miami",
    "Lothlorien",
    "Leningrad",
    "Los Angeles",
    "Tikal",
    "Karakorum",
    "Khartoum",
    "Ravnica",
    "Tokyo",
    "Delhi",
    "Berkeley",
    "Munich",
    "Qarth",
    "Cuzco",
    "Meereen",
    "New Capenna",
    "The Hive",
    "Nairobi",
    "Barcelona",
    "Toronto",
    "Coruscant",
    "Zigatvar",
    "Wuhan",
    "Cape Town",
    "Tel Aviv",
    "Sunspear",
    "Moscow",
    "Osgiliath",
    "Oldtown",
    "Bern",
    "Lannisport",
    "Nineveh",
    "Atlanta",
    "Tehran",
    "Aleppo",
    "Pune",
    "Oslo",
    "Tijuana",
    "Palenque",
    "Myr",
    "Santiago",
    "Uskdarler",
    "Mos Eisley",
    "Caemlyn",
    "Riga",
    "Nimrud",
    "White Harbor",
    "Dublin",
    "Theed",
    "Venice",
    "Tar Valon",
    "Calgary",
    "Kaposvar",
    "Lagos",
    "Pyongyang",
    "Sarvahr",
    "Marseilles",
    "Ankara",
    "Montreal",
    "Noah's Rainbow",
    "Arrakeen",
    "Chichen Itza",
    "Nassau",
    "Hong Kong",
    "Baikonur",
    "Bunker 118",
    "Braavos",
    "Dardogar",
    "New Jericho",
    "Jimboomba",
    "Winterfell",
    "Chongqing",
    "Tenochtitlan",
    "Jakarta",
    "Temesvar",
    "Kistel",
    "Cairo",
    "Addis Ababa",
    "Riyadh",
    "Kinshasa",
    "Almaty",
    "Merv",
    "Boston",
    "Wakanda",
    "Carthag",
    "Zirc",
    "Caracas",
    "Havana",
    "Ingulath",
    "New York",
    "Budapest",
    "Buenos Aires",
    "Bogota",
    "Lima",
    "Sao Paulo",
    "Mexico City",
    "Bangkok",
    "Manila",
    "Kuala Lumpur",
    "Singapore",
    "Hanoi",
    "Luanda",
    "Mombasa",
    "Kigali",
    "Sydney",
    "Shanghai",
    "Beijing",
}


def generate_random_city_name(already_taken_names: set[str]) -> str:
    names = CITY_NAMES - already_taken_names
    return random.choice(list(names))

def get_city_name_for_civ(civ: Civ, game_state: 'GameState') -> str:
    already_taken_names = set(city.name for city in list(game_state.cities_by_id.values()) + list(game_state.fresh_cities_for_decline.values()))
    city_names = CITY_NAMES_BY_CIV[civ.template.name]

    for city_name in city_names:
        if city_name not in already_taken_names:
            return city_name

    return generate_random_city_name(already_taken_names)