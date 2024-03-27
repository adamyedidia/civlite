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
        super().__init__(name, hover_entity_type="unit", hover_entity_name=unit_template.name)

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

merchant_names = {
    "metal": ["Beowulf", "[ANCIENT METAL MERCHANT]", "Colaeus", "Ned Stark", "Catherine de Medici", "Benjamin Franklin", "Otto von Bismark", "Franklin Delano Roosevelt", "Vladimir Putin", "[FUTURE METAL MERCHANT]"],
    "wood": ["Gilgamesh", "[ANCIENT WOOD MERCHANT]", "Marcus Licinius Crassus", "Irene of Athens", "Leonardo da Vinci", "[INDUSTRIAL WOOD MERCHANT]", "Henry Ford", "[MODERN WOOD MERCHANT]", "Steve Jobs", "[FUTURE WOOD MERCHANT]"],
    "food": ["Moses", "[ANCIENT FOOD MERCHANT]", "Zhang Qian", "Harald Bluetooth", "Marco Polo", "[INDUSTRIAL FOOD MERCHANT]", "Queen Victoria", "Gandhi", "[INFORMATION FOOD MERCHANT]", "[FUTURE FOOD MERCHANT]"],
    "science": ["Prometheus", "Confucius", "Archimedes", "Copernicus", "Francis Bacon", "Charles Darwin", "Albert Einstein", "John von Neumann", "[INFORMATION SCIENCE MERCHANT]", "[FUTURE SCIENCE MERCHANT]"],
}
# Ibn Fadlan, 
for resource in ["metal", "wood", "food", "science"]:
    for age in range(10):
        _great_people_by_age[age].append(GreatMerchant(merchant_names[resource][age], _target_value_by_age(age), resource))

for tech in TECHS.values():
    t = TechTemplate.from_json(tech)
    level = t.advancement_level
    scientist_name = tech.get("great_scientist_name", f"[A{level - 1} Scientist: {t.name}]")
    _great_people_by_age[level - 1].append(GreatScientist(scientist_name, t))
    for unit in t.unlocks_units:
        u = UnitTemplate.from_json(UNITS[unit])
        great_people_names: dict[str, str] = UNITS[unit].get('great_people_names', {})
        advanced_general_name: str = great_people_names.get("general_advanced", f"[A{level - 1} General: {unit}]")
        _great_people_by_age[level - 1].append(GreatGeneral(advanced_general_name, u, round(0.5 * _target_value_by_age(level - 1) / u.metal_cost)))
        normal_general_name: str = great_people_names.get("general_normal", f"[A{level} General: {unit}]")
        _great_people_by_age[level].append(GreatGeneral(normal_general_name, u, round(0.8 * _target_value_by_age(level) / u.metal_cost)))
        horde_general_name: str = great_people_names.get("general_horde", f"[A{level + 1} General: {unit}]")
        _great_people_by_age[level + 1].append(GreatGeneral(horde_general_name, u, round(1.1 * _target_value_by_age(level + 1) / u.metal_cost)))

        engineer_name = great_people_names.get("engineer", f"[A{level - 1} Engineer: {u.building_name}]")
        _great_people_by_age[level - 1].append(GreatEngineer(engineer_name, u, max(0, 0.5 * _target_value_by_age(level - 1) - u.wood_cost)))

unique_names = set()
duplicate_names = set()

for age, great_people in _great_people_by_age.items():
    for great_person in great_people:
        if great_person.name in unique_names:
            duplicate_names.add(great_person.name)
        unique_names.add(great_person.name)

if duplicate_names:
    raise ValueError(f"Duplicate great person names found: {duplicate_names}")

print(unique_names)
num_placeholder = len([name for name in unique_names if name.startswith("[")])
print(f"Named {len(unique_names) - num_placeholder} out of {len(unique_names)} great people")

_great_people_by_age[6].append(GreatGeneral("Ōishi Yoshio", UnitTemplate.from_json(UNITS["Swordsman"]), 47))

great_people_by_name: dict[str, GreatPerson] = {great_person.name: great_person for great_person_list in _great_people_by_age.values() for great_person in great_person_list}

# Set some numbers to their correct values, even if it's not balanced.
great_people_by_name["King Arthur"].number = 12
great_people_by_name["Alexandre Dumas"].number = 3

def random_great_people_by_age(age: int, n: int = 1) -> list[GreatPerson]:
    return random.sample(_great_people_by_age[age], n)

for name, person in great_people_by_name.items():
    if isinstance(person, GreatGeneral) and person.name.startswith("["):
        print(person.unit_template.name, person.number)


