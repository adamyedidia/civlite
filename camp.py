from collections import defaultdict
from typing import Optional
import random

from civ import Civ

from typing import TYPE_CHECKING
from map_object import MapObject
from settings import CAMP_CLEAR_CITY_POWER_REWARD, CAMP_CLEAR_VP_REWARD, STRICT_MODE
from unit import Unit

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

class Camp(MapObject):
    def __init__(self, civ: Civ, advancement_level=0, unit: UnitTemplate | None = None):
        # civ actually can be None very briefly before GameState.from_json() is done, 
        # but I don't want to tell the type-checker so we don't have to put a million asserts everywhere

        super().__init__()
        self.id = generate_unique_id()
        self.under_siege_by_civ: Optional[Civ] = None
        self.civ: Civ = civ
        self.civ_id: str = civ.id if civ else None  # type: ignore
        self.target: Optional['Hex'] = None
        if STRICT_MODE:
            assert unit is None or advancement_level == 0, f"Only set one of unit and advancement_level"
        self.unit: UnitTemplate = unit or random_unit_by_age(advancement_level)

    def update_nearby_hexes_visibility(self, game_state: 'GameState', short_sighted: bool = False) -> None:
        if short_sighted:
            neighbors = self.hex.get_neighbors(game_state.hexes, include_self=True)
        else:
            neighbors = self.hex.get_hexes_within_range(game_state.hexes, 2)

        for nearby_hex in neighbors:
            nearby_hex.visibility_by_civ[self.civ.id] = True

    def build_unit(self, sess, game_state: 'GameState', unit: UnitTemplate) -> bool:
        self.target = game_state.pick_random_hex()

        if not self.hex.is_occupied(unit.type, self.civ):
            self.spawn_unit_on_hex(sess, game_state, unit, self.hex)
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
        self.spawn_unit_on_hex(sess, game_state, unit, best_hex)
        return True

    def spawn_unit_on_hex(self, sess, game_state: 'GameState', unit_template: UnitTemplate, hex: 'Hex') -> None:
        unit = Unit(unit_template, self.civ)
        unit.set_hex(hex)
        hex.units.append(unit)
        game_state.units.append(unit)
        if self.hex.coords != unit.hex.coords:
            game_state.add_animation_frame_for_civ(sess, {
                "type": "UnitSpawn",
                "start_coords": self.hex.coords,
                "end_coords": unit.hex.coords,
            }, self.civ)

    def handle_siege(self, sess, game_state: 'GameState') -> None:
        siege_state = self.get_siege_state(game_state)

        if self.under_siege_by_civ is None:
            self.under_siege_by_civ = siege_state
        else:
            if siege_state is None or siege_state.id != self.under_siege_by_civ.id:
                self.under_siege_by_civ = siege_state
            else:
                self.clear(sess, siege_state, game_state)

    def get_siege_state(self, game_state: 'GameState') -> Optional[Civ]:
        for unit in self.hex.units:
            if unit.civ.id != self.civ.id and unit.template.type == 'military':
                return unit.civ

        # num_neighboring_units_by_civ_name = defaultdict(int)

        # for hex in self.hex.get_neighbors(game_state.hexes):
        #     for unit in hex.units:
        #         if unit.template.type == 'military':
        #             num_neighboring_units_by_civ_name[unit.civ.template.name] += 1

        # for civ_name, num_neighboring_units in num_neighboring_units_by_civ_name.items():
        #     if num_neighboring_units >= 4 and civ_name != self.civ.template.name:
        #         return game_state.get_civ_by_name(civ_name)

        return None

    def update_nearby_hexes_hostile_foundability(self, hexes: dict[str, 'Hex']) -> None:
        for hex in self.hex.get_neighbors(hexes, include_self=True):
            for key in hex.is_foundable_by_civ:
                if key != self.civ.id or hex == self.hex:
                    hex.is_foundable_by_civ[key] = False

    def clear(self, sess, civ: Civ, game_state: 'GameState') -> None:
        civ.city_power += CAMP_CLEAR_CITY_POWER_REWARD
        civ.gain_vps(CAMP_CLEAR_VP_REWARD, f"Clearing Camps ({CAMP_CLEAR_VP_REWARD}/camp)")

        game_state.add_animation_frame(sess, {
            "type": "CampClear",
            "civ": civ.template.name,
            "vpReward": CAMP_CLEAR_VP_REWARD,
            "cityPowerReward": CAMP_CLEAR_CITY_POWER_REWARD,
        }, hexes_must_be_visible=[self.hex])

        game_state.unregister_camp(self)

    def update_civ_by_id(self, civs_by_id: dict[str, Civ]) -> None:
        self.civ = civs_by_id[self.civ_id]
        self.under_siege_by_civ = civs_by_id[self.under_siege_by_civ] if self.under_siege_by_civ else None  # type: ignore

    def roll_turn(self, sess, game_state: 'GameState') -> None:
        self.handle_siege(sess, game_state)
        if game_state.turn_num % 2 == 0:
            self.build_unit(sess, game_state, self.unit)

    def to_json(self):
        return {
            "id": self.id,
            "under_siege_by_civ_id": self.under_siege_by_civ.id if self.under_siege_by_civ else None,
            "hex": self.hex.coords,
            "civ_id": self.civ.id,
            "unit": self.unit.name
        }
    
    @staticmethod
    def from_json(json: dict):
        camp = Camp(civ=None)  # type: ignore
        camp.id = json["id"]
        camp.civ_id = json["civ_id"]
        camp.under_siege_by_civ = json["under_siege_by_civ_id"]
        camp.unit = UNITS.by_name(json["unit"])
        return camp

