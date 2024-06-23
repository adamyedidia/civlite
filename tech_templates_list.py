from typing import Generator
from effects_list import BuildBuildingEffect, BuildUnitBuildingEffect, BuildUnitsEffect, FreeRandomTechEffect, GainResourceEffect, GetGreatPersonEffect, GrowEffect, PointsEffect, StrengthAllUnitsEffect
from tech_template import TechTemplate

class TECHS():
    item_type = TechTemplate
    ARCHERY = TechTemplate(
        name='Archery',
        cost=25,
        advancement_level=1,
        breakthrough_effect=BuildUnitBuildingEffect("Archer"),
    )
    BRONZE_WORKING = TechTemplate(
        name= 'Bronze Working',
        cost= 25,
        advancement_level= 1,
        breakthrough_effect=BuildUnitsEffect("Spearman", 1, extra_str=2),
    )
    POTTERY = TechTemplate(
        name='Pottery',
        cost=20,
        advancement_level=1,
        breakthrough_cost=25,
        breakthrough_effect=GainResourceEffect("science", 10),
    )
    THE_WHEEL = TechTemplate(
        name='The Wheel',
        cost=35,
        advancement_level=1,
        breakthrough_effect=GainResourceEffect("city_power", 50),
    )
    MINING = TechTemplate(
        name='Mining',
        cost=30,
        advancement_level=1,
        breakthrough_effect=GainResourceEffect("metal", 10),
    )
    FORESTRY = TechTemplate(
        name='Forestry',
        cost=25,
        advancement_level=1,
        breakthrough_effect=GainResourceEffect("wood", 10),
    )
    IRRIGATION = TechTemplate(
        name='Irrigation',
        cost=25,
        advancement_level=1,
        breakthrough_effect=GrowEffect(1),
    )
    MATHEMATICS = TechTemplate(
        name='Mathematics',
        cost=50,
        advancement_level=2,
        # TODO need to keep this label in sync with the main one, that's kinda silly. Should make it a constant.
        breakthrough_effect=PointsEffect(lambda _1, _2 : 2, "Double vps for teching this", label=f"Research (2/tech)"),
    )
    HORSEBACK_RIDING = TechTemplate(
        name='Horseback Riding',
        cost=50,
        advancement_level=2,
        breakthrough_effect=BuildUnitsEffect("Horseman", 1),
    )
    IRON_WORKING = TechTemplate(
        name='Iron Working',
        cost=45,
        advancement_level=2,
        breakthrough_effect=BuildUnitsEffect("Swordsman", 1),
    )
    CURRENCY = TechTemplate(
        name='Currency',
        cost=40,
        advancement_level=2,
        breakthrough_effect=GrowEffect(2),
    )
    ENGINEERING = TechTemplate(
        name='Engineering',
        cost=45,
        advancement_level=2,
        breakthrough_effect=GainResourceEffect("wood", 20),
    )
    CONSTRUCTION = TechTemplate(
        name='Construction',
        cost=50,
        advancement_level=2,
        breakthrough_effect=BuildBuildingEffect("Aqueduct"),
    )
    EDUCATION = TechTemplate(
        name='Education',
        cost=55,
        advancement_level=3,
        breakthrough_effect=BuildBuildingEffect("National College"),
    )
    MACHINERY = TechTemplate(
        name='Machinery',
        cost=60,
        advancement_level=3,
        breakthrough_effect=BuildUnitsEffect("Swordsman", 2),
    )
    CIVIL_SERVICE = TechTemplate(
        name='Civil Service',
        cost=60,
        advancement_level=3,
        breakthrough_effect=GainResourceEffect("city_power", 100),
    )
    CHIVALRY = TechTemplate(
        name='Chivalry',
        cost=65,
        advancement_level=3,
        breakthrough_effect=BuildUnitsEffect("Knight", 1),
    )
    COMPASS = TechTemplate(
        name='Compass',
        cost=50,
        advancement_level=3,
        breakthrough_cost=55,
        breakthrough_effect=BuildBuildingEffect("Observatory")
    )
    PHYSICS = TechTemplate(
        name='Physics',
        cost=70,
        advancement_level=3,
        breakthrough_effect=GainResourceEffect("science", 30),
    )
    PRINTING_PRESS = TechTemplate(
        name='Printing Press',
        cost=75,
        advancement_level=4,
        breakthrough_effect=FreeRandomTechEffect(age=1)
    )
    GUNPOWDER = TechTemplate(
        name='Gunpowder',
        cost=90,
        advancement_level=4,
        breakthrough_cost=105,
        breakthrough_effect=BuildUnitsEffect("Musketman", 2),
    )
    RENAISSANCE = TechTemplate(
        name='Renaissance',
        cost=0,
        advancement_level=999,
    )
    METALLURGY = TechTemplate(
        name='Metallurgy',
        cost=95,
        advancement_level=4,
        breakthrough_effect=BuildUnitBuildingEffect("Cannon"),
    )
    ARCHITECTURE = TechTemplate(
        name='Architecture',
        cost=75,
        advancement_level=4,
        breakthrough_effect=GainResourceEffect("wood", 30),
    )
    MEDICINE = TechTemplate(
        name='Medicine',
        cost=150,
        advancement_level=5,
        breakthrough_effect=GrowEffect(5),
    )
    MILITARY_SCIENCE = TechTemplate(
        name='Military Science',
        cost=150,
        advancement_level=5,
        breakthrough_effect=GainResourceEffect("metal", 60),
    )
    INDUSTRIALIZATION = TechTemplate(
        name='Industrialization',
        cost=150,
        advancement_level=5,
        # TODO need to keep this label in sync with the main one, that's kinda silly. Should make it a constant.
        breakthrough_effect=PointsEffect(lambda _1, _2 : 6, "4x vps for teching this", label=f"Research (2/tech)"),
    )
    DYNAMITE = TechTemplate(
        name='Dynamite',
        cost=170,
        advancement_level=6,
        breakthrough_effect = FreeRandomTechEffect(age=2)
    )
    MASS_MARKETS = TechTemplate(
        name='Mass Markets',
        cost=200,
        advancement_level=6,
        breakthrough_effect=BuildUnitsEffect("Rifleman", 8)
    )
    RADIO = TechTemplate(
        name='Radio',
        cost=250,
        advancement_level=6,
        breakthrough_effect=BuildUnitsEffect("Infantry", 4)
    )
    COMBINED_ARMS = TechTemplate(
        name='Combined Arms',
        cost=300,
        advancement_level=7,
        breakthrough_effect=StrengthAllUnitsEffect(2)
    )
    BALLISTICS = TechTemplate(
        name='Ballistics',
        cost=400,
        advancement_level=7,
        breakthrough_effect=BuildUnitsEffect("Rocket Launcher", 1)
    )
    MECHANIZED_AGRICULTURE = TechTemplate(
        name='Mechanized Agriculture',
        cost=450,
        advancement_level=7,
        breakthrough_effect=GainResourceEffect("food", 250),
    )
    ROCKETRY = TechTemplate(
        name='Rocketry',
        cost=500,
        advancement_level=8,
        breakthrough_effect=BuildUnitsEffect("Rocket Launcher", 3)
    )
    COMPUTERS = TechTemplate(
        name='Computers',
        cost=500,
        advancement_level=8,
        breakthrough_effect=BuildBuildingEffect("Internet")
    )
    NANOTECHNOLOGY = TechTemplate(
        name='Nanotechnology',
        cost=750,
        advancement_level=9,
        breakthrough_effect=GainResourceEffect("wood", 300)
    )     
    MEGAROBOTICS = TechTemplate(
        name='Megarobotics',
        cost=1000,
        advancement_level=9,
        breakthrough_effect=BuildUnitsEffect("Giant Death Robot", 4)
    )

    # all & by_name are copy-pasted methods to all template lists.
    # I wasn't able to set up a base class system for this
    # That handled the dynamic type properly.
    @classmethod
    def all(cls) -> Generator[TechTemplate, None, None]:
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), TechTemplate):
                yield getattr(cls, attr)
    @classmethod
    def by_name(cls, name: str) -> TechTemplate:
        for item in cls.all():
            if item.name == name:
                return item
        raise KeyError(f'No item with name {name}')
