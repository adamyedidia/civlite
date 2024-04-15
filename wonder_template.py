from typing import TYPE_CHECKING, Union
import abc
import inflect


if TYPE_CHECKING:
    from city import City
    from civ import Civ
    from game_state import GameState

p = inflect.engine()

class CityTargetEffect(abc.ABC):
    @abc.abstractmethod
    def __call__(self, city: 'City', game_state: 'GameState'):
        raise NotImplementedError

    @abc.abstractproperty
    def description(self) -> str:
        raise NotImplementedError

class WonderBoostCheck(abc.ABC):
    @abc.abstractmethod
    def __call__(self, civ: 'Civ', game_state: 'GameState') -> bool:
        raise NotImplementedError

    @abc.abstractproperty
    def description(self) -> str:
        raise NotImplementedError

class WonderTemplate():
    def __init__(self, 
                 name: str, 
                 advancement_level: int, 
                 on_build_effects: list[CityTargetEffect],
                 boost_check: WonderBoostCheck):
        self.name = name
        self.advancement_level: int = advancement_level
        self.on_build_effects: list[CityTargetEffect] = on_build_effects
        self.boost_check: WonderBoostCheck = boost_check
        self.base_cost: int = self.advancement_level * 30

    def to_json(self):
        return {
            'name': self.name,
            'advancement_level': self.advancement_level,
            'on_build_abilities': [ability.description for ability in self.on_build_effects],
            'boost_check': self.boost_check.description,
        }


