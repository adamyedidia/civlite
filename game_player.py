from typing import Optional, TYPE_CHECKING
from settings import STRICT_MODE
from tech_templates_list import TECHS

from tenet_template import TenetTemplate
from tenet_template_list import TENETS, tenets_by_level

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
        self.a6_tenet_info: Optional[dict] = None
        self.fog_cities: dict[str, dict] = {}
        self.fog_camp_coords_with_turn: dict[str, int] = {}

    @property
    def score(self) -> int:
        return sum(self.score_dict.values())
    
    def has_tenet(self, tenet: TenetTemplate, check_complete_quest: bool = False) -> bool:
        if not tenet in self.tenets:
            return False
        if check_complete_quest and tenet.is_quest:
            return self.tenets[tenet]["complete"]
        return True

    def tenet_at_level(self, level: int) -> TenetTemplate | None:
        if len(self.tenets) >= level:
            return [t for t in self.tenets if t.advancement_level == level][0]
        return None
    
    def increment_tenet_progress(self, tenet: TenetTemplate, game_state: 'GameState', amount: int = 1):
        if tenet.is_quest:
            self.tenets[tenet]["progress"] += amount

    def quest_roll_turn(self, game_state: 'GameState'):
        if self.has_tenet(TENETS.FOUNTAIN_OF_YOUTH):
            for tech_name in self.tenets[TENETS.FOUNTAIN_OF_YOUTH]["unclaimed_techs"]:
                tech = TECHS.by_name(tech_name)
                if any(c.has_tech(tech) for c in game_state.civs_by_id.values()):
                    self.tenets[TENETS.FOUNTAIN_OF_YOUTH]["unclaimed_techs"].remove(tech_name)

        for tenet in self.tenets:
            if tenet.is_quest and self.tenets[tenet]["progress"] >= tenet.quest_target and not self.tenets[tenet]["complete"]:
                self.tenets[tenet]["complete"] = True
                game_state.add_parsed_announcement({
                    "turn_num": game_state.turn_num,
                    "type": "quest_complete",
                    "civ_id": self.civ_id,
                    "player_num": self.player_num,
                    "message_for_civ": f'QUEST COMPLETE: {tenet.quest_complete_message}',
                })

    def get_tenet_target_city(self, game_state):
        civ = self.get_current_civ(game_state)
        target = civ.capital_city(game_state)
        if target is None:
            my_cities = civ.get_my_cities(game_state)
            if my_cities:
                target = max(my_cities, key=lambda c: c.population)
            else:
                target = None
        return target

    def select_tenet(self, tenet: TenetTemplate, game_state: 'GameState'):
        prior_claimants = len(game_state.tenets_claimed_by_player_nums[tenet])
        if STRICT_MODE:
            assert tenet not in self.tenets
            assert prior_claimants == 0 or (prior_claimants == 1 and game_state.duplicate_tenets_claimable(tenet.advancement_level))
        if prior_claimants > 0:
            self.get_current_civ(game_state).gain_vps(-5, "Copycat tenet")
        if tenet.initialize_data is not None:
            self.tenets[tenet] = tenet.initialize_data(self, game_state)
        else:
            self.tenets[tenet] = {}
        if tenet.is_quest:
            self.tenets[tenet]["progress"] = 0
            self.tenets[tenet]["complete"] = False
        if tenet.instant_effect is not None:
            target = self.get_tenet_target_city(game_state)
            if target is not None:
                tenet.instant_effect.apply(city=target, game_state=game_state)
        if self.active_tenet_choice_level == 6:
            assert self.a6_tenet_info is not None and tenet.name in self.a6_tenet_info
            self.get_current_civ(game_state).gain_vps(self.a6_tenet_info[tenet.name]["score"], self.a6_tenet_info[tenet.name]["full_name"])
        self.update_active_tenet_choice_level(game_state)

    def get_current_civ(self, game_state: 'GameState') -> 'Civ':
        assert self.civ_id is not None
        return game_state.civs_by_id[self.civ_id]
    
    def update_active_tenet_choice_level(self, game_state: 'GameState'):
        civ_level = self.get_current_civ(game_state).get_advancement_level()
        tenet_level = len(self.tenets)
        if tenet_level < civ_level and len(tenets_by_level[tenet_level + 1]) > 0:
            self.active_tenet_choice_level = tenet_level + 1
        else:
            self.active_tenet_choice_level = None
        
        self.a6_tenet_info = {}
        first_three_civs = [game_state.civs_by_id[civ_id] for civ_id in self.all_civ_ids[:3]]
        for tenet in tenets_by_level[6]:
            assert tenet.a6_score_key is not None and tenet.a6_score_weights is not None
            key: str = tenet.a6_score_key
            weights: list[float] = tenet.a6_score_weights
            best_idx = max(range(len(first_three_civs)), key=lambda i: first_three_civs[i].score_dict.get(key, 0) * weights[i])
            self.a6_tenet_info[tenet.name] = {
                "full_name": f"{tenet.name} of {first_three_civs[best_idx].template.name}",
                "score": int(first_three_civs[best_idx].score_dict.get(key, 0) * weights[best_idx]),
            }

    def tenet_quest_display(self) -> dict:
        quest_tenet = [t for t in self.tenets if t.is_quest]
        if not quest_tenet:
            return {}
        quest_tenet = quest_tenet[0]
        return {
            "name": quest_tenet.name,
            "progress": self.tenets[quest_tenet]["progress"],
            "target": quest_tenet.quest_target,
            "complete": self.tenets[quest_tenet]["complete"],
        }
    
    def add_fog_city(self, city):
        self.fog_cities[city.hex.coords] = {
            "name": city.name,
            "capital": city.capital and city.civ.game_player is not None,
        }

    def to_json(self) -> dict:
        a7_tenet = self.tenet_at_level(7)
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
            "fog_cities": self.fog_cities,
            "fog_camp_coords_with_turn": self.fog_camp_coords_with_turn,
            "tenets": {t.name: info for t, info in self.tenets.items()},
            "active_tenet_choice_level": self.active_tenet_choice_level,
            "tenet_quest": self.tenet_quest_display(),
            "a6_tenet_info": self.a6_tenet_info,
            "a7_tenet_yield": a7_tenet.a7_yield if a7_tenet is not None else None,
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
        game_player.fog_cities = json["fog_cities"]
        game_player.fog_camp_coords_with_turn = json["fog_camp_coords_with_turn"]
        game_player.tenets = {TENETS.by_name(name): info for name, info in json["tenets"].items()}
        game_player.active_tenet_choice_level = json["active_tenet_choice_level"]
        game_player.a6_tenet_info = json["a6_tenet_info"]

        return game_player

