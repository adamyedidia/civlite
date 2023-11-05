class TechTemplate:
    def __init__(self, name: str, cost: int):
        self.name = name
        self.cost = cost

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "cost": self.cost,
        }
    
    @staticmethod
    def from_json(json: dict) -> "TechTemplate":
        return TechTemplate(
            name=json["name"],
            cost=json["cost"],
        )
