class GamePlayer:
    def __init__(self, player_num: int, username: str):
        self.player_num = player_num
        self.username = username
        self.score = 0

    def to_json(self) -> dict:
        return {
            "player_num": self.player_num,
            "username": self.username,
            "score": self.score,
        }
    
    @staticmethod
    def from_json(json: dict) -> "GamePlayer":
        return GamePlayer(
            player_num=json["player_num"],
            username=json["username"],
        )