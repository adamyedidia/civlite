from math import sqrt
from random import random, shuffle
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
        self.hex: Optional['Hex'] = None
        self.strength = self.template.strength
        self.has_attacked = False
        self.destination = None

    def __repr__(self):
        return f"<Unit {self.civ.moniker()} {self.template.name} @ {self.hex.coords if self.hex is not None else None}"

    def midturn_update(self, game_state):
        self.calculate_destination_hex(game_state)
        print(f"Calculating for {self} => {self.destination.coords if self.destination else None}")

    def has_ability(self, ability_name: str) -> bool:
        return any([ability.name == ability_name for ability in self.template.abilities])

    def numbers_of_ability(self, ability_name: str) -> list:
        return [ability.numbers for ability in self.template.abilities if ability.name == ability_name][0]

    def get_closest_target(self) -> Optional['Hex']:
        if not self.hex:
            return None

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
        print(f"Moving {self} => {self.destination}")
        if self.has_moved or self.hex is None or self.get_closest_target() is None or self.has_attacked:
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
            }, hexes_must_be_visible=[starting_hex, new_hex], no_commit=True)

    def attack(self, sess, game_state: 'GameState') -> None:
        if self.hex is None or self.has_attacked:
            return

        hexes_to_check = self.hex.get_hexes_within_range(game_state.hexes, self.template.range)

        best_target = self.get_best_target(hexes_to_check)

        if best_target is not None:
            self.fight(sess, game_state, best_target)
            self.has_attacked = True

    def get_best_target(self, hexes_to_check: list['Hex']) -> Optional['Unit']:
        if self.hex is None:
            return None

        type_scores = {
            'military': 1,
            'support': 2,
        }

        best_target = None
        best_target_distance = 10
        best_target_type_score = 10
        best_target_strength = 10000

        closest_target = self.get_closest_target()
        if closest_target is None:
            closest_target = self.hex

        for hex in hexes_to_check:
            if hex.visibility_by_civ.get(self.civ.id):
                for unit in hex.units:
                    if unit.civ.id != self.civ.id:
                        distance = closest_target.distance_to(hex)
                        if distance < best_target_distance:
                            best_target = unit
                            best_target_distance = distance
                            best_target_type_score = type_scores[unit.template.type]
                            best_target_strength = unit.strength
                        elif distance == best_target_distance and type_scores[unit.template.type] < best_target_type_score:
                            best_target = unit
                            best_target_distance = distance
                            best_target_type_score = type_scores[unit.template.type]
                            best_target_strength = unit.strength
                        elif distance == best_target_distance and type_scores[unit.template.type] == best_target_type_score and unit.strength < best_target_strength:
                            best_target = unit
                            best_target_distance = distance
                            best_target_type_score = type_scores[unit.template.type]
                            best_target_strength = unit.strength

        return best_target

    def get_damage_to_deal_from_effective_strengths(self, effective_strength: float, target_effective_strength: float) -> int:
        ratio_of_strengths = effective_strength / target_effective_strength

        # This is a very scientific formula
        return int(round(40 ** sqrt(ratio_of_strengths)))

    def compute_bonus_strength(self, game_state: 'GameState', enemy: 'Unit') -> int:
        bonus_strength = 0

        if self.has_ability('BonusNextTo') and self.hex is not None:
            unit_type = self.numbers_of_ability('BonusNextTo')[0]
            
            for neighboring_hex in self.hex.get_neighbors(game_state.hexes):
                for unit in neighboring_hex.units:
                    if unit.template.has_tag(unit_type):
                        bonus_strength += self.numbers_of_ability('BonusNextTo')[1]
                        break

        if self.has_ability('BonusAgainst'):
            unit_type = self.numbers_of_ability('BonusAgainst')[0]
            if enemy.template.has_tag(unit_type):
                bonus_strength += self.numbers_of_ability('BonusAgainst')[1]

        return bonus_strength

    def punch(self, game_state: 'GameState', target: 'Unit', damage_reduction_factor: float = 1.0) -> None:
        self.effective_strength = (self.strength + self.compute_bonus_strength(game_state, target)) * damage_reduction_factor * (0.5 + 0.5 * (self.health / 100))
        target.effective_strength = target.strength + target.compute_bonus_strength(game_state, self)

        target.health = max(0, target.health - self.get_damage_to_deal_from_effective_strengths(self.effective_strength, target.effective_strength))

        if target.health == 0:
            target.die(game_state, self)

            if (game_player := self.civ.game_player) is not None:
                game_player.score += UNIT_KILL_REWARD
                game_player.score_from_killing_units += UNIT_KILL_REWARD

                if self.civ.has_ability('ExtraVpsPerUnitKilled'):
                    game_player.score += self.civ.numbers_of_ability('ExtraVpsPerUnitKilled')[0]
                    game_player.score_from_abilities += self.civ.numbers_of_ability('ExtraVpsPerUnitKilled')[0]


    def fight(self, sess, game_state: 'GameState', target: 'Unit') -> None:
        if self.hex is None or target.hex is None:
            return

        self_hex_coords = self.hex.coords
        target_hex_coords = target.hex.coords

        self_hex = self.hex
        target_hex = target.hex

        self.punch(game_state, target)

        if self.has_ability('Splash'):
            for neighboring_hex in target_hex.get_neighbors(game_state.hexes):
                for unit in neighboring_hex.units:
                    if unit.civ.id != self.civ.id:
                        self.punch(game_state, unit, self.numbers_of_ability('Splash')[0])

        if self.template.has_tag('ranged'):
            # target.target = self.hex
            pass
        else:
            target.punch(game_state, self)

        game_state.add_animation_frame(sess, {
            "type": "UnitAttack",
            "attack_type": ("melee" if not self.template.has_tag('ranged') else "ranged") 
                            if not self.template.has_tag('gunpowder') and not self.template.has_tag('armored') and not self.template.name == 'Nanoswarm' 
                            else ("gunpowder_melee" if not self.template.has_tag('ranged') else "gunpowder_ranged"),
            "start_coords": self_hex_coords,
            "end_coords": target_hex_coords,
        }, hexes_must_be_visible=[self_hex, target_hex], no_commit=True)

    def die(self, game_state: 'GameState', killer: 'Unit'):
        if self.hex is None:
            return

        my_hex = self.hex

        self.hex.units = [unit for unit in self.hex.units if unit.id != self.id]
        game_state.units = [unit for unit in game_state.units if unit.id != self.id]
        self.hex = None

        if killer.has_ability('ConvertKills'):
            new_unit = Unit(killer.template, killer.civ)
            new_unit.hex = my_hex
            my_hex.units.append(new_unit)
            game_state.units.append(new_unit)

    def calculate_destination_hex(self, game_state):
        assert self.hex is not None  # Not sure how this could possibly happen.
        # Stationary units don't move
        if self.template.movement == 0:
            self.destination = None
            return self.destination

        # Don't leave besieging cities
        if (self.hex.city and self.hex.city.civ.id != self.civ.id) or self.hex.camp:
            self.destination = None
            return self.destination

        neighbors = self.hex.get_neighbors(game_state.hexes)
        # shuffle(neighbors)  Do not duffle so that it's deterministic and you can't change your units plans by placing a bunch of flags over and over till you roll well.
        for neighboring_hex in neighbors:
            # Attack neighboring cities
            if neighboring_hex.camp or (neighboring_hex.city and neighboring_hex.city.civ.id != self.civ.id):
                self.destination = neighboring_hex
                return self.destination
            
            # Attack neighboring friendly cities under seige
            if (neighboring_hex.city and neighboring_hex.city.civ.id == self.civ.id and neighboring_hex.units and neighboring_hex.units[0].civ.id != self.civ.id):
                self.destination = neighboring_hex
                return self.destination
            
            # Don't abandon threatened cities
            # Debatable: should others next to the city help defend?
            if self.hex.city and neighboring_hex.units and neighboring_hex.units[0].civ.id != self.civ.id:
                self.destination =  None
                return self.destination

        # If none of the other things applied, go to nearest flag.
        target = self.get_closest_target()
        self.destination = target
        return self.destination

    def move_one_step(self, game_state: 'GameState', coord_strs: list[str], sensitive: bool = False) -> bool:
        if self.destination is None: return False

        best_hex = None
        best_distance = self.hex.distance_to(self.destination) if not sensitive else self.hex.sensitive_distance_to(self.destination)

        neighbors = self.hex.get_neighbors(game_state.hexes)
        shuffle(neighbors)

        for neighboring_hex in neighbors:
            neighboring_hex_sensitive_distance_to_target = 10000
            neighboring_hex_distance_to_target = 10000
            if sensitive:
                neighboring_hex_sensitive_distance_to_target = neighboring_hex.sensitive_distance_to(self.destination)

                is_better_distance = neighboring_hex_sensitive_distance_to_target < best_distance
            else:
                neighboring_hex_distance_to_target = neighboring_hex.distance_to(self.destination)
                is_better_distance = neighboring_hex_distance_to_target < best_distance

            if is_better_distance and not neighboring_hex.is_occupied(self.template.type, self.civ):
                best_hex = neighboring_hex
                best_distance = neighboring_hex_sensitive_distance_to_target if sensitive else neighboring_hex_distance_to_target
        if best_hex is not None:
            self.take_one_step_to_hex(best_hex)
            coord_strs.append(best_hex.coords)
            return True
        return False

    def take_one_step_to_hex(self, hex: 'Hex') -> None:
        if self.hex is not None:
            self.hex.remove_unit(self)
        self.hex = hex
        hex.units.append(self)

    def update_civ_by_id(self, civs_by_id: dict[str, Civ]) -> None:
        self.civ = civs_by_id[self.civ.id]

    def update_nearby_hexes_friendly_foundability(self) -> None:
        if self.hex is None:
            return
        self.hex.is_foundable_by_civ[self.civ.id] = True

    def update_nearby_hexes_hostile_foundability(self, hexes: dict[str, 'Hex']) -> None:
        if self.hex is None:
            return
        
        for hex in self.hex.get_neighbors(hexes):
            for key in hex.is_foundable_by_civ:
                if key != self.civ.id:
                    hex.is_foundable_by_civ[key] = False

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.template.name,
            "health": self.health,
            "civ": self.civ.to_json(),
            "has_moved": self.has_moved,
            "coords": self.hex.coords if self.hex is not None else None,
            "strength": self.strength,
            "template": self.template.to_json(),
            "has_attacked": self.has_attacked,
            "closest_target": self.destination.coords if self.destination is not None else None,  # TODO make this respect priority of attacks, defends.
        }
    
    @staticmethod
    def from_json(json: dict,) -> "Unit":
        unit = Unit(
            template=UnitTemplate.from_json(UNITS[json["name"]]),
            civ=Civ.from_json(json["civ"]),
        )
        unit.id = json["id"]
        unit.health = json["health"]
        unit.has_moved = json["has_moved"]
        unit.strength = json["strength"]
        unit.has_attacked = json["has_attacked"]

        return unit