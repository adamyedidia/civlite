from typing import Any, Optional
from animation_frame import AnimationFrame
from building_template import BuildingTemplate
from camp import Camp
from city import City
from civ import Civ
from civ_template import CivTemplate
from civ_templates_list import BARBARIAN_CIV
from game_player import GamePlayer
from hex import Hex
from redis_utils import rget_json, rlock, rset_json
from tech_template import TechTemplate
from tech_templates_list import TECHS
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


def get_all_camps(hexes: dict[str, Hex]) -> list[Camp]:
    camps = []
    for hex in hexes.values():
        if hex.camp:
            camps.append(hex.camp)
    return camps


class GameState:
    def __init__(self, game_id: str, hexes: dict[str, Hex]):
        self.hexes = hexes
        self.game_id = game_id
        self.units = get_all_units(hexes)
        self.cities = get_all_cities(hexes)
        self.camps = get_all_camps(hexes)
        self.civs_by_id: dict[str, Civ] = {}
        self.turn_num = 1
        self.game_player_by_player_num: dict[int, GamePlayer] = {}
        self.wonders_built: dict[str, bool] = {}
        self.special_mode: Optional[str] = 'starting_location'
        self.barbarians: Civ = Civ(CivTemplate.from_json(BARBARIAN_CIV["Barbarians"]), None)

    def set_unit_and_city_hexes(self) -> None:
        for hex in self.hexes.values():
            for unit in hex.units:
                unit.hex = hex
            if hex.city:
                hex.city.hex = hex
            if hex.camp:
                hex.camp.hex = hex

    def pick_random_hex(self) -> Hex:
        return random.choice(list(self.hexes.values()))

    def update_from_player_moves(self, player_num: int, moves: list[dict]) -> Optional[list[Civ]]:
        game_player_to_return: Optional[GamePlayer] = None
        for move in moves:
            if move['move_type'] == 'choose_starting_city':
                city_id = move['city_id']

                for city in self.cities:
                    if (game_player := city.civ.game_player) and game_player.player_num == player_num:
                        if city.id == city_id:
                            game_player_to_return = game_player
                            game_player_to_return.civ_id = city.civ.id
                            self.game_player_by_player_num[player_num].civ_id = city.civ.id
                            city.capitalize()

                        else:
                            if city.hex:
                                camp = Camp(self.barbarians)
                                camp.hex = city.hex
                                city.hex.camp = camp
                                self.camps.append(camp)

                                city.hex.city = None
                                city.hex = None
                                self.cities = [c for c in self.cities if c.id != city.id]

                            del self.civs_by_id[city.civ.id]

                self.refresh_visibility_by_civ()

            if move['move_type'] == 'choose_tech':
                tech_name = move['tech_name']
                game_player = self.game_player_by_player_num[player_num]
                assert game_player.civ_id
                civ = self.civs_by_id[game_player.civ_id]
                tech = TechTemplate.from_json(TECHS[tech_name])
                civ.tech_queue.append(tech)
                game_player_to_return = game_player

        if game_player_to_return is not None and game_player_to_return.civ_id is not None:
            from_civ_perspectives = [self.civs_by_id[game_player_to_return.civ_id]]
            return from_civ_perspectives

        return None

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

        for civ in self.civs_by_id.values():
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

        for civ_to_announce in self.civs_by_id.values():
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
        for civ in self.civs_by_id.values():
            if hexes_must_be_visible is None or any(hex.visibility_by_civ.get(civ.id) for hex in hexes_must_be_visible):
                self.add_animation_frame_for_civ(sess, data, civ)

        sess.commit()

    def get_civ_by_name(self, civ_name: str) -> Civ:
        for civ in self.civs_by_id.values():
            if civ.template.name == civ_name:
                return civ
        raise Exception("Civ not found")
    
    def to_json(self, from_civ_perspectives: Optional[list[Civ]] = None) -> dict:
        return {
            "game_id": self.game_id,
            "hexes": {key: hex.to_json(from_civ_perspectives=from_civ_perspectives) for key, hex in self.hexes.items()},
            "civs_by_id": {civ_id: civ.to_json() for civ_id, civ in self.civs_by_id.items()},
            "game_player_by_player_num": {player_num: game_player.to_json() for player_num, game_player in self.game_player_by_player_num.items()},
            "turn_num": self.turn_num,
            "wonders_built": self.wonders_built,
            "special_mode": self.special_mode,
        }
    
    @staticmethod
    def from_json(json: dict) -> "GameState":
        hexes = {key: Hex.from_json(hex_json) for key, hex_json in json["hexes"].items()}
        game_state = GameState(game_id=json["game_id"], hexes=hexes)
        game_state.civs_by_id = {civ_id: Civ.from_json(civ_json) for civ_id, civ_json in json["civs_by_id"].items()}
        game_state.game_player_by_player_num = {int(player_num): GamePlayer.from_json(game_player_json) for player_num, game_player_json in json["game_player_by_player_num"].items()}
        game_state.turn_num = json["turn_num"]
        game_state.wonders_built = json["wonders_built"].copy()
        game_state.special_mode = json["special_mode"]
        game_state.set_unit_and_city_hexes()
        return game_state


def get_most_recent_game_state_json(sess, game_id: str) -> dict:
    most_recent_game_state_animation_frame = (
        sess.query(AnimationFrame)
        .filter(AnimationFrame.game_id == game_id)
        .filter(AnimationFrame.player_num == None)
        .filter(AnimationFrame.frame_num == 0)
        .order_by(AnimationFrame.turn_num.desc())
        .first()
    )

    assert most_recent_game_state_animation_frame is not None

    most_recent_game_state = most_recent_game_state_animation_frame.game_state

    return most_recent_game_state


def update_staged_moves(sess, game_id: str, player_num: int, moves: list[dict]) -> tuple[GameState, Optional[list[Civ]]]:
    with rlock(f'staged_moves_lock:{game_id}:{player_num}'):
        staged_moves = rget_json(f'staged_moves:{game_id}:{player_num}') or []
        game_state_json = rget_json(f'staged_game_state:{game_id}:{player_num}') or get_most_recent_game_state_json(sess, game_id)
        game_state = GameState.from_json(game_state_json)
        from_civ_perspectives = game_state.update_from_player_moves(player_num, moves)

        staged_moves.extend(moves)

        rset_json(f'staged_moves:{game_id}:{player_num}', staged_moves, ex=24 * 60 * 60)
        rset_json(f'staged_game_state:{game_id}:{player_num}', game_state.to_json())

        return game_state, from_civ_perspectives
