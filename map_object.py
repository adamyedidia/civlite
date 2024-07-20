from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from civ import Civ
    from hex import Hex

class MapObject:
    def __init__(self, civ: 'Civ | None' = None, hex: 'Hex | None' = None):
        self._hex: 'Hex | None' = hex
        self._partially_loaded_hex_coords: str | None = None
        self._civ: 'Civ | None' = civ
        self._partially_loaded_civ_id: str | None = None

    @property
    def hex(self) -> 'Hex':
        assert self._hex is not None
        return self._hex
    
    def finish_loading_hex(self, hex: 'Hex'):
        assert self._hex is None and hex.coords == self._partially_loaded_hex_coords, f"hex coords {hex.coords} != {self._partially_loaded_hex_coords}"
        self._hex = hex
        self._partially_loaded_hex_coords = None

    def update_hex(self, hex: 'Hex'):
        assert self._hex is not None
        self._hex = hex

    @property
    def civ(self) -> 'Civ':
        assert self._civ is not None
        return self._civ
    
    def finish_loading_civ(self, civs_by_id: dict[str, 'Civ']) -> None:
        assert self._partially_loaded_civ_id is not None and self._civ is None
        self._civ = civs_by_id[self._partially_loaded_civ_id]
        self._partially_loaded_civ_id = None

    def update_civ(self, civ: 'Civ'):
        assert self._civ is not None
        self._civ = civ
    
    def to_json(self):
        return {
            "hex": self.hex.coords,
            "civ_id": self.civ.id,
        }
    
    def from_json(self, json):
        self._partially_loaded_civ_id = json["civ_id"]
        self._partially_loaded_hex_coords = json["hex"]