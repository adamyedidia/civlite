from typing import Generator
from building_template import BuildingTemplate, BuildingType
from terrain_templates_list import TERRAINS
from effects_list import BuildEeachUnitEffect, GainResourceEffect, GainUnhappinessEffect, GrowEffect, MilitarizeEffect, ResetHappinessThisCityEffect, UrbanizeEffect
from tech_templates_list import TECHS
from yields import ConstantYields, Yields, YieldsPerBuildingType, YieldsPerPopulation, YieldsPerTerrainType, YieldsPerUniqueTerrainType

class BUILDINGS():
    LUMBER_MILL = BuildingTemplate(
        name="Lumber Mill",
        type=BuildingType.RURAL,
        cost=10,
        calculate_yields=YieldsPerTerrainType(TERRAINS.FOREST, Yields(wood=1)),
        prereq=TECHS.FORESTRY,
    )
    TRAINING_GROUNDS = BuildingTemplate(
        name="Training Grounds",
        type=BuildingType.RURAL,
        cost=10,
        prereq=TECHS.FORESTRY,
        abilities=[{
            "name": "UnitsExtraStrengthByAge",
            "numbers": [1, 1],
        }],
    )
    SLAVE_TRADE = BuildingTemplate(
        name="Slave Trade",
        type=BuildingType.URBAN,
        cost=10,
        prereq=TECHS.BRONZE_WORKING,
        on_build=[GainResourceEffect("wood", 30), GainUnhappinessEffect(20)],
    )
    PASTURE = BuildingTemplate(
        name="Pasture",
        type=BuildingType.RURAL,
        cost=10,
        prereq=TECHS.IRRIGATION,
        abilities=[{
            "name": "UnitsExtraStrengthByTag",
            "numbers": ["mounted", 1],
        }],
    )
    GRANARY = BuildingTemplate(
        name="Granary",
        type=BuildingType.RURAL,
        cost=10,
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
        calculate_yields=YieldsPerUniqueTerrainType(Yields(science=1)),
        prereq=TECHS.POTTERY,
    )
    MINE = BuildingTemplate(
        name="Mine",
        type=BuildingType.RURAL,
        cost=10,
        calculate_yields=YieldsPerTerrainType(TERRAINS.HILLS, Yields(metal=1)),
        prereq=TECHS.MINING,
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
        cost=15,
        calculate_yields=ConstantYields(Yields(metal=4)),
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
    QUARRY = BuildingTemplate(
        name="Quarry",
        type=BuildingType.RURAL,
        cost=15,
        calculate_yields=ConstantYields(Yields(wood=4)),
        prereq=TECHS.ENGINEERING,
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
        calculate_yields=YieldsPerPopulation(Yields(wood=1)),
        prereq=TECHS.COMPASS,
    )
    TAX_OFFICE = BuildingTemplate(
        name="Tax Office",
        type=BuildingType.URBAN,
        cost=20,
        calculate_yields=YieldsPerBuildingType("rural", Yields(wood=2, metal=2)),
        prereq=TECHS.COMPASS,
    )
    PLANTATION = BuildingTemplate(
        name="Plantation",
        type=BuildingType.RURAL,
        cost=20,
        calculate_yields=YieldsPerPopulation(Yields(food=1)),
        prereq=TECHS.CIVIL_SERVICE,
    )
    CONSCRIPTION_POST = BuildingTemplate(
        name="Conscription Post",
        type=BuildingType.URBAN,
        cost=20,
        calculate_yields=YieldsPerPopulation(Yields(metal=1)),
        prereq=TECHS.CIVIL_SERVICE,
    )
    FACTORY = BuildingTemplate(
        name="Factory",
        type=BuildingType.URBAN,
        cost=75,
        calculate_yields=YieldsPerPopulation(Yields(wood=1, metal=1)),
        prereq=TECHS.INDUSTRIALIZATION,
    )
    COMMERCIAL_CENTER = BuildingTemplate(
        name="Commercial Center",
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
            "numbers": [4, 5],
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
    FORGE = BuildingTemplate(
        name="Forge",
        type=BuildingType.RURAL,
        cost=30,
        calculate_yields=YieldsPerTerrainType(TERRAINS.HILLS, Yields(metal=2)),
        prereq=TECHS.ARCHITECTURE,
    )
    LUMBER_FARM = BuildingTemplate(
        name="Lumber Farm",
        type=BuildingType.RURAL,
        cost=30,
        calculate_yields=YieldsPerTerrainType(TERRAINS.FOREST, Yields(wood=2)),
        prereq=TECHS.ARCHITECTURE,
    )
    OUTPOST = BuildingTemplate(
        name="Outpost",
        type=BuildingType.RURAL,
        cost=30,
        calculate_yields=YieldsPerTerrainType({TERRAINS.MOUNTAINS, TERRAINS.DESERT, TERRAINS.TUNDRA}, Yields(science=4)),
        prereq=TECHS.METALLURGY,
    )
    VOLUNTEER_POST = BuildingTemplate(
        name="Volunteer Post",
        type=BuildingType.RURAL,
        cost=50,
        per_turn=BuildEeachUnitEffect(),
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
        cost=15,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["metal", 1],
        }],
        prereq=TECHS.MACHINERY,
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
        cost=15,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["wood", 1],
        }],
        prereq=TECHS.ENGINEERING,
    )
    HUSBANDRY_CENTER = BuildingTemplate(
        name="Husbandry Center",
        type=BuildingType.URBAN,
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["food", 2],
        }],
        prereq=TECHS.IRRIGATION,
    )
    GRAND_PALACE = BuildingTemplate(
        name="Grand Palace",
        type=BuildingType.RURAL,
        cost=100,
        on_build=ResetHappinessThisCityEffect(),
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
        on_build=GrowEffect(5),
    )
    LAND_REFORM = BuildingTemplate(
        name="Land Reform",
        type=BuildingType.RURAL,
        cost=50,
        prereq=TECHS.COMBINED_ARMS,
        calculate_yields=YieldsPerBuildingType("rural", Yields(food=4, wood=4, metal=4, science=4)),
    )
    PUBLIC_TRANSIT = BuildingTemplate(
        name="Public Transit",
        type=BuildingType.URBAN,
        cost=20,
        prereq=TECHS.MASS_MARKETS,
        calculate_yields=YieldsPerBuildingType("urban", Yields(food=2, wood=2, metal=2, science=2)),
    )
    AIRFORCE_BASE = BuildingTemplate(
        name="Airforce Base",
        type=BuildingType.RURAL,
        cost=50,
        prereq=TECHS.RADIO,
        abilities=[{
            "name": "Airforce",
            "numbers": [20, 5],
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
        type=BuildingType.RURAL,
        cost=100,
        calculate_yields=YieldsPerPopulation(Yields(food=2, wood=2, metal=2, science=2)),      
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