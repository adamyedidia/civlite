from typing import List

class TechTemplate:
    def __init__(self, name: str, cost: int, advancement_level: int, unlocks_units: List[str] = [], unlocks_buildings: List[str] = []):

        self.name = name
        self.cost = cost
        self.advancement_level = advancement_level
        self.unlocks_units = unlocks_units
        self.unlocks_buildings = unlocks_buildings
        
    def __repr__(self):
        return f"<TechTemplate {self.name}>"

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, TechTemplate):
            return False
        return self.name == __value.name

    def __hash__(self) -> int:
        return hash(self.name)

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "cost": self.cost,
            "advancement_level": self.advancement_level,
            "unlocks_units": self.unlocks_units,
            "unlocks_buildings": self.unlocks_buildings,
        }
    
    @staticmethod
    def from_json(json: dict) -> "TechTemplate":
        raise ValueError("Don't get Templates from json, just look them up by name in TECHS.")
