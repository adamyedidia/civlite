from typing import Optional

class GamePlayer:
    def __init__(self, player_num: int, username: str, is_bot: bool = False):
        self.player_num = player_num
        self.username = username
        self.score_dict = {}  # TODO(dfarhi) it would be nice to not store this duplicative with civ's score_dicts.
        self.renaissances = 0
        self.decline_this_turn = False
        self.failed_to_decline_this_turn = False
        self.all_civ_ids: list[str] = []

        self.civ_id: Optional[str] = None

        self.is_bot = is_bot

    @property
    def score(self) -> int:
        return sum(self.score_dict.values())

    def to_json(self) -> dict:
        return {
            "player_num": self.player_num,
            "username": self.username,
            "score": self.score,
            "score_dict": self.score_dict,
            "civ_id": self.civ_id,
            "is_bot": self.is_bot,
            "renaissances": self.renaissances,
            "decline_this_turn": self.decline_this_turn,
            "failed_to_decline_this_turn": self.failed_to_decline_this_turn,
            "all_civ_ids": self.all_civ_ids,
        }
    
    @staticmethod
    def from_json(json: dict) -> "GamePlayer":
        game_player = GamePlayer(
            player_num=json["player_num"],
            username=json["username"],
            is_bot=json["is_bot"],
        )
        game_player.civ_id = json["civ_id"]
        game_player.score_dict = json["score_dict"]
        game_player.renaissances = json["renaissances"]
        game_player.decline_this_turn = json["decline_this_turn"]
        game_player.failed_to_decline_this_turn = json["failed_to_decline_this_turn"]
        game_player.all_civ_ids = json["all_civ_ids"]

        return game_player

