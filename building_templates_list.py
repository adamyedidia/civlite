from typing import Generator
from building_template import BuildingTemplate, BuildingType
from terrain_templates_list import TERRAINS
from effects_list import BuildEachUnitEffect, GainResourceEffect, GainUnhappinessEffect, GrowEffect, ResetHappinessThisCityEffect
from tech_templates_list import TECHS
from unit_template import UnitTag
from yields import ConstantYields, Yields, YieldsIncreaseTownCenter, YieldsPerBuildingType, YieldsPerPopulation, YieldsPerTerrainType, YieldsPerUniqueTerrainType

class BUILDINGS():
    LUMBER_MILL = BuildingTemplate(
        name="Lumber Mill",
        type=BuildingType.RURAL,
        cost=5,
        calculate_yields=YieldsPerTerrainType(TERRAINS.FOREST, Yields(wood=1)),
        prereq=TECHS.FORESTRY,
    )
    TRAINING_GROUNDS = BuildingTemplate(
        name="Training Grounds",
        type=BuildingType.RURAL,
        cost=15,
        prereq=TECHS.FORESTRY,
        abilities=[{
            "name": "UnitsExtraStrengthByAge",
            "numbers": [1, 1],
        }],
    )
    SLAVE_TRADE = BuildingTemplate(
        name="Slave Trade",
        type=BuildingType.URBAN,
        cost=1,
        prereq=TECHS.BRONZE_WORKING,
        on_build=[GainResourceEffect("wood", 30), GainUnhappinessEffect(20)],
    )
    PASTURE = BuildingTemplate(
        name="Pasture",
        type=BuildingType.RURAL,
        cost=15,
        prereq=TECHS.IRRIGATION,
        abilities=[{
            "name": "UnitsExtraStrengthByTag",
            "numbers": [UnitTag.MOUNTED, 1],
        }],
    )
    GRANARY = BuildingTemplate(
        name="Granary",
        type=BuildingType.RURAL,
        cost=5,
        calculate_yields=YieldsPerTerrainType(TERRAINS.PLAINS, Yields(food=1)),
        prereq=TECHS.POTTERY,
    )
    ROADS = BuildingTemplate(
        name="Roads",
        type=BuildingType.RURAL,
        cost=10,
        abilities=[{
            "name": "ReducePuppetDistancePenalty",
            "numbers": [0.05],
        }],
        prereq=TECHS.THE_WHEEL,
    )
    LIBRARY = BuildingTemplate(
        name="Library",
        type=BuildingType.URBAN,
        cost=5,
        calculate_yields=YieldsPerUniqueTerrainType(Yields(science=2)),
        prereq=TECHS.POTTERY,
    )
    MINE = BuildingTemplate(
        name="Mine",
        type=BuildingType.RURAL,
        cost=5,
        calculate_yields=YieldsPerTerrainType(TERRAINS.HILLS, Yields(metal=1)),
        prereq=TECHS.MINING,
    )
    FISHERY = BuildingTemplate(
        name="Fishery",
        type=BuildingType.RURAL,
        cost=5,
        calculate_yields=YieldsPerTerrainType(TERRAINS.OCEAN, Yields(food=2)),
        prereq=TECHS.FISHING,
    )
    AQUEDUCT = BuildingTemplate(
        name="Aqueduct",
        type=BuildingType.RURAL,
        cost=20,
        abilities=[{
            "name": "CityGrowthCostReduction",
            "numbers": [0.5],
        }],
        prereq=TECHS.CONSTRUCTION,
    )
    BAZAAR = BuildingTemplate(
        name="Bazaar",
        type=BuildingType.URBAN,
        cost=20,
        prereq=TECHS.CURRENCY,
        abilities=[{
            "name": "DecreaseFoodDemand",
            "numbers": [8, 2],
        }],
    )
    WORKSHOP = BuildingTemplate(
        name="Workshop",
        type=BuildingType.RURAL,
        cost=10,
        calculate_yields=ConstantYields(Yields(metal=6)),
        prereq=TECHS.CONSTRUCTION,
    )
    MANORS = BuildingTemplate(
        name="Manors",
        type=BuildingType.RURAL,
        cost=15,
        calculate_yields=ConstantYields(Yields(food=6)),
        prereq=TECHS.CURRENCY,
    )
    MAGISTERIUM = BuildingTemplate(
        name="Magisterium",
        type=BuildingType.URBAN,
        cost=20,
        abilities=[{
            "name": "ExtraTerritory",
            "numbers": [],
        }],
        prereq=TECHS.MATHEMATICS,
    )
    FORUM = BuildingTemplate(
        name="Forum",
        type=BuildingType.URBAN,
        cost=10,
        calculate_yields=YieldsIncreaseTownCenter(constant=5),
        prereq=TECHS.IRON_WORKING,
    )
    QUARRY = BuildingTemplate(
        name="Quarry",
        type=BuildingType.RURAL,
        cost=10,
        calculate_yields=ConstantYields(Yields(wood=5)),
        prereq=TECHS.ENGINEERING,
    )
    LIGHTHOUSE = BuildingTemplate(
        name="Lighthouse",
        type=BuildingType.RURAL,
        cost=10,
        calculate_yields=YieldsPerTerrainType(TERRAINS.OCEAN, Yields(food=1, science=1, metal=1)),
        prereq=TECHS.MATHEMATICS,
    )
    UNIVERSITY = BuildingTemplate(
        name="University",
        type=BuildingType.URBAN,
        cost=15,
        calculate_yields=YieldsPerPopulation(Yields(science=1)),
        prereq=TECHS.EDUCATION,
    )
    HARBOR = BuildingTemplate(
        name="Harbor",
        type=BuildingType.URBAN,
        cost=20,
        calculate_yields=YieldsPerTerrainType(TERRAINS.OCEAN, Yields(wood=5)),
        prereq=TECHS.COMPASS,
    )
    TAX_OFFICE = BuildingTemplate(
        name="Tax Office",
        type=BuildingType.URBAN,
        cost=10,
        calculate_yields=YieldsPerBuildingType(BuildingType.RURAL, Yields(wood=2, metal=2)),
        prereq=TECHS.COMPASS,
    )
    WATERMILL = BuildingTemplate(
        name="Watermill",
        type=BuildingType.URBAN,
        cost=20,
        calculate_yields=YieldsPerPopulation(Yields(wood=1)),
        prereq=TECHS.MACHINERY,
    )
    PLANTATION = BuildingTemplate(
        name="Plantation",
        type=BuildingType.RURAL,
        cost=20,
        calculate_yields=YieldsPerPopulation(Yields(food=1)),
        prereq=TECHS.CIVIL_SERVICE,
    )
    FORGE = BuildingTemplate(
        name="Forge",
        type=BuildingType.URBAN,
        cost=20,
        calculate_yields=YieldsPerPopulation(Yields(metal=1)),
        prereq=TECHS.MACHINERY,
    )
    FACTORY = BuildingTemplate(
        name="Factory",
        type=BuildingType.URBAN,
        cost=75,
        calculate_yields=YieldsPerPopulation(Yields(wood=1, metal=1)),
        prereq=TECHS.INDUSTRIALIZATION,
    )
    SKYSCRAPER = BuildingTemplate(
        name="Skyscraper",
        type=BuildingType.URBAN,
        cost=75,
        calculate_yields=YieldsPerPopulation(Yields(wood=1, science=1)),
        prereq=TECHS.MILITARY_SCIENCE,
    )
    LABORATORY = BuildingTemplate(
        name="Laboratory",
        type=BuildingType.URBAN,
        cost=75,
        calculate_yields=YieldsPerPopulation(Yields(science=1, metal=1)),
        prereq=TECHS.MEDICINE,
    )
    ARMY_BASE = BuildingTemplate(
        name="Army Base",
        type=BuildingType.RURAL,
        cost=40,
        prereq=TECHS.MILITARY_SCIENCE,
        abilities=[{
            "name": "UnitsExtraStrengthByAge",
            "numbers": [4, 3],
        }],
    )
    OBSERVATORY = BuildingTemplate(
        name="Observatory",
        type=BuildingType.RURAL,
        cost=20,
        calculate_yields=ConstantYields(Yields(science=8)),
        prereq=TECHS.PHYSICS,
    )
    RAILROADS = BuildingTemplate(
        name="Railroads",
        type=BuildingType.RURAL,
        cost=30,
        abilities=[{
            "name": "ReducePuppetDistancePenalty",
            "numbers": [0.02],
        }],
        prereq=TECHS.DYNAMITE,
    )
    CONSTRUCTION_DEPOT = BuildingTemplate(
        name="Construction Depot",
        type=BuildingType.RURAL,
        cost=5,
        on_build=GainResourceEffect("wood", 100),
        prereq=TECHS.DYNAMITE,
    )
    SHOPPING_MALL = BuildingTemplate(
        name="Shopping Mall",
        type=BuildingType.URBAN,
        cost=20,
        abilities=[{
            "name": "DecreaseFoodDemand",
            "numbers": [40, 10],
        }],
        prereq=TECHS.MASS_MARKETS,
    )
    WINDMILL = BuildingTemplate(
        name="Windmill",
        type=BuildingType.RURAL,
        cost=20,
        calculate_yields=YieldsPerTerrainType(TERRAINS.PLAINS, Yields(food=2)),
        prereq=TECHS.PHYSICS,
    )
    PLAZA = BuildingTemplate(
        name="Plaza",
        type=BuildingType.URBAN,
        cost=50,
        calculate_yields=YieldsIncreaseTownCenter(multiplier=1),
        prereq=TECHS.ARCHITECTURE,
    )
    OUTPOST = BuildingTemplate(
        name="Outpost",
        type=BuildingType.RURAL,
        cost=30,
        calculate_yields=YieldsPerTerrainType({TERRAINS.MOUNTAINS, TERRAINS.DESERT, TERRAINS.TUNDRA}, Yields(science=6)),
        prereq=TECHS.METALLURGY,
    )
    CONSCRIPTION_POST = BuildingTemplate(
        name="Conscription Post",
        type=BuildingType.RURAL,
        cost=20,
        per_turn=BuildEachUnitEffect(),
        prereq=TECHS.PRINTING_PRESS,
    )
    CARAVANSERY = BuildingTemplate(
        name="Caravansery",
        type=BuildingType.RURAL,
        cost=30,
        prereq=TECHS.PRINTING_PRESS,
        abilities=[{
            "name": "DecreaseFoodDemand",
            "numbers": [20, 4],
        }],
    )
    IRONWORKS = BuildingTemplate(
        name="Ironworks",
        type=BuildingType.URBAN,
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["metal", 1],
        }],
        prereq=TECHS.IRON_WORKING,
    )
    NATIONAL_COLLEGE = BuildingTemplate(
        name="National College",
        type=BuildingType.URBAN,
        cost=30,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["science", 2],
        }],
        prereq=TECHS.EDUCATION,
    )
    TIMBERWORKS = BuildingTemplate(
        name="Timberworks",
        type=BuildingType.URBAN,
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["wood", 1],
        }],
        prereq=TECHS.ENGINEERING,
    )
    HUSBANDRY_CENTER = BuildingTemplate(
        name="Husbandry Center",
        type=BuildingType.URBAN,
        cost=5,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["food", 1],
        }],
        prereq=TECHS.IRRIGATION,
    )
    GRAND_PALACE = BuildingTemplate(
        name="Grand Palace",
        type=BuildingType.RURAL,
        cost=100,
        on_build=[ResetHappinessThisCityEffect(), GainResourceEffect("city_power", 100)],
        prereq=TECHS.INDUSTRIALIZATION,
    )
    INDUSTRIAL_FARM = BuildingTemplate(
        name="Industrial Farm",
        type=BuildingType.RURAL,
        cost=50,
        calculate_yields=ConstantYields(Yields(food=20)),
        prereq=TECHS.MEDICINE,
    )
    AUTOMATED_FARM = BuildingTemplate(
        name="Automated Farm",
        type=BuildingType.RURAL,
        cost=80,
        calculate_yields=ConstantYields(Yields(food=30, wood=15)),
        prereq=TECHS.MECHANIZED_AGRICULTURE,
    )
    SUBURBS = BuildingTemplate(
        name="Suburbs",
        type=BuildingType.RURAL,
        cost=50,
        prereq=TECHS.MECHANIZED_AGRICULTURE,
        on_build=GrowEffect(10),
    )
    LAND_REFORM = BuildingTemplate(
        name="Land Reform",
        type=BuildingType.RURAL,
        cost=50,
        prereq=TECHS.COMBINED_ARMS,
        calculate_yields=YieldsPerBuildingType(BuildingType.RURAL, Yields(food=4, wood=4, metal=4, science=4)),
    )
    PUBLIC_TRANSIT = BuildingTemplate(
        name="Public Transit",
        type=BuildingType.URBAN,
        cost=20,
        prereq=TECHS.MASS_MARKETS,
        calculate_yields=YieldsPerBuildingType(BuildingType.URBAN, Yields(food=2, wood=2, metal=2, science=2)),
    )
    AIRFORCE_BASE = BuildingTemplate(
        name="Airforce Base",
        type=BuildingType.RURAL,
        cost=50,
        prereq=TECHS.RADIO,
        abilities=[{
            "name": "Airforce",
            "numbers": [5, 5],
        }],
    )
    DEPLOYMENT_CENTER = BuildingTemplate(
        name="Deployment Center",
        type=BuildingType.URBAN,
        cost=50,
        prereq=TECHS.COMBINED_ARMS,
        abilities=[{
            "name": "DeploymentCenter",
            "numbers": [],
        }],
    )
    INTERNET = BuildingTemplate(
        name="Internet",
        type=BuildingType.URBAN,
        cost=100,
        calculate_yields=YieldsPerPopulation(Yields(food=1, wood=1, metal=1, science=1)),      
        prereq=TECHS.COMPUTERS,
    )

    # all & by_name are copy-pasted methods to all template lists.
    # I wasn't able to set up a base class system for this
    # That handled the dynamic type properly.
    @classmethod
    def all(cls) -> Generator[BuildingTemplate, None, None]:
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), BuildingTemplate):
                yield getattr(cls, attr)
    @classmethod
    def by_name(cls, name: str) -> BuildingTemplate:
        for item in cls.all():
            if item.name == name:
                return item
        raise KeyError(f'No item with name {name}')