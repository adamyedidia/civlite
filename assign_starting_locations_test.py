import numpy as np
import pytest

from assign_starting_locations import assign_starting_locations
from civ_template import CivTemplate
from region import Region
from hex import Hex
from terrain_templates_list import TERRAINS
from yields import Yields

# Use arbitrary values from the Region enum for testing
regionA, regionB, regionC = list(Region)[:3]

# Create dummy hex class for testing
def hex(q, r, s) -> Hex:
    return Hex(q, r, s, TERRAINS.HILLS, Yields())

# Create dummy civ templates for testing
def create_dummy_civ_templates(nums: list[int]) -> list[CivTemplate]:
    result = []
    for region, num in zip([regionA, regionB, regionC], nums):
        result.extend([CivTemplate(name=f"civ_{region.name}_num{i}", abilities=[], advancement_level=0, region=region) for i in range(num)])
    return result

class TestAssignStartingLocations:
    def test_assign_starting_locations(self):
        np.random.seed(0)
        civs = create_dummy_civ_templates([1, 2, 3])
        locations = [
            hex(0, 0, 0),
            hex(-1, -1, 2),
            hex(1, 0, -1),
            hex(1, -2, 1),
            hex(-2, 0, 2),
            hex(-1, -2, 3),
        ]
        starting_locations = assign_starting_locations(civs, locations)
        print(starting_locations)