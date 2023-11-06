from typing import TYPE_CHECKING, Optional, Union
from building import Building
from building_template import BuildingTemplate
from civ import Civ
from settings import BASE_CITY_HEALTH
from unit import Unit
from unit_template import UnitTemplate

if TYPE_CHECKING:
    from hex import Hex
    from game_state import GameState


class City:
    def __init__(self, civ: Civ):
        self.civ = civ
        self.original_civ_id = civ.id
        self.name = generate_random_city_name()
        self.population = 1
        self.buildings: list[Building] = []
        self.food = 0
        self.metal = 0
        self.wood = 0
        self.focus = 'food'
        self.health = BASE_CITY_HEALTH
        self.target: Optional['Hex'] = None
        self.was_occupied_by_civ_id: Optional[str] = None
        self.hex: Optional['Hex'] = None
        self.autobuild_unit: Optional[UnitTemplate] = None
        self.units_queue: list[UnitTemplate] = []
        self.buildings_queue: list[Union[UnitTemplate, BuildingTemplate]] = []

    def harvest_yields(self, game_state: 'GameState') -> None:
        if self.hex is None:
            return

        for hex in [self.hex, *self.hex.get_neighbors(game_state.hexes)]:
            self.food += hex.yields.food
            self.metal += hex.yields.metal
            self.wood += hex.yields.wood
            self.civ.science += hex.yields.science
        
        self.civ.science += self.population
        self.food += 2

        if self.focus == 'food':
            self.food += self.population
        elif self.focus == 'metal':
            self.metal += self.population
        elif self.focus == 'wood':
            self.wood += self.population
        elif self.focus == 'science':
            self.civ.science += self.population

    def roll_turn(self, sess, game_state: 'GameState') -> None:
        self.harvest_yields(game_state)
        self.build_units(sess, game_state)
        self.build_buildings(sess, game_state)

    def build_units(self, sess, game_state: 'GameState') -> None:
        if self.autobuild_unit is not None:
            while self.metal >= self.autobuild_unit.metal_cost:
                if self.build_unit(sess, game_state, self.autobuild_unit):
                    self.metal -= self.autobuild_unit.metal_cost
                else: 
                    break
        else:
            while self.units_queue and self.metal >= self.units_queue[0].metal_cost:
                unit = self.units_queue[0]
                if self.metal >= unit.metal_cost:
                    self.units_queue.pop(0)
                    self.build_unit(sess, game_state, unit)

    def build_unit(self, sess, game_state: 'GameState', unit: UnitTemplate) -> bool:
        if not self.hex:
            return False

        if not self.hex.is_occupied(unit.type):
            self.spawn_unit_on_hex(sess, game_state, unit, self.hex)
            return True

        best_hex = None
        best_hex_distance_from_target = 10000

        for hex in self.hex.get_neighbors(game_state.hexes):
            if not hex.is_occupied(unit.type):
                distance_from_target = hex.distance_to(self.target or self.hex)
                if distance_from_target < best_hex_distance_from_target:
                    best_hex = hex
                    best_hex_distance_from_target = distance_from_target

        if best_hex is None:
            for hex in self.hex.get_distance_2_hexes(game_state.hexes):
                if not hex.is_occupied(unit.type):
                    distance_from_target = hex.distance_to(self.target or self.hex)
                    if distance_from_target < best_hex_distance_from_target:
                        best_hex = hex
                        best_hex_distance_from_target = distance_from_target            

        if best_hex is None:
            return False
        self.spawn_unit_on_hex(sess, game_state, unit, best_hex)
        return True

    def spawn_unit_on_hex(self, sess, game_state: 'GameState', unit_template: UnitTemplate, hex: 'Hex') -> None:
        if self.hex is None:
            return
        unit = Unit(unit_template, self.civ)
        unit.hex = hex
        hex.units.append(unit)
        game_state.units.append(unit)
        if self.hex.coords != unit.hex.coords:
            game_state.add_animation_frame_for_civ(sess, {
                "type": "UnitSpawn",
                "start_coords": self.hex.coords,
                "end_coords": unit.hex.coords,
            }, self.civ)

    def build_buildings(self, sess, game_state: 'GameState') -> None:
        while self.buildings_queue:
            building = self.buildings_queue[0]
            if isinstance(building, BuildingTemplate):
                if self.wood >= building.cost:
                    self.buildings_queue.pop(0)
                    self.build_building(sess, game_state, building)
                else:
                    break

            elif isinstance(building, UnitTemplate):
                if self.wood >= building.wood_cost:
                    self.buildings_queue.pop(0)
                    self.build_building(sess, game_state, building)
                else:
                    break

            else:
                break

    def build_building(self, sess, game_state: 'GameState', building: Union[BuildingTemplate, UnitTemplate]) -> None:
        unit_template = building if isinstance(building, UnitTemplate) else None
        building_template = building if isinstance(building, BuildingTemplate) else None

        self.buildings.append(Building(unit_template=unit_template, building_template=building_template))


    def to_json(self) -> dict:
        return {
            "civ": self.civ.to_json(),
            "original_civ_id": self.original_civ_id,
            "name": self.name,
            "population": self.population,
            "buildings": [building.to_json() for building in self.buildings],
            "food": self.food,
            "metal": self.metal,
            "wood": self.wood,
            "health": self.health,
            "was_occupied_by_civ_id": self.was_occupied_by_civ_id,
            "hex": self.hex.coords if self.hex else None,
            "autobuild_unit": self.autobuild_unit.name if self.autobuild_unit else None,
        }

    @staticmethod
    def from_json(json: dict) -> "City":
        city = City(
            civ=Civ.from_json(json["civ"]),
        )
        city.original_civ_id = json["original_civ_id"]
        city.name = json["name"]
        city.population = json["population"]
        city.buildings = [Building.from_json(building) for building in json["buildings"]]
        city.food = json["food"]
        city.metal = json["metal"]
        city.wood = json["wood"]
        city.health = json["health"]
        city.was_occupied_by_civ_id = json["was_occupied_by_civ_id"]

        return city


CITY_NAMES = [
    "Miami",
    "Lothlorien",
    "Leningrad",
    "Los Angeles",
    "Tikal",
    "Karakorum",
    "Khartoum",
    "Ravnica",
    "Tokyo",
    "Delhi",
    "Berkeley",
    "Munich",
    "Qarth",
    "Cuzco",
    "Meereen",
    "New Capenna",
    "The Hive",
    "Nairobi",
    "Barcelona",
    "Toronto",
    "Coruscant",
    "Zigatvar",
    "Wuhan",
    "Cape Town",
    "Tel Aviv",
    "Sunspear",
    "Moscow",
    "Osgiliath",
    "Oldtown",
    "Bern",
    "Lannisport",
    "Nineveh",
    "Atlanta",
    "Tehran",
    "Aleppo",
    "Pune",
    "Oslo",
    "Tijuana",
    "Palenque",
    "Myr",
    "Santiago",
    "Uskdarler",
    "Mos Eisley",
    "Caemlyn",
    "Riga",
    "Nimrud",
    "White Harbor",
    "Dublin",
    "Theed",
    "Venice",
    "Tar Valon",
    "Calgary",
    "Kaposvar",
    "Lagos",
    "Pyongyang",
    "Sarvahr",
    "Marseilles",
    "Ankara",
    "Montreal",
    "Noah's Rainbow",
    "Arrakeen",
    "Chichen Itza",
    "Nassau",
    "Hong Kong",
    "Baikonur",
    "Bunker 118",
    "Braavos",
    "Dardogar",
    "New Jericho",
    "Jimboomba",
    "Winterfell",
    "Chongqing",
    "Tenochtitlan",
    "Jakarta",
    "Temesvar",
    "Kistel",
    "Cairo",
    "Addis Ababa",
    "Riyadh",
    "Kinshasa",
    "Almaty",
    "Merv",
    "Boston",
    "Wakanda",
    "Carthag",
    "Zirc",
    "Caracas",
    "Havana",
    "Ingulath",
    "New York",
    "Budapest",
    "Buenos Aires",
    "Bogota",
    "Lima",
    "Sao Paulo",
    "Mexico City",
    "Bangkok",
    "Manila",
    "Kuala Lumpur",
    "Singapore",
    "Hanoi",
    "Luanda",
    "Mombasa",
    "Kigali",
    "Sydney",
    "Shanghai",
    "Beijing",
]


def generate_random_city_name() -> str:
    return "City"
