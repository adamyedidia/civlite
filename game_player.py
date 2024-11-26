from typing import Optional, TYPE_CHECKING
from settings import STRICT_MODE

from tenet_template import TenetTemplate
from tenet_template_list import TENETS

if TYPE_CHECKING:
    from game_state import GameState
    from civ import Civ

class GamePlayer:
    def __init__(self, player_num: int, username: str, is_bot: bool = False, vitality_multiplier: float = 1.0):
        self.player_num = player_num
        self.username = username
        self.score_dict = {}  # TODO(dfarhi) it would be nice to not store this duplicative with civ's score_dicts.
        self.decline_this_turn = False
        self.failed_to_decline_this_turn = False
        self.all_civ_ids: list[str] = []

        self.civ_id: Optional[str] = None

        self.is_bot = is_bot
        self.vitality_multiplier = vitality_multiplier

        self.tenets: dict[TenetTemplate, dict] = {}
        self.active_tenet_choice_level: Optional[int] = None

    @property
    def score(self) -> int:
        return sum(self.score_dict.values())
    
    def has_tenet(self, tenet: TenetTemplate, check_complete_quest: bool = False) -> bool:
        if not tenet in self.tenets:
            return False
        if check_complete_quest and tenet.quest_target > 0:
            return self.tenets[tenet]["progress"] >= tenet.quest_target
        return True
    
    def increment_tenet_progress(self, tenet: TenetTemplate):
        if tenet.quest_target > 0:
            self.tenets[tenet]["progress"] += 1

    def select_tenet(self, tenet: TenetTemplate, game_state: 'GameState'):
        if STRICT_MODE:
            assert tenet not in self.tenets
            assert game_state.tenets_claimed_by_player_nums[tenet] == []
        if tenet.initialize_data is not None:
            self.tenets[tenet] = tenet.initialize_data(self)
        else:
            self.tenets[tenet] = {}
        if tenet.quest_target > 0:
            self.tenets[tenet]["progress"] = 0
        if tenet.instant_effect is not None:
            civ = self.get_current_civ(game_state)
            target = civ.capital_city(game_state)
            if target is None:
                my_cities = civ.get_my_cities(game_state)
                if my_cities:
                    target = max(my_cities, key=lambda c: c.population)
                else:
                    target = None
            if target is not None:
                tenet.instant_effect.apply(city=target, game_state=game_state)
        self.update_active_tenet_choice_level(game_state)

    def get_current_civ(self, game_state: 'GameState') -> 'Civ':
        assert self.civ_id is not None
        return game_state.civs_by_id[self.civ_id]
    
    def update_active_tenet_choice_level(self, game_state: 'GameState'):
        civ_level = self.get_current_civ(game_state).get_advancement_level()
        tenet_level = len(self.tenets)
        if tenet_level < civ_level:
            self.active_tenet_choice_level = tenet_level + 1
        else:
            self.active_tenet_choice_level = None

    def to_json(self) -> dict:
        return {
            "player_num": self.player_num,
            "username": self.username,
            "score": self.score,
            "score_dict": self.score_dict,
            "civ_id": self.civ_id,
            "is_bot": self.is_bot,
            "decline_this_turn": self.decline_this_turn,
            "failed_to_decline_this_turn": self.failed_to_decline_this_turn,
            "all_civ_ids": self.all_civ_ids,
            "vitality_multiplier": self.vitality_multiplier,
            "tenets": {t.name: info for t, info in self.tenets.items()},
            "active_tenet_choice_level": self.active_tenet_choice_level,
        }
    
    @staticmethod
    def from_json(json: dict) -> "GamePlayer":
        game_player = GamePlayer(
            player_num=json["player_num"],
            username=json["username"],
            is_bot=json["is_bot"],
            vitality_multiplier=json["vitality_multiplier"],
        )
        game_player.civ_id = json["civ_id"]
        game_player.score_dict = json["score_dict"]
        game_player.decline_this_turn = json["decline_this_turn"]
        game_player.failed_to_decline_this_turn = json["failed_to_decline_this_turn"]
        game_player.all_civ_ids = json["all_civ_ids"]
        game_player.tenets = {TENETS.by_name(name): info for name, info in json["tenets"].items()}
        game_player.active_tenet_choice_level = json["active_tenet_choice_level"]

        return game_player

