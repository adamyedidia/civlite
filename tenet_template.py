from typing import Callable, TYPE_CHECKING
from effect import CityTargetEffect

if TYPE_CHECKING:
    from game_state import GameState


class TenetTemplate:
    def __init__(self, name, advancement_level, initialize_data: Callable[['GameState'], dict] | None=None, description: str | None=None, instant_effect: CityTargetEffect | None=None, quest_description: str | None=None, quest_target: int = 0, quest_complete_message: str | None=None):
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
        self.quest_complete_message = quest_complete_message

        if any([self.quest_description, self.quest_complete_message, self.quest_target]):
            assert all([self.quest_description, self.quest_complete_message, self.quest_target]), "quest_description, quest_complete_message, and quest_target must all be provided"

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "quest_description": self.quest_description,
            "advancement_level": self.advancement_level
        }