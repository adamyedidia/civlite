from template_list import TemplateList
from unit_template import UnitTemplate

class UNITS(TemplateList):
    item_type = UnitTemplate
    WARRIOR = UnitTemplate(
        name="Warrior",
        building_name="Warrior Hut",
        type="military",
        metal_cost=8,
        wood_cost=0,
        strength=6,
        movement=1,
        range=1,
        tags=["infantry"],
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
        tags=["ranged"],
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
        tags=["ranged"],
        prereq="Archery",
        abilities=[],
        great_people_names={
            "engineer": "Ashoka",
            "general_advanced": "Hippolyta",
            "general_normal": "Legolas",
            "general_horde": "Robin Hood",
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
        tags=["infantry"],
        prereq="Bronze Working",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["mounted", 4],
        }],
        great_people_names={
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
        prereq="The Wheel",
        tags=["mounted"],
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["ranged", 5],
        }],
        great_people_names={
            "general_advanced": "Thutmose III",
            "general_normal": "Ramesses II",
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
        prereq="Masonry",
        tags=["defensive"],
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
        tags=["ranged", "siege"],
        prereq="Mathematics",
        abilities=[{
            "name": "BonusNextTo",
            "numbers": ["infantry", 4],
        }],
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
        tags=["mounted"],
        prereq="Horseback Riding",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["siege", 6],
        }],
        great_people_names={
            "engineer": "King Solomon",
            "general_advanced": "Alexander the Great",
            "general_normal": "The Nazgul",  # Because there's 9 of them
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
        tags=["ranged", "mounted"],
        prereq="Horseback Riding",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["infantry", 8],
        }],
        great_people_names={
            "general_normal": "Hannibal Barca",
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
        tags=["infantry"],
        prereq="Iron Working",
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
        tags=["infantry"],
        prereq="Civil Service",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["mounted", 7],
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
        tags=["ranged"],
        prereq="Compass",
        abilities=[{
            "name": "BonusNextTo",
            "numbers": ["siege", 4],
        }],
        great_people_names={
            "general_advanced": "Henry V",
            "general_normal": "Joan of Arc",
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
        tags=["mounted"],
        prereq="Chivalry",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["ranged", 8],
        }],
        great_people_names={
            "engineer": "Charlemagne",
            "general_advanced": "Roland and Oliver",
            "general_normal": "William of Orange",
            "general_horde": "King Arthur",
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
        tags=["siege"],
        prereq="Physics",
        abilities=[{
            "name": "BonusNextTo",
            "numbers": ["infantry", 6],
        }],
        great_people_names={
            "engineer": "Saladin",
            "general_advanced": "Richard the Lionheart",
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
        tags=["infantry", "gunpowder"],
        prereq="Gunpowder",
        abilities=[],
        great_people_names={
            "general_advanced": "Alexandre Dumas",
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
        tags=["ranged", "siege", "gunpowder"],
        prereq="Metallurgy",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["defensive", 10],
        }],
        great_people_names={
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
        tags=["defensive"],
        prereq="Chivalry",
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
        tags=["mounted"],
        prereq="Military Science",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["siege", 15],
        }],
        great_people_names={
            "engineer": "Gustavus Adolphus",
            "general_advanced": "Sitting Bull",
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
        tags=["infantry", "gunpowder"],
        prereq="Rifling",
        abilities=[],
        great_people_names={
            "engineer": "Ulysses S. Grant",
            "general_advanced": "Robert E Lee",  # Issue: the civil war is generally taken to ahve been after the napoleonic wars.
            "general_normal": "Duke of Wellington",
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
        tags=["ranged", "gunpowder"],
        prereq="Industrialization",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["infantry", 15],
        }],
        great_people_names={
            "engineer": "Richard Gatling",
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
        tags=["ranged", "siege", "gunpowder"],
        prereq="Dynamite",
        abilities=[{
            "name": "BonusNextTo",
            "numbers": ["infantry", 15],
        }],
        great_people_names={
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
        tags=["infantry", "gunpowder"],
        prereq="Radio",
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
        tags=["armored"],
        prereq="Combined Arms",
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
        tags=["ranged", "gunpowder"],
        prereq="Ballistics",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["infantry", 20],
        }],
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
        tags=["ranged", "siege", "gunpowder"],
        prereq="Rocketry",
        abilities=[{
            "name": "Splash",
            "numbers": [0.6],
        }],
        great_people_names={
            "engineer": "Robert Oppenheimer",  # Issue: Tocket Launcher isn't really the same as Atomic Bomb
            "general_advanced": "Douglas MacArthur",  # Issue: Tocket Launcher isn't really the same as Atomic Bomb
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
        tags=["infantry", "gunpowder"],
        prereq="Ballistics",
        abilities=[{
            "name": "BonusAgainst",
            "numbers": ["armored", 30],
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
        tags=["armored"],
        prereq="Megarobotics",
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
        prereq="Nanotechnology",
        abilities=[{
            "name": "ConvertKills",
            "numbers": [],
        }],
    )

UNITS_BY_BUILDING_NAME = {
    unit.building_name: unit for unit in UNITS.all() if unit.building_name is not None
}