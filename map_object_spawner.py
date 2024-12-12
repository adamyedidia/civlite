import abc
from typing import TYPE_CHECKING
from civ_templates_list import CIVS

from map_object import MapObject
from tenet_template_list import TENETS
from unit import Unit

if TYPE_CHECKING:
    from civ import Civ
    from hex import Hex
    from game_state import GameState
    from unit_template import UnitTemplate

class MapObjectSpawner(MapObject):
    def __init__(self, civ: 'Civ | None', hex: 'Hex | None'):
        super().__init__(civ, hex)
        self.under_siege_by_civ: 'Civ | None' = None
        self._partially_loaded_under_siege_by_civ_id: str | None = None

    def _finish_loading_under_siege_by_civ(self, civs_by_id: dict[str, 'Civ']) -> None:
        assert self.under_siege_by_civ is None
        if self._partially_loaded_under_siege_by_civ_id is not None:
            self.under_siege_by_civ = civs_by_id[self._partially_loaded_under_siege_by_civ_id]
            self._partially_loaded_under_siege_by_civ_id = None

    def get_siege_state(self, game_state: 'GameState') -> 'Civ | None':
        for unit in self.hex.units:
            if unit.civ.id != self.civ.id:
                return unit.civ
        return None

    def handle_siege(self, sess, game_state: 'GameState') -> None:
        siege_state = self.get_siege_state(game_state)
        if siege_state is None:
            self.under_siege_by_civ = None
            return
        
        if self.under_siege_by_civ == siege_state or (siege_state.has_tenet(TENETS.HYMN_OF_UNITY) and siege_state.get_advancement_level() > self.civ.get_advancement_level()) and self.civ.template != CIVS.BARBARIAN:
            self.capture(sess, siege_state, game_state)
        else:
            self.under_siege_by_civ = siege_state

    @abc.abstractmethod
    def capture(self, sess, siege_state: 'Civ', game_state: 'GameState') -> None:
        pass

    def from_json_postprocess(self, game_state: 'GameState') -> None:
        super().from_json_postprocess(game_state)
        self._finish_loading_under_siege_by_civ(game_state.civs_by_id)

    def to_json(self):
        return {
            **super().to_json(),
            "under_siege_by_civ_id": self.under_siege_by_civ.id if self.under_siege_by_civ is not None else None
        }
    
    def from_json(self, json):
        super().from_json(json)
        self._partially_loaded_under_siege_by_civ_id = json["under_siege_by_civ_id"]
