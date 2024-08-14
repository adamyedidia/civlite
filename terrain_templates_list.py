from typing import Generator
from yields import Yields
from terrain_template import TerrainTemplate

class TERRAINS():
    PLAINS = TerrainTemplate(
        name= 'plains',
        yields= Yields(food=1, wood=0, metal=1, science=0),
        bonus_yields= Yields(food=3, wood=0, metal=1, science=0),
        frequency= 1,
    )
    FOREST = TerrainTemplate(
        name= 'forest',
        yields= Yields(food=1, wood=1, metal=0, science=0),
        bonus_yields= Yields(food=1, wood=3, metal=0, science=0),
        frequency= 1,
    )
    HILLS = TerrainTemplate(
        name= 'hills',
        yields= Yields(food=0, wood=1, metal=1, science=0),
        bonus_yields= Yields(food=0, wood=1, metal=3, science=0),
        frequency= 1,
    )
    OCEAN = TerrainTemplate(
        name= 'ocean',
        yields= Yields(food=1, wood=0, metal=0, science=1),
        bonus_yields= Yields(food=3, wood=0, metal=0, science=1),
        frequency= 0.0,
    )

    MOUNTAINS = TerrainTemplate(
        name= 'mountain',
        yields= Yields(food=0, wood=0, metal=1, science=0),
        bonus_yields= Yields(food=0, wood=0, metal=3, science=0),
        frequency= 0.1,
    )
    DESERT = TerrainTemplate(
        name= 'desert',
        yields= Yields(food=0, wood=0, metal=0, science=1),
        bonus_yields= Yields(food=3, wood=0, metal=0, science=2),
        frequency= 0.1,
    )
    TUNDRA = TerrainTemplate(
        name= 'tundra',
        yields= Yields(food=0, wood=1, metal=0, science=0),
        bonus_yields= Yields(food=0, wood=1, metal=0, science=3),
        frequency= 0.1,
    )

    # all & by_name are copy-pasted methods to all template lists.
    # I wasn't able to set up a base class system for this
    # That handled the dynamic type properly.
    @classmethod
    def all(cls) -> Generator[TerrainTemplate, None, None]:
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), TerrainTemplate):
                yield getattr(cls, attr)
    @classmethod
    def by_name(cls, name: str) -> TerrainTemplate:
        for item in cls.all():
            if item.name == name:
                return item
        raise KeyError(f'No item with name {name}')