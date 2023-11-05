from typing import Optional
from unit import Unit
from utils import coords_str
from yields import Yields
from city import City


class Hex:
    def __init__(self, q: int, r: int, s: int, yields: Yields) -> None:
        assert not (q + r + s)
        self.q = q
        self.r = r
        self.s = s
        self.yields = yields
        self.units: list[Unit] = []
        self.city: Optional[City] = None
        self.coords = coords_str((q, r, s))

    def distance_to(self, other: "Hex") -> int:
        return max(abs(self.q - other.q), abs(self.r - other.r), abs(self.s - other.s))

    def is_occupied(self, unit_type: str) -> bool:
        return any(unit.template.type == unit_type for unit in self.units)

    def to_json(self) -> dict:
        return {
            "q": self.q,
            "r": self.r,
            "s": self.s,
            "yields": self.yields.to_json(),
            "units": [unit.to_json() for unit in self.units],
            "city": self.city.to_json() if self.city else None,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Hex":
        hex = Hex(
            q=json["q"],
            r=json["r"],
            s=json["s"],
            yields=Yields.from_json(json["yields"]),
        )
        hex.units = [Unit.from_json(unit_json) for unit_json in json["units"]]
        if json["city"]:
            hex.city = City.from_json(json["city"])

        return hex