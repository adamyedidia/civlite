from typing import List, TYPE_CHECKING

from effect import Effect
from effects_list import NullEffect

if TYPE_CHECKING:
    from unit_template import UnitTemplate
    from building_template import BuildingTemplate

class TechTemplate:
    def __init__(self, name: str, cost: int, advancement_level: int, breakthrough_effect: Effect = NullEffect(), breakthrough_cost: int | None = None):
        self.name = name
        self.cost = cost
        self.breakthrough_cost: int = breakthrough_cost or int(cost * 1.2)
        self.breakthrough_effect = breakthrough_effect
        self.advancement_level = advancement_level
        self.unlocks_units: list['UnitTemplate'] = []
        self.unlocks_buildings: list['BuildingTemplate'] = []
        
    def __repr__(self):
        return f"<TechTemplate {self.name}>"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, TechTemplate):
            return False
        return self.name == __value.name

    def __hash__(self) -> int:
        return hash(self.name)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "cost": self.cost,
            "breakthrough_cost": self.breakthrough_cost,
            "breakthrough_effect": self.breakthrough_effect.description,
            "advancement_level": self.advancement_level,
            "unlocks_units": [u.name for u in self.unlocks_units],
            "unlocks_buildings": [b.name for b in self.unlocks_buildings],
        }
    
    @staticmethod
    def from_json(json: dict) -> "TechTemplate":
        raise ValueError("Don't get Templates from json, just look them up by name in TECHS.")
