from typing import Optional
from civ_template import CivTemplate


class GamePlayer:
    def __init__(self, player_num: int, username: str, is_bot: bool = False):
        self.player_num = player_num
        self.username = username
        self.score = 0
        self.civ_id: Optional[str] = None

        # (hex coords, civ name, city_id)
        self.decline_options: list[tuple[str, str, str]] = []
        self.is_bot = is_bot

    def to_json(self) -> dict:
        return {
            "player_num": self.player_num,
            "username": self.username,
            "score": self.score,
            "civ_id": self.civ_id,
            "decline_options": self.decline_options,
            "is_bot": self.is_bot,
        }
    
    @staticmethod
    def from_json(json: dict) -> "GamePlayer":
        game_player = GamePlayer(
            player_num=json["player_num"],
            username=json["username"],
            is_bot=json["is_bot"],
        )
        game_player.score = json["score"]
        game_player.civ_id = json["civ_id"]
        game_player.decline_options = json["decline_options"]

        return game_player