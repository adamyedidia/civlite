from typing import Callable

from ability import Ability


ABILITIES: dict[str, Callable] = {}

CIV_ABILITIES: dict[str, Callable] = {}

BUILDING_ABILITIES: dict[str, Callable] = {
    "IncreaseYieldsForTerrain": lambda x, y, z: Ability(
        name="IncreaseYieldsForTerrain",
        description=f"Increase {x} yields in {y}s by {z}.",
        numbers=[x, y, z],
    )
}