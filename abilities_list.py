from typing import Callable

from ability import Ability
import inflect
import math
p = inflect.engine()


ABILITIES: dict[str, Callable] = {}

def make_increase_strength_for_unit_ability(unit_name, strength_increase: int | None = None) -> Ability:
    from unit_templates_list import UNITS  # hackity hack hack
    if strength_increase is None:
        strength_increase = math.ceil(UNITS.by_name(unit_name).strength * 0.25)
    return Ability(
        name="IncreasedStrengthForUnit",
        description=f"{p.plural(unit_name)} you build have +{strength_increase} strength.",
        numbers=[unit_name, strength_increase],
    )

CIV_ABILITIES: dict[str, Callable] = {
    "IncreaseCapitalYields": lambda x, y: Ability(
        name="IncreaseCapitalYields",
        description=f"Increase {x} yields in the capital by {y}.",
        numbers=[x, y],
    ),
    "DevelopCheap": lambda x: Ability(
        name="DevelopCheap",
        description=f"First {dict(urban='Urbanize', rural='Expand', unit='Militarize')[x]} in each city costs half as much.",
        numbers=[x],
    ),
    "OnDevelop": lambda x, y: Ability(
        name="OnDevelop",
        description=f"On {dict(urban='Urbanize', rural='Expand', unit='Militarize')[x.value]}: {y.description}.",
        numbers=[x, y],
    ),
    "IncreaseFocusYields": lambda x, y: Ability(
        name="IncreaseFocusYields",
        description=f"Each city with a {x} focus makes +{y} {x}.",
        numbers=[x, y],
    ),
    "IncreasedStrengthForUnit": make_increase_strength_for_unit_ability,
    "IncreasedStrengthForNthUnit": lambda x, y, z: Ability(
        name="IncreasedStrengthForNthUnit",
        description=f"The {p.ordinal(x)} {y} you build has +{z} strength.",
        numbers=[x, y, z],
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
    "ExtraVpsPerUnitKilled": lambda x, y: Ability(
        name="ExtraVpsPerUnitKilled",
        description=f"Receive {y} extra VP for each unit you kill with a {x} unit." if x is not None else f"Receive {y} extra VP for each unit you kill.",
        numbers=[x, y],
    ),
    "StartWithResources": lambda x, y: Ability(
        name="StartWithResources",
        description=f"Start the game with {y} {x}.",
        numbers=[x, y],
    ),
}

BUILDING_ABILITIES: dict[str, Callable] = {
    "CityGrowthCostReduction": lambda x: Ability(
        name="CityGrowthCostReduction",
        description=f"Reduce the cost of city growth by {'{:.0%}'.format(x)}.",
        numbers=[x],
    ),
    "IncreaseFocusYieldsPerPopulation": lambda resource, amount: Ability(
        name="IncreaseFocusYieldsPerPopulation",
        description=f"Increase {resource} yields per population in the city with a {resource} focus by {amount}. Double this yield if {resource} matches the city center yield.",
        numbers=[resource, amount],
    ),
    "DecreaseFoodDemand": lambda x, y: Ability(
        name="DecreaseFoodDemand",
        description=f"Decrease food demand by {x} in this city" + ("." if y == 0 else f" and {y} in all other cities."),
        numbers=[x, y],
    ),
    "DecreaseFoodDemandPuppets": lambda x: Ability(
        name="DecreaseFoodDemandPuppets",
        description=f"Decrease food demand by {x} for puppet cities.",
        numbers=[x],
    ),
    "ExtraTerritory": lambda: Ability(
        name="ExtraTerritory",
        description=f"+1 maximum territories.",
        numbers=[],
    ),
    "ReducePuppetDistancePenalty": lambda x: Ability(
        name="ReducePuppetDistancePenalty",
        description=f"Reduce travel distance cost for puppet cities to {'{:.0%}'.format(x)} per hex.",
        numbers=[x],
    ),
    "NewUnitsGainBonusStrength": lambda x: Ability(
        name="NewUnitsGainBonusStrength",
        description=f"New units you build get +{x} extra strength.",
        numbers=[x],
    ),    
    "ExtraVpPerAgeOfTechResearched": lambda x: Ability(
        name="ExtraVpPerAgeOfTechResearched",
        description=f"Receive {x} extra VP per age of tech you research.",
        numbers=[x],
    ),
    "ExtraVpsForCityCapture": lambda x: Ability(
        name="ExtraVpsForCityCapture",
        description=f"Receive {x} extra VP for each city you capture.",
        numbers=[x],
    ),
    "UnitsExtraStrengthByTag": lambda x, y: Ability(
        name="UnitsExtraStrengthByTag",
        description=f"New {x.value} units get +{y} strength",
        numbers=[x, y],
    ),
    "UnitsExtraStrengthByAge": lambda x, y: Ability(
        name="UnitsExtraStrengthByAge",
        description=f"New units of age {x} or later get +{y} strength",
        numbers=[x, y],
    ),
    "Airforce": lambda x, y: Ability(
        name="Airforce",
        description=f"Gives +{x} strength to battles within range {y}.",
        numbers=[x, y],
    ),
    "DeploymentCenter": lambda: Ability(
        name="Deployment Center",
        description=f"Units built by this city will be built at the location of your primary flag rather than the city.",
        numbers=[],
    ),
    "CityPowerPerKill": lambda x: Ability(
        name="CityPowerPerKill",
        description=f"Gain {x} city power for each enemy unit you kill.",
        numbers=[x],
    ),
    "DecreaseVitalityDecayPerAdjacentOcean": lambda x: Ability(
        name="DecreaseVitalityDecayPerAdjacentOcean",
        description=f"Decrease vitality decay rate by {x:.1%} percentage points per adjacent ocean tile.",
        numbers=[x],
    ),
}

UNIT_ABILITIES: dict[str, Callable] = {
    "BonusAgainst": lambda tag: Ability(
        name="BonusAgainst",
        description=f"Bonus vs {tag} (+50%).",
        numbers=[tag],
    ),
    "DoubleBonusAgainst": lambda tag: Ability(
        name="DoubleBonusAgainst",
        description=f"Double bonus vs {tag} (+100%).",
        numbers=[tag],
    ),
    "BonusNextTo": lambda tag: Ability(
        name="BonusNextTo",
        description=f"Bonus next to friendly {tag} (+50%).",
        numbers=[tag],
    ),
    "Splash": lambda x: Ability(
        name="Splash",
        description=f"Splash: Also attacks adjacent enemies at {'{:.0%}'.format(x)} strength.",
        numbers=[x],
    ),
    "ConvertKills": lambda: Ability(
        name="ConvertKills",
        description=f"Converts killed enemy units into more copies of itself.",
        numbers=[],
    ),
    "HealAllies": lambda: Ability(
        name="HealAllies",
        description=f"Heal all adjacent allies after moving (non wondrous).",
        numbers=[],
    ),
    "MultipleAttack": lambda x: Ability(
        name="MultipleAttack",
        description=f"Attack {x} times per turn.",
        numbers=[x],
    ),
    "Missile": lambda: Ability(
        name="Missile",
        description=f"Dies after attacking.",
        numbers=[],
    ),
}
