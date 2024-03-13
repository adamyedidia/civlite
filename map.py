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


def is_valid_decline_location(decline_location: Hex, hexes: dict[str, Hex], other_decline_locations: list[Hex]) -> bool:
    # Don't choose a spot with a city or an active player's units nearby
    if decline_location.city is not None: 
        return False
    # Don't use spaces with units
    if any([unit.civ.game_player for unit in decline_location.units]):
        return False
    for hex in decline_location.get_neighbors(hexes):
        # Can't be next to a city.
        if hex.city is not None:
            return False
        # Can't be next to a potential city
        if any(hex.is_foundable_by_civ.values()):
            return False
        # Can't be next to an active player's unit. That would be weird.
        if any([unit.civ.game_player for unit in hex.units]):
            return False
        
    print(decline_location.get_distance_2_hexes(hexes))
    for hex in decline_location.get_distance_2_hexes(hexes):
        # Can't be within 2 of an existing city.
        if hex.city is not None:
            return False
    
    # Don't use the edge of the map.
    if len([hex for hex in decline_location.get_neighbors(hexes)]) < 6:
        return False

    # Stay at least 3 from other fresh sites.
    for other_decline_location in other_decline_locations:
        if other_decline_location.distance_to(decline_location) < 3:
            return False

    return True


def sample_weight(q, r, s) -> float:
    radius: int = max(abs(q), abs(r), abs(s))
    return 0.3 ** (radius)

def generate_decline_locations(hexes: dict[str, Hex], n: int, existing_decline_locations: list[Hex] = []) -> list[Hex]:
    """
    Generate n new decline locations that don't collide with the existing ones.
    """
    decline_locations: list[Hex] = []

    hexes_list: list[Hex] = list(hexes.values())
    weights: list[float] = [sample_weight(hex.q, hex.r, hex.s) for hex in hexes_list]

    while len(decline_locations) < n and len(hexes_list) > 0:
        decline_location: Hex = random.choices(hexes_list, weights=weights)[0]
        if is_valid_decline_location(decline_location, hexes, existing_decline_locations + decline_locations):
            decline_locations.append(decline_location)
        
        idx: int = hexes_list.index(decline_location)
        hexes_list.pop(idx)
        weights.pop(idx)

    return decline_locations
