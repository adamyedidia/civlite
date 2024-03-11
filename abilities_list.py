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
        description=f"Increase {x} yields in {y}s around your second city by {z}.",
        numbers=[x, y, z],
    ),
    "IncreaseYieldsForTerrain": lambda x, y, z: Ability(
        name="IncreaseYieldsForTerrain",
        description=f"When you found or capture a city for the first time, increase {x} yields in {y}s around it by {z}.",
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
    "StartWithResources": lambda x, y: Ability(
        name="StartWithResources",
        description=f"Start the game with {y} {x}.",
        numbers=[x, y],
    ),
}

BUILDING_ABILITIES: dict[str, Callable] = {
    "IncreaseYieldsForTerrain": lambda x, y, z: Ability(
        name="IncreaseYieldsForTerrain",
        description=f"Increase {x} yields in {z}s around the city by {y}.",
        numbers=[x, y, z],
    ),
    "IncreaseYieldsInCity": lambda x, y: Ability(
        name="IncreaseYieldsInCity",
        description=f"Increase {x} yields in the city by {y}.",
        numbers=[x, y],
    ),
    "IncreaseYieldsPerPopulation": lambda x, y: Ability(
        name="IncreaseYieldsPerPopulation",
        description=f"Increase {x} yields per population in the city by {y}.",
        numbers=[x, y],
    ),
    "CityGrowthCostReduction": lambda x: Ability(
        name="CityGrowthCostReduction",
        description=f"Reduce the cost of city growth by {'{:.0%}'.format(x)}.",
        numbers=[x],
    ),
    "IncreaseFocusYieldsPerPopulation": lambda x, y: Ability(
        name="IncreaseFocusYieldsPerPopulation",
        description=f"Increase {x} yields per population in the city with a {x} focus by {y}.",
        numbers=[x, y],
    ),
    "DecreaseFoodDemand": lambda x: Ability(
        name="DecreaseFoodDemand",
        description=f"Decrease food demand by {x}.",
        numbers=[x],
    ),
    "NewUnitsGainBonusStrength": lambda x: Ability(
        name="UnitsHaveExtraStrength",
        description=f"New units you build get +{x} extra strength.",
        numbers=[x],
    ),    
    "GainCityPower": lambda x: Ability(
        name="GainCityPower",
        description=f"Gain {x} city power upon completion.",
        numbers=[x],
    ),
    "GainFreeUnits": lambda x, y: Ability(
        name="GainFreeUnits",
        description=f"Gain {y} free {x} units upon completion.",
        numbers=[x, y],
    ),
    "DoubleYieldsForTerrainInCity": lambda x: Ability(
        name="DoubleYieldsForTerrainInCity",
        description=f"Double yields in {x}s adjacent to and in the city.",
        numbers=[x],
    ),
    "IncreasePopulationOfNewCities": lambda x: Ability(
        name="IncreasePopulationOfNewCities",
        description=f"New cities you build start with an extra {x} population.",
        numbers=[x],
    ),
    "ExistingUnitsGainBonusStrength": lambda x: Ability(
        name="ExistingUnitsGainBonusStrength",
        description=f"All existing units gain +{x} strength.",
        numbers=[x],
    ),
    "ExtraVpsForTechs": lambda x: Ability(
        name="ExtraVpsForTechs",
        description=f"Receive {x} extra VP for each tech you research.",
        numbers=[x],
    ),
    "ExtraVpsForCityGrowth": lambda x: Ability(
        name="ExtraVpsForCityGrowth",
        description=f"Receive {x} VP each time your population grows.",
        numbers=[x],
    ),
    "ExtraVpsForCityCapture": lambda x: Ability(
        name="ExtraVpsForCityCapture",
        description=f"Receive {x} extra VP for each city you capture.",
        numbers=[x],
    ),
    "EndTheGame": lambda: Ability(
        name="EndTheGame",
        description=f"The game ends when this building is completed, and the player with the most victory points wins.",
        numbers=[],
    ),
    "TripleCityPopulation": lambda: Ability(
        name="TripleCityPopulation",
        description=f"Triple the population of the city upon completion.",
        numbers=[],
    ),
}

UNIT_ABILITIES: dict[str, Callable] = {
    "BonusAgainst": lambda x, y: Ability(
        name="BonusAgainst",
        description=f"Has +{y} strength against {x} units.",
        numbers=[x, y],
    ),
    "BonusNextTo": lambda x, y: Ability(
        name="BonusNextTo",
        description=f"Has +{y} strength when next to friendly {x} units.",
        numbers=[x, y],
    ),
    "Splash": lambda x: Ability(
        name="Splash",
        description=f"Deals damage equivalent {'{:.0%}'.format(x)}% of strength to all enemy units adjacent to the target.",
        numbers=[x],
    ),
    "ConvertKills": lambda: Ability(
        name="ConvertKills",
        description=f"Converts killed enemy units into more copies of itself.",
        numbers=[],
    ),
}