from typing import Generator
from building_template import BuildingType
from building_templates_list import BUILDINGS
from civ_template import CivTemplate
from effects_list import BuildBuildingEffect, BuildUnitsEffect, GainResourceEffect, GrowEffect, PointsEffect, ResetHappinessThisCityEffect
from unit_templates_list import UNITS
import settings

def player_civs(min_advancement_level=0, max_advancement_level=9) -> Generator[CivTemplate, None, None]:
    for civ_template in CIVS.all():
        if civ_template != CIVS.BARBARIAN and min_advancement_level <= civ_template.advancement_level <= max_advancement_level:
            yield civ_template

class CIVS():
    # all & by_name are copy-pasted methods to all template lists.
    # I wasn't able to set up a base class system for this
    # That handled the dynamic type properly.
    @classmethod
    def all(cls) -> Generator[CivTemplate, None, None]:
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), CivTemplate):
                yield getattr(cls, attr)
    @classmethod
    def by_name(cls, name: str) -> CivTemplate:
        for item in cls.all():
            if item.name == name:
                return item
        raise KeyError(f'No item with name {name}')

    BARBARIAN = CivTemplate(
        name="Barbarians",
        abilities=[],
        colors=("#FF0000", "#666666",),
        advancement_level=0,
    )

    PUEBLO = CivTemplate(
        name="Pueblo",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 2]
        }],
        advancement_level=0,
    )
    EGPYT = CivTemplate(
        name="Egypt",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [5]
        }],
        advancement_level=0,
    )
    MYCENAEANS = CivTemplate(
        name="Mycenaeans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 2]
        }],
        advancement_level=0,
    )
    HARRAPANS = CivTemplate(
        name="Harrapans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 2]
        }],
        advancement_level=0,
    )
    SHANG = CivTemplate(
        name="Shang",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 2]
        }],
        advancement_level=0,
    )
    SUMER = CivTemplate(
        name="Sumer",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 2]
        }],
        advancement_level=0,
    )
    INDUS = CivTemplate(
        name="Indus",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 2]
        }],
        advancement_level=0,
    )
    MINOANS = CivTemplate(
        name="Minoans",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 2]
        }],
        advancement_level=0,
    )
    BABYLON = CivTemplate(
        name="Babylon",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 2]
        }],
        advancement_level=0,
    )
    CARALANS = CivTemplate(
        name="Caralans",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [4, "Warrior", 2]
        }],
        advancement_level=0,
    )
    TROY = CivTemplate(
        name="Troy",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [4, "Slinger", 2]
        }],
        advancement_level=0,
    )    
    NUBIANS = CivTemplate(
        name="Nubians",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [2, "Archer", 3]
        }],
        advancement_level=0,
    )
    TEOTIHUACAN = CivTemplate(
        name="Teotihuacan",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [2, "Spearman", 3]
        }],
        advancement_level=0,
    )
    SCYTHIANS = CivTemplate(
        name="Scythians",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [2, "Chariot", 3]
        }],
        advancement_level=0,
    )
    MAYA = CivTemplate(
        name="Maya",
        abilities=[{
            "name": "ExtraVpsPerCityCaptured",
            "numbers": [5]
        }],
        advancement_level=0,
    )
    JOMON = CivTemplate(
        name="Jomon",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [100]
        }],
        advancement_level=0,
    )
    YANGSHAO = CivTemplate(
        name="Yangshao",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": [1]
        }],
        advancement_level=0,
    )
    OLMECS = CivTemplate(
        name="Olmecs",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("food", 15)]
        }],
        advancement_level=0,
    )
    HITTITES = CivTemplate(
        name="Hittites",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("metal", 15)]
        }],
        advancement_level=0,
    )
    PHOENICIANS = CivTemplate(
        name="Phoenicians",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("science", 15)]
        }],
        advancement_level=0,
    )
    ELAMITES = CivTemplate(
        name="Elamites",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("wood", 15)]
        }],
        advancement_level=0,
    )
    LYDIA = CivTemplate(
        name="Lydia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, PointsEffect(lambda city, game_state: 5, "Gain 4 points", "Lydians")]
        }],
        advancement_level=0,
    )
    THRACE = CivTemplate(
        name="Thrace",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, BuildUnitsEffect(UNITS.HORSE_ARCHER, 1)]
        }],
        advancement_level=0,
    )
    ROMANS = CivTemplate(
        name="Romans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Swordsman", 1],
        }],
        advancement_level=1,
    )
    GREECE = CivTemplate(
        name="Greece",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Spearman", 1],
        }],
        advancement_level=1,
    )
    GOKTURKS = CivTemplate(
        name="Gokturks",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horse Archer", 1],
        }],
        advancement_level=1,
    )
    PERSIA = CivTemplate(
        name="Persia",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Spearman", 1],
        }],
        advancement_level=1,
    )
    HAN = CivTemplate(
        name="Han",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [100],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman", 1],
        }],
        advancement_level=1,
    )
    HUNS = CivTemplate(
        name="Huns",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horse Archer", 1],
        }],
        advancement_level=1,
    )
    CARTHAGE = CivTemplate(
        name="Carthage",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, BuildUnitsEffect(UNITS.HORSEMAN, 1)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horseman", 1],
        }],
        advancement_level=1,
    )
    GOTHS = CivTemplate(
        name="Goths",
        abilities=[{
            "name": "ExtraVpsPerCityCaptured",
            "numbers": [5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Swordsman", 1],
        }],
        advancement_level=1,
    )
    FRANKS = CivTemplate(
        name="Franks",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 20],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight", 1],
        }],
        advancement_level=1,
    )
    CELTS = CivTemplate(
        name="Celts",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman", 1],
        }],
        advancement_level=1,
    )
    JOSEON = CivTemplate(
        name="Joseon",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Chariot", 1],
        }],
        advancement_level=1,
    )
    JIN = CivTemplate(
        name="Jin",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman", 1],
        }],
        advancement_level=1,
    )
    VIKINGS = CivTemplate(
        name="Vikings",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Swordsman", 1],
        }],
        advancement_level=1,
    )
    BYZANTINES = CivTemplate(
        name="Byzantines",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Trebuchet", 1],
        }],
        advancement_level=1,
    )
    GUPTA = CivTemplate(
        name="Gupta",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["urban"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Catapult", 1],
        }],
        advancement_level=1,
    )
    POLYNESIA = CivTemplate(
        name="Polynesia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GrowEffect(1)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Slinger", 2],
        }],
        advancement_level=1,
    )
    SUKHOTHAI = CivTemplate(
        name="Sukhothai",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["unit"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman", 1],
        }],
        advancement_level=1,
    )
    SRIVIJAYA = CivTemplate(
        name="Srivijaya",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("wood", 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Garrison", 1],
        }],
        advancement_level=1,
    )
    SASSANIDS = CivTemplate(
        name="Sassanids",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["rural"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horseman", 1],
        }],
        advancement_level=1,
    )
    ABBASIDS = CivTemplate(
        name="Abbasids",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("science", 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight", 1],
        }],
        advancement_level=1,
    )
    UMAYYADS = CivTemplate(
        name="Umayyads",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, BuildUnitsEffect(UNITS.KNIGHT, 1)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight", 1],
        }],
        advancement_level=1,
    )
    XHOSA = CivTemplate(
        name="Xhosa",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Archer", 1],
        }],
        advancement_level=1,
    )
    XIONGNU = CivTemplate(
        name="Xiongnu",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": [1],
        }],
        advancement_level=1,
    )
    AKSUM = CivTemplate(
        name="Aksum",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Archer", 1],
        }],
        advancement_level=1,
    )
    CUMANS = CivTemplate(
        name="Cumans",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horse Archer", 1],
        }],
        advancement_level=1,
    )
    MAJAPAHIT = CivTemplate(
        name="Majapahit",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman", 2],
        }],
        advancement_level=2,
    )
    KHMER = CivTemplate(
        name="Khmer",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 30],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon", 2],
        }],
        advancement_level=2,
    )
    SELJUKS = CivTemplate(
        name="Seljuks",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 30],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon", 2],
        }],
        advancement_level=2,
    )
    TIMURIDS = CivTemplate(
        name="Timurids",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight", 2],
        }],
        advancement_level=2,
    )
    MALI = CivTemplate(
        name="Mali",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman", 2],
        }],
        advancement_level=2,
    )
    SONGHAI = CivTemplate(
        name="Songhai",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight", 2],
        }],
        advancement_level=2,
    )
    MONGOLS = CivTemplate(
        name="Mongols",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horse Archer", 1],
        }],
        advancement_level=2,
    )
    AZTECS = CivTemplate(
        name="Aztecs",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": [1],
        }],
        advancement_level=2,
    )
    INCA = CivTemplate(
        name="Inca",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman", 2],
        }],
        advancement_level=2,
    )
    MUGHALS = CivTemplate(
        name="Mughals",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman", 2],
        }],
        advancement_level=2,
    )
    MARATHAS = CivTemplate(
        name="Marathas",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon", 2],
        }],
        advancement_level=2,
    )
    ZULU = CivTemplate(
        name="Zulu",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [150],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman", 2],
        }],
        advancement_level=2,
    )
    MAURYA = CivTemplate(
        name="Maurya",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman", 2],
        }],
        advancement_level=2,
    )
    CHOLA = CivTemplate(
        name="Chola",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight", 2],
        }],
        advancement_level=2,
    )
    MING = CivTemplate(
        name="Ming",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman", 2],
        }],
        advancement_level=2,
    )
    QIN = CivTemplate(
        name="Qin",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman", 2],
        }],
        advancement_level=2,
    )
    BURGUNDY = CivTemplate(
        name="Burgundy",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect('metal', 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman", 2],
        }],
        advancement_level=2,
    )
    BOHEMIA = CivTemplate(
        name="Bohemia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect('wood', 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Militia", 2],
        }],
        advancement_level=2,
    )
    ENGLAND = CivTemplate(
        name="England",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["urban"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman", 2],
        }],
        advancement_level=2,
    )
    NOVGOROD = CivTemplate(
        name="Novgorod",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["rural"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman", 2],
        }],
        advancement_level=2,
    )
    CASTILE = CivTemplate(
        name="Castile",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["unit"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry", 2],
        }],
        advancement_level=2,
    )
    VENICE = CivTemplate(
        name="Venice",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, BuildBuildingEffect(BUILDINGS.HARBOR)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman", 2],
        }],
        advancement_level=2,
    )
    ARAGON = CivTemplate(
        name="Aragon",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman", 2],
        }],
        advancement_level=2,
    )
    MAMLUKS = CivTemplate(
        name="Mamluks",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect('science', 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight", 2],
        }],
        advancement_level=2,
    )
    DELHI = CivTemplate(
        name="Delhi",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 30],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman", 2],
        }],
        advancement_level=2,
    )
    BAHMANI = CivTemplate(
        name="Bahmani",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, ResetHappinessThisCityEffect()],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman", 2],
        }],
        advancement_level=2,
    )
    VIJAYANAGARA = CivTemplate(
        name="Vijayanagara",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 30],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight", 2],
        }],
        advancement_level=2,
    )
    IROQUOIS = CivTemplate(
        name="Iroquois",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry", 4],
        }],
        advancement_level=4,
    )
    OTTOMANS = CivTemplate(
        name="Ottomans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman", 4],
        }],
        advancement_level=4,
    )
    AUSTRIA_HUNGARY = CivTemplate(
        name="Austria-Hungary",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Gatling Gun", 4],
        }],
        advancement_level=4,
    )
    SWEDEN = CivTemplate(
        name="Sweden",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman", 4],
        }],
        advancement_level=4,
    )
    RUSSIA = CivTemplate(
        name="Russia",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [250],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry", 4],
        }],
        advancement_level=4,
    )
    ARABIA = CivTemplate(
        name="Arabia",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight", 4],
        }],
        advancement_level=4,
    )
    PORTUGAL = CivTemplate(
        name="Portugal",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman", 4],
        }],
        advancement_level=4,
    )
    SPAIN = CivTemplate(
        name="Spain",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry", 4],
        }],
        advancement_level=4,
    )
    FRANCE = CivTemplate(
        name="France",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman", 4],
        }],
        advancement_level=4,
    )
    PRUSSIA = CivTemplate(
        name="Prussia",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Artillery", 4],
        }],
        advancement_level=4,
    )
    MANCHU = CivTemplate(
        name="Manchu",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon", 4],
        }],
        advancement_level=4,
    )
    POLAND = CivTemplate(
        name="Poland",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry", 4],
        }],
        advancement_level=4,
    )
    LITHUANIA = CivTemplate(
        name="Lithuania",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry", 4],
        }],
        advancement_level=4,
    )
    NETHERLANDS = CivTemplate(
        name="Netherlands",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Gatling Gun", 4],
        }],
        advancement_level=4,
    )
    DENMARK = CivTemplate(
        name="Denmark",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Gatling Gun", 4],
        }],
        advancement_level=4,
    )
    BRAZIL = CivTemplate(
        name="Brazil",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 50],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman", 6],
        }],
        advancement_level=5,
    )
    UNITED_STATES = CivTemplate(
        name="United States",
        abilities=[{
            "name": "ExtraVpsPerCityCaptured",
            "numbers": [5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Infantry", 6],
        }],
        advancement_level=5,
    )
    MEXICO = CivTemplate(
        name="Mexico",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Artillery", 6],
        }],
        advancement_level=5,
    )
    UNITED_KINGDOM = CivTemplate(
        name="United Kingdom",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman", 6],
        }],
        advancement_level=5,
    )
    INDONESIA = CivTemplate(
        name="Indonesia",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon", 6],
        }],
        advancement_level=5,
    )
    JAPAN = CivTemplate(
        name="Japan",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Swordsman", 10],
        }],
        advancement_level=5,
    )
    KOREA = CivTemplate(
        name="Korea",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 6],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon", 6],
        }],
        advancement_level=5,
    )
    ETHIOPIA = CivTemplate(
        name="Ethiopia",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 60],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman", 6],
        }],
        advancement_level=5,
    )    
    ITALY = CivTemplate(
        name="Italy",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Artillery", 6],
        }],
        advancement_level=5,
    )
    GERMANY = CivTemplate(
        name="Germany",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 6],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Tank", 6],
        }],
        advancement_level=5,
    )
    COMANCHES = CivTemplate(
        name="Comanches",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": [1],
        }],
        advancement_level=5,
    )
    CANADA = CivTemplate(
        name="Canada",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 75],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Infantry", 8],
        }],
        advancement_level=7,
    )
    AUSTRALIA = CivTemplate(
        name="Australia",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 75],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Bazooka", 8],
        }],
        advancement_level=7,
    )
    VIETNAM = CivTemplate(
        name="Vietnam",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 75],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Bazooka", 8],
        }],
        advancement_level=7,
    )
    INDIA = CivTemplate(
        name="India",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 150],
        }],
        advancement_level=7,
    )
    SOVIET_UNION = CivTemplate(
        name="Soviet Union",
        abilities=[{
            "name": "ExtraVpsPerCityCaptured",
            "numbers": [5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rocket Launcher", 8],
        }],
        advancement_level=7,
    )
    COMMUNIST_CHINA = CivTemplate(
        name="Communist China",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 10],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rocket Launcher", 8],
        }],
        advancement_level=7,
    )
    TURKEY = CivTemplate(
        name="Turkey",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 10],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Infantry", 8],
        }],
        advancement_level=7,
    )
    SOLARIA = CivTemplate(
        name="Solaria",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 200],
        }],
        advancement_level=10,
    )
    ARCTIC_ALLIANCE = CivTemplate(
        name="Arctic Alliance",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 400],
        }],
        advancement_level=9,
    )
    GREATER_EURO_ZONE = CivTemplate(
        name="Greater EuroZone",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 30],
        }],
        advancement_level=9,
    )
    CELESTIAL_EMPIRE = CivTemplate(
        name="Celestial Empire",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 150],
        }],
        advancement_level=9,
    )
    THE_MACHINE_INTELLIGENCE = CivTemplate(
        name="The Machine Intelligence",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Giant Death Robot", 100],
        }],
        advancement_level=9,
    )


_num_a0_civs = len([civ for civ in CIVS.all() if civ.advancement_level ==0])
assert _num_a0_civs >= settings.MAX_PLAYERS * settings.NUM_STARTING_LOCATION_OPTIONS, f"There are only {_num_a0_civs} age 0 civs, but we need {settings.MAX_PLAYERS * settings.NUM_STARTING_LOCATION_OPTIONS} for a maximum size game to fit."