from typing import Any


BUILDINGS: dict[str, dict] = {
    "Lumber Mill": {
        "name": "Lumber Mill",
        "type": "economy",
        "cost": 15,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["wood", 1, "forest"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["wood", 1, "jungle"],
        }],
        "prereq": "Forestry",
    },
    "Granary": {
        "name": "Granary",
        "type": "economy",
        "cost": 10,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 1, "plains"],
        }],
        "prereq": "Pottery",
    },
    "Library": {
        "name": "Library",
        "type": "science",
        "cost": 10,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["science", 1, "tundra"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["science", 1, "desert"],
        }],
        "prereq": "Writing",
    },
    "Mine": {
        "name": "Mine",
        "type": "economy",
        "cost": 15,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 1, "hills"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 1, "mountain"],
        }],
        "prereq": "Mining",
    },
    "Plantation": {
        "name": "Plantation",
        "type": "economy",
        "cost": 15,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 1, "grassland"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 1, "marsh"],
        }],
        "prereq": "Irrigation",
    },
    "Aqueduct": {
        "name": "Aqueduct",
        "type": "economy",
        "cost": 20,
        "abilities": [{
            "name": "CityGrowthCostReduction",
            "numbers": [0.5],
        }],
        "prereq": "Construction",
    },
    "Colosseum": {
        "name": "Colosseum",
        "type": "economy",
        "cost": 10,
        "prereq": "Construction",
        "abilities": [],
        "vp_reward": 1,
    },
    "Workshop": {
        "name": "Workshop",
        "type": "economy",
        "cost": 15,
        "abilities": [{
            "name": "IncreaseYieldsInCity",
            "numbers": ["metal", 4],
        }],
        "prereq": "Mathematics",
    },
    "University": {
        "name": "University",
        "type": "science",
        "cost": 25,
        "abilities": [{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["science", 1],
        }],
        "prereq": "Education",
    },
    "Factory": {
        "name": "Factory",
        "type": "economy",
        "cost": 50,
        "abilities": [{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["metal", 1],
        }, {
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["wood", 1],
        }],
        "prereq": "Industrialization",
    },
    "Observatory": {
        "name": "Observatory",
        "type": "science",
        "cost": 15,
        "abilities": [{
            "name": "IncreaseYieldsInCity",
            "numbers": ["science", 4],
        }],
        "prereq": "Compass",
    },
    "Paper Maker": {
        "name": "Paper Maker",
        "type": "science",
        "cost": 15,
        "abilities": [{
            "name": "IncreaseYieldsInCity",
            "numbers": ["wood", 4],
        }],
        "prereq": "Paper",
    },
    "Zoo": {
        "name": "Zoo",
        "type": "economy",
        "cost": 20,
        "prereq": "Medicine",
        "abilities": [],
        "vp_reward": 1,
    },
    "Stadium": {
        "name": "Stadium",
        "type": "economy",
        "cost": 40,
        "prereq": "Radio",
        "abilities": [],
        "vp_reward": 1,
    },

    "Windmill": {
        "name": "Windmill",
        "type": "economy",
        "cost": 30,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 2, "tundra"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 2, "grassland"],
        }],
        "prereq": "Physics",
    },
    "Forge": {
        "name": "Forge",
        "type": "economy",
        "cost": 30,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 2, "mountain"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 2, "plains"],
        }],
        "prereq": "Metallurgy",
    },
    "Lumber Farm": {
        "name": "Lumber Farm",
        "type": "economy",
        "cost": 30,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["wood", 2, "forest"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["wood", 2, "hills"],
        }],
        "prereq": "Architecture",
    },
    "Apothecary": {
        "name": "Apothecary",
        "type": "economy",
        "cost": 30,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 2, "marsh"],
        }, {
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["food", 2, "jungle"],
        }],
        "prereq": "Medicine",
    },
    'Caravansery': {
        "name": "Caravansery",
        "type": "economy",
        "cost": 15,
        "abilities": [{
            "name": "IncreaseYieldsForTerrain",
            "numbers": ["metal", 2, 'desert'],
        }],
        "prereq": "Economics",
    },

    "Ironworks": {
        "name": "Ironworks",
        "type": "economy",
        "cost": 20,
        "abilities": [{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["metal", 2],
        }],
        "prereq": "Iron Working",
        "is_national_wonder": True,
        "prereq": "Engineering",
    },
    "National College": {
        "name": "National College",
        "type": "science",
        "cost": 20,
        "abilities": [{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["science", 2],
        }],
        "is_national_wonder": True,
        "prereq": "Education",
    },
    "Timberworks": {
        "name": "Timberworks",
        "type": "economy",
        "cost": 20,
        "abilities": [{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["wood", 2],
        }],
        "is_national_wonder": True,
        "prereq": "Machinery",
    },
    "Husbandry Center": {
        "name": "Husbandry Center",
        "type": "economy",
        "cost": 20,
        "abilities": [{
            "name": "IncreaseFocusYieldsPerPopulation",
            "numbers": ["food", 2],
        }],
        "is_national_wonder": True,
        "prereq": "Chivalry",
    },
    'Industrial Farm': {
        "name": "Industrial Farm",
        "type": "economy",
        "cost": 60,
        "abilities": [{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["food", 2],
        }],
        "prereq": "Mechanized Agriculture",
    },
    "Internet": {
        "name": "Internet",
        "type": "economy",
        "cost": 100,
        "abilities": [{
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["food", 2],
        }, {
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["wood", 2],
        }, {
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["metal", 2],
        }, {
            "name": "IncreaseYieldsPerPopulation",
            "numbers": ["science", 2],
        }],        
        "prereq": "Computers",
    },
    "Hanging Gardens": {
        "name": "Hanging Gardens",
        "type": "economy",
        "cost": 50,
        "abilities": [{
            "name": "IncreaseYieldsInCity",
            "numbers": ["food", 5],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Code of Laws",
    },
    "Pyramids": {
        "name": "Pyramids",
        "type": "wonder",
        "cost": 50,
        "abilities": [
            {
                "name": "GainCityPower",
                "numbers": [100],
            },
        ],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Masonry",
    },
    "Temple of Artemis": {
        "name": "Temple of Artemis",
        "type": "economy",
        "cost": 50,
        "abilities": [{
            "name": "GainFreeUnits",
            "numbers": ["Archer", 3],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Calendar",
    },
    "Colossus": {
        "name": "Colossus",
        "type": "economy",
        "cost": 60,
        "abilities": [{
            "name": "IncreaseYieldsInCity",
            "numbers": ["metal", 5],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Iron Working",
    },
    "Statue of Zeus": {
        "name": "Statue of Zeus",
        "type": "economy",
        "cost": 60,
        "abilities": [{
            "name": "NewUnitsGainBonusStrength",
            "numbers": [1],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Currency",
    },
    "Great Library": {
        "name": "Great Library",
        "type": "science",
        "cost": 60,
        "abilities": [{
            "name": "IncreaseYieldsInCity",
            "numbers": ["science", 5],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Writing",
    },
    "Petra": {
        "name": "Petra",
        "type": "economy",
        "cost": 70,
        "abilities": [{
            "name": "DoubleYieldsForTerrainInCity",
            "numbers": ["desert"],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Currency",
    },
    "Chichen Itza": {
        "name": "Chichen Itza",
        "type": "economy",
        "cost": 80,
        "abilities": [{
            "name": "IncreasePopulationOfNewCities",
            "numbers": [3],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Civil Service",
    },
    "Great Lighthouse": {
        "name": "Great Lighthouse",
        "type": "economy",
        "cost": 90,
        "abilities": [{
            "name": "IncreaseYieldsInCity",
            "numbers": ["food", 10],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Compass",
    },
    'Forbidden Palace': {
        "name": "Forbidden Palace",
        "type": "economy",
        "cost": 100,
        "abilities": [{
            "name": "GainCityPower",
            "numbers": [200],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Printing Press",
    },
    "Himeji Castle": {
        "name": "Himeji Castle",
        "type": "economy",
        "cost": 110,
        "abilities": [{
            "name": "ExistingUnitsGainBonusStrength",
            "numbers": [2],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Gunpowder",
    },
    "Notre Dame": {
        "name": "Notre Dame",
        "type": "economy",
        "cost": 120,
        "abilities": [{
            "name": "IncreaseYieldsInCity",
            "numbers": ["wood", 15],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Architecture",
    },
    "Porcelain Tower": {
        "name": "Porcelain Tower",
        "type": "science",
        "cost": 140,
        "abilities": [{
            "name": "ExtraVpsForTechs",
            "numbers": [1],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Medicine",
    },
    "Brandenburg Gate": {
        "name": "Brandenburg Gate",
        "type": "economy",
        "cost": 150,
        "abilities": [{
            "name": "NewUnitsGainBonusStrength",
            "numbers": [3],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Military Science",
    },
    "Statue of Liberty": {
        "name": "Statue of Liberty",
        "type": "economy",
        "cost": 250,
        "abilities": [{
            "name": "ExtraVpsForCityGrowth",
            "numbers": [1],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Radio",
    },
    "Kremlin": {
        "name": "Kremlin",
        "type": "economy",
        "cost": 300,
        "abilities": [{
            "name": "ExtraVpsForCityCapture",
            "numbers": [10],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Communism",
    },
    "Fast Food Chains": {
        "name": "Fast Food Chains",
        "type": "economy",
        "cost": 350,
        "abilities": [{
            "name": "TripleCityPopulation",
            "numbers": [],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Mechanized Agriculture",
    },
    "Apollo Program": {
        "name": "Apollo Program",
        "type": "economy",
        "cost": 400,
        "abilities": [{
            "name": "ExtraVpsForTechs",
            "numbers": [5],
        }],
        "is_wonder": True,
        "vp_reward": 5,
        "prereq": "Rocketry",
    },
    'AGI': {
        "name": "AGI",
        "type": "economy",
        "cost": 750,
        "abilities": [{
            "name": "EndTheGame",
            "numbers": [],
        }],
        "is_wonder": True,
        "vp_reward": 10,
        "prereq": "Megarobotics",
    },
}