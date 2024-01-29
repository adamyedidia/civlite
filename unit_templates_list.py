UNITS = {
    "Warrior": {
        "name": "Warrior",
        "building_name": None,
        "type": "military",
        "metal_cost": 10,
        "wood_cost": 0,
        "strength": 6,
        "movement": 1,
        "range": 1,
        "ranged": False,
        "mounted": False,
        "abilities": []
    },
    "Slinger": {
        "name": "Slinger",
        "building_name": "Pebble Pile",
        "type": "military",
        "metal_cost": 5,
        "wood_cost": 3,
        "strength": 4,
        "movement": 1,
        "range": 1,
        "ranged": True,
        "prereq": None,
        "mounted": False,
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
        "ranged": True,
        "prereq": "Archery",
        "mounted": False,
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
        "ranged": False,
        "prereq": "Bronze Working",
        "mounted": False,
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
        "ranged": False,
        "prereq": "The Wheel",
        "mounted": True,
        "abilities": [{
            "name": "BonusAgainst",
            "numbers": ["ranged", 5],
        }],
    },
}

UNITS_BY_BUILDING_NAME = {
    unit_json["building_name"]: unit_json for unit_json in UNITS.values() if unit_json["building_name"] is not None
}

PRODUCTION_BUILDINGS_BY_UNIT_NAME = {
    unit_json["name"]: unit_json["building_name"] for unit_json in UNITS.values() if unit_json["building_name"] is not None
}