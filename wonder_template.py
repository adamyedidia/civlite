
from ability import Ability
from effects_list import BuildUnitsEffect
from effect import CityTargetEffect
from utils import deterministic_hash
from yields import YieldsCalculation

class WonderTemplate:
    def __init__(self, name: str, age: int, on_build: CityTargetEffect | list[CityTargetEffect] = [], per_turn: CityTargetEffect | list[CityTargetEffect] = [], vp_reward: int = 5, abilities: list[Ability] = [], override_description: str | None = None, calculate_yields: YieldsCalculation | None = None):
        self.name = name
        self.advancement_level = age
        self.on_build: list[CityTargetEffect] = on_build if isinstance(on_build, list) else [on_build]
        self.per_turn: list[CityTargetEffect] = per_turn if isinstance(per_turn, list) else [per_turn]
        self.vp_reward = vp_reward
        self.abilities = abilities
        self._override_description = override_description
        self.calculate_yields = calculate_yields

    def __repr__(self):
        return f"<WonderTemplate {self.name})>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WonderTemplate):
            return False
        return self.name == other.name
    
    def __lt__(self, other: 'WonderTemplate'):
        # Sort by age, with larger ages first.
        return (-self.advancement_level, self.name) < (-other.advancement_level, other.name)
    
    def __hash__(self) -> int:
        return deterministic_hash(self.name)
    
    def description(self) -> list[str]:
        if self._override_description is not None:
            return [self._override_description]
        effect_descs = [f"On build: {e.description}" for e in self.on_build] + [f"Per turn: {e.description}" for e in self.per_turn]
        effect_descs.extend([f"Passive: {a.description}" for a in self.abilities])
        if self.calculate_yields is not None:
            effect_descs.append(f"Yields per turn: {self.calculate_yields.description} (ignores vitality)")
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
            "advancement_level": self.advancement_level,
            "vp_reward": self.vp_reward,
            "hover_unit_name": self.hover_unit_name(),
        }

