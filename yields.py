

class Yields:
    def __init__(self, food: int, metal: int, stone: int, science: int) -> None:
        self.food = food
        self.metal = metal
        self.stone = stone
        self.science = science

    def to_json(self) -> dict:
        return {
            "food": self.food,
            "metal": self.metal,
            "stone": self.stone,
            "science": self.science,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Yields":
        return Yields(
            food=json["food"],
            metal=json["metal"],
            stone=json["stone"],
            science=json["science"],
        )