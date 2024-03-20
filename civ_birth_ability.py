from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from civ import Civ
from unit_template import UnitTemplate
if TYPE_CHECKING:
    from game_state import GameState
    from city import City

class BirthAbility(ABC):
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def apply(self, sess, civ: Civ, game_state: GameState) -> None:
        pass

    def get_city(self, civ: Civ, game_state: GameState) -> City:
        all_my_cities: list[City] = [city for city in game_state.cities_by_id.values() if city.civ == civ]
        assert len(all_my_cities) == 1, f"Expected 1 city, got {len(all_my_cities)}"
        return all_my_cities[0]

class StartWithUnits(BirthAbility):
    def __init__(self, unit_template: UnitTemplate, num: int):
        self.unit_template: UnitTemplate = unit_template
        self.num: int = num

    def description(self) -> str:
        return f"Start with {self.num} {self.unit_template.name} units"
    
    def apply(self, sess, civ: Civ, game_state: GameState) -> None:
        city: City = self.get_city(civ, game_state)
        for _ in range(self.num):
            city.build_unit(sess, game_state, self.unit_template)

class StartWithUnitBuilding(BirthAbility):
    def __init__(self, unit_template: UnitTemplate):
        self.unit_template: UnitTemplate = unit_template

    def description(self) -> str:
        return f"Start with {self.unit_template.building_name} built."
    
    def apply(self, sess, civ: Civ, game_state: GameState) -> None:
        city: City = self.get_city(civ, game_state)
        city.build_building(sess, game_state, self.unit_template)

class ImproveCapitalTerrain(BirthAbility):
    def __init__(self, resource: str):
        self.resource: str = resource

    def description(self) -> str:
        return f"Improve all terrain around the capital by one yield."
    
    def apply(self, sess, civ: Civ, game_state: GameState) -> None:
        city: City = self.get_city(civ, game_state)
        assert city.hex is not None
        for hex in city.hex.get_neighbors(game_state.hexes):
            if hex.terrain in ("forest", "jungle"):
                hex.yields.wood += 1
            elif hex.terrain in ("plains", "grassland"):
                hex.yields.food += 1
            elif hex.terrain in ("hills", "mountain"):
                hex.yields.metal += 1
            elif hex.terrain in ("desert", "marsh", "tundra"):
                hex.yields.science += 1




