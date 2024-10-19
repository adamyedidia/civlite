from collections import defaultdict
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from civ_template import CivTemplate
    from hex import Hex
    from region import Region

def _calc_distances(arr1, arr2) -> np.ndarray:
    # arr1 is [I, K]; arr2 is [J, K]
    # returns [I, J]
    # where value at i,j is max(abs(arr1[i,k] - arr2[j,k])) over k
    assert arr1.ndim == 2
    assert arr2.ndim == 2
    assert arr1.shape[1] == arr2.shape[1]

    return np.max(np.abs(arr1[:, np.newaxis] - arr2), axis=2)

def assign_starting_locations(starting_civ_template_options: 'list[CivTemplate]', starting_locations: 'list[Hex]', retries: int = 100) -> 'dict[CivTemplate, Hex]':
    """
    A waaaay too complicated function to assign starting locations to civs
    in a way that keeps civs of the same region close to each other.
    """
    assert len(starting_civ_template_options) == len(starting_locations)
    if retries == 0:
        raise ValueError("Failed to assign starting locations")
    np.random.seed(retries)
    by_region: 'dict[Region, list[CivTemplate]]' = defaultdict(list)
    for civ in starting_civ_template_options:
        by_region[civ.region].append(civ)
    
    num_regions = len(by_region)
    regions_by_size = sorted(by_region.keys(), key=lambda r: len(by_region[r]))

    starting_locations_array = np.array([[h.q, h.r, h.s] for h in starting_locations])
    # Sample indices from the range of the number of rows in starting_locations_array
    sampled_indices = np.random.choice(starting_locations_array.shape[0], len(by_region), replace=False)
    # Use the sampled indices to select rows from starting_locations_array
    zone_centers = starting_locations_array[sampled_indices]

    distances = _calc_distances(starting_locations_array, zone_centers)
    zone_assignments = np.argmin(distances, axis=1)
    zone_sizes = np.bincount(zone_assignments)
    zones_by_size = np.argsort(zone_sizes)
    regions_by_zone_dic = {zones_by_size[z]: regions_by_size[z] for z in range(num_regions)}
    regions_by_zone = [regions_by_zone_dic[z] for z in range(num_regions)]
    # print(f"{by_region=}\n{zone_centers=}\n{distances=}\n{zone_assignments=}\n{zone_sizes=}\n{zones_by_size=}\n{regions_by_zone=}")
    # Now we have a first approximate assignment of regions to zones
    # But the sizes aren't quite right, need to move some around.

    # First lets recenter the zones.
    zone_centers = np.array([
        np.mean(starting_locations_array[zone_assignments == z, :], axis=0)
        for z in range(num_regions)
    ])
    distances = _calc_distances(starting_locations_array, zone_centers)
    # print(f"{distances=}")

    zone_zone_distance = _calc_distances(zone_centers, zone_centers)
    # print(f"{zone_zone_distance=}")

    success = False
    for iter in range(100):
        # print(f"====== Iteration {iter} ======")
        zone_sizes = np.bincount(zone_assignments)
        zone_excesses = np.array([zone_size - len(by_region[regions_by_zone[z]]) for z, zone_size in enumerate(zone_sizes)])
        # print(f"{zone_excesses=}")
        if all(zone_excesses == 0):
            success = True
            break
        zone_zone_distance[:, zone_excesses >= 0] = np.inf
        distance_to_lacking_zone = np.min(zone_zone_distance, axis=1)
        # print(f"{distance_to_lacking_zone=}")

        masked_distances = distances.copy()
        masked_distances[np.arange(len(zone_assignments)), zone_assignments] = np.inf
        # print(f"{masked_distances=}")
        # break ties with distance_to_lacking_zone
        second_best_zones = np.argmin(masked_distances + 1e-6 * distance_to_lacking_zone, axis=1)
        # print(f"{second_best_zones=}")
        switching_costs = distances[np.arange(len(zone_assignments)), second_best_zones] - distances[np.arange(len(zone_assignments)), zone_assignments]
        # print(f"{switching_costs=}")

        # Only move if closer to a lacking zone.
        movable_mask = distance_to_lacking_zone[zone_assignments] > distance_to_lacking_zone[second_best_zones]
        # print(f"{movable_mask=}")

        # Finally, don't move more than excesses out of any one region
        for z in range(num_regions):
            movable_location_indices_in_zone = np.where(np.logical_and(zone_assignments == z, movable_mask))[0]
            movable_location_indices_in_zone = sorted(movable_location_indices_in_zone, key=lambda i: float(switching_costs[i]), reverse=True)
            # print(f"z{z}:{movable_location_indices_in_zone=}")
            if len(movable_location_indices_in_zone) > zone_excesses[z]:
                moving_too_many = movable_location_indices_in_zone[zone_excesses[z]:]
                # print(f"moving_too_many: {moving_too_many=}")
                movable_mask[moving_too_many] = False
        # print(f"{movable_mask=}")
        if not np.any(movable_mask):
            # print("=!=!=!=!=!=!= No movable locations =!=!=!=!=!=!= ")
            return assign_starting_locations(starting_civ_template_options, starting_locations, retries=retries-1)
        # print(f"{movable_mask=}")

        zone_assignments[movable_mask] = second_best_zones[movable_mask]
    
    if not success:
        # print("=!=!=!=!=!=!= ASSIGNMENT FAILED; RETRYING =!=!=!=!=!=!= ")
        return assign_starting_locations(starting_civ_template_options, starting_locations, retries=retries-1)
    # Now we have a good assignment with no excesses.
    # Just need to massage the data type from zone_assignments to the dict we need to return.
    assignment = {}
    region_counters = {r: 0 for r in regions_by_size}
    for location_idx, zone in enumerate(zone_assignments):
        region = regions_by_zone[zone]
        civ = by_region[region][region_counters[region]]
        region_counters[region] += 1
        assignment[civ] = starting_locations[location_idx]
    # print(f"{assignment=}")
    return assignment
