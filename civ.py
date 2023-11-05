from typing import Optional

from civ_template import CivTemplate
from civ_templates_list import CIVS
from utils import generate_unique_id


class Civ:
    def __init__(self, civ_template: CivTemplate, player_num: Optional[int]):
        self.id = generate_unique_id()
        self.player_num = player_num
        self.template = civ_template
        self.science = 0

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "player_num": self.player_num,
            "name": self.template.name,
            "science": self.science,
        }

    @staticmethod
    def from_json(json: dict) -> "Civ":
        civ = Civ(
            civ_template=CivTemplate.from_json(CIVS[json["name"]]),
            player_num=json["player_num"],
        )
        civ.id = json["id"]
        civ.science = json["science"]

        return civ
