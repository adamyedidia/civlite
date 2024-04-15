from typing import Optional, Union
from abilities_list import BUILDING_ABILITIES
from ability import Ability
from wood_buildable import WoodBuildable
from tech_template import TechTemplate
from tech_templates_list import TECHS

class BuildingTemplate(WoodBuildable):
    def __init__(self, building_name: str, type: str, cost: int, abilities: list[dict[str, Union[str, list]]], is_wonder: bool = False, is_national_wonder: bool = False, vp_reward: Optional[int] = None, prereq: Optional[TechTemplate] = None):
        super().__init__(building_name)
        self.type = type
        self.cost = cost
        self.abilities: list[Ability] = [BUILDING_ABILITIES[ability["name"]](*ability["numbers"]) for ability in abilities]  # type: ignore
        self.is_wonder = is_wonder
        self.is_national_wonder = is_national_wonder
        self.vp_reward: int | None = vp_reward
        self.prereq: TechTemplate | None = prereq
        if prereq:
            prereq.unlocks_buildings.append(self)

    def __repr__(self):
        return f"<BuildingTemplate {self.building_name})>"
    
    def building_cost_for_civ(self, civ) -> float:
        return self.cost

    def to_json(self) -> dict:
        return {
            "name": self.building_name,
            "type": self.type,
            "cost": self.cost,
            "abilities": [ability.to_json() for ability in self.abilities],
            "is_wonder": self.is_wonder,
            "vp_reward": self.vp_reward,
            "is_national_wonder": self.is_national_wonder,
            "prereq": self.prereq.name if self.prereq else None,
        }

    
    @staticmethod
    def from_json(json: dict) -> "BuildingTemplate":
        raise ValueError("Don't get Templates from json, just look them up by name in BUILDINGS.")
