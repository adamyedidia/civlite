from typing import Optional, Union
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from unit_template import UnitTemplate
from unit_templates_list import UNITS
from wonder_template import WonderTemplate
from wonder_templates_list import WONDERS
from tech_template import TechTemplate

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_state import GameState

class Building:
    def __init__(self, template: Union[UnitTemplate, BuildingTemplate, WonderTemplate]) -> None:
        self.template = template
        self.unit_name = template.name if isinstance(template, UnitTemplate) else None
        self.ruined: bool = False

    def __repr__(self):
        return f"<Building {self.template.name}>"

    @property
    def building_name(self) -> str:
        if isinstance(self.template, UnitTemplate):
            return self.template.building_name
        else:
            return self.template.name
 
    @property
    def type(self) -> str:
        return "unit" if isinstance(self.template, UnitTemplate) else "building" if isinstance(self.template, BuildingTemplate) else "wonder"

    @property
    def is_national_wonder(self) -> bool:
        return isinstance(self.template, BuildingTemplate) and self.template.is_national_wonder
    
    @property
    def is_wonder(self) -> bool:
        return isinstance(self.template, WonderTemplate)

    @property
    def abilities(self) -> list:
        if isinstance(self.template, BuildingTemplate):
            return self.template.abilities
        return []

    @property
    def prereq(self) -> Optional[TechTemplate]:
        if isinstance(self.template, BuildingTemplate):
            return self.template.prereq
        elif isinstance(self.template, UnitTemplate):
            return self.template.prereq
        return None
    
    @property
    def vp_reward(self) -> int:
        if isinstance(self.template, BuildingTemplate):
            return self.template.vp_reward or 0
        if isinstance(self.template, WonderTemplate):
            return self.template.vp_reward
        return 0

    def update_ruined_status(self, city, game_state: 'GameState') -> None:
        if isinstance(self.template, WonderTemplate):
            builders = game_state.built_wonders[self.template].civs
            self.ruined = not city.civ in builders

    def has_ability(self, ability_name: str) -> bool:
        if isinstance(self.template, UnitTemplate):
            return False
        if isinstance(self.template, WonderTemplate) and self.ruined:
            return False
        return any([ability.name == ability_name for ability in self.template.abilities])

    def numbers_of_ability(self, ability_name: str) -> list:
        assert isinstance(self.template, BuildingTemplate)
        return [ability.numbers for ability in self.template.abilities if ability.name == ability_name][0]

    def to_json(self) -> dict:
        return {
            "type": self.type,
            "template_name": self.template.name,
            "building_name": self.building_name,
            "unit_name": self.unit_name,
            "ruined": self.ruined
        }
    
    @staticmethod
    def from_json(json: dict) -> "Building":
        type = json.get('type')
        proto_dict = UNITS if type == 'unit' else BUILDINGS if type == 'building' else WONDERS
        b = Building(template=proto_dict.by_name(json['template_name']))
        b.ruined = json['ruined']
        return b
