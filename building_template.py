from typing import Optional, Union
from abilities_list import BUILDING_ABILITIES
from ability import Ability


class BuildingTemplate:
    def __init__(self, name: str, type: str, cost: int, abilities: list[list[Union[str, list]]], is_wonder: bool = False, vp_reward: Optional[int] = None):
        self.name = name
        self.type = type
        self.cost = cost
        self.abilities: list[Ability] = [BUILDING_ABILITIES[ability[0]](*ability[1]) for ability in abilities]  # type: ignore
        self.is_wonder = is_wonder
        self.vp_reward = vp_reward


    def to_json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "cost": self.cost,
            "abilities": [ability.to_json() for ability in self.abilities],
            **({"is_wonder": self.is_wonder,
            "vp_reward": self.vp_reward,} if self.is_wonder else {}),
        }
    
    @staticmethod
    def from_json(json: dict) -> "BuildingTemplate":
        return BuildingTemplate(
            name=json["name"],
            type=json["type"],
            cost=json["cost"],
            abilities=[[ability[0], ability[1]] for ability in json["abilities"]],
            is_wonder=json.get("is_wonder", False),
            vp_reward=json.get("vp_reward", None),
        )
