from typing import Generator
from building_template import BuildingTemplate
from terrain_templates_list import TERRAINS
from effects_list import BuildBuildingEffect, IncreaseYieldsForTerrain, IncreaseYieldsInCity, IncreaseYieldsPerTerrainType, ResetHappinessThisCityEffect
from tech_templates_list import TECHS

class BUILDINGS():
    LUMBER_MILL = BuildingTemplate(
        name="Lumber Mill",
        type="economy",
        cost=15,
        on_build=IncreaseYieldsForTerrain("wood", 1, TERRAINS.FOREST, buff_type='small'),
        prereq=TECHS.FORESTRY,
        exclusion_group="a1",
    )
    GRANARY = BuildingTemplate(
        name="Granary",
        type="economy",
        cost=10,
        on_build=IncreaseYieldsForTerrain("food", 1, TERRAINS.PLAINS, buff_type='small'),
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
        on_build=IncreaseYieldsPerTerrainType("science", 1),
        prereq=TECHS.POTTERY,
        exclusion_group="a1",
    )
    MINE = BuildingTemplate(
        name="Mine",
        type="economy",
        cost=15,
        on_build=IncreaseYieldsForTerrain("metal", 1, TERRAINS.HILLS, buff_type='small'),
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
        cost=20,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["science", 1],
        }],
        prereq=TECHS.EDUCATION,
        exclusion_group="a3",
    )
    HARBOR = BuildingTemplate(
        name="Harbor",
        type="economy",
        cost=20,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["wood", 1],
        }],
        prereq=TECHS.COMPASS,
        exclusion_group="a3",
    )
    CONSCRIPTION_POST = BuildingTemplate(
        name="Conscription Post",
        type="economy",
        cost=20,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["metal", 1],
        }],
        prereq=TECHS.CIVIL_SERVICE,
        exclusion_group="a3",
    )
    FACTORY = BuildingTemplate(
        name="Factory",
        type="economy",
        cost=40,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["wood", 1],
        }],
        prereq=TECHS.INDUSTRIALIZATION,
        exclusion_group="factory",
    )
    INDUSTRIAL_MINE = BuildingTemplate(
        name="Industrial Mine",
        type="economy",
        cost=40,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["metal", 1],
        }],
        prereq=TECHS.MILITARY_SCIENCE,
        exclusion_group="factory",
    )
    LABORATORY = BuildingTemplate(
        name="Laboratory",
        type="economy",
        cost=40,
        abilities=[{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["science", 1],
        }],
        prereq=TECHS.MEDICINE,
        exclusion_group="factory",
    )
    OBSERVATORY = BuildingTemplate(
        name="Observatory",
        type="science",
        cost=15,
        on_build=IncreaseYieldsInCity("science", 4),
        prereq=TECHS.PHYSICS,
    )
    PAPER_MAKER = BuildingTemplate(
        name="Paper Maker",
        type="science",
        cost=15,
        on_build=IncreaseYieldsInCity("wood", 4),
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
        on_build=IncreaseYieldsForTerrain("food", 2, TERRAINS.PLAINS, buff_type='large'),
        prereq=TECHS.PHYSICS,
    )
    FORGE = BuildingTemplate(
        name="Forge",
        type="economy",
        cost=30,
        on_build=IncreaseYieldsForTerrain("metal", 2, TERRAINS.HILLS, buff_type='large'),
        prereq=TECHS.ARCHITECTURE,
    )
    LUMBER_FARM = BuildingTemplate(
        name="Lumber Farm",
        type="economy",
        cost=30,
        on_build=IncreaseYieldsForTerrain("wood", 2, TERRAINS.FOREST, buff_type='large'),
        prereq=TECHS.ARCHITECTURE,
    )
    # APOTHECARY = BuildingTemplate(
    #     name="Apothecary",
    #     type="economy",
    #     cost=30,
    #     on_build=IncreaseYieldsForTerrain("food", 2, ["marsh", "jungle"]),
    #     prereq=TECHS.GUNPOWDER,
    # )
    OUTPOST = BuildingTemplate(
        name="Outpost",
        type="economy",
        cost=30,
        on_build=IncreaseYieldsForTerrain("science", 4, [TERRAINS.MOUNTAINS, TERRAINS.DESERT, TERRAINS.TUNDRA], buff_type='large'),
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
        prereq=TECHS.MILITARY_SCIENCE,
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
    
# Hack to set up circular references without importing BUILDINGS in TECHS.
for tech in TECHS.all():
    if isinstance(tech.breakthrough_effect, BuildBuildingEffect):
        tech.breakthrough_effect.building_template = BUILDINGS.by_name(tech.breakthrough_effect.building_template_temp_str)