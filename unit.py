from math import sqrt
from random import random
from typing import TYPE_CHECKING, Optional
from animation_frame import AnimationFrame
from civ import Civ
from settings import UNIT_KILL_REWARD
from unit_template import UnitTemplate
from unit_templates_list import UNITS
from utils import generate_unique_id

if TYPE_CHECKING:
    from game_state import GameState
    from hex import Hex


class Unit:
    def __init__(self, template: UnitTemplate, civ: Civ) -> None:
        self.id = generate_unique_id()
        self.template = template
        self.health = 100
        self.civ = civ
        self.has_moved = False
        self.target: Optional['Hex'] = None
        self.hex: Optional['Hex'] = None

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

    def move(self, sess, game_state: 'GameState', sensitive: bool = False) -> None:
        if self.has_moved or self.hex is None or self.target is None:
            return
        should_move_sensitively = sensitive
        starting_hex = self.hex
        coord_strs = [starting_hex.coords]
        for _ in range(self.template.movement):
            if self.move_one_step(game_state, coord_strs, sensitive=should_move_sensitively):
                self.has_moved = True
                should_move_sensitively = True

        if self.has_moved:
            new_hex = self.hex

            self.update_nearby_hexes_visibility(game_state)

            game_state.add_animation_frame(sess, {
                "type": "UnitMovement",
                "coords": coord_strs,
            }, hexes_must_be_visible=[starting_hex, new_hex])

            if new_hex.coords == self.target.coords and (target := self.get_best_target(new_hex.get_hexes_within_range(game_state.hexes, 2))) is not None:
                self.target = target.hex

    def attack(self, sess, game_state: 'GameState') -> None:
        if self.hex is None or self.target is None:
            return
        hexes_to_check = self.hex.get_hexes_within_range(game_state.hexes, self.template.range)

        best_target = self.get_best_target(hexes_to_check)

        if best_target is not None:
            self.fight(sess, game_state, best_target)

    def get_best_target(self, hexes_to_check: list['Hex']) -> Optional['Unit']:
        if self.hex is None or self.target is None:
            return None

        type_scores = {
            'military': 1,
            'support': 2,
        }

        best_target = None
        best_target_distance = 10
        best_target_type_score = 10
        best_target_strength = 10000

        for hex in hexes_to_check:
            if hex.visibility_by_civ.get(self.civ.id):
                for unit in hex.units:
                    if unit.civ.id != self.civ.id:
                        distance = self.hex.distance_to(hex)
                        if distance < best_target_distance:
                            best_target = unit
                            best_target_distance = distance
                            best_target_type_score = type_scores[unit.template.type]
                            best_target_strength = unit.template.strength
                        elif distance == best_target_distance and type_scores[unit.template.type] < best_target_type_score:
                            best_target = unit
                            best_target_distance = distance
                            best_target_type_score = type_scores[unit.template.type]
                            best_target_strength = unit.template.strength
                        elif distance == best_target_distance and type_scores[unit.template.type] == best_target_type_score and unit.template.strength < best_target_strength:
                            best_target = unit
                            best_target_distance = distance
                            best_target_type_score = type_scores[unit.template.type]
                            best_target_strength = unit.template.strength

        return best_target

    def get_damage_to_deal_from_effective_strengths(self, effective_strength: float, target_effective_strength: float) -> int:
        ratio_of_strengths = effective_strength / target_effective_strength

        # This is a very scientific formula
        return int(round(40 ** sqrt(ratio_of_strengths)))

    def punch(self, game_state: 'GameState', target: 'Unit') -> None:
        self.effective_strength = self.template.strength * (1 + self.health / 100)
        target.effective_strength = target.template.strength

        target.health = max(0, target.health - self.get_damage_to_deal_from_effective_strengths(self.effective_strength, target.effective_strength))

        if target.health == 0:
            target.die(game_state)
            if (game_player := self.civ.game_player) is not None:
                game_player.score += UNIT_KILL_REWARD

    def fight(self, sess, game_state: 'GameState', target: 'Unit') -> None:
        if self.hex is None or target.hex is None:
            return

        self.punch(game_state, target)
        if self.template.ranged:
            target.target = self.hex
        else:
            target.punch(game_state, self)

        game_state.add_animation_frame(sess, {
            "type": "UnitAttack",
            "start_coords": self.hex.coords,
            "end_coords": target.hex.coords,
        }, hexes_must_be_visible=[self.hex, target.hex])

    def die(self, game_state: 'GameState'):
        if self.hex is None:
            return

        self.hex.units = [unit for unit in self.hex.units if unit.id != self.id]
        game_state.units = [unit for unit in game_state.units if unit.id != self.id]
        self.hex = None

    def move_one_step(self, game_state: 'GameState', coord_strs: list[str], sensitive: bool = False) -> bool:
        if self.hex is not None and self.target is not None:
            neighbors = self.hex.get_neighbors(game_state.hexes)
            random.shuffle(neighbors)
            for neighboring_hex in self.hex.get_neighbors(game_state.hexes):

                if sensitive:
                    my_sensitive_distance_to_target = self.hex.sensitive_distance_to(self.target)
                    neighboring_hex_sensitive_distance_to_target = neighboring_hex.sensitive_distance_to(self.target)
                    is_better_distance = neighboring_hex_sensitive_distance_to_target < my_sensitive_distance_to_target
                else:
                    my_distance_to_target = self.hex.distance_to(self.target)
                    neighboring_hex_distance_to_target = neighboring_hex.distance_to(self.target)
                    is_better_distance = neighboring_hex_distance_to_target < my_distance_to_target

                if is_better_distance and not neighboring_hex.is_occupied(self.template.type, self.civ):
                    self.take_one_step_to_hex(neighboring_hex)
                    coord_strs.append(neighboring_hex.coords)

                    return True
                
        return False

    def take_one_step_to_hex(self, hex: 'Hex') -> None:
        if self.hex is not None:
            self.hex.remove_unit(self)
        self.hex = hex
        hex.units.append(self)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.template.name,
            "attack": self.attack,
            "health": self.health,
            "civ": self.civ.to_json(),
            "target": self.target,
            "has_moved": self.has_moved,
            "coords": self.hex.coords if self.hex is not None else None,
        }
    
    @staticmethod
    def from_json(json: dict,) -> "Unit":
        unit = Unit(
            template=UnitTemplate.from_json(UNITS[json["name"]]),
            civ=Civ.from_json(json["civ"]),
        )
        unit.id = json["id"]
        unit.attack = json["attack"]
        unit.health = json["health"]
        unit.has_moved = json["has_moved"]
        unit.target = json["target"]

        return unit