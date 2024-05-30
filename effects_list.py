import random
from typing import TYPE_CHECKING

from city import City
from civ import TechStatus
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
    def __init__(self, unit_template: UnitTemplate, num: int) -> None:
        self.unit_template = unit_template
        self.num = num

    @property
    def description(self) -> str:
        name = self.unit_template.name
        if self.num == 1:
            return f"Build a free {name}"
        return f"Build {self.num} free {p.plural(name)}"  # type: ignore

    def apply(self, city: 'City', game_state: 'GameState'):
        for _ in range(self.num):
            city.build_unit(unit=self.unit_template, game_state=game_state)

class FreeRandomTechEffect(CityTargetEffect):
    def __init__(self, age) -> None:
        self.age = age

    @property
    def description(self) -> str:
        return f"Learn a free age {self.age} tech"
    
    def apply(self, city: 'City', game_state: 'GameState'):
        civ = city.civ

        # try at the right age, but if none available, go down to age below.
        for a in range(self.age, 0, -1):
            available_techs = [tech for tech, status in civ.techs_status.items() if status == TechStatus.AVAILABLE and tech.advancement_level == a]
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
    def __init__(self, amount: int) -> None:
        self.amount = amount

    @property
    def description(self) -> str:
        return f"Gain {self.amount} population"

    def apply(self, city: 'City', game_state: 'GameState'):
        for _ in range(self.amount):
            city.grow_inner(game_state=game_state)

class FreeNearbyCityEffect(CityTargetEffect):
    @property
    def description(self) -> str:
        return f"Build a free nearby city 20 unhappiness"

    def apply(self, city: City, game_state: GameState):
        my_civ = city.civ
        def valid_spot(hex: 'Hex') -> bool:
            if hex.camp is not None:
                return False
            if len(hex.units) > 0 and hex.units[0].civ != my_civ:
                return False
            for neighbor in hex.get_neighbors(game_state.hexes):
                if neighbor.city is not None:
                    return False
            return True
        assert city.hex is not None
        for hex in city.hex.get_distance_2_hexes(game_state.hexes):
            if valid_spot(hex):
                city = game_state.found_city_for_civ(civ=city.civ, city_id=None, hex=hex)
                city.unhappiness = 20
                return
            
class RecruitBarbariansEffect(CityTargetEffect):
    def __init__(self, range: int) -> None:
        self.range = range

    @property
    def description(self) -> str:
        return f"Recruit all barbarians within {self.range} tiles"
    
    def apply(self, city: City, game_state: GameState):
        assert city.hex
        for hex in city.hex.get_hexes_within_range(game_state.hexes, self.range):
            if len(hex.units) > 0 and hex.units[0].civ == game_state.barbarians:
                hex.units[0].civ = city.civ
