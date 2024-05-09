from typing import Generator
from building_template import BuildingTemplate
from tech_templates_list import TECHS

class BUILDINGS():
    LUMBER_MILL = BuildingTemplate(
        name="Lumber Mill",
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
        name="Granary",
        type="economy",
        cost=10,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 1, "plains"],
        }],
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
        name="Mine",
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
        name="Plantation",
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
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["metal", 4],
        }],
        prereq=TECHS.MATHEMATICS,
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
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["science", 4],
        }],
        prereq=TECHS.COMPASS,
    )
    PAPER_MAKER = BuildingTemplate(
        name="Paper Maker",
        type="science",
        cost=15,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["wood", 4],
        }],
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
        name="Forge",
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
        name="Lumber Farm",
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
        name="Apothecary",
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
        name="Outpost",
        type="economy",
        cost=15,
        abilities=[{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 2, 'desert'],
        }],
        prereq=TECHS.RIFLING,
    )
    CARAVANSERY = BuildingTemplate(
        name="Caravansery",
        type="economy",
        cost=20,
        prereq=TECHS.ECONOMICS,
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
        abilities=[{
            "name": "ResetCityUnhappiness",
            "numbers": [],
        }],
        is_national_wonder=True,
        prereq=TECHS.RIFLING,
    )
    WORLDS_FAIR = BuildingTemplate(
        name="World's Fair",
        type="economy",
        cost=100,
        abilities=[{
            "name": "ResetCivUnhappiness",
            "numbers": [],
        }],
        is_wonder=True,
        prereq=TECHS.RADIO,
        vp_reward=5,
    )
    INDUSTRIAL_FARM = BuildingTemplate(
        name="Industrial Farm",
        type="economy",
        cost=80,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["food", 30],
        }, {
            "name": "IncreaseYieldsInCity",
            "numbers": ["wood", 15],
        }],
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
    HANGING_GARDENS = BuildingTemplate(
        name="Hanging Gardens",
        type="economy",
        cost=50,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["food", 5],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.CODE_OF_LAWS,
    )
    PYRAMIDS = BuildingTemplate(
        name="Pyramids",
        type="wonder",
        cost=50,
        abilities=[
            {
                "name": "GainCityPower",
                "numbers": [100],
            },
        ],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.MASONRY,
    )
    TEMPLE_OF_ARTEMIS = BuildingTemplate(
        name="Temple of Artemis",
        type="economy",
        cost=50,
        abilities=[{
            "name": "GainFreeUnits",
            "numbers": ["Archer", 3],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.CALENDAR,
    )
    COLOSUS = BuildingTemplate(
        name="Colossus",
        type="economy",
        cost=60,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["metal", 5],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.IRON_WORKING,
    )
    STATUE_OF_ZEUS = BuildingTemplate(
        name="Statue of Zeus",
        type="economy",
        cost=60,
        abilities=[{
            "name": "NewUnitsGainBonusStrength",
            "numbers": [1],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.ENGINEERING,
    )
    GREAT_LIBRARY = BuildingTemplate(
        name="Great Library",
        type="science",
        cost=60,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["science", 5],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.WRITING,
    )
    PETRA = BuildingTemplate(
        name="Petra",
        type="economy",
        cost=70,
        abilities=[{
            "name": "DoubleYieldsForTerrainInCity",
            "numbers": ["desert"],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.CURRENCY,
    )
    CHICHEN_ITZA = BuildingTemplate(
        name="Chichen Itza",
        type="economy",
        cost=80,
        abilities=[{
            "name": "IncreasePopulationOfNewCities",
            "numbers": [3],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.CIVIL_SERVICE,
    )
    GREAT_LIGHTHOUSE = BuildingTemplate(
        name="Great Lighthouse",
        type="economy",
        cost=90,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["food", 10],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.COMPASS,
    )
    FORBIDDEN_PALACE = BuildingTemplate(
        name="Forbidden Palace",
        type="economy",
        cost=100,
        abilities=[{
            "name": "GainCityPower",
            "numbers": [200],
        }, {
            "name": "ExtraTerritory",
            "numbers": [],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.PRINTING_PRESS,
    )
    HIMEJI_CASTLE = BuildingTemplate(
        name="Himeji Castle",
        type="economy",
        cost=110,
        abilities=[{
            "name": "ExistingUnitsGainBonusStrength",
            "numbers": [2],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.GUNPOWDER,
    )
    NOTRE_DAME = BuildingTemplate(
        name="Notre Dame",
        type="economy",
        cost=120,
        abilities=[{
            "name": "IncreaseYieldsInCity",
            "numbers": ["wood", 15],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.ARCHITECTURE,
    )
    PORCELAIN_TOWER = BuildingTemplate(
        name="Porcelain Tower",
        type="science",
        cost=140,
        abilities=[{
            "name": "ExtraVpsForTechs",
            "numbers": [1],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.ECONOMICS,
    )
    BRANDEMBURG_GATE = BuildingTemplate(
        name="Brandenburg Gate",
        type="economy",
        cost=150,
        abilities=[{
            "name": "NewUnitsGainBonusStrength",
            "numbers": [3],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.MILITARY_SCIENCE,
    )
    STATUE_OF_LIBERTY = BuildingTemplate(
        name="Statue of Liberty",
        type="economy",
        cost=250,
        abilities=[{
            "name": "ExtraVpsForCityGrowth",
            "numbers": [1],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.RADIO,
    )
    KREMLIN = BuildingTemplate(
        name="Kremlin",
        type="economy",
        cost=300,
        abilities=[{
            "name": "ExtraVpsForCityCapture",
            "numbers": [10],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.COMBINED_ARMS,
    )
    FAST_FOOD_CHAINS = BuildingTemplate(
        name="Fast Food Chains",
        type="economy",
        cost=350,
        abilities=[{
            "name": "TripleCityPopulation",
            "numbers": [],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.MECHANIZED_AGRICULTURE,
    )
    APPLOLO_PROGRAM = BuildingTemplate(
        name="Apollo Program",
        type="economy",
        cost=400,
        abilities=[{
            "name": "ExtraVpsForTechs",
            "numbers": [5],
        }],
        is_wonder=True,
        vp_reward=5,
        prereq=TECHS.ROCKETRY,
    )
    AGI = BuildingTemplate(
        name="AGI",
        type="economy",
        cost=750,
        abilities=[{
            "name": "EndTheGame",
            "numbers": [],
        }],
        is_wonder=True,
        vp_reward=10,
        prereq=TECHS.MEGAROBOTICS,
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