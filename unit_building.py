from unit_template import UnitTemplate
from unit_templates_list import UNITS


class UnitBuilding:    
    def __init__(self, template: UnitTemplate) -> None:
        self.template = template
        self.active: bool = False
        self.metal: float = 0
        self.projected_metal_income: float = 0

    @property
    def one_per_civ_key(self):
        return self.template.name

    @property
    def prereq(self):
        return self.template.prereq

    def to_json(self):
        return {
            "template_name": self.template.name,
            "active": self.active,
            "metal": self.metal,
            "projected_metal_income": self.projected_metal_income,
        }
    
    @staticmethod
    def from_json(json) -> "UnitBuilding":
        unit = UnitBuilding(UNITS.by_name(json["template_name"]))
        unit.active = json["active"]
        unit.metal = json["metal"]
        unit.projected_metal_income = json["projected_metal_income"]
        return unit
