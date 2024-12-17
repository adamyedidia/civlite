import abc
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from civ import Civ
    from game_state import GameState
    from hex import Hex

class MapObject(abc.ABC):
    def __init__(self, civ: 'Civ | None' = None, hex: 'Hex | None' = None):
        self._hex: 'Hex | None' = hex
        self._partially_loaded_hex_coords: str | None = None
        self._civ: 'Civ | None' = civ
        self._partially_loaded_civ_id: str | None = None

    @property
    def hex(self) -> 'Hex':
        assert self._hex is not None
        return self._hex
    
    def _finish_loading_hex(self, hexes: dict[str, 'Hex']):
        assert self._partially_loaded_hex_coords is not None and self._hex is None
        hex = hexes[self._partially_loaded_hex_coords]
        assert hex.coords == self._partially_loaded_hex_coords, f"hex coords {hex.coords} != {self._partially_loaded_hex_coords}"
        self._hex = hex
        self._partially_loaded_hex_coords = None

    def update_hex(self, hex: 'Hex'):
        assert self._hex is not None
        self._hex = hex

    @property
    def civ(self) -> 'Civ':
        assert self._civ is not None
        return self._civ
    
    def _finish_loading_civ(self, civs_by_id: dict[str, 'Civ']) -> None:
        assert self._partially_loaded_civ_id is not None and self._civ is None
        assert self._partially_loaded_civ_id in civs_by_id, f"civ id {self._partially_loaded_civ_id} not in civs_by_id.\n{self}\n{civs_by_id}"
        self._civ = civs_by_id[self._partially_loaded_civ_id]
        self._partially_loaded_civ_id = None

    def update_civ(self, civ: 'Civ'):
        assert self._civ is not None
        self._civ = civ

    def from_json_postprocess(self, game_state: 'GameState') -> None:
        self._finish_loading_civ(game_state.civs_by_id)
        self._finish_loading_hex(game_state.hexes)

    def get_closest_target(self) -> 'Hex | None':
        """
        Returns the target closest to the given hex. If there are multiple targets at the same distance, returns one at random.
        """        
        targets = self.civ.targets

        if not targets:
            return None
        if not self.hex:
            return None

        targets_copy = targets[:]
        random.shuffle(targets_copy)
        return min(targets_copy, key=lambda target: self.hex.distance_to(target))

    def sight_range(self, short_sighted: bool) -> int:
        return 2 if short_sighted else 1
    
    @property
    def no_cities_adjacent_range(self) -> int | None:
        return None

    def update_nearby_hexes_visibility(self, game_state: 'GameState', short_sighted: bool = False) -> None:
        range = self.sight_range(short_sighted)
        neighbors = self.hex.get_hexes_within_range(game_state.hexes, range)

        for nearby_hex in neighbors:
            nearby_hex.visibility_by_civ[self.civ.id] = True

    def update_nearby_hexes_hostile_foundability(self, hexes: dict[str, 'Hex']) -> None:
        # No one can make cities adjacent to an enemy MapObject.
        for hex in self.hex.get_neighbors(hexes, include_self=True):
            for key in hex.is_foundable_by_civ:
                if key != self.civ.id:
                    hex.is_foundable_by_civ[key] = False

        # Even myself can't make cities within no_cities_adjacent_range
        if self.no_cities_adjacent_range is not None:
            for hex in self.hex.get_hexes_within_range(hexes, self.no_cities_adjacent_range):
                hex.is_foundable_by_civ[self.civ.id] = False

    def to_json(self):
        return {
            "hex": self.hex.coords,
            "civ_id": self.civ.id,
        }
    
    def from_json(self, json):
        self._partially_loaded_civ_id = json["civ_id"]
        self._partially_loaded_hex_coords = json["hex"]