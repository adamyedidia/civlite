from typing import Generator
from abilities_list import BUILDING_ABILITIES
from TechStatus import TechStatus
from unit_templates_list import UNITS
from effects_list import BuildUnitsEffect, EndGameEffect, FreeNearbyCityEffect, FreeRandomTechEffect, GainResourceEffect, GetGreatPersonEffect, GrowEffect, PointsEffect, RecruitBarbariansEffect, ResetHappinessAllCitiesEffect, StealPopEffect, StrengthAllUnitsEffect, ZigguratWarriorsEffect
from wonder_template import WonderTemplate

class WONDERS():
    ########################## Age 0 ##########################
    # Options:
    # * SPHINX

    PYRAMIDS = WonderTemplate(
        name="Pyramids", age=0,
        on_build=FreeNearbyCityEffect()
    )

    STONEHENGE = WonderTemplate(
        name="Stonehenge", age=0,
        per_turn=BuildUnitsEffect(unit_template=UNITS.SLINGER, num=1)
    )

    ZIGGURAT_OF_UR = WonderTemplate(name="Ziggurat of Ur", age=0,
                                    per_turn=ZigguratWarriorsEffect())

    # 7th century BC
    HANGING_GARDENS = WonderTemplate(
        name="Hanging Gardens", age=0,
        on_build=PointsEffect(calculate_points=lambda city, _: 3 * city.population, description="+3 vp per population in this city")
    )

    ########################## Age 1 ##########################

    # 6th century BC
    TEMPLE_OF_ARTEMIS = WonderTemplate(
        name="Temple of Artemis", age=1,
        on_build=BuildUnitsEffect(unit_template=UNITS.ARCHER, num=4)
    )

    # 5th century BC
    STATUE_OF_ZEUS = WonderTemplate(
        name="Statue of Zeus", age=1,
        on_build=BuildUnitsEffect(unit_template=UNITS.ZEUS, num=1)
    )

    # 6th century or earlier
    ORACLE = WonderTemplate(
        name="Oracle", age=1,
        on_build=FreeRandomTechEffect(age=2)
    )

    GREAT_BATH = WonderTemplate(
        name="Great Bath", age=1,
        on_build=RecruitBarbariansEffect(range=3)
    )

    # 5th century BC
    PARTHENON = WonderTemplate(
        name="Parthenon", age=1,
        on_build=GetGreatPersonEffect(age_offset=1)
    )

    ########################## Age 2 ##########################
    # Options:
    # * Terracotta army (2nd century BC)

    # 3rd century BC
    GREAT_LIBRARY = WonderTemplate(
        name="Great Library", age=2,
        on_build=GainResourceEffect(resource='science', amount=100)
    )

    # 3rd century BC
    # Build a bunch of Garrisons around your periphery
    # GREAT_WALL = WonderTemplate(name="Great Wall", age=2)

    # 3rd century BC
    COLOSSUS = WonderTemplate(
        name="Colossus", age=2,
        on_build=BuildUnitsEffect(unit_template=UNITS.COLOSSUS, num=1),
        per_turn=GainResourceEffect(resource='metal', amount=2)
    )

    # 4th century BC
    MAUSOLEUM = WonderTemplate(
        name="Mausoleum", age=2,
        on_build=PointsEffect(calculate_points=lambda city, game_state: len(city.civ.get_my_cities(game_state)) * 2, description="+2 vp per city you own")
    )

    # 3rd century BC
    PALACE_OF_DOMITIAN = WonderTemplate(
        name="Palace of Domitian", age=2,
        on_build=GetGreatPersonEffect(age_offset=1)
    )
    

    ########################## Age 3 ##########################

    CAMELOT = WonderTemplate(
        name="Camelot", age=3,
        on_build=BuildUnitsEffect(unit_template=UNITS.SIR_LANCELOT, num=1)
    )
    # 6th century
    HAGIA_SOPHIA = WonderTemplate(name="Hagia Sophia", age=3, on_build=GrowEffect(amount=10))
    # 4th century
    HIPPODROME = WonderTemplate(
        name="Hippodrome", age=3,
        per_turn=BuildUnitsEffect(unit_template=UNITS.CHARIOT, num=2)
        )

    ########################## Age 4 ##########################
    # Options:
    # * Chichen Itza (13th c)
    # * Porcelain Tower (15th century), 
    # * Alhambra (13th century), 
    # * Angkor Wat (12th century), 
    # * Macchu Picchu (15th century)
    # * Taj Mahal (16th century)

    # 13th century
    NOTRE_DAME = WonderTemplate(name="Notre Dame", age=4, vp_reward=20)
    # 15th century
    # Gain city power & max territories?
    # FORBIDDEN_PALACE = WonderTemplate(name="Forbidden Palace", age=4)
    # 16th-17th century
    HIMEJI_CASTLE = WonderTemplate(name="Himeji Castle", age=4, on_build=StrengthAllUnitsEffect(amount=2))
    # 15th century
    SISTENE_CHAPEL = WonderTemplate(
        name="Sistene Chapel", age=4,
        on_build=BuildUnitsEffect(unit_template=UNITS.ARCHANGEL, num=2)
    )

    # 17th century
    VERSAILLES = WonderTemplate(name="Versailles", age=4, on_build=GetGreatPersonEffect(age_offset=2))

    ########################## Age 5 ##########################
    # Options:
    # * Brandenburg Gate (1791)

    # 1849
    KREMLIN = WonderTemplate(
        name="Kremlin", age=5,
        on_build=PointsEffect(calculate_points=lambda city, _: int(city.civ.city_power / 25), description="+1 vp per 25 city power you have stored")
    )

    # 1836
    ARC_DE_TRIOMPHE = WonderTemplate(
        name="Arc de Triomphe", age=5,
        abilities=[BUILDING_ABILITIES["ExtraVpsForCityCapture"](5)]
    )

    # 1859
    BIG_BEN = WonderTemplate(
        name="Big Ben", age=5,
        per_turn=PointsEffect(calculate_points=lambda city, _: 2, description="+2 vp per turn")
    )

    ########################## Age 6 ##########################
    # Options
    # * Cristo Redentor (1931)
    # * Empire State Building (1931)

    # 1886
    STATUE_OF_LIBERTY = WonderTemplate(
        name="Statue of Liberty", age=6,
        per_turn=StealPopEffect(num=1, cities=5)
    )

    # Eiffel Tower was 1889
    WORLDS_FAIR = WonderTemplate(
        name="World's Fair", age=6,
        on_build=ResetHappinessAllCitiesEffect()
    )

    # 1931
    CRISTO_REDENTOR = WonderTemplate(
        name="Cristo Redentor", age=6,
        on_build=BuildUnitsEffect(unit_template=UNITS.RIFLEMAN, num=8),
        per_turn=GrowEffect(amount=3)
    )

    # 1886
    NEUSCHWANSTEIN = WonderTemplate(
        name="Neuschwanstein", age=6,
        on_build=GetGreatPersonEffect(age_offset=2)
    )

    ########################## Age 7 ##########################

    FAST_FOOD_CHAINS = WonderTemplate(
        name="Fast Food Chains", age=7,
        on_build=GrowEffect(amount_fn=lambda city, _: city.population * 2, description="Triple city population")
    )

    MANHATTAN_PROJECT = WonderTemplate(
        name="Manhattan Project", age=7,
        on_build=BuildUnitsEffect(unit_template=UNITS.ATOMIC_BOMB, num=2, stacked=True)
    )

    UNITED_NATIONS = WonderTemplate(
        name="United Nations", age=7,
        on_build=RecruitBarbariansEffect(range=100)
    )

    ########################## Age 8 ##########################

    APOLLO_PROGRAM = WonderTemplate(
        name="Apollo Program", age=8,
        abilities=[BUILDING_ABILITIES["ExtraVpPerAgeOfTechResearched"](2)]
    )

    HUBBLE_SPACE_TELESCOPE = WonderTemplate(name="Hubble Space Telescope", age=8, on_build=FreeRandomTechEffect(age=9))

    AVENGERS_TOWER = WonderTemplate(
        name="Avengers Tower", age=8,
        on_build=BuildUnitsEffect(unit_template=UNITS.IRONMAN, num=1)
    )

    ########################## Age 9 ##########################

    # UNTESTED
    AGI = WonderTemplate(
        name="AGI", age=9,
        on_build=[
            PointsEffect(calculate_points=lambda city, _: sum([t.advancement_level for t, status in city.civ.techs_status.items() if status == TechStatus.RESEARCHED]), description="+1 vp per age of tech you have researched"),
            EndGameEffect()]
    )
    MARS_COLONY = WonderTemplate(
        name="Mars Colony", age=9,
        on_build=[
            PointsEffect(calculate_points=lambda city, _: int(city.civ.vitality / 0.1), description="+3 vp per 10% vitality"),
            EndGameEffect()]
    )
    PANACEA = WonderTemplate(
        name="Panacea", age=9,
        on_build=[
            PointsEffect(calculate_points=lambda city, game_state: int(sum([c.population / 2 for c in city.civ.get_my_cities(game_state)])), description="+1 point per two population in your nation"),
            EndGameEffect()]
    )
    DYSON_SWARM = WonderTemplate(name="Dyson Swarm", age=9, vp_reward=70)

    # all & by_name are copy-pasted methods to all template lists.
    # I wasn't able to set up a base class system for this
    # That handled the dynamic type properly.
    @classmethod
    def all(cls) -> Generator[WonderTemplate, None, None]:
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), WonderTemplate):
                yield getattr(cls, attr)
    @classmethod
    def by_name(cls, name: str) -> WonderTemplate:
        for item in cls.all():
            if item.name == name:
                return item
        raise KeyError(f'No item with name {name}')
    
    @classmethod
    def all_by_age(cls, age: int) -> Generator[WonderTemplate, None, None]:
        for item in cls.all():
            if item.age == age:
                yield item

