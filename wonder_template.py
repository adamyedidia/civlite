
from ability import Ability
from effects_list import BuildUnitsEffect
from effect import Effect

class WonderTemplate:
    def __init__(self, name: str, age: int, on_build: Effect | list[Effect] = [], per_turn: Effect | list[Effect] = [], vp_reward: int = 5, abilities: list[Ability] = [], override_description: str | None = None):
        self.name = name
        self.age = age
        self.on_build: list[Effect] = on_build if isinstance(on_build, list) else [on_build]
        self.per_turn: list[Effect] = per_turn if isinstance(per_turn, list) else [per_turn]
        self.vp_reward = vp_reward
        self.abilities = abilities
        self._override_description = override_description

    def __repr__(self):
        return f"<WonderTemplate {self.name})>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WonderTemplate):
            return False
        return self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def description(self) -> list[str]:
        if self._override_description is not None:
            return [self._override_description]
        effect_descs = [f"On build: {e.description}" for e in self.on_build] + [f"Per turn: {e.description}" for e in self.per_turn]
        effect_descs.extend([f"Passive: {a.description}" for a in self.abilities])
        return effect_descs
    
    def hover_unit_name(self) -> str:
        for eff in self.per_turn + self.on_build:
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

