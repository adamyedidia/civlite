
from building_templates_list import BUILDINGS
from effects_list import NullEffect
from effect import CityTargetEffect

def get_wonder_abilities_deprecated(wonder_name):
    return BUILDINGS.by_name(wonder_name).abilities if wonder_name in [b.name for b in BUILDINGS.all()] else []

class WonderTemplate:
    def __init__(self, name: str, age: int, on_build: CityTargetEffect | None = None, per_turn: CityTargetEffect | None = None, vp_reward: int = 5, abilities = []):
        self.name = name
        self.age = age
        self.on_build: CityTargetEffect = on_build or NullEffect()
        self.per_turn: CityTargetEffect = per_turn or NullEffect()
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
    
    def description(self) -> str:
        effect_descs = []
        if self.on_build != NullEffect():
            effect_descs.append(f"On build: {self.on_build.description}")
        if self.per_turn != NullEffect():
            effect_descs.append(f"Each turn: {self.per_turn.description}")
        effect_descs.extend([a.description for a in self.abilities])
        return "\n ".join(effect_descs)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description(),
            "age": self.age,
            "vp_reward": self.vp_reward,
        }

