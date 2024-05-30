from typing import Generator
from unit_templates_list import UNITS
from effects_list import BuildUnitsEffect, FreeNearbyCityEffect, FreeRandomTechEffect, GainResourceEffect, GrowEffect, RecruitBarbariansEffect
from wonder_template import WonderTemplate

class WONDERS():
    PYRAMIDS = WonderTemplate(
        name="Pyramids", age=0,
        on_build=FreeNearbyCityEffect()
    )

    STONEHENGE = WonderTemplate(
        name="Stonehenge", age=0,
        on_build=BuildUnitsEffect(unit_template=UNITS.SLINGER, num=3)
    )

    # TODO Your warriors get +2 strength?
    ZIGGURAT_OF_UR = WonderTemplate(name="Ziggurat of Ur", age=0)

    # 7th century BC
    HANGING_GARDENS = WonderTemplate(
        name="Hanging Gardens", age=0,
        on_build=GrowEffect(amount=4)
    )

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

    # 5th century BC
    PARTHENON = WonderTemplate(
        name="Parthenon", age=1,
        on_build=RecruitBarbariansEffect(range=3)
    )
    
    # 3rd century BC
    GREAT_LIBRARY = WonderTemplate(
        name="Great Library", age=2,
        on_build=GainResourceEffect(resource='science', amount=100)
    )

    # 3rd century BC
    # TODO Build a bunch of Garrisons around your periphery
    GREAT_WALL = WonderTemplate(name="Great Wall", age=2)

    # 3rd century BC
    COLOSSUS = WonderTemplate(
        name="Colossus", age=2,
        on_build=BuildUnitsEffect(unit_template=UNITS.COLOSUS, num=1)
    )
    # Terracotta army (2nd century)
    
    CAMELOT = WonderTemplate(
        name="Camelot", age=3,
        on_build=BuildUnitsEffect(unit_template=UNITS.KNIGHT, num=12)
    )

    # 6th century
    # TODO
    HAGIA_SOPHIA = WonderTemplate(name="Hagia Sophia", age=3)
    PLACEHOLDER_A3_NUM3 = WonderTemplate(name="PLACEHOLDER_A3_NUM3", age=3)
    # Chichen Itza (13th century)

    PLACEHOLDER_A4_NUM1 = WonderTemplate(name="PLACEHOLDER_A4_NUM1", age=4)
    PLACEHOLDER_A4_NUM2 = WonderTemplate(name="PLACEHOLDER_A4_NUM2", age=4)
    PLACEHOLDER_A4_NUM3 = WonderTemplate(name="PLACEHOLDER_A4_NUM3", age=4)
    # Notre Dame (13th century), Porcelain Tower, Himeji Castle (16th-17th century), Forbidden Palace (15th century)
    # Alhambra (13th century)
    # Angkor Wat (12th century)
    # Macchu Picchu (15th century)


    PLACEHOLDER_A5_NUM1 = WonderTemplate(name="PLACEHOLDER_A5_NUM1", age=5)
    PLACEHOLDER_A5_NUM2 = WonderTemplate(name="PLACEHOLDER_A5_NUM2", age=5)
    PLACEHOLDER_A5_NUM3 = WonderTemplate(name="PLACEHOLDER_A5_NUM3", age=5)

    PLACEHOLDER_A6_NUM1 = WonderTemplate(name="PLACEHOLDER_A6_NUM1", age=6)
    PLACEHOLDER_A6_NUM2 = WonderTemplate(name="PLACEHOLDER_A6_NUM2", age=6)
    PLACEHOLDER_A6_NUM3 = WonderTemplate(name="PLACEHOLDER_A6_NUM3", age=6)

    PLACEHOLDER_A7_NUM1 = WonderTemplate(name="PLACEHOLDER_A7_NUM1", age=7)
    PLACEHOLDER_A7_NUM2 = WonderTemplate(name="PLACEHOLDER_A7_NUM2", age=7)
    PLACEHOLDER_A7_NUM3 = WonderTemplate(name="PLACEHOLDER_A7_NUM3", age=7)

    PLACEHOLDER_A8_NUM1 = WonderTemplate(name="PLACEHOLDER_A8_NUM1", age=8)
    PLACEHOLDER_A8_NUM2 = WonderTemplate(name="PLACEHOLDER_A8_NUM2", age=8)
    PLACEHOLDER_A8_NUM3 = WonderTemplate(name="PLACEHOLDER_A8_NUM3", age=8)

    PLACEHOLDER_A9_NUM1 = WonderTemplate(name="PLACEHOLDER_A9_NUM1", age=9)
    PLACEHOLDER_A9_NUM2 = WonderTemplate(name="PLACEHOLDER_A9_NUM2", age=9)
    PLACEHOLDER_A9_NUM3 = WonderTemplate(name="PLACEHOLDER_A9_NUM3", age=9)

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

