from typing import Optional
from civ import Civ
from unit_template import UnitTemplate
from unit_templates_list import UNITS


class Unit:
    def __init__(self, template: UnitTemplate, civ: Civ) -> None:
        self.template = template
        self.attack = template.attack        
        self.health = template.health
        self.civ = civ
        self.has_acted = False
        self.target: Optional[str] = None

    def act(self) -> None:
        pass

    def move_one_step(self) -> None:
        pass

    def to_json(self) -> dict:
        return {
            "name": self.template.name,
            "attack": self.attack,
            "health": self.health,
            "civ": self.civ.to_json(),
            "target": self.target,
            "has_acted": self.has_acted,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Unit":
        unit = Unit(
            template=UnitTemplate.from_json(UNITS[json["name"]]),
            civ=Civ.from_json(json["civ"]),
        )
        unit.attack = json["attack"]
        unit.health = json["health"]
        unit.has_acted = json["has_acted"]
        unit.target = json["target"]

        return unit