from unit_template import UnitTemplate
from unit_templates_list import UNITS


class Unit:
    def __init__(self, template: UnitTemplate, player_num: int) -> None:
        self.template = template
        self.attack = template.attack        
        self.health = template.health
        self.player_num = player_num

    def to_json(self) -> dict:
        return {
            "name": self.template.name,
            "attack": self.attack,
            "health": self.health,
            "player_num": self.player_num,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Unit":
        unit = Unit(
            template=UnitTemplate.from_json(UNITS[json["name"]]),
            player_num=json["player_num"],
        )
        unit.attack = json["attack"]
        unit.health = json["health"]

        return unit