from typing import Generator
from unit_template import UnitTemplate, UnitTag
from tech_templates_list import TECHS

class UNITS():
    WARRIOR = UnitTemplate(
        name="Warrior",
        building_name="Warrior Hut",
        metal_cost=8,
        wood_cost=0,
        strength=1,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY],
        abilities=[{
            "name": "BonusNextTo",
            "numbers": [UnitTag.INFANTRY.value],
        }],
        prereq=None,
    )
    SLINGER = UnitTemplate(
        name="Slinger",
        building_name="Pebble Pile",
        metal_cost=4,
        wood_cost=10,
        strength=1,
        movement=1,
        range=1,
        tags=[UnitTag.RANGED],
        prereq=None,
        abilities=[],
    )    
    ARCHER = UnitTemplate(
        name="Archer",
        building_name="Bowyer",
        metal_cost=8,
        wood_cost=10,
        strength=2,
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
        metal_cost=7,
        wood_cost=5,
        strength=2,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY],
        prereq=TECHS.BRONZE_WORKING,
        abilities=[{
            "name": "DoubleBonusAgainst",
            "numbers": [UnitTag.MOUNTED.value],
        }],
        great_people_names={
            "engineer": "Judah Maccabee",  # This doesn't super fit.
            "general_advanced": "Conan the Barbarian",
            "general_normal": "Lysander",
            "general_horde": "Boudicca",
        },
    )
    CHARIOT = UnitTemplate(
        name="Chariot",
        building_name="Wheelwright",
        metal_cost=12,
        wood_cost=15,
        strength=3,
        movement=1,
        range=1,
        prereq=TECHS.THE_WHEEL,
        tags=[UnitTag.MOUNTED],
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.RANGED.value],
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
        metal_cost=8,
        wood_cost=5,
        strength=4,
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
        metal_cost=12,
        wood_cost=15,
        strength=3,
        movement=1,
        range=2,
        tags=[UnitTag.SIEGE, UnitTag.RANGED],
        prereq=TECHS.MATHEMATICS,
        abilities=[{
            "name": "BonusNextTo",
            "numbers": [UnitTag.INFANTRY.value],
        }],
        great_people_names={
            "engineer": "Vitruvius",
            "general_advanced": "Odysseus",
            "general_normal": "Philip II of Macedonia",
            "general_horde": "Edward Longshanks",
        }
    )
    HORSEMAN = UnitTemplate(
        name="Horseman",
        building_name="Stable",
        metal_cost=15,
        wood_cost=15,
        strength=4,
        movement=2,
        range=1,
        tags=[UnitTag.MOUNTED],
        prereq=TECHS.HORSEBACK_RIDING,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.RANGED.value],
        }],
        great_people_names={
            "engineer": "King Solomon",
            "general_advanced": "Alexander the Great",
            "general_normal": "Riders of Rohan",
            "general_horde": "Gengis Khan",
        },
    )
    HORSE_ARCHER = UnitTemplate(
        name="Horse Archer",
        building_name="Ranged Stable",
        metal_cost=15,
        wood_cost=25,
        strength=3,
        movement=2,
        range=1,
        tags=[UnitTag.RANGED, UnitTag.MOUNTED],
        prereq=TECHS.HORSEBACK_RIDING,
        abilities=[{
            "name": "DoubleBonusAgainst",
            "numbers": [UnitTag.INFANTRY.value],
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
        metal_cost=15,
        wood_cost=15,
        strength=5,
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
        metal_cost=12,
        wood_cost=30,
        strength=4,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY],
        prereq=TECHS.CIVIL_SERVICE,
        abilities=[{
            "name": "DoubleBonusAgainst",
            "numbers": [UnitTag.MOUNTED.value],
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
        metal_cost=15,
        wood_cost=20,
        strength=5,
        movement=1,
        range=2,
        tags=[UnitTag.RANGED],
        prereq=TECHS.COMPASS,
        abilities=[],
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
        metal_cost=30,
        wood_cost=10,
        strength=12,
        movement=2,
        range=1,
        tags=[UnitTag.MOUNTED],
        prereq=TECHS.CHIVALRY,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.RANGED.value],
        }],
        great_people_names={
            "engineer": "Charlemagne",
            "general_advanced": "Roland and Oliver",
            "general_normal": "William of Orange",
            "general_horde": "Joan of Arc",
        },
    )
    TREBUCHET = UnitTemplate(
        name="Trebuchet",
        building_name="Adv. Siege Workshop",
        metal_cost=20,
        wood_cost=25,
        strength=5,
        movement=1,
        range=2,
        tags=[UnitTag.SIEGE, UnitTag.RANGED],
        prereq=TECHS.PHYSICS,
        abilities=[{
            "name": "BonusNextTo",
            "numbers": [UnitTag.INFANTRY.value],
        }],
        great_people_names={
            "engineer": "Saladin",
            "general_normal": "El Cid",
            "general_advanced": "Richard the Lionheart",
            "general_horde": "Tokugawa Ieyasu",
        },
    )
    MUSKETMAN = UnitTemplate(
        name="Musketman",
        building_name="Gunsmith",
        metal_cost=15,
        wood_cost=25,
        strength=8,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY, UnitTag.GUNPOWDER],
        prereq=TECHS.GUNPOWDER,
        abilities=[],
        great_people_names={
            "engineer": "D'Artagnan",
            "general_advanced": "Jan Zizka",
            "general_normal": "Hernan Cortes",
            "general_horde": "George Washington",
        },
    )
    CANNON = UnitTemplate(
        name="Cannon",
        building_name="Foundry",
        metal_cost=35,
        wood_cost=30,
        strength=10,
        movement=1,
        range=2,
        tags=[UnitTag.RANGED, UnitTag.SIEGE, UnitTag.GUNPOWDER],
        prereq=TECHS.METALLURGY,
        abilities=[{
            "name": "BonusNextTo",
            "numbers": [UnitTag.INFANTRY.value],
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
        metal_cost=15,
        wood_cost=6,
        strength=10,
        movement=0,
        range=1,
        tags=[UnitTag.DEFENSIVE],
        prereq=TECHS.CHIVALRY,
        abilities=[],
        great_people_names={
            "engineer": "Emperor Constantine",
            "general_advanced": "Odo of France",
            "general_normal": "William Wallace",
            "general_horde": "Louis XIV",
        },
    )
    CAVALRY = UnitTemplate(
        name="Cavalry",
        building_name="Adv. Stable",
        metal_cost=40,
        wood_cost=20,
        strength=15,
        movement=2,
        range=1,
        tags=[UnitTag.MOUNTED],
        prereq=TECHS.MILITARY_SCIENCE,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.RANGED.value],
        }],
        great_people_names={
            "engineer": "Gustavus Adolphus",
            "general_advanced": "Sitting Bull",
            "general_normal": "Geronimo",
            "general_horde": "Zorro",
        },
    )
    RIFLEMAN = UnitTemplate(
        name="Rifleman",
        building_name="Rifle Range",
        metal_cost=15,
        wood_cost=40,
        strength=10,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY, UnitTag.GUNPOWDER],
        prereq=TECHS.MEDICINE,
        abilities=[],
        great_people_names={
            "engineer": "Oliver Winchester",
            "general_normal": "Robert E Lee",
            "general_advanced": "Duke of Wellington",
            "general_horde": "Giuseppe Garibaldi",
        },
    )
    GATLING_GUN = UnitTemplate(
        name="Gatling Gun",
        building_name="Machine Shop",
        metal_cost=50,
        wood_cost=30,
        strength=15,
        movement=1,
        range=1,
        tags=[UnitTag.RANGED, UnitTag.GUNPOWDER],
        prereq=TECHS.INDUSTRIALIZATION,
        abilities=[{
            "name": "BonusAgainst",
            "numbers": [UnitTag.INFANTRY.value],
        }],
        great_people_names={
            "engineer": "Richard Gatling",
            "general_advanced": "Suleiman I",
            "general_normal": "Ulysses S. Grant",
            "general_horde": "Theodore Roosevelt"
        },
    )
    RAMPARTS = UnitTemplate(
        name="Ramparts",
        building_name="Bastion",
        metal_cost=30,
        wood_cost=10,
        strength=30,
        movement=0,
        range=1,
        tags=[UnitTag.DEFENSIVE],
        prereq=TECHS.MASS_MARKETS,
        abilities=[],
        great_people_names={
        },
    )
    ARTILLERY = UnitTemplate(
        name="Artillery",
        building_name="Adv. Foundry",
        metal_cost=60,
        wood_cost=30,
        strength=20,
        movement=1,
        range=3,
        tags=[UnitTag.RANGED, UnitTag.SIEGE, UnitTag.GUNPOWDER],
        prereq=TECHS.DYNAMITE,
        abilities=[{
            "name": "BonusNextTo",
            "numbers": [UnitTag.INFANTRY.value],
        }],
        great_people_names={
            "engineer": "Henry Shrapnel",
            "general_advanced": "Oliver Cromwell",
            "general_normal": "Paul von Hindenburg",
            "general_horde": "Woodrow Wilson",
        },
    )
    INFANTRY = UnitTemplate(
        name="Infantry",
        building_name="Barracks",
        metal_cost=30,
        wood_cost=60,
        strength=18,
        movement=1,
        range=1,
        tags=[UnitTag.INFANTRY, UnitTag.GUNPOWDER],
        prereq=TECHS.RADIO,
        abilities=[],
        great_people_names={
            "engineer": "Winston Churchill",
            "general_advanced": "Catherine the Great",
            "general_normal": "Dwight D. Eisenhower",
            "general_horde": "Joseph Stalin",
        },
    )
    TANK = UnitTemplate(
        name="Tank",
        building_name="Tank Factory",
        metal_cost=75,
        wood_cost=45,
        strength=40,
        movement=2,
        range=1,
        tags=[UnitTag.MOUNTED, UnitTag.GUNPOWDER],
        prereq=TECHS.COMBINED_ARMS,
        abilities=[],
        great_people_names={
            "engineer": "Ernest Swinton",
            "general_normal": "Erwin Rommel",
            "general_advanced": "George Patton",
            "general_horde": "Vladimir Putin",
        },
    )
    MACHINE_GUN = UnitTemplate(
        name="Machine Gun",
        building_name="Adv. Machine Shop",
        metal_cost=50,
        wood_cost=50,
        strength=20,
        movement=1,
        range=1,
        tags=[UnitTag.RANGED, UnitTag.GUNPOWDER],
        prereq=TECHS.BALLISTICS,
        abilities=[{
            "name": "DoubleBonusAgainst",
            "numbers": [UnitTag.INFANTRY.value],
        }],
        great_people_names={
            "engineer": "Uzi Gal",
            "general_normal": "John J. Pershing",
            "general_advanced": "Benito Mussolini",
            "general_horde": "Arcturus Mengsk",
        }
    )
    ROCKET_LAUNCHER = UnitTemplate(
        name="Rocket Launcher",
        building_name="Rocket Factory",
        metal_cost=80,
        wood_cost=60,
        strength=40,
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
            "general_normal": "Kim Il Sung",
            "general_horde": "General Zod",
        },
    )
    BAZOOKA = UnitTemplate(
        name="Bazooka",
        building_name="Armory",
        metal_cost=50,
        wood_cost=50,
        strength=20,
        movement=1,
        range=2,
        tags=[UnitTag.INFANTRY, UnitTag.GUNPOWDER, UnitTag.RANGED],
        prereq=TECHS.BALLISTICS,
        abilities=[{
            "name": "DoubleBonusAgainst",
            "numbers": [UnitTag.MOUNTED.value],
        }],
        great_people_names={
            "engineer": "Che Guevara",
            "general_normal": "Jayne Cobb",
            "general_advanced": "Rocket Raccoon",
            "general_horde": "The Terminator",
        }
    )
    GIANT_DEATH_ROBOT = UnitTemplate(
        name="Giant Death Robot",
        building_name="GDR Factory",
        metal_cost=100,
        wood_cost=100,
        strength=100,
        movement=3,
        range=1,
        tags=[UnitTag.GUNPOWDER],
        prereq=TECHS.MEGAROBOTICS,
        abilities=[{
            "name": "MultipleAttack",
            "numbers": [2],
        }],
        great_people_names={
            "engineer": "Tony Stark",
            "general_advanced": "Optimus Prime",
            "general_normal": "Amuro Ray",
        },
    )
    NANOSWARM = UnitTemplate(
        name="Nanoswarm",
        building_name="Nanofactory",
        metal_cost=60,
        wood_cost=20,
        strength=40,
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
            "general_advanced": "Lex Luther",
            "general_normal": "Ender Wiggin",  # Doesn't really fit but he's a good character.
        }
    )

    ZEUS = UnitTemplate(
        name="Zeus",
        metal_cost=40,
        strength=8,
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
        metal_cost=50,
        strength=32,
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
        metal_cost=80,
        strength=16,
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
        metal_cost=60,
        strength=20,
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
        metal_cost=100,
        strength=100,
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