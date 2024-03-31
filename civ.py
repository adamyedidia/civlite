import random
from enum import Enum
from typing import TYPE_CHECKING, Optional, Dict
from collections import defaultdict
from building_templates_list import BUILDINGS

from civ_template import CivTemplate
from civ_templates_list import ANCIENT_CIVS, CIVS
from game_player import GamePlayer
from settings import FAST_VITALITY_DECAY_RATE, NUM_STARTING_LOCATION_OPTIONS, VITALITY_DECAY_RATE, BASE_CITY_POWER_INCOME, TECH_VP_REWARD, RENAISSANCE_VP_REWARD
from tech_template import TechTemplate
from unit_templates_list import UNITS
from utils import generate_unique_id
from building_templates_list import BUILDINGS
from tech_templates_list import TECHS

import random

if TYPE_CHECKING:
    from game_state import GameState
    from hex import Hex
    from city import City


class TechStatus(Enum):
    RESEARCHED = 'researched'
    UNAVAILABLE = 'unavailable'
    DISCARDED = 'discarded'
    AVAILABLE = 'available'
    RESEARCHING = 'researching'

class Civ:
    def __init__(self, civ_template: CivTemplate, game_player: Optional[GamePlayer]):
        self.id = generate_unique_id()
        self.game_player = game_player
        self.template = civ_template
        self.science = 0.0
        self.techs_status: Dict[str, TechStatus] = {tech: TechStatus.UNAVAILABLE for tech in TECHS}
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
        self.in_decline = False
        self.initial_advancement_level = 0
        self.trade_hub_id: Optional[str] = None

    def __eq__(self, other: 'Civ') -> bool:
        # TODO(dfarhi) clean up all remaining instances of (civ1.id == civ2.id)
        return other is not None and self.id == other.id

    def moniker(self) -> str:
        game_player_parenthetical = f' ({self.game_player.username})' if self.game_player else ''
        return f"{self.template.name}{game_player_parenthetical}"

    def has_ability(self, ability_name: str) -> bool:
        return any([ability.name == ability_name for ability in self.template.abilities])

    def numbers_of_ability(self, ability_name: str) -> list:
        return [ability.numbers for ability in self.template.abilities if ability.name == ability_name][0]

    def midturn_update(self, game_state):
        self.adjust_projected_yields(game_state)

    def adjust_projected_yields(self, game_state: 'GameState') -> None:
        self.projected_science_income = 0.0
        self.projected_city_power_income = BASE_CITY_POWER_INCOME

        for city in game_state.cities_by_id.values():
            if city.civ.id == self.id:
                self.projected_science_income += city.projected_income['science']
                self.projected_city_power_income += city.projected_income['city-power']

    def has_tech(self, tech_name):
        return self.techs_status[tech_name] == TechStatus.RESEARCHED

    @property
    def researching_tech_name(self):
        all_researching_techs = [tech for tech, status in self.techs_status.items() if status == TechStatus.RESEARCHING]
        assert len(all_researching_techs) <= 1
        return all_researching_techs[0] if all_researching_techs else None

    @property
    def researched_techs(self):
        return [tech for tech, status in self.techs_status.items() if status == TechStatus.RESEARCHED]

    def select_tech(self, tech_name):
        try:
            assert tech_name is None or self.techs_status[tech_name] in (TechStatus.AVAILABLE, TechStatus.RESEARCHING), f"Civ {self} tried to research {tech_name} which is in status {self.techs_status[tech_name]}; all statuses were: {self.techs_status}"
        except Exception:
            print(f"{self.moniker()} tried to research {tech_name} which is in status {self.techs_status[tech_name]}; all statuses were: {self.techs_status}")
            return
        if self.researching_tech_name:
            self.techs_status[self.researching_tech_name] = TechStatus.AVAILABLE
        if tech_name is not None:
            self.techs_status[tech_name] = TechStatus.RESEARCHING 

    def initialize_techs(self, start_techs):
        for tech in start_techs:
            self.techs_status[tech] = TechStatus.RESEARCHED
        self.initial_advancement_level = self.get_advancement_level()
        self.get_new_tech_choices()

    def get_new_tech_choices(self):
        print(f"getting new techs for {self.moniker()}.")
        tech_level = len(self.researched_techs)
        max_advancement_level = 1 + tech_level // 3

        characteristic_tech_offered = False

        if self.has_ability('IncreasedStrengthForUnit'):
            special_unit_name = self.numbers_of_ability('IncreasedStrengthForUnit')[0]

            if (prereq := UNITS[special_unit_name].get('prereq')):
                characteristic_tech = TECHS[prereq]

                if characteristic_tech['advancement_level'] <= max_advancement_level and self.techs_status[characteristic_tech['name']] == TechStatus.UNAVAILABLE:
                    characteristic_tech_offered = True
                    self.techs_status[characteristic_tech['name']] = TechStatus.AVAILABLE



        num_techs_to_offer = 2 if characteristic_tech_offered else 3

        techs_to_sample_from = [TechTemplate.from_json(tech) for tech in TECHS.values() 
                                if (tech['advancement_level'] <= max_advancement_level 
                                    and self.techs_status[tech['name']] == TechStatus.UNAVAILABLE)]

        if len(techs_to_sample_from) < num_techs_to_offer:
            techs_to_offer = techs_to_sample_from

        else:
            techs_to_offer = random.sample(techs_to_sample_from, num_techs_to_offer)

        for choice in techs_to_offer:
            self.techs_status[choice.name] = TechStatus.AVAILABLE
        if len(techs_to_offer) < num_techs_to_offer and self.game_player is not None:
            # We've teched to too many things, time for a Renaissance
            self.techs_status['Renaissance'] = TechStatus.AVAILABLE

    def get_advancement_level(self) -> int:
        my_techs = [tech['advancement_level'] for tech_name, tech in TECHS.items() if self.has_tech(tech_name)]
        if len(my_techs) == 0:
            return 0
        return max(my_techs)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "game_player": self.game_player.to_json() if self.game_player else None,
            "name": self.template.name,
            "science": self.science,
            "techs_status": {tech: status.value for tech, status in self.techs_status.items()},
            "num_researched_techs": len(self.researched_techs),
            "researching_tech_name": self.researching_tech_name,
            "current_tech_choices": [TECHS[tech_name] for tech_name, status in self.techs_status.items() if status in (TechStatus.AVAILABLE, TechStatus.RESEARCHING)],
            "vitality": self.vitality,
            "city_power": self.city_power,
            "available_buildings": self.available_buildings,
            "available_unit_buildings": self.available_unit_buildings,
            "target1": self.target1.coords if self.target1 else None,
            "target2": self.target2.coords if self.target2 else None,
            "projected_science_income": self.projected_science_income,
            "projected_city_power_income": self.projected_city_power_income,
            "in_decline": self.in_decline,
            "advancement_level": self.get_advancement_level(),
            "initial_advancement_level": self.initial_advancement_level,
            "renaissance_cost": self.renaissance_cost() if self.game_player is not None else None,
            "trade_hub_id": self.trade_hub_id,
        }

    def fill_out_available_buildings(self, game_state: 'GameState') -> None:
        self.available_buildings = [building["name"] for building in BUILDINGS.values() if (
            (not building.get('prereq')) or self.has_tech(building.get("prereq"))  # type: ignore
            and (not building.get('is_wonder') or not game_state.wonders_built_to_civ_id.get(building['name']))
            and (not building.get('is_national_wonder') or not building['name'] in (game_state.national_wonders_built_by_civ_id.get(self.id) or []))
        )]
        self.available_unit_buildings: list[str] = [
            str(unit.get("building_name")) for unit in UNITS.values() 
            if (((not unit.get('prereq')) or self.has_tech(unit.get("prereq"))) and 
                unit.get("building_name") and
                (TECHS[unit['prereq']]['advancement_level'] if unit.get('prereq') else 0) >= self.initial_advancement_level - 1)
            ]

    def bot_decide_decline(self, game_state: 'GameState') -> str | None:
        """
        Returns the coords of the location to decline to, or None if I shouldn't decline.
        """
        # Don't decline if I'm sieging a city
        if any([city.under_siege_by_civ == self for city in game_state.cities_by_id.values()]):
            print(f"{self.moniker()} deciding not to decline because I'm seiging a city.")
            return None

        # Don't decline if I'm sieging a camp
        if any([camp.under_siege_by_civ == self for camp in game_state.camps]):
            print(f"{self.moniker()} deciding not to decline because I'm seiging a camp.")
            return None

        # Don't decline if I have above average army size.
        all_army_sizes: dict[str, float] = defaultdict(float)
        for unit in game_state.units:
            all_army_sizes[unit.civ.id] += unit.template.metal_cost
        active_army_sizes: dict[str, float] = {
            game_player.civ_id: all_army_sizes[game_player.civ_id] 
            for game_player in game_state.game_player_by_player_num.values() 
            if game_player.civ_id is not None}
        my_rank: int = sum(active_army_sizes[self.id] <= other for other in active_army_sizes.values())
        total_players: int = len(game_state.game_player_by_player_num)
        if my_rank <= total_players / 2:
            print(f"{self.moniker()} deciding not to decline because I'm rank {my_rank} of {total_players}")
            return None
        
        # Don't decline if it would let someone else win
        assert self.game_player is not None
        other_players = [player for player in game_state.game_player_by_player_num.values() if player.player_num != self.game_player.player_num]
        max_player_score = max(other_players, key=lambda player: player.score).score
        if game_state.game_end_score() - max_player_score < 25:
                print(f"{self.moniker()} deciding not to decline because opponent would win.")
                return None

        my_cities: list[City] = [city for city in game_state.cities_by_id.values() if city.civ == self]
        my_total_yields: float = sum(
            [city.projected_income['food'] +city.projected_income['wood'] + city.projected_income['metal'] +city.projected_income['science'] 
             for city in my_cities])
        
        option_total_yields: dict[str, float] = {}
        for city in game_state.cities_by_id.values():
            assert city.hex is not None, "Unregistered city found!"
            if city.civ_to_revolt_into is None:
                continue

            current_total_yields = city.projected_income['food'] +city.projected_income['wood'] + city.projected_income['metal'] +city.projected_income['science'] 
            option_total_yields[city.hex.coords] = current_total_yields / city.civ.vitality * city.revolting_starting_vitality

        for coords, city in game_state.fresh_cities_for_decline.items():
            option_total_yields[coords] = city.projected_income['food'] +city.projected_income['wood'] + city.projected_income['metal'] +city.projected_income['science'] 
        
        if len(option_total_yields) == 0:
            print(f"{self.moniker()} deciding not to decline because there are no options.")
            return None
        best_option_yields, best_option = max((yields, coords) for coords, yields in option_total_yields.items())
        print(f"{self.moniker()} deciding whether to revolt. My yields are: {my_total_yields}; options have: {option_total_yields}")
        if best_option_yields <= my_total_yields * 2:
            print(f"{self.moniker()} deciding not to decline because I have {my_total_yields} and the best option has {best_option_yields}")
            return None

        print(f"{self.moniker()} deciding to decline at {best_option} because I have {my_total_yields} and the best option has {best_option_yields}")     
        return best_option

    def bot_move(self, game_state: 'GameState') -> None:
        if self.game_player and not self.in_decline and (decline_coords := self.bot_decide_decline(game_state)):
            game_state.execute_decline(decline_coords, self.game_player)

        if random.random() < 0.2 or self.target1 is None or self.target2 is None:
            enemy_cities = [city for city in game_state.cities_by_id.values() if city.civ.id != self.id]
            possible_target_hexes = [*[city.hex for city in enemy_cities if city.hex], *[camp.hex for camp in game_state.camps if camp.hex]]

            random.shuffle(possible_target_hexes)

            if len(possible_target_hexes) > 0:
                self.target1 = possible_target_hexes[0]
                self.target1_coords = self.target1.coords
            if len(possible_target_hexes) > 1:
                self.target2 = possible_target_hexes[1]
                self.target2_coords = self.target2.coords

        if self.researching_tech_name is None:
            if self.has_ability('IncreasedStrengthForUnit'):
                special_unit_name = self.numbers_of_ability('IncreasedStrengthForUnit')[0]
                special_tech_name = UNITS[special_unit_name].get('prereq', None)
            else:
                special_tech_name = None

            available_techs = [tech_name for tech_name, status in self.techs_status.items() if status == TechStatus.AVAILABLE]
            if special_tech_name and self.techs_status[special_tech_name] == TechStatus.AVAILABLE:
                tech_name = special_tech_name
            else:
                if len(available_techs) > 0:
                    tech_name = random.choice(available_techs)
                else:
                    print(f"{self.moniker()} has no available techs")
                    tech_name = None
            self.select_tech(tech_name)
            print(f"  {self.moniker()} chose tech {tech_name} from {available_techs}")

        game_state.refresh_foundability_by_civ()

        if not self.in_decline and self.city_power >= 100 and not self.template.name == 'Barbarians':
            for hex in game_state.hexes.values():
                if hex.is_foundable_by_civ.get(self.id):
                    game_state.found_city_for_civ(self, hex, generate_unique_id())
                    break

        for city in game_state.cities_by_id.values():
            if city.civ.id == self.id:
                city.bot_move(game_state)

    def renaissance_cost(self):
        base_cost = 100 * self.get_advancement_level()
        if self.game_player is None:
            # Something very odd hsa happened, because renaiissance isn't offered to declined civs.
            # But I guess this could happen if you decline while it's queued.
            return base_cost
        return base_cost * (1 + self.game_player.renaissances)

    def complete_research(self, tech: TechTemplate, game_state: 'GameState'):

        for tech_name, status in self.techs_status.items():
            if status == TechStatus.AVAILABLE and tech_name != "Renaissance" and tech_name != tech.name:
                self.techs_status[tech_name] = TechStatus.DISCARDED

        if tech.name == "Renaissance":
            print(f"Renaissance for civ {self.moniker()}")
            cost: int = self.renaissance_cost()
            self.science -= cost
            for tech_name, status in self.techs_status.items():
                if status == TechStatus.DISCARDED:
                    self.techs_status[tech_name] = TechStatus.UNAVAILABLE
            if self.game_player is not None:
                self.game_player.score_from_researching_techs += RENAISSANCE_VP_REWARD
                self.game_player.score += RENAISSANCE_VP_REWARD
                self.game_player.renaissances += 1
        else:
            self.science -= tech.cost
            self.techs_status[tech.name] = TechStatus.RESEARCHED

        # Never discard renaissance
        self.techs_status['Renaissance'] = TechStatus.UNAVAILABLE

        self.get_new_tech_choices()

        if self.game_player:
            self.game_player.score += TECH_VP_REWARD
            self.game_player.score_from_researching_techs += TECH_VP_REWARD

            for wonder in game_state.wonders_built_to_civ_id:
                if game_state.wonders_built_to_civ_id[wonder] == self.id and (abilities := BUILDINGS[wonder]["abilities"]):
                    for ability in abilities:
                        if ability["name"] == "ExtraVpsForTechs":
                            self.game_player.score += ability["numbers"][0]    
                            self.game_player.score_from_abilities += ability["numbers"][0]

    def roll_turn(self, sess, game_state: 'GameState') -> None:
        self.fill_out_available_buildings(game_state)

        if self.researching_tech_name:
            researching_tech = TechTemplate.from_json(TECHS[self.researching_tech_name])
            cost = self.renaissance_cost() if researching_tech.name == "Renaissance" else researching_tech.cost
            if researching_tech and cost <= self.science:
                self.complete_research(researching_tech, game_state)

                game_state.add_animation_frame_for_civ(sess, {
                    "type": "TechResearched",
                    "tech": researching_tech.name,
                }, self)

        if self.vitality > 1:
            self.vitality = max(self.vitality * FAST_VITALITY_DECAY_RATE, VITALITY_DECAY_RATE)
        else:
            self.vitality *= VITALITY_DECAY_RATE

        self.city_power += BASE_CITY_POWER_INCOME * self.vitality

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
        civ.techs_status = {tech: TechStatus(status) for tech, status in json["techs_status"].items()}
        civ.vitality = json["vitality"]
        civ.city_power = json["city_power"]
        civ.available_buildings = json["available_buildings"][:]
        civ.available_unit_buildings = json["available_unit_buildings"][:]
        civ.target1_coords = json["target1"]
        civ.target2_coords = json["target2"]
        civ.projected_science_income = json["projected_science_income"]
        civ.projected_city_power_income = json["projected_city_power_income"]
        civ.in_decline = json["in_decline"]
        civ.initial_advancement_level = json.get("initial_advancement_level", 0)
        civ.trade_hub_id = json.get("trade_hub_id")

        return civ

    def __repr__(self) -> str:
        return f"<Civ {self.id}: {self.template.name}>"

def create_starting_civ_options_for_players(game_players: list[GamePlayer], starting_locations: list['Hex']) -> dict[int, list[tuple[Civ, 'Hex']]]:
    assert len(game_players) <= 8

    starting_civ_option_jsons = random.sample([civ for civ in list(ANCIENT_CIVS.values()) if civ['advancement_level'] == 0], NUM_STARTING_LOCATION_OPTIONS * len(game_players))

    starting_civ_options = {}

    counter = 0

    for game_player in game_players:
        starting_civ_options[game_player.player_num] = []
        for _ in range(NUM_STARTING_LOCATION_OPTIONS):
            civ = Civ(CivTemplate.from_json(starting_civ_option_jsons[counter]), game_player)
            civ.get_new_tech_choices()
            if civ.has_ability('ExtraCityPower'):
                civ.city_power += civ.numbers_of_ability('ExtraCityPower')[0]

            starting_civ_options[game_player.player_num].append((civ, starting_locations[counter]))
            counter += 1

    return starting_civ_options
