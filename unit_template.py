from typing import Union, Optional

from ability import Ability
from abilities_list import ABILITIES, UNIT_ABILITIES
from tech_templates_list import TECHS
from tech_template import TechTemplate
from enum import Enum

class UnitTag(Enum):
    INFANTRY = "infantry"
    RANGED = "ranged"
    MOUNTED = "mounted"
    SIEGE = "siege"
    ARMORED = "armored"
    GUNPOWDER = "gunpowder"
    DEFENSIVE = "defensive"

class UnitTemplate:
    def __init__(self, name: str, building_name: str, metal_cost: int, wood_cost: int, strength: int, tags: list[UnitTag], movement: int, range: int, abilities: list[dict[str, Union[str, list]]], type: str, prereq: Optional[TechTemplate], great_people_names: dict[str, str] = {}) -> None:
        self.name = name
        self.building_name = building_name
        self.metal_cost = metal_cost
        self.wood_cost = wood_cost
        self.strength = strength
        self.tags = tags
        self.movement = movement
        self.range = range
        # TODO clean this up, define the Abilities directly.
        self.abilities: list[Ability] = [UNIT_ABILITIES[ability["name"]](*ability["numbers"]) for ability in abilities]  # type: ignore
        self.type = type
        self.prereq: TechTemplate | None = prereq
        if prereq:
            prereq.unlocks_units.append(self)
        self.great_people_names = great_people_names



    def __repr__(self):
        return f"<UnitTemplate {self.name}>"

    def advancement_level(self):
        if self.prereq is None:
            return 0
        return self.prereq.advancement_level

    def has_tag(self, tag: UnitTag) -> bool:
        return tag in self.tags

    def has_tag_by_name(self, tag_name: str) -> bool:
        return any(t.value == tag_name for t in self.tags)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "building_name": self.building_name,
            "metal_cost": self.metal_cost,
            "wood_cost": self.wood_cost,
            "strength": self.strength,
            "tags": [t.value for t in self.tags],
            "movement": self.movement,
            "range": self.range,
            "abilities": [ability.to_json() for ability in self.abilities],
            "type": self.type,
            "prereq": self.prereq.name if self.prereq else None,
        }

    
    @staticmethod
    def from_json(json: dict) -> "UnitTemplate":
        raise ValueError("Don't get Templates from json, just look them up by name in UNITS.")