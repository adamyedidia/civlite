from random import random
from hex import Hex
from settings import MAP_HOMOGENEITY_LEVEL
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
        hex_to_propagate = random.choice(hexes.values())
        random_neighbor_of_hex = random.choice(hex_to_propagate.get_neighbors(hexes))
        random_neighbor_of_hex.terrain = hex_to_propagate.terrain
        random_neighbor_of_hex.yields = hex_to_propagate.yields.copy()

    return hexes