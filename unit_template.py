from typing import Union, Optional

from ability import Ability
from abilities_list import UNIT_ABILITIES
from tech_templates_list import TECHS
from tech_template import TechTemplate
from enum import Enum

from utils import deterministic_hash

class UnitTag(Enum):
    INFANTRY = "infantry"
    RANGED = "ranged"  # target doesn't punch back
    MOUNTED = "mounted"
    SIEGE = "siege"
    GUNPOWDER = "gunpowder"
    DEFENSIVE = "defensive"
    WONDROUS = "wondrous"  # Built from a wonder; Lose 5 hp per turn

class UnitTemplate:
    def __init__(self, name: str, building_name: str | None, metal_cost: int, wood_cost: int, strength: int, tags: list[UnitTag], movement: int, range: int, abilities: list[dict[str, Union[str, list]]], prereq: Optional[TechTemplate], great_people_names: dict[str, str] = {}) -> None:
        self.name = name
        self.building_name: str = building_name or ""
        self.buildable: bool = building_name is not None
        self.metal_cost = metal_cost
        self.wood_cost = wood_cost
        self.strength = strength
        self.tags = tags
        self.movement = movement
        self.range = range
        # TODO clean this up, define the Abilities directly.
        self.abilities: list[Ability] = [UNIT_ABILITIES[ability["name"]](*ability["numbers"]) for ability in abilities]  # type: ignore
        self.prereq: TechTemplate | None = prereq
        if prereq:
            prereq.unlocks_units.append(self)
        self.great_people_names = great_people_names

        if self.range > 1:
            assert self.has_tag(UnitTag.RANGED), f"Ranged unit {self.name} has range {self.range} but does not have the RANGED tag."

    def __eq__(self, other: "UnitTemplate") -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return deterministic_hash(self.name)

    def __repr__(self):
        return f"<UnitTemplate {self.name}>"

    def _priority(self) -> tuple:
        return (self.advancement_level, self.wood_cost, self.metal_cost, self.strength, self.range, self.movement)

    def __lt__(self, other: "UnitTemplate") -> bool:
        return self._priority() < other._priority()

    @property
    def advancement_level(self) -> int:
        if self.prereq is None:
            return 0
        return self.prereq.advancement_level

    def has_tag(self, tag: UnitTag) -> bool:
        return tag in self.tags

    def has_tag_by_name(self, tag_name: str) -> bool:
        return any(t.value == tag_name for t in self.tags)

    def attack_type(self):
        if self.name in ['Infantry', 'Ramparts']:
            return "infantry"
        elif self.name in ['Gatling Gun', 'Machine Gun']:
            return "machine_gun"
        elif self.name in ['Artillery', "Tank"]:
            return "artillery"
        elif self.name in ["Bazooka", "Rocket Artillery"]:
            return "rocket"
        elif self.name in ["Nanoswarm", "Giant Death Robot", "Ironman"]:
            return "laser"
        else:
            return  (("melee" if not self.has_tag(UnitTag.RANGED) else "ranged") 
                            if not self.has_tag(UnitTag.GUNPOWDER)
                            else ("gunpowder_melee" if not self.has_tag(UnitTag.RANGED) else "gunpowder_ranged"))

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
            "prereq": self.prereq.name if self.prereq else None,
            "advancement_level": self.advancement_level,
        }

    
    @staticmethod
    def from_json(json: dict) -> "UnitTemplate":
        raise ValueError("Don't get Templates from json, just look them up by name in UNITS.")