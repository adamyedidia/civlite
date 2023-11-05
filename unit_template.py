from typing import Union

from ability import Ability
from abilities_list import ABILITIES

class UnitTemplate:
    def __init__(self, name: str, building_name: str, metal_cost: int, wood_cost: int, strength: int, ranged_attacker: bool, movement: int, range: int, abilities: list[list[Union[str, list]]], type: str) -> None:
        self.name = name
        self.building_name = building_name
        self.metal_cost = metal_cost
        self.wood_cost = wood_cost
        self.strength = strength
        self.ranged_attacker = ranged_attacker
        self.movement = movement
        self.range = range
        self.abilities: list[Ability] = ABILITIES[abilities[0]](*abilities[1])  # type: ignore
        self.type = type

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "building_name": self.building_name,
            "metal_cost": self.metal_cost,
            "wood_cost": self.wood_cost,
            "strength": self.strength,
            "ranged_attacker": self.ranged_attacker,
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
            ranged_attacker=json["ranged_attacker"],
            movement=json["movement"],
            range=json["range"],
            abilities=[[ability["name"], ability["numbers"]] for ability in json["abilities"]],
            type=json["type"],
        )