import random
from typing import TYPE_CHECKING, Optional
from building_templates_list import BUILDINGS

from civ_template import CivTemplate
from civ_templates_list import ANCIENT_CIVS, CIVS
from game_player import GamePlayer
from settings import FAST_VITALITY_DECAY_RATE, NUM_STARTING_LOCATION_OPTIONS, VITALITY_DECAY_RATE, BASE_CITY_POWER_INCOME
from tech import Tech
from tech_template import TechTemplate
from unit_templates_list import UNITS
from utils import generate_unique_id

import random

if TYPE_CHECKING:
    from game_state import GameState
    from hex import Hex


class Civ:
    def __init__(self, civ_template: CivTemplate, game_player: Optional[GamePlayer]):
        self.id = generate_unique_id()
        self.game_player = game_player
        self.template = civ_template
        self.science = 0.0
        self.tech_queue: list[TechTemplate] = []
        self.techs: dict[str, bool] = {}
        self.vitality = 1.0
        self.city_power = 0.0
        self.available_buildings: list[str] = []
        self.available_unit_buildings: list[str] = []
        self.target1: Optional['Hex'] = None
        self.target2: Optional['Hex'] = None
        self.target1_coords: Optional[str] = None
        self.target2_coords: Optional[str] = None
        self.projected_science_income = 0.0
        self.projected_city_power_income = 0.0

        self.fill_out_available_buildings()

    def has_ability(self, ability_name: str) -> bool:
        return any([ability.name == ability_name for ability in self.template.abilities])

    def numbers_of_ability(self, ability_name: str) -> list:
        return [ability.numbers for ability in self.template.abilities if ability.name == ability_name][0]

    def adjust_projected_yields(self, game_state: 'GameState') -> None:
        self.projected_science_income = 0.0
        self.projected_city_power_income = BASE_CITY_POWER_INCOME

        for city in game_state.cities_by_id.values():
            if city.civ.id == self.id:
                self.projected_science_income += city.projected_science_income
                self.projected_city_power_income += city.projected_city_power_income

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "game_player": self.game_player.to_json() if self.game_player else None,
            "name": self.template.name,
            "science": self.science,
            "tech_queue": [tech_template.to_json() for tech_template in self.tech_queue],
            "techs": self.techs,
            "vitality": self.vitality,
            "city_power": self.city_power,
            "available_buildings": self.available_buildings,
            "available_unit_buildings": self.available_unit_buildings,
            "target1": self.target1.coords if self.target1 else None,
            "target2": self.target2.coords if self.target2 else None,
            "projected_science_income": self.projected_science_income,
            "projected_city_power_income": self.projected_city_power_income,
        }

    def fill_out_available_buildings(self) -> None:
        self.available_buildings = [building["name"] for building in BUILDINGS.values() if (not building.get('prereq')) or self.techs.get(building.get("prereq"))]  # type: ignore
        self.available_unit_buildings = [unit.get("building_name") for unit in UNITS.values() if (((not unit.get('prereq')) or self.techs.get(unit.get("prereq"))) and unit.get("building_name"))]  # type: ignore

    def roll_turn(self, sess, game_state: 'GameState') -> None:
        self.fill_out_available_buildings()
        
        while self.tech_queue and self.tech_queue[0].cost <= self.science:
            self.science -= self.tech_queue[0].cost
            self.techs[self.tech_queue[0].name] = True
            tech = self.tech_queue.pop(0)

            game_state.add_animation_frame_for_civ(sess, {
                "type": "TechResearched",
                "tech": tech.name,
            }, self)

        if self.vitality > 1:
            self.vitality *= FAST_VITALITY_DECAY_RATE
        else:
            self.vitality *= VITALITY_DECAY_RATE

        self.city_power += BASE_CITY_POWER_INCOME

    def update_game_player(self, game_player_by_player_num: dict[int, GamePlayer]) -> None:
        if self.game_player is not None:
            self.game_player = game_player_by_player_num[self.game_player.player_num]

    @staticmethod
    def from_json(json: dict) -> "Civ":
        civ = Civ(
            civ_template=CivTemplate.from_json(CIVS[json["name"]]),
            game_player=GamePlayer.from_json(json["game_player"]) if json["game_player"] else None,
        )
        civ.id = json["id"]
        civ.science = json["science"]
        civ.tech_queue = [TechTemplate.from_json(tech_template) for tech_template in json["tech_queue"]]
        civ.techs = json["techs"].copy()
        civ.vitality = json["vitality"]
        civ.city_power = json["city_power"]
        civ.available_buildings = json["available_buildings"][:]
        civ.available_unit_buildings = json["available_unit_buildings"][:]
        civ.fill_out_available_buildings()
        civ.target1_coords = json["target1"]
        civ.target2_coords = json["target2"]
        civ.projected_science_income = json["projected_science_income"]
        civ.projected_city_power_income = json["projected_city_power_income"]

        return civ

    def __repr__(self) -> str:
        return f"<Civ {self.id}: {self.template.name}>"


def create_starting_civ_options_for_players(game_players: list[GamePlayer], starting_locations: list['Hex']) -> dict[int, list[tuple[Civ, 'Hex']]]:
    assert len(game_players) <= 8

    starting_civ_option_jsons = random.sample(list(ANCIENT_CIVS.values()), NUM_STARTING_LOCATION_OPTIONS * len(game_players))

    starting_civ_options = {}

    counter = 0

    for game_player in game_players:
        starting_civ_options[game_player.player_num] = []
        for _ in range(NUM_STARTING_LOCATION_OPTIONS):
            starting_civ_options[game_player.player_num].append((Civ(CivTemplate.from_json(starting_civ_option_jsons[counter]), game_player), starting_locations[counter]))
            counter += 1

    return starting_civ_options
