from unit_template import UnitTemplate
from unit_templates_list import UNITS


class Building:
    def __init__(self, unit_template: UnitTemplate):
        self.name = unit_template.building_name
        self.unit_name = unit_template.name

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "unit_name": self.unit_name,
        }
    
    def from_json(json: dict) -> "Building":
        return Building(
            unit_template=UnitTemplate.from_json(UNITS[json["unit_name"]]),
        )