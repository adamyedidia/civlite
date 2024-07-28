from collections import defaultdict
from typing import Optional
import random

from civ import Civ

from typing import TYPE_CHECKING
from map_object_spawner import MapObjectSpawner
from settings import CAMP_CLEAR_CITY_POWER_REWARD, CAMP_CLEAR_VP_REWARD, STRICT_MODE

from unit_template import UnitTemplate
from unit_templates_list import UNITS
from utils import generate_unique_id

if TYPE_CHECKING:
    from hex import Hex
    from game_state import GameState

UNITS_BY_AGE: dict[int, set[UnitTemplate]] = defaultdict(set)
for unit in UNITS.all():
    UNITS_BY_AGE[unit.advancement_level()].add(unit)

def random_unit_by_age(advancement_level) -> UnitTemplate:
    if advancement_level <= 0:
        return UNITS.WARRIOR
    if len(UNITS_BY_AGE[advancement_level]) > 0:
        return random.choice(list(UNITS_BY_AGE[advancement_level]))
    else:
        return random_unit_by_age(advancement_level - 1)

class Camp(MapObjectSpawner):
    def __init__(self, civ: Civ | None = None, advancement_level=0, unit: UnitTemplate | None = None, hex: 'Hex | None' = None):
        super().__init__(civ, hex)
        self.id = generate_unique_id()
        self.target: Optional['Hex'] = None
        if STRICT_MODE:
            assert unit is None or advancement_level == 0, f"Only set one of unit and advancement_level"
        self.unit: UnitTemplate = unit or random_unit_by_age(advancement_level)

    def __repr__(self):
        return f"Camp(id={self.id}, hex={self.hex.coords if self._hex else None})"

    def build_unit(self, game_state: 'GameState', unit: UnitTemplate) -> bool:
        self.target = game_state.pick_random_hex()

        if not self.hex.is_occupied(unit.type, self.civ):
            self.civ.spawn_unit_on_hex(game_state, unit, self.hex)
            return True

        best_hex = None
        best_hex_distance_from_target = 10000

        for hex in self.hex.get_neighbors(game_state.hexes):
            if not hex.is_occupied(unit.type, self.civ, allow_enemy_city=False):
                distance_from_target = hex.distance_to(self.target or self.hex)
                if distance_from_target < best_hex_distance_from_target:
                    best_hex = hex
                    best_hex_distance_from_target = distance_from_target

        if best_hex is None:
            for hex in self.hex.get_distance_2_hexes(game_state.hexes):
                if not hex.is_occupied(unit.type, self.civ, allow_enemy_city=False):
                    distance_from_target = hex.distance_to(self.target or self.hex)
                    if distance_from_target < best_hex_distance_from_target:
                        best_hex = hex
                        best_hex_distance_from_target = distance_from_target            

        if best_hex is None:
            return False
        self.civ.spawn_unit_on_hex(game_state, unit, best_hex)
        return True

    @property
    def no_cities_adjacent_range(self) -> int:
        return 0

    def capture(self, sess, civ: Civ, game_state: 'GameState') -> None:
        civ.city_power += CAMP_CLEAR_CITY_POWER_REWARD
        civ.gain_vps(CAMP_CLEAR_VP_REWARD, f"Clearing Camps ({CAMP_CLEAR_VP_REWARD}/camp)")

        game_state.add_animation_frame(sess, {
            "type": "CampClear",
            "civ": civ.template.name,
            "vpReward": CAMP_CLEAR_VP_REWARD,
            "cityPowerReward": CAMP_CLEAR_CITY_POWER_REWARD,
        }, hexes_must_be_visible=[self.hex])

        game_state.unregister_camp(self)

    def roll_turn(self, sess, game_state: 'GameState') -> None:
        self.handle_siege(sess, game_state)
        if game_state.turn_num % 2 == 0:
            self.build_unit(game_state, self.unit)

    def to_json(self):
        return {
            **super().to_json(),
            "id": self.id,
            "hex": self.hex.coords,
            "civ_id": self.civ.id,
            "unit": self.unit.name
        }
    
    @staticmethod
    def from_json(json: dict):
        camp = Camp()
        super(Camp, camp).from_json(json)
        camp.id = json["id"]
        camp.unit = UNITS.by_name(json["unit"])
        return camp

