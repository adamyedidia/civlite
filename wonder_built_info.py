from civ import Civ

class WonderBuiltInfo:
    def __init__(self, player_nums: list[int | None], civs: list[Civ], turn_num: int) -> None:
        self.player_nums = player_nums
        self.civs = civs
        self.turn_num = turn_num

    def __repr__(self) -> str:
        return f"WonderBuiltInfo(player_nums={self.player_nums}, civs={self.civs}, turn_num={self.turn_num})"

    def to_json(self):
        return {
            "player_nums": self.player_nums,
            "civ_ids": [civ.id for civ in self.civs],
            "turn_num": self.turn_num
        }
    
    @staticmethod
    def from_json(json, game_state) -> "WonderBuiltInfo":
        civs: list[Civ] = [game_state.civs_by_id[civ_id] for civ_id in json["civ_ids"]]
        return WonderBuiltInfo(json["player_nums"], civs, json["turn_num"])
