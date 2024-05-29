from abc import ABC, abstractmethod, abstractproperty
from typing import TYPE_CHECKING

from unit_template import UnitTemplate

if TYPE_CHECKING:
    from city import City
    from game_state import GameState

import inflect
p = inflect.engine()

class CityTargetEffect(ABC):
    @abstractproperty
    def description(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def apply(self, city: 'City', game_state: 'GameState'):
        raise NotImplementedError

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
