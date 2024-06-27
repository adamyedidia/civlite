from typing import Optional, Union
from abilities_list import BUILDING_ABILITIES
from ability import Ability
from effect import Effect
from tech_template import TechTemplate
from tech_templates_list import TECHS

class BuildingTemplate:
    def __init__(self, 
                 name: str, 
                 type: str, 
                 cost: int, 
                 on_build: Effect | list[Effect] = [],
                 abilities: list[dict[str, Union[str, list]]] = [], 
                 is_national_wonder: bool = False, 
                 vp_reward: Optional[int] = None, 
                 prereq: Optional[TechTemplate] = None,
                 exclusion_group: Optional[str] = None):
        self.name = name
        self.type = type
        self.cost = cost
        self.on_build: list[Effect] = on_build if isinstance(on_build, list) else [on_build]
        self.abilities: list[Ability] = [BUILDING_ABILITIES[ability["name"]](*ability["numbers"]) for ability in abilities]  # type: ignore
        self.is_national_wonder = is_national_wonder
        self.vp_reward: int | None = vp_reward
        self.prereq: TechTemplate | None = prereq
        self.exclusion_group: str | None = exclusion_group
        if prereq:
            prereq.unlocks_buildings.append(self)

    def __repr__(self):
        return f"<BuildingTemplate {self.name})>"

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "cost": self.cost,
            "description": [f"On build: {effect.description}" for effect in self.on_build] + [f"Passive: {ability.description}" for ability in self.abilities],
            "vp_reward": self.vp_reward,
            "is_national_wonder": self.is_national_wonder,
            "prereq": self.prereq.name if self.prereq else None,
            "exclusion_group": self.exclusion_group,
        }

    
    @staticmethod
    def from_json(json: dict) -> "BuildingTemplate":
        raise ValueError("Don't get Templates from json, just look them up by name in BUILDINGS.")
