from math import sqrt, ceil
from random import random, shuffle
from typing import TYPE_CHECKING, Generator, Optional
from civ import Civ
from settings import UNIT_KILL_REWARD
from unit_template import UnitTemplate, UnitTag
from unit_templates_list import UNITS
from utils import generate_unique_id

if TYPE_CHECKING:
    from game_state import GameState
    from hex import Hex


class Unit:
    def __init__(self, template: UnitTemplate, civ: Civ) -> None:
        # civ actually can be None very briefly before GameState.from_json() is done, 
        # but I don't want to tell the type-checker so we don't have to put a million asserts everywhere

        self.id = generate_unique_id()
        self.template = template
        self.health = 100
        self.civ = civ
        self.civ_id: str = civ.id if civ else None  # type: ignore
        self.has_moved = False
        self.hex: Optional['Hex'] = None
        self.strength = self.template.strength
        self.attacks_used = 0
        self.destination = None

    def num_attacks(self) -> int:
        num_units = self.get_stack_size()
        if self.has_ability('MultipleAttack'):
            return num_units * self.numbers_of_ability('MultipleAttack')[0]
        return num_units

    @property
    def done_attacking(self):
        return self.attacks_used >= self.num_attacks()

    def __repr__(self):
        return f"<Unit {self.civ.moniker()} {self.template.name} @ {self.hex.coords if self.hex is not None else None}"

    def midturn_update(self, game_state):
        self.calculate_destination_hex(game_state)

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

    def get_stack_size(self) -> int:
        return int(ceil(self.health / 100))

    def update_nearby_hexes_visibility(self, game_state: 'GameState', short_sighted: bool = False) -> None:
        if self.hex is None:
            return
        if short_sighted:
            neighbors = self.hex.get_neighbors(game_state.hexes)
        else:
            neighbors = self.hex.get_hexes_within_range(game_state.hexes, 2)

        for nearby_hex in neighbors:
            nearby_hex.visibility_by_civ[self.civ.id] = True

    def move(self, sess, game_state: 'GameState', sensitive: bool = False) -> None:
        if self.has_moved or self.hex is None:
            return
        stack_count_not_acted: int = max(0, self.get_stack_size() - self.attacks_used)
        if stack_count_not_acted == 0:
            return

        starting_hex = self.hex
        coord_strs = [starting_hex.coords]
        for _ in range(self.template.movement):
            if self.move_one_step(game_state, coord_strs, sensitive=sensitive):
                self.has_moved = True
                sensitive = True

        # At this point we might have moved with whole stack
        # When we should have left some behind
        if self.has_moved and self.attacks_used > 0:
            split_unit: Unit = Unit(self.template, self.civ)

            split_unit.health = self.attacks_used * 100
            self.health -= split_unit.health

            split_unit.attacks_used = self.attacks_used
            self.attacks_used = 0

            split_unit.hex = starting_hex
            starting_hex.units.append(split_unit)
            game_state.units.append(split_unit)

        if self.has_moved:
            new_hex = self.hex

            self.update_nearby_hexes_visibility(game_state)

            game_state.add_animation_frame(sess, {
                "type": "UnitMovement",
                "coords": coord_strs,
            }, hexes_must_be_visible=[starting_hex, new_hex], no_commit=True)

    def merge_into_neighboring_unit(self, sess, game_state: 'GameState', always_merge_if_possible: bool = False) -> bool:
        if self.hex is None:
            return False

        closest_target = self.get_closest_target()
        if closest_target is None:
            closest_target = self.hex

        coord_strs = [self.hex.coords]
        starting_hex = self.hex

        for neighboring_hex in self.hex.get_neighbors(game_state.hexes):
            if neighboring_hex.sensitive_distance_to(closest_target) < self.hex.sensitive_distance_to(closest_target) or always_merge_if_possible:
                for unit in neighboring_hex.units:
                    if unit.civ.id == self.civ.id and unit.template.name == self.template.name:
                        unit.health += self.health
                        self.remove_from_game(game_state)

                        self.update_nearby_hexes_visibility(game_state)
                        coord_strs.append(neighboring_hex.coords)

                        if sess is not None:
                            game_state.add_animation_frame(sess, {
                                "type": "UnitMovement",
                                "coords": coord_strs,
                            }, hexes_must_be_visible=[starting_hex, neighboring_hex], no_commit=True)

                        return True
                    
        return False

    def friendly_neighboring_unit_count(self, game_state: 'GameState') -> int:
        if self.hex is None:
            return 0
        
        units_in_neighboring_hexes: list['Unit'] = []
        for neighboring_hex in self.hex.get_neighbors(game_state.hexes):
            units_in_neighboring_hexes.extend(neighboring_hex.units)

        return len([unit for unit in units_in_neighboring_hexes if unit.civ.id == self.civ.id])

    def attack(self, sess, game_state: 'GameState') -> None:
        if self.hex is None or self.done_attacking:
            return

        while not self.done_attacking:
            if self.hex is None:
                return

            if self.template.range <= 3:
                hexes_to_check = self.hex.get_hexes_within_range(game_state.hexes, self.template.range)
            else:
                print(f"Unit {self} has long range ({self.template.range}), this is computationally expensive!")
                hexes_to_check = self.hex.get_hexes_within_range_expensive(game_state.hexes, self.template.range)

            best_target = self.get_best_target(hexes_to_check)

            if best_target is None:
                break

            else:
                self.fight(sess, game_state, best_target)
                self.attacks_used += 1

    def target_score(self, target: 'Unit') -> tuple[float, float, float, float, float]:
        """
        Ranking function for which target to attack
        """
        assert target.hex is not None and self.hex is not None

        type_scores = {
            'military': 2,
            'support': 1,
        }
        seiging_my_city: bool = (target.hex.city is not None and target.hex.city.civ == self.civ and len(target.hex.units) > 0 and target.hex.units[0].civ != self.civ)
        closest_target: Hex = self.destination or self.hex
        is_vandetta_civ: bool = target.civ.id == self.civ.vandetta_civ_id
        return seiging_my_city, is_vandetta_civ, -closest_target.distance_to(target.hex), type_scores[target.template.type], -target.strength

    def valid_attack(self, target: 'Unit') -> bool:
        visible: bool = target.hex is not None and target.hex.visible_to_civ(self.civ)
        return visible and target.civ != self.civ

    def get_best_target(self, hexes_to_check: Generator['Hex', None, None]) -> Optional['Unit']:
        if self.hex is None:
            return None

        units: list[Unit] = [unit for hex in hexes_to_check for unit in hex.units if self.valid_attack(unit)]
        if len(units) > 0:
            return max(units, key=self.target_score)
        else:
            return None

    def get_damage_to_deal_from_effective_strengths(self, effective_strength: float, target_effective_strength: float) -> int:
        ratio_of_strengths = effective_strength / target_effective_strength

        # This is a very scientific formula
        return int(round(40 ** sqrt(ratio_of_strengths)))

    def compute_bonus_strength(self, game_state: 'GameState', enemy: 'Unit') -> int:
        bonus_strength = 0

        if self.has_ability('BonusNextTo') and self.hex is not None:
            unit_type: str = self.numbers_of_ability('BonusNextTo')[0]
            for neighboring_hex in self.hex.get_neighbors(game_state.hexes):
                for unit in neighboring_hex.units:
                    if unit.template.has_tag_by_name(unit_type):
                        bonus_strength += self.numbers_of_ability('BonusNextTo')[1]
                        break

        if self.has_ability('BonusAgainst'):
            unit_type: str = self.numbers_of_ability('BonusAgainst')[0]
            if enemy.template.has_tag_by_name(unit_type):
                bonus_strength += self.numbers_of_ability('BonusAgainst')[1]

        return bonus_strength

    def punch(self, game_state: 'GameState', target: 'Unit', damage_reduction_factor: float = 1.0) -> None:
        self.effective_strength = (self.strength + self.compute_bonus_strength(game_state, target)) * damage_reduction_factor * (0.5 + 0.5 * (min(self.health, 100) / 100))
        target.effective_strength = target.strength + target.compute_bonus_strength(game_state, self)
        target.take_damage(self.get_damage_to_deal_from_effective_strengths(self.effective_strength, target.effective_strength), from_civ=self.civ, game_state=game_state)

    def take_damage(self, amount: float, game_state: 'GameState', from_civ: Civ | None, from_unit: 'Unit | None' = None):
        original_stack_size = self.get_stack_size()
        self.health = max(0, self.health - amount)
        final_stack_size = self.get_stack_size()

        if self.health == 0:
            self.die(game_state, from_unit)

        if from_civ is not None:
            for _ in range(original_stack_size - final_stack_size):
                from_civ.gain_vps(UNIT_KILL_REWARD, f"Unit Kill ({UNIT_KILL_REWARD}/unit)")

                if from_civ.has_ability('ExtraVpsPerUnitKilled'):
                    from_civ.gain_vps(from_civ.numbers_of_ability('ExtraVpsPerUnitKilled')[0], from_civ.template.name)

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
                    if unit.civ != self.civ:
                        self.punch(game_state, unit, self.numbers_of_ability('Splash')[0])

        if self.template.has_tag(UnitTag.RANGED):
            # target.target = self.hex
            pass
        else:
            target.punch(game_state, self)

        game_state.add_animation_frame(sess, {
            "type": "UnitAttack",
            "attack_type": ("melee" if not self.template.has_tag(UnitTag.RANGED) else "ranged") 
                            if not self.template.has_tag(UnitTag.GUNPOWDER) and not self.template.has_tag(UnitTag.ARMORED) and not self.template == UNITS.NANOSWARM 
                            else ("gunpowder_melee" if not self.template.has_tag(UnitTag.RANGED) else "gunpowder_ranged"),
            "start_coords": self_hex_coords,
            "end_coords": target_hex_coords,
        }, hexes_must_be_visible=[self_hex, target_hex], no_commit=True)

        if self.has_ability('Missile'):
            print(f"Missile depleting")
            print(self.health)
            self.take_damage(100, game_state, from_civ=None)
            print(self.health)
            # Only one attack from a stack of missiles per turn
            self.attacks_used += 1000
            print(self.health, self.attacks_used)

    def remove_from_game(self, game_state: 'GameState') -> None:
        if self.hex is None:
            return        
        self.hex.units = [unit for unit in self.hex.units if unit.id != self.id]
        game_state.units = [unit for unit in game_state.units if unit.id != self.id]
        self.hex = None        

    def die(self, game_state: 'GameState', killer: 'Unit | None'):
        if self.hex is None:
            return

        my_hex = self.hex

        self.remove_from_game(game_state)

        if killer is not None and killer.has_ability('ConvertKills'):
            new_unit = Unit(killer.template, killer.civ)
            new_unit.hex = my_hex
            my_hex.units.append(new_unit)
            game_state.units.append(new_unit)

    def currently_sieging(self):
        if not self.hex:
            return False
        return (self.hex.city and self.hex.city.civ != self.civ) or (self.hex.camp and self.hex.camp.civ != self.civ)

    def calculate_destination_hex(self, game_state):
        assert self.hex is not None  # Not sure how this could possibly happen.
        # Stationary units don't move
        if self.template.movement == 0:
            self.destination = None
            return self.destination

        # Don't leave besieging cities
        if self.currently_sieging():
            self.destination = None
            return self.destination

        neighbors = self.hex.get_neighbors(game_state.hexes)
        # shuffle(neighbors)  Do not shuffle so that it's deterministic and you can't change your units plans by placing a bunch of flags over and over till you roll well.
        for neighboring_hex in neighbors:
            # Don't abandon threatened cities
            if self.hex.city and neighboring_hex.units and neighboring_hex.units[0].civ.id != self.civ.id:
                self.destination =  None
                return self.destination

            # Move into adjacent friendly empty threatened cities
            if neighboring_hex.city is not None and neighboring_hex.is_threatened_city(game_state) and neighboring_hex.city.civ.id == self.civ.id and len(neighboring_hex.units) == 0:
                self.destination = neighboring_hex
                return self.destination

            # Attack neighboring friendly cities under seige
            if (neighboring_hex.city and neighboring_hex.city.civ.id == self.civ.id and neighboring_hex.units and neighboring_hex.units[0].civ.id != self.civ.id):
                self.destination = neighboring_hex
                return self.destination

            # Attack neighboring empty cities
            if neighboring_hex.city and neighboring_hex.city.civ.id != self.civ.id and len(neighboring_hex.units) == 0:
                self.destination = neighboring_hex
                return self.destination

            # Attack neighboring camps
            if neighboring_hex.camp and neighboring_hex.camp.civ != self.civ and not (len(neighboring_hex.units) > 0 and neighboring_hex.units[0].civ.id == self.civ.id):
                self.destination = neighboring_hex
                return self.destination

        # If none of the other things applied, go to nearest flag.
        target = self.get_closest_target()
        self.destination = target
        return self.destination

    def move_one_step(self, game_state: 'GameState', coord_strs: list[str], sensitive: bool = False) -> bool:
        # Potentially change your mind at the last minute
        self.calculate_destination_hex(game_state)

        if self.destination is None: return False

        assert self.hex
        best_hex = None
        best_distance = self.hex.distance_to(self.destination) if not sensitive else self.hex.sensitive_distance_to(self.destination)

        neighbors = list(self.hex.get_neighbors(game_state.hexes))
        shuffle(neighbors)

        for neighboring_hex in neighbors:
            neighboring_hex_sensitive_distance_to_target = 10000
            neighboring_hex_distance_to_target = 10000
            if sensitive:
                neighboring_hex_sensitive_distance_to_target = neighboring_hex.sensitive_distance_to(self.destination)
                # IF moving sensitive, use <= to prefer moving over staying still.
                is_better_distance = neighboring_hex_sensitive_distance_to_target <= best_distance
            else:
                neighboring_hex_distance_to_target = neighboring_hex.distance_to(self.destination)
                # If it's the first try at moving, use < to prefer staying still (maybe a better spot will open up)
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

    def turn_end(self, game_state: 'GameState') -> None:
        self.has_moved = False
        self.attacks_used = 0

        if self.has_ability('HealAllies') and self.hex is not None:
            for neighbor in self.hex.get_neighbors(game_state.hexes):
                for unit in neighbor.units:
                    if unit.civ == self.civ and not unit.has_ability('HealAllies'):
                        unit.health = ceil(unit.health / 100) * 100

        if self.template.has_tag(UnitTag.WONDROUS):
            self.take_damage(5, game_state, from_civ=None)

    def update_civ_by_id(self, civs_by_id: dict[str, Civ]) -> None:
        self.civ = civs_by_id[self.civ_id]

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
            "civ_id": self.civ.id,
            "has_moved": self.has_moved,
            "coords": self.hex.coords if self.hex is not None else None,
            "strength": self.strength,
            "template": self.template.to_json(),
            "attacks_used": self.attacks_used,
            "done_attacking": self.done_attacking,
            "stack_size": self.get_stack_size(),
            "closest_target": self.destination.coords if self.destination is not None else None,
        }
    
    @staticmethod
    def from_json(json: dict,) -> "Unit":
        unit = Unit(
            template=UNITS.by_name(json["name"]),
            civ=None,  # type: ignore
        )
        unit.id = json["id"]
        unit.health = json["health"]
        unit.has_moved = json["has_moved"]
        unit.strength = json["strength"]
        unit.attacks_used = json["attacks_used"]
        unit.civ_id = json["civ_id"]

        return unit
