import random
from typing import Generator, TYPE_CHECKING
from building_template import BuildingType
from effects_list import BuildUnitsEffect, GainSlotsEffect, PointsEffect, UpgradeTerrainEffect
from settings import WONDER_VPS
from tech_templates_list import TECHS
from tenet_template import TenetTemplate
from terrain_templates_list import TERRAINS
from unit_template import UnitTag
from unit_templates_list import UNITS
from yields import Yields
import score_strings

if TYPE_CHECKING:
    from game_state import GameState
    from game_player import GamePlayer

EL_DORADO_NUM_HEXES = 5
def el_dorado_generate_hexes(game_player: 'GamePlayer', game_state: 'GameState') -> list[str]:
    hexes = list(game_state.hexes.values())
    region_centers = random.sample(hexes, 2)
    i = 0
    while region_centers[0].distance_to(region_centers[1]) < 6 and i < 100:
        sample = random.sample(hexes, 2)
        if sample[0].distance_to(sample[1]) > region_centers[0].distance_to(region_centers[1]):
            region_centers = sample
        i += 1

    num_in_center_0 = random.randint(1, 3)
    num_in_center_1 = EL_DORADO_NUM_HEXES - num_in_center_0
    result = []
    for center, num_in_center in zip(region_centers, [num_in_center_0, num_in_center_1]):
        options = []
        d = 2
        while len(options) < num_in_center:
            nearby_hexes = center.get_hexes_within_range_expensive(game_state.hexes, d, exclude_ocean=True)
            options = [h.coords for h in nearby_hexes if h.city is None and not any(u.civ.id == game_player.civ_id for u in h.units)]
            d += 1
        result.extend(random.sample(options, num_in_center))
    return result

ORDER_FOOD = "food"
ORDER_WOOD = "wood"
ORDER_METAL = "metal"
ORDER_SCIENCE = "science"

class TENETS():
    TALES_OF_SCHEHERAZADE = TenetTemplate(
        advancement_level=1,
        name="Scheherazade's Tales",
        instant_effect=PointsEffect(lambda _c, _g: 6, label="Scheherazade", description="Gain 6 points."),
        sort_order=ORDER_WOOD,
    )

    MAUIS_FISHHOOK = TenetTemplate(
        advancement_level=1,
        name="Mauis Fishhook",
        instant_effect=GainSlotsEffect(2, BuildingType.RURAL),
        sort_order=ORDER_FOOD,
    )

    PROMETHEAN_FIRE = TenetTemplate(
        advancement_level=1,
        name="Promethean Fire",
        instant_effect=UpgradeTerrainEffect(2, TERRAINS.MOUNTAINS, Yields(metal=2, science=3), "Volcano"),
        sort_order=ORDER_SCIENCE,
    )

    DAVID_VS_GOLIATH = TenetTemplate(
        advancement_level=1,
        name="David vs Goliath",
        instant_effect=BuildUnitsEffect(UNITS.SLINGER, num=1, extra_str=2),
        sort_order=ORDER_METAL,
    )

    RISE_OF_EQUALITY = TenetTemplate(
        advancement_level=2,
        name="Rise of Equality",
        description="Steal 10 city_power income from all players in an age earlier than you.",
        sort_order=ORDER_FOOD,
    )

    PROMISE_OF_FREEDOM = TenetTemplate(
        advancement_level=2,
        name="Promise of Freedom",
        description="Each turn all players in an age earlier than you lose 1 vp; if your age is ahead of the game age, gain 1 vp.",
        sort_order=ORDER_SCIENCE,
    )

    HYMN_OF_UNITY = TenetTemplate(
        advancement_level=2,
        name="Hymn of Unity",
        description="Instantly capture cities from civs that are in an earlier age than yours without siege.",
        sort_order=ORDER_METAL,
    )

    GLORIOUS_ORDER = TenetTemplate(
        advancement_level=2,
        name="Glorious Order",
        description="You can build wonders from your civ's age when ahead of the global age. Cities of civs in ages behind yours demand 8 more food per turn.",
        sort_order=ORDER_WOOD,
    )

    HOLY_GRAIL = TenetTemplate(
        advancement_level=3,
        name="Holy Grail",
        description="When choosing Great People, you select two of the choices but lose 100 science.",
        quest_description="Kill 25 units belonging to the civ that controls the Holy City (at the time). If you control the Holy City, it gains 30 food demand per turn and this counts as 5 kills.",
        quest_complete_message="We may never find the goblet of the Lord. But the deeds of our crusades shall echo through the ages, and the heros of our people will remember the call.",
        quest_target=25,
        initialize_data=lambda game_player, game_state: {"holy_city_id": random.choice([c for c in game_state.cities_by_id.values() if c.civ != game_player.get_current_civ(game_state)]).id},
    )

    EL_DORADO = TenetTemplate(
        advancement_level=3,
        name="El Dorado",
        description="-1 max territories. In your territory capitals, +3 metal per military slot and +3 wood per urban slot.",
        quest_description=f"Explore the {EL_DORADO_NUM_HEXES} marked hexes.",
        quest_complete_message="After a long search we conclude that El Dorado was a myth. But we do not lose heart; the City of Gold always lay not in the ruined wilderness, but in our dreams. And this we will build the City with our own hands. Look not to the past for El Dorato ... look to the future.",
        quest_target=EL_DORADO_NUM_HEXES,
        initialize_data=lambda game_player, game_state: {"hexes": el_dorado_generate_hexes(game_player, game_state)},
    )

    FOUNTAIN_OF_YOUTH = TenetTemplate(
        advancement_level=3,
        name="Fountain of Youth",
        description="Your vitality decays one percentge point slower per turn.",
        quest_description="Tech to a tech no other civ has, 4 times.",
        quest_complete_message="In all the ages of history no person has escaped death by drinking from a simple fountain. But what no person can do, perhaps a people can. Though we each die, together our lineage and our ideas live on.",
        quest_target=4,
        initialize_data=lambda game_player, game_state: {"unclaimed_techs": [t.name for t in TECHS.all() if t != TECHS.RENAISSANCE and not any(c.has_tech(t) for c in game_state.civs_by_id.values())]},
    )

    YGGDRASILS_SEEDS = TenetTemplate(
        advancement_level=3,
        name="Yggdrasils Seeds",
        description="New cities you build start with 30 food, 30 wood, 30 metal.",
        quest_description="Each forest contains an acorn. Collect 15 acorns, by having sight of the hex at the start of the turn.",
        quest_complete_message="Yggdrasil's seeds have taken root. The world tree will grow and bear fruit for all eternity.",
        quest_target=15,
        initialize_data=lambda game_player, game_state: {"unseen_hexes": [h.coords for h in game_state.hexes.values() if h.terrain == TERRAINS.FOREST]},
    )

    FAITH = TenetTemplate(
        advancement_level=4,
        name="Faith",
        description="Gain double vps for wonder crowns.",
        sort_order=ORDER_WOOD,
    )

    RATIONALISM = TenetTemplate(
        advancement_level=4,
        name="Rationalism",
        description="Upon completing a tech, gain extra vps for its level above III.",
        sort_order=ORDER_SCIENCE,
    )

    HONOR = TenetTemplate(
        advancement_level=4,
        name="Honor",
        description="Gain double vps for clearing camps and fighting barbarian units.",
        sort_order=ORDER_METAL,
    )

    COMMUNITY = TenetTemplate(
        advancement_level=4,
        name="Community",
        description="Gain double vps for developing in your cities.",
        sort_order=ORDER_FOOD,
    )

    DRAGONS = TenetTemplate(
        advancement_level=5,
        name="Dragons",
        a5_unit_types=[UnitTag.RANGED],
    )

    UNICORNS = TenetTemplate(
        advancement_level=5,
        name="Unicorns",
        a5_unit_types=[UnitTag.MOUNTED],
    )

    GIANTS = TenetTemplate(
        advancement_level=5,
        name="Giants",
        a5_unit_types=[UnitTag.SIEGE, UnitTag.DEFENSIVE],
    )

    NINJAS = TenetTemplate(
        advancement_level=5,
        name="Ninjas",
        a5_unit_types=[UnitTag.INFANTRY],
    )

    SPLENDOR = TenetTemplate(
        advancement_level=6,
        name="Splendor",
        description="Gain more points from wonder crowns based on a previous civ: 2.5x your first civ, 2x your second, or 1.5x your third (whichever is best).",
        a6_score_key=score_strings.WONDER,
        a6_score_weights=[2.5, 2, 1.5],
        sort_order=ORDER_WOOD,
    )

    WISDOM = TenetTemplate(
        advancement_level=6,
        name="Wisdom",
        description="Gain more points from research based on a previous civ: 2x your first civ, 1x your second, or 0.5x your third (whichever is best).",
        a6_score_key=score_strings.TECH,
        a6_score_weights=[2, 1, 0.5],
        sort_order=ORDER_SCIENCE,
    )

    MIGHT = TenetTemplate(
        advancement_level=6,
        name="Might",
        description="Gain more points from unit kills based on a previous civ: 1.5x your first civ, 1x your second, or 0.5x your third (whichever is best).",
        a6_score_key=score_strings.UNIT_KILL,
        a6_score_weights=[1.5, 1, 0.5],
        sort_order=ORDER_METAL,
    )

    PROSPERITY = TenetTemplate(
        advancement_level=6,
        name="Prosperity",
        description="Gain more points from development based on a previous civ: 4x your first civ, 3x your second, or 2x your third (whichever is best).",
        a6_score_key=score_strings.DEVELOPMENT,
        a6_score_weights=[4, 3, 2],
        sort_order=ORDER_FOOD,
    )

    SPACE_RACE = TenetTemplate(
        advancement_level=7,
        name="Space Race",
        description="Your trade hub now spends 50 city power to steal 4 science from every other city.",
        a7_yield="science",
        sort_order=ORDER_SCIENCE,
    )

    IRON_CURTAIN = TenetTemplate(
        advancement_level=7,
        name="Iron Curtain",
        description="Your trade hub now spends 50 city power to steal 4 metal from every other city.",
        a7_yield="metal",
        sort_order=ORDER_METAL,
    )

    TRADE_WARS = TenetTemplate(
        advancement_level=7,
        name="Trade Wars",
        description="Your trade hub now spends 50 city power to steal 4 wood from every other city.",
        a7_yield="wood",
        sort_order=ORDER_WOOD,
    )

    POPULATION_BOOM = TenetTemplate(
        advancement_level=7,
        name="Population Boom",
        description="Your trade hub now spends 50 city power to steal 4 food from every other city.",
        a7_yield="food",
        sort_order=ORDER_FOOD,
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
    for i in range(1, 10)
}