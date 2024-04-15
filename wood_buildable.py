from typing import TYPE_CHECKING, Optional

import abc

if TYPE_CHECKING:
    from civ import Civ
    from ability import Ability
    from tech_template import TechTemplate

class WoodBuildable(abc.ABC):
    """
    Base class for anything that a city can build out of wood.
    """
    def __init__(self, building_name: str):
        self.building_name: str = building_name
        # Tech that is needed to build this. Used on decline to make sure you get all the techs that unlock the buildings you have.
        self.prereq: Optional['TechTemplate'] = None

    @abc.abstractmethod

    def building_cost_for_civ(self, civ: 'Civ') -> float:
        raise NotImplementedError()

    def get_abilities(self) -> list['Ability']:
        return []

    def has_ability(self, ability_name: str) -> bool:
        return False

    def numbers_of_ability(self, ability_name: str) -> list:
        return []

    @abc.abstractmethod
    def to_json(self) -> dict:
        raise NotImplementedError()

