from typing import Callable, TYPE_CHECKING
from effect import CityTargetEffect
from unit_template import UnitTag

if TYPE_CHECKING:
    from game_state import GameState
    from game_player import GamePlayer


class TenetTemplate:
    def __init__(self, name, advancement_level, initialize_data: Callable[['GamePlayer', 'GameState'], dict] | None=None, description: str | None=None, 
                 instant_effect: CityTargetEffect | None=None, 
                 quest_description: str | None=None, quest_target: int = 0, quest_complete_message: str | None=None, 
                 a5_unit_types: list[UnitTag] | None=None,
                 a6_score_key: str | None=None, a6_score_weights: list[float] | None=None,
                 a7_yield: str | None=None):
        self.name = name
        if description is not None:
            self.description = description
        elif instant_effect is not None:
            self.description = instant_effect.description
        elif a5_unit_types is not None:
            self.description = f"+10 city power for each kill by a {' or '.join([unit_type.name for unit_type in a5_unit_types])} unit."
        else:
            raise ValueError("Either description, instant_effect, or a5_unit_types must be provided.")
        self.advancement_level = advancement_level
        self.quest_description = quest_description
        self.instant_effect = instant_effect
        self.initialize_data = initialize_data
        self.quest_target = quest_target
        self.quest_complete_message = quest_complete_message
        self.a5_unit_types = a5_unit_types
        self.a6_score_key = a6_score_key
        self.a6_score_weights = a6_score_weights
        self.a7_yield = a7_yield

        if any([self.quest_description, self.quest_complete_message, self.quest_target]):
            assert all([self.quest_description, self.quest_complete_message, self.quest_target]), "quest_description, quest_complete_message, and quest_target must all be provided"
        if any([self.a6_score_key, self.a6_score_weights]):
            assert all([self.a6_score_key, self.a6_score_weights]), "a6_score_key and a6_score_weights must all be provided"

    def __repr__(self):
        return f"<TenetTemplate {self.name}>"

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "quest_description": self.quest_description,
            "advancement_level": self.advancement_level
        }