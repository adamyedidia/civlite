from typing import TYPE_CHECKING, Optional

from civ_template import CivTemplate
from civ_templates_list import CIVS
from game_player import GamePlayer
from settings import FAST_VITALITY_DECAY_RATE, VITALITY_DECAY_RATE
from tech import Tech
from tech_template import TechTemplate
from utils import generate_unique_id

if TYPE_CHECKING:
    from game_state import GameState


class Civ:
    def __init__(self, civ_template: CivTemplate, game_player: Optional[GamePlayer]):
        self.id = generate_unique_id()
        self.game_player = game_player
        self.template = civ_template
        self.science = 0.0
        self.tech_queue: list[TechTemplate] = []
        self.techs: dict[str, bool] = {}
        self.vitality = 1.0

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "game_player": self.game_player.to_json() if self.game_player else None,
            "name": self.template.name,
            "science": self.science,
            "tech_queue": [tech_template.to_json() for tech_template in self.tech_queue],
            "techs": self.techs,
            "vitality": self.vitality,
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

        return civ
