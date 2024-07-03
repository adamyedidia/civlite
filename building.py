from typing import Optional, Union
from building_template import BuildingTemplate
from building_templates_list import BUILDINGS
from ability import Ability
from effect import CityTargetEffect
from unit_template import UnitTemplate
from unit_templates_list import UNITS
from wonder_template import WonderTemplate
from wonder_templates_list import WONDERS
from tech_template import TechTemplate

from typing import TYPE_CHECKING

from yields import Yields

if TYPE_CHECKING:
    from game_state import GameState
    from city import City

class Building:
    def __init__(self, template: Union[UnitTemplate, BuildingTemplate, WonderTemplate]) -> None:
        self._template = template  # TODO remove external calls to this
        self.ruined: bool = False

    def __repr__(self):
        return f"<Building {self._template.name}>"

    @property
    def building_name(self) -> str:
        if isinstance(self._template, UnitTemplate):
            return self._template.building_name
        else:
            return self._template.name
 
    @property
    def type(self) -> str:
        return "unit" if isinstance(self._template, UnitTemplate) else self._template.type.value if isinstance(self._template, BuildingTemplate) else "wonder"

    @property
    def one_per_civ(self) -> bool:
        return self._template != UNITS.WARRIOR
    
    @property
    def destroy_on_owner_change(self) -> bool:
        return isinstance(self._template, BuildingTemplate)
    
    @property
    def prereq(self) -> Optional[TechTemplate]:
        if isinstance(self._template, BuildingTemplate):
            return self._template.prereq
        elif isinstance(self._template, UnitTemplate):
            return self._template.prereq
        return None
    
    @property
    def vp_reward(self) -> int:
        if isinstance(self._template, BuildingTemplate):
            return self._template.vp_reward or 0
        if isinstance(self._template, WonderTemplate):
            return self._template.vp_reward
        return 0
    
    @property
    def on_build(self) -> list[CityTargetEffect]:
        if isinstance(self._template, BuildingTemplate):
            return self._template.on_build
        if isinstance(self._template, WonderTemplate):
            return self._template.on_build
        return []
    
    @property
    def per_turn(self) -> list[CityTargetEffect]:
        if isinstance(self._template, BuildingTemplate):
            return self._template.per_turn
        if isinstance(self._template, WonderTemplate):
            return self._template.per_turn
        return []
    
    @property
    def advancement_level(self) -> int:
        if isinstance(self._template, BuildingTemplate):
            return self._template.advancement_level()
        elif isinstance(self._template, UnitTemplate):
            return self._template.advancement_level()
        elif isinstance(self._template, WonderTemplate):
            return self._template.age
        return 0

    def update_ruined_status(self, city, game_state: 'GameState') -> None:
        if isinstance(self._template, WonderTemplate):
            self.ruined = (city.id, city.civ.id) not in game_state.built_wonders[self._template].infos

    def passive_building_abilities_of_name(self, ability_name: str) -> list[Ability]:
        if isinstance(self._template, UnitTemplate):
            return []
        if isinstance(self._template, WonderTemplate) and self.ruined:
            return []
        return [ability for ability in self._template.abilities if ability.name == ability_name]

    def calculate_yields(self, city: 'City', game_state: 'GameState') -> Yields:
        if isinstance(self._template, BuildingTemplate) and self._template.calculate_yields is not None:
            return self._template.calculate_yields.calculate(city)
        return Yields()

    def to_json(self) -> dict:
        return {
            "type": self.type,
            "template_name": self._template.name,
            "building_name": self.building_name,
            "ruined": self.ruined
        }
    
    @staticmethod
    def from_json(json: dict) -> "Building":
        type = json.get('type')
        proto_dict = UNITS if type == 'unit' else WONDERS if type == 'wonder' else BUILDINGS
        b = Building(template=proto_dict.by_name(json['template_name']))
        b.ruined = json['ruined']
        return b
