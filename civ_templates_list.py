from typing import Generator
from building_template import BuildingType
from civ_template import CivTemplate
from effects_list import BuildBuildingEffect, BuildUnitsEffect, GainResourceEffect, GrowEffect, PointsEffect, ResetHappinessThisCityEffect
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
        for min_advancement_level in range(advancement_level_target, -1, -1):
            for search_regions in [target_regions, set(Region)]:
                # Try in order of (correct age correct region, correct age any region, age -1 correct region, age -1 any region, age -2 correct region, age -2 any region, ...)
                decline_choice_big_civ_pool: list[CivTemplate] = [
                    civ for civ in player_civs(min_advancement_level=min_advancement_level, max_advancement_level=max_advancement_level, regions=search_regions) 
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
    SCYTHIANS = CivTemplate(
        name="Scythians",
        abilities=[{
            "name": "IncreasedStrengthForNthUnit",
            "numbers": [2, "Chariot", 3]
        }],
        advancement_level=0,
        region=Region.MIDDLE_EAST,
    )
    MAYA = CivTemplate(
        name="Maya",
        abilities=[{
            "name": "ExtraVpsPerCityCaptured",
            "numbers": [5]
        }],
        advancement_level=0,
        region=Region.AMERICAS,
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
    GREECE = CivTemplate(
        # 7th century BC ish
        name="Greece",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Spearman"],
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
    JOSEON = CivTemplate(
        # 1392 AD
        name="Joseon",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["rural"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Chariot"],
        }],
        advancement_level=1,
        region=Region.EAST_ASIA,
    )
    SRIVIJAYA = CivTemplate(
        # 7th century AD
        name="Srivijaya",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect("wood", 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Garrison"],
        }],
        advancement_level=1,
        region=Region.SOUTH_ASIA,
    )
    ROMANS = CivTemplate(
        # 509 BC (Republic began)
        name="Romans",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Swordsman"],
        }],
        advancement_level=1,
        region=Region.MEDITERRANEAN,
    )
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
    VIKINGS = CivTemplate(
        # 8th century AD
        name="Vikings",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Swordsman"],
        }],
        advancement_level=1,
        region=Region.EUROPE,
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
        advancement_level=1,
        region=Region.MEDITERRANEAN,
    )
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
    HUNS = CivTemplate(
        # 4th century AD
        name="Huns",
        abilities=[{
            "name": "IncreaseFocusYields", 
            "numbers": ["food", 2]
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horse Archer"],
        }],
        advancement_level=1,
        region=Region.EUROPE,
    )
    # CUMANS = CivTemplate(
    #     name="Cumans",
    #     abilities=[{
    #         "name": "IncreasedStrengthForUnit",
    #         "numbers": ["Horse Archer"],
    #     }],
    #     advancement_level=1,
    # )
    GUPTA = CivTemplate(
        # 3rd century AD
        name="Gupta",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["urban"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Catapult"],
        }],
        advancement_level=1,
        region=Region.SOUTH_ASIA,
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
    JIN = CivTemplate(
        name="Jin",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman"],
        }],
        advancement_level=2,
        region=Region.EAST_ASIA,
    )
    FRANKS = CivTemplate(
        # 5th century AD very loosely
        name="Franks",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 20],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=2,
        region=Region.EUROPE,
    )
    CELTS = CivTemplate(
        # ????
        name="Celts",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 2],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=2,
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
        advancement_level=2,
        region=Region.SOUTH_ASIA,
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
        advancement_level=2,
        region=Region.MEDITERRANEAN,
    )
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
        advancement_level=2,
        region=Region.MIDDLE_EAST,
    )
    UMAYYADS = CivTemplate(
        # 661 AD
        name="Umayyads",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.URBAN, BuildUnitsEffect(UNITS.KNIGHT, 1)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=2,
        region=Region.MEDITERRANEAN,
    )
    # XIONGNU = CivTemplate(
    #     name="Xiongnu",
    #     abilities=[{
    #         "name": "ExtraVpsPerUnitKilled",
    #         "numbers": [1],
    #     }],
    #     advancement_level=1,
    # )
    MAJAPAHIT = CivTemplate(
        # 1292
        name="Majapahit",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=3,
        region=Region.SOUTH_ASIA,
    )
    KHMER = CivTemplate(
        # 802
        name="Khmer",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 30],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=3,
        region=Region.SOUTH_ASIA,
    )
    SELJUKS = CivTemplate(
        # 1037
        name="Seljuks",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 30],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=3,
        region=Region.MIDDLE_EAST,
    )
    TIMURIDS = CivTemplate(
        # 1370
        name="Timurids",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=2,
        region=Region.MIDDLE_EAST,
    )
    MALI = CivTemplate(
        # 1226
        name="Mali",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=2,
        region=Region.AFRICA,
    )
    SONGHAI = CivTemplate(  # TODO: These should be age 3 -- they should be after Mali since Mali declined and Songhai replaced them.
        # 1464
        name="Songhai",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=3,
        region=Region.AFRICA,
    )
    MONGOLS = CivTemplate(  # TODO: These should be age 3 surely.
        # 1206
        name="Mongols",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["metal", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Horse Archer"],
        }],
        advancement_level=3,
        region=Region.EAST_ASIA,
    )
    AZTECS = CivTemplate(
        # 1428
        name="Aztecs",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": ["infantry", 1],
        }],
        advancement_level=2,
        region=Region.AMERICAS,
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
        advancement_level=2,
        region=Region.AMERICAS,
    )
    MUGHALS = CivTemplate(
        # 1526
        name="Mughals",
        abilities=[{
            "name": "ExtraVpsPerWonder",
            "numbers": [5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=3,
        region=Region.SOUTH_ASIA,
    )
    MARATHAS = CivTemplate(
        # 1674
        name="Marathas",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=3,
        region=Region.SOUTH_ASIA,
    )
    ZULU = CivTemplate(
        # 1816
        name="Zulu",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [150],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=2,
        region=Region.AFRICA,
    )
    MAURYA = CivTemplate(
        # 322 BC
        name="Maurya",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=3,
        region=Region.SOUTH_ASIA,
    )
    CHOLA = CivTemplate(
        # 3rd century BC
        name="Chola",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=2,
        region=Region.SOUTH_ASIA,
    )
    MING = CivTemplate(
        # 1368
        name="Ming",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman"],
        }],
        advancement_level=2,
        region=Region.EAST_ASIA,
    )
    QIN = CivTemplate(
        # 221 BC
        name="Qin",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman"],
        }],
        advancement_level=3,
        region=Region.EAST_ASIA,
    )
    BURGUNDY = CivTemplate(
        # Ambiguous; maybe 855?
        name="Burgundy",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect('metal', 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=3,
        region=Region.EUROPE,
    )
    BOHEMIA = CivTemplate(
        # 12th century AD, loosely
        name="Bohemia",
        abilities=[{
            "name": "OnDevelop",
            "numbers": [BuildingType.RURAL, GainResourceEffect('wood', 20)],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Militia"],
        }],
        advancement_level=2,
        region=Region.EUROPE,
    )
    ENGLAND = CivTemplate(
        # 1066
        name="England",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["urban"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Crossbowman"],
        }],
        advancement_level=2,
        region=Region.EUROPE,
    )
    NOVGOROD = CivTemplate(
        # 1136
        name="Novgorod",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["rural"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=3,
        region=Region.EUROPE,
    )
    CASTILE = CivTemplate(
        # 1065
        name="Castile",
        abilities=[{
            "name": "DevelopCheap",
            "numbers": ["unit"],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=4,
        region=Region.MEDITERRANEAN,
    )
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
    ARAGON = CivTemplate(
        # 1164
        name="Aragon",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 3],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Pikeman"],
        }],
        advancement_level=2,
        region=Region.MEDITERRANEAN,
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
        advancement_level=2,
        region=Region.MEDITERRANEAN,
    )
    DELHI = CivTemplate(
        # 1206
        name="Delhi",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 30],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=3,
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
            "numbers": ["Pikeman"],
        }],
        advancement_level=2,
        region=Region.SOUTH_ASIA,
    )
    VIJAYANAGARA = CivTemplate(
        # 1336
        name="Vijayanagara",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 30],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=2,
        region=Region.SOUTH_ASIA,
    )
    IROQUOIS = CivTemplate(
        # 16th century
        name="Iroquois",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=4,
        region=Region.AMERICAS,
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
    SWEDEN = CivTemplate(
        # 1611
        name="Sweden",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
    )
    RUSSIA = CivTemplate(
        # 1721
        name="Russia",
        abilities=[{
            "name": "ExtraCityPower",
            "numbers": [250],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
    )
    ARABIA = CivTemplate(
        # ????
        name="Arabia",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Knight"],
        }],
        advancement_level=4,
        region=Region.MEDITERRANEAN,
    )
    PORTUGAL = CivTemplate(
        # 1139
        name="Portugal",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Musketman"],
        }],
        advancement_level=4,
        region=Region.MEDITERRANEAN,
    )
    SPAIN = CivTemplate(
        # 1492
        name="Spain",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=4,
        region=Region.MEDITERRANEAN,
    )
    FRANCE = CivTemplate(
        # Depends what you mean
        name="France",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
    )
    PRUSSIA = CivTemplate(
        # 1701
        name="Prussia",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Artillery"],
        }],
        advancement_level=5,
        region=Region.EUROPE,
    )
    MANCHU = CivTemplate(
        # To the extent this is a polity, it's the same as the Qing dynasty
        name="Manchu",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["science", 4],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=4,
        region=Region.EAST_ASIA
    )
    POLAND = CivTemplate(
        # 1569
        name="Poland",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["wood", 5],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
    )
    LITHUANIA = CivTemplate(
        # Basically part of poland for most of history
        name="Lithuania",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["wood", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cavalry"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
    )
    NETHERLANDS = CivTemplate(
        # 1581
        name="Netherlands",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Gatling Gun"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
    )
    DENMARK = CivTemplate(
        # 10th century
        name="Denmark",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Gatling Gun"],
        }],
        advancement_level=4,
        region=Region.EUROPE,
    )
    BRAZIL = CivTemplate(
        # 1822
        name="Brazil",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 50],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Rifleman"],
        }],
        advancement_level=5,
        region=Region.AMERICAS,
    )
    UNITED_STATES = CivTemplate(
        # 1776
        name="United States",
        abilities=[{
            "name": "ExtraVpsPerCityCaptured",
            "numbers": [5],
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
    INDONESIA = CivTemplate(
        # 1945?
        name="Indonesia",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["food", 8],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=5,
        region=Region.SOUTH_ASIA,
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
    KOREA = CivTemplate(
        # 1897
        name="Korea",
        abilities=[{
            "name": "IncreaseCapitalYields",
            "numbers": ["science", 6],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Cannon"],
        }],
        advancement_level=5,
        region=Region.EAST_ASIA,
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
        advancement_level=5,
        region=Region.AFRICA,
    )    
    ITALY = CivTemplate(
        # 1861
        name="Italy",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 40],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Artillery"],
        }],
        advancement_level=5,
        region=Region.MEDITERRANEAN,
    )
    GERMANY = CivTemplate(
        # 1871
        name="Germany",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["metal", 6],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Tank"],
        }],
        advancement_level=6,
        region=Region.EUROPE,
    )
    COMANCHES = CivTemplate(
        # 18th century
        name="Comanches",
        abilities=[{
            "name": "ExtraVpsPerUnitKilled",
            "numbers": ["mounted", 1],
        }],
        advancement_level=5,
        region=Region.AMERICAS,
    )
    CANADA = CivTemplate(
        # 1867
        name="Canada",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 75],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Infantry"],
        }],
        advancement_level=7,
        region=Region.AMERICAS,
    )
    AUSTRALIA = CivTemplate(
        # 1901
        name="Australia",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 75],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Bazooka"],
        }],
        advancement_level=7,
        region=Region.SOUTH_ASIA,
    )
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
    INDIA = CivTemplate(
        # 1947
        name="India",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 150],
        }],
        advancement_level=7,
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
            "numbers": ["Rocket Launcher"],
        }],
        advancement_level=7,
        region=Region.EUROPE,
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
    TURKEY = CivTemplate(
        # 1923
        name="Turkey",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 10],
        }, {
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Infantry"],
        }],
        advancement_level=7,
        region=Region.MEDITERRANEAN,
    )
    SOLARIA = CivTemplate(
        name="Solaria",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["science", 200],
        }],
        advancement_level=10,
        region=Region.GLOBAL,
    )
    ARCTIC_ALLIANCE = CivTemplate(
        name="Arctic Alliance",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["food", 400],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
    )
    GREATER_EURO_ZONE = CivTemplate(
        name="Greater EuroZone",
        abilities=[{
            "name": "IncreaseFocusYields",
            "numbers": ["wood", 30],
        }],
        advancement_level=9,
        region=Region.EUROPE,
    )
    CELESTIAL_EMPIRE = CivTemplate(
        name="Celestial Empire",
        abilities=[{
            "name": "StartWithResources",
            "numbers": ["metal", 150],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
    )
    THE_MACHINE_INTELLIGENCE = CivTemplate(
        name="The Machine Intelligence",
        abilities=[{
            "name": "IncreasedStrengthForUnit",
            "numbers": ["Giant Death Robot"],
        }],
        advancement_level=9,
        region=Region.GLOBAL,
    )

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

_num_a0_civs = len([civ for civ in CIVS.all() if civ.advancement_level ==0])
assert _num_a0_civs >= settings.MAX_PLAYERS * settings.NUM_STARTING_LOCATION_OPTIONS, f"There are only {_num_a0_civs} age 0 civs, but we need {settings.MAX_PLAYERS * settings.NUM_STARTING_LOCATION_OPTIONS} for a maximum size game to fit."

import city_names
for civ in CIVS.all():
    assert civ.name in city_names.CITY_NAMES_BY_CIV, f"Civ {civ.name} does not have a corresponding city list in city_names.py"


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