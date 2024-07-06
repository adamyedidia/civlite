from typing import TYPE_CHECKING, Generator, Optional
from camp import Camp
from civ import Civ
from terrain_templates_list import TERRAINS
from terrain_template import TerrainTemplate
from unit import Unit
from utils import coords_str
from yields import Yields
from city import City

if TYPE_CHECKING:
    from game_state import GameState


class Hex:
    def __init__(self, q: int, r: int, s: int, terrain: TerrainTemplate, yields: Yields, has_building_slot: bool = False) -> None:
        assert not (q + r + s)
        self.q = q
        self.r = r
        self.s = s
        self.terrain = terrain
        self.has_building_slot = has_building_slot
        self.yields = yields
        self.units: list[Unit] = []
        self.city: Optional[City] = None
        self.camp: Optional[Camp] = None
        self.coords = coords_str((q, r, s))
        self.visibility_by_civ: dict[str, bool] = {}
        self.is_foundable_by_civ: dict[str, bool] = {}

    def visible_to_civ(self, civ: Civ) -> bool:
        return self.visibility_by_civ.get(civ.id, False)

    def __repr__(self):
        return f"<Hex {self.coords}>"

    def distance_to(self, other: "Hex") -> int:
        return max(abs(self.q - other.q), abs(self.r - other.r), abs(self.s - other.s))

    # distance_to, but it prefers to move to hexes that are not a straight line away
    def sensitive_distance_to(self, other: "Hex") -> float:
        return self.distance_to(other) - 0.000001 * abs(self.q - other.q) * abs(self.r - other.r) * abs(self.s - other.s)

    def remove_unit(self, unit: Unit) -> None:
        self.units = [u for u in self.units if u.id != unit.id]

    def hexes_at_offsets(self, offsets: list[tuple[int, int, int]], hexes: dict[str, "Hex"]) -> Generator["Hex", None, None]:
        for (delta_q, delta_r, delta_s) in offsets:
            neighbor = hexes.get(coords_str((self.q + delta_q, self.r + delta_r, self.s + delta_s)))
            if neighbor:
                yield neighbor

    def get_neighbors(self, hexes: dict[str, "Hex"], include_self=False) -> Generator["Hex", None, None]:
        yield from self.hexes_at_offsets([
            (1, 0, -1),
            (1, -1, 0),
            (0, -1, 1),
            (-1, 0, 1),
            (-1, 1, 0),
            (0, 1, -1),
        ], hexes)
        if include_self:
            yield self

    def get_distance_2_hexes(self, hexes: dict[str, "Hex"]) -> Generator["Hex", None, None]:
        yield from self.hexes_at_offsets([
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
        ], hexes)
    
    def get_distance_3_hexes(self, hexes: dict[str, "Hex"]) -> Generator["Hex", None, None]:
        yield from self.hexes_at_offsets([
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
        ], hexes)

    def get_hexes_within_range(self, hexes: dict[str, "Hex"], range: int) -> Generator["Hex", None, None]:
        assert range > 0 and range <= 3
        if range >= 1:
            yield from self.get_neighbors(hexes, include_self=True)
        if range >= 2:
            yield from self.get_distance_2_hexes(hexes)
        if range >= 3:
            yield from self.get_distance_3_hexes(hexes)
    
    def get_hexes_within_range_expensive(self, hexes: dict[str, "Hex"], range: int) -> Generator["Hex", None, None]:
        for hex in hexes.values():
            if hex.distance_to(self) <= range:
                yield hex

    def is_occupied(self, unit_type: str, civ: Civ) -> bool:
        """
        Is this hex occupied by a unit of this type or by an enemy of this civ?
        """
        return any(unit.template.type == unit_type or unit.civ.template.name != civ.template.name for unit in self.units)

    def is_threatened_city(self, game_state):
        """ Is there an enemy unit adjacent? """
        if not self.city: return False
        for hex in self.get_neighbors(game_state.hexes):
            if hex.units and hex.units[0].civ.id != self.city.civ.id:
                return True
        return False

    def from_json_postprocess(self, game_state: 'GameState') -> None:
        for unit in self.units:
            unit.update_civ_by_id(game_state.civs_by_id)
            unit.hex = self
            # Don't append here; they got added in GameState.init
            # game_state.units.append(unit)
        if self.city:
            self.city.update_civ_by_id(game_state.civs_by_id)
            self.city.hex = self
            game_state.cities_by_id[self.city.id] = self.city
        if self.camp:
            self.camp.update_civ_by_id(game_state.civs_by_id)          
            self.camp.hex = self

    def to_json(self, from_civ_perspectives: Optional[list[Civ]] = None) -> dict:
        return {
            "q": self.q,
            "r": self.r,
            "s": self.s,
            "terrain": self.terrain.name,
            "has_building_slot": self.has_building_slot,
            **({
                "yields": self.yields.to_json(),
                "units": [unit.to_json() for unit in self.units],
                "city": self.city.to_json() if self.city else None,
                "camp": self.camp.to_json() if self.camp else None,
                "visibility_by_civ": self.visibility_by_civ,
                "is_foundable_by_civ": self.is_foundable_by_civ,
            } if (from_civ_perspectives is None or any([self.visible_to_civ(from_civ_perspective) for from_civ_perspective in from_civ_perspectives])) and self.yields is not None else {}),
        }
    
    @staticmethod
    def from_json(json: dict) -> "Hex":
        hex = Hex(
            q=json["q"],
            r=json["r"],
            s=json["s"],
            terrain=TERRAINS.by_name(json["terrain"]),
            has_building_slot=json["has_building_slot"],
            yields=Yields.from_json(json['yields']) if 'yields' in json else Yields(),
        )
        hex.units = [Unit.from_json(unit_json) for unit_json in json.get("units") or []]
        if json.get("city"):
            hex.city = City.from_json(json.get("city")) if "city" in json else None  # type: ignore
        if json.get("camp"):
            hex.camp = Camp.from_json(json.get("camp")) if "camp" in json else None  # type: ignore
        hex.visibility_by_civ = (json.get("visibility_by_civ") or {}).copy()
        if json.get("is_foundable_by_civ"):
            hex.is_foundable_by_civ = (json.get("is_foundable_by_civ") or {}).copy()

        return hex

