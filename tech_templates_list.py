from typing import Generator
from settings import RENAISSANCE_VITALITY_BOOST
from tech_template import TechTemplate

class TECHS():
    item_type = TechTemplate
    ARCHERY = TechTemplate(
        name= 'Archery',
        cost= 20,
        advancement_level= 1,
    )
    BRONZE_WORKING = TechTemplate(
        name= 'Bronze Working',
        cost= 15,
        advancement_level= 1,
    )
    POTTERY = TechTemplate(
        name='Pottery',
        cost=15,
        advancement_level=1,
    )
    THE_WHEEL = TechTemplate(
        name='The Wheel',
        cost=25,
        advancement_level=1,
    )
    MINING = TechTemplate(
        name='Mining',
        cost=25,
        advancement_level=1,
    )
    FORESTRY = TechTemplate(
        name='Forestry',
        cost=20,
        advancement_level=1,
    )
    IRRIGATION = TechTemplate(
        name='Irrigation',
        cost=20,
        advancement_level=1,
    )
    FISHING = TechTemplate(
        name='Fishing',
        cost=20,
        advancement_level=1,
    )
    MATHEMATICS = TechTemplate(
        name='Mathematics',
        cost=45,
        advancement_level=2,
    )
    HORSEBACK_RIDING = TechTemplate(
        name='Horseback Riding',
        cost=45,
        advancement_level=2,
    )
    IRON_WORKING = TechTemplate(
        name='Iron Working',
        cost=45,
        advancement_level=2,
    )
    CURRENCY = TechTemplate(
        name='Currency',
        cost=40,
        advancement_level=2,
    )
    ENGINEERING = TechTemplate(
        name='Engineering',
        cost=40,
        advancement_level=2,
    )
    CONSTRUCTION = TechTemplate(
        name='Construction',
        cost=40,
        advancement_level=2,
    )
    EDUCATION = TechTemplate(
        name='Education',
        cost=55,
        advancement_level=3,
    )
    MACHINERY = TechTemplate(
        name='Machinery',
        cost=60,
        advancement_level=3,
    )
    CIVIL_SERVICE = TechTemplate(
        name='Civil Service',
        cost=60,
        advancement_level=3,
    )
    CHIVALRY = TechTemplate(
        name='Chivalry',
        cost=65,
        advancement_level=3,
    )
    COMPASS = TechTemplate(
        name='Compass',
        cost=70,
        advancement_level=3,
    )
    PHYSICS = TechTemplate(
        name='Physics',
        cost=70,
        advancement_level=3,
    )
    PRINTING_PRESS = TechTemplate(
        name='Printing Press',
        cost=75,
        advancement_level=4,
    )
    GUNPOWDER = TechTemplate(
        name='Gunpowder',
        cost=90,
        advancement_level=4,
    )
    RENAISSANCE = TechTemplate(
        name='Renaissance',
        cost=0,
        advancement_level=999,
        text=f"Multiply your vitality by {RENAISSANCE_VITALITY_BOOST:.0%} and refresh all discarded techs.",
    )
    METALLURGY = TechTemplate(
        name='Metallurgy',
        cost=95,
        advancement_level=4,
    )
    ARCHITECTURE = TechTemplate(
        name='Architecture',
        cost=100,
        advancement_level=4,
    )
    MEDICINE = TechTemplate(
        name='Medicine',
        cost=110,
        advancement_level=5,
    )
    MILITARY_SCIENCE = TechTemplate(
        name='Military Science',
        cost=130,
        advancement_level=5,
    )
    INDUSTRIALIZATION = TechTemplate(
        name='Industrialization',
        cost=150,
        advancement_level=5,
    )
    DYNAMITE = TechTemplate(
        name='Dynamite',
        cost=170,
        advancement_level=6,
    )
    MASS_MARKETS = TechTemplate(
        name='Mass Markets',
        cost=200,
        advancement_level=6,
    )
    RADIO = TechTemplate(
        name='Radio',
        cost=250,
        advancement_level=6,
    )
    COMBINED_ARMS = TechTemplate(
        name='Combined Arms',
        cost=300,
        advancement_level=7,
    )
    BALLISTICS = TechTemplate(
        name='Ballistics',
        cost=400,
        advancement_level=7,
    )
    MECHANIZED_AGRICULTURE = TechTemplate(
        name='Mechanized Agriculture',
        cost=450,
        advancement_level=7,
    )
    ROCKETRY = TechTemplate(
        name='Rocketry',
        cost=500,
        advancement_level=8,
    )
    COMPUTERS = TechTemplate(
        name='Computers',
        cost=600,
        advancement_level=8,
    )
    NANOTECHNOLOGY = TechTemplate(
        name='Nanotechnology',
        cost=750,
        advancement_level=9,
    )     
    MEGAROBOTICS = TechTemplate(
        name='Megarobotics',
        cost=1000,
        advancement_level=9,
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
