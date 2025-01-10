from typing import Generator
from building_template import BuildingType
from building_templates_list import BUILDINGS
from civ_template import CivTemplate
from effects_list import BuildBuildingEffect, BuildUnitsEffect, FreeRandomTechEffect, GainResourceEffect, GrowEffect, PointsEffect, ResetHappinessThisCityEffect, StealPopEffect
from region import Region
from unit_templates_list import UNITS
import settings

def player_civs(min_advancement_level=0, max_advancement_level=9, regions: set[Region] = set(Region)) -> Generator[CivTemplate, None, None]:
    for civ_template in CIVS.all():
        if civ_template != CIVS.BARBARIAN and min_advancement_level <= civ_template.advancement_level <= max_advancement_level and civ_template.region in regions:
            yield civ_template

def find_civ_pool(n, advancement_level_target, target_regions: set[Region], civs_already_in_game: list[CivTemplate]) -> list[CivTemplate]:
    decline_choice_big_civ_pool = []
    amounts_found = {}
    for max_advancement_level in range(advancement_level_target, 11):
        # Try in order of (correct age correct region, age -1 correct region, correct age any region, age -2 correct region, age -1 any region, age -3 correct region, ...)
        for min_advancement_level in range(advancement_level_target, -1, -1):
            for search_correct_regions in [True, False]:
                if search_correct_regions:
                    search_regions = target_regions
                    min_search_age = min_advancement_level
                else:
                    search_regions = set(Region)
                    min_search_age = min_advancement_level + 1
                # print(f"Searching for {n} civs at {min_search_age=}, {max_advancement_level=}, {search_regions=}")
                decline_choice_big_civ_pool: list[CivTemplate] = [
                    civ for civ in player_civs(min_advancement_level=min_search_age, max_advancement_level=max_advancement_level, regions=search_regions) 
                    if civ not in civs_already_in_game]

                if len(decline_choice_big_civ_pool) >= n:
                    return decline_choice_big_civ_pool
                amounts_found[(max_advancement_level, min_advancement_level, len(search_regions))] = len(decline_choice_big_civ_pool)
    else:
        raise ValueError(f"Couldn't find enough civs to decline ({n}) in {target_regions}.\n\nargs were {advancement_level_target=}, {target_regions=}, {civs_already_in_game=}.\n\nFinal amounts found was {amounts_found}")

CIV_COLORS = {
    "Barbarians": ("#404040", "#f50021"),
    "Pueblo": ("#ed0000", "#ffffff"),
    "Egypt": ("#ce1126", "#404040"),
    "Mycenaeans": ("#008800", "#ffffff"),
    "Harrapans": ("#ff0000", "#404040"),
    "Shang": ("#229e45", "#f8e509"),
    "Sumer": ("#32cbfe", "#ffb012"),
    "Indus": ("#00aad4", "#ffcc00"),
    "Minoans": ("#2a6b11", "#66950c"),
    "Babylon": ("#125dd3", "#eea831"),
    "Caralans": ("#ffffff", "#909090"),
    "Troy": ("#2194de", "#ce1029"),
    "Nubians": ("#078930", "#0000be"),
    "Teotihuacan": ("#100df6", "#fee422"),
    "Akkad": ("#1c3b67", "#ffff00"),
    "Assyria": ("#ffffff", "#0000be"),
    "Jomon": ("#f6b02e", "#fad083"),
    "Yangshao": ("#e80000", "#ffffff"),
    "Longshan": ("#0099cc", "#ffe513"),
    "Olmecs": ("#e20212", "#00ffff"),
    "Hittites": ("#b62dd7", "#ffb200"),
    "Phoenicia": ("#0066ff", "#cc0000"),
    "Elamites": ("#800080", "#ffffff"),
    "Lydia": ("#001ea1", "#d81c3f"),
    "Thrace": ("#003788", "#ffffff"),
    "Polynesia": ("#003887", "#ffffff"),
    "Scythians": ("#fed100", "#404040"),
    "Sparta": ("#ffff00", "#ff5700"),
    "Athens": ("#ffffff", "#0061f3"),
    "Persia": ("#410c72", "#c73d30"),
    "Macedonia": ("#0078f0", "#0179ef"),
    "Maurya": ("#007d41", "#ffc400"),
    "Chola": ("#ffa101", "#404040"),
    "Qin": ("#404040", "#ffffff"),
    "Romans": ("#cc0000", "#ffd90c"),
    "Parthia": ("#630085", "#e7bc2a"),
    "Carthage": ("#0066ff", "#cc0000"),
    "Han": ("#e20212", "#b3a400"),
    "Gupta": ("#ffff00", "#aa0000"),
    "Huns": ("#f9f9f9", "#e7c03b"),
    "Franks": ("#0000be", "#ffd700"),
    "Maya": ("#364a90", "#ffffff"),
    "Celts": ("#59a859", "#ffff00"),
    "Jin": ("#44aa00", "#404040"),
    "Byzantines": ("#c8100b", "#f8c420"),
    "Srivijaya": ("#ff0000", "#00318d"),
    "Umayyads": ("#0099cc", "#009933"),
    "Abbasids": ("#ce1126", "#ffffff"),
    "Vikings": ("#ffffff", "#404040"),
    "Khmer": ("#187e37", "#cdd5cf"),
    "Seljuks": ("#2d96ff", "#ffffff"),
    "Castile": ("#cc0000", "#bda944"),
    "England": ("#ffffff", "#cc0000"),
    "Novgorod": ("#ffffff", "#0087dd"),
    "Portugal": ("#ff0000", "#009900"),
    "Aragon": ("#fcdd09", "#da121a"),
    "Bohemia": ("#ffffff", "#0080ff"),
    "Mongols": ("#e90649", "#0082d1"),
    "Delhi": ("#10931c", "#fc000f"),
    "Mali": ("#ce1126", "#fcd116"),
    "Ethiopia": ("#298c08", "#ef2118"),
    "Denmark": ("#d00c33", "#ffffff"),
    "Sukhothai": ("#e70000", "#ffffff"),
    "Mamluks": ("#fcd116", "#fcd116"),
    "Inca": ("#df0000", "#ffa000"),
    "Austria-Hungary": ("#df0000", "#ffffff"),
    "Majapahit": ("#e70011", "#ffffff"),
    "Ottomans": ("#ff0000", "#008000"),
    "Vijayanagara": ("#002c93", "#ffc726"),
    "Bahmani": ("#0070ff", "#00be00"),
    "Ming": ("#ed1c24", "#00a651"),
    "Timurids": ("#404040", "#ffffff"),
    "Joseon": ("#ffe000", "#ff0003"),
    "Aztecs": ("#dc3632", "#404040"),
    "Songhai": ("#ffffff", "#3399ff"),
    "Spain": ("#c60b1e", "#ffc400"),
    "Iroquois": ("#821a7b", "#ffffff"),
    "Poland": ("#df0000", "#ffffff"),
    "Mughals": ("#306030", "#d40d0d"),
    "United Kingdom": ("#cc0000", "#0000be"),
    "Marathas": ("#ffffff", "#ff9600"),
    "Prussia": ("#ffffff", "#404040"),
    "Comanches": ("#0000ff", "#c80000"),
    "Russia": ("#ffffff", "#fe0101"),
    "United States": ("#bd3d44", "#ffffff"),
    "Mexico": ("#0b7226", "#bc0000"),
    "Zulu": ("#ffffff", "#b10c0c"),
    "Japan": ("#ffffff", "#d30000"),
    "Sweden": ("#00447b", "#ffcc00"),
    "Brazil": ("#229e45", "#f8e509"),
    "Italy": ("#01bd01", "#ffffff"),
    "Canada": ("#ff0000", "#ffffff"),
    "Germany": ("#404040", "#ffce00"),
    "Korea": ("#ffffff", "#ff1600"),
    "Australia": ("#0000be", "#cc0000"),
    "Soviet Union": ("#cc0000", "#cd0400"),
    "Turkey": ("#e30a17", "#ffffff"),
    "Indonesia": ("#e70011", "#ffffff"),
    "India": ("#e77300", "#329203"),
    "Communist China": ("#e20212", "#f6e204"),
    "Unified Latin America": ("#75aadb", "#ffffff"),
    "NATO": ("#00358a", "#214ca9"),
    "Arctic Alliance": ("#fe6500", "#ffffff"),
    "Greater EuroZone": ("#0000be", "#0101bd"),
    "Celestial Empire": ("#ff0000", "#009933"),
    "The Machine Intelligence": ("#404040", "#26d009"),
    "Solaria": ("#165044", "#7fcc2b"),
}
# Bespoke choices to prevent civs from looking like barbarians
OVERWRITE_CIV_COLORS = {
    "Egypt": ("#c09300", "#ce1126"),
    "Harrapans": ("#404040", "#ffff00"),
}

print(CIV_COLORS["Harrapans"])

CIV_COLORS.update(OVERWRITE_CIV_COLORS)
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
        advancement_level=-1,
        region=Region.BARBARIAN,
    )

    PUEBLO = CivTemplate(
        # About 1000 AD -- move later?
        name="Pueblo",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 2]
        }],
        advancement_level=0,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Pueblo"]
    )
    EGPYT = CivTemplate(
        name="Egypt",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [5]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Egypt"]
    )
    MYCENAEANS = CivTemplate(
        name="Mycenaeans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 2]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Mycenaeans"]
    )
    HARRAPANS = CivTemplate(
        name="Harrapans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 2]
        }],
        advancement_level=0,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Harrapans"]
    )
    SHANG = CivTemplate(
        name="Shang",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 2]
        }],
        advancement_level=0,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Shang"]
    )
    SUMER = CivTemplate(
        name="Sumer",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 2]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Sumer"]
    )
    INDUS = CivTemplate(
        name="Indus",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 2]
        }],
        advancement_level=0,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Indus"]
    )
    MINOANS = CivTemplate(
        name="Minoans",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 2]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Minoans"]
    )
    BABYLON = CivTemplate(
        name="Babylon",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 2]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Babylon"]
    )
    CARALANS = CivTemplate(
        name="Caralans",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [4, "Warrior", 2]
        }],
        advancement_level=0,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Caralans"]
    )
    TROY = CivTemplate(
        name="Troy",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [4, "Slinger", 2]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Troy"]
    )    
    NUBIANS = CivTemplate(
        name="Nubians",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [2, "Archer", 3]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Nubians"]
    )
    TEOTIHUACAN = CivTemplate(
        # late 1st millenim BC -- could go to a1?
        name="Teotihuacan",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [2, "Spearman", 3]
        }],
        advancement_level=0,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Teotihuacan"]
    )
    AKKAD = CivTemplate(
        name="Akkad",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 2]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Akkad"]
    )
    ASSYRIA = CivTemplate(
        name="Assyria",
        abilities=[{
            "name": "ExtraVpsPerCityCaptured",
            "numbers": [5]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Assyria"]
    )
    JOMON = CivTemplate(
        name="Jomon",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [100]
        }],
        advancement_level=0,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Jomon"]
    )
    YANGSHAO = CivTemplate(
        name="Yangshao",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": ["ranged", 1]
        }],
        advancement_level=0,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Yangshao"]
    )
    LONGSHAN = CivTemplate(
        name="Longshan",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, PointsEffect(lambda city, game_state: 6, "Gain 6 points", "Longshan")]
        }],
        advancement_level=0,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Longshan"]
    )
    OLMECS = CivTemplate(
        name="Olmecs",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("food", 10)]
        }],
        advancement_level=0,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Olmecs"]
    )
    HITTITES = CivTemplate(
        name="Hittites",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("metal", 10)]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Hittites"]
    )
    PHOENICIA = CivTemplate(
        name="Phoenicia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("science", 10)]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Phoenicia"]
    )
    ELAMITES = CivTemplate(
        name="Elamites",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("wood", 10)]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Elamites"]
    )
    LYDIA = CivTemplate(
        name="Lydia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, PointsEffect(lambda city, game_state: 2, "Gain 2 points", "Lydia")]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Lydia"]
    )
    THRACE = CivTemplate(
        name="Thrace",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, BuildUnitsEffect(UNITS.HORSE_ARCHER, 1)]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Thrace"]
    )


    POLYNESIA = CivTemplate(
        # Depends what you mean
        name="Polynesia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GrowEffect(1)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Slinger"],
        }],
        advancement_level=1,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Polynesia"]
    )
    SCYTHIANS = CivTemplate(
        # 9th century BC
        name="Scythians",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": ["mounted", 1]
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horse Archer"]
        }],
        advancement_level=1,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Scythians"]
    )
    SPARTA = CivTemplate(
        # 7th century BC ish
        name="Sparta",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Spearman"],
        }],
        advancement_level=1,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Sparta"]
    )
    ATHENS = CivTemplate(
        # 5th century BC
        name="Athens",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Swordsman"],
        }],
        advancement_level=1,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Athens"]
    )
    PERSIA = CivTemplate(
        # 550 BC
        name="Persia",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Archer"],
        }],
        advancement_level=1,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Persia"]
    )
    MACEDONIA = CivTemplate(
        # 4th century BC
        name="Macedonia",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Chariot"],
        }],
        advancement_level=1,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Macedonia"]
    )
    MAURYA = CivTemplate(
        # 322 BC
        name="Maurya",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [50],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horseman"],
        }],
        advancement_level=1,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Maurya"]
    )
    CHOLA = CivTemplate(
        # 3rd century BC
        name="Chola",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Catapult"],
        }],
        advancement_level=1,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Chola"]
    )
    QIN = CivTemplate(
        # 221 BC
        name="Qin",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Garrison", 3],
        }],
        advancement_level=1,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Qin"]
    )


    ROMANS = CivTemplate(
        # 509 BC (Republic began); 27 BC (Empire began)
        name="Romans",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Swordsman"],
        }],
        advancement_level=2,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Romans"]
    )
    PARTHIA = CivTemplate(
        # 3rd century BC
        name="Parthia",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Trebuchet"],
        }, ],
        advancement_level=2,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Parthia"]
    )
    CARTHAGE = CivTemplate(
        # 2nd century BC ish
        name="Carthage",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, BuildUnitsEffect(UNITS.HORSEMAN, 1)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horseman"],
        }],
        advancement_level=2,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Carthage"]
    )
    HAN = CivTemplate(
        # 2nd century BC
        name="Han",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [100],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman"],
        }],
        advancement_level=2,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Han"]
    )
    GUPTA = CivTemplate(
        # 3rd century AD
        name="Gupta",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, PointsEffect(lambda city, game_state: 4, "Gain 4 points", "Gupta")],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Catapult"],
        }],
        advancement_level=2,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Gupta"]
    )
    HUNS = CivTemplate(
        # 4th century AD
        name="Huns",
        abilities=[{
            "name": "IncreaseFocusYields", 
            "numbers": ["metal", 3]
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horse Archer"],
        }],
        advancement_level=2,
        region=Region.EUROPE,
        colors=CIV_COLORS["Huns"]
    )
    FRANKS = CivTemplate(
        # 5th century AD very loosely
        name="Franks",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("metal", 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=2,
        region=Region.EUROPE,
        colors=CIV_COLORS["Franks"]
    )
    MAYA = CivTemplate(
        # 1st century AD
        name="Maya",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Spearman"],
        }],
        advancement_level=2,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Maya"]
    )
    CELTS = CivTemplate(
        # ????
        name="Celts",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.UNIT, BuildUnitsEffect(UNITS.PIKEMAN, 2)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=2,
        region=Region.EUROPE,
        colors=CIV_COLORS["Celts"]
    )

    JIN = CivTemplate(
        # 266 AD
        name="Jin",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman"],
        }],
        advancement_level=3,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Jin"]
    )
    BYZANTINES = CivTemplate(
        # 324 AD
        name="Byzantines",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Trebuchet"],
        }],
        advancement_level=3,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Byzantines"]
    )
    SRIVIJAYA = CivTemplate(
        # 7th century AD
        name="Srivijaya",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("wood", 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Militia"],
        }],
        advancement_level=3,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Srivijaya"]
    )
    # UMAYYADS = CivTemplate(
    #     # 661 AD
    #     name="Umayyads",
    #     abilities=[{
    #         "name": "OnDevelop",
    #         "numbers": [BuildingType.URBAN, BuildUnitsEffect(UNITS.KNIGHT, 1)],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Knight"],
    #     }],
    #     advancement_level=3,
    ##     region=Region.MEDITERRANEAN,
    # )
    ABBASIDS = CivTemplate(
        # 750 AD
        name="Abbasids",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("science", 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=3,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Abbasids"]
    )
    VIKINGS = CivTemplate(
        # 8th century AD
        name="Vikings",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.UNIT, BuildUnitsEffect(UNITS.SWORDSMAN, 4)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=3,
        region=Region.EUROPE,
        colors=CIV_COLORS["Vikings"]
    )
    KHMER = CivTemplate(
        # 802
        name="Khmer",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [200],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=3,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Khmer"]
    )
    # SELJUKS = CivTemplate(
    #     # 1037
    #     name="Seljuks",
    #     abilities=[{
    #         "name": "StartWithResources",
    #         "numbers": ["metal", 30],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Cannon"],
    #     }],
    #     advancement_level=3,
    ##     region=Region.MIDDLE_EAST,
    # )
    # CASTILE = CivTemplate(
    #     # 1065
    #     name="Castile",
    #     abilities=[{
    #         "name": "DevelopCheap",
    #         "numbers": ["unit"],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Cavalry"],
    #     }],
    #     advancement_level=3,
    ##     region=Region.MEDITERRANEAN,
    # )
    ENGLAND = CivTemplate(
        # 1066
        name="England",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman"],
        }],
        advancement_level=3,
        region=Region.EUROPE,
        colors=CIV_COLORS["England"]
    )
    NOVGOROD = CivTemplate(
        # 1136
        name="Novgorod",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=3,
        region=Region.EUROPE,
        colors=CIV_COLORS["Novgorod"]
    )
    PORTUGAL = CivTemplate(
        # 1139
        name="Portugal",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=3,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Portugal"]
    )
    ARAGON = CivTemplate(
        # 1164
        name="Aragon",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=3,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Aragon"]
    )
    BOHEMIA = CivTemplate(
        # 12th century AD, loosely
        name="Bohemia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect('food', 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=3,
        region=Region.EUROPE,
        colors=CIV_COLORS["Bohemia"]
    )
    MONGOLS = CivTemplate(
        # 1206
        name="Mongols",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horse Archer", 2],
        }],
        advancement_level=3,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Mongols"]
    )
    DELHI = CivTemplate(
        # 1206
        name="Delhi",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=3,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Delhi"]
    )
    MALI = CivTemplate(
        # 1226
        name="Mali",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect('science', 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Trebuchet"],
        }],
        advancement_level=3,
        region=Region.AFRICA,
        colors=CIV_COLORS["Mali"]
    )


    ETHIOPIA = CivTemplate(
        # 1270
        name="Ethiopia",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 60],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman"],
        }],
        advancement_level=4,
        region=Region.AFRICA,
        colors=CIV_COLORS["Ethiopia"]
    )
    DENMARK = CivTemplate(
        # 10th century, technically. Ought to be an age after Vikings.
        name="Denmark",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
        colors=CIV_COLORS["Denmark"]
    )
    SUKHOTHAI = CivTemplate(
        # 1238 AD
        name="Sukhothai",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["unit"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=4,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Sukhothai"]
    )
    MAMLUKS = CivTemplate(
        # 1261
        name="Mamluks",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect('science', 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=4,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Mamluks"]
    )
    INCA = CivTemplate(
        # 13th century
        name="Inca",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=3,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Inca"]
    )


    AUSTRIA_HUNGARY = CivTemplate(
        # 1281 (Hapsburg Empire)
        name="Austria-Hungary",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Gatling Gun"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
        colors=CIV_COLORS["Austria-Hungary"]
    )
    MAJAPAHIT = CivTemplate(
        # 1292
        name="Majapahit",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=4,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Majapahit"]
    )
    OTTOMANS = CivTemplate(
        # 1299
        name="Ottomans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman"],
        }],
        advancement_level=4,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Ottomans"]
    )
    VIJAYANAGARA = CivTemplate(
        # 1336 -- huge cities that grew very fast, fought with giant hordes of relatively low-tech infantry.
        name="Vijayanagara",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, GainResourceEffect('wood', 60)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=4,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Vijayanagara"]
    )
    BAHMANI = CivTemplate(
        # 1347 -- very into knights ("Lords of the Horse"), early adopter of cannons.
        name="Bahmani",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, ResetHappinessThisCityEffect()],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=4,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Bahmani"]
    )
    MING = CivTemplate(
        # 1368
        name="Ming",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman"],
        }],
        advancement_level=4,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Ming"]
    )
    TIMURIDS = CivTemplate(
        # 1370
        name="Timurids",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=4,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Timurids"]
    )
    JOSEON = CivTemplate(
        # 1392 AD
        name="Joseon",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, GainResourceEffect('science', 60)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=4,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Joseon"]
    )
    AZTECS = CivTemplate(
        # 1428
        name="Aztecs",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": ["infantry", 1],
        }],
        advancement_level=4,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Aztecs"]
    )
    SONGHAI = CivTemplate(
        # 1464
        name="Songhai",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Gatling Gun"],  # TODO -- This doesn't make sense, they didn't have gunpowder.
        }],
        advancement_level=4,
        region=Region.AFRICA,
        colors=CIV_COLORS["Songhai"]
    )
    SPAIN = CivTemplate(
        # 1492
        name="Spain",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=4,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Spain"]
    )
    IROQUOIS = CivTemplate(
        # 16th century
        name="Iroquois",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=4,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Iroquois"]
    )
    POLAND = CivTemplate(
        # 1569
        name="Poland",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, PointsEffect(lambda city, gs: city.population // 5, "Gain 1 VP per 5 population", "Poland")],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
        colors=CIV_COLORS["Poland"]
    )


    MUGHALS = CivTemplate(
        # 1526
        name="Mughals",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Gatling Gun"],
        }],
        advancement_level=5,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Mughals"]
    )
    # NETHERLANDS = CivTemplate(
    #     # 1581
    #     name="Netherlands",
    #     abilities=[{
    #         "name": "StartWithResources",
    #         "numbers": ["science", 40],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Gatling Gun"],
    #     }],
    #     advancement_level=5,
    ##     region=Region.EUROPE,
    # )
    UNITED_KINGDOM = CivTemplate(
        # 1603
        name="United Kingdom",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman"],
        }],
        advancement_level=5,
        region=Region.EUROPE,
        colors=CIV_COLORS["United Kingdom"]
    )
    MARATHAS = CivTemplate(
        # 1674
        name="Marathas",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Infantry"],
        }],
        advancement_level=5,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Marathas"]
    )
    PRUSSIA = CivTemplate(
        # 1701
        name="Prussia",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Artillery"],
        }],
        advancement_level=5,
        region=Region.EUROPE,
        colors=CIV_COLORS["Prussia"]
    )
    COMANCHES = CivTemplate(
        # 18th century
        name="Comanches",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": ["mounted", 2],
        }],
        advancement_level=5,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Comanches"]
    )
    RUSSIA = CivTemplate(
        # 1721
        name="Russia",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [300],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=5,
        region=Region.EUROPE,
        colors=CIV_COLORS["Russia"]
    )
    UNITED_STATES = CivTemplate(
        # 1776
        name="United States",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, StealPopEffect(1, 4)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Infantry"],
        }],
        advancement_level=5,
        region=Region.AMERICAS,
        colors=CIV_COLORS["United States"]
    )
    MEXICO = CivTemplate(
        # 1810
        name="Mexico",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Artillery"],
        }],
        advancement_level=5,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Mexico"]
    )
    ZULU = CivTemplate(
        # 1816
        name="Zulu",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": ["infantry", 1],
        }, {
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, BuildBuildingEffect(BUILDINGS.ARMY_BASE)],
        }],
        advancement_level=5,
        region=Region.AFRICA,
        colors=CIV_COLORS["Zulu"]
)
    JAPAN = CivTemplate(
        # Depends what you mean
        name="Japan",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Swordsman", 10],
        }],
        advancement_level=5,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Japan"]
    )


    SWEDEN = CivTemplate(
        # 1611
        name="Sweden",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, GainResourceEffect('science', 100)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Machine Gun"],
        }],
        advancement_level=6,
        region=Region.EUROPE,
        colors=CIV_COLORS["Sweden"]
    )
    BRAZIL = CivTemplate(
        # 1822
        name="Brazil",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, GrowEffect(5)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Bazooka"],
        }],
        advancement_level=6,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Brazil"]
    )
    ITALY = CivTemplate(
        # 1861
        name="Italy",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 200],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Artillery"],
        }],
        advancement_level=6,
        region=Region.MEDITERRANEAN,
        colors=CIV_COLORS["Italy"]
    )
    CANADA = CivTemplate(
        # 1867
        name="Canada",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Machine Gun"],
        }],
        advancement_level=6,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Canada"]
    )
    GERMANY = CivTemplate(
        # 1871
        name="Germany",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Tank"],
        }],
        advancement_level=6,
        region=Region.EUROPE,
        colors=CIV_COLORS["Germany"]
    )
    KOREA = CivTemplate(
        # 1897
        name="Korea",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Tank"],
        }],
        advancement_level=6,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Korea"]
    )
    AUSTRALIA = CivTemplate(
        # 1901
        name="Australia",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Bazooka"],
        }],
        advancement_level=6,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Australia"]
    )
    SOVIET_UNION = CivTemplate(
        # 1922
        name="Soviet Union",
        abilities=[{
            "name": "ExtraVpsPerCityCaptured",
            "numbers": [5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Infantry"],
        }],
        advancement_level=6,
        region=Region.EUROPE,
        colors=CIV_COLORS["Soviet Union"]
    )


    TURKEY = CivTemplate(
        # 1923
        name="Turkey",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 10],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Machine Gun"],
        }],
        advancement_level=7,
        region=Region.MIDDLE_EAST,
        colors=CIV_COLORS["Turkey"]
    )
    INDONESIA = CivTemplate(
        # 1945?
        name="Indonesia",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 10],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Bazooka"],
        }],
        advancement_level=7,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["Indonesia"]
    )
    INDIA = CivTemplate(
        # 1947
        name="India",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, GrowEffect(10)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Tank"],
        }],
        advancement_level=7,
        region=Region.SOUTH_ASIA,
        colors=CIV_COLORS["India"]
    )
    COMMUNIST_CHINA = CivTemplate(
        # 1949
        name="Communist China",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 10],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rocket Launcher"],
        }],
        advancement_level=7,
        region=Region.EAST_ASIA,
        colors=CIV_COLORS["Communist China"]
    )
    UNIFIED_LATIN_AMERICA = CivTemplate(
        name="Unified Latin America",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": [None, 1],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rocket Launcher"],
        }],
        advancement_level=7,
        region=Region.AMERICAS,
        colors=CIV_COLORS["Unified Latin America"]
    )
    NATO = CivTemplate(
        name="NATO",
        abilities=[{ 
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, FreeRandomTechEffect(6)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rocket Launcher"],
        }],
        advancement_level=7,
        region=Region.EUROPE,
        colors=CIV_COLORS["NATO"]
    )

    ARCTIC_ALLIANCE = CivTemplate(
        name="Arctic Alliance",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 500],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
        colors=CIV_COLORS["Arctic Alliance"]
    )
    GREATER_EURO_ZONE = CivTemplate(
        name="Greater EuroZone",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 500],
        }],
        advancement_level=9,
        region=Region.EUROPE,
        colors=CIV_COLORS["Greater EuroZone"]
    )
    CELESTIAL_EMPIRE = CivTemplate(
        name="Celestial Empire",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 500],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
        colors=CIV_COLORS["Celestial Empire"]
    )
    THE_MACHINE_INTELLIGENCE = CivTemplate(
        name="The Machine Intelligence",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Giant Death Robot"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Nanoswarm"],
        }, {
            "name": "ExtraVpsPerUnitKilled",
            "numbers": [None, 2],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
        colors=CIV_COLORS["The Machine Intelligence"]
    )
    SOLARIA = CivTemplate(
        name="Solaria",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [20],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
        colors=CIV_COLORS["Solaria"]
    )

    # FRANCE = CivTemplate(
    #     # Depends what you mean
    #     name="France",
    #     abilities=[{
    #         "name": "IncreaseFocusYields",
    #         "numbers": ["wood", 4],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Rifleman"],
    #     }],
    #     advancement_level=5,
    ##     region=Region.EUROPE,
    # )

    # For debugging / sciencing
    # A0_BLANK = CivTemplate(
    #     name="A0 Blank",
    #     abilities=[],
    #     colors=("#000000", "#000000",),
    #     advancement_level=0,
    # )
    # A1_BLANK = CivTemplate(
    #     name="A1 Blank",
    #     abilities=[],
    #     colors=("#000000", "#000000",),
    #     advancement_level=1,
    # )
    # A2_BLANK = CivTemplate(
    #     name="A2 Blank",
    #     abilities=[],
    #     colors=("#000000", "#000000",),
    #     advancement_level=2,
    # )
    # A4_BLANK = CivTemplate(
    #     name="A4 Blank",
    #     abilities=[],
    #     colors=("#000000", "#000000",),
    #     advancement_level=4,
    # )
    # A5_BLANK = CivTemplate(
    #     name="A5 Blank",
    #     abilities=[],
    #     colors=("#000000", "#000000",),
    #     advancement_level=5,
    # )
    # A7_BLANK = CivTemplate(
    #     name="A7 Blank",
    #     abilities=[],
    #     colors=("#000000", "#000000",),
    #     advancement_level=7,
    # )


   # XHOSA = CivTemplate(
    #     name="Xhosa",
    #     abilities=[{
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Archer"],
    #     }],
    #     advancement_level=1,
    # )
    # AKSUM = CivTemplate(
    #     # 1st century AD
    #     name="Aksum",
    #     abilities=[{
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Archer"],
    #     }],
    #     advancement_level=1,
    # )
    # GOTHS = CivTemplate(
    #     # 3rd century AD ish
    #     name="Goths",
    #     abilities=[{
    #         "name": "ExtraVpsPerCityCaptured",
    #         "numbers": [5],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Swordsman"],
    #     }],
    #     advancement_level=1,
    # )
    # SASSANIDS = CivTemplate(
    #     name="Sassanids",
    #     abilities=[{
    #         "name": "DevelopCheap",
    #         "numbers": ["rural"],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Horseman"],
    #     }],
    #     advancement_level=1,
    # )
    # GOKTURKS = CivTemplate(
    #     name="Gokturks",
    #     abilities=[{
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Horse Archer"],
    #     }],
    #     advancement_level=1,
    # )
    # CUMANS = CivTemplate(
    #     name="Cumans",
    #     abilities=[{
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Horse Archer"],
    #     }],
    #     advancement_level=1,
    # )
    # XIONGNU = CivTemplate(
    #     name="Xiongnu",
    #     abilities=[{
    #         "name": "ExtraVpsPerUnitKilled",
    #         "numbers": [1],
    #     }],
    #     advancement_level=1,
    # )
    # VENICE = CivTemplate(
    #     name="Venice",
    #     abilities=[{
    #         "name": "OnDevelop",
    #         "numbers": [BuildingType.URBAN, BuildBuildingEffect(BUILDINGS.HARBOR)],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Musketman"],
    #     }],
    #     advancement_level=2,
    # )
    # MANCHU = CivTemplate(
    #     # To the extent this is a polity, it's the same as the Qing dynasty
    #     name="Manchu",
    #     abilities=[{
    #         "name": "IncreaseFocusYields",
    #         "numbers": ["science", 4],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Cannon"],
    #     }],
    #     advancement_level=4,
    ##     region=Region.EAST_ASIA
    # )
    # LITHUANIA = CivTemplate(
    #     # Basically part of poland for most of history
    #     name="Lithuania",
    #     abilities=[{
    #         "name": "StartWithResources",
    #         "numbers": ["wood", 40],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Cavalry"],
    #     }],
    #     advancement_level=4,
    ##     region=Region.EUROPE,
    # )
    # VIETNAM = CivTemplate(
    #     name="Vietnam",
    #     abilities=[{
    #         "name": "StartWithResources",
    #         "numbers": ["wood", 75],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Bazooka"],
    #     }],
    #     advancement_level=7,
    ##     region=Region.SOUTH_ASIA,
    # )
    # BURGUNDY = CivTemplate(
    #     # Ambiguous; maybe 855?
    #     name="Burgundy",
    #     abilities=[{
    #         "name": "OnDevelop",
    #         "numbers": [BuildingType.RURAL, GainResourceEffect('metal', 20)],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Musketman"],
    #     }],
    #     advancement_level=3,
    ##     region=Region.EUROPE,
    # )
    # ARABIA = CivTemplate(
    #     # ????
    #     name="Arabia",
    #     abilities=[{
    #         "name": "StartWithResources",
    #         "numbers": ["food", 40],
    #     }, {
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Knight"],
    #     }],
    #     advancement_level=4,
    ##     region=Region.MEDITERRANEAN,
    # )

_num_a0_civs = len([civ for civ in CIVS.all() if civ.advancement_level ==0])
assert _num_a0_civs >= settings.MAX_PLAYERS * settings.NUM_STARTING_LOCATION_OPTIONS, f"There are only {_num_a0_civs} age 0 civs, but we need {settings.MAX_PLAYERS * settings.NUM_STARTING_LOCATION_OPTIONS} for a maximum size game to fit."

import city_names
for civ in CIVS.all():
    assert civ.name in city_names.CITY_NAMES_BY_CIV, f"Civ {civ.name} does not have a corresponding city list in city_names.py"

CHECK_ORDERS = [
    [{CIVS.MYCENAEANS, CIVS.MINOANS}, {CIVS.ATHENS, CIVS.SPARTA, CIVS.MACEDONIA}, CIVS.ROMANS, CIVS.BYZANTINES, CIVS.OTTOMANS, CIVS.TURKEY],
    [CIVS.ROMANS, CIVS.ITALY],
    [CIVS.ARAGON, CIVS.SPAIN],
    [CIVS.MALI, CIVS.SONGHAI],
    [CIVS.VIKINGS, CIVS.DENMARK, CIVS.SWEDEN],
    [CIVS.EGPYT, CIVS.MAMLUKS],
    [CIVS.ENGLAND, CIVS.UNITED_KINGDOM],
    [CIVS.SRIVIJAYA, CIVS.MAJAPAHIT, CIVS.INDONESIA],
    [CIVS.NOVGOROD, CIVS.RUSSIA, CIVS.SOVIET_UNION],
    [CIVS.SHANG, CIVS.QIN, CIVS.HAN, CIVS.JIN, CIVS.MING, CIVS.COMMUNIST_CHINA],
    [CIVS.PHOENICIA, CIVS.CARTHAGE],
    [CIVS.PRUSSIA, CIVS.GERMANY],
    [CIVS.MAYA, CIVS.AZTECS, CIVS.MEXICO],
    [CIVS.JOMON, CIVS.JAPAN],
    [CIVS.JOSEON, CIVS.KOREA],
    [CIVS.IROQUOIS, CIVS.UNITED_STATES],
    [CIVS.INDUS, CIVS.MAURYA, CIVS.GUPTA, CIVS.DELHI, {CIVS.BAHMANI, CIVS.VIJAYANAGARA}, CIVS.MUGHALS, CIVS.INDIA],
    [CIVS.BABYLON, CIVS.PERSIA, CIVS.TIMURIDS],
]

for check_order in CHECK_ORDERS:
    previous_age = -999
    for i in range(len(check_order)):
        if isinstance(check_order[i], set):
            ages = [civ.advancement_level for civ in check_order[i]]
            assert all(age == ages[0] for age in ages), f"Civs in set {[civ.name for civ in check_order[i]]} do not have the same advancement level"
            current_age = ages[0]
        else:
            current_age = check_order[i].advancement_level
        # print(f"Checking {check_order[i - 1]} and {check_order[i]}; current age is {current_age}, previous age is {previous_age}")
        assert current_age > previous_age, f"Civs {check_order[i - 1]} and {check_order[i]} are not in strictly increasing order of advancement levels"
        previous_age = current_age


if __name__ == "__main__":
    from collections import defaultdict
    from tabulate import tabulate

    ages = [age for age in range(10) if any(civ.advancement_level == age for civ in CIVS.all())]

    # Initialize a nested defaultdict to store counts
    civ_counts = defaultdict(lambda: defaultdict(int))

    # Count civs by region and age
    for civ in CIVS.all():
        civ_counts[civ.region][civ.advancement_level] += 1

    # Prepare data for tabulation
    table_data = []
    headers = ["Region"] + [str(age) for age in ages]

    for region in Region:
        row = [region.name]
        for age in ages:
            num_civs = civ_counts[region][age]
            if num_civs > 0:
                row.append(str(num_civs))
            else:
                row.append("")
        table_data.append(row)

    # Add a total row
    total_row = ["TOTAL"]
    for age in ages:
        total_row.append(str(sum(civ_counts[region][age] for region in Region)))
    table_data.append(total_row)

    # Print the table
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # for age in range(11):
    #     print(f"====== {age} ======")
    #     for civ in [civ for civ in CIVS.all() if civ.advancement_level == age]:
    #         print(civ.name)

    # # Print civs that aren't in any CHECK_ORDERS
    # all_civs = set(CIVS.all())
    # civs_in_check_orders = set()
    # for check_order in CHECK_ORDERS:
    #     for item in check_order:
    #         if isinstance(item, set):
    #             civs_in_check_orders.update(item)
    #         else:
    #             civs_in_check_orders.add(item)
    
    # civs_not_in_check_orders = all_civs - civs_in_check_orders
    
    # if civs_not_in_check_orders:
    #     print("\nCivs not in any CHECK_ORDERS:")
    #     for civ in sorted(civs_not_in_check_orders, key=lambda c: (c.advancement_level, c.name)):
    #         print(f"- {civ.name} (Age: {civ.advancement_level})")
    # else:
    #     print("\nAll civs are included in CHECK_ORDERS.")

    