import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from civ import Civ
    from game_state import GameState
    from hex import Hex
    from unit import Unit
    from unit_template import UnitTemplate

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
        self._civ = civs_by_id[self._partially_loaded_civ_id]
        self._partially_loaded_civ_id = None

    def update_civ(self, civ: 'Civ'):
        assert self._civ is not None
        self._civ = civ

    def from_json_postprocess(self, game_state: 'GameState') -> None:
        self._finish_loading_civ(game_state.civs_by_id)
        self._finish_loading_hex(game_state.hexes)

    def get_closest_target(self) -> 'Hex | None':
        target1 = self.civ.target1
        target2 = self.civ.target2

        if target1 is None and target2 is None:
            return None
        
        if target1 is None:
            return target2
        
        if target2 is None:
            return target1
        
        if self.hex.distance_to(target1) <= self.hex.distance_to(target2):
            return target1
        else:
            return target2

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

    def spawn_unit_on_hex(self, game_state: 'GameState', unit_template: 'UnitTemplate', hex: 'Hex', bonus_strength: int=0, stack_size=1) -> 'Unit | None':
        from unit import Unit
        unit = Unit(unit_template, civ=self.civ, hex=hex)
        unit.health *= stack_size
        hex.units.append(unit)
        game_state.units.append(unit)
        unit.strength += bonus_strength

        return unit

    def get_siege_state(self, game_state: 'GameState') -> 'Civ | None':
        for unit in self.hex.units:
            if unit.civ.id != self.civ.id and unit.template.type == 'military':
                return unit.civ
        return None

    def handle_siege(self, sess, game_state: 'GameState') -> None:
        siege_state = self.get_siege_state(game_state)

        if self.under_siege_by_civ is None:
            self.under_siege_by_civ = siege_state
        else:
            if siege_state is None or siege_state.id != self.under_siege_by_civ.id:
                self.under_siege_by_civ = siege_state
            else:
                self.capture(sess, siege_state, game_state)

    @abc.abstractmethod
    def capture(self, sess, siege_state: 'Civ', game_state: 'GameState') -> None:
        pass

    def to_json(self):
        return {
            "hex": self.hex.coords,
            "civ_id": self.civ.id,
        }
    
    def from_json(self, json):
        self._partially_loaded_civ_id = json["civ_id"]
        self._partially_loaded_hex_coords = json["hex"]