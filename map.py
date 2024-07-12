import random
from civ_templates_list import CIVS
from terrain_template import TerrainTemplate
from terrain_templates_list import TERRAINS
from hex import Hex
from settings import MAP_HOMOGENEITY_LEVEL, PER_PLAYER_AREA, GOOD_HEX_PROBABILITY
from utils import coords_str, get_all_coords_up_to_n
from yields import Yields

def infer_map_size_from_num_players(num_players: int) -> int:
    for map_size in range(100):
        num_hexes_for_map_size = 3 * map_size * (map_size - 1) + 1

        if num_hexes_for_map_size >= num_players * PER_PLAYER_AREA:
            return map_size

    raise Exception('Uh oh')


def _pick_random_terrain() -> TerrainTemplate:
    all_terrains = list(TERRAINS.all())
    terrain = random.choices(all_terrains, weights=[terrain.frequency for terrain in all_terrains]).pop()
    return terrain


def create_hex_map(map_size: int) -> dict[str, Hex]:
    coords = get_all_coords_up_to_n(map_size)

    hexes: dict[str, Hex] = {}

    for q, r, s in coords:
        terrain = _pick_random_terrain()
        hexes[coords_str((q, r, s))] = Hex(q, r, s, terrain, terrain.yields.copy())

    for _ in range(int(MAP_HOMOGENEITY_LEVEL * len(coords))):
        hex_to_propagate = random.choice(list(hexes.values()))
        random_neighbor_of_hex = random.choice(list(hex_to_propagate.get_neighbors(hexes)))
        random_neighbor_of_hex.terrain = hex_to_propagate.terrain
        random_neighbor_of_hex.yields = hex_to_propagate.yields.copy()

    for hex in hexes.values():
        if random.random() < GOOD_HEX_PROBABILITY:
            hex.yields = hex.terrain.bonus_yields.copy()



    return hexes


def generate_starting_locations(hexes: dict[str, Hex], n: int) -> list[Hex]:

    starting_locations = []

    while len(starting_locations) < n:
        starting_location = random.choice(list(hexes.values()))

        if len(list(starting_location.get_neighbors(hexes))) >= 6:
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
    if any([unit.civ.template != CIVS.BARBARIAN for unit in decline_location.units]):
        return False
    for hex in decline_location.get_neighbors(hexes):
        if hex.city is not None:
            return False
        if any(hex.is_foundable_by_civ.values()):
            return False
        if any([unit.civ.game_player for unit in hex.units]):
            return False
    if len(list(decline_location.get_neighbors(hexes))) < 6:
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
        decline_location = random.choice(list(hexes.values()))

        if is_valid_decline_location(decline_location, hexes, existing_decline_locations + decline_locations):
            decline_locations.append(decline_location)
        
        num_attempts += 1

    return decline_locations
