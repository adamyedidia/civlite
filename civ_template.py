from typing import Union
from abilities_list import CIV_ABILITIES
from ability import Ability


class CivTemplate:
    def __init__(self, name: str, primary_color: str, secondary_color: str, abilities: list[list[Union[str, list]]], advancement_level: int):
        self.name = name
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.abilities: list[Ability] = [CIV_ABILITIES[ability[0]](*ability[1]) for ability in abilities]  # type: ignore
        self.advancement_level: int = advancement_level

    def __repr__(self) -> str:

        return f"<CivTemplate {self.name}>"

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "abilities": [ability.to_json() for ability in self.abilities],
            "advancement_level": self.advancement_level
        }

    
    @staticmethod
    def from_json(json: dict) -> "CivTemplate":
        return CivTemplate(
            name=json["name"],
            primary_color=json["primary_color"],
            secondary_color=json["secondary_color"],
            abilities=[[ability["name"], ability["numbers"]] for ability in json["abilities"]],
            advancement_level=json["advancement_level"],
        )