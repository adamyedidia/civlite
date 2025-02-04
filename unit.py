from math import ceil
import random
from typing import TYPE_CHECKING, Generator, Optional
from civ_templates_list import CIVS
from map_object import MapObject
from tenet_template_list import TENETS
from wonder_templates_list import WONDERS
from settings import UNIT_KILL_REWARD, DAMAGE_DOUBLE_EXPONENT, DAMAGE_EQUAL_STR
from unit_template import UnitTemplate, UnitTag
from unit_templates_list import UNITS
from utils import generate_unique_id
from logging_setup import logger
import score_strings


if TYPE_CHECKING:
    from game_state import GameState
    from hex import Hex
    from civ import Civ


class Unit(MapObject):
    def __init__(self, template: UnitTemplate, civ: 'Civ | None' = None, hex: 'Hex | None' = None) -> None:
        super().__init__(civ, hex)
        self.id = generate_unique_id("UNIT")
        self.template = template
        self.health = 100
        self.has_moved = False
        self.strength = self.template.strength
        self.attacks_used = 0
        self.destination: list['Hex'] = []

    @property
    def dead(self):
        return self.health <= 0

    def num_attacks(self) -> int:
        num_units = self.get_stack_size()
        if self.has_ability('MultipleAttack'):
            return num_units * self.numbers_of_ability('MultipleAttack')[0]
        return num_units

    @property
    def done_attacking(self):
        return self.attacks_used >= self.num_attacks()

    def __repr__(self):
        return f"<Unit {self.civ.moniker()} {self.template.name} @ {self._hex.coords if self._hex is not None else None}"

    def midturn_update(self, game_state):
        self.calculate_destination_hex(game_state)

    def has_ability(self, ability_name: str) -> bool:
        return any([ability.name == ability_name for ability in self.template.abilities])

    def numbers_of_ability(self, ability_name: str) -> list:
        return [ability.numbers for ability in self.template.abilities if ability.name == ability_name][0]

    def get_stack_size(self) -> int:
        return int(ceil(self.health / 100))

    def move(self, sess, game_state: 'GameState', sensitive: bool = False) -> None:
        if self.has_moved:
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
            split_unit: Unit = Unit(self.template, civ=self.civ, hex=starting_hex)

            split_unit.health = self.attacks_used * 100
            split_unit.strength = self.strength
            self.health -= split_unit.health

            split_unit.attacks_used = self.attacks_used
            self.attacks_used = 0

            assert not starting_hex.is_occupied(self.civ, allow_enemy_city=False, allow_allied_unit=False, allow_enemy_unit=False)
            starting_hex.units.append(split_unit)
            game_state.units.append(split_unit)

        if self.has_moved:
            new_hex = self.hex

            self.update_nearby_hexes_visibility(game_state)

            game_state.add_animation_frame(sess, {
                "type": "UnitMovement",
                "movement_type": "armored" if self.template.name in ["Tank", "Rocket Launcher"] else "mounted" if self.template.has_tag(UnitTag.MOUNTED) else "infantry",
                "coords": coord_strs,
            }, hexes_must_be_visible=[starting_hex, new_hex], no_commit=True)

    def merge_into_neighboring_unit(self, sess, game_state: 'GameState', always_merge_if_possible: bool = False) -> bool:
        closest_targets = self.get_closest_targets()
        if len(closest_targets) == 0:
            closest_targets = [self.hex]

        coord_strs = [self.hex.coords]
        starting_hex = self.hex

        for neighboring_hex in self.hex.get_neighbors(game_state.hexes):
            if neighboring_hex.distance_to_list(closest_targets, sensitive=True) < self.hex.distance_to_list(closest_targets, sensitive=True) or always_merge_if_possible:
                for unit in neighboring_hex.units:
                    if unit.civ.id == self.civ.id and unit.template.name == self.template.name and unit.strength == self.strength:
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
        units_in_neighboring_hexes: list['Unit'] = []
        for neighboring_hex in self.hex.get_neighbors(game_state.hexes):
            units_in_neighboring_hexes.extend(neighboring_hex.units)

        return len([unit for unit in units_in_neighboring_hexes if unit.civ.id == self.civ.id])

    def attack(self, sess, game_state: 'GameState') -> None:
        while not self.done_attacking:
            if self.hex is None:
                return

            if self.template.range <= 3:
                hexes_to_check = self.hex.get_hexes_within_range(game_state.hexes, self.template.range)
            else:
                logger.info(f"Unit {self} has long range ({self.template.range}), this is computationally expensive!")
                hexes_to_check = self.hex.get_hexes_within_range_expensive(game_state.hexes, self.template.range)

            best_target = self.get_best_target(hexes_to_check)

            if best_target is None:
                break

            else:
                self.fight(sess, game_state, best_target)
                self.attacks_used += 1

    def target_score(self, target: 'Unit') -> tuple[float, float, float, float]:
        """
        Ranking function for which target to attack
        """
        seiging_my_city: bool = (target.hex.city is not None and target.hex.city.civ == self.civ and len(target.hex.units) > 0 and target.hex.units[0].civ != self.civ)
        targets: list['Hex'] = self.destination if len(self.destination) > 0 else [self.hex]
        distance_to_target = min(target.hex.distance_to(t) for t in targets)
        is_vandetta_civ: bool = target.civ.id == self.civ.vandetta_civ_id
        return seiging_my_city, is_vandetta_civ, -distance_to_target, -target.strength

    def valid_attack(self, target: 'Unit') -> bool:
        visible: bool = target.hex.visible_to_civ(self.civ)
        return visible and target.civ != self.civ

    def get_best_target(self, hexes_to_check: Generator['Hex', None, None]) -> Optional['Unit']:
        units: list[Unit] = [unit for hex in hexes_to_check for unit in hex.units if self.valid_attack(unit)]
        if len(units) > 0:
            return max(units, key=self.target_score)
        else:
            return None

    @staticmethod
    def get_damage_to_deal_from_effective_strengths(effective_strength: float, target_effective_strength: float) -> int:
        ratio_of_strengths = effective_strength / target_effective_strength

        # This is a very scientific formula
        return int(round(DAMAGE_EQUAL_STR ** (ratio_of_strengths ** DAMAGE_DOUBLE_EXPONENT)))

    def _compute_bonus_strength(self, game_state: 'GameState', enemy: 'Unit', battle_location: 'Hex',  support_hexes: set[tuple['Hex', 'Hex']] = set()) -> float:
        bonuses = 0

        if self.has_ability('BonusNextTo'):
            unit_tag: str = self.numbers_of_ability('BonusNextTo')[0]
            valid_support_hexes = [hex
                                   for hex in self.hex.get_neighbors(game_state.hexes)
                                   if any(unit.civ == self.civ and unit.template.has_tag_by_name(unit_tag) for unit in hex.units)
                                   ]
            if len(valid_support_hexes) > 0:
                bonuses += 1
                # Pick a random one of the support hexes to display in the UI
                # Ensure it's secretly deterministic so that if the same unit gets support in the attack and again in the coutnerattack
                # It doesn't draw two different lines.
                random_support_hex = valid_support_hexes[(self.hex.q * 17 + self.hex.r * 13 + self.hex.s * 11) % len(valid_support_hexes)]
                support_hexes.add((self.hex, random_support_hex))

        if self.has_ability('BonusAgainst'):
            unit_type: str = self.numbers_of_ability('BonusAgainst')[0]
            if enemy.template.has_tag_by_name(unit_type):
                bonuses += 1
        if self.has_ability('DoubleBonusAgainst'):
            unit_type: str = self.numbers_of_ability('DoubleBonusAgainst')[0]
            if enemy.template.has_tag_by_name(unit_type):
                bonuses += 2

        # Each bonus gives 50% of base strength
        bonus_strength = self.strength * (0.5 * bonuses)

        af_bonus = 0
        af_city = None
        for city in self.civ.get_my_cities(game_state):
            assert battle_location is not None
            for ability, _ in city.passive_building_abilities_of_name('Airforce'):
                if city.hex.distance_to(battle_location) <= ability.numbers[1]:
                    af_bonus = max(af_bonus, ability.numbers[0])
                    af_city = city

        if af_city is not None:
            support_hexes.add((af_city.hex, self.hex))

        return bonus_strength + af_bonus

    def punch(self, game_state: 'GameState', target: 'Unit', battle_location: 'Hex', damage_reduction_factor: float = 1.0, support_hexes: set[tuple['Hex', 'Hex']] = set()) -> None:
        self.effective_strength = (self.strength + self._compute_bonus_strength(game_state, target, battle_location, support_hexes)) * damage_reduction_factor * (0.5 + 0.5 * (min(self.health, 100) / 100))
        target.effective_strength = target.strength + target._compute_bonus_strength(game_state, self, battle_location, support_hexes)
        target.take_damage(self.get_damage_to_deal_from_effective_strengths(self.effective_strength, target.effective_strength), from_civ=self.civ, from_unit=self, game_state=game_state)

    def take_damage(self, amount: float, game_state: 'GameState', from_civ: 'Civ | None', from_unit: 'Unit | None' = None):
        original_stack_size = self.get_stack_size()
        self.health = max(0, self.health - amount)
        final_stack_size = self.get_stack_size()

        if self.dead:
            self.remove_from_game(game_state)

        if from_civ is not None:
            for _ in range(original_stack_size - final_stack_size):
                from_civ.gain_vps(UNIT_KILL_REWARD, score_strings.UNIT_KILL)

                if from_civ is not None and from_civ.has_tenet(TENETS.HONOR) and self.civ.template == CIVS.BARBARIAN:
                    from_civ.gain_vps(UNIT_KILL_REWARD, f"Honor")

                if from_civ.has_ability('ExtraVpsPerUnitKilled') and from_unit is not None:
                    tag, amount = from_civ.numbers_of_ability('ExtraVpsPerUnitKilled')
                    if tag is None or from_unit.template.has_tag_by_name(tag):
                        from_civ.gain_vps(amount, from_civ.template.name)

                if from_civ.game_player is None and WONDERS.UNITED_NATIONS in game_state.built_wonders and random.random() < 0.50:
                    for _, civ_id in game_state.built_wonders[WONDERS.UNITED_NATIONS].infos:
                        game_state.civs_by_id[civ_id].gain_vps(UNIT_KILL_REWARD, f"United Nations")

                if from_unit is not None and from_unit.has_ability('ConvertKills'):
                    from_unit.health += 100

                for ability, _ in from_civ.passive_building_abilities_of_name('CityPowerPerKill', game_state):
                    from_civ.city_power += ability.numbers[0]

                if from_unit and (from_civ_a5_tenet := from_civ.tenet_at_level(5)) and from_civ_a5_tenet.a5_unit_types and any(from_unit.template.has_tag(tag) for tag in from_civ_a5_tenet.a5_unit_types):
                    from_civ.city_power += 10

                if from_civ.game_player is not None \
                    and from_civ.has_tenet(TENETS.HOLY_GRAIL) \
                    and (holy_city := game_state.cities_by_id.get(from_civ.game_player.tenets[TENETS.HOLY_GRAIL]["holy_city_id"])) is not None \
                    and holy_city.civ == self.civ:
                    from_civ.game_player.increment_tenet_progress(TENETS.HOLY_GRAIL, game_state)

    def fight(self, sess, game_state: 'GameState', target: 'Unit') -> None:
        self_hex_coords = self.hex.coords
        target_hex_coords = target.hex.coords
        support_hexes: set[tuple['Hex', 'Hex']] = set()  # list of hexes that supported the battle for anmation. Updated a side effect of punch

        self_hex = self.hex
        target_hex = target.hex

        self.punch(game_state, target, battle_location=target_hex, support_hexes=support_hexes)

        if self.has_ability('Splash'):
            for neighboring_hex in target_hex.get_neighbors(game_state.hexes):
                for unit in neighboring_hex.units:
                    if unit.civ != self.civ:
                        self.punch(game_state, unit, damage_reduction_factor=self.numbers_of_ability('Splash')[0], battle_location=target_hex, support_hexes=support_hexes)

        if self.template.has_tag(UnitTag.RANGED):
            pass
        else:
            target.punch(game_state, self, battle_location=target_hex, support_hexes=support_hexes)

        game_state.add_animation_frame(sess, {
            "type": "UnitAttack",
            "attack_type": self.template.attack_type(),
            "start_coords": self_hex_coords,
            "end_coords": target_hex_coords,
            "support_coords": [(hex1.coords, hex2.coords) for hex1, hex2 in support_hexes],
            "attacker_corpse": {
                "coords": self_hex_coords,
                "unit_name": self.template.name,
                "unit_civ_id": self.civ.id,
            } if self.dead else None,
            "defender_corpse": {
                "coords": target_hex_coords,
                "unit_name": target.template.name,
                "unit_civ_id": target.civ.id,
            } if target.dead else None,
        }, hexes_must_be_visible=[self_hex, target_hex], no_commit=True)

        if self.has_ability('Missile'):
            self.take_damage(100, game_state, from_civ=None)
            # Only one attack from a stack of missiles per turn
            self.attacks_used += 1000

    def remove_from_game(self, game_state: 'GameState') -> None:       
        self.hex.units = [unit for unit in self.hex.units if unit.id != self.id]
        game_state.units = [unit for unit in game_state.units if unit.id != self.id]

    def currently_sieging(self):
        return (self.hex.city and self.hex.city.civ != self.civ) or (self.hex.camp and self.hex.camp.civ != self.civ)

    def calculate_destination_hex(self, game_state):
        self.destination = self._calculate_destination(game_state)
        return self.destination

    def _calculate_destination(self, game_state) -> list['Hex']:
        # Stationary units don't move
        if self.template.movement == 0:
            return [self.hex]

        # Don't leave besieging cities
        if self.currently_sieging():
            return [self.hex]

        # Don't abandon threatened cities
        if (self.hex.city or self.hex.camp) and self.hex.is_threatened(game_state, self.civ):
            return [self.hex]

        neighbors = list(self.hex.get_neighbors(game_state.hexes))

        # Move to adjacent flags
        adjacent_flags = [hex for hex in neighbors if hex in self.civ.targets]
        if len(adjacent_flags) > 0:
            return adjacent_flags

        # Move into adjacent friendly empty threatened cities
        adjacent_threatened_cities = [neighboring_hex for neighboring_hex in neighbors if neighboring_hex.city and neighboring_hex.is_threatened(game_state, self.civ) and neighboring_hex.city.civ == self.civ and len(neighboring_hex.units) == 0]
        if len(adjacent_threatened_cities) > 0:
            return adjacent_threatened_cities

        # ... and camps
        adjacent_threatened_camps = [neighboring_hex for neighboring_hex in neighbors if neighboring_hex.camp and neighboring_hex.is_threatened(game_state, self.civ) and neighboring_hex.camp.civ == self.civ and len(neighboring_hex.units) == 0]
        if len(adjacent_threatened_camps) > 0:
            return adjacent_threatened_camps

        # Attack neighboring friendly cities under seige
        adjacent_friendly_cities = [neighboring_hex for neighboring_hex in neighbors if neighboring_hex.city and neighboring_hex.city.civ == self.civ and neighboring_hex.units and neighboring_hex.units[0].civ != self.civ]
        if len(adjacent_friendly_cities) > 0:
            return adjacent_friendly_cities

        # ... and camps
        adjacent_friendly_camps = [neighboring_hex for neighboring_hex in neighbors if neighboring_hex.camp and neighboring_hex.camp.civ == self.civ and neighboring_hex.units and neighboring_hex.units[0].civ != self.civ]
        if len(adjacent_friendly_camps) > 0:
            return adjacent_friendly_camps

        # Attack neighboring empty cities
        adjacent_enemy_cities = [neighboring_hex for neighboring_hex in neighbors if neighboring_hex.city and neighboring_hex.city.civ != self.civ and len(neighboring_hex.units) == 0]
        if len(adjacent_enemy_cities) > 0:
            return adjacent_enemy_cities
            
        # ... and camps
        adjacent_enemy_camps = [neighboring_hex for neighboring_hex in neighbors if neighboring_hex.camp and neighboring_hex.camp.civ != self.civ and len(neighboring_hex.units) == 0]
        if len(adjacent_enemy_camps) > 0:
            return adjacent_enemy_camps

        # Attack neighboring camps
        adjacent_enemy_camps = [neighboring_hex for neighboring_hex in neighbors if neighboring_hex.camp and neighboring_hex.camp.civ != self.civ and not (len(neighboring_hex.units) > 0 and neighboring_hex.units[0].civ == self.civ)]
        if len(adjacent_enemy_camps) > 0:
            return adjacent_enemy_camps

        # If none of the other things applied, go to nearest flag.
        return self.get_closest_targets()

    def move_one_step(self, game_state: 'GameState', coord_strs: list[str], sensitive: bool = False) -> bool:
        # Potentially change your mind at the last minute
        self.calculate_destination_hex(game_state)

        if len(self.destination) == 0: return False
        
        best_hex = None
        best_distance = min(self.hex.distance_to(destination) if not sensitive else self.hex.sensitive_distance_to(destination) for destination in self.destination)

        neighbors = list(self.hex.get_neighbors(game_state.hexes, exclude_ocean=True))
        random.shuffle(neighbors)

        for neighboring_hex in neighbors:
            if neighboring_hex.coords in coord_strs:
                # Don't loop.
                continue
            neighboring_hex_sensitive_distance_to_target = 10000
            neighboring_hex_distance_to_target = 10000
            if sensitive:
                neighboring_hex_sensitive_distance_to_target = min(neighboring_hex.sensitive_distance_to(destination) for destination in self.destination)
                # IF moving sensitive, use <= to prefer moving over staying still.
                is_better_distance = neighboring_hex_sensitive_distance_to_target <= best_distance
            else:
                neighboring_hex_distance_to_target = min(neighboring_hex.distance_to(destination) for destination in self.destination)
                # If it's the first try at moving, use < to prefer staying still (maybe a better spot will open up)
                is_better_distance = neighboring_hex_distance_to_target < best_distance

            if is_better_distance and not neighboring_hex.is_occupied(self.civ, allow_enemy_city=True):
                best_hex = neighboring_hex
                best_distance = neighboring_hex_sensitive_distance_to_target if sensitive else neighboring_hex_distance_to_target
        if best_hex is not None:
            self.take_one_step_to_hex(best_hex, game_state)
            coord_strs.append(best_hex.coords)
            return True
        return False

    def take_one_step_to_hex(self, hex: 'Hex', game_state: 'GameState') -> None:
        assert not hex.is_occupied(self.civ, allow_enemy_city=True)
        self.hex.remove_unit(self)
        self.update_hex(hex)
        hex.append_unit(self, game_state)

    def turn_end(self, game_state: 'GameState') -> None:
        self.has_moved = False
        self.attacks_used = 0

        if self.has_ability('HealAllies'):
            for neighbor in self.hex.get_neighbors(game_state.hexes):
                for unit in neighbor.units:
                    if unit.civ == self.civ and not unit.template.has_tag(UnitTag.WONDROUS):
                        unit.health = ceil(unit.health / 100) * 100

        if self.template.has_tag(UnitTag.WONDROUS):
            self.take_damage(5, game_state, from_civ=None)

    def update_nearby_hexes_friendly_foundability(self) -> None:
        if self.civ.template != CIVS.BARBARIAN:
            self.hex.is_foundable_by_civ[self.civ.id] = True

    def capture(self, sess, game_state: 'GameState') -> None:
        raise ValueError(f"Somehow a unit got sieged and captured. That should only happen to cities and camps. {self.id=} {self.template.name=} {self.hex.coords=}")

    def to_json(self) -> dict:
        return {
            **super().to_json(),
            "id": self.id,
            "name": self.template.name,
            "health": self.health,
            "has_moved": self.has_moved,
            "coords": self.hex.coords,
            "strength": self.strength,
            "template": self.template.to_json(),
            "attacks_used": self.attacks_used,
            "done_attacking": self.done_attacking,
            "stack_size": self.get_stack_size(),
            "closest_target": [destination.coords for destination in self.destination],
        }
    
    @staticmethod
    def from_json(json: dict,) -> "Unit":
        unit = Unit(
            template=UNITS.by_name(json["name"]),
        )
        super(Unit, unit).from_json(json)
        unit.id = json["id"]
        unit.health = json["health"]
        unit.has_moved = json["has_moved"]
        unit.strength = json["strength"]
        unit.attacks_used = json["attacks_used"]

        return unit
