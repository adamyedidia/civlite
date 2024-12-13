from collections import defaultdict
from typing import Optional
import random

from civ import Civ

from typing import TYPE_CHECKING
from civ_templates_list import CIVS
from map_object_spawner import MapObjectSpawner
from settings import CAMP_CLEAR_CITY_POWER_REWARD, CAMP_CLEAR_VP_REWARD, STRICT_MODE
from tenet_template_list import TENETS

from unit_template import UnitTag, UnitTemplate
from unit_templates_list import UNITS
from utils import generate_unique_id

if TYPE_CHECKING:
    from hex import Hex
    from game_state import GameState

UNITS_BY_AGE: dict[int, set[UnitTemplate]] = defaultdict(set)
for unit in UNITS.all():
    UNITS_BY_AGE[unit.advancement_level].add(unit)

def random_unit_by_age(advancement_level) -> UnitTemplate:
    if advancement_level <= 0:
        return UNITS.WARRIOR
    if len(UNITS_BY_AGE[advancement_level]) > 0:
        return random.choice(list(UNITS_BY_AGE[advancement_level]))
    else:
        return random_unit_by_age(advancement_level - 1)

class Camp(MapObjectSpawner):
    def __init__(self, civ: Civ | None = None, advancement_level=0, unit: UnitTemplate | None = None, hex: 'Hex | None' = None, turn_spawned: int=0):
        super().__init__(civ, hex)
        self.id = generate_unique_id("CAMP")
        self.target: Optional['Hex'] = None
        self.turn_spawned = turn_spawned
        if STRICT_MODE:
            assert unit is None or advancement_level == 0, f"Only set one of unit and advancement_level"
        self.unit: UnitTemplate = unit or random_unit_by_age(advancement_level)

    def __repr__(self):
        return f"Camp(id={self.id}, hex={self.hex.coords if self._hex else None})"

    def build_unit(self, game_state: 'GameState', unit: UnitTemplate, stack_size: int = 1) -> bool:
        self.target = game_state.pick_random_hex()

        if not self.hex.is_occupied(self.civ, allow_enemy_city=False):
            self.civ.spawn_unit_on_hex(game_state, unit, self.hex, stack_size=stack_size)
            return True

        free_neighbors = [h for h in self.hex.get_neighbors(game_state.hexes, exclude_ocean=True) if not h.is_occupied(self.civ, allow_enemy_city=False)]
        if self.unit.has_tag(UnitTag.DEFENSIVE):
            free_neighbors = [h for h in free_neighbors if not any(n.units and n.units[0].civ == self.civ and n.units[0].template == self.unit for n in h.get_neighbors(game_state.hexes))]
        if len(free_neighbors) > 0:
            best_hex = random.choice(free_neighbors)
            self.civ.spawn_unit_on_hex(game_state, unit, best_hex, stack_size=stack_size)
            return True

        if self.hex.units and self.hex.units[0].civ == self.civ and self.hex.units[0].template == self.unit:
            self.hex.units[0].health += 100 * stack_size
            return True
        
        for hex in self.hex.get_neighbors(game_state.hexes, exclude_ocean=True):
            if hex.units and hex.units[0].civ == self.civ and hex.units[0].template == self.unit:
                hex.units[0].health += 100 * stack_size
                return True
            
        return False


    @property
    def no_cities_adjacent_range(self) -> int:
        return 0

    def capture(self, sess, civ: Civ, game_state: 'GameState') -> None:
        civ.city_power += CAMP_CLEAR_CITY_POWER_REWARD
        civ.gain_vps(CAMP_CLEAR_VP_REWARD, f"Clearing Camps ({CAMP_CLEAR_VP_REWARD}/camp)")
        if civ.has_tenet(TENETS.HONOR):
            civ.gain_vps(CAMP_CLEAR_VP_REWARD, f"Honor")

        game_state.add_animation_frame(sess, {
            "type": "CampClear",
            "civ": civ.template.name,
            "vpReward": CAMP_CLEAR_VP_REWARD,
            "cityPowerReward": CAMP_CLEAR_CITY_POWER_REWARD,
        }, hexes_must_be_visible=[self.hex])

        game_state.unregister_camp(self)

    def roll_turn(self, sess, game_state: 'GameState') -> None:
        self.handle_siege(sess, game_state)
        if self.hex.camp is None:
            # The camp got cleared, it shouldn't spawn.
            return
        if self.unit.advancement_level < game_state.advancement_level - 3 and random.random() < 0.2 and self.under_siege_by_civ is None:
            # This camp is too old. It makes a last hurrah and then dies.
            self.build_unit(game_state, self.unit, stack_size=3)
            game_state.unregister_camp(self)

        # Game players that own camps through great bath get double production.
        produce_unit = (game_state.turn_num % 2 == self.turn_spawned % 2) or (not self.civ.template == CIVS.BARBARIAN)
        if produce_unit:
            self.build_unit(game_state, self.unit)

    def to_json(self):
        return {
            **super().to_json(),
            "id": self.id,
            "hex": self.hex.coords,
            "civ_id": self.civ.id,
            "unit": self.unit.name,
            "turn_spawned": self.turn_spawned,
        }
    
    @staticmethod
    def from_json(json: dict):
        camp = Camp()
        super(Camp, camp).from_json(json)
        camp.id = json["id"]
        camp.unit = UNITS.by_name(json["unit"])
        camp.turn_spawned = json["turn_spawned"]
        return camp

