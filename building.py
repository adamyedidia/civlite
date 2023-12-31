from typing import Optional
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from unit_template import UnitTemplate
from unit_templates_list import UNITS


class Building:
    def __init__(self, unit_template: Optional[UnitTemplate], building_template: Optional[BuildingTemplate]) -> None:
        assert (unit_template is None) + (building_template is None) == 1
        self.unit_name = None
        self.unit_template = None
        self.building_template = None
        if unit_template is not None:
            self.name = unit_template.building_name
            self.unit_name = unit_template.name
            self.unit_template = unit_template
        else:
            assert building_template
            self.building_template = building_template

    @property
    def type(self) -> str:
        return "military" if self.unit_name else self.building_template.type  # type: ignore

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "unit_name": self.unit_name,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Building":
        unit_name = json.get('unit_name')
        if unit_name is not None:
            return Building(
                unit_template=UnitTemplate.from_json(UNITS[unit_name]),
                building_template=None,
            )
        
        return Building(
            unit_template=None,
            building_template=BuildingTemplate.from_json(BUILDINGS[json['name']]),
        )