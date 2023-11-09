from typing import Any


BUILDINGS: dict[str, Any] = {
    "Lumber Mill": {
        "name": "Lumber Mill",
        "type": "economy",
        "cost": 20,
        "abilities": [["IncreaseYieldsForTerrain", ["wood", 1, "forest"]]],
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