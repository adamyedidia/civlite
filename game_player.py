from typing import Optional


class GamePlayer:
    def __init__(self, player_num: int, username: str):
        self.player_num = player_num
        self.username = username
        self.score = 0
        self.civ_id: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "player_num": self.player_num,
            "username": self.username,
            "score": self.score,
            "civ_id": self.civ_id,
        }
    
    @staticmethod
    def from_json(json: dict) -> "GamePlayer":
        game_player = GamePlayer(
            player_num=json["player_num"],
            username=json["username"],
        )
        game_player.score = json["score"]
        game_player.civ_id = json["civ_id"]

        return game_player