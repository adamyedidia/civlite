from typing import TYPE_CHECKING, Optional
from camp import Camp
from civ import Civ
from unit import Unit
from utils import coords_str
from yields import Yields
from city import City

if TYPE_CHECKING:
    from game_state import GameState


class Hex:
    def __init__(self, q: int, r: int, s: int, terrain: str, yields: Yields) -> None:
        assert not (q + r + s)
        self.q = q
        self.r = r
        self.s = s
        self.terrain = terrain
        self.yields = yields
        self.units: list[Unit] = []
        self.city: Optional[City] = None
        self.camp: Optional[Camp] = None
        self.coords = coords_str((q, r, s))
        self.visibility_by_civ: dict[str, bool] = {}
        self.is_foundable_by_civ: dict[str, bool] = {}

    def distance_to(self, other: "Hex") -> int:
        return max(abs(self.q - other.q), abs(self.r - other.r), abs(self.s - other.s))

    # distance_to, but it prefers to move to hexes that are not a straight line away
    def sensitive_distance_to(self, other: "Hex") -> float:
        return self.distance_to(other) - 0.000001 * abs(self.q - other.q) * abs(self.r - other.r) * abs(self.s - other.s)

    def remove_unit(self, unit: Unit) -> None:
        self.units = [u for u in self.units if u.id != unit.id]

    def get_neighbors(self, hexes: dict[str, "Hex"]) -> list["Hex"]:
        neighbors = []
        for (delta_q, delta_r, delta_s) in [
            (1, 0, -1),
            (1, -1, 0),
            (0, -1, 1),
            (-1, 0, 1),
            (-1, 1, 0),
            (0, 1, -1),
        ]:
            neighbor = hexes.get(coords_str((self.q + delta_q, self.r + delta_r, self.s + delta_s)))
            if neighbor:
                neighbors.append(neighbor)
        return neighbors

    def get_distance_2_hexes(self, hexes: dict[str, "Hex"]) -> list["Hex"]:
        neighbors = []
        for (delta_q, delta_r, delta_s) in [
            (2, 0, -2),
            (2, -2, 0),
            (0, -2, 2),
            (-2, 0, 2),
            (-2, 2, 0),
            (0, 2, -2),
            (2, -1, -1),
            (1, -2, 1),
            (-1, -1, 2),
            (-2, 1, 1),
            (-1, 2, -1),
            (1, 1, -2),
        ]:
            neighbor = hexes.get(coords_str((self.q + delta_q, self.r + delta_r, self.s + delta_s)))
            if neighbor:
                neighbors.append(neighbor)
        return neighbors
    
    def get_distance_3_hexes(self, hexes: dict[str, "Hex"]) -> list["Hex"]:
        neighbors = []
        for (delta_q, delta_r, delta_s) in [
            (3, 0, -3),
            (3, -3, 0),
            (0, -3, 3),
            (-3, 0, 3),
            (-3, 3, 0),
            (0, 3, -3),
            (3, -1, -2),
            (3, -2, -1),
            (1, -3, 2),
            (2, -3, 1),
            (-1, -2, 3),
            (-2, -1, 3),
            (-3, 1, 2),
            (-3, 2, 1),
            (-2, 3, -1),
            (-1, 3, -2),
            (1, 2, -3),
            (2, 1, -3),
        ]:
            neighbor = hexes.get(coords_str((self.q + delta_q, self.r + delta_r, self.s + delta_s)))
            if neighbor:
                neighbors.append(neighbor)
        return neighbors

    def get_hexes_within_distance_2(self, hexes: dict[str, "Hex"]) -> list["Hex"]:
        return [*self.get_neighbors(hexes), *self.get_distance_2_hexes(hexes)]
    
    def get_hexes_within_distance_3(self, hexes: dict[str, "Hex"]) -> list["Hex"]:
        return [*self.get_neighbors(hexes), *self.get_distance_2_hexes(hexes), *self.get_distance_3_hexes(hexes)]
    
    def get_hexes_within_range(self, hexes: dict[str, "Hex"], range: int) -> list["Hex"]:
        assert range > 0 and range <= 3
        if range == 1:
            return self.get_neighbors(hexes)
        elif range == 2:
            return self.get_hexes_within_distance_2(hexes)
        elif range == 3:
            return self.get_hexes_within_distance_3(hexes)
        else:
            raise Exception("Invalid range")

    def is_occupied(self, unit_type: str, civ: Civ) -> bool:
        return any(unit.template.type == unit_type or unit.civ.template.name != civ.template.name for unit in self.units)

    def update_civ_by_id(self, civs_by_id: dict[str, Civ]) -> None:
        for unit in self.units:
            unit.update_civ_by_id(civs_by_id)
        if self.city:
            self.city.update_civ_by_id(civs_by_id)
        if self.camp:
            self.camp.update_civ_by_id(civs_by_id)          

    def to_json(self, from_civ_perspectives: Optional[list[Civ]] = None) -> dict:
        return {
            "q": self.q,
            "r": self.r,
            "s": self.s,
            "terrain": self.terrain,
            **({
                "yields": self.yields.to_json(),
                "units": [unit.to_json() for unit in self.units],
                "city": self.city.to_json() if self.city else None,
                "camp": self.camp.to_json() if self.camp else None,
                "visibility_by_civ": self.visibility_by_civ,
                "is_foundable_by_civ": self.is_foundable_by_civ,
            } if from_civ_perspectives is None or any([self.visibility_by_civ.get(from_civ_perspective.id) for from_civ_perspective in from_civ_perspectives]) else {}),
        }
    
    @staticmethod
    def from_json(json: dict) -> "Hex":
        hex = Hex(
            q=json["q"],
            r=json["r"],
            s=json["s"],
            terrain=json["terrain"],
            yields=Yields.from_json(json["yields"]),
        )
        hex.units = [Unit.from_json(unit_json) for unit_json in json["units"]]
        if json.get("city"):
            hex.city = City.from_json(json["city"])
        if json.get("camp"):
            hex.camp = Camp.from_json(json["camp"])
        hex.visibility_by_civ = json["visibility_by_civ"].copy()
        hex.is_foundable_by_civ = json["is_foundable_by_civ"].copy()

        return hex