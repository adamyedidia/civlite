from typing import Optional
from abilities_list import CIV_ABILITIES
from ability import Ability
from civ_templates_colors_list import colors_list


class CivTemplate:
    def __init__(self, 
                name: str, 
                abilities: list[Ability], 
                advancement_level: int, 
                colors: Optional[tuple[str, str]] = None, 
            ):
        self.name: str = name
        if colors is None:
            colors = colors_list.pop(0)
        self.primary_color, self.secondary_color = colors
        self.abilities: list[Ability] = abilities
        self.advancement_level: int = advancement_level

    def __repr__(self) -> str:
        return f"<CivTemplate {self.name}>"

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "abilities": [ability.to_json() for ability in self.abilities],
        }
    
    @staticmethod
    def from_json(json: dict) -> "CivTemplate":
        raise ValueError("Don't recreate Templates from json. Get them by name from CIV_TEMPLATES.")