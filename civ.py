from typing import Optional

from civ_template import CivTemplate
from civ_templates_list import CIVS
from game_player import GamePlayer
from tech import Tech
from tech_template import TechTemplate
from utils import generate_unique_id


class Civ:
    def __init__(self, civ_template: CivTemplate, game_player: Optional[GamePlayer]):
        self.id = generate_unique_id()
        self.game_player = game_player
        self.template = civ_template
        self.science = 0
        self.tech_queue: list[TechTemplate] = []
        self.techs: dict[str, bool] = {}

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "game_player": self.game_player.to_json() if self.game_player else None,
            "name": self.template.name,
            "science": self.science,
            "tech_queue": [tech_template.to_json() for tech_template in self.tech_queue],
            "techs": self.techs,
        }

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

        return civ
