from typing import Optional
from civ_template import CivTemplate


class GamePlayer:
    def __init__(self, player_num: int, username: str, is_bot: bool = False):
        self.player_num = player_num
        self.username = username
        self.score = 0
        self.score_from_killing_units = 0
        self.score_from_capturing_cities_and_camps = 0
        self.score_from_researching_techs = 0
        self.score_from_building_vps = 0
        self.score_from_abilities = 0
        self.score_from_survival = 0
        self.score_from_revolting_cities = 0
        self.renaissances = 0
        self.decline_this_turn = False

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
            "sfku": self.score_from_killing_units,
            "sfccac": self.score_from_capturing_cities_and_camps,
            "sfrt": self.score_from_researching_techs,
            "sfbv": self.score_from_building_vps,
            "sfa": self.score_from_abilities,
            "sfs": self.score_from_survival,
            "sfrc": self.score_from_revolting_cities,
            "renaissances": self.renaissances,
            "decline_this_turn": self.decline_this_turn,
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
        game_player.score_from_killing_units = json["sfku"]
        game_player.score_from_capturing_cities_and_camps = json["sfccac"]
        game_player.score_from_researching_techs = json["sfrt"]
        game_player.score_from_building_vps = json["sfbv"]
        game_player.score_from_abilities = json["sfa"]
        game_player.score_from_survival = json["sfs"]
        game_player.score_from_revolting_cities = json["sfrc"]
        game_player.renaissances = json["renaissances"]
        game_player.decline_this_turn = json["decline_this_turn"]

        return game_player

