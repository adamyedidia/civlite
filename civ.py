from typing import Optional

from civ_template import CivTemplate
from civ_templates_list import CIVS


class Civ:
    def __init__(self, civ_template: CivTemplate, player_num: Optional[int]):
        self.player_num = player_num
        self.template = civ_template

    def to_json(self) -> dict:
        return {
            "player_num": self.player_num,
            "name": self.template.name,
        }

    @staticmethod
    def from_json(json: dict) -> "Civ":
        return Civ(
            civ_template=CivTemplate.from_json(CIVS[json["name"]]),
            player_num=json["player_num"],
        )
