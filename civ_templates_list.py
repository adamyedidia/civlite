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
                print(f"Searching for {n} civs at {min_search_age=}, {max_advancement_level=}, {search_regions=}")
                decline_choice_big_civ_pool: list[CivTemplate] = [
                    civ for civ in player_civs(min_advancement_level=min_search_age, max_advancement_level=max_advancement_level, regions=search_regions) 
                    if civ not in civs_already_in_game]

                if len(decline_choice_big_civ_pool) >= n:
                    return decline_choice_big_civ_pool
                amounts_found[(max_advancement_level, min_advancement_level, len(search_regions))] = len(decline_choice_big_civ_pool)
    else:
        raise ValueError(f"Couldn't find enough civs to decline ({n}) in {target_regions}.\n\nargs were {advancement_level_target=}, {target_regions=}, {civs_already_in_game=}.\n\nFinal amounts found was {amounts_found}")

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
    )
    EGPYT = CivTemplate(
        name="Egypt",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [5]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
    )
    MYCENAEANS = CivTemplate(
        name="Mycenaeans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 2]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
    )
    HARRAPANS = CivTemplate(
        name="Harrapans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 2]
        }],
        advancement_level=0,
        region=Region.SOUTH_ASIA,
    )
    SHANG = CivTemplate(
        name="Shang",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 2]
        }],
        advancement_level=0,
        region=Region.EAST_ASIA,
    )
    SUMER = CivTemplate(
        name="Sumer",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 2]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
    )
    INDUS = CivTemplate(
        name="Indus",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 2]
        }],
        advancement_level=0,
        region=Region.SOUTH_ASIA,
    )
    MINOANS = CivTemplate(
        name="Minoans",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 2]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
    )
    BABYLON = CivTemplate(
        name="Babylon",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 2]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
    )
    CARALANS = CivTemplate(
        name="Caralans",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [4, "Warrior", 2]
        }],
        advancement_level=0,
        region=Region.AMERICAS,
    )
    TROY = CivTemplate(
        name="Troy",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [4, "Slinger", 2]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
    )    
    NUBIANS = CivTemplate(
        name="Nubians",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [2, "Archer", 3]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
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
    )
    AKKAD = CivTemplate(
        name="Akkad",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 2]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
    )
    ASSYRIA = CivTemplate(
        name="Assyria",
        abilities=[{
            "name": "ExtraVpsPerCityCaptured",
            "numbers": [5]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
    )
    JOMON = CivTemplate(
        name="Jomon",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [100]
        }],
        advancement_level=0,
        region=Region.EAST_ASIA,
    )
    YANGSHAO = CivTemplate(
        name="Yangshao",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": ["ranged", 1]
        }],
        advancement_level=0,
        region=Region.EAST_ASIA,
    )
    OLMECS = CivTemplate(
        name="Olmecs",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("food", 10)]
        }],
        advancement_level=0,
        region=Region.AMERICAS,
    )
    HITTITES = CivTemplate(
        name="Hittites",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("metal", 10)]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
    )
    PHOENICIA = CivTemplate(
        name="Phoenicia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("science", 10)]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,
    )
    ELAMITES = CivTemplate(
        name="Elamites",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("wood", 10)]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
    )
    LYDIA = CivTemplate(
        name="Lydia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, PointsEffect(lambda city, game_state: 2, "Gain 2 points", "Lydia")]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
    )
    THRACE = CivTemplate(
        name="Thrace",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, BuildUnitsEffect(UNITS.HORSE_ARCHER, 1)]
        }],
        advancement_level=0,
        region=Region.MEDITERRANEAN,

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
        region=Region.MEDITERRANEAN,
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
        region=Region.MEDITERRANEAN,
    )
    VIJAYANAGARA = CivTemplate(
        # 1336
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
    )
    BAHMANI = CivTemplate(
        # 1347
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
        region=Region.MEDITERRANEAN,
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
    )

    ARCTIC_ALLIANCE = CivTemplate(
        name="Arctic Alliance",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 500],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
    )
    GREATER_EURO_ZONE = CivTemplate(
        name="Greater EuroZone",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 500],
        }],
        advancement_level=9,
        region=Region.EUROPE,
    )
    CELESTIAL_EMPIRE = CivTemplate(
        name="Celestial Empire",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 500],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
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
    )
    SOLARIA = CivTemplate(
        name="Solaria",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [20],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
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
    [CIVS.INDUS, CIVS.MAURYA, CIVS.GUPTA, CIVS.DELHI, CIVS.MUGHALS, CIVS.INDIA],
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
        print(f"Checking {check_order[i - 1]} and {check_order[i]}; current age is {current_age}, previous age is {previous_age}")
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