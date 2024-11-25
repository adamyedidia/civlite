import random
from typing import TYPE_CHECKING, Callable, Literal

from TechStatus import TechStatus
from building_template import BuildingTemplate, BuildingType
from settings import STRICT_MODE, VITALITY_DECAY_RATE
from terrain_template import TerrainTemplate
from terrain_templates_list import TERRAINS
from unit_templates_list import UNITS
from effect import CityTargetEffect
from unit_template import UnitTemplate
from logging_setup import logger


import inflect

from yields import Yields
p = inflect.engine()

if TYPE_CHECKING:
    from city import City
    from civ import Civ
    from game_state import GameState
    from hex import Hex

class NullEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return ""

    def apply(self, city: 'City', game_state: 'GameState'):
        pass

class BuildUnitsEffect(CityTargetEffect):
    def __init__(self, unit_template: UnitTemplate, num: int, stacked: bool=False, extra_str: int=0) -> None:
        self.unit_template = unit_template
        self.num = num
        self.stacked = stacked
        self.extra_str = extra_str

    @property
    def description(self) -> str:
        name = self.unit_template.name
        if self.num == 1:
            desc =  f"Build a free {name}"
        else:
            desc = f"Build {self.num} free {p.plural(name)}"  # type: ignore
        if self.extra_str > 0:
            desc += f" with +{self.extra_str} strength"
        return desc

    def apply(self, city: 'City', game_state: 'GameState'):
        stack_size = self.num if self.stacked else 1
        num_stacks = 1 if self.stacked else self.num

        for _ in range(num_stacks):
            unit = city.build_unit(unit=self.unit_template, game_state=game_state, stack_size=stack_size, bonus_strength=self.extra_str)

class BuildBuildingEffect(CityTargetEffect):
    def __init__(self, building_template: BuildingTemplate) -> None:
        self.building_template = building_template

    @property
    def description(self) -> str:
        return f"Build a free {self.building_template.name}."

    def apply(self, city: 'City', game_state: 'GameState'):
        if not city.has_building(self.building_template):
            city.build_building(building=self.building_template, game_state=game_state, free=True)

class FreeRandomTechEffect(CityTargetEffect):
    def __init__(self, age, number=1) -> None:
        self.age = age
        self.number = number

    @property
    def description(self) -> str:
        return f"Learn {self.number} random age {self.age} {p.plural('tech', self.number)} for free"  # type: ignore
    
    def learn_one_tech(self, civ: 'Civ', game_state: 'GameState'):
        # try at the right age, but if none available, go down to age below.
        for a in range(self.age, 0, -1):
            available_techs = [tech for tech, status in civ.techs_status.items() if status in {TechStatus.UNAVAILABLE, TechStatus.AVAILABLE} and tech.advancement_level == a]
            if available_techs:
                chosen = random.choice(available_techs)
                civ.gain_tech(tech=chosen, game_state=game_state)
                return

    def apply(self, city: 'City', game_state: 'GameState'):
        civ = city.civ
        for _ in range(self.number):
            self.learn_one_tech(civ, game_state)

class GainResourceEffect(CityTargetEffect):
    def __init__(self, resource: Literal["wood", "food", "metal", "science", "city_power"], amount: int) -> None:
        self.resource = resource
        self.amount = amount

    @property
    def description(self) -> str:
        return f"Gain {self.amount} {self.resource}"

    def apply(self, city: 'City', game_state: 'GameState'):
        if self.resource == 'food':
            city.food += self.amount
        elif self.resource == 'wood':
            city.wood += self.amount
        elif self.resource == 'metal':
            city.metal += self.amount
        elif self.resource == 'science':
            city.civ.science += self.amount
        elif self.resource == 'city_power':
            city.civ.city_power += self.amount

class GainUnhappinessEffect(CityTargetEffect):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    @property
    def description(self) -> str:
        return f"Gain {self.amount} unhappiness"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        city.unhappiness += self.amount

class GrowEffect(CityTargetEffect):
    def __init__(self, amount: int | None = None, amount_fn: Callable[['City', 'GameState'], int] | None = None, description: str | None =None) -> None:
        assert (amount is None) != (amount_fn is None), "amount and amount_fn are mutually exclusive"
        self.amount = amount
        self.amount_fn = amount_fn
        if amount_fn is not None:
            assert description is not None, "description is required for amount_fn"
            self._description: str = description
        else:
            self._description = f"Grow {self.amount} population"

    def get_amount(self, city: 'City', game_state: 'GameState') -> int:
        if self.amount_fn is not None:
            return self.amount_fn(city, game_state)
        elif self.amount is not None:
            return self.amount
        else:
            raise ValueError("amount or amount_fn must be provided")

    @property
    def description(self) -> str:
        return self._description

    def apply(self, city: 'City', game_state: 'GameState'):
        for _ in range(self.get_amount(city, game_state)):
            city.grow_inner(game_state=game_state)

class FreeNearbyCityEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return f"Build a free nearby city with 20 unhappiness"

    def apply(self, city: 'City', game_state: 'GameState'):
        my_civ = city.civ
        def valid_spot(hex: 'Hex') -> bool:
            if hex.camp is not None:
                return False
            if len(hex.units) > 0 and hex.units[0].civ != my_civ:
                return False
            for neighbor in hex.get_neighbors(game_state.hexes, include_self=True):
                if neighbor.city is not None:
                    return False
            return True
        for hex in city.hex.get_distance_2_hexes(game_state.hexes, exclude_ocean=True):
            if valid_spot(hex):
                city.civ.city_power += 100
                city = game_state.found_city_for_civ(civ=city.civ, city_id=None, hex=hex)
                city.unhappiness = 20
                return
            
class RecruitBarbariansEffect(CityTargetEffect):
    def __init__(self, range: int) -> None:
        self.range = range

    @property
    def description(self) -> str:
        return f"Recruit all barbarians within {self.range} tiles (including camps). Your camps produce double units."
    
    def apply(self, city: 'City', game_state: 'GameState'):
        for hex in city.hex.get_hexes_within_range_expensive(game_state.hexes, self.range):
            if len(hex.units) > 0 and hex.units[0].civ == game_state.barbarians:
                hex.units[0].update_civ(city.civ)
            if hex.camp is not None and hex.camp.civ == game_state.barbarians:
                hex.camp.update_civ(city.civ)

class PointsEffect(CityTargetEffect):
    def __init__(self, calculate_points: Callable[['City', 'GameState'], int], description: str, label: str) -> None:
        self.calculate_points = calculate_points
        self._description = description
        self._label = label

    @property
    def description(self) -> str:
        return self._description
    
    def apply(self, city: 'City', game_state: 'GameState'):
        value = self.calculate_points(city, game_state)
        city.civ.gain_vps(value, self._label)


class StrengthAllUnitsEffect(CityTargetEffect):
    def __init__(self, amount: int) -> None:
        self.amount = amount

    @property
    def description(self) -> str:
        return f"All your existing units gain {self.amount} strength"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        for unit in game_state.units:
            if unit.civ == city.civ:
                unit.strength += self.amount

class StealPopEffect(CityTargetEffect):
    def __init__(self, num: int, cities: int) -> None:
        self.num = num
        self.cities = cities

    @property
    def description(self) -> str:
        return f"Steal {self.num} population from the {self.cities} unhappiest cities"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        all_cities = list(game_state.cities_by_id.values())
        all_cities.sort(key=lambda c: c.unhappiness, reverse=True)
        for c in all_cities[:self.cities]:
            city.grow_inner(game_state=game_state)
            if c.population > 1:
                c.population -= 1
            else:
                c.barbarian_capture(game_state=game_state)
        

class ResetHappinessThisCityEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return "Reset the happiness in this city to 0 (before income)"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        city.unhappiness = 0

class ResetHappinessAllCitiesEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return "Reset the happiness in all your cities to zero (before income)"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        for c in city.civ.get_my_cities(game_state=game_state):
            c.unhappiness = 0

class GetGreatPersonEffect(CityTargetEffect):
    def __init__(self, age_offset: int) -> None:
        self.age_offset: int = age_offset

    @property
    def description(self) -> str:
        return f"Get a great person from {p.number_to_words(self.age_offset)} {p.plural('age', self.age_offset)} ago."  # type: ignore
    
    def apply(self, city: 'City', game_state: 'GameState'):
        city.civ.get_great_person(game_state.advancement_level - self.age_offset, city, game_state)

class ZigguratWarriorsEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return "One warrior gets +1 strength & -20 health"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        my_warriors = [unit for unit in game_state.units if unit.civ == city.civ and unit.template == UNITS.WARRIOR]
        prefer_smaller_stacks = sorted(my_warriors, key=lambda u: (u.get_stack_size(), u.strength, random.random()))
        if len(prefer_smaller_stacks) > 0:
            unit = prefer_smaller_stacks[0]
            unit.strength += 1
            unit.take_damage(20 * unit.get_stack_size(), game_state=game_state, from_civ=None)

class EndGameEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return "End the game"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        game_state.game_over = True

class BuildEeachUnitEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return "Build one free unit of each type this city can build."
    
    def apply(self, city: 'City', game_state: 'GameState'):
        for unit in city.available_units:
            city.build_unit(game_state=game_state, unit=unit)

class GreatWallEffect(CityTargetEffect):
    def __init__(self, num_garrisons: int) -> None:
        self.num_garrisons = num_garrisons

    @property
    def description(self) -> str:
        return f"Build {self.num_garrisons} garrisons around your border"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        my_cities = city.civ.get_my_cities(game_state=game_state)
        all_distance_2 = {hex for c in my_cities for hex in c.hex.get_distance_2_hexes(game_state.hexes, exclude_ocean=True)}
        # Remove ones that are interior
        border_hexes = {hex for hex in all_distance_2 if min(hex.distance_to(c.hex) for c in my_cities) == 2}
        # if any contain an enemy, add the ones closer.
        for _ in range(2):
            for hex in border_hexes.copy():
                if hex.city or hex.camp or any(u.civ != city.civ for u in hex.units):
                    border_hexes.remove(hex)
                    for n in hex.get_neighbors(game_state.hexes, include_self=False, exclude_ocean=True):
                        if min(n.distance_to(c.hex) for c in my_cities) <= 1:
                            border_hexes.add(n)
        # Remove any that still contain a unit
        border_hexes = {hex for hex in border_hexes if not hex.is_occupied(UNITS.GARRISON.type, city.civ)}
        built_hexes = set()
        for _ in range(self.num_garrisons):
            if len(border_hexes) > 0:
                hex = random.choice(list(border_hexes))
                success = city.civ.spawn_unit_on_hex(game_state=game_state, unit_template=UNITS.GARRISON, hex=hex, bonus_strength=0)
                if success:
                    built_hexes.add(hex)
                    for n in hex.get_neighbors(game_state.hexes, include_self=True):
                        if n in border_hexes:
                            border_hexes.remove(n)
                else:
                    if STRICT_MODE:
                        raise ValueError(f"Failed to build garrison on {hex.q}, {hex.r}, {hex.s}")
                    else: 
                        logger.warning(f"Failed to build garrison on {hex.q}, {hex.r}, {hex.s}")
            elif len(built_hexes) > 0:
                hex = min(built_hexes, key=lambda h: (h.units[0].get_stack_size(), random.random()))
                unit = hex.units[0]
                city.reinforce_unit(unit=unit)
                if unit.get_stack_size() >= 3:
                    built_hexes.remove(hex)
            else:
                city = random.choice(my_cities)
                city.build_unit(game_state=game_state, unit=UNITS.GARRISON)
        return
    
class GainSlotsEffect(CityTargetEffect):
    def __init__(self, num: int, type: BuildingType, free_building: BuildingTemplate | None = None) -> None:
        self.num = num
        self.type = type
        self.free_building = free_building
        assert self.free_building is None or self.free_building.type == self.type

    @property
    def description(self) -> str:
        if self.free_building is not None:
            return f"Gain {self.num} free {self.type.value} {p.plural('slot', self.num)} with a free {self.free_building.name}."  # type: ignore
        else:
            return f"Gain {self.num} free {self.type.value} {p.plural('slot', self.num)}."  # type: ignore
    
    def apply(self, city: 'City', game_state: 'GameState'):
        for _ in range(self.num):
            # Need a rural slot no matter what
            city.develop(BuildingType.RURAL, game_state, free=True)
            # If it's supposed to be an advanced on, turn a rural into it.
            if self.type in (BuildingType.URBAN, BuildingType.UNIT):
                city.develop(self.type, game_state, free=True)
        if self.free_building is not None:
            city.build_building(game_state=game_state, building=self.free_building, free=True)

class GreatLighthouseEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return "Reduce vitality decay rate by 5% per adjacent ocean tile"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        num_ocean_neighbors = city.terrains_dict.get(TERRAINS.OCEAN, 0)
        vitality_decay_reduction = 1 - 0.05 * num_ocean_neighbors
        new_vitality_decay_rate = 1 - (1 - VITALITY_DECAY_RATE) * vitality_decay_reduction
        city.civ.vitality *= new_vitality_decay_rate / VITALITY_DECAY_RATE

class UpgradeTerrainEffect(CityTargetEffect):
    def __init__(self, num: int, terrain: TerrainTemplate, override_yields: Yields, override_name: str | None = None) -> None:
        self.num = num
        self.terrain = terrain
        self.total_yields = override_yields or terrain.yields
        self.display_name = override_name or terrain.name

    @property
    def description(self) -> str:
        return f"Upgrade {self.num} adjacent tiles to {self.display_name} (yields {self.total_yields.pretty_print()})"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        neighbors = list(city.hex.get_neighbors(game_state.hexes, include_self=False))
        for hex in random.sample(neighbors, self.num):
            old_terrain_type = hex.terrain
            hex.terrain = self.terrain
            hex.yields = self.total_yields
            for possible_city in hex.get_neighbors(game_state.hexes, include_self=False):
                if possible_city.city is not None:
                    if possible_city.city.terrains_dict[old_terrain_type] == 1:
                        del possible_city.city.terrains_dict[old_terrain_type]
                    else:
                        possible_city.city.terrains_dict[old_terrain_type] -= 1
                    if self.terrain in possible_city.city.terrains_dict:
                        possible_city.city.terrains_dict[self.terrain] += 1
                    else:
                        possible_city.city.terrains_dict[self.terrain] = 1

