from typing import Generator
from tech_template import TechTemplate

class TECHS():
    item_type = TechTemplate
    ARCHERY = TechTemplate(
        name= 'Archery',
        cost= 25,
        advancement_level= 1,
    )
    BRONZE_WORKING = TechTemplate(
        name= 'Bronze Working',
        cost= 25,
        advancement_level= 1,
    )
    POTTERY = TechTemplate(
        name='Pottery',
        cost=20,
        unlocks_buildings=['Granary'],
        advancement_level=1,
    )
    CODE_OF_LAWS = TechTemplate(
        name='Code of Laws',
        cost=20,
        unlocks_buildings=['Hanging Gardens'],
        advancement_level=1,
    )
    CALENDAR = TechTemplate(
        name='Calendar',
        cost=25,
        unlocks_buildings=['Temple of Artemis'],
        advancement_level=1,
    )
    THE_WHEEL = TechTemplate(
        name='The Wheel',
        cost=35,
        unlocks_buildings=['Roads'],
        advancement_level=1,
    )
    MINING = TechTemplate(
        name='Mining',
        cost=30,
        unlocks_buildings=['Mine'],
        advancement_level=1,
    )
    FORESTRY = TechTemplate(
        name='Forestry',
        cost=25,
        advancement_level=1,
        unlocks_buildings=['Lumber Mill'],
    )
    IRRIGATION = TechTemplate(
        name='Irrigation',
        cost=25,
        unlocks_buildings=['Plantation', 'Husbandry Center'],
        advancement_level=1,
    )
    WRITING = TechTemplate(
        name='Writing',
        cost=30,
        unlocks_buildings=['Library', 'Great Library'],
        advancement_level=1,
    )
    MASONRY = TechTemplate(
        name='Masonry',
        cost=30,
        unlocks_buildings=['Pyramids'],
        advancement_level=1,
    )
    MATHEMATICS = TechTemplate(
        name='Mathematics',
        cost=50,
        unlocks_buildings=['Workshop', 'Magisterium'],
        advancement_level=2,
    )
    HORSEBACK_RIDING = TechTemplate(
        name='Horseback Riding',
        cost=50,
        advancement_level=2,
    )
    IRON_WORKING = TechTemplate(
        name='Iron Working',
        cost=45,
        unlocks_buildings=['Colossus'],
        advancement_level=2,
    )
    CURRENCY = TechTemplate(
        name='Currency',
        cost=40,
        unlocks_buildings=['Petra', 'Bazaar'],
        advancement_level=2,
    )
    ENGINEERING = TechTemplate(
        name='Engineering',
        cost=45,
        unlocks_buildings=['Timberworks',  'Statue of Zeus'],
        advancement_level=2,
    )
    CONSTRUCTION = TechTemplate(
        name='Construction',
        cost=50,
        unlocks_buildings=['Aqueduct', 'Colosseum'],
        advancement_level=2,
    )
    EDUCATION = TechTemplate(
        name='Education',
        cost=55,
        unlocks_buildings=['University', 'National College'],
        advancement_level=3,
    )
    MACHINERY = TechTemplate(
        name='Machinery',
        cost=60,
        unlocks_buildings=['Ironworks'],
        advancement_level=3,
    )
    CIVIL_SERVICE = TechTemplate(
        name='Civil Service',
        cost=60,
        unlocks_buildings=['Chichen Itza'],
        advancement_level=3,
    )
    CHIVALRY = TechTemplate(
        name='Chivalry',
        cost=65,
        unlocks_buildings=[],
        advancement_level=3,
    )
    COMPASS = TechTemplate(
        name='Compass',
        cost=70,
        unlocks_buildings=['Observatory', 'Great Lighthouse'],
        advancement_level=3,
    )
    PHYSICS = TechTemplate(
        name='Physics',
        cost=70,
        unlocks_buildings=['Windmill'],
        advancement_level=3,
    )
    PRINTING_PRESS = TechTemplate(
        name='Printing Press',
        cost=75,
        unlocks_buildings=['Forbidden Palace', 'Paper Maker'],
        advancement_level=4,
    )
    GUNPOWDER = TechTemplate(
        name='Gunpowder',
        cost=90,
        unlocks_buildings=['Himeji Castle'],
        advancement_level=4,
    )
    RENAISSANCE = TechTemplate(
        name='Renaissance',
        cost=0,
        advancement_level=999,
    )
    METALLURGY = TechTemplate(
        name='Metallurgy',
        cost=95,
        unlocks_buildings=['Forge'],
        advancement_level=4,
    )
    ARCHITECTURE = TechTemplate(
        name='Architecture',
        cost=100,
        unlocks_buildings=['Notre Dame', 'Lumber Farm'],
        advancement_level=4,
    )
    MEDICINE = TechTemplate(
        name='Medicine',
        cost=110,
        unlocks_buildings=['Apothecary', 'Zoo'],
        advancement_level=5,
    )
    ECONOMICS = TechTemplate(
        name='Economics',
        cost=120,
        unlocks_buildings=['Caravansery', 'Porcelain Tower'],
        advancement_level=4,
    )
    MILITARY_SCIENCE = TechTemplate(
        name='Military Science',
        cost=130,
        unlocks_buildings=['Brandenburg Gate'],
        advancement_level=5,
    )
    RIFLING = TechTemplate(
        name='Rifling',
        cost=140,
        unlocks_buildings=['Outpost'],
        advancement_level=5,
    )
    INDUSTRIALIZATION = TechTemplate(
        name='Industrialization',
        cost=150,
        unlocks_buildings=['Factory'],
        advancement_level=5,
    )
    DYNAMITE = TechTemplate(
        name='Dynamite',
        cost=170,
        unlocks_buildings=['Railroads'],
        advancement_level=6,
    )
    RADIO = TechTemplate(
        name='Radio',
        cost=250,
        unlocks_buildings=['Stadium', 'Statue of Liberty'],
        advancement_level=6,
    )
    COMBINED_ARMS = TechTemplate(
        name='Combined Arms',
        cost=300,
        unlocks_buildings=['Kremlin'],
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
        unlocks_buildings=['Industrial Farm', 'Fast Food Chains'],
        advancement_level=7,
    )
    ROCKETRY = TechTemplate(
        name='Rocketry',
        cost=500,
        unlocks_buildings=['Apollo Program'],
        advancement_level=8,
    )
    COMPUTERS = TechTemplate(
        name='Computers',
        cost=600,
        unlocks_buildings=['Internet'],
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
        unlocks_buildings=['AGI'],
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
