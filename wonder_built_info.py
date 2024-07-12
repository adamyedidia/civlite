class WonderBuiltInfo:
    def __init__(self, turn_num: int) -> None:
        self.infos: list[tuple[str, str]] = []
        self.turn_num = turn_num

    def __repr__(self) -> str:
        return f"WonderBuiltInfo(infos={self.infos}, turn_num={self.turn_num})"

    def to_json(self):
        return {
            "infos": [(city_id, civ_id) for city_id, civ_id in self.infos],
            "turn_num": self.turn_num
        }
    
    @staticmethod
    def from_json(json) -> "WonderBuiltInfo":
        info = WonderBuiltInfo(json["turn_num"])
        info.infos = [(city_id, civ_id) for city_id, civ_id in json["infos"]]
        return info
        
