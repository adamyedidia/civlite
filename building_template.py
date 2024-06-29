from typing import Callable, Optional, Union, TYPE_CHECKING
from abilities_list import BUILDING_ABILITIES
from ability import Ability
from effect import CityTargetEffect
from tech_template import TechTemplate
from yields import Yields, YieldsCalculation

if TYPE_CHECKING:
    from city import City
    from game_state import GameState

class BuildingTemplate:
    def __init__(self, 
                 name: str, 
                 type: str, 
                 cost: int, 
                 on_build: CityTargetEffect | list[CityTargetEffect] = [],
                 abilities: list[dict[str, Union[str, list]]] = [], 
                 vp_reward: Optional[int] = None, 
                 prereq: Optional[TechTemplate] = None,
                 exclusion_group: Optional[str] = None,
                 calculate_yields: YieldsCalculation | None = None,
    ):
        self.name = name
        self.type = type
        self.cost = cost
        self.on_build: list[CityTargetEffect] = on_build if isinstance(on_build, list) else [on_build]
        self.abilities: list[Ability] = [BUILDING_ABILITIES[ability["name"]](*ability["numbers"]) for ability in abilities]  # type: ignore
        self.vp_reward: int | None = vp_reward
        self.prereq: TechTemplate | None = prereq
        self.exclusion_group: str | None = exclusion_group
        self.calculate_yields = calculate_yields
        if prereq:
            prereq.unlocks_buildings.append(self)

    def __repr__(self):
        return f"<BuildingTemplate {self.name})>"

    def advancement_level(self) -> int:
        return self.prereq.advancement_level if self.prereq else 0

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "cost": self.cost,
            "description": [f"On build: {effect.description}" for effect in self.on_build] + [f"Passive: {ability.description}" for ability in self.abilities] + ([f"Yields: {self.calculate_yields.description}"] if self.calculate_yields else []),
            "vp_reward": self.vp_reward,
            "prereq": self.prereq.name if self.prereq else None,
            "exclusion_group": self.exclusion_group,
        }

    
    @staticmethod
    def from_json(json: dict) -> "BuildingTemplate":
        raise ValueError("Don't get Templates from json, just look them up by name in BUILDINGS.")
