from collections import defaultdict
from typing import TYPE_CHECKING, Optional, Union
from building import Building
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from civ_template import CivTemplate
from civ import Civ
from camp import Camp
from settings import ADDITIONAL_PER_POP_FOOD_COST, BASE_FOOD_COST_OF_POP, CITY_CAPTURE_REWARD
from unit import Unit
from unit_template import UnitTemplate
from unit_templates_list import UNITS, UNITS_BY_BUILDING_NAME
from wonder_template import WonderTemplate, get_wonder_abilities_deprecated
from wonder_templates_list import WONDERS
from civ_templates_list import CIVS
from utils import generate_unique_id
import random
from typing import Dict
import traceback

if TYPE_CHECKING:
    from hex import Hex
    from game_state import GameState

TRADE_HUB_CITY_POWER_PER_TURN = 20

def resourcedict() -> Dict[str, float]:
    return {
        "food": 0.0,
        "wood": 0.0,
        "metal": 0.0,
        "science": 0.0,
        "city-power": 0.0,
        "unhappiness": 0.0,
    }

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
        self.under_siege_by_civ: Optional[Civ] = None
        self.hex: Optional['Hex'] = None
        self.infinite_queue_unit: Optional[UnitTemplate] = None
        self.buildings_queue: list[Union[UnitTemplate, BuildingTemplate, WonderTemplate]] = []
        self.buildings: list[Building] = [Building(UNITS.WARRIOR)]
        self.available_buildings: list[BuildingTemplate] = []
        self.available_wonders: list[WonderTemplate] = []
        self.available_buildings_to_descriptions: dict[str, dict[str, Union[str, float, int]]] = {}
        self.capital = False
        self._territory_parent_id: Optional[str] = None
        self._territory_parent_coords: Optional[str] = None
        self.available_units: list[UnitTemplate] = []
        self.projected_income = resourcedict()
        self.projected_income_base = resourcedict()  # income without focus
        self.projected_income_focus = resourcedict()  # income from focus
        self.projected_income_puppets: dict[str, dict[str, float]] = {'wood': {}, 'metal': {}}
        self.terrains_dict = {}
        self.founded_turn: int | None = None
        self.hidden_building_names: list[str] = []

        # Revolt stuff
        self.civ_to_revolt_into: Optional[CivTemplate] = None
        self.revolting_starting_vitality: float = 1.0
        self.unhappiness: float = 0.0
        self.is_decline_view_option: bool = False
        self.revolt_unit_count: int = 0

        self.handle_cleanup()

    def __repr__(self):
        return f"<City {self.name} @ {self.hex.coords if self.hex else None}>"

    def has_building(self, building_name: str) -> bool:
        return building_name in [b.building_name for b in self.buildings]

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
                child.set_territory_parent_if_needed(game_state)

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

    def set_territory_parent_if_needed(self, game_state: 'GameState') -> None:
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
        self.adjust_projected_yields(game_state)
        self.refresh_available_buildings()

    def is_trade_hub(self):
        return self.civ.trade_hub_id == self.id
    
    def is_fake_city(self) -> bool:
        assert self.hex is not None
        return self.hex.city != self

    def puppet_distance_penalty(self) -> float:
        bldg_factors: list[float] = [bldg.numbers_of_ability('ReducePuppetDistancePenalty')[0] for bldg in self.buildings if bldg.has_ability('ReducePuppetDistancePenalty')]
        return min([.1] + bldg_factors)

    def toggle_discard(self, building_name: str, hidden=True) -> None:
        if hidden and building_name not in self.hidden_building_names:
            self.hidden_building_names.append(building_name)
        elif not hidden and building_name in self.hidden_building_names:
            self.hidden_building_names.remove(building_name)

    def adjust_projected_yields(self, game_state: 'GameState') -> None:
        if self.hex is None:
            self.projected_income = resourcedict()
            self.projected_income_base = resourcedict()
            self.projected_income_focus = resourcedict()
        self.projected_income_base = self._get_projected_yields_without_focus(game_state)
        self.projected_income_focus = self._get_projected_yields_from_focus(game_state)
        self.food_demand: float = self._calculate_food_demand(game_state)

        self.projected_income = self.projected_income_base.copy()
        self.projected_income[self.focus] += self.projected_income_focus[self.focus]
 
        self.projected_income['unhappiness'] = max(0, self.food_demand - self.projected_income['food'])
        self.projected_income['city-power'] = max(0, self.projected_income['food'] - self.food_demand)

        if self.is_trade_hub():
            city_power_to_consume: float = min(
                TRADE_HUB_CITY_POWER_PER_TURN, 
                self.civ.city_power, 
                2 * (self.unhappiness + self.projected_income['unhappiness']))
            self.projected_income["unhappiness"] -= 0.5 * city_power_to_consume
            self.projected_income['city-power'] -= city_power_to_consume

        # If I'm a puppet, give my yields to my parent.
        parent: City | None = self.get_territory_parent(game_state)
        if parent:
            assert self.hex is not None
            assert parent.hex is not None
            distance: int = self.hex.distance_to(parent.hex)
            distance_penalty: float = parent.puppet_distance_penalty() * distance
            parent.projected_income_puppets['wood'][self.name] = self.projected_income['wood'] * (1 - distance_penalty)
            parent.projected_income_puppets['metal'][self.name] = self.projected_income['metal'] * (1 - distance_penalty)
            parent.adjust_projected_yields(game_state)
        else:
            for key, puppets_dict in self.projected_income_puppets.items():
                self.projected_income[key] += sum(puppet_income for puppet_income in puppets_dict.values())

    def _get_projected_yields_without_focus(self, game_state) -> dict[str, float]:
        vitality = self.civ.vitality
        yields = resourcedict()

        assert self.hex

        for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
            yields["food"] += hex.yields.food * vitality
            yields["metal"] += hex.yields.metal * vitality
            yields["wood"] += hex.yields.wood * vitality
            yields["science"] += hex.yields.science * vitality
        
        yields_per_population = {
            "food": 0,
            "metal": 0,
            "wood": 0,
            "science": 1,
        }

        for building in self.buildings:
            for ability in building.abilities:
                if ability.name == 'IncreaseYieldsPerPopulation':
                    yields_per_population[ability.numbers[0]] += ability.numbers[1]

        for key in yields_per_population:
            yields[key] += self.population * yields_per_population[key] * vitality


        yields["food"] += 2 * vitality
        return yields

    def _get_projected_yields_from_focus(self, game_state) -> dict[str, float]:
        vitality = self.civ.vitality
        yields = resourcedict()
        yields["food"] += self.population * vitality
        yields["metal"] += self.population * vitality
        yields["wood"] += self.population * vitality
        yields["science"] += self.population * vitality

        if self.civ.has_ability('IncreaseFocusYields'):
            bonus_resource, count = self.civ.numbers_of_ability('IncreaseFocusYields')
            yields[bonus_resource] += count
        for building in self.buildings:
            for ability in building.abilities:
                if ability.name == 'IncreaseFocusYieldsPerPopulation':
                    focus, amount_per_pop = ability.numbers
                    yields[focus] += amount_per_pop * self.population * vitality

        return yields

    def harvest_yields(self, game_state: 'GameState') -> None:
        self.adjust_projected_yields(game_state)  # TODO(dfarhi) this probably shouldn't be neessary since it should be called whenever teh state changes?
        self.food += self.projected_income["food"]
        self.civ.science += self.projected_income["science"]
        self.civ.city_power += self.projected_income["food"]
        self.unhappiness += self.projected_income['unhappiness']

        if self.is_territory_capital:
            self.wood += self.projected_income["wood"]
            self.metal += self.projected_income["metal"]


    def update_nearby_hexes_visibility(self, game_state: 'GameState', short_sighted: bool = False) -> None:
        if self.hex is None:
            return
        self.hex.visibility_by_civ[self.civ.id] = True

        # Always let cities have sight 2, even in decline mode (short_sighted = True)
        neighbors = self.hex.get_hexes_within_distance_2(game_state.hexes)

        for nearby_hex in neighbors:
            nearby_hex.visibility_by_civ[self.civ.id] = True

    def update_nearby_hexes_hostile_foundability(self, hexes: dict[str, 'Hex']) -> None:
        if self.hex is None:
            return

        for hex in [*self.hex.get_neighbors(hexes), self.hex]:
            for key in hex.is_foundable_by_civ:
                hex.is_foundable_by_civ[key] = False            

    def roll_turn(self, sess, game_state: 'GameState', fake: bool = False) -> None:
        """
        Fake: is this just a fake city for decline view?
        """
        if not fake:
            self.revolt_to_rebels_if_needed(game_state)
            self.harvest_yields(game_state)
            self.grow(game_state)
            if self.is_territory_capital:
                self.build_units(game_state)
                self.build_buildings(game_state)
            self.roll_wonders(game_state)
            self.handle_siege(sess, game_state)
        
        self.handle_unhappiness(game_state)
        self.handle_cleanup()
        self.midturn_update(game_state)

    def roll_wonders(self, game_state: 'GameState') -> None:
        for blfg in self.buildings:
            if isinstance(blfg.template, WonderTemplate):
                blfg.template.per_turn.apply(self, game_state)

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
        else:
            result += 2

        for building in self.buildings:
            for ability in building.abilities:
                if ability.name == 'DecreaseFoodDemand':
                    result -= ability.numbers[0]
        parent = self.get_territory_parent(game_state)
        if parent is not None:
            for building in parent.buildings:
                for ability in building.abilities:
                    if ability.name == 'DecreaseFoodDemandPuppets':
                        result -= ability.numbers[0]
        result = max(result, 0)
        return result

    def handle_unhappiness(self, game_state: 'GameState') -> None:
        if self.is_fake_city():
            self.revolting_starting_vitality = 1.0 + 0.05 * game_state.turn_num
        else:
            self.revolting_starting_vitality = 1.0 + 0.025 * game_state.turn_num + 0.0075 * self.unhappiness

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

        if self.civ.game_player:
            for wonder in game_state.wonders_built_to_civ_id:
                if game_state.wonders_built_to_civ_id[wonder] == self.civ.id and (abilities := get_wonder_abilities_deprecated(wonder)):
                    for ability in abilities:
                        if ability.name == "ExtraVpsForCityGrowth":
                            self.civ.game_player.score += ability.numbers[0]
                            self.civ.score += ability.numbers[0]    
                            self.civ.game_player.score_from_abilities += ability.numbers[0]


    def grow(self, game_state: 'GameState') -> None:
        while self.food >= self.growth_cost():
            self.food -= self.growth_cost()
            self.grow_inner(game_state)

    def growth_cost(self) -> float:
        total_growth_cost_reduction = 0.0

        for building in self.buildings:
            for ability in building.abilities:
                if ability.name == 'CityGrowthCostReduction':
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

        for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
            if not hex.terrain in self.terrains_dict:
                self.terrains_dict[hex.terrain] = 1
            else:
                self.terrains_dict[hex.terrain] += 1

    def refresh_available_wonders(self, game_state: 'GameState') -> None:
        self.available_wonders: list[WonderTemplate] = game_state.available_wonders()

    def refresh_available_buildings(self) -> None:
        if not self.civ:
            return

        old_available_buildings = set(self.available_buildings)
        self.available_buildings = self.civ.available_buildings
        new_bldgs = set(self.available_buildings) - old_available_buildings

        if not self.hex:
            return
        
        new_available_bldgs = self.get_available_buildings(include_in_queue=True)

        # Validate queue
        self.buildings_queue = [bldg for bldg in self.buildings_queue if bldg in new_available_bldgs]

        for template in new_available_bldgs:
            building_template = template if isinstance(template, BuildingTemplate) else None
            if building_template is not None:
                total_yields: float = 0
                total_pseudoyields: float = 0
                is_economic_building = False
                if building_template.vp_reward is not None:
                    total_yields += building_template.vp_reward
                    # AIs count points as worth 3 resources
                    total_pseudoyields += building_template.vp_reward * 2
                for ability in building_template.abilities:
                    if ability.name == 'IncreaseYieldsForTerrain':
                        is_economic_building = True
                        terrain = ability.numbers[2]
                        total_yields += int(ability.numbers[1] * (self.terrains_dict.get(terrain) or 0))

                    if ability.name == 'IncreaseYieldsInCity':
                        is_economic_building = True
                        total_yields += int(ability.numbers[1])

                    if ability.name == 'IncreaseYieldsPerPopulation':
                        is_economic_building = True
                        total_yields += int(ability.numbers[1] * self.population)

                    if ability.name == "CityGrowthCostReduction":
                        is_economic_building = True
                        ratio = ability.numbers[0]
                        effective_income_multiplier = 1 / ratio
                        effective_income_bonus = self.projected_income_base['food'] * (effective_income_multiplier - 1)
                        total_pseudoyields += int(effective_income_bonus / self.civ.vitality)

                    if ability.name == "DecreaseFoodDemand":
                        is_economic_building = True
                        unhappiness_saved: float = min(ability.numbers[0], self.food_demand)
                        total_yields += unhappiness_saved  # Display the raw number to humans

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
                        is_economic_building = True
                        yields = sum(sum(puppets_incomes.values()) for puppets_incomes in self.projected_income_puppets.values())
                        total_yields += round(yields * (self.puppet_distance_penalty() - ability.numbers[0]), ndigits=1)

                if is_economic_building:
                    self.available_buildings_to_descriptions[building_template.name] = {
                        "type": "yield",
                        "value": total_yields,
                        "value_for_ai": total_yields + total_pseudoyields,
                    }        
                    if building_template in new_bldgs and total_yields == 0 and total_pseudoyields == 0:
                        self.toggle_discard(building_template.name, hidden=True)

                elif not building_template.is_wonder:
                    self.available_buildings_to_descriptions[building_template.name] = {
                        "type": "???",
                        "value": 0,
                    }

            elif isinstance(template, WonderTemplate):
                self.available_buildings_to_descriptions[template.name] = {
                    "type": "wonder",
                    "value": template.age,
                }

            elif isinstance(template, UnitTemplate):
                self.available_buildings_to_descriptions[template.building_name] = {
                    "type": "strength",
                    "value": template.strength, 
                }

    def refresh_available_units(self) -> None:
        self.available_units = [unit for unit in UNITS.all() if unit.building_name is None or self.has_production_building_for_unit(unit)]
        self.available_units.sort(key=lambda unit: (unit.advancement_level(), unit.metal_cost, unit.name))

    def has_production_building_for_unit(self, unit: UnitTemplate) -> bool:
        return self.has_building(unit.building_name)

    def handle_cleanup(self) -> None:

        self.refresh_available_units()
        self.refresh_available_buildings()

    def get_available_buildings(self, include_in_queue=False) -> list[Union[BuildingTemplate, UnitTemplate, WonderTemplate]]:
        if not self.civ:
            return []
        if include_in_queue:
            building_names_in_queue = {}
        else:
            building_names_in_queue = {building.building_name if hasattr(building, 'building_name') else building.name for building in self.buildings_queue}  # type: ignore
        wonders: list[WonderTemplate] = [wonder for wonder in self.available_wonders if wonder.name not in building_names_in_queue]
        buildings: list[BuildingTemplate] = [building for building in self.available_buildings if not building.name in building_names_in_queue and not self.has_building(building.name)]
        unit_buildings: list[UnitTemplate] = [unit for unit in self.civ.available_unit_buildings if not unit.building_name in building_names_in_queue and not self.has_production_building_for_unit(unit)]
        return [*wonders, *buildings, *unit_buildings]

    def build_units(self, game_state: 'GameState') -> None:
        if self.infinite_queue_unit:
            while self.metal >= self.infinite_queue_unit.metal_cost:
                if self.metal >= self.infinite_queue_unit.metal_cost:
                    if self.build_unit(game_state, self.infinite_queue_unit):
                        self.metal -= self.infinite_queue_unit.metal_cost
                    else:
                        break

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


    def build_unit(self, game_state: 'GameState', unit: UnitTemplate, give_up_if_still_impossible: bool = False, stack_size=1) -> bool:
        if not self.hex:
            return False

        if not self.hex.is_occupied(unit.type, self.civ):
            self.spawn_unit_on_hex(game_state, unit, self.hex, stack_size=stack_size)
            return True

        best_hex = None
        best_hex_distance_from_target = 10000

        for hex in self.hex.get_neighbors(game_state.hexes):
            if not hex.is_occupied(unit.type, self.civ):
                distance_from_target = hex.distance_to(self.get_closest_target() or self.hex)
                if distance_from_target < best_hex_distance_from_target:
                    best_hex = hex
                    best_hex_distance_from_target = distance_from_target

        best_unit_to_reinforce = None
        if best_hex is None:

            best_unit_penalty = 10000

            # for hex in self.hex.get_distance_2_hexes(game_state.hexes):
            #     if not hex.is_occupied(unit.type, self.civ):
            #         distance_from_target = hex.distance_to(self.get_closest_target() or self.hex)
            #         if distance_from_target < best_hex_distance_from_target:
            #             best_hex = hex
            #             best_hex_distance_from_target = distance_from_target            

            for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                if hex.is_occupied(unit.type, self.civ):
                    unit_to_possibly_reinforce = hex.units[0]
                    if unit_to_possibly_reinforce.civ.id == self.civ.id and unit_to_possibly_reinforce.template.name == unit.name and unit_to_possibly_reinforce.hex:
                        unit_penalty = unit_to_possibly_reinforce.health * 10 + unit_to_possibly_reinforce.hex.distance_to(self.get_closest_target() or self.hex)
                        if unit_penalty < best_unit_penalty:
                            best_unit_to_reinforce = unit_to_possibly_reinforce
                            best_unit_penalty = unit_penalty            

        if best_hex is None:
            if best_unit_to_reinforce:
                self.reinforce_unit(best_unit_to_reinforce, stack_size=stack_size)
                return True
            
            else:
                if give_up_if_still_impossible:
                    return False
                num_merges = 0

                # Try merging friendly units
                for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                    if hex.units and hex.units[0].civ.id == self.civ.id:
                        if hex.units[0].merge_into_neighboring_unit(None, game_state, always_merge_if_possible=True):
                            num_merges += 1
                    if num_merges >= 2:
                        break

                # If that doesn't work, try merging enemy units, so long as they aren't on the city itself
                if num_merges == 0:
                    for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                        if hex.units and not hex.city:
                            if hex.units[0].merge_into_neighboring_unit(None, game_state, always_merge_if_possible=True):
                                num_merges += 1
                                break
                        if num_merges >= 2:
                            break

                # If that doesn't work, and we have a lot of metal to spend, try removing friendly units altogether
                if num_merges == 0 and self.metal > 75:
                    for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                        if hex.units and hex.units[0].civ.id == self.civ.id and hex.units[0].health < 300:
                            hex.units[0].remove_from_game(game_state)
                            break

                return self.build_unit(game_state, unit, give_up_if_still_impossible=True, stack_size=stack_size)

        self.spawn_unit_on_hex(game_state, unit, best_hex)
        return True

    def spawn_unit_on_hex(self, game_state: 'GameState', unit_template: UnitTemplate, hex: 'Hex', stack_size=1) -> None:
        if self.hex is None:
            return
        unit = Unit(unit_template, self.civ)
        unit.health *= stack_size
        unit.hex = hex
        hex.units.append(unit)
        game_state.units.append(unit)

        if self.civ.has_ability('IncreasedStrengthForUnit'):
            if self.civ.numbers_of_ability('IncreasedStrengthForUnit')[0] == unit_template.name:
                unit.strength += self.civ.numbers_of_ability('IncreasedStrengthForUnit')[1]

        for wonder in game_state.wonders_built_to_civ_id:
            if game_state.wonders_built_to_civ_id[wonder] == self.civ.id:
                for ability in get_wonder_abilities_deprecated(wonder):
                    if ability.name == 'NewUnitsGainBonusStrength':
                        unit.strength += ability.numbers[0]

    def reinforce_unit(self, unit: Unit, stack_size=1) -> None:
        unit.health += 100 * stack_size

    def build_buildings(self, game_state: 'GameState') -> None:
        while self.buildings_queue:
            building: UnitTemplate | BuildingTemplate | WonderTemplate = self.buildings_queue[0]
            cost = building.wood_cost if isinstance(building, UnitTemplate) else building.cost if isinstance(building, BuildingTemplate) else game_state.wonder_cost_by_age[building.age]
            if self.wood >= cost:
                self.buildings_queue.pop(0)
                self.build_building(game_state, building)
                self.wood -= cost
            else:
                break

    def build_building(self, game_state: 'GameState', building: Union[BuildingTemplate, UnitTemplate, WonderTemplate]) -> None:
        new_building = Building(building)

        self.buildings.append(new_building)

        if isinstance(building, UnitTemplate):
            self.infinite_queue_unit = building

        is_national_wonder: bool = isinstance(building, BuildingTemplate) and building.is_national_wonder

        if new_building.has_ability('IncreaseYieldsForTerrain'):
            for ability in new_building.abilities:
                assert self.hex
                numbers = ability.numbers
                for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                    if hex.terrain == numbers[2]:
                        new_value = getattr(hex.yields, numbers[0]) + numbers[1]
                        setattr(hex.yields, numbers[0], new_value)

        if new_building.has_ability('DoubleYieldsForTerrainInCity'):
            assert self.hex
            numbers = new_building.numbers_of_ability('DoubleYieldsForTerrainInCity')
            for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                if hex.terrain == numbers[0]:
                    for yield_name in ['food', 'metal', 'wood', 'science']:
                        new_value = getattr(hex.yields, yield_name) * 2
                        setattr(hex.yields, yield_name, new_value)

        if new_building.has_ability('ExistingUnitsGainBonusStrength'):
            for unit in game_state.units:
                if unit.civ.id == self.civ.id:
                    unit.strength += new_building.numbers_of_ability('ExistingUnitsGainBonusStrength')[0]

        if new_building.has_ability('IncreaseYieldsInCity'):
            assert self.hex
            numbers = new_building.numbers_of_ability('IncreaseYieldsInCity')
            new_value = getattr(self.hex.yields, numbers[0]) + numbers[1]
            setattr(self.hex.yields, numbers[0], new_value)

        if self.civ.game_player:
            self.civ.game_player.score += new_building.vp_reward
            self.civ.score += new_building.vp_reward
            self.civ.game_player.score_from_building_vps += new_building.vp_reward

        if new_building.has_ability('GainCityPower'):
            self.civ.city_power += new_building.numbers_of_ability('GainCityPower')[0]

        if new_building.has_ability('GainFreeUnits'):
            for _ in range(new_building.numbers_of_ability('GainFreeUnits')[1]):
                self.build_unit(game_state, UNITS.by_name(new_building.numbers_of_ability('GainFreeUnits')[0]))

        if new_building.has_ability('EndTheGame'):
            game_state.game_over = True

        if new_building.has_ability('TripleCityPopulation'):
            self.population *= 3

        if new_building.has_ability('ResetCityUnhappiness'):
            self.unhappiness = 0
        
        if new_building.has_ability('ResetCivUnhappiness'):
            for city in game_state.cities_by_id.values():
                if city.civ == self.civ:
                    city.unhappiness = 0

        if isinstance(building, WonderTemplate):
            building.on_build.apply(self, game_state)
            game_state.handle_wonder_built(self.civ, building)

        if is_national_wonder:
            if self.civ.id not in game_state.national_wonders_built_by_civ_id:
                game_state.national_wonders_built_by_civ_id[self.civ.id] = [building.name]
            else:
                game_state.national_wonders_built_by_civ_id[self.civ.id].append(building.name)

        if is_national_wonder or isinstance(building, WonderTemplate):
            # Clear it from any other cities immediately; you can't build two in one turn.
            for city in self.civ.get_my_cities(game_state):
                city.buildings_queue = [building for building in city.buildings_queue if building.name != building.name]

    def get_siege_state(self, game_state: 'GameState') -> Optional[Civ]:
        if self.hex is None:
            return None

        for unit in self.hex.units:
            if unit.civ.id != self.civ.id and unit.template.type == 'military':
                return unit.civ

        return None
    
    def hide_bad_buildings(self):
        highest_unit_level = max([0] + [u.advancement_level() for u in self.civ.available_unit_buildings])
        for building in self.get_available_buildings():
            if isinstance(building, BuildingTemplate):
                if building.is_wonder or building.is_national_wonder:
                    continue
                desc = self.available_buildings_to_descriptions[building.name]
                if desc.get('type') == 'yield' and desc.get('value') == 0 and desc.get('value_for_ai') == 0:
                    self.toggle_discard(building.name, hidden=True)
            elif isinstance(building, UnitTemplate):
                if building.advancement_level() < highest_unit_level - 1:
                    self.toggle_discard(building.building_name, hidden=True)


    def change_owner(self, civ: Civ, game_state: 'GameState') -> None:
        """
        Called when an existing city changes owner; called by capture() and process_decline_option().
        """
        # Remove trade hub
        if self.is_trade_hub():
            self.civ.trade_hub_id = None

        # Re-assign global wonders, and remove national wonders.
        for building in self.buildings:
            if building.is_wonder:
                game_state.wonders_built_to_civ_id[building.building_name] = civ.id
            if building.is_national_wonder:
                game_state.national_wonders_built_by_civ_id[self.civ.id].remove(building.building_name)
        self.buildings = [b for b in self.buildings if not b.is_national_wonder]

        # Change the civ
        self.civ = civ

        # Fix territory parent lines
        self.orphan_territory_children(game_state)
        self.set_territory_parent_if_needed(game_state)

        # Reset various properties
        self.hidden_building_names = []
        self.under_siege_by_civ = None
        self.buildings_queue = []
        self.infinite_queue_unit = None
        self.ever_controlled_by_civ_ids[civ.id] = True

        # Update available stuff
        self.refresh_available_buildings()
        self.refresh_available_units()
        self.hide_bad_buildings()

    def barbarian_capture(self, game_state: 'GameState') -> None:
        """Barbarians replace the city with a camp."""
        
        # Call change_owner to do the cleanup on the previous civ ownership
        self.change_owner(game_state.barbarians, game_state)

        best_unit: UnitTemplate = max(self.available_units, key=lambda x: (x.advancement_level(), random.random()))

        assert self.hex and self.hex.city


        # Also build a handful of units out of the ruins of the city
        for u in self.available_units:
            print(u)
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
        self.wood /= 2
        self.metal /= 2

        military_bldgs = [building for building in self.buildings if isinstance(building.template, UnitTemplate)]
        military_bldgs.sort(key=lambda unit: (-unit.template.advancement_level(), random.random()))  # type: ignore
        best_3 = military_bldgs[:3]
        top_level = [building for building in military_bldgs if building.template.advancement_level() == military_bldgs[0].template.advancement_level()]  # type: ignore
        for building in military_bldgs:
            if building not in best_3 and building not in top_level:
                self.buildings.remove(building)

        if civ.game_player and civ.id not in self.ever_controlled_by_civ_ids:
            civ.game_player.score += CITY_CAPTURE_REWARD
            civ.score += CITY_CAPTURE_REWARD
            civ.game_player.score_from_capturing_cities_and_camps += CITY_CAPTURE_REWARD

            if civ.has_ability('ExtraVpsPerCityCaptured'):
                civ.game_player.score += civ.numbers_of_ability('ExtraVpsPerCityCaptured')[0]
                civ.score += civ.numbers_of_ability('ExtraVpsPerCityCaptured')[0]
                civ.game_player.score_from_abilities += civ.numbers_of_ability('ExtraVpsPerCityCaptured')[0]

            if civ.has_ability('IncreaseYieldsForTerrain'):
                assert self.hex
                numbers = civ.numbers_of_ability('IncreaseYieldsForTerrain')
                for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                    if hex.terrain == numbers[1]:
                        new_value = getattr(hex.yields, numbers[0]) + numbers[2]
                        setattr(hex.yields, numbers[0], new_value)                

            for wonder in game_state.wonders_built_to_civ_id:
                if game_state.wonders_built_to_civ_id[wonder] == self.civ.id and (abilities := get_wonder_abilities_deprecated(wonder)):
                    for ability in abilities:
                        if ability.name == "ExtraVpsForCityCapture":
                            civ.game_player.score += ability.numbers[0]
                            civ.score += ability.numbers[0]
                            civ.game_player.score_from_abilities += ability.numbers[0]

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
    
        if civ.has_ability('IncreaseCapitalYields'):
            if self.hex:
                self.hex.yields.increase(civ.numbers_of_ability('IncreaseCapitalYields')[0],
                                            civ.numbers_of_ability('IncreaseCapitalYields')[1])
                
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

        if civ.has_ability('IncreaseYieldsForTerrain'):
            assert self.hex
            numbers = civ.numbers_of_ability('IncreaseYieldsForTerrain')
            for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                if hex.terrain == numbers[1]:
                    new_value = getattr(hex.yields, numbers[0]) + numbers[2]
                    setattr(hex.yields, numbers[0], new_value)

                
    def update_civ_by_id(self, civs_by_id: dict[str, Civ]) -> None:
        self.civ = civs_by_id[self.civ_id]
        self.under_siege_by_civ = civs_by_id[self.under_siege_by_civ.id] if self.under_siege_by_civ else None                                    

    def bot_pick_wonder(self, choices: list[WonderTemplate], game_state: 'GameState') -> Optional[WonderTemplate]:
        affordable_ages: set[int] = {age for age in game_state.wonders_by_age.keys() if game_state.wonder_cost_by_age[age] <= self.wood + self.projected_income['wood']}
        affordable_choices: list[WonderTemplate] = [choice for choice in choices if choice.age in affordable_ages]
        if len(affordable_choices) == 0:
            return None
        # Build the highest age one we can afford
        return max(affordable_choices, key=lambda x: (x.age, random.random()))

    def bot_pick_economic_building(self, choices: list[BuildingTemplate]) -> Optional[BuildingTemplate]:
        national_wonders = [building for building in choices if building.is_national_wonder]
        nonwonders = [building for building in choices if not building.is_wonder and not building.is_national_wonder]

        existing_national_wonders: list[BuildingTemplate] = [building for building in self.buildings if isinstance(building, BuildingTemplate) and building.is_national_wonder]
        if len(national_wonders) > 0 and len(existing_national_wonders) == 0 and self.population >= 8:
            return random.choice(national_wonders)

        if len(nonwonders) > 0:
            # print(f"    Choosing nonwonder; {self.available_buildings_to_descriptions=}")
            ACCEPTABLE_PAYOFF_TURNS = 8
            inverse_payoff_turns: dict[BuildingTemplate, float] = {
                building: float(self.available_buildings_to_descriptions[building.name].get('value_for_ai', 0)) / building.cost
                for building in nonwonders
                if building.name in self.available_buildings_to_descriptions and self.available_buildings_to_descriptions[building.name]['type'] == 'yield'
            }
            print(f"    {inverse_payoff_turns=}")
            if len(nonwonders) > len(inverse_payoff_turns):
                print(f"**** didn't consider these non-yield buildings: {set(nonwonders) - set(inverse_payoff_turns.keys() )}")
            if len(inverse_payoff_turns) > 0:
                # calulcate the argmin of the payoff turns
                best_building = max(inverse_payoff_turns, key=lambda x: inverse_payoff_turns.get(x, 0))
                if inverse_payoff_turns[best_building] > 1.0 / ACCEPTABLE_PAYOFF_TURNS:
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

        print(f"Planning Ai move for city {self.name}")
        self.midturn_update(game_state)

        # Don't build stationary units
        available_units = [unit for unit in self.available_units if unit.movement > 0]
        highest_level = max([effective_advancement_level(unit, slingers_better_than_warriors=True) for unit in available_units])
        highest_tier_units = [unit for unit in available_units if effective_advancement_level(unit, slingers_better_than_warriors=True) == highest_level]
        if highest_level < self.civ.get_advancement_level() - 2 and not self.is_threatened_city(game_state):
            self.infinite_queue_unit = None
            print(f"  not building units because the best I can built is level {highest_level} units and I'm at tech level {self.civ.get_advancement_level()}")
        elif highest_level < self.civ.get_advancement_level() - 4:
            self.infinite_queue_unit = None
            print(f"  not building units even though threatened, because the best I can built is level {highest_level} units and I'm at tech level {self.civ.get_advancement_level()}")
        else:
            self.infinite_queue_unit = random.choice(highest_tier_units)
            print(f"  set unit build: {self.infinite_queue_unit.name} (available were from {[u.name for u in available_units]})")

        available_buildings = self.get_available_buildings()
        wonders: list[WonderTemplate] = [building for building in available_buildings if isinstance(building, WonderTemplate)]
        economic_buildings: list[BuildingTemplate] = [building for building in available_buildings if isinstance(building, BuildingTemplate)]
        military_buildings: list[UnitTemplate] = [building for building in available_buildings if isinstance(building, UnitTemplate) and building.movement > 0]
        lotsa_wood: bool = self.projected_income_base['wood'] > self.projected_income_base['metal'] * 2
        if len(military_buildings) > 0:
            # Choose buildings first by effective advancement level, then randomly
            best_military_building = max(military_buildings, key=lambda building: (
                effective_advancement_level(building, slingers_better_than_warriors=lotsa_wood), 
                random.random()
                ))
        else:
            best_military_building = None
        if best_military_building is not None and (self.infinite_queue_unit is None or effective_advancement_level(best_military_building, slingers_better_than_warriors=lotsa_wood) > effective_advancement_level(self.infinite_queue_unit, slingers_better_than_warriors=lotsa_wood)):
            self.buildings_queue = [best_military_building]
            print(f"  overwrote building queue because of new military unit (lvl {effective_advancement_level(best_military_building, slingers_better_than_warriors=lotsa_wood)}): {self.buildings_queue}")
            if self.infinite_queue_unit is not None and not self.is_threatened_city(game_state):
                print(f"  not building units to wait for new military building.")
                self.infinite_queue_unit = None
        elif len(self.buildings_queue) > 0:
            print(f"  continuing previous build queue: {self.buildings_queue}")
        elif len(wonders) > 0 and (wonder_choice := self.bot_pick_wonder(wonders, game_state)) is not None:
            self.buildings_queue = [wonder_choice]
            print(f"  set building queue to wonder: {self.buildings_queue}")
        elif len(economic_buildings) > 0 and (choice := self.bot_pick_economic_building(economic_buildings)) is not None:
            self.buildings_queue = [choice]
            print(f"  set building queue to economic building: {self.buildings_queue}")
        else:
            print(f"  no buildings available")

        if self.civ_to_revolt_into is not None or self.unhappiness + self.projected_income['unhappiness'] > game_state.unhappiness_threshold:
            self.focus = 'food'
            print(f"  chose focus: {self.focus} to prevent revolt")
        else:
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
            if len(focuses_with_best_yields) == 1:
                self.focus = focuses_with_best_yields[0]
            elif len(production_city.buildings_queue) > 0 and isinstance(production_city.buildings_queue[0], BuildingTemplate) and production_city.buildings_queue[0].is_national_wonder:
                self.focus = 'wood'
            elif self.population < 3 and 'food' in focuses_with_best_yields:
                self.focus = 'food'
            elif production_city.infinite_queue_unit is not None and 'metal' in focuses_with_best_yields:
                self.focus = 'metal'
            elif len(production_city.buildings_queue) > 0 and 'wood' in focuses_with_best_yields:
                self.focus = 'wood'
            elif 'science' in focuses_with_best_yields:
                self.focus = 'science'
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
            "under_siege_by_civ": self.under_siege_by_civ.to_json() if self.under_siege_by_civ else None,
            "hex": self.hex.coords if self.hex else None,
            "infinite_queue_unit": self.infinite_queue_unit.name if self.infinite_queue_unit is not None else "",
            "buildings_queue": [building.building_name if hasattr(building, 'building_name') else building.name for building in self.buildings_queue],  # type: ignore
            "buildings": [building.to_json() for building in self.buildings],
            "available_buildings": [b.name for b in self.available_buildings],
            "available_wonders": [w.name for w in self.available_wonders],
            "available_buildings_to_descriptions": self.available_buildings_to_descriptions.copy(),
            "available_building_names": [template.building_name if hasattr(template, 'building_name') else template.name for template in self.get_available_buildings()],  # type: ignore
            "capital": self.capital,
            "available_units": [u.name for u in self.available_units],
            "projected_income": self.projected_income,
            "projected_income_base": self.projected_income_base,
            "projected_income_focus": self.projected_income_focus,
            "projected_income_puppets": self.projected_income_puppets,
            "growth_cost": self.growth_cost(),
            "terrains_dict": self.terrains_dict,
            "hidden_building_names": self.hidden_building_names,

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
        city.food = json["food"]
        city.metal = json["metal"]
        city.wood = json["wood"]
        city.under_siege_by_civ = Civ.from_json(json["under_siege_by_civ"]) if json["under_siege_by_civ"] else None
        city.capital = json["capital"]
        city.buildings_queue = [UNITS_BY_BUILDING_NAME[building] if building in UNITS_BY_BUILDING_NAME else BUILDINGS.by_name(building) if building in [b.name for b in BUILDINGS.all()] else WONDERS.by_name(building) for building in json["buildings_queue"]]
        city.available_buildings = [BUILDINGS.by_name(b) for b in json["available_buildings"]]
        city.available_wonders = [WONDERS.by_name(w) for w in json["available_wonders"]]
        city.available_buildings_to_descriptions = (json.get("available_buildings_to_descriptions") or {}).copy()
        city.available_units = [UNITS.by_name(unit) for unit in json["available_units"]]
        city.infinite_queue_unit = None if json["infinite_queue_unit"] == "" else UNITS.by_name(json["infinite_queue_unit"])
        city.focus = json["focus"]
        city.projected_income = json["projected_income"]
        city.projected_income_base = json["projected_income_base"]
        city.projected_income_focus = json["projected_income_focus"]
        city.terrains_dict = json.get("terrains_dict") or {}
        city.hidden_building_names = json.get("hidden_building_names") or []
        city.civ_to_revolt_into = CIVS.by_name(json["civ_to_revolt_into"]) if json["civ_to_revolt_into"] else None
        city.revolting_starting_vitality = json["revolting_starting_vitality"]
        city.unhappiness = json["unhappiness"]
        city.is_decline_view_option = json["is_decline_view_option"]
        city.revolt_unit_count = json["revolt_unit_count"]
        city._territory_parent_id = json["territory_parent_id"]
        city._territory_parent_coords = json["territory_parent_coords"]
        city.founded_turn = json["founded_turn"]

        city.handle_cleanup()

        return city


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


def generate_random_city_name(game_state: Optional['GameState'] = None) -> str:
    names = CITY_NAMES
    if game_state is not None:
        names = CITY_NAMES - set(city.name for city in game_state.cities_by_id.values())
    return random.choice(list(names))
