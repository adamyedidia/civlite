import random
from typing import TYPE_CHECKING, Optional

from civ_template import CivTemplate
from civ_templates_list import ANCIENT_CIVS, CIVS
from game_player import GamePlayer
from settings import FAST_VITALITY_DECAY_RATE, NUM_STARTING_LOCATION_OPTIONS, VITALITY_DECAY_RATE
from tech import Tech
from tech_template import TechTemplate
from utils import generate_unique_id

import random

if TYPE_CHECKING:
    from game_state import GameState
    from hex import Hex


class Civ:
    def __init__(self, civ_template: CivTemplate, game_player: Optional[GamePlayer]):
        self.id = generate_unique_id()
        self.game_player = game_player
        self.template = civ_template
        self.science = 0.0
        self.tech_queue: list[TechTemplate] = []
        self.techs: dict[str, bool] = {}
        self.vitality = 1.0
        self.city_power = 0.0

    def has_ability(self, ability_name: str) -> bool:
        return any([ability.name == ability_name for ability in self.template.abilities])

    def numbers_of_ability(self, ability_name: str) -> list:
        return [ability.numbers for ability in self.template.abilities if ability.name == ability_name]

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "game_player": self.game_player.to_json() if self.game_player else None,
            "name": self.template.name,
            "science": self.science,
            "tech_queue": [tech_template.to_json() for tech_template in self.tech_queue],
            "techs": self.techs,
            "vitality": self.vitality,
            "city_power": self.city_power,
        }

    def roll_turn(self, sess, game_state: 'GameState') -> None:
        while self.tech_queue and self.tech_queue[0].cost <= self.science:
            self.science -= self.tech_queue[0].cost
            self.techs[self.tech_queue[0].name] = True
            self.tech_queue.pop(0)

            game_state.add_animation_frame_for_civ(sess, {
                "type": "TechResearched",
                "tech": self.tech_queue[0].name,
            }, self)

        if self.vitality > 1:
            self.vitality *= FAST_VITALITY_DECAY_RATE
        else:
            self.vitality *= VITALITY_DECAY_RATE

        self.city_power += 20

    @staticmethod
    def from_json(json: dict) -> "Civ":
        civ = Civ(
            civ_template=CivTemplate.from_json(CIVS[json["name"]]),
            game_player=GamePlayer.from_json(json["game_player"]) if json["game_player"] else None,
        )
        civ.id = json["id"]
        civ.science = json["science"]
        civ.tech_queue = [TechTemplate.from_json(tech_template) for tech_template in json["tech_queue"]]
        civ.techs = json["techs"].copy()
        civ.vitality = json["vitality"]
        civ.city_power = json["city_power"]

        return civ


def create_starting_civ_options_for_players(game_players: list[GamePlayer], starting_locations: list['Hex']) -> dict[int, list[tuple[Civ, 'Hex']]]:
    assert len(game_players) <= 8

    starting_civ_option_jsons = random.sample(list(ANCIENT_CIVS.values()), NUM_STARTING_LOCATION_OPTIONS * len(game_players))

    starting_civ_options = {}

    counter = 0

    for game_player in game_players:
        starting_civ_options[game_player.player_num] = []
        for _ in range(NUM_STARTING_LOCATION_OPTIONS):
            starting_civ_options[game_player.player_num].append((Civ(CivTemplate.from_json(starting_civ_option_jsons[counter]), game_player), starting_locations[counter]))
            counter += 1

    return starting_civ_options
