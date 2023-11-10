from typing import Any, Optional
from animation_frame import AnimationFrame
from building_template import BuildingTemplate
from city import City
from civ import Civ
from game_player import GamePlayer
from hex import Hex
from redis_utils import rget_json, rlock, rset_json
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
        self.civs: list[Civ] = []
        self.turn_num = 1
        self.game_players: list[GamePlayer] = []
        self.wonders_built: dict[str, bool] = {}
        self.special_mode: Optional[str] = 'starting_location'

    def set_unit_and_city_hexes(self) -> None:
        for hex in self.hexes.values():
            for unit in hex.units:
                unit.hex = hex
            if hex.city:
                hex.city.hex = hex

    def refresh_visibility_by_civ(self, short_sighted: bool = False) -> None:
        for hex in self.hexes.values():
            hex.visibility_by_civ = {}

        for unit in self.units:
            unit.update_nearby_hexes_visibility(self, short_sighted=short_sighted)

        for city in self.cities:
            city.update_nearby_hexes_visibility(self, short_sighted=short_sighted)

    def roll_turn(self, sess) -> None:
        units_copy = self.units[:]
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.move(sess, self)
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.move(sess, self, sensitive=True)
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.attack(sess, self)

        cities_copy = self.cities[:]
        random.shuffle(cities_copy)
        for city in cities_copy:
            city.roll_turn(sess, self)

        for civ in self.civs:
            civ.roll_turn(sess, self)

        self.turn_num += 1

    def handle_wonder_built(self, sess, civ: Civ, building_template: BuildingTemplate) -> None:
        self.wonders_built[building_template.name] = True
        
        if (game_player := civ.game_player) is not None and (vp_reward := building_template.vp_reward) is not None:
            game_player.score += vp_reward

        for city in self.cities:
            for i, building in enumerate(city.buildings_queue):
                if i > 0 and building.name == building_template.name:
                    city.buildings_queue = [building for building in city.buildings_queue if building.name != building_template.name]
                    break

        for civ_to_announce in self.civs:
            self.add_animation_frame_for_civ(sess, {
                'type': 'WonderBuilt',
                'civ': civ.template.name,
                'wonder': building_template.name,
            }, civ_to_announce)

    def add_animation_frame_for_civ(self, sess, data: dict[str, Any], civ: Optional[Civ]) -> None:
        if civ is not None and (game_player := civ.game_player) is not None:
            highest_existing_frame_num = (
                sess.query(AnimationFrame.frame_num)
                .filter(AnimationFrame.game_id == self.game_id)
                .filter(AnimationFrame.turn_num == self.turn_num)
                .filter(AnimationFrame.player_num == game_player.player_num)
                .order_by(AnimationFrame.frame_num.desc())
                .first()
            ) or 0

            frame = AnimationFrame(
                game_id=self.game_id,
                turn_num=self.turn_num,
                frame_num=highest_existing_frame_num + 1,
                player_num=game_player.player_num,
                data=data,
                game_state=self.to_json(from_civ_perspectives=[civ]),
            )

            sess.add(frame)

    def add_animation_frame(self, sess, data: dict[str, Any], hexes_must_be_visible: Optional[list[Hex]] = None) -> None:
        self.add_animation_frame_for_civ(sess, data, None)
        for civ in self.civs:
            if hexes_must_be_visible is None or any(hex.visibility_by_civ.get(civ.id) for hex in hexes_must_be_visible):
                self.add_animation_frame_for_civ(sess, data, civ)

        sess.commit()

    def get_civ_by_name(self, civ_name: str) -> Civ:
        for civ in self.civs:
            if civ.template.name == civ_name:
                return civ
        raise Exception("Civ not found")
    
    def to_json(self, from_civ_perspectives: Optional[list[Civ]] = None) -> dict:
        return {
            "game_id": self.game_id,
            "hexes": {key: hex.to_json(from_civ_perspectives=from_civ_perspectives) for key, hex in self.hexes.items()},
            "civs": [civ.to_json() for civ in self.civs],
            "game_players": [game_player.to_json() for game_player in self.game_players],
            "turn_num": self.turn_num,
            "wonders_built": self.wonders_built,
            "special_mode": self.special_mode,
        }
    
    @staticmethod
    def from_json(json: dict) -> "GameState":
        hexes = {key: Hex.from_json(hex_json) for key, hex_json in json["hexes"].items()}
        game_state = GameState(game_id=json["game_id"], hexes=hexes)
        game_state.civs = [Civ.from_json(civ_json) for civ_json in json["civs"]]
        game_state.game_players = [GamePlayer.from_json(game_player_json) for game_player_json in json["game_players"]]
        game_state.turn_num = json["turn_num"]
        game_state.wonders_built = json["wonders_built"].copy()
        game_state.special_mode = json["special_mode"]
        game_state.set_unit_and_city_hexes()
        return game_state


def update_staged_moves(game_id: str, player_num: int, moves: dict) -> None:
    with rlock(f'staged_moves_lock:{game_id}:{player_num}'):
        staged_moves = rget_json(f'staged_moves:{game_id}:{player_num}') or {}
        staged_moves.update(moves)
        rset_json(f'staged_moves:{game_id}:{player_num}', staged_moves, ex=24 * 60 * 60)
