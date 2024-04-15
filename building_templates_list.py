from typing import Generator
from building_template import BuildingTemplate
from tech_templates_list import TECHS

class BUILDINGS():
    LUMBER_MILL = BuildingTemplate(
        building_name="Lumber Mill",
        type="economy",
        cost=15,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["wood", 1, "forest"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["wood", 1, "jungle"],
        }],
        prereq=TECHS.FORESTRY,
    )
    GRANARY = BuildingTemplate(
        building_name="Granary",
        type="economy",
        cost=10,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 1, "plains"],
        }],
        prereq=TECHS.POTTERY,
    )
    ROADS = BuildingTemplate(
        building_name="Roads",
        type="economy",
        cost=10,
        abilities=[{
            "name": "ReducePuppetDistancePenalty",
            "numbers": [0.05],
        }],
        prereq=TECHS.THE_WHEEL,
    )
    LIBRARY = BuildingTemplate(
        building_name="Library",
        type="science",
        cost=10,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["science", 1, "tundra"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["science", 1, "desert"],
        }],
        prereq=TECHS.WRITING,
    )
    MINE = BuildingTemplate(
        building_name="Mine",
        type="economy",
        cost=15,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 1, "hills"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 1, "mountain"],
        }],
        prereq=TECHS.MINING,
    )
    PLANTATION = BuildingTemplate(
        building_name="Plantation",
        type="economy",
        cost=15,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 1, "grassland"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 1, "marsh"],
        }],
        prereq=TECHS.IRRIGATION,
    )
    AQUEDUCT = BuildingTemplate(
        building_name="Aqueduct",
        type="economy",
        cost=20,
        abilities=[{
            "name": "CityGrowthCostReduction",
            "numbers": [0.5],
        }],
        prereq=TECHS.CONSTRUCTION,
    )
    COLOSSEUM = BuildingTemplate(
        building_name="Colosseum",
        type="economy",
        cost=10,
        prereq=TECHS.CONSTRUCTION,
        abilities=[],
        vp_reward=1,
    )
    BAZAAR = BuildingTemplate(
        building_name="Bazaar",
        type="economy",
        cost=10,
        prereq=TECHS.CURRENCY,
        abilities=[{
            "name": "DecreaseFoodDemand",
            "numbers": [4],
        }],
    )
    WORKSHOP = BuildingTemplate(
        building_name="Workshop",
        type="economy",
        cost=15,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["metal", 4],
        }],
        prereq=TECHS.MATHEMATICS,
    )
    MAGISTERIUM = BuildingTemplate(
        building_name="Magisterium",
        type="economy",
        cost=20,
        abilities=[{
            "name": "ExtraTerritory",
            "numbers": [],
        }],
        is_national_wonder=True,
        prereq=TECHS.MATHEMATICS,
    )
    UNIVERSITY = BuildingTemplate(
        building_name="University",
        type="science",
        cost=25,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["science", 1],
        }],
        prereq=TECHS.EDUCATION,
    )
    FACTORY = BuildingTemplate(
        building_name="Factory",
        type="economy",
        cost=50,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["metal", 1],
        }, {
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["wood", 1],
        }],
        prereq=TECHS.INDUSTRIALIZATION,
    )
    OBSERVATORY = BuildingTemplate(
        building_name="Observatory",
        type="science",
        cost=15,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["science", 4],
        }],
        prereq=TECHS.COMPASS,
    )
    PAPER_MAKER = BuildingTemplate(
        building_name="Paper Maker",
        type="science",
        cost=15,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["wood", 4],
        }],
        prereq=TECHS.PRINTING_PRESS,
    )
    ZOO = BuildingTemplate(
        building_name="Zoo",
        type="economy",
        cost=20,
        prereq=TECHS.MEDICINE,
        abilities=[],
        vp_reward=1,
    )
    STADIUM = BuildingTemplate(
        building_name="Stadium",
        type="economy",
        cost=40,
        prereq=TECHS.RADIO,
        abilities=[],
        vp_reward=1,
    )
    RAILROADS = BuildingTemplate(
        building_name="Railroads",
        type="economy",
        cost=30,
        abilities=[{
            "name": "ReducePuppetDistancePenalty",
            "numbers": [0.02],
        }],
        prereq=TECHS.DYNAMITE,
    )
    WINDMILL = BuildingTemplate(
        building_name="Windmill",
        type="economy",
        cost=30,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 2, "tundra"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 2, "grassland"],
        }],
        prereq=TECHS.PHYSICS,
    )
    FORGE = BuildingTemplate(
        building_name="Forge",
        type="economy",
        cost=30,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 2, "mountain"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 2, "plains"],
        }],
        prereq=TECHS.METALLURGY,
    )
    LUMBER_FARM = BuildingTemplate(
        building_name="Lumber Farm",
        type="economy",
        cost=30,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["wood", 2, "forest"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["wood", 2, "hills"],
        }],
        prereq=TECHS.ARCHITECTURE,
    )
    APOTHECARY = BuildingTemplate(
        building_name="Apothecary",
        type="economy",
        cost=30,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 2, "marsh"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 2, "jungle"],
        }],
        prereq=TECHS.MEDICINE,
    )
    OUTPOST = BuildingTemplate(
        building_name="Outpost",
        type="economy",
        cost=15,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 2, 'desert'],
        }],
        prereq=TECHS.RIFLING,
    )
    CARAVANSERY = BuildingTemplate(
        building_name="Caravansery",
        type="economy",
        cost=20,
        prereq=TECHS.ECONOMICS,
        abilities=[{
            "name": "DecreaseFoodDemand",
            "numbers": [10],
        }],
    )
    IRONWORKS = BuildingTemplate(
        building_name="Ironworks",
        type="economy",
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["metal", 2],
        }],
        is_national_wonder=True,
        prereq=TECHS.MACHINERY,
    )
    NATIONAL_COLLEGE = BuildingTemplate(
        building_name="National College",
        type="science",
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["science", 2],
        }],
        is_national_wonder=True,
        prereq=TECHS.EDUCATION,
    )
    TIMBERWORKS = BuildingTemplate(
        building_name="Timberworks",
        type="economy",
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["wood", 2],
        }],
        is_national_wonder=True,
        prereq=TECHS.ENGINEERING,
    )
    HUSBANDRY_CENTER = BuildingTemplate(
        building_name="Husbandry Center",
        type="economy",
        cost=20,
        abilities=[{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["food", 2],
        }],
        is_national_wonder=True,
        prereq=TECHS.IRRIGATION,
    )
    INDUSTRIAL_FARM = BuildingTemplate(
        building_name="Industrial Farm",
        type="economy",
        cost=60,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["food", 2],
        }],
        prereq=TECHS.MECHANIZED_AGRICULTURE,
    )
    INTERNET = BuildingTemplate(
        building_name="Internet",
        type="economy",
        cost=100,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["food", 2],
        }, {
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["wood", 2],
        }, {
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["metal", 2],
        }, {
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["science", 2],
        }],        
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
            if item.building_name == name:
                return item
        raise KeyError(f'No item with name {name}')
