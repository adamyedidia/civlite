from __future__ import annotations

import abc
from collections import defaultdict
import random
from typing import TYPE_CHECKING, Optional

from tech_templates_list import TECHS
from tech_template import TechTemplate
from unit_template import UnitTemplate
from unit_templates_list import UNITS

if TYPE_CHECKING:
    from city import City

class GreatPerson(abc.ABC):
    def __init__(self, name: str, hover_entity_type: Optional[str] = None, hover_entity_name: Optional[str] = None):
        self.name: str = name
        self.hover_entity_type: Optional[str] = hover_entity_type
        self.hover_entity_name: Optional[str] = hover_entity_name

    @abc.abstractmethod
    def description(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def apply(self, game_state, city: City):
        # TODO remove sess?
        raise NotImplementedError()
    
    def to_json(self):
        return {
            "name": self.name,
            "description": self.description(),
            "hover_entity_type": self.hover_entity_type,
            "hover_entity_name": self.hover_entity_name,
            }
    
    @staticmethod
    def from_json(json) -> "GreatPerson":
        return great_people_by_name[json["name"]]

class GreatGeneral(GreatPerson):
    def __init__(self, name, unit_template: UnitTemplate, number: int):
        self.unit_template: UnitTemplate = unit_template
        self.number: int = number
        super().__init__(name, hover_entity_type="unit", hover_entity_name=unit_template.name)

    def description(self) -> str:
        return f"Immediately build {self.number} free {self.unit_template.name}s"

    def apply(self, game_state, city: City):
        for _ in range(self.number):
            city.build_unit(game_state, self.unit_template)

class GreatMerchant(GreatPerson):
    def __init__(self, name, amount: float, resource: str):
        self.amount: float = amount
        self.resource: str = resource
        super().__init__(name)

    def description(self) -> str:
        return f"Immediately gain {self.amount} {self.resource}"

    def apply(self, game_state, city: City):
        if self.resource == "metal":
            city.metal += self.amount
        elif self.resource == "wood":
            city.wood += self.amount
        elif self.resource == "food":
            city.food += self.amount
            city.grow(game_state)
        elif self.resource == "science":
            city.civ.science += self.amount

class GreatScientist(GreatPerson):
    def __init__(self, name, tech_template: TechTemplate):
        self.tech_template: TechTemplate = tech_template
        super().__init__(name, hover_entity_type="tech", hover_entity_name=tech_template.name)

    def description(self) -> str:
        return f"Immediately learn {self.tech_template.name}"

    def apply(self, game_state, city: City):
        city.civ.gain_tech(game_state, self.tech_template)

class GreatEngineer(GreatPerson):
    def __init__(self, name, unit_template: UnitTemplate, extra_wood: float):
        self.unit_template: UnitTemplate = unit_template
        self.extra_wood: float = extra_wood
        super().__init__(name, hover_entity_type="unit", hover_entity_name=unit_template.building_name)

    def description(self) -> str:
        desc: str = f"Immediately build a free {self.unit_template.building_name}"
        if self.extra_wood > 0:
            desc += f" and gain {int(self.extra_wood)} wood."
        return desc

    def apply(self, game_state, city: City):
        city.build_building(game_state, self.unit_template)
        city.refresh_available_units()
        city.wood += self.extra_wood

_great_people_by_age: dict[int, list[GreatPerson]] = defaultdict(list)

def _target_value_by_age(age: int) -> int:
    return {
        0: 30,
        1: 60,
        2: 100,
        3: 150,
        4: 200,
        5: 250,
        6: 300,
        7: 400,
        8: 600,
        9: 800,
        10: 1600,
    }[age]

for resource in ["metal", "wood", "food", "science"]:
    for age in range(10):
        _great_people_by_age[age].append(GreatMerchant(f"A{age} Merchant: {resource}", _target_value_by_age(age), resource))

for tech in TECHS.values():
    t = TechTemplate.from_json(tech)
    level = t.advancement_level
    _great_people_by_age[level - 1].append(GreatScientist(f"A{level - 1} Scientist: {t.name}", t))
    for unit in t.unlocks_units:
        u = UnitTemplate.from_json(UNITS[unit])
        _great_people_by_age[level - 1].append(GreatGeneral(f"A{level - 1} General: {unit}", u, int(0.4 * _target_value_by_age(level - 1) / u.metal_cost)))
        _great_people_by_age[level].append(GreatGeneral(f"A{level} General: {unit}", u, int(0.7 * _target_value_by_age(level) / u.metal_cost)))
        _great_people_by_age[level + 1].append(GreatGeneral(f"A{level + 1} General: {unit}", u, int(1.0 * _target_value_by_age(level + 1) / u.metal_cost)))

        _great_people_by_age[level - 1].append(GreatEngineer(f"A{level - 1} Engineer: {unit}", u, max(0, 0.5 * _target_value_by_age(level - 1) - u.wood_cost)))


great_people_by_name: dict[str, GreatPerson] = {great_person.name: great_person for great_person_list in _great_people_by_age.values() for great_person in great_person_list}

def random_great_people_by_age(age: int, n: int = 1) -> list[GreatPerson]:
    return random.sample(_great_people_by_age[age], n)

