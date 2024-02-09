from typing import Union

from ability import Ability
from abilities_list import ABILITIES, UNIT_ABILITIES

class UnitTemplate:
    def __init__(self, name: str, building_name: str, metal_cost: int, wood_cost: int, strength: int, tags: list[str], movement: int, range: int, abilities: list[list[Union[str, list]]], type: str) -> None:
        self.name = name
        print(name)
        self.building_name = building_name
        self.metal_cost = metal_cost
        self.wood_cost = wood_cost
        self.strength = strength
        self.tags = tags
        self.movement = movement
        self.range = range
        self.abilities: list[Ability] = [UNIT_ABILITIES[ability[0]](*ability[1]) for ability in abilities]  # type: ignore
        self.type = type

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "building_name": self.building_name,
            "metal_cost": self.metal_cost,
            "wood_cost": self.wood_cost,
            "strength": self.strength,
            "tags": self.tags,
            "movement": self.movement,
            "range": self.range,
            "abilities": [ability.to_json() for ability in self.abilities],
            "type": self.type,
        }
    
    @staticmethod
    def from_json(json: dict) -> "UnitTemplate":
        return UnitTemplate(
            name=json["name"],
            building_name=json["building_name"],
            metal_cost=json["metal_cost"],
            wood_cost=json["wood_cost"],
            strength=json["strength"],
            tags=json["tags"],
            movement=json["movement"],
            range=json["range"],
            abilities=[[ability["name"], ability["numbers"]] for ability in json["abilities"]],
            type=json["type"],
        )