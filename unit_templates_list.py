UNITS = {
    "Scout": {
        "name": "Scout",
        "building_name": None,
        "type": "military",
        "metal_cost": 5,
        "wood_cost": 0,
        "strength": 2,
        "movement": 2,
        "range": 1,
        "tags": [],
        "abilities": [],
    },
    "Warrior": {
        "name": "Warrior",
        "building_name": None,
        "type": "military",
        "metal_cost": 8,
        "wood_cost": 0,
        "strength": 6,
        "movement": 1,
        "range": 1,
        "tags": ["infantry"],
        "abilities": [],
    },
    "Slinger": {
        "name": "Slinger",
        "building_name": "Pebble Pile",
        "type": "military",
        "metal_cost": 5,
        "wood_cost": 5,
        "strength": 4,
        "movement": 1,
        "range": 1,
        "tags": ["ranged"],
        "prereq": None,
        "abilities": [],
    },    
    "Archer": {
        "name": "Archer",
        "building_name": "Bowyer",
        "type": "military",
        "metal_cost": 7,
        "wood_cost": 10,
        "strength": 7,
        "movement": 1,
        "range": 1,
        "tags": ["ranged"],
        "prereq": "Archery",
        "abilities": [],
    },
    "Spearman": {
        "name": "Spearman",
        "building_name": "Spear Lodge",
        "type": "military",
        "metal_cost": 7,
        "wood_cost": 10,
        "strength": 8,
        "movement": 1,
        "range": 1,
        "tags": ["infantry"],
        "prereq": "Bronze Working",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["mounted", 4],
        }],
    },
    "Chariot": {
        "name": "Chariot",
        "building_name": "Wheelwright",
        "type": "military",
        "metal_cost": 10,
        "wood_cost": 10,
        "strength": 10,
        "movement": 1,
        "range": 1,
        "prereq": "The Wheel",
        "tags": ["mounted"],
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["ranged", 5],
        }],
    },
    "Garrison": {
        "name": "Garrison",
        "building_name": "Walls",
        "type": "military",
        "metal_cost": 8,
        "wood_cost": 3,
        "strength": 12,
        "movement": 0,
        "range": 1,
        "prereq": "Masonry",
        "tags": ["defensive"],
        "abilities": [],
    },
    "Catapult": {
        "name": "Catapult",
        "building_name": "Siege Workshop",
        "type": "military",
        "metal_cost": 12,
        "wood_cost": 15,
        "strength": 8,
        "movement": 1,
        "range": 2,
        "tags": ["ranged", "siege"],
        "prereq": "Mathematics",
        "abilities": [{
            "name": "BonusNextTo",
            "numbers": ["infantry", 4],
        }],
    },
    "Horseman": {
        "name": "Horseman",
        "building_name": "Stable",
        "type": "military",
        "metal_cost": 12,
        "wood_cost": 15,
        "strength": 12,
        "movement": 2,
        "range": 1,
        "tags": ["mounted"],
        "prereq": "Horseback Riding",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["siege", 6],
        }],
    },
    "Horse Archer": {
        "name": "Horse Archer",
        "building_name": "Ranged Stable",
        "type": "military",
        "metal_cost": 15,
        "wood_cost": 20,
        "strength": 10,
        "movement": 2,
        "range": 1,
        "tags": ["ranged", "mounted"],
        "prereq": "Horseback Riding",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["infantry", 5],
        }],
    },
    "Swordsman": {
        "name": "Swordsman",
        "building_name": "Smithy",
        "type": "military",
        "metal_cost": 16,
        "wood_cost": 16,
        "strength": 16,
        "movement": 1,
        "range": 1,
        "tags": ["infantry"],
        "prereq": "Iron Working",
        "abilities": [],
    },
    "Pikeman": {
        "name": "Pikeman",
        "building_name": "Pikesmith",
        "type": "military",
        "metal_cost": 12,
        "wood_cost": 20,
        "strength": 14,
        "movement": 1,
        "range": 1,
        "tags": ["infantry"],
        "prereq": "Civil Service",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["mounted", 7],
        }],
    },
    "Crossbowman": {
        "name": "Crossbowman",
        "building_name": "Crossbow Range",
        "type": "military",
        "metal_cost": 15,
        "wood_cost": 20,
        "strength": 14,
        "movement": 1,
        "range": 1,
        "tags": ["ranged"],
        "prereq": "Machinery",
        "abilities": [{
            "name": "BonusNextTo",
            "numbers": ["siege", 4],
        }],
    },
    "Knight": {
        "name": "Knight",
        "building_name": "Tournament Grounds",
        "type": "military",
        "metal_cost": 25,
        "wood_cost": 20,
        "strength": 16,
        "movement": 3,
        "range": 1,
        "tags": ["mounted"],
        "prereq": "Chivalry",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["ranged", 8],
        }],
    },
    "Trebuchet": {
        "name": "Trebuchet",
        "building_name": "Adv. Siege Workshop",
        "type": "military",
        "metal_cost": 20,
        "wood_cost": 25,
        "strength": 12,
        "movement": 1,
        "range": 2,
        "tags": ["siege"],
        "prereq": "Physics",
        "abilities": [{
            "name": "BonusNextTo",
            "numbers": ["infantry", 6],
        }],
    },
    "Musketman": {
        "name": "Musketman",
        "building_name": "Gunsmith",
        "type": "military",
        "metal_cost": 15,
        "wood_cost": 25,
        "strength": 20,
        "movement": 1,
        "range": 1,
        "tags": ["infantry", "gunpowder"],
        "prereq": "Gunpowder",
        "abilities": [],
    },
    "Hussar": {
        "name": "Hussar",
        "building_name": "Ducal Stable",
        "type": "military",
        "metal_cost": 15,
        "wood_cost": 25,
        "strength": 15,
        "movement": 4,
        "range": 1,
        "tags": ["mounted"],
        "prereq": "Steel",
        "abilities": [{
            "name": "BonusNextTo",
            "numbers": ["gunpowder", 5],
        }],
    },
    "Cannon": {
        "name": "Cannon",
        "building_name": "Foundry",
        "type": "military",
        "metal_cost": 30,
        "wood_cost": 30,
        "strength": 20,
        "movement": 1,
        "range": 2,
        "tags": ["ranged", "siege", "gunpowder"],
        "prereq": "Metallurgy",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["defensive", 10],
        }],
    },
    "Militia": {
        "name": "Militia",
        "building_name": "Castle",
        "type": "military",
        "metal_cost": 15,
        "wood_cost": 6,
        "strength": 20,
        "movement": 0,
        "range": 1,
        "tags": ["defensive"],
        "prereq": "Chivalry",
        "abilities": [],
    },
    "Cavalry": {
        "name": "Cavalry",
        "building_name": "Adv. Stable",
        "type": "military",
        "metal_cost": 30,
        "wood_cost": 25,
        "strength": 25,
        "movement": 1,
        "range": 1,
        "tags": ["mounted"],
        "prereq": "Military Science",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["siege", 15],
        }],
    },
    "Rifleman": {
        "name": "Rifleman",
        "building_name": "Rifle Range",
        "type": "military",
        "metal_cost": 20,
        "wood_cost": 35,
        "strength": 30,
        "movement": 1,
        "range": 1,
        "tags": ["infantry", "gunpowder"],
        "prereq": "Rifling",
        "abilities": [],
    },
    "Gatling Gun": {
        "name": "Gatling Gun",
        "building_name": "Machine Shop",
        "type": "military",
        "metal_cost": 35,
        "wood_cost": 30,
        "strength": 25,
        "movement": 1,
        "range": 1,
        "tags": ["ranged", "gunpowder"],
        "prereq": "Industrialization",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["infantry", 15],
        }],
    },
    "Artillery": {
        "name": "Artillery",
        "building_name": "Adv. Foundry",
        "type": "military",
        "metal_cost": 45,
        "wood_cost": 45,
        "strength": 30,
        "movement": 1,
        "range": 2,
        "tags": ["ranged", "siege", "gunpowder"],
        "prereq": "Dynamite",
        "abilities": [{
            "name": "BonusNextTo",
            "numbers": ["infantry", 15],
        }],
    },
    "Infantry": {
        "name": "Infantry",
        "building_name": "Barracks",
        "type": "military",
        "metal_cost": 25,
        "wood_cost": 50,
        "strength": 45,
        "movement": 1,
        "range": 1,
        "tags": ["infantry", "gunpowder"],
        "prereq": "Military Science",
        "abilities": [],
    },
    "Tank": {
        "name": "Tank",
        "building_name": "Tank Factory",
        "type": "military",
        "metal_cost": 60,
        "wood_cost": 45,
        "strength": 60,
        "movement": 2,
        "range": 1,
        "tags": ["armored"],
        "prereq": "Combined Arms",
        "abilities": [],
    },
    "Machine Gun": {
        "name": "Machine Gun",
        "building_name": "Adv. Machine Shop",
        "type": "military",
        "metal_cost": 50,
        "wood_cost": 40,
        "strength": 40,
        "movement": 1,
        "range": 1,
        "tags": ["ranged", "gunpowder"],
        "prereq": "Ballistics",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["infantry", 20],
        }],
    },
    "Rocket Launcher": {
        "name": "Rocket Launcher",
        "building_name": "Rocket Factory",
        "type": "military",
        "metal_cost": 80,
        "wood_cost": 60,
        "strength": 50,
        "movement": 1,
        "range": 3,
        "tags": ["ranged", "siege", "gunpowder"],
        "prereq": "Rocketry",
        "abilities": [{
            "name": "Splash",
            "numbers": [0.6],
        }],
    },
    "Bazooka": {
        "name": "Bazooka",
        "building_name": "Armory",
        "type": "military",
        "metal_cost": 40,
        "wood_cost": 50,
        "strength": 45,
        "movement": 1,
        "range": 2,
        "tags": ["infantry", "gunpowder"],
        "prereq": "Rocketry",
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["armored", 30],
        }],
    },
    "Giant Death Robot": {
        "name": "Giant Death Robot",
        "building_name": "GDR Factory",
        "type": "military",
        "metal_cost": 100,
        "wood_cost": 100,
        "strength": 100,
        "movement": 1,
        "range": 1,
        "tags": ["armored"],
        "prereq": "Megarobotics",
        "abilities": [],
    },
    "Nanoswarm": {
        "name": "Nanoswarm",
        "building_name": "Nanofactory",
        "type": "military",
        "metal_cost": 60,
        "wood_cost": 80,
        "strength": 50,
        "movement": 1,
        "range": 1,
        "tags": [],
        "prereq": "Nanotechnology",
        "abilities": [{
            "name": "ConvertKills",
            "numbers": [],
        }],
    },
}

UNITS_BY_BUILDING_NAME = {
    unit_json["building_name"]: unit_json for unit_json in UNITS.values() if unit_json["building_name"] is not None
}

PRODUCTION_BUILDINGS_BY_UNIT_NAME = {
    unit_json["name"]: unit_json["building_name"] for unit_json in UNITS.values() if unit_json["building_name"] is not None
}