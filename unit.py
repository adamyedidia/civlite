from civ import Civ
from unit_template import UnitTemplate
from unit_templates_list import UNITS


class Unit:
    def __init__(self, template: UnitTemplate, civ: Civ) -> None:
        self.template = template
        self.attack = template.attack        
        self.health = template.health
        self.civ = civ

    def to_json(self) -> dict:
        return {
            "name": self.template.name,
            "attack": self.attack,
            "health": self.health,
            "civ": self.civ.to_json(),
        }
    
    @staticmethod
    def from_json(json: dict) -> "Unit":
        unit = Unit(
            template=UnitTemplate.from_json(UNITS[json["name"]]),
            civ=Civ.from_json(json["civ"]),
        )
        unit.attack = json["attack"]
        unit.health = json["health"]

        return unit