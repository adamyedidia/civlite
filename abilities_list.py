from typing import Callable

from ability import Ability


ABILITIES: dict[str, Callable] = {}

CIV_ABILITIES: dict[str, Callable] = {
    "IncreaseCapitalYields": lambda x, y: Ability(
        name="IncreaseCapitalYields",
        description=f"Increase {x} yields in the capital by {y}.",
        numbers=[x, y],
    ),
    "IncreaseFocusYields": lambda x, y: Ability(
        name="IncreaseFocusYields",
        description=f"Each city with a {x} focus makes +{y} {x}.",
        numbers=[x, y],
    ),
    "IncreaseYieldsForTerrainNextToSecondCity": lambda x, y, z: Ability(
        name="IncreaseYieldsForTerrainNextToSecondCity",
        description=f"Increase {x} yields in {y}s next to your second city by {z}.",
        numbers=[x, y, z],
    ),
    "IncreaseYieldsForTerrain": lambda x, y, z: Ability(
        name="IncreaseYieldsForTerrain",
        description=f"Increase {x} yields in {y}s next to each city by {z}.",
        numbers=[x, y, z],
    ),
    "IncreasedStrengthForUnit": lambda x, y: Ability(
        name="IncreasedStrengthForUnit",
        description=f"{x}s you build have +{y} strength.",
        numbers=[x, y],
    ),
    "ExtraVpsPerWonder": lambda x: Ability(
        name="ExtraVpsPerWonder",
        description=f"Receive {x} extra VP for each wonder you build.",
        numbers=[x],
    ),
    "ExtraCityPower": lambda x: Ability(
        name="ExtraCityPower",
        description=f"At the start of the game, gain {x} city power.",
        numbers=[x],
    ),
    "ExtraVpsPerCityCaptured": lambda x: Ability(
        name="ExtraVpsPerCityCaptured",
        description=f"Receive {x} extra VP for each city you capture.",
        numbers=[x],
    ),
    "ExtraVpsPerUnitKilled": lambda x: Ability(
        name="ExtraVpsPerUnitKilled",
        description=f"Receive {x} extra VP for each unit you kill.",
        numbers=[x],
    ),
}

BUILDING_ABILITIES: dict[str, Callable] = {
    "IncreaseYieldsForTerrain": lambda x, y, z: Ability(
        name="IncreaseYieldsForTerrain",
        description=f"Increase {x} yields in {y}s by {z}.",
        numbers=[x, y, z],
    )
}