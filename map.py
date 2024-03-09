import random
from typing import Optional
from hex import Hex
from settings import MAP_HOMOGENEITY_LEVEL, PER_PLAYER_AREA, GOOD_HEX_PROBABILITY
from utils import coords_str, get_all_coords_up_to_n
from yields import Yields

TERRAIN_CHANCES: dict[str, float] = {
    "plains": 0.15,
    "forest": 0.15,
    "hills": 0.15,
    "grassland": 0.15,
    "desert": 0.08,
    "jungle": 0.08,
    "mountain": 0.08,
    "tundra": 0.08,
    "marsh": 0.08,
}

TERRAIN_TO_YIELDS: dict[str, Yields] = {
    "plains": Yields(food=1, metal=1, wood=0, science=0),
    "forest": Yields(food=0, metal=0, wood=2, science=0),
    "hills": Yields(food=0, metal=1, wood=1, science=0),
    "grassland": Yields(food=2, metal=0, wood=0, science=0),
    "desert": Yields(food=0, metal=1, wood=0, science=1),
    "jungle": Yields(food=1, metal=0, wood=1, science=0),
    "mountain": Yields(food=0, metal=2, wood=0, science=0),
    "tundra": Yields(food=0, metal=0, wood=1, science=1),
    "marsh": Yields(food=1, metal=0, wood=0, science=1),
}


def infer_map_size_from_num_players(num_players: int) -> int:
    for map_size in range(100):
        num_hexes_for_map_size = 3 * map_size * (map_size - 1) + 1

        if num_hexes_for_map_size >= num_players * PER_PLAYER_AREA:
            return map_size

    raise Exception('Uh oh')


def pick_random_terrain() -> str:
    terrain = random.choices(list(TERRAIN_CHANCES.keys()), list(TERRAIN_CHANCES.values()))[0]
    return terrain


def create_hex_map(map_size: int) -> dict[str, Hex]:
    coords = get_all_coords_up_to_n(map_size)

    hexes: dict[str, Hex] = {}

    for q, r, s in coords:
        terrain = pick_random_terrain()
        hexes[coords_str((q, r, s))] = Hex(q, r, s, terrain, TERRAIN_TO_YIELDS[terrain].copy())

    for _ in range(MAP_HOMOGENEITY_LEVEL):
        hex_to_propagate = random.choice(list(hexes.values()))
        random_neighbor_of_hex = random.choice(hex_to_propagate.get_neighbors(hexes))
        random_neighbor_of_hex.terrain = hex_to_propagate.terrain
        random_neighbor_of_hex.yields = hex_to_propagate.yields.copy()

    for hex in hexes.values():
        if random.random() < GOOD_HEX_PROBABILITY:
            hex.yields.food *= 2
            hex.yields.wood *= 2
            hex.yields.metal *= 2
            hex.yields.science *= 2

    return hexes


def generate_starting_locations(hexes: dict[str, Hex], n: int) -> list[Hex]:

    starting_locations = []

    while len(starting_locations) < n:
        starting_location = random.choice(list(hexes.values()))

        if len(starting_location.get_neighbors(hexes)) >= 6:
            too_close = False

            for other_starting_location in starting_locations:
                if other_starting_location.distance_to(starting_location) < 3:
                    too_close = True
                    break
            
            if not too_close:
                starting_locations.append(starting_location)

    return starting_locations


def is_valid_decline_location(decline_location: Hex, hexes: dict[str, Hex], other_decline_locations: list[Hex]) -> bool:
    # print(f"Considering decline at {decline_location.coords}. {[hex.city is not None for hex in decline_location.get_neighbors(hexes)]}")
    # Don't choose a spot with a city or an active player's units nearby
    if decline_location.city is not None: 
        return False
    if any([unit.civ.game_player for unit in decline_location.units]):
        return False
    for hex in decline_location.get_neighbors(hexes):
        if hex.city is not None:
            return False
        if any(hex.is_foundable_by_civ.values()):
            return False
        if any([unit.civ.game_player for unit in hex.units]):
            return False

    for other_decline_location in other_decline_locations:
        # print(f"Distance to other is {other_decline_location.distance_to(decline_location)}")
        if other_decline_location.distance_to(decline_location) < 3:
            return False

    return True


def generate_decline_locations(hexes: dict[str, Hex], n: int, existing_decline_locations: list[Hex] = []) -> list[Hex]:
    """
    Generate n new decline locations that don't collide with the existing ones.
    """
    decline_locations = []

    num_attempts = 0

    while len(decline_locations) < n and num_attempts < 1000:
        print(num_attempts, n, len(decline_locations))
        decline_location = random.choice(list(hexes.values()))

        if is_valid_decline_location(decline_location, hexes, existing_decline_locations + decline_locations):
            decline_locations.append(decline_location)
        
        num_attempts += 1

    return decline_locations
