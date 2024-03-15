from civ_template import CivTemplate
from abilities_list import CIV_ABILITIES

BARBARIAN_CIV: CivTemplate = CivTemplate(
        name="Barbarians",
        colors=("#FF0000", "#666666"),
        abilities=[],
        advancement_level=0,
)
FRESH_CIV_TEMPLATES: list[CivTemplate] = [
    CivTemplate(
        name="Pueblo",
        abilities=[CIV_ABILITIES["IncreaseCapitalYields"]("wood", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Egypt",
        abilities=[CIV_ABILITIES["ExtraVpsPerWonder"](5)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Mycenaeans",
        abilities=[CIV_ABILITIES["IncreaseCapitalYields"]("metal", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Harrapans",
        abilities=[CIV_ABILITIES["IncreaseCapitalYields"]("food", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Shang",
        abilities=[CIV_ABILITIES["IncreaseCapitalYields"]("science", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Sumer",
        abilities=[CIV_ABILITIES["IncreaseFocusYields"]("wood", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Indus",
        abilities=[CIV_ABILITIES["IncreaseFocusYields"]("food", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Minoans",
        abilities=[CIV_ABILITIES["IncreaseFocusYields"]("metal", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Babylon",
        abilities=[CIV_ABILITIES["IncreaseFocusYields"]("science", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Hittites",
        abilities=[CIV_ABILITIES["IncreaseYieldsForTerrainNextToSecondCity"]("wood", "forest", 1)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Phoenicia",
        abilities=[CIV_ABILITIES["IncreaseYieldsForTerrainNextToSecondCity"]("metal", "hills", 1)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Nazca",
        abilities=[CIV_ABILITIES["IncreaseYieldsForTerrainNextToSecondCity"]("food", "plains", 1)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Bantu",
        abilities=[CIV_ABILITIES["IncreaseYieldsForTerrainNextToSecondCity"]("food", "grassland", 1)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Olmecs",
        abilities=[CIV_ABILITIES["IncreaseYieldsForTerrain"]("wood", "jungle", 1)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Zhou",
        abilities=[CIV_ABILITIES["IncreaseYieldsForTerrain"]("metal", "desert", 1)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Nubians",
        abilities=[CIV_ABILITIES["IncreaseYieldsForTerrain"]("food", "marsh", 1)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Pama-Nguyan",
        abilities=[CIV_ABILITIES["IncreaseYieldsForTerrain"]("wood", "tundra", 1)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Assyrians",
        abilities=[CIV_ABILITIES["IncreaseYieldsForTerrain"]("metal", "mountain", 1)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Caralans",
        abilities=[CIV_ABILITIES["IncreasedStrengthForUnit"]("Warrior", 3)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Troy",
        abilities=[CIV_ABILITIES["IncreasedStrengthForUnit"]("Slinger", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Elamites",
        abilities=[CIV_ABILITIES["IncreasedStrengthForUnit"]("Archer", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Teotihuacan",
        abilities=[CIV_ABILITIES["IncreasedStrengthForUnit"]("Spearman", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Scythians",
        abilities=[CIV_ABILITIES["IncreasedStrengthForUnit"]("Chariot", 2)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Maya",
        abilities=[CIV_ABILITIES["ExtraVpsPerCityCaptured"](5)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Jomon",
        abilities=[CIV_ABILITIES["ExtraCityPower"](50)],
        advancement_level=0,
    ),
    CivTemplate(
        name="Yangshao",
        abilities=[CIV_ABILITIES["ExtraVpsPerUnitKilled"](1)],
        advancement_level=0,
    ),    
    CivTemplate(
        name="Huns",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("metal", 20),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Horse Archer", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Vikings",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("metal", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Swordsman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Goths",
        abilities=[
            CIV_ABILITIES["ExtraVpsPerCityCaptured"](5),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Swordsman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Franks",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("wood", 20),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Knight", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Cumans",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("metal", "forest", 1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Horse Archer", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Xhosa",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("wood", "grassland", 1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Archer", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Polynesia",
        abilities=[
            CIV_ABILITIES["ExtraCityPower"](100),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Slinger", 5),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Mongols",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("metal", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Horse Archer", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Aztecs",
        abilities=[
            CIV_ABILITIES["ExtraVpsPerUnitKilled"](1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Swordsman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Inca",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("wood", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Pikeman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Songhai",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("food", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Knight", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="England",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("wood", "forest", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Crossbowman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Novgorod",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("wood", "hills", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Musketman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Sweden",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("science", 40),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Rifleman", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Lithuania",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("wood", 40),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cavalry", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Brazil",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("metal", 50),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Rifleman", 7),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="United States",
        abilities=[
            CIV_ABILITIES["ExtraVpsPerCityCaptured"](5),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Infantry", 7),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="Canada",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("science", 75),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Infantry", 8),
        ],
        advancement_level=7,
    ),
    CivTemplate(
        name="Australia",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("food", 75),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Bazooka", 8),
        ],
        advancement_level=7,
    ),
    CivTemplate(
        name="Arctic Alliance",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("food", 400),
        ],
        advancement_level=9,
    ),
]

REVOLT_CIV_TEMPLATES: list[CivTemplate] = [
    CivTemplate(
        name="Romans",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("wood", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Swordsman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Greece",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("science", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Spearman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Gokturks",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("metal", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Horse Archer", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Persia",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("food", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Spearman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Han",
        abilities=[
            CIV_ABILITIES["ExtraCityPower"](100),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Crossbowman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Carthage",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("food", 20),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Horseman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Celts",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("wood", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Pikeman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Joseon",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("science", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Chariot", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Jin",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("food", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Crossbowman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Byzantines",
        abilities=[
            CIV_ABILITIES["ExtraVpsPerWonder"](5),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Trebuchet", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Gupta",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("food", "grassland", 1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Catapult", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Sukhothai",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("wood", "forest", 1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Pikeman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Srivijaya",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("wood", "hills", 1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Garrison", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Sassanids",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("metal", "plains", 1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Horseman", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Abbasids",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("metal", "hills", 1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Knight", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Umayyads",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("food", "plains", 1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Knight", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Xiongnu",
        abilities=[
            CIV_ABILITIES["ExtraVpsPerUnitKilled"](1),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Aksum",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("science", "plains", 1),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Archer", 3),
        ],
        advancement_level=1,
    ),
    CivTemplate(
        name="Majapahit",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("wood", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Pikeman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Khmer",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("wood", 30),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cannon", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Seljuks",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("metal", 30),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cannon", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Timurids",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("wood", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Knight", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Mali",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("science", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Pikeman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Mughals",
        abilities=[
            CIV_ABILITIES["ExtraVpsPerWonder"](5),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Musketman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Marathas",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("food", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cannon", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Zulu",
        abilities=[
            CIV_ABILITIES["ExtraCityPower"](150),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Pikeman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Maurya",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("food", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Musketman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Chola",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("food", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Knight", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Ming",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("science", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Crossbowman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Qin",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("science", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Crossbowman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Burgundy",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("metal", "plains", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Musketman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Bohemia",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("food", "grassland", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Militia", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Castile",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("food", "plains", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cavalry", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Venice",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("science", "grassland", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Musketman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Aragon",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("food", 3),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Pikeman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Mamluks",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("science", "plains", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Knight", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Delhi",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("food", 30),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Musketman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Bahmani",
        abilities=[
            CIV_ABILITIES["IncreaseYieldsForTerrain"]("wood", "grassland", 2),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Pikeman", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Vijayanagara",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("science", 30),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Knight", 4),
        ],
        advancement_level=2,
    ),
    CivTemplate(
        name="Iroquois",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("wood", 5),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cavalry", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Ottomans",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("food", 5),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Rifleman", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Austria-Hungary",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("science", 5),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Gatling Gun", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Russia",
        abilities=[
            CIV_ABILITIES["ExtraCityPower"](250),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cavalry", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Arabia",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("food", 40),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Knight", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Portugal",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("science", 4),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Musketman", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Spain",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("metal", 4),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cavalry", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="France",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("wood", 4),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Rifleman", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Prussia",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("metal", 4),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Artillery", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Manchu",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("science", 4),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cannon", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Poland",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("wood", 5),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cavalry", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Netherlands",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("science", 40),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Gatling Gun", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Denmark",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("metal", 40),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Gatling Gun", 5),
        ],
        advancement_level=4,
    ),
    CivTemplate(
        name="Mexico",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("food", 8),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Artillery", 7),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="United Kingdom",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("wood", 8),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Rifleman", 7),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="Indonesia",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("food", 8),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cannon", 7),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="Japan",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("metal", 8),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Swordsman", 12),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="Korea",
        abilities=[
            CIV_ABILITIES["IncreaseCapitalYields"]("science", 8),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Cannon", 7),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="Ethiopia",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("science", 8),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Rifleman", 7),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="Italy",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("metal", 40),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Artillery", 7),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="Germany",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("metal", 6),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Tank", 7),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="Comanches",
        abilities=[
            CIV_ABILITIES["ExtraVpsPerUnitKilled"](1),
        ],
        advancement_level=5,
    ),
    CivTemplate(
        name="Vietnam",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("wood", 75),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Bazooka", 8),
        ],
        advancement_level=7,
    ),
    CivTemplate(
        name="India",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("food", 150),
        ],
        advancement_level=7,
    ),
    CivTemplate(
        name="Soviet Union",
        abilities=[
            CIV_ABILITIES["ExtraVpsPerCityCaptured"](5),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Rocket Launcher", 8),
        ],
        advancement_level=7,
    ),
    CivTemplate(
        name="Communist China",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("metal", 10),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Rocket Launcher", 8),
        ],
        advancement_level=7,
    ),
    CivTemplate(
        name="Turkey",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("wood", 10),
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Infantry", 8),
        ],
        advancement_level=7,
    ),
    CivTemplate(
        name="Solaria",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("science", 200),
        ],
        advancement_level=9,
    ),
    CivTemplate(
        name="Greater EuroZone",
        abilities=[
            CIV_ABILITIES["IncreaseFocusYields"]("wood", 30),
        ],
        advancement_level=9,
    ),
    CivTemplate(
        name="Celestial Empire",
        abilities=[
            CIV_ABILITIES["StartWithResources"]("metal", 150),
        ],
        advancement_level=9,
    ),
    CivTemplate(
        name="The Machine Intelligence",
        abilities=[
            CIV_ABILITIES["IncreasedStrengthForUnit"]("Giant Death Robot", 100),
        ],
        advancement_level=9,
    ),
]

CIV_TEMPLATES: dict[str, CivTemplate] = {
    civ_template.name: civ_template 
    for civ_template in [BARBARIAN_CIV] + REVOLT_CIV_TEMPLATES + FRESH_CIV_TEMPLATES
}

print(CIV_TEMPLATES['Egypt'].primary_color)
print(CIV_TEMPLATES['Elamites'].primary_color)

