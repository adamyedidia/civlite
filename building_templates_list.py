from typing import Generator
from building_template import BuildingTemplate
from effects_list import IncreaseYieldsForTerrain, IncreaseYieldsInCity, ResetHappinessThisCityEffect
from tech_templates_list import TECHS

class BUILDINGS():
    LUMBER_MILL = BuildingTemplate(
        name="Lumber Mill",
        type="economy",
        cost=15,
        on_build=IncreaseYieldsForTerrain("wood", 1, ["forest", "jungle"]),
        prereq=TECHS.FORESTRY,
    )
    GRANARY = BuildingTemplate(
        name="Granary",
        type="economy",
        cost=10,
        on_build=IncreaseYieldsForTerrain("food", 1, "plains"),
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
        cost=10,
        on_build=IncreaseYieldsForTerrain("science", 1, ["tundra", "desert"]),
        prereq=TECHS.POTTERY,
    )
    MINE = BuildingTemplate(
        name="Mine",
        type="economy",
        cost=15,
        on_build=IncreaseYieldsForTerrain("metal", 1, ["hills", "mountain"]),
        prereq=TECHS.MINING,
    )
    PLANTATION = BuildingTemplate(
        name="Plantation",
        type="economy",
        cost=15,
        on_build=IncreaseYieldsForTerrain("food", 1, ["grassland", "marsh"]),
        prereq=TECHS.IRRIGATION,
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
        on_build=IncreaseYieldsInCity("metal", 4),
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
        is_national_wonder=True,
        prereq=TECHS.MATHEMATICS,
    )
    UNIVERSITY = BuildingTemplate(
        name="University",
        type="science",
        cost=25,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["science", 1],
        }],
        prereq=TECHS.EDUCATION,
    )
    FACTORY = BuildingTemplate(
        name="Factory",
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
        name="Observatory",
        type="science",
        cost=15,
        on_build=IncreaseYieldsInCity("science", 4),
        prereq=TECHS.COMPASS,
    )
    PAPER_MAKER = BuildingTemplate(
        name="Paper Maker",
        type="science",
        cost=15,
        on_build=IncreaseYieldsInCity("wood", 4),
        prereq=TECHS.PRINTING_PRESS,
    )
    ZOO = BuildingTemplate(
        name="Zoo",
        type="economy",
        cost=20,
        prereq=TECHS.MEDICINE,
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
        on_build=IncreaseYieldsForTerrain("food", 2, ["tundra", "grassland"]),
        prereq=TECHS.PHYSICS,
    )
    FORGE = BuildingTemplate(
        name="Forge",
        type="economy",
        cost=30,
        on_build=IncreaseYieldsForTerrain("metal", 2, ["mountain", "plains"]),
        prereq=TECHS.ARCHITECTURE,
    )
    LUMBER_FARM = BuildingTemplate(
        name="Lumber Farm",
        type="economy",
        cost=30,
        on_build=IncreaseYieldsForTerrain("wood", 2, ["forest", "hills"]),
        prereq=TECHS.ARCHITECTURE,
    )
    APOTHECARY = BuildingTemplate(
        name="Apothecary",
        type="economy",
        cost=30,
        on_build=IncreaseYieldsForTerrain("food", 2, ["marsh", "jungle"]),
        prereq=TECHS.MEDICINE,
    )
    OUTPOST = BuildingTemplate(
        name="Outpost",
        type="economy",
        cost=15,
        on_build=IncreaseYieldsForTerrain("metal", 2, "desert"),
        prereq=TECHS.RIFLING,
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
        is_national_wonder=True,
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
        is_national_wonder=True,
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
        is_national_wonder=True,
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
        is_national_wonder=True,
        prereq=TECHS.IRRIGATION,
    )
    GRAND_PALACE = BuildingTemplate(
        name="Grand Palace",
        type="economy",
        cost=100,
        on_build=ResetHappinessThisCityEffect(),
        is_national_wonder=True,
        prereq=TECHS.RIFLING,
    )
    INDUSTRIAL_FARM = BuildingTemplate(
        name="Industrial Farm",
        type="economy",
        cost=80,
        on_build=[IncreaseYieldsInCity("food", 30), IncreaseYieldsInCity("wood", 15)],
        prereq=TECHS.MECHANIZED_AGRICULTURE,
    )
    INTERNET = BuildingTemplate(
        name="Internet",
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
            if item.name == name:
                return item
        raise KeyError(f'No item with name {name}')