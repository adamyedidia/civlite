from typing import Optional, Union
from enum import Enum

from abilities_list import BUILDING_ABILITIES
from ability import Ability
from effect import CityTargetEffect
from tech_template import TechTemplate
from yields import YieldsCalculation


class BuildingType(Enum):
    RURAL = "rural"
    URBAN = "urban"
    UNIT = "unit"

class BuildingTemplate:
    def __init__(self, 
                 name: str, 
                 type: BuildingType, 
                 cost: int, 
                 on_build: CityTargetEffect | list[CityTargetEffect] = [],
                 per_turn: CityTargetEffect | list[CityTargetEffect] = [],
                 abilities: list[dict[str, Union[str, list]]] = [], 
                 vp_reward: Optional[int] = None, 
                 prereq: Optional[TechTemplate] = None,
                 calculate_yields: YieldsCalculation | None = None,
    ):
        self.name = name
        self.type = type
        self.cost = cost
        self.on_build: list[CityTargetEffect] = on_build if isinstance(on_build, list) else [on_build]
        self.per_turn: list[CityTargetEffect] = per_turn if isinstance(per_turn, list) else [per_turn]
        self.abilities: list[Ability] = [BUILDING_ABILITIES[ability["name"]](*ability["numbers"]) for ability in abilities]  # type: ignore
        self.vp_reward: int | None = vp_reward
        self.prereq: TechTemplate | None = prereq
        self.calculate_yields = calculate_yields
        if prereq:
            prereq.unlocks_buildings.append(self)

    def __repr__(self):
        return f"<BuildingTemplate {self.name})>"
    
    def __lt__(self, other: 'BuildingTemplate') -> bool:
        return (self.advancement_level(), self.cost, self.name) < (other.advancement_level(), other.cost, other.name)

    def advancement_level(self) -> int:
        return self.prereq.advancement_level if self.prereq else 0
    
    @property
    def useless_if_zero_yields(self):
        return self.calculate_yields is not None and len(self.abilities) == len(self.on_build) == len(self.per_turn) == 0

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type.value,
            "cost": self.cost,
            "description": [f"On build: {effect.description}" for effect in self.on_build] + 
                [f"Per turn: {effect.description}" for effect in self.per_turn] +
                [f"Passive: {ability.description}" for ability in self.abilities] + 
                ([f"Yields: {self.calculate_yields.description}"] if self.calculate_yields else []),
            "vp_reward": self.vp_reward,
            "prereq": self.prereq.name if self.prereq else None,
            "advancement_level": self.advancement_level(),
        }

    
    @staticmethod
    def from_json(json: dict) -> "BuildingTemplate":
        raise ValueError("Don't get Templates from json, just look them up by name in BUILDINGS.")
