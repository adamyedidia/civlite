from settings import STRICT_MODE
from unit_template import UnitTemplate
from unit_templates_list import UNITS


class UnitBuilding:    
    def __init__(self, template: UnitTemplate) -> None:
        self.template = template
        self.active: bool = False
        self.production_rate: float = 0.0
        self.metal: float = 0
        self.projected_metal_income: float = 0
        self.delete_queued = False

    @property
    def one_per_civ_key(self):
        return self.template.name

    @property
    def prereq(self):
        return self.template.prereq
    
    @property
    def projected_unit_count(self) -> int:
        if self.active:
            return int((self.metal + self.projected_metal_income) / self.template.metal_cost)
        else:
            return 0
    
    def adjust_projected_unit_builds(self, total_metal):
        self.projected_metal_income = total_metal * self.production_rate

    def harvest_yields(self, amount):
        amount = amount * self.production_rate
        if STRICT_MODE:
            assert round(amount, 3) == round(self.projected_metal_income, 3), f"Projection failure in {self.template.building_name}! {amount} != {self.projected_metal_income}"
        self.metal += self.projected_metal_income
        self.projected_metal_income = 0

    def to_json(self):
        return {
            "template_name": self.template.name,
            "active": self.active,
            "production_rate": self.production_rate,
            "metal": self.metal,
            "projected_metal_income": self.projected_metal_income,
            "projected_unit_count": self.projected_unit_count,
            "delete_queued": self.delete_queued,
        }
    
    @staticmethod
    def from_json(json) -> "UnitBuilding":
        unit = UnitBuilding(UNITS.by_name(json["template_name"]))
        unit.active = json["active"]
        unit.production_rate = json["production_rate"]
        unit.metal = json["metal"]
        unit.projected_metal_income = json["projected_metal_income"]
        unit.delete_queued = json["delete_queued"]
        return unit
