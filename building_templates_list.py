from typing import Any


BUILDINGS: dict[str, dict] = {
    "Lumber Mill": {
        "name": "Lumber Mill",
        "type": "economy",
        "cost": 20,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["wood", 1, "forest"],
        }],
        "prereq": "Forestry",
    },
    "Colossus": {
        "name": "Colossus",
        "type": "wonder",
        "cost": 80,
        "abilities": [],
        "is_wonder": True,
        "vp_reward": 5,
    },
}