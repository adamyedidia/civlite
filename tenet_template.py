from typing import Callable, TYPE_CHECKING
from effect import CityTargetEffect

if TYPE_CHECKING:
    from game_player import GamePlayer


class TenetTemplate:
    def __init__(self, name, advancement_level, initialize_data: Callable[['GamePlayer'], dict] | None=None, description: str | None=None, instant_effect: CityTargetEffect | None=None, quest_description: str | None=None, quest_target: int = 0):
        self.name = name
        if description is not None:
            self.description = description
        elif instant_effect is not None:
            self.description = instant_effect.description
        else:
            raise ValueError("Either description or instant_effect must be provided.")
        self.advancement_level = advancement_level
        self.quest_description = quest_description
        self.instant_effect = instant_effect
        self.initialize_data = initialize_data
        self.quest_target = quest_target

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "advancement_level": self.advancement_level
        }