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

if TYPE_CHECKING:
    from hex import Hex
    from game_state import GameState


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
        self.autobuild_unit: Optional[UnitTemplate] = None
        self.units_queue: list[UnitTemplate] = []
        self.buildings_queue: list[Union[UnitTemplate, BuildingTemplate]] = []
        self.buildings: list[Building] = []
        self.available_buildings: list[str] = []
        self.capital = False
        self.available_units: list[str] = []
        self.projected_food_income = 0.0
        self.projected_metal_income = 0.0
        self.projected_wood_income = 0.0
        self.projected_science_income = 0.0
        self.projected_city_power_income = 0.0

        self.handle_cleanup()

    def has_building(self, building_name: str) -> bool:
        return any([(building.template.building_name if hasattr(building.template, 'building_name') else building.template.name) == building_name for building in self.buildings])  # type: ignore

    def building_is_in_queue(self, building_name: str) -> bool:
        return any([(building.building_name if hasattr(building, 'building_name') else building.name) == building_name for building in self.buildings_queue])  # type: ignore

    def adjust_projected_yields(self, game_state: 'GameState') -> None:
        projected_yields = self.get_projected_yields(game_state)

        self.projected_food_income = projected_yields['food']
        self.projected_metal_income = projected_yields['metal']
        self.projected_wood_income = projected_yields['wood']
        self.projected_science_income = projected_yields['science']
        self.projected_city_power_income = projected_yields['city_power']

    def get_projected_yields(self, game_state: 'GameState') -> dict[str, float]:
        if self.hex is None:
            return {
                "food": 0,
                "metal": 0,
                "wood": 0,
                "science": 0,
                "city_power": 0,
            }

        vitality = self.civ.vitality
        yields = defaultdict(float)

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

                if ability.name == 'IncreaseFocusYieldsPerPopulation' and self.focus == ability.numbers[0]:
                    yields_per_population[self.focus] += ability.numbers[1]

        for key in yields_per_population:
            yields[key] += self.population * yields_per_population[key] * vitality

            if key == 'food':
                yields["city_power"] += self.population * yields_per_population[key] * vitality

        yields["food"] += 2 * vitality
        yields["city_power"] += 2 * vitality

        if self.focus == 'food':
            yields["food"] += self.population * vitality
            yields["city_power"] += self.population * vitality
        elif self.focus == 'metal':
            yields["metal"] += self.population * vitality
        elif self.focus == 'wood':
            yields["wood"] += self.population * vitality
        elif self.focus == 'science':
            yields["science"] += self.population * vitality

        if self.civ.has_ability('IncreaseFocusYields') and self.focus == self.civ.numbers_of_ability('IncreaseFocusYields')[0]:
            yields[self.focus] += self.civ.numbers_of_ability('IncreaseFocusYields')[1]

        return yields

    def harvest_yields(self, game_state: 'GameState') -> None:
        if self.hex is None:
            return
        
        vitality = self.civ.vitality

        for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
            self.food += hex.yields.food * vitality
            self.civ.city_power += hex.yields.food * vitality
            self.metal += hex.yields.metal * vitality
            self.wood += hex.yields.wood * vitality
            self.civ.science += hex.yields.science * vitality
        
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
            if key in ["food"]:
                self.food += self.population * yields_per_population[key] * vitality
                self.civ.city_power += self.population * yields_per_population[key] * vitality

            if key in ["metal", "wood"]:
                new_value = getattr(self, key) + self.population * yields_per_population[key] * vitality
                setattr(self, key, new_value)
            
            if key in ["science"]:
                self.civ.science += self.population * yields_per_population[key] * vitality

        self.food += 2 * vitality
        self.civ.city_power += 2 * vitality

        if self.focus == 'food':
            self.food += self.population * vitality
            self.civ.city_power += self.population * vitality
        elif self.focus == 'metal':
            self.metal += self.population * vitality
        elif self.focus == 'wood':
            self.wood += self.population * vitality
        elif self.focus == 'science':
            self.civ.science += self.population * vitality

        if self.civ.has_ability('IncreaseFocusYields') and self.focus == self.civ.numbers_of_ability('IncreaseFocusYields')[0]:
            if self.focus in ['wood', 'metal']:
                new_value = getattr(self, self.focus) + self.civ.numbers_of_ability('IncreaseFocusYields')[1]
                setattr(self, self.focus, new_value)
            elif self.focus in ['food']:
                self.food += self.civ.numbers_of_ability('IncreaseFocusYields')[1]
                self.civ.city_power += self.civ.numbers_of_ability('IncreaseFocusYields')[1]
            elif self.focus in ['science']:
                self.civ.science += self.civ.numbers_of_ability('IncreaseFocusYields')[1]

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

        for hex in [*self.hex.get_hexes_within_distance_2(hexes), self.hex]:
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
                if game_state.wonders_built_to_civ_id[wonder] == self.id and (abilities := BUILDINGS[wonder]["abilities"]):
                    for ability in abilities:
                        if ability["name"] == "ExtraVpsForCityGrowth":
                            self.civ.game_player.score += ability["numbers"][0]    
                            self.civ.game_player.score_from_abilities += ability["numbers"][0]


    def grow(self, game_state: 'GameState') -> None:
        while self.food >= self.growth_cost():
            self.food -= self.growth_cost()
            self.grow_inner(game_state)

    def growth_cost(self) -> int:
        total_growth_cost_reduction = 0

        for building in self.buildings:
            for ability in building.template.abilities:
                if ability.name == 'CityGrowthCostReduction':
                    total_growth_cost_reduction += ability.numbers[0]

        return (BASE_FOOD_COST_OF_POP + self.population * ADDITIONAL_PER_POP_FOOD_COST) * (1 - total_growth_cost_reduction)

    def handle_siege(self, sess, game_state: 'GameState') -> None:
        siege_state = self.get_siege_state(game_state)

        if self.under_siege_by_civ is None:
            self.under_siege_by_civ = siege_state
        else:
            if siege_state is None or siege_state.id != self.under_siege_by_civ.id:
                self.under_siege_by_civ = siege_state
            else:
                self.capture(sess, siege_state, game_state)

    def refresh_available_buildings(self) -> None:
        self.available_buildings = [building_name for building_name in self.civ.available_buildings if not self.has_building(building_name) and not self.building_is_in_queue(building_name)]

    def refresh_available_units(self) -> None:
        self.available_units = [unit['name'] for unit in UNITS.values() if unit['building_name'] is None or self.has_production_building_for_unit(unit['name'])]

    def has_production_building_for_unit(self, unit_name: str) -> bool:
        return self.has_building(PRODUCTION_BUILDINGS_BY_UNIT_NAME[unit_name])

    def handle_cleanup(self) -> None:
        self.refresh_available_units()
        self.refresh_available_buildings()

    def get_available_buildings(self, game_state: 'GameState') -> list[Union[BuildingTemplate, UnitTemplate]]:
        building_names_in_queue = [building.building_name if hasattr(building, 'building_name') else building.name for building in self.buildings_queue]  # type: ignore
        buildings = [BuildingTemplate.from_json(BUILDINGS[building_name]) for building_name in self.available_buildings if not building_name in building_names_in_queue and not self.has_building(building_name)]
        unit_buildings = [UnitTemplate.from_json(UNITS_BY_BUILDING_NAME[building_name]) for building_name in self.civ.available_unit_buildings if not building_name in building_names_in_queue and not self.has_building(building_name)]
        return [*buildings, *unit_buildings]

    def build_units(self, sess, game_state: 'GameState') -> None:
        if self.autobuild_unit is not None:
            while self.metal >= self.autobuild_unit.metal_cost:
                if self.build_unit(sess, game_state, self.autobuild_unit):
                    self.metal -= self.autobuild_unit.metal_cost
                else: 
                    break
        else:
            while self.units_queue and self.metal >= self.units_queue[0].metal_cost:
                unit = self.units_queue[0]
                if self.metal >= unit.metal_cost:
                    self.units_queue.pop(0)
                    self.build_unit(sess, game_state, unit)
                    self.metal -= unit.metal_cost

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

        for hex in self.hex.get_neighbors(game_state.hexes):
            if not hex.is_occupied(unit.type, self.civ):
                distance_from_target = hex.distance_to(self.get_closest_target() or self.hex)
                if distance_from_target < best_hex_distance_from_target:
                    best_hex = hex
                    best_hex_distance_from_target = distance_from_target

        if best_hex is None:
            for hex in self.hex.get_distance_2_hexes(game_state.hexes):
                if not hex.is_occupied(unit.type, self.civ):
                    distance_from_target = hex.distance_to(self.get_closest_target() or self.hex)
                    if distance_from_target < best_hex_distance_from_target:
                        best_hex = hex
                        best_hex_distance_from_target = distance_from_target            

        if best_hex is None:
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

        if new_building.has_ability('IncreaseYieldsForTerrain'):
            assert self.hex
            numbers = new_building.numbers_of_ability('IncreaseYieldsForTerrain')
            for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                if hex.terrain == numbers[2]:
                    new_value = getattr(hex.yields, numbers[0]) + numbers[1]
                    setattr(hex.yields, numbers[0], new_value)

        if new_building.has_ability('DoubleYieldsForTerrainInCity'):
            assert self.hex
            numbers = new_building.numbers_of_ability('DoubleYieldsForTerrainInCity')
            for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
                if hex.terrain == numbers[0]:
                    new_value = getattr(hex.yields, numbers[1]) * 2
                    setattr(hex.yields, numbers[1], new_value)

        if new_building.has_ability('ExistingUnitsGainBonusStrength'):
            for unit in game_state.units:
                if unit.civ.id == self.civ.id:
                    unit.strength += new_building.numbers_of_ability('ExistingUnitsGainBonusStrength')[0]

        if new_building.has_ability('IncreaseYieldsInCity'):
            assert self.hex
            numbers = new_building.numbers_of_ability('IncreaseYieldsForTerrain')
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

        if civ.game_player and civ.id not in self.ever_controlled_by_civ_ids:
            civ.game_player.score += CITY_CAPTURE_REWARD
            civ.game_player.score_from_capturing_cities_and_camps += CITY_CAPTURE_REWARD
            self.ever_controlled_by_civ_ids[civ.id] = True

            if civ.has_ability('ExtraVpsPerCityCaptured'):
                civ.game_player.score += civ.numbers_of_ability('ExtraVpsPerCityCaptured')[0]
                civ.game_player.score_from_abilities += civ.numbers_of_ability('ExtraVpsPerCityCaptured')[0]

            for wonder in game_state.wonders_built_to_civ_id:
                if game_state.wonders_built_to_civ_id[wonder] == self.id and (abilities := BUILDINGS[wonder]["abilities"]):
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

        if self.hex:
            game_state.add_animation_frame(sess, {
                "type": "CityCapture",
                "civ": civ.template.name,
                "city": self.name,
                "vpReward": CITY_CAPTURE_REWARD,
            }, hexes_must_be_visible=[self.hex])

    def capitalize(self) -> None:
        civ = self.civ
        self.capital = True
    
        if civ.has_ability('IncreaseCapitalYields'):
            if self.hex:
                self.hex.yields.increase(civ.numbers_of_ability('IncreaseCapitalYields')[0],
                                            civ.numbers_of_ability('IncreaseCapitalYields')[1])
                
    def update_civ_by_id(self, civs_by_id: dict[str, Civ]) -> None:
        self.civ = civs_by_id[self.civ.id]
        self.under_siege_by_civ = civs_by_id[self.under_siege_by_civ.id] if self.under_siege_by_civ else None                                    

    def bot_move(self, game_state: 'GameState') -> None:
        self.focus = random.choice(['food', 'metal', 'wood', 'science'])
        available_buildings = self.get_available_buildings(game_state)
        if len(available_buildings) > 0:
            self.buildings_queue.append(random.choice(available_buildings))
        available_units = self.available_units
        if len(available_units) > 0:
            self.units_queue.append(UnitTemplate.from_json(UNITS[random.choice(available_units)]))
        

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
            "autobuild_unit": self.autobuild_unit.name if self.autobuild_unit else None,
            "units_queue": [unit.name for unit in self.units_queue],
            "buildings_queue": [building.building_name if hasattr(building, 'building_name') else building.name for building in self.buildings_queue],  # type: ignore
            "buildings": [building.to_json() for building in self.buildings],
            "available_buildings": self.available_buildings,
            "available_building_names": [template.building_name if hasattr(template, 'building_name') else template.name for template in self.get_available_buildings(None)],  # type: ignore
            "capital": self.capital,
            "available_units": self.available_units,
            "projected_food_income": self.projected_food_income,
            "projected_metal_income": self.projected_metal_income,
            "projected_wood_income": self.projected_wood_income,
            "projected_science_income": self.projected_science_income,
            "projected_city_power_income": self.projected_city_power_income,
            "growth_cost": self.growth_cost(),
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
        city.available_units = json["available_units"][:]
        city.units_queue = [UnitTemplate.from_json(UNITS[unit]) for unit in json["units_queue"]]
        city.focus = json["focus"]
        city.projected_food_income = json["projected_food_income"]
        city.projected_metal_income = json["projected_metal_income"]
        city.projected_wood_income = json["projected_wood_income"]
        city.projected_science_income = json["projected_science_income"]
        city.projected_city_power_income = json["projected_city_power_income"]

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
