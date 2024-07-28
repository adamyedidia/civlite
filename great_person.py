from __future__ import annotations

import abc
from collections import defaultdict
import inflect
from typing import TYPE_CHECKING, Optional
from TechStatus import TechStatus

from tech_templates_list import TECHS
from tech_template import TechTemplate
from unit_template import UnitTemplate
from unit_templates_list import UNITS

if TYPE_CHECKING:
    from city import City
    from civ import Civ

p = inflect.engine()

class GreatPerson(abc.ABC):
    def __init__(self, name: str, advancement_level: int, hover_entity_type: Optional[str] = None, hover_entity_name: Optional[str] = None):
        self.name: str = name
        self.advancement_level: int = advancement_level
        self.hover_entity_type: Optional[str] = hover_entity_type
        self.hover_entity_name: Optional[str] = hover_entity_name

    @abc.abstractmethod
    def description(self) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def apply(self, game_state, city: City, civ: Civ):
        raise NotImplementedError()
    
    def valid_for_city(self, city: City, civ: Civ) -> bool:
        return city.civ == civ
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"
    
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
    def __init__(self, name, advancement_level: int, unit_template: UnitTemplate, number: int):
        self.unit_template: UnitTemplate = unit_template
        self.number: int = number
        super().__init__(name, advancement_level, hover_entity_type="unit", hover_entity_name=unit_template.name)

    def description(self) -> str:
        return f"Immediately build {self.number} free {p.plural(self.unit_template.name)}"  # type: ignore

    def apply(self, game_state, city: City, civ: Civ):
        for _ in range(self.number):
            city.build_unit(game_state, self.unit_template, override_civ=civ)

    def valid_for_city(self, city: City, civ: Civ) -> bool:
        return True

class GreatMerchant(GreatPerson):
    def __init__(self, name, advancement_level: int, amount: float, resource: str):
        self.amount: float = amount
        self.resource: str = resource
        super().__init__(name, advancement_level)

    def description(self) -> str:
        return f"Immediately gain {self.amount} {self.resource}"

    def apply(self, game_state, city: City, civ: Civ):
        if self.resource == "metal":
            city.metal += self.amount
        elif self.resource == "wood":
            city.wood += self.amount
        elif self.resource == "food":
            city.food += self.amount
            city.grow(game_state)
        elif self.resource == "science":
            civ.science += self.amount

    def valid_for_city(self, city: City, civ: Civ) -> bool:
        if self.resource in ["metal", "wood", "food"]:
            return city.civ == civ
        return True

class GreatScientist(GreatPerson):
    def __init__(self, name, advancement_level: int, tech_template: TechTemplate, extra_science: float):
        self.tech_template: TechTemplate = tech_template
        self.extra_science: float = extra_science
        super().__init__(name, advancement_level, hover_entity_type="tech", hover_entity_name=tech_template.name)

    def description(self) -> str:
        desc = f"Immediately learn {self.tech_template.name}"
        if self.extra_science > 0:
            desc += f" and gain {int(self.extra_science)} science."
        return desc

    def apply(self, game_state, city: City, civ: Civ):
        civ.gain_tech(game_state, self.tech_template)
        civ.science += self.extra_science

    def valid_for_city(self, city: City, civ: Civ) -> bool:
        return civ.techs_status[self.tech_template] in (TechStatus.AVAILABLE, TechStatus.UNAVAILABLE)

class GreatEngineer(GreatPerson):
    def __init__(self, name, advancement_level: int, unit_template: UnitTemplate, extra_wood: float):
        self.unit_template: UnitTemplate = unit_template
        self.extra_wood: float = extra_wood
        super().__init__(name, advancement_level, hover_entity_type="unit", hover_entity_name=unit_template.name)

    def description(self) -> str:
        desc: str = f"Immediately build a free {self.unit_template.building_name}"
        if self.extra_wood > 0:
            desc += f" and gain {int(self.extra_wood)} wood."
        return desc

    def apply(self, game_state, city: City, civ: Civ):
        city.build_building(game_state, self.unit_template, free=True)
        city.midturn_update(game_state)
        city.wood += self.extra_wood

    def valid_for_city(self, city: City, civ: Civ) -> bool:
        return city.civ == civ and not city.has_building(self.unit_template)

_great_people_by_age: dict[int, list[GreatPerson]] = defaultdict(list)

def _target_value_by_age(age: int) -> int:
    return {
        0: 40,
        1: 80,
        2: 120,
        3: 180,
        4: 240,
        5: 320,
        6: 420,
        7: 560,
        8: 900,
        9: 1500,
        10: 2500,
    }[age]

merchant_names = {
    "metal": ["Beowulf", "Darius I", "Colaeus", "Ned Stark", "Catherine de Medici", "Benjamin Franklin", "Otto von Bismark", "Franklin Delano Roosevelt", "Vladimir Putin", "Nick Fury"],
    "wood": ["Gilgamesh", "Nebuchadnezzar II", "Marcus Licinius Crassus", "Tyrion Lannister", "Leonardo da Vinci", "Gustave Eiffel", "Andrew Carnegie", "Robert Moses", "Steve Jobs", "Hari Seldon"],
    "food": ["Moses", "Siddhartha", "Zhang Qian", "Harald Bluetooth", "Marco Polo", "Cyrus McCormick", "Queen Victoria", "Gandhi", "Donald Henderson", "Jean-Luc Picard"],
    "science": ["Prometheus", "Confucius", "Archimedes", "Copernicus", "Francis Bacon", "Charles Darwin", "Albert Einstein", "John von Neumann", "Ada Lovelace", "Dr Emmett Brown"],
}

scientist_names = {
    'Archery': 'Artemis',
    'Bronze Working': 'Hephaestus',
    'Pottery': 'The Potter of Mohenjo-Daro',
    # 'Code of Laws': 'Hammurabi',
    'The Wheel': 'Daedalus',
    'Mining': 'Thoth',
    'Forestry': 'Johnny Appleseed',
    'Irrigation': 'King Yu the Great',
    # 'Writing': 'Socrates',
    # 'Masonry': 'Imhotep',
    'Mathematics': "Euclid",
    'Horseback Riding': 'Xenophon',
    'Iron Working': 'Ashurbanipal',
    'Currency': 'Alyattes of Lydia',
    'Engineering': 'Qin Shi Huang',
    'Construction': 'Emperor Vespasian',
    'Education': 'Robert of Sorbon',
    'Machinery': 'Heron of Alexandria',
    'Civil Service': 'Emperor Wen of Sui',
    'Chivalry': 'Uther Pendragon',
    'Compass': 'Galileo Galilei',
    'Physics': 'Isaac Newton',
    'Printing Press': 'Johannes Gutenberg',
    'Gunpowder': 'Li Tian',
    'Metallurgy': 'Niccolo Machiavelli',
    'Architecture': 'Michelangelo',
    "Medicine": 'Louis Pasteur',
    # 'Economics': 'Adam Smith',
    'Military Science': 'Frederick the Great',
    'Industrialization': 'James Watt',
    'Dynamite': 'Alfred Nobel',
    'Radio': 'Nikola Tesla',
    'Mass Markets': 'Henry Ford',
    'Combined Arms': 'Vladimir Lenin',
    # 'Ballistics': 'TODO',
    'Mechanized Agriculture': 'Norman Borlaug',
    'Rocketry': 'Marie Curie',
    'Computers': 'Alan Turing',
    'Nanotechnology': 'Richard Feynman',
    'Megarobotics': 'Isaac Asimov',
}

for resource in ["metal", "wood", "food", "science"]:
    for age in range(10):
        _great_people_by_age[age].append(GreatMerchant(merchant_names[resource][age], age, _target_value_by_age(age), resource))

for t in TECHS.all():
    if t == TECHS.RENAISSANCE:
        continue
    level = t.advancement_level
    scientist_name = scientist_names.get(t.name, f"[A{level - 1} Scientist: {t.name}]")
    _great_people_by_age[level - 1].append(GreatScientist(scientist_name, level - 1, t, extra_science=max(0, _target_value_by_age(level - 1) - t.cost)))
    for u in t.unlocks_units:
        great_people_names: dict[str, str] = u.great_people_names
        advanced_general_name: str = great_people_names.get("general_advanced", f"[A{level - 1} General: {u.name}]")
        _great_people_by_age[level - 1].append(GreatGeneral(advanced_general_name, level - 1, u, round(0.5 * _target_value_by_age(level - 1) / u.metal_cost)))
        normal_general_name: str = great_people_names.get("general_normal", f"[A{level} General: {u.name}]")
        _great_people_by_age[level].append(GreatGeneral(normal_general_name, level, u, round(0.65 * _target_value_by_age(level) / u.metal_cost)))
        horde_general_name: str = great_people_names.get("general_horde", f"[A{level + 1} General: {u.name}]")
        _great_people_by_age[level + 1].append(GreatGeneral(horde_general_name, level + 1, u, round(0.8 * _target_value_by_age(level + 1) / u.metal_cost)))

        engineer_name = great_people_names.get("engineer", f"[A{level - 1} Engineer: {u.building_name}]")
        _great_people_by_age[level - 1].append(GreatEngineer(engineer_name, level - 1, u, max(0, 0.5 * _target_value_by_age(level - 1) - u.wood_cost)))

unique_names = set()
duplicate_names = set()

for age, great_people in _great_people_by_age.items():
    for great_person in great_people:
        if great_person.name in unique_names:
            duplicate_names.add(great_person.name)
        unique_names.add(great_person.name)

if duplicate_names:
    raise ValueError(f"Duplicate great person names found: {duplicate_names}")

_great_people_by_age[5].append(GreatGeneral("Ōishi Yoshio", 5, UNITS.SWORDSMAN, 47))

def great_people_by_age(age: int) -> list[GreatPerson]:
    return _great_people_by_age[age]

for age, people in _great_people_by_age.items():
    for person in people:
        assert person.advancement_level == age

###### unnamed great people #####
num_placeholder = len([name for name in unique_names if name.startswith("[")])
print(f"Named {len(unique_names) - num_placeholder} out of {len(unique_names)} great people")
unnamed_list = []

for age, people in _great_people_by_age.items():
    if 0 <= age <= 9:
        if __name__ == "__main__":
            print(f"\n======= Age {age} =======")
        for person in people.copy():
            if __name__ == "__main__":
                print(f"{person.name}: {person.description()}")
            if person.name.startswith("["):
                people.remove(person)
                unnamed_list.append(person)
    else:
        print(f"======= INVALID AGE {age}")
        for person in people:
            print(person.name)

great_people_by_name: dict[str, GreatPerson] = {great_person.name: great_person for great_person_list in _great_people_by_age.values() for great_person in great_person_list}

print(f"****************** Unnamed great people ({len(unnamed_list)}) ******************")
for person in unnamed_list:
    if isinstance(person, GreatGeneral):
        print(person.advancement_level, person.number, person.unit_template.name)
    elif isinstance(person, GreatMerchant):
        print(person.advancement_level, person.amount, person.resource)
    elif isinstance(person, GreatScientist):
        print(person.advancement_level, person.tech_template.name)
    elif isinstance(person, GreatEngineer):
        print(f"{person.advancement_level} {person.unit_template.building_name} ({person.unit_template.name})")
    else:
        print(person.advancement_level, person.name)

# Set some numbers to their correct values, even if it's not balanced.
for name, number in [("Roland and Oliver", 2), ("The Horatii", 3)]:
    gp = great_people_by_name[name]
    assert isinstance(gp, GreatGeneral)
    if gp.number != number:
        print(f"Setting {name} to {number} for flavor (should have been {gp.number})")
    gp.number = number