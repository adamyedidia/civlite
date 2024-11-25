from typing import Generator
from building_template import BuildingType
from effects_list import BuildUnitsEffect, GainSlotsEffect, PointsEffect, UpgradeTerrainEffect
from settings import WONDER_VPS
from tenet_template import TenetTemplate
from terrain_templates_list import TERRAINS
from unit_templates_list import UNITS
from yields import Yields

class TENETS():
    TALES_OF_SCHEHERAZADE = TenetTemplate(
        advancement_level=1,
        name="Scheherazade's Tales",
        instant_effect=PointsEffect(lambda _c, _g: 5, label="Scheherazade", description="Gain 5 points."),
    )

    MAUIS_FISHHOOK = TenetTemplate(
        advancement_level=1,
        name="Mauis Fishhook",
        instant_effect=GainSlotsEffect(2, BuildingType.RURAL)
    )

    PROMETHEAN_FIRE = TenetTemplate(
        advancement_level=1,
        name="Promethean Fire",
        instant_effect=UpgradeTerrainEffect(2, TERRAINS.MOUNTAINS, Yields(metal=3, science=3), "Volcano"),
    )

    DAVID_VS_GOLIATH = TenetTemplate(
        advancement_level=1,
        name="David vs Goliath",
        instant_effect=BuildUnitsEffect(UNITS.SLINGER, num=1, extra_str=2)
    )

    RISE_OF_EQUALITY = TenetTemplate(
        advancement_level=2,
        name="Rise of Equality",
        description="Each turn all players in an age earlier than you lose 25 city_power; if your age is ahead of the game age, gain 25 city_power."
    )

    PROMISE_OF_FREEDOM = TenetTemplate(
        advancement_level=2,
        name="Promise of Freedom",
        description="Each turn all players in an age earlier than you lose 1 vp; if your age is ahead of the game age, gain 1 vp."
    )

    HYMN_OF_UNITY = TenetTemplate(
        advancement_level=2,
        name="Hymn of Unity",
        description="Instantly capture cities that are in an earlier age than yours without siege.",
    )

    GLORIOUS_ORDER = TenetTemplate(
        advancement_level=2,
        name="Glorious Order",
        description="You can build wonders from your civ's age when ahead of the global age. Your cities demand 1 less food per wonder your ideology has built.",
        initialize_data=lambda game_player: {"num_wonders_built": game_player.score_dict.get("Wonders", 0) / WONDER_VPS}
    )

    # all & by_name are copy-pasted methods to all template lists.
    # I wasn't able to set up a base class system for this
    # That handled the dynamic type properly.
    @classmethod
    def all(cls) -> Generator[TenetTemplate, None, None]:
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), TenetTemplate):
                yield getattr(cls, attr)
    @classmethod
    def by_name(cls, name: str) -> TenetTemplate:
        for item in cls.all():
            if item.name == name:
                return item
        raise KeyError(f'No item with name {name}')
    
tenets_by_level = {
    i: [t for t in TENETS.all() if t.advancement_level == i]
    for i in range(5)
}