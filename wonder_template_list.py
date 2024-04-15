from typing import TYPE_CHECKING, Generator

import inflect

from unit_template import UnitTemplate
from tech_template import TechTemplate

from tech_templates_list import TECHS
from unit_templates_list import UNITS
from wonder_template import WonderTemplate, CityTargetEffect, WonderBoostCheck

if TYPE_CHECKING:
    from city import City
    from civ import Civ
    from game_state import GameState

p = inflect.engine()

class FreeUnits(CityTargetEffect):
    def __init__(self, unit_template: UnitTemplate, number: int):
        self.unit_template: UnitTemplate = unit_template
        self.number: int = number

    def __call__(self, city: 'City', game_state: 'GameState'):
        for _ in range(self.number):
            city.build_unit(game_state, self.unit_template)

    @property
    def description(self) -> str:
        return f"Immediately build {self.number} free {p.plural(self.unit_template.name)}"  # type: ignore

class GainPopulation(CityTargetEffect):
    def __init__(self, number: int):
        self.number: int = number

    def __call__(self, city: 'City', game_state: 'GameState'):
        for _ in range(self.number):
            city.grow_inner(game_state)

    @property
    def description(self) -> str:
        return f"Immediately gain {self.number} population"
    
class GainCityPower(CityTargetEffect):
    def __init__(self, number: int):
        self.number: int = number

    def __call__(self, city: 'City', game_state: 'GameState'):
        city.civ.city_power += self.number

    @property
    def description(self) -> str:
        return f"Immediately gain {self.number} city power"

class HasTech(WonderBoostCheck):
    def __init__(self, tech_template: TechTemplate):
        self.tech_template: TechTemplate = tech_template

    def __call__(self, civ: 'Civ', game_state: 'GameState') -> bool:
        return civ.has_tech(self.tech_template)

    @property
    def description(self) -> str:
        return f"Research {self.tech_template.name}"

class TotalPopulation(WonderBoostCheck):
    def __init__(self, number: int):
        self.number: int = number

    def __call__(self, civ: 'Civ', game_state: 'GameState') -> bool:
        return sum(city.population for city in civ.get_my_cities(game_state)) >= self.number

    @property
    def description(self) -> str:
        return f"Have {self.number} total population"

class WONDERS():
    TEMPLE_OF_ARTEMIS = WonderTemplate(
        name="Temple of Artemis",
        advancement_level=1,
        on_build_effects=[FreeUnits(unit_template=UNITS.ARCHER, number=3)],
        boost_check=HasTech(tech_template=TECHS.CALENDAR),
    )

    HANGING_GARDENS = WonderTemplate(
        name="Hanging Gardens",
        advancement_level=1,
        on_build_effects=[GainPopulation(5)],
        boost_check=HasTech(tech_template=TECHS.CODE_OF_LAWS),
    )

    PYRAMIDS = WonderTemplate(
        name="Pyramids",
        advancement_level=1,
        on_build_effects=[GainCityPower(100)],
        boost_check=TotalPopulation(7),
    )

    # all & by_name are copy-pasted methods to all template lists.
    # I wasn't able to set up a base class system for this
    # That handled the dynamic type properly.
    @classmethod
    def all(cls) -> Generator[WonderTemplate, None, None]:
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), WonderTemplate):
                yield getattr(cls, attr)
    @classmethod
    def by_name(cls, name: str) -> WonderTemplate:
        for item in cls.all():
            if item.name == name:
                return item
        raise KeyError(f'No item with name {name}')