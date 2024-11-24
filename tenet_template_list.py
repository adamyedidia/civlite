from typing import Generator
from tenet_template import TenetTemplate

class TENETS():
    GREEK_FIRE = TenetTemplate(
        advancement_level=1,
        name="Greek Fire",
        quest_description="Urbanize a city to max urban slots (4)",
        description="Your ranged units always act first in turn order.",
    )

    AEGIS_OF_CONQUERORS = TenetTemplate(
        advancement_level=1,
        name="Aegis of Conquerors",
        quest_description="Build 5 cities on Hills.",
        description="Your strongest infantry unit takes only 2 damage from each attack."
    )

    FOUNTAIN_OF_YOUTH = TenetTemplate(
        advancement_level=1,
        name="Fountain of Youth",
        quest_description="Clear 8 barbarian camps.",
        description="Your vitality decays slower."        
    )

    KNIGHTS_OF_ATLANTIS = TenetTemplate(
        advancement_level=1,
        name="Knights of Atlantis",
        quest_description="Own 4 coastal cities.",
        description="Your mounted units have +1 speed."           
    )

    LURE_OF_SUPREMACY = TenetTemplate(
        advancement_level=2,
        name="Lure of Supremacy",
        description="Military units get +10% strength against units of lower tech level."
    )

    SONG_OF_FREEDOM = TenetTemplate(
        advancement_level=2,
        name="Song of Freedom",
        description="All players in an age earlier than you lose 1 vp per turn."
    )

    RISE_OF_EQUALITY = TenetTemplate(
        advancement_level=2,
        name="Rise of Equality",
        description="Instantly capture cities that are in an earlier age than yours.",
    )

    GLORIOUS_ORDER = TenetTemplate(
        advancement_level=2,
        name="Glorious Order",
        description="You can build wonders from your civ's age when ahead of the global age."
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