import random
from civ_templates_list import CIVS
from terrain_template import TerrainTemplate
from terrain_templates_list import TERRAINS
from hex import Hex
from settings import MAP_HOMOGENEITY_LEVEL, PER_PLAYER_AREA_MIN, PER_PLAYER_AREA_MAX, GOOD_HEX_PROBABILITY
from utils import coords_str, get_all_coords_up_to_n
from logging_setup import logger


def infer_map_size_from_num_players(num_players: int) -> int:
    for map_size in range(100):
        num_hexes_for_map_size = 3 * map_size * (map_size - 1) + 1

        if num_hexes_for_map_size >= num_players * PER_PLAYER_AREA_MAX:
            return map_size

    raise Exception('Uh oh')


def _pick_random_terrain() -> TerrainTemplate:
    all_terrains = list(TERRAINS.all())
    terrain = random.choices(all_terrains, weights=[terrain.frequency for terrain in all_terrains]).pop()
    return terrain

def _hex_has_opposite_land_neighbors(hex: Hex, hexes: dict[str, Hex]) -> bool:
    for offset_pair in [((1, -1, 0), (-1, 1, 0)), ((1, 0, -1), (-1, 0, 1)), ((0, 1, -1), (0, -1, 1))]:
        terrains = [neighbor.terrain for neighbor in hex.hexes_at_offsets(offset_pair, hexes)]
        if all(terrain != TERRAINS.OCEAN for terrain in terrains):
            return True
    return False

def create_hex_map(num_players: int) -> dict[str, Hex]:
    map_size = infer_map_size_from_num_players(num_players)
    total_hexes = map_size * (map_size - 1) * 3 + 1
    target_hexes = random.randint(num_players * PER_PLAYER_AREA_MIN, num_players * PER_PLAYER_AREA_MAX)
    excess_hexes = total_hexes - target_hexes
    logger.info(f"Creating map with {target_hexes} land hexes by making a map of size {map_size} ({total_hexes} hexes) and removing {excess_hexes} excess hexes")
    return _create_hex_map(map_size, num_ocean_bites=excess_hexes)

def _create_hex_map(map_size: int, num_ocean_bites: int) -> dict[str, Hex]:
    coords = get_all_coords_up_to_n(map_size)

    hexes: dict[str, Hex] = {}

    for q, r, s in coords:
        if max(abs(q), abs(r), abs(s)) > map_size - 1:
            terrain = TERRAINS.OCEAN
        else:
            terrain = _pick_random_terrain()
        hexes[coords_str((q, r, s))] = Hex(q, r, s, terrain, terrain.yields.copy())

    random_ordered_hexes = list(hexes.values())
    random.shuffle(random_ordered_hexes)
    for _ in range(num_ocean_bites):
        for hex in random_ordered_hexes:
            if hex.terrain != TERRAINS.OCEAN and not _hex_has_opposite_land_neighbors(hex, hexes):
                hex.terrain = TERRAINS.OCEAN
                hex.yields = TERRAINS.OCEAN.yields.copy()
                break

    land_hexes = [hex for hex in hexes.values() if hex.terrain != TERRAINS.OCEAN]

    for _ in range(int(MAP_HOMOGENEITY_LEVEL * len(land_hexes))):
        hex_to_propagate = random.choice(land_hexes)
        random_neighbor_of_hex = random.choice(list(hex_to_propagate.get_neighbors(hexes, exclude_ocean=True)))
        random_neighbor_of_hex.terrain = hex_to_propagate.terrain
        random_neighbor_of_hex.yields = hex_to_propagate.yields.copy()

    for hex in hexes.values():
        if random.random() < GOOD_HEX_PROBABILITY:
            hex.yields = hex.terrain.bonus_yields.copy()

    for coords, hex in list(hexes.items()):
        if all(neighbor.terrain == TERRAINS.OCEAN for neighbor in hex.get_neighbors(hexes)):
            del hexes[coords]

    return hexes


def generate_starting_locations(hexes: dict[str, Hex], n: int) -> list[Hex]:

    starting_locations = []

    while len(starting_locations) < n:
        starting_location = random.choice(list(hexes.values()))

        if len(list(starting_location.get_neighbors(hexes))) >= 6 and starting_location.terrain != TERRAINS.OCEAN:
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
    if decline_location.terrain == TERRAINS.OCEAN:
        return False
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
