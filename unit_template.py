from typing import Union

from ability import Ability
from abilities_list import ABILITIES

class UnitTemplate:
    def __init__(self, name: str, building_name: str, metal_cost: int, stone_cost: int, attack: int, health: int, movement: int, range: int, armor: int, abilities: list[list[Union[str, list]]], type: str) -> None:
        self.name = name
        self.building_name = building_name
        self.metal_cost = metal_cost
        self.stone_cost = stone_cost
        self.attack = attack
        self.health = health
        self.movement = movement
        self.range = range
        self.armor = armor
        self.abilities: list[Ability] = ABILITIES[abilities[0]](*abilities[1])  # type: ignore
        self.type = type

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "building_name": self.building_name,
            "metal_cost": self.metal_cost,
            "stone_cost": self.stone_cost,
            "attack": self.attack,
            "health": self.health,
            "movement": self.movement,
            "range": self.range,
            "armor": self.armor,
            "abilities": [ability.to_json() for ability in self.abilities],
            "type": self.type,
        }
    
    @staticmethod
    def from_json(json: dict) -> "UnitTemplate":
        return UnitTemplate(
            name=json["name"],
            building_name=json["building_name"],
            metal_cost=json["metal_cost"],
            stone_cost=json["stone_cost"],
            attack=json["attack"],
            health=json["health"],
            movement=json["movement"],
            range=json["range"],
            armor=json["armor"],
            abilities=[[ability["name"], ability["numbers"]] for ability in json["abilities"]],
            type=json["type"],
        )