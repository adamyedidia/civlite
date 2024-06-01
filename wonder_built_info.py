from civ import Civ
from city import City

class WonderBuiltInfo:
    def __init__(self, turn_num: int) -> None:
        self.infos: list[tuple[City, Civ]] = []
        self.turn_num = turn_num

    def __repr__(self) -> str:
        return f"WonderBuiltInfo(infos={self.infos}, turn_num={self.turn_num})"

    def to_json(self):
        return {
            "infos": [(city.id, civ.id) for city, civ in self.infos],
            "turn_num": self.turn_num
        }
    
    @staticmethod
    def from_json(json, game_state) -> "WonderBuiltInfo":
        info = WonderBuiltInfo(json["turn_num"])
        info.infos = [(game_state.cities_by_id[city_id], game_state.civs_by_id[civ_id]) for city_id, civ_id in json["infos"]]
        return info
        
