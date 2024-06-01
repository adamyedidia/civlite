
from building_templates_list import BUILDINGS
from ability import Ability
from effects_list import BuildUnitsEffect, NullEffect
from effect import CityTargetEffect

def get_wonder_abilities_deprecated(wonder_name):
    return BUILDINGS.by_name(wonder_name).abilities if wonder_name in [b.name for b in BUILDINGS.all()] else []

class WonderTemplate:
    def __init__(self, name: str, age: int, on_build: CityTargetEffect | list[CityTargetEffect] = [], per_turn: CityTargetEffect | list[CityTargetEffect] = [], vp_reward: int = 5, abilities: list[Ability] = []):
        self.name = name
        self.age = age
        self.on_build: list[CityTargetEffect] = on_build if isinstance(on_build, list) else [on_build]
        self.per_turn: list[CityTargetEffect] = per_turn if isinstance(per_turn, list) else [per_turn]
        self.vp_reward = vp_reward
        self.abilities = abilities

    def __repr__(self):
        return f"<WonderTemplate {self.name})>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WonderTemplate):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def description(self) -> list[str]:
        effect_descs = [e.description for e in self.on_build + self.per_turn]
        effect_descs.extend([a.description for a in self.abilities])
        return effect_descs
    
    def hover_unit_name(self) -> str:
        for eff in [self.per_turn, self.on_build]:
            if isinstance(eff, BuildUnitsEffect):
                return eff.unit_template.name
        return ""

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description(),
            "age": self.age,
            "vp_reward": self.vp_reward,
            "hover_unit_name": self.hover_unit_name(),
        }

