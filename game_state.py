from typing import Any, Optional
from animation_frame import AnimationFrame
from city import City
from civ import Civ
from hex import Hex
from unit import Unit
import random


def get_all_units(hexes: dict[str, Hex]) -> list[Unit]:
    units = []
    for hex in hexes.values():
        units.extend(hex.units)
    return units


def get_all_cities(hexes: dict[str, Hex]) -> list[City]:
    cities = []
    for hex in hexes.values():
        if hex.city:
            cities.append(hex.city)
    return cities


class GameState:
    def __init__(self, game_id: str, hexes: dict[str, Hex]):
        self.hexes = hexes
        self.game_id = game_id
        self.units = get_all_units(hexes)
        self.cities = get_all_cities(hexes)
        self.civs = []
        self.turn_num = 1

    def set_unit_hexes(self) -> None:
        for hex in self.hexes.values():
            for unit in hex.units:
                unit.hex = hex

    def roll_turn(self, sess) -> None:
        units_copy = self.units[:]
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.move(self, sess)
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.move(self, sess, sensitive=True)
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.attack(self, sess)

        cities_copy = self.cities[:]
        random.shuffle(cities_copy)
        for city in cities_copy:
            city.roll_turn(self, sess)

        self.turn_num += 1

    def add_animation_frame_for_civ(self, sess, data: dict[str, Any], civ: Optional[Civ]) -> None:
        highest_existing_frame_num = (
            sess.query(AnimationFrame.frame_num)
            .filter(AnimationFrame.game_id == self.game_id)
            .filter(AnimationFrame.turn_num == self.turn_num)
            .filter(AnimationFrame.player_num == (civ.player_num if civ is not None else None))
            .order_by(AnimationFrame.frame_num.desc())
            .first()
        ) or 0

        frame = AnimationFrame(
            game_id=self.game_id,
            turn_num=self.turn_num,
            frame_num=highest_existing_frame_num + 1,
            player_num=civ.player_num if civ is not None else None,
            data=data,
            game_state=self.to_json(from_civ_perspective=civ),
        )

        sess.add(frame)

    def add_animation_frame(self, sess, data: dict[str, Any], hexes_must_be_visible: Optional[list[Hex]] = None) -> None:
        self.add_animation_frame_for_civ(sess, data, None)
        for civ in self.civs:
            if hexes_must_be_visible is None or any(hex.visibility_by_civ.get(civ.id) for hex in hexes_must_be_visible):
                self.add_animation_frame_for_civ(sess, data, civ)

        sess.commit()
        
    def to_json(self, from_civ_perspective: Optional[Civ] = None) -> dict:
        return {
            "game_id": self.game_id,
            "hexes": {key: hex.to_json(from_civ_perspective=from_civ_perspective) for key, hex in self.hexes.items()},
            "civs": [civ.to_json() for civ in self.civs],
        }
    
    @staticmethod
    def from_json(json: dict) -> "GameState":
        hexes = {key: Hex.from_json(hex_json) for key, hex_json in json["hexes"].items()}
        game_state = GameState(game_id=json["game_id"], hexes=hexes)
        game_state.civs = [Civ.from_json(civ_json) for civ_json in json["civs"]]
        game_state.set_unit_hexes()
        return game_state
