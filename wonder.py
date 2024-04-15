from typing import TYPE_CHECKING, Optional
from wood_buildable import WoodBuildable

from wonder_template import WonderTemplate
from wonder_template_list import WONDERS

if TYPE_CHECKING:
    from civ import Civ
    from game_state import GameState

class Wonder(WoodBuildable):
    def __init__(self, template: WonderTemplate):
        super().__init__(template.name)
        self.template: WonderTemplate = template
        self.built_by_civ: Optional[Civ] = None
        self.big_boosted_civs: set[Civ] = set()
        self.boosted_civs: set[Civ] = set()
        self.unboosted_cost: float = 0

    @property
    def built(self):
        return self.built_by_civ is not None

    def roll_turn(self, game_state: 'GameState') -> None:
        if self.built:
            # Eventually there might be some kind of wonder.on_turn_roll() abilities that go here.
            pass
        
        else:
            all_civs = game_state.civs_by_id.values()
            new_boosted_civs: set[Civ] = {civ for civ in all_civs if self.template.boost_check(civ, game_state)}
            if len(self.big_boosted_civs) == 0:
                # This is the first turn anyone got a boost
                self.big_boosted_civs = new_boosted_civs
            else:
                # These civs didn't win the race but they get the small boost.
                self.boosted_civs = self.boosted_civs.union(new_boosted_civs)
            num_existing_wonders = len([w for w in game_state.wonders_by_level[self.template.advancement_level] if w.built])
            self.unboosted_cost = self.template.base_cost * (1 + 0.5 * num_existing_wonders)

    def building_cost_for_civ(self, civ: 'Civ') -> float:
        if civ in self.big_boosted_civs:
            return self.unboosted_cost * 0.5
        elif civ in self.boosted_civs:
            return self.unboosted_cost * 0.75
        return self.unboosted_cost

    def to_json(self):
        return {
            "template": self.template.name,
            "built_by_civ": self.built_by_civ.id if self.built_by_civ else None,
            "big_boosted_civs": [c.id for c in self.big_boosted_civs],
            "boosted_civs": [c.id for c in self.boosted_civs],
            "unboosted_cost": self.unboosted_cost,
        }

    @classmethod
    def from_json(cls, json: dict, game_state):
        w = cls(WONDERS.by_name(json["template"]))
        w.built_by_civ = game_state.civs_by_id[json["built_by_civ"]] if json["built_by_civ"] else None
        w.big_boosted_civs = {game_state.civs_by_id[c] for c in json["big_boosted_civs"]}
        w.boosted_civs = {game_state.civs_by_id[c] for c in json["boosted_civs"]}
        w.unboosted_cost = json["unboosted_cost"]
        return w
