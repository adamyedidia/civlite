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
        description="Steal 10 city_power income from all players in an age earlier than you."
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
        description="You can build wonders from your civ's age when ahead of the global age. Cities in ages behind yours demand 4 more food per turn.",
    )

    HOLY_GRAIL = TenetTemplate(
        advancement_level=3,
        name="Holy Grail",
        description="Placeholder",
        instant_effect=PointsEffect(lambda _c, _g: 1, label="Holy Grail", description="Gain 1 vp."),
    )

    EL_DORADO = TenetTemplate(
        advancement_level=3,
        name="El Dorado",
        description="Placeholder",
        instant_effect=PointsEffect(lambda _c, _g: 1, label="", description="Gain 1 vp."),
    )

    FOUNTAIN_OF_YOUTH = TenetTemplate(
        advancement_level=3,
        name="Fountain of Youth",
        description="Placeholder",
        instant_effect=PointsEffect(lambda _c, _g: 1, label="Fountain of Youth", description="Gain 1 vp."),
    )

    YGGDRASILS_SEEDS = TenetTemplate(
        advancement_level=3,
        name="Yggdrasils Seeds",
        description="New cities you build immediately expand twice and start with 50 food, 50 wood, and 50 metal.",
        quest_description="Build 4 cities on forests.",
        quest_target=4,
    )

    FAITH = TenetTemplate(
        advancement_level=4,
        name="Faith",
        description="Gain double vps for wonder crowns.",
    )

    RATIONALISM = TenetTemplate(
        advancement_level=4,
        name="Rationalism",
        description="Upon completing a tech, gain extra vps for its level above III.",
    )

    HONOR = TenetTemplate(
        advancement_level=4,
        name="Honor",
        description="Gain double vps for fighting barbarian units and camps.",
    )

    COMMUNITY = TenetTemplate(
        advancement_level=4,
        name="Community",
        description="Gain double vps for developing in your cities.",
    )

    DRAGONS = TenetTemplate(
        advancement_level=5,
        name="Dragons",
        description="+10 city power for each kill by a ranged unit.",
    )

    UNICORNS = TenetTemplate(
        advancement_level=5,
        name="Unicorns",
        description="+10 city power for each kill by a mounted unit.",
    )

    GIANTS = TenetTemplate(
        advancement_level=5,
        name="Giants",
        description="+10 city power for each kill by a seige unit.",
    )

    NINJAS = TenetTemplate(
        advancement_level=5,
        name="Ninjas",
        description="+10 city power for each kill by an infantry unit.",
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