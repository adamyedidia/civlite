from typing import Union
from abilities_list import CIV_ABILITIES
from ability import Ability


class CivTemplate:
    def __init__(self, name: str, color: str, abilities: list[list[Union[str, list]]]):
        self.name = name
        self.color = color
        self.abilities: list[Ability] = CIV_ABILITIES[abilities[0]](*abilities[1])  # type: ignore

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "color": self.color,
            "abilities": [ability.to_json() for ability in self.abilities],
        }
    
    @staticmethod
    def from_json(json: dict) -> "CivTemplate":
        return CivTemplate(
            name=json["name"],
            color=json["color"],
            abilities=[[ability["name"], ability["numbers"]] for ability in json["abilities"]],
        )