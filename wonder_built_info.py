from civ import Civ

class WonderBuiltInfo:
    def __init__(self, player_num: int, civ: Civ, turn_num: int) -> None:
        self.player_num = player_num
        self.civ = civ
        self.turn_num = turn_num

    def to_json(self):
        return {
            "player_num": self.player_num,
            "civ_id": self.civ.id,
            "turn_num": self.turn_num
        }
    
    @staticmethod
    def from_json(json, game_state) -> "WonderBuiltInfo":
        civ: Civ = game_state.civs_by_id[json["civ_id"]]
        return WonderBuiltInfo(json["player_num"], civ, json["turn_num"])
