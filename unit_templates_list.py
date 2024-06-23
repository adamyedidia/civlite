from typing import Generator
from unit_template import UnitTemplate, UnitTag
from tech_templates_list import TECHS

class UNITS():
    WARRIOR = UnitTemplate(
        name="Warrior",
        building_name="Warrior Hut",
        type="military",
        metal_cost=8,
        wood_cost=0,
        strength=6,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY],
        abilities=[],
        prereq=None,
    )
    SLINGER = UnitTemplate(
        name="Slinger",
        building_name="Pebble Pile",
        type="military",
        metal_cost=4,
        wood_cost=10,
        strength=5,
        movement=1,
        range=1,
        tags=[UnitTag.RANGED],
        prereq=None,
        abilities=[],
    )    
    ARCHER = UnitTemplate(
        name="Archer",
        building_name="Bowyer",
        type="military",
        metal_cost=7,
        wood_cost=10,
        strength=7,
        movement=1,
        range=2,
        tags=[UnitTag.RANGED],
        prereq=TECHS.ARCHERY,
        abilities=[],
        great_people_names={
            "engineer": "Ashoka",
            "general_advanced": "Hippolyta",
            "general_normal": "Legolas",
            "general_horde": "Vercingetorix",
        },
    )
    SPEARMAN = UnitTemplate(
        name="Spearman",
        building_name="Spear Lodge",
        type="military",
        metal_cost=7,
        wood_cost=10,
        strength=8,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY],
        prereq=TECHS.BRONZE_WORKING,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.MOUNTED.value, 4],
        }],
        great_people_names={
            "engineer": "Judah Maccabee",  # This doesn't super fit.
            "general_advanced": "Achilles and Patroclus",
            "general_normal": "Lysander",
            "general_horde": "Boudicca",
        },
    )
    CHARIOT = UnitTemplate(
        name="Chariot",
        building_name="Wheelwright",
        type="military",
        metal_cost=10,
        wood_cost=10,
        strength=10,
        movement=1,
        range=1,
        prereq=TECHS.THE_WHEEL,
        tags=[UnitTag.MOUNTED],
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.RANGED.value, 5],
        }],
        great_people_names={
            "engineer": "Apollo",
            "general_advanced": "Thutmose III",
            "general_normal": "Ramesses II",
            "general_horde": "Cyrus the Great",
        },
    )
    GARRISON = UnitTemplate(
        name="Garrison",
        building_name="Walls",
        type="military",
        metal_cost=8,
        wood_cost=3,
        strength=12,
        movement=0,
        range=1,
        prereq=TECHS.MINING,
        tags=[UnitTag.DEFENSIVE],
        abilities=[],
        great_people_names={
            "engineer": "Bran the Builder",
            "general_advanced": "Hector of Troy",
            "general_normal": "Leonidas",
            "general_horde": "King Theoden",
        },
    )
    CATAPULT = UnitTemplate(
        name="Catapult",
        building_name="Siege Workshop",
        type="military",
        metal_cost=12,
        wood_cost=15,
        strength=10,
        movement=1,
        range=2,
        tags=[UnitTag.SIEGE, UnitTag.RANGED],
        prereq=TECHS.MATHEMATICS,
        abilities=[{
            "name": "BonusNextTo",
            "numbers": [UnitTag.INFANTRY.value, 4],
        }],
        great_people_names={
            "engineer": "Vitruvius",
            "general_normal": "Philip II of Macedonia",
            "general_horde": "Edward Longshanks",
        }
    )
    HORSEMAN = UnitTemplate(
        name="Horseman",
        building_name="Stable",
        type="military",
        metal_cost=12,
        wood_cost=15,
        strength=12,
        movement=2,
        range=1,
        tags=[UnitTag.MOUNTED],
        prereq=TECHS.HORSEBACK_RIDING,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.SIEGE.value, 6],
        }],
        great_people_names={
            "engineer": "King Solomon",
            "general_advanced": "Alexander the Great",
            # "general_normal": "The Nazgul",  # Because there's 9 of them  # Now there's 6
            "general_horde": "Gengis Khan",
        },
    )
    HORSE_ARCHER = UnitTemplate(
        name="Horse Archer",
        building_name="Ranged Stable",
        type="military",
        metal_cost=12,
        wood_cost=20,
        strength=10,
        movement=2,
        range=1,
        tags=[UnitTag.RANGED, UnitTag.MOUNTED],
        prereq=TECHS.HORSEBACK_RIDING,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.INFANTRY.value, 8],
        }],
        great_people_names={
            "engineer": "Hannibal Barca",
            "general_normal": "Khalid ibn al-Walid",
            "general_advanced": "Tomyris",
            "general_horde": "Attila the Hun",
        },
    )
    SWORDSMAN = UnitTemplate(
        name="Swordsman",
        building_name="Smithy",
        type="military",
        metal_cost=16,
        wood_cost=16,
        strength=16,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY],
        prereq=TECHS.IRON_WORKING,
        abilities=[],
        great_people_names={
            "engineer": "Julius Caesar",
            "general_advanced": "The Horatii",
            "general_normal": "Scipio Africanus",
            "general_horde": "Aragorn",
        },
    )
    PIKEMAN = UnitTemplate(
        name="Pikeman",
        building_name="Pikesmith",
        type="military",
        metal_cost=12,
        wood_cost=20,
        strength=14,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY],
        prereq=TECHS.CIVIL_SERVICE,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.MOUNTED.value, 7],
        }],
        great_people_names={
            "engineer": "Shaka Zulu",
            "general_normal": "Frederick Barbarossa",
            "general_advanced": "Sun Tzu",
            "general_horde": "Montezuma",
        },
    )
    CROSSBOWMAN = UnitTemplate(
        name="Crossbowman",
        building_name="Crossbow Range",
        type="military",
        metal_cost=15,
        wood_cost=20,
        strength=13,
        movement=1,
        range=2,
        tags=[UnitTag.RANGED],
        prereq=TECHS.COMPASS,
        abilities=[{
            "name": "BonusNextTo",
            "numbers": [UnitTag.SIEGE.value, 4],
        }],
        great_people_names={
            "engineer": "Zhuge Liang",
            "general_horde": "Henry V",
            "general_advanced": "Robin Hood",
            "general_normal": "The Black Prince",
        },
    )
    KNIGHT = UnitTemplate(
        name="Knight",
        building_name="Tournament Grounds",
        type="military",
        metal_cost=25,
        wood_cost=20,
        strength=16,
        movement=2,
        range=1,
        tags=[UnitTag.MOUNTED],
        prereq=TECHS.CHIVALRY,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.RANGED.value, 8],
        }],
        great_people_names={
            "engineer": "Charlemagne",
            "general_advanced": "Roland and Oliver",
            "general_normal": "William of Orange",
        },
    )
    TREBUCHET = UnitTemplate(
        name="Trebuchet",
        building_name="Adv. Siege Workshop",
        type="military",
        metal_cost=20,
        wood_cost=25,
        strength=14,
        movement=1,
        range=2,
        tags=[UnitTag.SIEGE, UnitTag.RANGED],
        prereq=TECHS.PHYSICS,
        abilities=[{
            "name": "BonusNextTo",
            "numbers": [UnitTag.INFANTRY.value, 6],
        }],
        great_people_names={
            "engineer": "Saladin",
            "general_advanced": "Richard the Lionheart",
            "general_normal": "Joan of Arc",
            "general_horde": "Tokugawa Ieyasu",
        },
    )
    MUSKETMAN = UnitTemplate(
        name="Musketman",
        building_name="Gunsmith",
        type="military",
        metal_cost=15,
        wood_cost=25,
        strength=20,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY, UnitTag.GUNPOWDER],
        prereq=TECHS.GUNPOWDER,
        abilities=[],
        great_people_names={
            "general_normal": "Hernan Cortes",
            "general_horde": "George Washington",
        },
    )
    CANNON = UnitTemplate(
        name="Cannon",
        building_name="Foundry",
        type="military",
        metal_cost=30,
        wood_cost=30,
        strength=24,
        movement=1,
        range=2,
        tags=[UnitTag.RANGED, UnitTag.SIEGE, UnitTag.GUNPOWDER],
        prereq=TECHS.METALLURGY,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.DEFENSIVE.value, 10],
        }],
        great_people_names={
            "engineer": "Berthold the Black",
            "general_horde": "Napolean Bonaparte",
            "general_normal": "Jack Sparrow",
            "general_advanced": "Mehmet II",
        },
    )
    MILITIA = UnitTemplate(
        name="Militia",
        building_name="Castle",
        type="military",
        metal_cost=15,
        wood_cost=6,
        strength=20,
        movement=0,
        range=1,
        tags=[UnitTag.DEFENSIVE],
        prereq=TECHS.CHIVALRY,
        abilities=[],
        great_people_names={
            "general_advanced": "Odo of France",
            "general_normal": "William Wallace",
            "general_horde": "El Cid",
        },
    )
    CAVALRY = UnitTemplate(
        name="Cavalry",
        building_name="Adv. Stable",
        type="military",
        metal_cost=30,
        wood_cost=25,
        strength=25,
        movement=2,
        range=1,
        tags=[UnitTag.MOUNTED],
        prereq=TECHS.MILITARY_SCIENCE,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.SIEGE.value, 15],
        }],
        great_people_names={
            "engineer": "Gustavus Adolphus",
            "general_advanced": "Sitting Bull",
            "general_normal": "Jeb Stuart",
        },
    )
    RIFLEMAN = UnitTemplate(
        name="Rifleman",
        building_name="Rifle Range",
        type="military",
        metal_cost=20,
        wood_cost=35,
        strength=30,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY, UnitTag.GUNPOWDER],
        prereq=TECHS.MEDICINE,
        abilities=[],
        great_people_names={
            "general_normal": "Robert E Lee",
            "general_advanced": "Duke of Wellington",
        },
    )
    GATLING_GUN = UnitTemplate(
        name="Gatling Gun",
        building_name="Machine Shop",
        type="military",
        metal_cost=35,
        wood_cost=30,
        strength=25,
        movement=1,
        range=1,
        tags=[UnitTag.RANGED, UnitTag.GUNPOWDER],
        prereq=TECHS.INDUSTRIALIZATION,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.INFANTRY.value, 15],
        }],
        great_people_names={
            "engineer": "Richard Gatling",
            "general_normal": "Ulysses S. Grant",
            "general_horde": "Theodore Roosevelt"
        },
    )
    ARTILLERY = UnitTemplate(
        name="Artillery",
        building_name="Adv. Foundry",
        type="military",
        metal_cost=45,
        wood_cost=45,
        strength=30,
        movement=1,
        range=3,
        tags=[UnitTag.RANGED, UnitTag.SIEGE, UnitTag.GUNPOWDER],
        prereq=TECHS.DYNAMITE,
        abilities=[{
            "name": "BonusNextTo",
            "numbers": [UnitTag.INFANTRY.value, 15],
        }],
        great_people_names={
            "engineer": "Henry Shrapnel",
            "general_advanced": "Oliver Cromwell",
        },
    )
    INFANTRY = UnitTemplate(
        name="Infantry",
        building_name="Barracks",
        type="military",
        metal_cost=25,
        wood_cost=50,
        strength=45,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY, UnitTag.GUNPOWDER],
        prereq=TECHS.RADIO,
        abilities=[],
        great_people_names={
            "engineer": "Winston Churchill",
            "general_advanced": "Catherine the Great",
            "general_normal": "Dwight D. Eisenhower",
        },
    )
    TANK = UnitTemplate(
        name="Tank",
        building_name="Tank Factory",
        type="military",
        metal_cost=60,
        wood_cost=45,
        strength=60,
        movement=2,
        range=1,
        tags=[UnitTag.ARMORED],
        prereq=TECHS.COMBINED_ARMS,
        abilities=[],
        great_people_names={
            "general_normal": "Erwin Rommel",
            "general_advanced": "George Patton", 
        },
    )
    MACHINE_GUN = UnitTemplate(
        name="Machine Gun",
        building_name="Adv. Machine Shop",
        type="military",
        metal_cost=50,
        wood_cost=40,
        strength=40,
        movement=1,
        range=1,
        tags=[UnitTag.RANGED, UnitTag.GUNPOWDER],
        prereq=TECHS.BALLISTICS,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.INFANTRY.value, 20],
        }],
        great_people_names={
            "general_normal": "John J. Pershing", 
        }
    )
    ROCKET_LAUNCHER = UnitTemplate(
        name="Rocket Launcher",
        building_name="Rocket Factory",
        type="military",
        metal_cost=80,
        wood_cost=60,
        strength=50,
        movement=1,
        range=3,
        tags=[UnitTag.RANGED, UnitTag.SIEGE, UnitTag.GUNPOWDER],
        prereq=TECHS.ROCKETRY,
        abilities=[{
            "name": "Splash",
            "numbers": [0.6],
        }],
        great_people_names={
            "engineer": "Robert Oppenheimer",  # Issue: Rocket Launcher isn't really the same as Atomic Bomb
            "general_advanced": "Douglas MacArthur",  # Issue: Rocket Launcher isn't really the same as Atomic Bomb
        },
    )
    BAZOOKA = UnitTemplate(
        name="Bazooka",
        building_name="Armory",
        type="military",
        metal_cost=40,
        wood_cost=50,
        strength=45,
        movement=1,
        range=2,
        tags=[UnitTag.INFANTRY, UnitTag.GUNPOWDER, UnitTag.RANGED],
        prereq=TECHS.BALLISTICS,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.ARMORED.value, 30],
        }],
        great_people_names={
            "general_normal": "Jayne Cobb",
            "general_advanced": "Rocket Raccoon",
        }
    )
    GIANT_DEATH_ROBOT = UnitTemplate(
        name="Giant Death Robot",
        building_name="GDR Factory",
        type="military",
        metal_cost=100,
        wood_cost=100,
        strength=100,
        movement=3,
        range=1,
        tags=[UnitTag.ARMORED],
        prereq=TECHS.MEGAROBOTICS,
        abilities=[],
        great_people_names={
            "engineer": "Tony Stark",
            "general_advanced": "Optimus Prime",
            "general_normal": "Amuro Ray",
        },
    )
    NANOSWARM = UnitTemplate(
        name="Nanoswarm",
        building_name="Nanofactory",
        type="military",
        metal_cost=60,
        wood_cost=80,
        strength=50,
        movement=1,
        range=1,
        tags=[],
        prereq=TECHS.NANOTECHNOLOGY,
        abilities=[{
            "name": "ConvertKills",
            "numbers": [],
        }],
        great_people_names={
            "engineer": "Ray Kurzweil",
            "general_normal": "Ender Wiggin",  # Doesn't really fit but he's a good character.
        }
    )

    ZEUS = UnitTemplate(
        name="Zeus",
        type="military",
        metal_cost=40,
        strength=20,
        movement=1,
        range=3,
        tags=[UnitTag.WONDROUS, UnitTag.RANGED],
        abilities=[],

        building_name=None,
        prereq=None,
        wood_cost=0,
    )

    COLOSSUS = UnitTemplate(
        name="Colossus",
        type="military",
        metal_cost=50,
        strength=50,
        movement=0,
        range=1,
        tags=[UnitTag.WONDROUS, UnitTag.DEFENSIVE, UnitTag.INFANTRY],
        abilities=[],

        building_name=None,
        prereq=None,
        wood_cost=0,
    )

    SIR_LANCELOT = UnitTemplate(
        name="Sir Lancelot",
        type="military",
        metal_cost=80,
        strength=30,
        movement=3,
        range=1,
        tags=[UnitTag.WONDROUS, UnitTag.MOUNTED],
        abilities=[{
            "name": "MultipleAttack",
            "numbers": [2],
        }],

        building_name=None,
        prereq=None,
        wood_cost=0,
    )

    ARCHANGEL = UnitTemplate(
        name="Archangel",
        type="military",
        metal_cost=60,
        strength=35,
        movement=2,
        range=1,
        tags=[UnitTag.WONDROUS],
        abilities=[{
            "name": "HealAllies",
            "numbers": [],
        }],

        building_name=None,
        prereq=None,
        wood_cost=0,
    )

    ATOMIC_BOMB = UnitTemplate(
        name="Atomic Bomb",
        type="military",
        metal_cost=100,
        strength=200,
        movement=1,
        range=6,
        tags=[UnitTag.WONDROUS, UnitTag.RANGED, UnitTag.SIEGE, UnitTag.GUNPOWDER],
        abilities=[{
            "name": "Splash",
            "numbers": [1.0],
        }, {
            "name": "Missile",
            "numbers": [],
        }],
        building_name=None,
        prereq=None,
        wood_cost=0,
    )

    IRONMAN = UnitTemplate(
        name="Ironman",
        type="military",
        metal_cost=300,
        strength=150,
        movement=2,
        range=3,
        tags=[UnitTag.WONDROUS, UnitTag.RANGED, UnitTag.GUNPOWDER],
        abilities=[{
            "name": "MultipleAttack",
            "numbers": [4],
        }, {
            "name": "Splash",
            "numbers": [0.6],
        }],

        building_name=None,
        prereq=None,
        wood_cost=0,
    )

    # all & by_name are copy-pasted methods to all template lists.
    # I wasn't able to set up a base class system for this
    # That handled the dynamic type properly.
    @classmethod
    def all(cls) -> Generator[UnitTemplate, None, None]:
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), UnitTemplate):
                yield getattr(cls, attr)
    @classmethod
    def by_name(cls, name: str) -> UnitTemplate:
        for item in cls.all():
            if item.name == name:
                return item
        raise KeyError(f'No item with name {name}')

UNITS_BY_BUILDING_NAME = {
    unit.building_name: unit for unit in UNITS.all() if unit.building_name is not None
}