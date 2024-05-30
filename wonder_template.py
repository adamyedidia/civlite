
from building_templates_list import BUILDINGS
from effects_list import NullEffect
from effect import CityTargetEffect

def get_wonder_abilities_deprecated(wonder_name):
    return BUILDINGS.by_name(wonder_name).abilities if wonder_name in [b.name for b in BUILDINGS.all()] else []

class WonderTemplate:
    def __init__(self, name: str, age: int, on_build: CityTargetEffect | None = None, vp_reward: int = 5):
        self.name = name
        self.age = age
        self.on_build: CityTargetEffect = on_build or NullEffect()
        self.vp_reward = vp_reward

    def __repr__(self):
        return f"<WonderTemplate {self.name})>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WonderTemplate):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.on_build.description,
            "age": self.age,
            "vp_reward": self.vp_reward,
        }

