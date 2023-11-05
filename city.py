from typing import Optional
from building import Building
from civ import Civ
from settings import BASE_CITY_HEALTH


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
        self.science = 0
        self.health = BASE_CITY_HEALTH
        self.target: Optional[str] = None
        self.was_occupied_by_civ_id: Optional[str] = None

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
            "science": self.science,
            "health": self.health,
            "was_occupied_by_civ_id": self.was_occupied_by_civ_id,
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
        city.science = json["science"]
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
