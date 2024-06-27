from abc import ABC, abstractmethod, abstractproperty
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from city import City
    from civ import Civ
    from game_state import GameState

class Effect(ABC):
    @abstractproperty
    def description(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def apply_to_city(self, city: 'City', game_state: 'GameState'):
        raise NotImplementedError
    
    @abstractmethod
    def apply_to_civ(self, civ: 'Civ', game_state: 'GameState'):
        raise NotImplementedError

class CityTargetEffect(Effect):    
    def apply_to_civ(self, civ: 'Civ', game_state: 'GameState'):
        target = civ.primary_city(game_state)
        if target is not None:
            self.apply_to_city(target, game_state)

class CivTargetEffect(Effect):
    def apply_to_city(self, city: 'City', game_state: 'GameState'):
        self.apply_to_civ(city.civ, game_state)