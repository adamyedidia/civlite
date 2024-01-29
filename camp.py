from collections import defaultdict
from typing import Optional

from civ import Civ

from typing import TYPE_CHECKING
from settings import CAMP_CLEAR_CITY_POWER_REWARD, CAMP_CLEAR_VP_REWARD
from unit import Unit

from unit_template import UnitTemplate
from unit_templates_list import UNITS
from utils import generate_unique_id

if TYPE_CHECKING:
    from hex import Hex
    from game_state import GameState


class Camp:
    def __init__(self, civ: Civ):
        self.id = generate_unique_id()
        self.under_siege_by_civ: Optional[Civ] = None
        self.hex: Optional['Hex'] = None        
        self.civ: Civ = civ
        self.target: Optional['Hex'] = None

    def update_nearby_hexes_visibility(self, game_state: 'GameState', short_sighted: bool = False) -> None:
        if self.hex is None:
            return
        self.hex.visibility_by_civ[self.civ.id] = True

        if short_sighted:
            neighbors = self.hex.get_neighbors(game_state.hexes)
        else:
            neighbors = self.hex.get_hexes_within_distance_2(game_state.hexes)

        for nearby_hex in neighbors:
            nearby_hex.visibility_by_civ[self.civ.id] = True

    def build_unit(self, sess, game_state: 'GameState', unit: UnitTemplate) -> bool:
        if not self.hex:
            return False

        self.target = game_state.pick_random_hex()

        if not self.hex.is_occupied(unit.type, self.civ):
            self.spawn_unit_on_hex(sess, game_state, unit, self.hex)
            return True

        best_hex = None
        best_hex_distance_from_target = 10000

        for hex in self.hex.get_neighbors(game_state.hexes):
            if not hex.is_occupied(unit.type, self.civ):
                distance_from_target = hex.distance_to(self.target or self.hex)
                if distance_from_target < best_hex_distance_from_target:
                    best_hex = hex
                    best_hex_distance_from_target = distance_from_target

        if best_hex is None:
            for hex in self.hex.get_distance_2_hexes(game_state.hexes):
                if not hex.is_occupied(unit.type, self.civ):
                    distance_from_target = hex.distance_to(self.target or self.hex)
                    if distance_from_target < best_hex_distance_from_target:
                        best_hex = hex
                        best_hex_distance_from_target = distance_from_target            

        if best_hex is None:
            return False
        self.spawn_unit_on_hex(sess, game_state, unit, best_hex)
        return True

    def spawn_unit_on_hex(self, sess, game_state: 'GameState', unit_template: UnitTemplate, hex: 'Hex') -> None:
        if self.hex is None:
            return
        unit = Unit(unit_template, self.civ)
        unit.hex = hex
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
        if self.hex is None:
            return None

        for unit in self.hex.units:
            if unit.civ.id != self.civ.id and unit.template.type == 'military':
                return unit.civ

        num_neighboring_units_by_civ_name = defaultdict(int)

        for hex in self.hex.get_neighbors(game_state.hexes):
            for unit in hex.units:
                if unit.template.type == 'military':
                    num_neighboring_units_by_civ_name[unit.civ.id] += 1

        for civ_name, num_neighboring_units in num_neighboring_units_by_civ_name.items():
            if num_neighboring_units >= 4:
                return game_state.get_civ_by_name(civ_name)

        return None

    def clear(self, sess, civ: Civ, game_state: 'GameState') -> None:
        civ.city_power += CAMP_CLEAR_CITY_POWER_REWARD
        if civ.game_player:
            civ.game_player.score += CAMP_CLEAR_VP_REWARD

        if self.hex:
            game_state.add_animation_frame(sess, {
                "type": "CampClear",
                "civ": civ.template.name,
                "vpReward": CAMP_CLEAR_VP_REWARD,
                "cityPowerReward": CAMP_CLEAR_CITY_POWER_REWARD,
            }, hexes_must_be_visible=[self.hex])

            self.hex.camp = None

        self.hex = None

    def update_civ_by_id(self, civs_by_id: dict[str, Civ]) -> None:
        self.civ = civs_by_id[self.civ.id]
        self.under_siege_by_civ = civs_by_id[self.under_siege_by_civ.id] if self.under_siege_by_civ else None            

    def roll_turn(self, sess, game_state: 'GameState') -> None:
        if game_state.turn_num % 2 == 0:
            self.build_unit(sess, game_state, UnitTemplate.from_json(UNITS["Warrior"]))

        self.handle_siege(sess, game_state)


    def to_json(self):
        return {
            "id": self.id,
            "under_siege_by_civ": self.under_siege_by_civ.to_json() if self.under_siege_by_civ else None,
            "hex": self.hex.coords if self.hex else None,
            "civ": self.civ.to_json(),
        }
    
    @staticmethod
    def from_json(json: dict):
        camp = Camp(civ=Civ.from_json(json["civ"]))
        camp.id = json["id"]
        camp.under_siege_by_civ = Civ.from_json(json["under_siege_by_civ"]) if json["under_siege_by_civ"] else None
        return camp