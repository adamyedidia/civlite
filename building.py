import itertools
from typing import Optional, Union
from building_template import BuildingTemplate, BuildingType
from building_templates_list import BUILDINGS
from ability import Ability
from effect import CityTargetEffect
from settings import BASE_WONDER_COST
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
    def __init__(self, template: Union[BuildingTemplate, WonderTemplate]) -> None:
        self._template = template  # TODO remove external calls to this
        self.ruined: bool = False
        self.projected_bulldoze: bool = False

    def __repr__(self):
        return f"<Building {self._template.name}>"

    @property
    def building_name(self) -> str:
        return self._template.name
 
    @property
    def type(self) -> BuildingType | None:
        return self._template.type if isinstance(self._template, BuildingTemplate) else None

    @property
    def one_per_civ_key(self) -> str | None:
        return self._template.name if self._template != UNITS.WARRIOR else None
    
    @property
    def destroy_on_owner_change(self) -> bool:
        return isinstance(self._template, BuildingTemplate)
    
    @property
    def prereq(self) -> Optional[TechTemplate]:
        if isinstance(self._template, BuildingTemplate):
            return self._template.prereq
        return None
    
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
            return self._template.advancement_level
        elif isinstance(self._template, WonderTemplate):
            return self._template.advancement_level
        return 0

    def update_ruined_status(self, city, game_state: 'GameState') -> None:
        if isinstance(self._template, WonderTemplate):
            self.ruined = (city.id, city.civ.id) not in game_state.built_wonders[self._template].infos

    def passive_building_abilities_of_name(self, ability_name: str) -> list[Ability]:
        if isinstance(self._template, WonderTemplate) and self.ruined:
            return []
        return [ability for ability in self._template.abilities if ability.name == ability_name]

    def calculate_yields_previtality(self, city: 'City') -> Yields | None:
        if isinstance(self._template, BuildingTemplate) and self._template.calculate_yields is not None:
            return self._template.calculate_yields.calculate(city)
        else:
            return None
    
    def calculate_yields_postvitality(self, city) -> Yields | None:
        if self.ruined:
            return Yields()
        if isinstance(self._template, WonderTemplate) and self._template.calculate_yields is not None:
            return self._template.calculate_yields.calculate(city)
        else:
            return None

    def to_json(self) -> dict:
        return {
            "type": self.type.value if self.type else "wonder",
            "template_name": self._template.name,
            "building_name": self.building_name,
            "ruined": self.ruined,
            "projected_bulldoze": self.projected_bulldoze,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Building":
        type_str = json.get('type')
        type = BuildingType(type_str) if type_str != "wonder" else None
        proto_dict = WONDERS if type == None else BUILDINGS
        b = Building(template=proto_dict.by_name(json['template_name']))
        b.ruined = json['ruined']
        b.projected_bulldoze = json["projected_bulldoze"]
        return b

class QueueEntry:
    """
    An entry that can be in building queues.
    """
    def __init__(self, template: Union[UnitTemplate, BuildingTemplate, WonderTemplate]):
        self.template = template

    def __repr__(self):
        return self.template.name
    
    def get_cost(self, game_state: 'GameState') -> int:
        if isinstance(self.template, UnitTemplate):
            return self.template.wood_cost
        elif isinstance(self.template, BuildingTemplate):
            return self.template.cost
        elif isinstance(self.template, WonderTemplate):
            return BASE_WONDER_COST[self.template.advancement_level]
        else:
            raise ValueError("wtf")
    
    @staticmethod
    def find_queue_template_by_name(building_name) -> UnitTemplate | BuildingTemplate | WonderTemplate:
        for template in itertools.chain(WONDERS.all(), UNITS.all(), BUILDINGS.all()):
            if template.name == building_name:
                return template
        raise ValueError(f"No template {building_name}")    

    def to_json(self):
        return {
            'template_name': self.template.name
        }

    @staticmethod
    def from_json(json):
        return QueueEntry(
            template=QueueEntry.find_queue_template_by_name(json['template_name'])
        )
