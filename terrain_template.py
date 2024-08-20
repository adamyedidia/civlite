from utils import deterministic_hash
from yields import Yields


class TerrainTemplate:
    def __init__(self, name: str, yields: Yields, bonus_yields: Yields, frequency: float):
        self.name = name
        self.yields = yields
        self.bonus_yields = bonus_yields
        self.frequency = frequency

    def __hash__(self):
        return deterministic_hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
    
    def __str__(self):
        return self.name