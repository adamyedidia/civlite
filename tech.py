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
    

def get_tech_choices_for_civ(civ: "Civ") -> list[dict]:
    characteristic_tech = None

    if civ.has_ability('IncreasedStrengthForUnit'):
        print(civ.numbers_of_ability('IncreasedStrengthForUnit'))
        special_unit_name = civ.numbers_of_ability('IncreasedStrengthForUnit')[0]

        if (prereq := UNITS[special_unit_name].get('prereq')):
            characteristic_tech = TECHS[prereq]

    tech_level = len(civ.techs)

    max_science_for_techs_available = 5 * (tech_level + 2)

    num_techs_to_offer = 3 if characteristic_tech is None else 2

    techs_to_sample_from = [tech for tech in TECHS.values() 
                            if tech['cost'] <= max_science_for_techs_available and (characteristic_tech is None or tech['name'] != characteristic_tech['name'])]

    techs_to_offer = random.sample(techs_to_sample_from, num_techs_to_offer)

    return [*techs_to_offer, characteristic_tech] if characteristic_tech else techs_to_offer