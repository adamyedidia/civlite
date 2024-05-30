from abc import ABC, abstractmethod, abstractproperty
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from city import City
    from game_state import GameState

class CityTargetEffect(ABC):
    @abstractproperty
    def description(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def apply(self, city: 'City', game_state: 'GameState'):
        raise NotImplementedError

