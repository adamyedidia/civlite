

class Yields:
    def __init__(self, food: int, metal: int, wood: int, science: int) -> None:
        self.food = food
        self.metal = metal
        self.wood = wood
        self.science = science

    def copy(self) -> "Yields":
        return Yields(
            food=self.food,
            metal=self.metal,
            wood=self.wood,
            science=self.science,
        )

    def to_json(self) -> dict:
        return {
            "food": self.food,
            "metal": self.metal,
            "wood": self.wood,
            "science": self.science,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Yields":
        return Yields(
            food=json["food"],
            metal=json["metal"],
            wood=json["wood"],
            science=json["science"],
        )