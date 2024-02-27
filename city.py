from collections import defaultdict
from typing import TYPE_CHECKING, Optional, Union
from building import Building
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from civ import Civ
from settings import ADDITIONAL_PER_POP_FOOD_COST, BASE_FOOD_COST_OF_POP, CITY_CAPTURE_REWARD
from unit import Unit
from unit_template import UnitTemplate
from unit_templates_list import PRODUCTION_BUILDINGS_BY_UNIT_NAME, UNITS, UNITS_BY_BUILDING_NAME
from utils import generate_unique_id
import random
from typing import Dict

if TYPE_CHECKING:
    from hex import Hex
    from game_state import GameState


def resourcedict() -> Dict[str, float]:
    return {
        "food": 0.0,
        "wood": 0.0,
        "metal": 0.0,
        "science": 0.0,
        "city_power": 0.0,
    }

class City:
    def __init__(self, civ: Civ, id: Optional[str] = None):
        self.id = id or generate_unique_id()
        self.civ = civ
        self.ever_controlled_by_civ_ids: dict[str, bool] = {civ.id: True}
        self.name = generate_random_city_name()
        self.population = 1
        self.buildings: list[Building] = []
        self.food = 0.0
        self.metal = 0.0
        self.wood = 0.0
        self.focus: str = 'food'
        self.under_siege_by_civ: Optional[Civ] = None
        self.hex: Optional['Hex'] = None
        self.infinite_queue_unit: Optional[UnitTemplate] = None
        self.buildings_queue: list[Union[UnitTemplate, BuildingTemplate]] = []
        self.buildings: list[Building] = []
        self.available_buildings: list[str] = []
        self.available_buildings_to_descriptions: dict[str, dict[str, Union[str, int]]] = {}
        self.capital = False
        self.available_units: list[str] = []
        self.projected_income = resourcedict()
        self.projected_income_base = resourcedict()  # income without focus
        self.projected_income_focus = resourcedict()  # income from focus
        self.terrains_dict = {}

        self.handle_cleanup()

    def has_building(self, building_name: str) -> bool:
        return any([(building.template.building_name if hasattr(building.template, 'building_name') else building.template.name) == building_name for building in self.buildings])  # type: ignore

    def building_is_in_queue(self, building_name: str) -> bool:
        return any([(building.building_name if hasattr(building, 'building_name') else building.name) == building_name for building in self.buildings_queue])  # type: ignore

    def midturn_update(self, game_state: 'GameState') -> None:
        """
        Update things that could have changed due to the controlling player fiddling with focus etc.
        """
        self.adjust_projected_yields(game_state)

    def adjust_projected_yields(self, game_state: 'GameState') -> None:
        if self.hex is None:
            self.projected_income = resourcedict()
            self.projected_income_base = resourcedict()
            self.projected_income_focus = resourcedict()
        self.projected_income_base = self._get_projected_yields_without_focus(game_state)
        self.projected_income_focus = self._get_projected_yields_from_focus(game_state)

        self.projected_income = self.projected_income_base.copy()
        self.projected_income[self.focus] += self.projected_income_focus[self.focus]
        if self.focus == 'food':
            self.projected_income['city_power'] += self.projected_income_focus['food']

    def _get_projected_yields_without_focus(self, game_state) -> dict[str, float]:
        vitality = self.civ.vitality
        yields = resourcedict()

        assert self.hex

        for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
            yields["food"] += hex.yields.food * vitality
            yields["metal"] += hex.yields.metal * vitality
            yields["wood"] += hex.yields.wood * vitality
            yields["science"] += hex.yields.science * vitality
            yields["city_power"] += hex.yields.food * vitality
        
        yields_per_population = {
            "food": 0,
            "metal": 0,
            "wood": 0,
            "science": 1,
        }

        for building in self.buildings:
            for ability in building.template.abilities:
                if ability.name == 'IncreaseYieldsPerPopulation':
                    yields_per_population[ability.numbers[0]] += ability.numbers[1]

        for key in yields_per_population:
            yields[key] += self.population * yields_per_population[key] * vitality

            if key == 'food':
                yields["city_power"] += self.population * yields_per_population[key] * vitality

        yields["food"] += 2 * vitality
        yields["city_power"] += 2 * vitality
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
            for ability in building.template.abilities:
                if ability.name == 'IncreaseFocusYieldsPerPopulation':
                    focus, amount_per_pop = ability.numbers
                    yields[focus] += amount_per_pop * self.population * vitality

        return yields

    def harvest_yields(self, game_state: 'GameState') -> None:
        self.adjust_projected_yields(game_state)  # TODO(dfarhi) this probably shouldn't be neessary since it should be called whenever teh state changes?
        self.wood += self.projected_income["wood"]
        self.metal += self.projected_income["metal"]
        self.food += self.projected_income["food"]
        self.civ.science += self.projected_income["science"]
        self.civ.city_power += self.projected_income["food"]

    def update_nearby_hexes_visibility(self, game_state: 'GameState', short_sighted: bool = False) -> None:
        if self.hex is None:
            return
        self.hex.visibility_by_civ[self.civ.id] = True

        if short_sighted:
            neighbors = self.hex.get_neighbors(game_state.hexes)
        else:
            neighbors = self.hex.get_hexes_within_distance_2(game_state.hexes)


        for nearby_hex in neighbors:
            nearby_hex.visibility_by_civ[self.civ.id] = True

    def update_nearby_hexes_hostile_foundability(self, hexes: dict[str, 'Hex']) -> None:
        if self.hex is None:
            return

        for hex in [*self.hex.get_neighbors(hexes), self.hex]:
            for key in hex.is_foundable_by_civ:
                hex.is_foundable_by_civ[key] = False            

    def roll_turn(self, sess, game_state: 'GameState') -> None:
        self.harvest_yields(game_state)
        self.grow(game_state)
        self.build_units(sess, game_state)
        self.build_buildings(sess, game_state)
        self.handle_siege(sess, game_state)
        self.handle_cleanup()

    def grow_inner(self, game_state: 'GameState') -> None:
        self.population += 1

        if self.civ.game_player:
            for wonder in game_state.wonders_built_to_civ_id:
                if game_state.wonders_built_to_civ_id[wonder] == self.civ.id and (abilities := BUILDINGS[wonder]["abilities"]):
                    for ability in abilities:
                        if ability["name"] == "ExtraVpsForCityGrowth":
                            self.civ.game_player.score += ability["numbers"][0]    
                            self.civ.game_player.score_from_abilities += ability["numbers"][0]


    def grow(self, game_state: 'GameState') -> None:
        while self.food >= self.growth_cost():
            self.food -= self.growth_cost()
            self.grow_inner(game_state)

    def growth_cost(self) -> float:
        total_growth_cost_reduction = 0.0

        for building in self.buildings:
            for ability in building.template.abilities:
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

    def refresh_available_buildings(self) -> None:
        self.available_buildings = [building_name for building_name in self.civ.available_buildings if not self.has_building(building_name) and not self.building_is_in_queue(building_name)]

        if not self.hex:
            return

        for template in self.get_available_buildings():
            building_template = template if isinstance(template, BuildingTemplate) else None
            unit_template = template if isinstance(template, UnitTemplate) else None

            if building_template is not None:
                total_yields = 0
                is_economic_building = False
                for ability in building_template.abilities:
                    if ability.name == 'IncreaseYieldsForTerrain':
                        is_economic_building = True
                        terrain = ability.numbers[2]
                        total_yields += ability.numbers[1] * (self.terrains_dict.get(terrain) or 0)

                    if ability.name == 'IncreaseYieldsInCity':
                        is_economic_building = True
                        total_yields += ability.numbers[1]

                    if ability.name == 'IncreaseYieldsPerPopulation':
                        is_economic_building = True
                        total_yields += ability.numbers[1] * self.population

                if is_economic_building:
                    if total_yields > 0:
                        self.available_buildings_to_descriptions[building_template.name] = {
                            "type": "yield",
                            "value": total_yields,
                        }
                    else:
                        if not self.terrains_dict:
                            self.available_buildings_to_descriptions[building_template.name] = {
                                "type": "yield",
                                "value": 0,
                            }                            
                        else:
                            self.available_buildings = [building for building in self.available_buildings if building != building_template.name]

                elif not building_template.is_wonder:
                    self.available_buildings_to_descriptions[building_template.name] = {
                        "type": "yield",
                        "value": 0,
                    }

                if building_template.is_wonder:
                    self.available_buildings_to_descriptions[building_template.name] = {
                        "type": "wonder_cost",
                        "value": building_template.cost,
                    }

            if unit_template is not None:
                self.available_buildings_to_descriptions[unit_template.building_name] = {
                    "type": "strength",
                    "value": unit_template.strength,
                }



    def refresh_available_units(self) -> None:
        self.available_units = [unit['name'] for unit in UNITS.values() if unit['building_name'] is None or self.has_production_building_for_unit(unit['name'])]

    def has_production_building_for_unit(self, unit_name: str) -> bool:
        return self.has_building(PRODUCTION_BUILDINGS_BY_UNIT_NAME[unit_name])

    def handle_cleanup(self) -> None:
        self.refresh_available_units()
        self.refresh_available_buildings()

    def get_available_buildings(self) -> list[Union[BuildingTemplate, UnitTemplate]]:
        building_names_in_queue = [building.building_name if hasattr(building, 'building_name') else building.name for building in self.buildings_queue]  # type: ignore
        buildings = [BuildingTemplate.from_json(BUILDINGS[building_name]) for building_name in self.available_buildings if not building_name in building_names_in_queue and not self.has_building(building_name)]
        unit_buildings = [UnitTemplate.from_json(UNITS_BY_BUILDING_NAME[building_name]) for building_name in self.civ.available_unit_buildings if not building_name in building_names_in_queue and not self.has_building(building_name)]
        return [*buildings, *unit_buildings]

    def build_units(self, sess, game_state: 'GameState') -> None:
        if self.infinite_queue_unit:
            while self.metal >= self.infinite_queue_unit.metal_cost:
                if self.metal >= self.infinite_queue_unit.metal_cost:
                    self.build_unit(sess, game_state, self.infinite_queue_unit)
                    self.metal -= self.infinite_queue_unit.metal_cost

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


    def build_unit(self, sess, game_state: 'GameState', unit: UnitTemplate) -> bool:
        if not self.hex:
            return False

        if not self.hex.is_occupied(unit.type, self.civ):
            self.spawn_unit_on_hex(sess, game_state, unit, self.hex)
            return True

        best_hex = None
        best_hex_distance_from_target = 10000

        if "defensive" not in unit.tags:
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
                if hex.is_occupied(unit.type, self.civ) and ("defensive" not in unit.tags or hex.coords == self.hex.coords):
                    unit_to_possibly_reinforce = hex.units[0]
                    if unit_to_possibly_reinforce.civ.id == self.civ.id and unit_to_possibly_reinforce.template.name == unit.name and unit_to_possibly_reinforce.hex:
                        unit_penalty = unit_to_possibly_reinforce.health * 10 + unit_to_possibly_reinforce.hex.distance_to(self.get_closest_target() or self.hex)
                        if unit_penalty < best_unit_penalty:
                            best_unit_to_reinforce = unit_to_possibly_reinforce
                            best_unit_penalty = unit_penalty            

        if best_hex is None:
            if best_unit_to_reinforce:
                self.reinforce_unit(best_unit_to_reinforce)
                return True
            return False
        self.spawn_unit_on_hex(sess, game_state, unit, best_hex)
        return True

    def spawn_unit_on_hex(self, sess, game_state: 'GameState', unit_template: UnitTemplate, hex: 'Hex') -> None:
        if self.hex is None:
            return
        unit = Unit(unit_template, self.civ)
        unit.hex = hex
        hex.units.append(unit)
        game_state.units.append(unit)

        if self.civ.has_ability('IncreasedStrengthForUnit'):
            if self.civ.numbers_of_ability('IncreasedStrengthForUnit')[0] == unit_template.name:
                unit.strength += self.civ.numbers_of_ability('IncreasedStrengthForUnit')[1]

        for wonder in game_state.wonders_built_to_civ_id:
            if game_state.wonders_built_to_civ_id[wonder] == self.civ.id:
                for ability in BUILDINGS[wonder]["abilities"]:
                    if ability['name'] == 'NewUnitsGainBonusStrength':
                        unit.strength += ability['numbers'][0]

        if self.hex.coords != unit.hex.coords:
            game_state.add_animation_frame_for_civ(sess, {
                "type": "UnitSpawn",
                "start_coords": self.hex.coords,
                "end_coords": unit.hex.coords,
            }, self.civ)

    def reinforce_unit(self, unit: Unit) -> None:
        unit.health += 100

    def build_buildings(self, sess, game_state: 'GameState') -> None:
        while self.buildings_queue:
            building = self.buildings_queue[0]
            if isinstance(building, BuildingTemplate):
                if self.wood >= building.cost:
                    self.buildings_queue.pop(0)
                    self.build_building(sess, game_state, building)
                    self.wood -= building.cost
                else:
                    break

            elif isinstance(building, UnitTemplate):
                if self.wood >= building.wood_cost:
                    self.buildings_queue.pop(0)
                    self.build_building(sess, game_state, building)
                    self.wood -= building.wood_cost
                else:
                    break

            else:
                break

    def build_building(self, sess, game_state: 'GameState', building: Union[BuildingTemplate, UnitTemplate]) -> None:
        unit_template = building if isinstance(building, UnitTemplate) else None
        building_template = building if isinstance(building, BuildingTemplate) else None

        new_building = Building(unit_template=unit_template, building_template=building_template)

        self.buildings.append(new_building)

        if unit_template is not None:
            self.infinite_queue_unit = unit_template

        if new_building.has_ability('IncreaseYieldsForTerrain'):
            for ability in new_building.template.abilities:
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

        if isinstance(new_building.template, BuildingTemplate) and new_building.template.vp_reward and self.civ.game_player:
            self.civ.game_player.score += new_building.template.vp_reward
            self.civ.game_player.score_from_building_vps += new_building.template.vp_reward

        if new_building.has_ability('GainCityPower'):
            self.civ.city_power += new_building.numbers_of_ability('GainCityPower')[0]

        if new_building.has_ability('GainFreeUnits'):
            for _ in range(new_building.numbers_of_ability('GainFreeUnits')[1]):
                self.build_unit(sess, game_state, UnitTemplate.from_json(UNITS[new_building.numbers_of_ability('GainFreeUnits')[0]]))

        if new_building.has_ability('EndTheGame'):
            game_state.game_over = True

        if new_building.has_ability('TripleCityPopulation'):
            self.population *= 3

        if building_template is not None and building_template.is_wonder:
            assert isinstance(building_template, BuildingTemplate)
            game_state.handle_wonder_built(sess, self.civ, building_template, national=False)

        if building_template is not None and building_template.is_national_wonder:
            assert isinstance(building_template, BuildingTemplate)
            game_state.handle_wonder_built(sess, self.civ, building_template, national=True)

    def get_siege_state(self, game_state: 'GameState') -> Optional[Civ]:
        if self.hex is None:
            return None

        for unit in self.hex.units:
            if unit.civ.id != self.civ.id and unit.template.type == 'military':
                return unit.civ

        # num_neighboring_units_by_civ_name = defaultdict(int)

        # for hex in self.hex.get_neighbors(game_state.hexes):
        #     for unit in hex.units:
        #         if unit.template.type == 'military':
        #             num_neighboring_units_by_civ_name[unit.civ.template.name] += 1

        # for civ_name, num_neighboring_units in num_neighboring_units_by_civ_name.items():
        #     if num_neighboring_units >= 4 and civ_name != self.civ.template.name:
        #         return game_state.get_civ_by_name(civ_name)

        return None

    def capture(self, sess, civ: Civ, game_state: 'GameState') -> None:
        self.civ = civ

        for building in self.buildings:
            if isinstance(building.template, BuildingTemplate) and building.template.is_wonder:
                game_state.wonders_built_to_civ_id[building.template.name] = civ.id

        if civ.game_player and civ.id not in self.ever_controlled_by_civ_ids:
            civ.game_player.score += CITY_CAPTURE_REWARD
            civ.game_player.score_from_capturing_cities_and_camps += CITY_CAPTURE_REWARD
            self.ever_controlled_by_civ_ids[civ.id] = True

            if civ.has_ability('ExtraVpsPerCityCaptured'):
                civ.game_player.score += civ.numbers_of_ability('ExtraVpsPerCityCaptured')[0]
                civ.game_player.score_from_abilities += civ.numbers_of_ability('ExtraVpsPerCityCaptured')[0]

            if civ.has_ability('IncreaseYieldsForTerrain'):
                assert self.hex
                numbers = civ.numbers_of_ability('IncreaseYieldsForTerrain')
                for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                    if hex.terrain == numbers[1]:
                        new_value = getattr(hex.yields, numbers[0]) + numbers[2]
                        setattr(hex.yields, numbers[0], new_value)                

            for wonder in game_state.wonders_built_to_civ_id:
                if game_state.wonders_built_to_civ_id[wonder] == self.civ.id and (abilities := BUILDINGS[wonder]["abilities"]):
                    for ability in abilities:
                        if ability["name"] == "ExtraVpsForCityCapture":
                            civ.game_player.score += ability["numbers"][0]
                            civ.game_player.score_from_abilities += ability["numbers"][0]

        self.under_siege_by_civ = None

        for building in self.buildings:
            if isinstance(building.template, BuildingTemplate) and building.template.is_wonder:
                game_state.wonders_built_to_civ_id[building.template.name] = civ.id

            if isinstance(building.template, BuildingTemplate) and building.template.is_national_wonder:
                if civ.id in game_state.national_wonders_built_by_civ_id:
                    game_state.national_wonders_built_by_civ_id[civ.id].append(building.template.name)
                else:
                    game_state.national_wonders_built_by_civ_id[civ.id] = [building.template.name]

        self.buildings_queue = []

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
    
        self.buildings_queue = []

        self.civ.fill_out_available_buildings(game_state)
        self.refresh_available_buildings()
        self.refresh_available_units()

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
        self.civ = civs_by_id[self.civ.id]
        self.under_siege_by_civ = civs_by_id[self.under_siege_by_civ.id] if self.under_siege_by_civ else None                                    

    def bot_move(self, game_state: 'GameState') -> None:
        self.focus = random.choice(['food', 'metal', 'wood', 'science'])
        available_buildings = self.get_available_buildings()
        if len(available_buildings) > 0:
            self.buildings_queue.append(random.choice(available_buildings))
        available_units = self.available_units
        if len(available_units) > 0:
            # Make the unit queue 5 copies of the strongest unit available
            strongest_unit = None
            for unit in available_units:
                unit_json = UNITS[unit]
                effective_unit_strength = unit_json['strength'] if unit_json['movement'] > 0 else 0.5 * unit_json['strength']
                if strongest_unit is not None:
                    strongest_unit_json = UNITS[strongest_unit]
                    effective_strongest_unit_strength = strongest_unit_json['strength'] if strongest_unit_json['movement'] > 0 else 0.5 * strongest_unit_json['strength']
                else:
                    effective_strongest_unit_strength = 0
                if strongest_unit is None or effective_unit_strength > effective_strongest_unit_strength:
                    strongest_unit = unit

            if strongest_unit is not None:
                self.infinite_queue_unit = UnitTemplate.from_json(UNITS[strongest_unit])

        

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "civ": self.civ.to_json(),
            "ever_controlled_by_civ_ids": self.ever_controlled_by_civ_ids,
            "name": self.name,
            "population": self.population,
            "buildings": [building.to_json() for building in self.buildings],
            "food": self.food,
            "metal": self.metal,
            "wood": self.wood,
            "focus": self.focus,
            "under_siege_by_civ": self.under_siege_by_civ.to_json() if self.under_siege_by_civ else None,
            "hex": self.hex.coords if self.hex else None,
            "infinite_queue_unit": self.infinite_queue_unit.name if self.infinite_queue_unit is not None else "",
            "buildings_queue": [building.building_name if hasattr(building, 'building_name') else building.name for building in self.buildings_queue],  # type: ignore
            "buildings": [building.to_json() for building in self.buildings],
            "available_buildings": self.available_buildings,
            "available_buildings_to_descriptions": self.available_buildings_to_descriptions.copy(),
            "available_building_names": [template.building_name if hasattr(template, 'building_name') else template.name for template in self.get_available_buildings()],  # type: ignore
            "capital": self.capital,
            "available_units": self.available_units,
            "projected_income": self.projected_income,
            "projected_income_base": self.projected_income_base,
            "projected_income_focus": self.projected_income_focus,
            "growth_cost": self.growth_cost(),
            "terrains_dict": self.terrains_dict,
        }

    @staticmethod
    def from_json(json: dict) -> "City":
        city = City(
            civ=Civ.from_json(json["civ"]),
        )
        city.id = json["id"]
        city.ever_controlled_by_civ_ids = json["ever_controlled_by_civ_ids"].copy()
        city.name = json["name"]
        city.population = json["population"]
        city.buildings = [Building.from_json(building) for building in json["buildings"]]
        city.food = json["food"]
        city.metal = json["metal"]
        city.wood = json["wood"]
        city.under_siege_by_civ = Civ.from_json(json["under_siege_by_civ"]) if json["under_siege_by_civ"] else None
        city.capital = json["capital"]
        city.buildings_queue = [UnitTemplate.from_json(UNITS_BY_BUILDING_NAME[building]) if building in UNITS_BY_BUILDING_NAME else BuildingTemplate.from_json(BUILDINGS[building]) for building in json["buildings_queue"]]
        city.available_buildings = json["available_buildings"][:]
        city.available_buildings_to_descriptions = (json.get("available_buildings_to_descriptions") or {}).copy()
        city.available_units = json["available_units"][:]
        city.infinite_queue_unit = None if json["infinite_queue_unit"] == "" else UnitTemplate.from_json(UNITS[json["infinite_queue_unit"]])
        city.focus = json["focus"]
        city.projected_income = json["projected_income"]
        city.projected_income_base = json["projected_income_base"]
        city.projected_income_focus = json["projected_income_focus"]
        city.terrains_dict = json.get("terrains_dict") or {}

        city.handle_cleanup()

        return city


CITY_NAMES = [
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
]


def generate_random_city_name() -> str:
    return random.choice(CITY_NAMES)
