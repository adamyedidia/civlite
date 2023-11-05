from city import City
from hex import Hex
from unit import Unit
import random


def get_all_units(hexes: dict[str, Hex]) -> list[Unit]:
    units = []
    for hex in hexes.values():
        units.extend(hex.units)
    return units


def get_all_cities(hexes: dict[str, Hex]) -> list[City]:
    cities = []
    for hex in hexes.values():
        if hex.city:
            cities.append(hex.city)
    return cities


class GameState:
    def __init__(self, hexes: dict[str, Hex]):
        self.hexes = hexes
        self.units = get_all_units(hexes)
        self.cities = get_all_cities(hexes)

    def to_json(self) -> dict:
        return {
            "hexes": {key: hex.to_json() for key, hex in self.hexes.items()},
        }
    
    @staticmethod
    def from_json(json: dict) -> "GameState":
        hexes = {key: Hex.from_json(hex_json) for key, hex_json in json["hexes"].items()}
        return GameState(hexes=hexes)
    
    def roll_turn(self) -> None:
        units_copy = self.units[:]
        random.shuffle(units_copy)
        for unit in units_copy:
            unit.act()
