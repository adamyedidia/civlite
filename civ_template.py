from typing import Union
from abilities_list import CIV_ABILITIES
from ability import Ability
from civ_color_pairs import color_pairs

class CivTemplate:
    def __init__(self, name: str, abilities: list[dict[str, Union[str, list]]], advancement_level: int, colors: tuple[str, str] | None = None):
        self.name = name
        if colors is None:
            colors = color_pairs.pop(0)
        self.primary_color, self.secondary_color = colors
        self.abilities: list[Ability] = [CIV_ABILITIES[ability["name"]](*ability["numbers"]) for ability in abilities]  # type: ignore
        self.advancement_level: int = advancement_level

    def __repr__(self) -> str:
        return f"<CivTemplate {self.name}>"
    
    @property
    def unique_unit(self) -> str | None:
        for ability in self.abilities:
            if ability.name == "IncreasedStrengthForUnit":
                return ability.numbers[0]
            if ability.name == "IncreasedStrengthForNthUnit":
                return ability.numbers[1]
        return None

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
        raise ValueError("Don't get Templates from json, just look them up by name in CIVS.")