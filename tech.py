import random
from tech_template import TechTemplate
from tech_templates_list import TECHS

from typing import TYPE_CHECKING

from unit_templates_list import UNITS

if TYPE_CHECKING:
    from civ import Civ

class Tech:
    def __init__(self, template: TechTemplate):
        self.template = template
    
    def to_json(self) -> dict:
        return {
            "name": self.template.name,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Tech":
        return Tech(
            template=TechTemplate.from_json(TECHS[json['name']]),
        )
