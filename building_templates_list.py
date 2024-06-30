from typing import Generator
from building_template import BuildingTemplate
from terrain_templates_list import TERRAINS
from effects_list import ResetHappinessThisCityEffect
from tech_templates_list import TECHS
from yields import ConstantYields, Yields, YieldsPerPopulation, YieldsPerTerrainType, YieldsPerUniqueTerrainType

class BUILDINGS():
    LUMBER_MILL = BuildingTemplate(
        name="Lumber Mill",
        type="economy",
        cost=15,
        calculate_yields=YieldsPerTerrainType(TERRAINS.FOREST, Yields(wood=1)),
        prereq=TECHS.FORESTRY,
        exclusion_group="a1",
    )
    TRAINING_GROUNDS = BuildingTemplate(
        name="Training Grounds",
        type="military",
        cost=15,
        prereq=TECHS.FORESTRY,
        abilities=[{
            "name": "UnitsExtraStrengthByAge",
            "numbers": [2, 1],
        }],
    )
    PASTURE = BuildingTemplate(
        name="Pasture",
        type="military",
        cost=15,
        prereq=TECHS.IRRIGATION,
        abilities=[{
            "name": "UnitsExtraStrengthByTag",
            "numbers": ["mounted", 1],
        }],
    )
    GRANARY = BuildingTemplate(
        name="Granary",
        type="economy",
        cost=10,
        calculate_yields=YieldsPerTerrainType(TERRAINS.PLAINS, Yields(food=1)),
        prereq=TECHS.POTTERY,
    )
    ROADS = BuildingTemplate(
        name="Roads",
        type="economy",
        cost=10,
        abilities=[{
            "name": "ReducePuppetDistancePenalty",
            "numbers": [0.05],
        }],
        prereq=TECHS.THE_WHEEL,
    )
    LIBRARY = BuildingTemplate(
        name="Library",
        type="science",
        cost=15,
        calculate_yields=YieldsPerUniqueTerrainType(Yields(science=1)),
        prereq=TECHS.POTTERY,
        exclusion_group="a1",
    )
    MINE = BuildingTemplate(
        name="Mine",
        type="economy",
        cost=15,
        calculate_yields=YieldsPerTerrainType(TERRAINS.HILLS, Yields(metal=1)),
        prereq=TECHS.MINING,
        exclusion_group="a1",
    )
    AQUEDUCT = BuildingTemplate(
        name="Aqueduct",
        type="economy",
        cost=20,
        abilities=[{
            "name": "CityGrowthCostReduction",
            "numbers": [0.5],
        }],
        prereq=TECHS.CONSTRUCTION,
    )
    COLOSSEUM = BuildingTemplate(
        name="Colosseum",
        type="economy",
        cost=10,
        prereq=TECHS.CONSTRUCTION,
        abilities=[],
        vp_reward=1,
    )
    BAZAAR = BuildingTemplate(
        name="Bazaar",
        type="economy",
        cost=10,
        prereq=TECHS.CURRENCY,
        abilities=[{
            "name": "DecreaseFoodDemand",
            "numbers": [4],
        }],
    )
    WORKSHOP = BuildingTemplate(
        name="Workshop",
        type="economy",
        cost=15,
        calculate_yields=ConstantYields(Yields(metal=4)),
        prereq=TECHS.CURRENCY,
    )
    MAGISTERIUM = BuildingTemplate(
        name="Magisterium",
        type="economy",
        cost=20,
        abilities=[{
            "name": "ExtraTerritory",
            "numbers": [],
        }],
        prereq=TECHS.MATHEMATICS,
    )
    UNIVERSITY = BuildingTemplate(
        name="University",
        type="science",
        cost=20,
        calculate_yields=YieldsPerPopulation(Yields(science=1)),
        prereq=TECHS.EDUCATION,
        exclusion_group="a3",
    )
    HARBOR = BuildingTemplate(
        name="Harbor",
        type="economy",
        cost=20,
        calculate_yields=YieldsPerPopulation(Yields(wood=1)),
        prereq=TECHS.COMPASS,
        exclusion_group="a3",
    )
    CONSCRIPTION_POST = BuildingTemplate(
        name="Conscription Post",
        type="economy",
        cost=20,
        calculate_yields=YieldsPerPopulation(Yields(metal=1)),
        prereq=TECHS.CIVIL_SERVICE,
        exclusion_group="a3",
    )
    FACTORY = BuildingTemplate(
        name="Factory",
        type="economy",
        cost=40,
        calculate_yields=YieldsPerPopulation(Yields(wood=1)),
        prereq=TECHS.INDUSTRIALIZATION,
        exclusion_group="factory",
    )
    INDUSTRIAL_MINE = BuildingTemplate(
        name="Industrial Mine",
        type="economy",
        cost=40,
        calculate_yields=YieldsPerPopulation(Yields(metal=1)),
        prereq=TECHS.MILITARY_SCIENCE,
        exclusion_group="factory",
    )
    LABORATORY = BuildingTemplate(
        name="Laboratory",
        type="economy",
        cost=40,
        calculate_yields=YieldsPerPopulation(Yields(science=1)),
        prereq=TECHS.MEDICINE,
        exclusion_group="factory",
    )
    OBSERVATORY = BuildingTemplate(
        name="Observatory",
        type="science",
        cost=15,
        calculate_yields=ConstantYields(Yields(science=4)),
        prereq=TECHS.PHYSICS,
    )
    PAPER_MAKER = BuildingTemplate(
        name="Paper Maker",
        type="science",
        cost=15,
        calculate_yields=ConstantYields(Yields(wood=4)),
        prereq=TECHS.CIVIL_SERVICE,
    )
    ZOO = BuildingTemplate(
        name="Zoo",
        type="economy",
        cost=20,
        prereq=TECHS.PRINTING_PRESS,
        abilities=[],
        vp_reward=1,
    )
    STADIUM = BuildingTemplate(
        name="Stadium",
        type="economy",
        cost=40,
        prereq=TECHS.MASS_MARKETS,
        abilities=[],
        vp_reward=2,
    )
    RAILROADS = BuildingTemplate(
        name="Railroads",
        type="economy",
        cost=30,
        abilities=[{
            "name": "ReducePuppetDistancePenalty",
            "numbers": [0.02],
        }],
        prereq=TECHS.DYNAMITE,
    )
    SHOPPING_MALL = BuildingTemplate(
        name="Shopping Mall",
        type="economy",
        cost=20,
        abilities=[{
            "name": "DecreaseFoodDemand",
            "numbers": [10],
        }, {
            "name": "DecreaseFoodDemandPuppets",
            "numbers": [10],
        }],
        prereq=TECHS.MASS_MARKETS,
    )
    WINDMILL = BuildingTemplate(
        name="Windmill",
        type="economy",
        cost=30,
        calculate_yields=YieldsPerTerrainType(TERRAINS.PLAINS, Yields(food=2)),
        prereq=TECHS.PHYSICS,
    )
    FORGE = BuildingTemplate(
        name="Forge",
        type="economy",
        cost=30,
        calculate_yields=YieldsPerTerrainType(TERRAINS.HILLS, Yields(metal=2)),
        prereq=TECHS.ARCHITECTURE,
    )
    LUMBER_FARM = BuildingTemplate(
        name="Lumber Farm",
        type="economy",
        cost=30,
        calculate_yields=YieldsPerTerrainType(TERRAINS.FOREST, Yields(wood=2)),
        prereq=TECHS.ARCHITECTURE,
    )
    OUTPOST = BuildingTemplate(
        name="Outpost",
        type="economy",
        cost=30,
        calculate_yields=YieldsPerTerrainType({TERRAINS.MOUNTAINS, TERRAINS.DESERT, TERRAINS.TUNDRA}, Yields(science=4)),
        prereq=TECHS.METALLURGY,
    )
    CARAVANSERY = BuildingTemplate(
        name="Caravansery",
        type="economy",
        cost=20,
        prereq=TECHS.PRINTING_PRESS,
        abilities=[{
            "name": "DecreaseFoodDemand",
            "numbers": [10],
        }],
    )
    IRONWORKS = BuildingTemplate(
        name="Ironworks",
        type="economy",
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["metal", 2],
        }],
        prereq=TECHS.MACHINERY,
    )
    NATIONAL_COLLEGE = BuildingTemplate(
        name="National College",
        type="science",
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["science", 2],
        }],
        prereq=TECHS.EDUCATION,
    )
    TIMBERWORKS = BuildingTemplate(
        name="Timberworks",
        type="economy",
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["wood", 2],
        }],
        prereq=TECHS.ENGINEERING,
    )
    HUSBANDRY_CENTER = BuildingTemplate(
        name="Husbandry Center",
        type="economy",
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["food", 2],
        }],
        prereq=TECHS.IRRIGATION,
    )
    GRAND_PALACE = BuildingTemplate(
        name="Grand Palace",
        type="economy",
        cost=100,
        on_build=ResetHappinessThisCityEffect(),
        prereq=TECHS.MILITARY_SCIENCE,
    )
    INDUSTRIAL_FARM = BuildingTemplate(
        name="Industrial Farm",
        type="economy",
        cost=80,
        calculate_yields=ConstantYields(Yields(food=30, wood=15)),
        prereq=TECHS.MECHANIZED_AGRICULTURE,
    )
    INTERNET = BuildingTemplate(
        name="Internet",
        type="economy",
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