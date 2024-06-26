import random
from typing import TYPE_CHECKING, Callable

from TechStatus import TechStatus
from terrain_template import TerrainTemplate
from unit_templates_list import UNITS
from effect import CityTargetEffect
from unit_template import UnitTemplate

import inflect
p = inflect.engine()

if TYPE_CHECKING:
    from city import City
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
            unit = city.build_unit(unit=self.unit_template, game_state=game_state, stack_size=stack_size)
            if unit is not None:
                unit.strength += self.extra_str

class FreeRandomTechEffect(CityTargetEffect):
    def __init__(self, age) -> None:
        self.age = age

    @property
    def description(self) -> str:
        return f"Learn a random age {self.age} tech for free"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        civ = city.civ

        # try at the right age, but if none available, go down to age below.
        for a in range(self.age, 0, -1):
            available_techs = [tech for tech, status in civ.techs_status.items() if status in {TechStatus.UNAVAILABLE, TechStatus.AVAILABLE} and tech.advancement_level == a]
            if available_techs:
                chosen = random.choice(available_techs)
                civ.gain_tech(tech=chosen, game_state=game_state)
                return

class GainResourceEffect(CityTargetEffect):
    def __init__(self, resource: str, amount: int) -> None:
        assert resource in ("wood", "food", "metal", "science", "city_power")
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
        assert city.hex is not None
        for hex in city.hex.get_distance_2_hexes(game_state.hexes):
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
        return f"Recruit all barbarians within {self.range} tiles (including camps)"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        assert city.hex
        for hex in city.hex.get_hexes_within_range_expensive(game_state.hexes, self.range):
            if len(hex.units) > 0 and hex.units[0].civ == game_state.barbarians:
                hex.units[0].civ = city.civ
            if hex.camp is not None and hex.camp.civ == game_state.barbarians:
                hex.camp.civ = city.civ

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
            c.population -= 1
        

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
        city.civ.get_great_person(game_state.advancement_level - self.age_offset, city)

class ZigguratWarriorsEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return "Your warriors get +1 strength & -5 health"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        for unit in game_state.units:
            if unit.civ == city.civ and unit.template == UNITS.WARRIOR:
                unit.strength += 1
                unit.take_damage(5 * unit.get_stack_size(), game_state=game_state, from_civ=None)

class EndGameEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return "End the game"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        game_state.game_over = True

class IncreaseYieldsForTerrain(CityTargetEffect):
    def __init__(self, resource: str, amount: int, terrain: TerrainTemplate | list[TerrainTemplate], buff_type: str) -> None:
        self.resource = resource
        self.amount = amount
        self.terrain: list[TerrainTemplate] = [terrain] if isinstance(terrain, TerrainTemplate) else terrain
        self.buff_type = buff_type

    @property
    def description(self) -> str:
        terrain_strs: list[str] = [p.plural(t.name) for t in self.terrain] # type: ignore
        terrain_combined_str: str = " and ".join(terrain_strs)
        return f"Increase {self.resource} yields in {terrain_combined_str} around the city by {self.amount}."

    def apply(self, city: 'City', game_state: 'GameState'):
        assert city.hex is not None
        for hex in city.hex.get_neighbors(game_state.hexes, include_self=True):
            if hex.terrain in self.terrain:
                new_value = getattr(hex.yields, self.resource) + self.amount
                setattr(hex.yields, self.resource, new_value)
                hex.buff_counts[self.buff_type] += 1

class IncreaseYieldsInCity(CityTargetEffect):
    def __init__(self, resource: str, amount: int) -> None:
        self.resource = resource
        self.amount = amount

    @property
    def description(self) -> str:
        return f"Increase {self.resource} yields in the city by {self.amount}"

    def apply(self, city: 'City', game_state: 'GameState'):
        assert city.hex is not None
        new_value = getattr(city.hex.yields, self.resource) + self.amount
        setattr(city.hex.yields, self.resource, new_value)

class IncreaseYieldsPerTerrainType(CityTargetEffect):
    def __init__(self, resource: str, amount: int) -> None:
        self.resource = resource
        self.amount = amount

    @property
    def description(self) -> str:
        return f"Increase {self.resource} yields in the city by {self.amount} for each unique terrain type."

    def apply(self, city: 'City', game_state: 'GameState'):
        assert city.hex is not None
        num = len(set([hex.terrain for hex in city.hex.get_neighbors(game_state.hexes, include_self=True)]))
        new_value = getattr(city.hex.yields, self.resource) + self.amount * num
        setattr(city.hex.yields, self.resource, new_value)