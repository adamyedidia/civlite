from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from civ import Civ
    from hex import Hex

class MapObject:
    def __init__(self):
        self._hex: 'Hex | None' = None
        self._civ: 'Civ | None' = None

    @property
    def hex(self) -> 'Hex':
        assert self._hex is not None
        return self._hex
    
    def set_hex(self, hex: 'Hex'):
        assert self._hex is None
        self._hex = hex

    def update_hex(self, hex: 'Hex'):
        assert self._hex is not None
        self._hex = hex