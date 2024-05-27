from typing import Generator
from wonder_template import WonderTemplate

class WONDERS():
    PLACEHOLDER_A1_NUM1 = WonderTemplate(name="PLACEHOLDER_A1_NUM1", age=1)
    PLACEHOLDER_A1_NUM2 = WonderTemplate(name="PLACEHOLDER_A1_NUM2", age=1)
    PLACEHOLDER_A1_NUM3 = WonderTemplate(name="PLACEHOLDER_A1_NUM3", age=1)
    PLACEHOLDER_A1_NUM4 = WonderTemplate(name="PLACEHOLDER_A1_NUM4", age=1)

    PLACEHOLDER_A2_NUM1 = WonderTemplate(name="PLACEHOLDER_A2_NUM1", age=2)
    PLACEHOLDER_A2_NUM2 = WonderTemplate(name="PLACEHOLDER_A2_NUM2", age=2)
    PLACEHOLDER_A2_NUM3 = WonderTemplate(name="PLACEHOLDER_A2_NUM3", age=2)
    PLACEHOLDER_A2_NUM4 = WonderTemplate(name="PLACEHOLDER_A2_NUM4", age=2)

    PLACEHOLDER_A3_NUM1 = WonderTemplate(name="PLACEHOLDER_A3_NUM1", age=3)
    PLACEHOLDER_A3_NUM2 = WonderTemplate(name="PLACEHOLDER_A3_NUM2", age=3)
    PLACEHOLDER_A3_NUM3 = WonderTemplate(name="PLACEHOLDER_A3_NUM3", age=3)
    PLACEHOLDER_A3_NUM4 = WonderTemplate(name="PLACEHOLDER_A3_NUM4", age=3)

    PLACEHOLDER_A4_NUM1 = WonderTemplate(name="PLACEHOLDER_A4_NUM1", age=4)
    PLACEHOLDER_A4_NUM2 = WonderTemplate(name="PLACEHOLDER_A4_NUM2", age=4)
    PLACEHOLDER_A4_NUM3 = WonderTemplate(name="PLACEHOLDER_A4_NUM3", age=4)
    PLACEHOLDER_A4_NUM4 = WonderTemplate(name="PLACEHOLDER_A4_NUM4", age=4)

    PLACEHOLDER_A5_NUM1 = WonderTemplate(name="PLACEHOLDER_A5_NUM1", age=5)
    PLACEHOLDER_A5_NUM2 = WonderTemplate(name="PLACEHOLDER_A5_NUM2", age=5)
    PLACEHOLDER_A5_NUM3 = WonderTemplate(name="PLACEHOLDER_A5_NUM3", age=5)
    PLACEHOLDER_A5_NUM4 = WonderTemplate(name="PLACEHOLDER_A5_NUM4", age=5)

    PLACEHOLDER_A6_NUM1 = WonderTemplate(name="PLACEHOLDER_A6_NUM1", age=6)
    PLACEHOLDER_A6_NUM2 = WonderTemplate(name="PLACEHOLDER_A6_NUM2", age=6)
    PLACEHOLDER_A6_NUM3 = WonderTemplate(name="PLACEHOLDER_A6_NUM3", age=6)
    PLACEHOLDER_A6_NUM4 = WonderTemplate(name="PLACEHOLDER_A6_NUM4", age=6)

    PLACEHOLDER_A7_NUM1 = WonderTemplate(name="PLACEHOLDER_A7_NUM1", age=7)
    PLACEHOLDER_A7_NUM2 = WonderTemplate(name="PLACEHOLDER_A7_NUM2", age=7)
    PLACEHOLDER_A7_NUM3 = WonderTemplate(name="PLACEHOLDER_A7_NUM3", age=7)
    PLACEHOLDER_A7_NUM4 = WonderTemplate(name="PLACEHOLDER_A7_NUM4", age=7)

    PLACEHOLDER_A8_NUM1 = WonderTemplate(name="PLACEHOLDER_A8_NUM1", age=8)
    PLACEHOLDER_A8_NUM2 = WonderTemplate(name="PLACEHOLDER_A8_NUM2", age=8)
    PLACEHOLDER_A8_NUM3 = WonderTemplate(name="PLACEHOLDER_A8_NUM3", age=8)
    PLACEHOLDER_A8_NUM4 = WonderTemplate(name="PLACEHOLDER_A8_NUM4", age=8)

    PLACEHOLDER_A9_NUM1 = WonderTemplate(name="PLACEHOLDER_A9_NUM1", age=9)
    PLACEHOLDER_A9_NUM2 = WonderTemplate(name="PLACEHOLDER_A9_NUM2", age=9)
    PLACEHOLDER_A9_NUM3 = WonderTemplate(name="PLACEHOLDER_A9_NUM3", age=9)
    PLACEHOLDER_A9_NUM4 = WonderTemplate(name="PLACEHOLDER_A9_NUM4", age=9)

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

