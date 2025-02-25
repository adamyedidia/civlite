import math
from typing import TYPE_CHECKING, Generator, Literal, Optional, Union
from detailed_number import DetailedNumber
import score_strings
from building import Building, QueueEntry
from building_template import BuildingTemplate, BuildingType
from building_templates_list import BUILDINGS
from civ_template import CivTemplate
from civ import Civ
from camp import Camp
from effects_list import BuildEachUnitEffect, GainResourceEffect, GainUnhappinessEffect, GrowEffect, ResetHappinessThisCityEffect
from map_object_spawner import MapObjectSpawner
from move_type import MoveType
from region import Region
from settings import BASE_WONDER_COST, GOD_MODE
from tenet_template_list import TENETS
from terrain_templates_list import TERRAINS
from terrain_template import TerrainTemplate
from settings import AI, ADDITIONAL_PER_POP_FOOD_COST, BASE_FOOD_COST_OF_POP, CITY_CAPTURE_REWARD, DEVELOP_VPS, FOOD_DEMAND_REDUCTION_RECENT_OWNER_CHANGE, FOOD_DEMAND_REDUCTION_RECENT_OWNER_CHANGE_DECAY, FRESH_CITY_VITALITY_PER_TURN, REVOLT_VITALITY_PER_TURN, REVOLT_VITALITY_PER_UNHAPPINESS, STRICT_MODE, VITALITY_DECAY_RATE, UNIT_BUILDING_BONUSES, MAX_SLOTS, DEVELOP_COST, MAX_SLOTS_OF_TYPE
from unit import Unit
from unit_building import UnitBuilding
from unit_template import UnitTag, UnitTemplate
from unit_templates_list import UNITS
from wonder_template import WonderTemplate
from civ_templates_list import CIVS
from utils import deterministic_hash, generate_unique_id
import random
from city_names import CITY_NAMES_BY_CIV
from yields import DetailedYields, Yields
from logging_setup import logger

if TYPE_CHECKING:
    from hex import Hex
    from game_state import GameState
    from ability import Ability

TRADE_HUB_CITY_POWER_PER_TURN = 20

class BuildingDescription:
    def __init__(self):
        self.building_yields: Yields = Yields()
        self.non_vitality_yields: Yields = Yields()
        self.pseudoyields_for_ai_nonvitality: Yields = Yields()
        self.pseudoyields_for_ai_yesvitality: Yields = Yields()
        self.instant_yields: Yields = Yields()
        self.buffed_units: list[UnitTemplate] = []
        self.other_strings: list[str] = []

    @property
    def combined_display_yields(self) -> Yields:
        return self.building_yields + self.non_vitality_yields + self.instant_yields
    
    def to_json(self):
        return {
            "yields": self.building_yields.to_json(),
            "non_vitality_yields": self.non_vitality_yields.to_json(),
            "pseudoyields_for_ai_nonvitality": self.pseudoyields_for_ai_nonvitality.to_json(),
            "pseudoyields_for_ai_yesvitality": self.pseudoyields_for_ai_yesvitality.to_json(),
            "instant_yields": self.instant_yields.to_json(),
            "buffed_units": [u.name for u in self.buffed_units],
            "other_strings": self.other_strings,
            "combined_display_yields": self.combined_display_yields.to_json(),
        }
    
    @staticmethod
    def from_json(json_data):
        b = BuildingDescription()
        b.building_yields = Yields.from_json(json_data["yields"])
        b.non_vitality_yields = Yields.from_json(json_data["non_vitality_yields"])
        b.pseudoyields_for_ai_nonvitality = Yields.from_json(json_data["pseudoyields_for_ai_nonvitality"])
        b.pseudoyields_for_ai_yesvitality = Yields.from_json(json_data["pseudoyields_for_ai_yesvitality"])
        b.instant_yields = Yields.from_json(json_data["instant_yields"])
        b.buffed_units = [UNITS.by_name(u) for u in json_data["buffed_units"]]
        b.other_strings = json_data["other_strings"]
        return b

class City(MapObjectSpawner):
    def __init__(self, name: str, region: Region, civ: Civ | None = None, id: Optional[str] = None, hex: 'Hex | None' = None):
        super().__init__(civ, hex)
        self.id = id or generate_unique_id("CITY")
        self.ever_controlled_by_civ_ids: dict[str, bool] = {civ.id: True} if civ else {}
        self.name = name
        self.population = 1
        self.food = 0.0
        self.metal = 0.0
        self.wood = 0.0
        self.food_demand: DetailedNumber = DetailedNumber()
        self.food_demand_reduction_recent_owner_change: int = 0
        self.focus: str = 'food'
        self.rural_slots = 1
        self.urban_slots = 1
        self.military_slots = 1
        self.buildings_queue: list[QueueEntry] = []
        self.bot_favorite_builds: list[BuildingTemplate] = []
        self.buildings: list[Building] = []
        self.unit_buildings: list[UnitBuilding] = [UnitBuilding(UNITS.WARRIOR)]
        self.unit_buildings[0].active = True
        self.available_city_buildings: list[BuildingTemplate] = []
        self.available_wonders: list[WonderTemplate] = []
        self.available_unit_buildings: list[UnitTemplate] = []
        self.building_descriptions: dict[str, BuildingDescription] = {}
        self.available_buildings_payoff_times: dict[str, int] = {}
        self.capital = False
        self._territory_parent_id: Optional[str] = None
        self._territory_parent_coords: Optional[str] = None
        self.available_units: list[UnitTemplate] = []
        self.projected_income = Yields()
        self.projected_income_city_center = Yields()
        self.projected_income_base = DetailedYields()  # income without focus
        self.projected_income_focus = Yields()  # income from focus
        self.projected_income_puppets: dict[str, dict[str, tuple[float, int]]] = {'wood': {}, 'metal': {}} # (amount, distance)
        self.projected_on_decline_leaderboard: bool = False
        self.projected_build_queue_depth: int = 0
        self.projected_bulldozes: list[UnitTemplate] = []
        self.terrains_dict: dict[TerrainTemplate, int] = {}
        self.founded_turn: int | None = None
        self.develops_this_civ: dict[BuildingType, int] = {d: 0 for d in BuildingType}
        self.already_harvested_this_turn: bool = False
        self.last_owner_civ_id: Optional[str] = None

        # Revolt stuff
        self.civ_to_revolt_into: Optional[CivTemplate] = None
        self.revolting_starting_vitality: float = 1.0
        self.unhappiness: float = 0.0
        self.is_decline_view_option: bool = False
        self.revolt_unit_count: int = 0
        self.region = region

    def __repr__(self):
        return f"<City {self.name} @ {self.hex.coords if self._hex else None}>"
    
    def __hash__(self):
        return deterministic_hash(self.id)

    def has_building(self, template: BuildingTemplate | UnitTemplate | WonderTemplate) -> bool:
        if isinstance(template, UnitTemplate):
            return any(b.template == template for b in self.unit_buildings)
        else:
            return any(b._template == template for b in self.buildings)

    def orphan_territory_children(self, game_state: 'GameState', make_new_territory=True):
        """
        Call before changing ownership of a city to clear any puppets who have it as parent.
        """
        children: list[City] = [city for city in game_state.cities_by_id.values() if city.get_territory_parent(game_state) == self]
        if len(children) == 0:
            return
        if make_new_territory:
            new_territory_capital: City | None = max(children, key=lambda c: (c.population, c.id))
            new_territory_capital.make_territory_capital(game_state)
        else:
            new_territory_capital = None
        for child in children:
            if child != new_territory_capital:
                child.set_territory_parent_if_needed(game_state, adopt_focus=False)

    def _remove_income_from_parent(self, game_state: 'GameState') -> None:
        parent: City | None = self.get_territory_parent(game_state)
        if parent:
            for resource, data in parent.projected_income_puppets.items():
                if self.name in data:
                    del data[self.name]

    def make_territory_capital(self, game_state: 'GameState') -> None:
        self._remove_income_from_parent(game_state)
        self._territory_parent_id = None
        self._territory_parent_coords = None

    def set_territory_parent_if_needed(self, game_state: 'GameState', adopt_focus: bool, force=False) -> None:
        my_territories: list[City] = [city for city in game_state.cities_by_id.values() if city.civ == self.civ and city.is_territory_capital and city != self]
        choices: list[City] = [city for city in my_territories]
        if len(my_territories) < self.civ.max_territories and not force:
            # Room for another territory capital.
            self.make_territory_capital(game_state)
        else:
            # Pick the closest one to be my parent.
            if len(choices) == 0:
                raise ValueError(f"No choices for territory parent for {self.name}.")
            choice: City = min(choices, key=lambda c: (self.hex.distance_to(c.hex), c.capital, -c.population, c.id))
            self._remove_income_from_parent(game_state)
            self._territory_parent_id = choice.id
            self._territory_parent_coords = choice.hex.coords
            self.buildings_queue = []
            self.clear_unit_builds()

            if adopt_focus:
                self.focus = choice.focus

            # Take all the wood and metal over.
            new_parent = self.get_territory_parent(game_state)
            assert new_parent is not None
            distance = self.hex.distance_to(new_parent.hex)
            penalty = new_parent.puppet_distance_penalty(distance)
            new_parent.wood += self.wood * penalty
            self.wood = 0
            for bldg in new_parent.unit_buildings:
                new_parent.metal += bldg.metal * penalty
                bldg.metal = 0
            new_parent.metal += self.metal * penalty
            self.metal = 0

    @property
    def is_territory_capital(self) -> bool:
        return self._territory_parent_id is None
    
    def get_puppets(self, game_state: 'GameState') -> list['City']:
        return [city for city in game_state.cities_by_id.values() if city.get_territory_parent(game_state) == self]

    def get_territory_parent(self, game_state: 'GameState') -> Optional['City']:
        if self._territory_parent_id is None:
            return None
        elif self._territory_parent_id in game_state.cities_by_id:
            return game_state.cities_by_id[self._territory_parent_id]
        else:
            # This can happen if the parent isn't visible to the viewing civ.
            return None

    def midturn_update(self, game_state: 'GameState') -> None:
        """
        Update things that could have changed due to the controlling player fiddling with focus etc.
        """
        assert self.civ.vitality_decay_rate.value > 0, "Vitality decay rate is 0???. Make sure to call civ.update_vitality_decay_rate before city.midturn_update."
        if self.is_territory_capital:
            for puppet in self.get_puppets(game_state):
                puppet.midturn_update(game_state)
        self.adjust_projected_yields(game_state)
        self.adjust_projected_builds(game_state)
        if self.is_territory_capital:
            # Important to do this after adjusting yields because some payoff calculations depend on the current yields.
            self._refresh_available_buildings_and_units(game_state)
        self.adjust_projected_unit_builds()
        if self.is_territory_capital and self.civ.game_player and not self.civ.game_player.is_bot:
            self.bot_favorite_builds, _ = self.bot_choose_building_queue(game_state)


    def is_trade_hub(self):
        return self.civ.trade_hub_id == self.id
    
    def is_fake_city(self) -> bool:
        return self.hex.city != self

    def _puppet_penalty_per_distance(self) -> float:
        bldg_factors = [ability.numbers[0] for ability, _ in self.passive_building_abilities_of_name('ReducePuppetDistancePenalty')]
        return min([.1] + bldg_factors)
    
    def puppet_distance_penalty(self, distance: int) -> float:
        return max(0.1, 1 - self._puppet_penalty_per_distance() * distance)

    def unit_building_from_template(self, template: UnitTemplate):
        for bldg in self.unit_buildings:
            if bldg.template == template:
                return bldg
        raise KeyError(f"No unit building for {template}")

    def toggle_unit_build(self, unit: UnitTemplate):
        if STRICT_MODE:
            assert self.is_territory_capital, f"{self.name} tried to toggle unit build while a puppet"
            assert unit in self.available_units, f"{self.name} trying to build unit {unit} but only have {self.available_units}."
        unit_bldg = self.unit_building_from_template(unit)
        unit_bldg.active = not unit_bldg.active
        self.adjust_projected_unit_builds()

    def clear_unit_builds(self):
        for bldg in self.unit_buildings:
            bldg.active = False

    def adjust_projected_unit_builds(self):
        units_active = [u for u in self.unit_buildings if u.active]
        if len(units_active) == 0: return

        units_active.sort(key=lambda u: u.template.advancement_level)
        for bldg, bonus in zip(units_active, reversed(UNIT_BUILDING_BONUSES[len(units_active)])):
            bldg.production_rate = bonus

        total_metal = self.projected_total_metal
        for unit_building in units_active:
            # logger.info(f"{self.name} projecting {unit_building.template} {total_metal}")
            unit_building.adjust_projected_unit_builds(total_metal=total_metal)

    @property
    def projected_total_wood(self) -> float:
        if self.already_harvested_this_turn:
            return self.wood
        else:
            return self.wood + self.projected_income["wood"]
        
    @property
    def projected_total_metal(self) -> float:
        if self.already_harvested_this_turn:
            return self.metal
        else:
            return self.metal + self.projected_income["metal"]

    def adjust_projected_builds(self, game_state):
        if self.revolting_to_rebels_this_turn:
            self.projected_build_queue_depth = 0
        else:
            wood_available = self.projected_total_wood
            costs = [entry.get_cost(game_state) for entry in self.buildings_queue]
            free_wood = [sum(effect.amount for effect in b.template.on_build if isinstance(effect, GainResourceEffect) and effect.resource == "wood")
                    if not isinstance(b.template, UnitTemplate) else 0
                    for b in self.buildings_queue]
            costs = [cost - w for cost, w in zip(costs, free_wood)]

            cumsum_cost = [sum(costs[:i + 1]) for i in range(len(costs))]
            # Find the first place it's too much
            cumsum_excess = [wood_available - c for c in cumsum_cost]
            first_neg_idx = next((i for i, c in enumerate(cumsum_excess) if c < 0), len(cumsum_excess))
            self.projected_build_queue_depth = first_neg_idx

        unit_buildings_to_bulldoze = max(0, -self.empty_slots(BuildingType.UNIT, include_in_queue=True))
        if STRICT_MODE:
            assert unit_buildings_to_bulldoze <= self.num_buildings_of_type(BuildingType.UNIT, include_in_queue=True)
        targets = self.unit_buildings_ranked_for_bulldoze()
        for t in targets[:unit_buildings_to_bulldoze]:
            t.delete_queued = True
        for t in targets[unit_buildings_to_bulldoze:]:
            t.delete_queued = False

    def adjust_projected_yields(self, game_state: 'GameState') -> None:
        if self.revolting_to_rebels_this_turn:
            self.projected_income_base = DetailedYields()
            self.projected_income_focus = Yields(food=0, metal=0, wood=0, science=0)
            self.food_demand = DetailedNumber()
            self.projected_income_puppets = {resource: {} for resource in self.projected_income_puppets}
        else:
            self.projected_income_base = self._get_projected_yields_without_focus(game_state)
            self.projected_income_focus = self._get_projected_yields_from_focus(game_state)
            self.food_demand = self._calculate_food_demand(game_state)

        self.projected_income = self.projected_income_base.value + {self.focus: self.projected_income_focus[self.focus]}

        my_a7_tenet = self.civ.tenet_at_level(7)
        if self.is_trade_hub() and my_a7_tenet is None:
            # Have to calculate income BEFORE the trade hub, so that trade hub knows how much to do.
            self.projected_income.unhappiness += max(0, self.food_demand.value - self.projected_income.food)
            self.projected_income.city_power += max(0, self.projected_income.food - self.food_demand.value)

            city_power_to_consume = min(20, 2 * (self.unhappiness + self.projected_income.unhappiness))
            self.projected_income.unhappiness -= 0.5 * city_power_to_consume
            self.civ.trade_hub_city_power_consumption = city_power_to_consume
        elif self.is_trade_hub() and my_a7_tenet is not None:
            city_power_to_consume = 50
            amount = 4
            type = my_a7_tenet.a7_yield
            assert type is not None
            yields = Yields(**{type: amount * len(game_state.cities_by_id)})
            self.projected_income += yields
            self.projected_income_base.add_yields("Trade Hub", yields)
            game_state.a7_tenets_yields_stolen_this_turn[self.civ.id] = Yields(**{type: amount})
            self.civ.trade_hub_city_power_consumption = city_power_to_consume

            # Have to calculate income AFTER the trade hub, so that if we're stealing food it affects the income.
            self.projected_income.unhappiness += max(0, self.food_demand.value - self.projected_income.food)
            self.projected_income.city_power += max(0, self.projected_income.food - self.food_demand.value)
        else:
            self.projected_income.unhappiness += max(0, self.food_demand.value - self.projected_income.food)
            self.projected_income.city_power += max(0, self.projected_income.food - self.food_demand.value)       

        # If I'm a puppet, give my yields to my parent.
        parent: City | None = self.get_territory_parent(game_state)
        if parent:
            distance: int = self.hex.distance_to(parent.hex)
            distance_penalty: float = parent.puppet_distance_penalty(distance)
            parent.projected_income_puppets['wood'][self.name] = (self.projected_income.wood * distance_penalty, distance)
            parent.projected_income_puppets['metal'][self.name] = (self.projected_income.metal * distance_penalty, distance)
            parent.adjust_projected_yields(game_state)
        else:
            self.projected_income += {key: sum(amnt for amnt, distance in puppet_vals.values()) for key, puppet_vals in self.projected_income_puppets.items()}

        self.projected_on_decline_leaderboard = (self.unhappiness + self.projected_income.unhappiness > game_state.unhappiness_threshold)

    def _get_projected_yields_without_focus(self, game_state: 'GameState') -> DetailedYields:
        yields = DetailedYields()

        self.projected_income_city_center = (Yields(science=1) + {self.hex.terrain.city_center_yield: 1}) * self.population
        yields.add_yields("Town Square", self.projected_income_city_center)

        terrain_yields: Yields = sum([hex.yields for hex in self.hex.get_neighbors(game_state.hexes, include_self=True)], Yields())
        yields.add_yields("Terrain", terrain_yields)

        bldg_yields = [bldg.calculate_yields_previtality(self) for bldg in self.buildings]
        bldg_yields = [y for y in bldg_yields if y is not None]
        total_bldg_yields = sum(bldg_yields, Yields())
        yields.add_yields("Buildings", total_bldg_yields)
        
        yields.add_yields("Empty Slots", Yields(
            food=self.empty_slots(BuildingType.RURAL, include_in_queue=False),
            metal=self.empty_slots(BuildingType.UNIT, include_in_queue=False) * 2,
            science=self.empty_slots(BuildingType.URBAN, include_in_queue=False) * 2,
        ))

        if self.civ.has_ability("IncreaseCapitalYields") and self.capital:
            resource, amount = self.civ.numbers_of_ability("IncreaseCapitalYields")
            yields[resource].add(self.civ.template.name, amount)

        if self.civ.has_tenet(TENETS.EL_DORADO, check_complete_quest=True):
            yields.add_yields(TENETS.EL_DORADO.name, Yields(
                metal=3 * self.military_slots,
                wood=3 * self.urban_slots,
            ))

        yields.set_multiplier(self.civ.vitality)

        bldg_yields = [bldg.calculate_yields_postvitality(self) for bldg in self.buildings]
        bldg_yields = [y for y in bldg_yields if y is not None]
        total_bldg_yields = sum(bldg_yields, Yields())
        yields.add_yields("Wonders", total_bldg_yields)

        for civ_id, stolen_yields in game_state.a7_tenets_yields_stolen_last_turn.items():
            game_player = game_state.civs_by_id[civ_id].game_player
            username = "ours" if game_player == self.civ.game_player else game_player.username if game_player else "Unknown"
            yields.add_yields(f"Trade Hub ({username})", stolen_yields * -1)

        return yields

    def _get_projected_yields_from_focus(self, game_state) -> Yields:
        yields = Yields(metal=1, wood=1, science=1, food=1) * self.population

        if self.civ.has_ability('IncreaseFocusYields'):
            bonus_resource, count = self.civ.numbers_of_ability('IncreaseFocusYields')
            yields += {bonus_resource: count}
        for ability, _ in self.passive_building_abilities_of_name('IncreaseFocusYieldsPerPopulation'):
            focus, amount_per_pop = ability.numbers
            double = self.hex.terrain.city_center_yield == focus
            yields += {focus: amount_per_pop * self.population * (2 if double else 1)}

        return yields * self.civ.vitality

    def harvest_yields(self, game_state: 'GameState') -> None:
        self.adjust_projected_yields(game_state)  # TODO(dfarhi) this probably shouldn't be neessary since it should be called whenever the state changes?
        self.food += self.projected_income.food
        # Science and city power are harvested by the Civ instance.
        self.unhappiness += self.projected_income.unhappiness

        if self.is_territory_capital:
            self.wood += self.projected_income.wood
            self.metal += self.projected_income.metal
            if len(self.active_unit_buildings) > 0:
                for b in self.active_unit_buildings:
                    # logger.info(f"{self.name} harvesting {b.template} {self.metal}")
                    b.harvest_yields(self.metal)
                self.metal = 0
        self.already_harvested_this_turn = True

    @property
    def no_cities_adjacent_range(self) -> int:
        return 1

    def roll_turn_pre_harvest(self, game_state):
        """ All the turn roll stuff up to and including harvesting yields"""
        self.update_seen_by_players(game_state)
        self.harvest_yields(game_state)

    def roll_turn_post_harvest(self, sess, game_state: 'GameState', fake: bool = False) -> None:
        """
        All the turn roll stuff after harvest.
        They are split out so that we can make sure all cities harvest before any cities do stuff that could change another city's yields

        Fake: is this just a fake city for decline view?
        """
        if not fake:
            self.grow(game_state)
            if self.is_territory_capital:
                self.build_units(game_state)
                self.build_buildings(game_state)
            self.roll_wonders(game_state)
            self.handle_siege(sess, game_state)

        self.handle_unhappiness(game_state)

        if self.civ.has_tenet(TENETS.HOLY_GRAIL) and self.civ.game_player and self.id == self.civ.game_player.tenets[TENETS.HOLY_GRAIL]["holy_city_id"]:
            self.civ.game_player.increment_tenet_progress(TENETS.HOLY_GRAIL, 5)

    def update_seen_by_players(self, game_state: 'GameState') -> None:
        for civ in game_state.civs_by_id.values():
            if civ.game_player is not None:
                if self.hex.visible_to_civ(civ):
                    civ.game_player.add_fog_city(self)

    def roll_wonders(self, game_state: 'GameState') -> None:
        for bldg in self.buildings:
            bldg.update_ruined_status(self, game_state)
            if not bldg.ruined:
                for effect in bldg.per_turn:
                    effect.apply(self, game_state)

    def age(self, game_state) -> int:
        assert self.founded_turn is not None, "Can't get age of a fake city."
        return game_state.turn_num - self.founded_turn

    def _calculate_food_demand(self, game_state: 'GameState', include_recent_owner_change: bool = True) -> DetailedNumber:
        if self.founded_turn is None: return DetailedNumber()  # Not sure why we're even calculating this.
        if self.capital: 
            return DetailedNumber()
        result = DetailedNumber(min_zero=True)
        result.add("Age", 1.0 * self.age(game_state))

        if self.is_territory_capital:
            result.add("Puppets", -2 * len(self.get_puppets(game_state)))

        for ability, building in self.civ.passive_building_abilities_of_name('DecreaseFoodDemand', game_state):
            result.add(building.building_name, -ability.numbers[1])
        for ability, building in self.passive_building_abilities_of_name('DecreaseFoodDemand'):
            result.add(building.building_name, -ability.numbers[0] + ability.numbers[1])
        for game_player in game_state.game_player_by_player_num.values():
            if game_player.civ_id is None:
                # This can happen if the game player is in mid decline.
                continue
            if game_player.has_tenet(TENETS.GLORIOUS_ORDER) and game_player.get_current_civ(game_state).get_advancement_level() > self.civ.get_advancement_level():
                result.add(f"{TENETS.GLORIOUS_ORDER.name} ({game_player.username})", 8)
        parent = self.get_territory_parent(game_state)
        if parent is not None:
            for ability, building in parent.passive_building_abilities_of_name('DecreaseFoodDemandPuppets'):
                result.add(building.building_name, -ability.numbers[0])

        if self.civ.has_tenet(TENETS.HOLY_GRAIL) and self.civ.game_player and self.id == self.civ.game_player.tenets[TENETS.HOLY_GRAIL]["holy_city_id"]:
            result.add("Holy Grail", 30)

        if include_recent_owner_change:
            result.add("Recent conquest", -self.food_demand_reduction_recent_owner_change)
        return result

    def handle_unhappiness(self, game_state: 'GameState') -> None:
        if self.is_fake_city():
            self.revolting_starting_vitality = 1.0 + FRESH_CITY_VITALITY_PER_TURN * game_state.turn_num
        else:
            self.revolting_starting_vitality = 1.0 + REVOLT_VITALITY_PER_TURN * game_state.turn_num + REVOLT_VITALITY_PER_UNHAPPINESS * self.unhappiness

        if GOD_MODE:
            self.revolting_starting_vitality *= 10
        
        self.food_demand_reduction_recent_owner_change = max(0, self.food_demand_reduction_recent_owner_change - FOOD_DEMAND_REDUCTION_RECENT_OWNER_CHANGE_DECAY)

    @property
    def revolting_to_rebels_this_turn(self) -> bool:
        return self.unhappiness >= 100 and self.civ_to_revolt_into is not None and self.under_siege_by_civ is None

    def revolt_to_rebels(self, game_state: 'GameState') -> None:
        if STRICT_MODE:
            assert self.revolting_to_rebels_this_turn, f"City {self.name} shouldn't be revolting to rebels this turn."
        logger.info(f"City {self.name} revolting to rebels.")
        # Revolt to AI
        game_state.process_decline_option(self.hex.coords, [], is_game_player=False)
        game_state.make_new_civ_from_the_ashes(self)
        # Rebel civs have no great person
        self.civ.great_people_choices = []

    def grow_inner(self, game_state: 'GameState') -> None:
        self.population += 1

    def grow(self, game_state: 'GameState') -> None:
        while self.food >= self.growth_cost():
            self.food -= self.growth_cost()
            self.grow_inner(game_state)

    def growth_cost(self) -> float:
        total_growth_cost_reduction = 0.0

        for ability, _ in self.passive_building_abilities_of_name('CityGrowthCostReduction'):
            total_growth_cost_reduction += ability.numbers[0]

        return (BASE_FOOD_COST_OF_POP + self.population * ADDITIONAL_PER_POP_FOOD_COST) * max(1 - total_growth_cost_reduction, 0.3)

    def populate_terrains_dict(self, game_state: 'GameState') -> None:
        for hex in self.hex.get_neighbors(game_state.hexes, include_self=True):
            if not hex.terrain in self.terrains_dict:
                self.terrains_dict[hex.terrain] = 1
            else:
                self.terrains_dict[hex.terrain] += 1

    def _refresh_available_buildings_and_units(self, game_state: 'GameState'):
        if self.civ is None:
            return
        self.available_units = sorted([b.template for b in self.unit_buildings])
        
        if self.empty_slots(BuildingType.UNIT, include_in_queue=False) <= 0:
            min_level = min([u.advancement_level for u in self.available_units])
        else:
            min_level = 0
        if any([u.template.has_tag(UnitTag.DEFENSIVE) for u in self.unit_buildings]):
            # Can always replace defensive units.
            min_level = 0
        self.available_unit_buildings: list[UnitTemplate] = sorted([u for u in self.civ.available_unit_buildings if u.advancement_level >= min_level and not self.has_building(u)], reverse=True)
        if self.civ.has_tenet(TENETS.GLORIOUS_ORDER) and self.civ.get_advancement_level() >= game_state.advancement_level:
            self.available_wonders: list[WonderTemplate] = sorted(sum([game_state.available_wonders_by_age[i] for i in range(min(int(self.civ.get_advancement_level()) + 1, 9))], []))
        else:
            self.available_wonders: list[WonderTemplate] = sorted(game_state.available_wonders)
        self.available_city_buildings = self.civ.available_city_buildings

        self._update_city_building_descriptions(game_state)

        # Remove totally useless ones
        self.available_city_buildings = [b for b in self.available_city_buildings if not (b.useless_if_zero_yields and self.building_descriptions[b.name].combined_display_yields.total() == 0)]

        self.available_city_buildings.sort(key=lambda b: (
            -self.building_descriptions[b.name].combined_display_yields.total(),
            -b.advancement_level,
            b.name,
        ))

        # Validate queue
        self.buildings_queue = [entry for entry in self.buildings_queue if 
                                entry.template in self.available_city_buildings + self.available_unit_buildings + self.available_wonders]

    def calculate_payoff_time(self, yields: float, cost: float, vitality_exempt_yields: float = 0) -> float:
        civ_decay_rate = self.civ.vitality_decay_rate.value
        if civ_decay_rate == 0 and STRICT_MODE:
            raise ValueError("Vitality decay rate is 0???")
        # How much will it produce next turn?
        actual_yields = yields * (self.civ.vitality * (1 - civ_decay_rate))
        # Need to find a time t such that sum(actual_yields * (1 - civ_decay_rate)^k + vitality_exempt_yields) = cost
        # ==> actual_yields * (1 - (1 - civ_decay_rate)^t) /civ_decay_rate + vitality_exempt_yields * t = cost
        def solve_payoff_time(t):
            return actual_yields * (1 - (1 - civ_decay_rate)**t) / civ_decay_rate + vitality_exempt_yields * t - cost

        # Use binary search to find the payoff time
        left, right = 0, 10
        while right - left > 0.5:
            mid = (left + right) / 2
            if solve_payoff_time(mid) < 0:
                left = mid
            else:
                right = mid

        payoff_turns = right

        # Add 1 to account for the first turn (when it makes no yields since we're building it).
        payoff_turns += 1
        return payoff_turns
    
    def _calculate_city_building_description(self, building_template: BuildingTemplate, game_state: 'GameState') -> BuildingDescription:
        desc = BuildingDescription()
        desc.building_yields = building_template.calculate_yields.calculate(self) if building_template.calculate_yields is not None else Yields()

        for ability in building_template.abilities:
            if ability.name == "IncreaseFocusYieldsPerPopulation":
                resource: str = ability.numbers[0]
                amount: int = ability.numbers[1]
                double = self.hex.terrain.city_center_yield == resource
                desc.building_yields += Yields(**{resource: self.population * amount * (2 if double else 1)})

            if ability.name == "CityGrowthCostReduction":
                desc.other_strings.append(f"-{ability.numbers[0]:.0%}")
                ratio = ability.numbers[0]
                effective_income_multiplier = 1 / ratio
                effective_income_bonus = self.projected_income_base.food.value * (effective_income_multiplier - 1)
                previtality_effective_income_bonus = effective_income_bonus * (1 / self.civ.vitality)
                desc.pseudoyields_for_ai_yesvitality += Yields(food=previtality_effective_income_bonus, city_power=-previtality_effective_income_bonus)

            if ability.name == "DecreaseFoodDemand":
                resting_food_demand: float = self._calculate_food_demand(game_state, include_recent_owner_change=False).value
                food_demand_reduced: float = min(ability.numbers[0], resting_food_demand)
                unhappiness_saved: float = max(0, min(food_demand_reduced, resting_food_demand - self.projected_income.food))
                city_power_gained: float = food_demand_reduced - unhappiness_saved
                desc.non_vitality_yields.unhappiness += -unhappiness_saved
                desc.non_vitality_yields.city_power += city_power_gained
                # Note: ignores trade hub, that could be improved.

                # For the part that affects all other cities, let's just pessimistically assume that it's all city power.
                desc.non_vitality_yields.city_power += ability.numbers[1] * (len(self.civ.get_my_cities(game_state)) - 1)

            if ability.name == "DecreaseFoodDemandPuppets":
                for puppet in self.get_puppets(game_state):
                    resting_food_demand: float = puppet._calculate_food_demand(game_state, include_recent_owner_change=False).value
                    food_demand_reduced: float = min(ability.numbers[0], resting_food_demand)
                    unhappiness_saved: float = max(0, min(food_demand_reduced, resting_food_demand - puppet.projected_income.food))
                    city_power_gained: float = food_demand_reduced - unhappiness_saved
                    desc.non_vitality_yields.unhappiness += -unhappiness_saved
                    desc.non_vitality_yields.city_power += city_power_gained

            if ability.name == "ReducePuppetDistancePenalty":
                post_vitality_yields = Yields(**{
                    resource: sum(
                        amount / self.puppet_distance_penalty(distance) * (self._puppet_penalty_per_distance() - ability.numbers[0]) * distance
                        for amount, distance in puppet_infos.values()
                    )
                    for resource, puppet_infos in self.projected_income_puppets.items()})
                # This needs to count as a yes-vitality-adjusted yield since the yields will drop with future vitality.
                # But it's a final income (it's not supposed to be multiplied by vitality directly to ge the income).
                # So we divide it by vitality to get the correct value.
                desc.building_yields += post_vitality_yields * (1 / self.civ.vitality)

            if ability.name == "UnitsExtraStrengthByAge":
                age, buff = ability.numbers
                for unit_building in self.unit_buildings:
                    if unit_building.template.advancement_level >= age:
                        desc.buffed_units.append(unit_building.template)
                        buff_ratio = Unit.get_damage_to_deal_from_effective_strengths(unit_building.template.strength + buff, unit_building.template.strength) / Unit.get_damage_to_deal_from_effective_strengths(unit_building.template.strength, unit_building.template.strength + buff)
                        buff_ratio = buff_ratio ** 0.5  # Hack to make the AI not obsessed with these buildings. 
                        approximate_metal_value = buff_ratio * self.projected_income.metal
                        approximate_metal_value_yesvitality = approximate_metal_value * (1 / self.civ.vitality)
                        desc.pseudoyields_for_ai_yesvitality += Yields(metal=approximate_metal_value_yesvitality)

            if ability.name == "UnitsExtraStrengthByTag":
                tag, buff = ability.numbers
                for unit_building in self.unit_buildings:
                    if unit_building.template.has_tag(tag):
                       desc.buffed_units.append(unit_building.template)
                       buff_ratio = Unit.get_damage_to_deal_from_effective_strengths(unit_building.template.strength + buff, unit_building.template.strength) / Unit.get_damage_to_deal_from_effective_strengths(unit_building.template.strength, unit_building.template.strength + buff)
                       buff_ratio = buff_ratio ** 0.5  # Hack to make the AI not obsessed with these buildings. 
                       approximate_metal_value = buff_ratio * self.projected_income.metal
                       approximate_metal_value_yesvitality = approximate_metal_value * (1 / self.civ.vitality)
                       desc.pseudoyields_for_ai_yesvitality += Yields(metal=approximate_metal_value_yesvitality)

            if ability.name == "Airforce":
                strength, af_range = ability.numbers
                desc.other_strings.append(f"+{strength}")
                hexes_in_range = list(self.hex.get_hexes_within_range_expensive(game_state.hexes, range=af_range))
                num_enemy_cities = sum(1 for h in hexes_in_range if h.city is not None and h.city.civ != self.civ)
                num_enemy_units = sum(u.get_stack_size() for h in hexes_in_range for u in h.units if u.civ != self.civ)
                area_combatiness = max(num_enemy_cities / 3, num_enemy_units / 10)

                my_cities_total_metal_income_buff = sum(u.projected_metal_income * strength / u.template.strength for h in hexes_in_range if h.city is not None and h.city.civ == self.civ for u in h.city.unit_buildings)
                my_units_approx_metal_buff = sum(u.template.metal_cost * strength / u.template.strength * u.get_stack_size() for h in hexes_in_range for u in h.units if u.civ == self.civ)

                effective_metal_income = (my_cities_total_metal_income_buff + 0.3 * my_units_approx_metal_buff) * area_combatiness
                desc.pseudoyields_for_ai_yesvitality += Yields(metal=effective_metal_income)

            if ability.name == "Deployment Center":
                metal_value = 0.1 * self.projected_income["metal"]
                metal_value_yesvitality = metal_value * (1 / self.civ.vitality)
                desc.pseudoyields_for_ai_yesvitality += Yields(metal=metal_value_yesvitality)

            if ability.name == "ExtraTerritory":
                desc.other_strings.append(f"+1")
                if self.civ.max_territories <= len(self.civ.get_my_cities(game_state)):
                    desc.pseudoyields_for_ai_yesvitality += Yields(food=2, science=2, wood=2, metal=2)  # Pretty made-up numbers.

        for effect in building_template.on_build:
            if isinstance(effect, ResetHappinessThisCityEffect):
                desc.instant_yields += Yields(unhappiness=-self.unhappiness)
            elif isinstance(effect, GainResourceEffect):
                desc.instant_yields += Yields(**{effect.resource: effect.amount})
            elif isinstance(effect, GainUnhappinessEffect):
                desc.instant_yields += Yields(unhappiness=effect.amount)
            elif isinstance(effect, GrowEffect):
                if effect.amount is not None:
                    for i in range(effect.amount):
                        desc.instant_yields += Yields(food=self.growth_cost() + 2 * i)
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        for effect in building_template.per_turn:
            if isinstance(effect, BuildEachUnitEffect):
                for unit in self.available_units:
                    desc.pseudoyields_for_ai_nonvitality += Yields(metal=unit.metal_cost)
                    desc.buffed_units.append(unit)
                desc.pseudoyields_for_ai_nonvitality += Yields(food=-self.growth_cost(), city_power=self.growth_cost())
        return desc

    def _update_city_building_descriptions(self, game_state: 'GameState') -> None:
        for building_template in self.available_city_buildings + [b._template for b in self.buildings_of_type(BuildingType.RURAL) + self.buildings_of_type(BuildingType.URBAN)]:
            assert isinstance(building_template, BuildingTemplate)
            desc: BuildingDescription = self._calculate_city_building_description(building_template, game_state)
            self.building_descriptions[building_template.name] = desc
            combined_yesvitality_yields = desc.building_yields.total()
            combined_vitality_exempt_yields = desc.non_vitality_yields.total()
            if combined_yesvitality_yields + combined_vitality_exempt_yields > 0:
                slot_yields = 2 if building_template.type == BuildingType.URBAN else 1
                self.available_buildings_payoff_times[building_template.name] = math.ceil(self.calculate_payoff_time(combined_yesvitality_yields - slot_yields, vitality_exempt_yields=combined_vitality_exempt_yields, cost=building_template.cost))

    def has_production_building_for_unit(self, unit: UnitTemplate) -> bool:
        return self.has_building(unit)

    @property
    def active_unit_buildings(self):
        return [u for u in self.unit_buildings if u.active]

    def build_units(self, game_state: 'GameState') -> None:
        build_dict = {u: u.projected_unit_count for u in self.active_unit_buildings}
        max_units = max(build_dict.values()) if len(build_dict) > 0 else 0
        # Interleave them for better diversity
        for i in range(max_units):
            for bldg, target_num in sorted(build_dict.items(), key=lambda x: (x[1], random.random())):  # sort just for determinism.
                if i < target_num:
                    logger.info(f"{self.name}@{self.hex.coords} building {bldg.template.name} {i}/{target_num}, has {bldg.metal}")
                    unit = self.build_unit(game_state, bldg.template) 
                    if unit is not None:
                        bldg.metal -= bldg.template.metal_cost

    def sight_range(self, short_sighted: bool) -> int:
        """
        Cities have sight range 2 even in decline preview mode.
        """
        return 2

    def build_unit(self, game_state: 'GameState', unit: UnitTemplate, give_up_if_still_impossible: bool = False, stack_size=1, bonus_strength: int = 0, override_civ: Civ | None = None) -> Unit | None:
        bonus_strength = self._spawn_strength(unit, game_state) + bonus_strength
        civ = override_civ or self.civ

        spawn_hex = self.hex
        for _ in self.passive_building_abilities_of_name('Deployment Center'):
            if civ.targets:
                visible_hexes = [h for h in game_state.hexes.values() if h.visible_to_civ(civ)]
                spawn_hex = min(visible_hexes, key=lambda h: civ.get_target_from_hex(self.hex).distance_to(h))  # type: ignore

        if not spawn_hex.is_occupied(civ, allow_enemy_city=False):
            return civ.spawn_unit_on_hex(game_state, unit, spawn_hex, bonus_strength, stack_size=stack_size)
        if spawn_hex == self.hex and unit.has_tag(UnitTag.DEFENSIVE) and len(spawn_hex.units) > 0 and spawn_hex.units[0].civ == civ and spawn_hex.units[0].template == unit and spawn_hex.units[0].strength == unit.strength + bonus_strength:
            # Defensive units build in city center no matter what.
            self.reinforce_unit(spawn_hex.units[0], stack_size=stack_size)
            return spawn_hex.units[0]

        free_neighbors = [h for h in spawn_hex.get_neighbors(game_state.hexes, exclude_ocean=True) if not h.is_occupied(civ, allow_enemy_city=False)]
        if unit.has_tag(UnitTag.DEFENSIVE) and len(spawn_hex.units) > 0 and spawn_hex.units[0].civ != civ:
            # Never build two stacks of immobile units next to each other.
            free_neighbors = [h for h in free_neighbors if not any(u.template.has_tag(UnitTag.DEFENSIVE) for n in h.get_neighbors(game_state.hexes, include_self=False) for u in n.units)]
        if len(free_neighbors) > 0:
            best_hex = min(free_neighbors, key=lambda h: (h.distance_to_list(self.get_closest_targets() or [spawn_hex]), random.random()))
            if spawn_hex == self.hex and unit.has_tag(UnitTag.DEFENSIVE) and len(spawn_hex.units) > 0 and spawn_hex.units[0].civ == civ:
                # Kick out the unit that's there to build defensive units.
                spawn_hex.units[0].take_one_step_to_hex(best_hex, game_state)
                return civ.spawn_unit_on_hex(game_state, unit, spawn_hex, bonus_strength, stack_size=stack_size)
            else:
                return civ.spawn_unit_on_hex(game_state, unit, best_hex, bonus_strength, stack_size=stack_size)

        potential_units_to_reinforce = [u for hex in spawn_hex.get_neighbors(game_state.hexes, include_self=True) for u in hex.units if u.civ == civ and u.template == unit and u.strength == unit.strength + bonus_strength]  

        if len(potential_units_to_reinforce) > 0:
            best_unit_to_reinforce = min(potential_units_to_reinforce, key=lambda u: (
                            u.health, 
                            u.hex.distance_to_list(self.get_closest_targets() or [spawn_hex]),
                            random.random()
                            ))       
            self.reinforce_unit(best_unit_to_reinforce, stack_size=stack_size)
            return best_unit_to_reinforce
        
        if give_up_if_still_impossible:
            return None
        num_merges = 0

        # Try merging friendly units
        for hex in spawn_hex.get_neighbors(game_state.hexes, include_self=True):
            if hex.units and hex.units[0].civ.id == civ.id:
                if hex.units[0].merge_into_neighboring_unit(None, game_state, always_merge_if_possible=True):
                    num_merges += 1
            if num_merges >= 2:
                break

        # If that doesn't work, try merging enemy units, so long as they aren't on the city itself
        if num_merges == 0:
            for hex in spawn_hex.get_neighbors(game_state.hexes, include_self=True):
                if hex.units and not hex.city:
                    if hex.units[0].merge_into_neighboring_unit(None, game_state, always_merge_if_possible=True):
                        num_merges += 1
                        break
                if num_merges >= 2:
                    break

        # If that doesn't work, and we have a lot of metal to spend, try removing friendly units altogether
        if num_merges == 0 and self.metal > 75:
            for hex in spawn_hex.get_neighbors(game_state.hexes, include_self=True):
                if hex.units and hex.units[0].civ.id == civ.id and hex.units[0].health < 300:
                    hex.units[0].remove_from_game(game_state)
                    break

        return self.build_unit(game_state, unit, give_up_if_still_impossible=True, stack_size=stack_size, bonus_strength=bonus_strength, override_civ=override_civ)

    def _spawn_strength(self, unit_template: UnitTemplate, game_state: 'GameState') -> int:
        result = 0
        if self.civ.has_ability('IncreasedStrengthForUnit'):
            unit_name, strength_increase = self.civ.numbers_of_ability('IncreasedStrengthForUnit')
            if unit_name == unit_template.name:
                result += strength_increase

        if self.civ.has_ability('IncreasedStrengthForNthUnit'):
            n, unit_type, bonus = self.civ.numbers_of_ability('IncreasedStrengthForNthUnit')
            if unit_type == unit_template.name:
                self.civ.unique_units_built += 1
                if self.civ.unique_units_built == n:
                    result += bonus

        for ability, _ in self.civ.passive_building_abilities_of_name('NewUnitsGainBonusStrength', game_state):
            result += ability.numbers[0]

        for ability, _ in self.passive_building_abilities_of_name('UnitsExtraStrengthByTag'):
            if unit_template.has_tag(ability.numbers[0]):
                result += ability.numbers[1]
        for ability, _ in self.passive_building_abilities_of_name('UnitsExtraStrengthByAge'):
            if unit_template.advancement_level >= ability.numbers[0]:
                result += ability.numbers[1]
        return result

    def reinforce_unit(self, unit: Unit, stack_size=1) -> None:
        unit.health += 100 * stack_size

    def validate_building_queueable(self, building_template: UnitTemplate | BuildingTemplate | WonderTemplate) -> bool:
        if self.has_building(building_template):
            return False
        if isinstance(building_template, UnitTemplate):
            if building_template not in self.available_unit_buildings:
                return False
        if isinstance(building_template, BuildingTemplate):
            if building_template not in self.available_city_buildings:
                return False
            if building_template.type == BuildingType.URBAN and self.empty_slots(BuildingType.URBAN, include_in_queue=True) <= 0:
                return False
            if building_template.type == BuildingType.RURAL and self.empty_slots(BuildingType.RURAL, include_in_queue=True) <= 0:
                return False
        if isinstance(building_template, WonderTemplate):
            if building_template not in self.available_wonders:
                return False
        return True

    def build_buildings(self, game_state: 'GameState') -> None:
        while self.buildings_queue:
            entry = self.buildings_queue[0]
            building: UnitTemplate | BuildingTemplate | WonderTemplate = entry.template
            cost = entry.get_cost(game_state)
            if self.wood >= cost:
                self.buildings_queue.pop(0)
                self.build_building(game_state, building)
                self.wood -= cost
            else:
                break

    def buildings_of_type(self, type: BuildingType) -> list[Building]:
        return [b for b in self.buildings if b.type == type]

    def num_buildings_of_type(self, type: BuildingType, include_in_queue=False):
        def type_from_template(t: WonderTemplate | UnitTemplate | BuildingTemplate) -> BuildingType | None:
            if isinstance(t, WonderTemplate): return None
            if isinstance(t, UnitTemplate): return BuildingType.UNIT
            if isinstance(t, BuildingTemplate): return t.type
        if type == BuildingType.UNIT:
            bldgs = len(self.unit_buildings)
        else:
            bldgs = len(self.buildings_of_type(type))
        if include_in_queue:
            bldgs += len([b for b in self.buildings_queue if type_from_template(b.template) == type])
        return bldgs

    def empty_slots(self, type: BuildingType, include_in_queue=False) -> int:
        if type == BuildingType.RURAL:
            total_slots = self.rural_slots
        elif type == BuildingType.URBAN:
            total_slots = self.urban_slots
        elif type == BuildingType.UNIT:
            total_slots = self.military_slots
        else:
            raise ValueError(f"Unknown building type: {type}")
        return total_slots - self.num_buildings_of_type(type, include_in_queue=include_in_queue)

    def develop_cost(self, type: BuildingType):
        result = DEVELOP_COST[type.value] * 2 ** self.develops_this_civ[type]
        if (self.civ.has_ability("DevelopCheap") and self.civ.numbers_of_ability("DevelopCheap")[0] == type.value) and self.develops_this_civ[type] == 0:
            result /= 2
        return result

    def show_develop_button(self, type: BuildingType) -> bool:
        if not self.is_territory_capital:
            return False
        if self.civ.game_player is None:
            return False
        return True

    def cant_develop_reason(self, type: BuildingType) -> str | None:
        if not self.show_develop_button(type):
            return "Can't develop here."
        if self.revolting_to_rebels_this_turn:
            return "City revolting this turn."
        if type == BuildingType.RURAL and self.military_slots + self.urban_slots + self.rural_slots >= MAX_SLOTS:
            return f"Max slots ({MAX_SLOTS})"
        if type == BuildingType.URBAN and self.urban_slots >= MAX_SLOTS_OF_TYPE['urban']:
            return f"Max urban slots ({MAX_SLOTS_OF_TYPE['urban']})"
        if type == BuildingType.UNIT and self.military_slots >= MAX_SLOTS_OF_TYPE['unit']:
            return f"Max military slots ({MAX_SLOTS_OF_TYPE['unit']})"
        if type in [BuildingType.URBAN, BuildingType.UNIT] and self.num_buildings_of_type(BuildingType.RURAL, include_in_queue=True) == self.rural_slots:
            return "No rural slots available"
        if self.civ.city_power < self.develop_cost(type):
            return f"City power ({int(self.civ.city_power)} / {self.develop_cost(type)})"
        return None
    
    def can_develop(self, type: BuildingType) -> bool:
        return self.cant_develop_reason(type) is None
    
    def develop(self, type: BuildingType, game_state, free=False):
        if STRICT_MODE:
            assert free or self.can_develop(type)
        if type == BuildingType.URBAN:
            self.rural_slots -= 1
            self.urban_slots += 1
        if type == BuildingType.UNIT:
            self.rural_slots -= 1
            self.military_slots += 1
        if type == BuildingType.RURAL:
            self.rural_slots += 1
        if not free:
            self.civ.city_power -= self.develop_cost(type)
            self.develops_this_civ[type] += 1
        self.civ.gain_vps(DEVELOP_VPS, score_strings.DEVELOPMENT)  
        if self.civ.has_tenet(TENETS.COMMUNITY):
            self.civ.gain_vps(DEVELOP_VPS, "Community")
        if self.civ.has_ability("OnDevelop"):
            civ_type, effect = self.civ.numbers_of_ability("OnDevelop")
            if civ_type == type:
                effect.apply(self, game_state)

    def expand(self, game_state):
        self.develop(BuildingType.RURAL, game_state)

    def urbanize(self, game_state):
        self.develop(BuildingType.URBAN, game_state)

    def militarize(self, game_state):
        self.develop(BuildingType.UNIT, game_state)

    def unit_buildings_ranked_for_bulldoze(self, exclude: list[UnitBuilding] = []) -> list[UnitBuilding]:
        targets = [b for b in self.unit_buildings if b not in exclude]
        targets.sort(key=lambda b: (-b.template.has_tag(UnitTag.DEFENSIVE), b.template.advancement_level))
        return targets

    def building_in_queue(self, template) -> bool:
        return any(b.template == template for b in self.buildings_queue)

    def enqueue_build(self, template: Union[BuildingTemplate, UnitTemplate, WonderTemplate]) -> None:
        logger.info(f"enqueuing {template}")
        if STRICT_MODE:
            assert self.is_territory_capital, f"{self.name} tried to enqueue a building while a puppet"
            assert not self.has_building(template), (template, self.buildings_queue, self.building_in_queue(template))
        order = QueueEntry(template)
        self.buildings_queue.append(order)

    def build_building(self, game_state: 'GameState', building: Union[BuildingTemplate, UnitTemplate, WonderTemplate], free: bool = False) -> None:
        if isinstance(building, UnitTemplate):
            new_building = UnitBuilding(building)
            self.unit_buildings.append(new_building)
            if len(self.unit_buildings) > self.military_slots:
                bulldoze: UnitBuilding = self.unit_buildings_ranked_for_bulldoze(exclude=[new_building])[0]
                self.unit_buildings = [b for b in self.unit_buildings if b != bulldoze]
                self.metal += bulldoze.metal
            self.clear_unit_builds()
            self._refresh_available_buildings_and_units(game_state)
            self.toggle_unit_build(building)
        
        else:
            new_building = Building(building)
            self.buildings.append(new_building)

            for effect in new_building.on_build:
                effect.apply(self, game_state)

            if isinstance(building, WonderTemplate):
                game_state.handle_wonder_built(self, building)

        if new_building.one_per_civ_key and not free:
            if self.civ.id not in game_state.one_per_civs_built_by_civ_id:
                game_state.one_per_civs_built_by_civ_id[self.civ.id] = {new_building.one_per_civ_key: self.id}
            else:
                game_state.one_per_civs_built_by_civ_id[self.civ.id][new_building.one_per_civ_key] = self.id

            # Clear it from any other cities immediately; you can't build two in one turn.
            for city in self.civ.get_my_cities(game_state):
                city.buildings_queue = [b for b in city.buildings_queue if b.template != building]
    
    def passive_building_abilities_of_name(self, ability_name: str) -> Generator[tuple['Ability', 'Building'], None, None]:
        for building in self.buildings:
            for ability in building.passive_building_abilities_of_name(ability_name):
                yield ability, building

    def change_owner(self, civ: Civ, game_state: 'GameState') -> None:
        """
        Called when an existing city changes owner; called by capture() and process_decline_option().
        """
        old_civ = self.civ
        self.last_owner_civ_id = old_civ.id

        # Remove trade hub
        if self.is_trade_hub():
            old_civ.trade_hub_id = None

        for building in self.buildings:
            if building.one_per_civ_key and game_state.one_per_civs_built_by_civ_id.get(old_civ.id, {}).get(building.building_name) == self.id:
                del game_state.one_per_civs_built_by_civ_id[old_civ.id][building.building_name]
        self.buildings = [b for b in self.buildings if not b.destroy_on_owner_change]
        self.unit_buildings = []

        # Change the civ
        self.update_civ(civ)
        for building in self.buildings:
            building.update_ruined_status(city=self, game_state=game_state)

        # If they have a great person, reset the choices to make sure they are all valid
        if old_civ._great_people_choices_city_id == self.id:
            logger.info(f"Resetting great people choices for {old_civ.moniker()}")
            age = old_civ.great_people_choices[0].advancement_level
            old_civ.great_people_choices = []
            old_civ.get_great_person(age=age, city=self, game_state=game_state)

        # Fix territory parent lines
        self.orphan_territory_children(game_state)

        # Reset various properties
        self.under_siege_by_civ = None
        self.buildings_queue = []
        self.clear_unit_builds()
        self.ever_controlled_by_civ_ids[civ.id] = True
        self.develops_this_civ = {d: 0 for d in BuildingType}

        self.unhappiness = 0
        self.food_demand_reduction_recent_owner_change = FOOD_DEMAND_REDUCTION_RECENT_OWNER_CHANGE
        self.wood = 0
        self.metal = 0
        for bldg in self.unit_buildings:
            bldg.metal = 0
        self.set_territory_parent_if_needed(game_state, adopt_focus=True)

        # Update available stuff
        self.civ.update_vitality_decay_rate(game_state)
        self.midturn_update(game_state)

    def barbarian_capture(self, game_state: 'GameState') -> None:
        """Barbarians replace the city with a camp."""

        old_civ = self.civ

        if len(self.available_units) > 0:
            best_unit: UnitTemplate = max(self.available_units, key=lambda x: (x.advancement_level, random.random()))
        else:
            best_unit = random.choice([u for u in UNITS.all() if not u.has_tag(UnitTag.WONDROUS) and u.advancement_level == max(0, game_state.advancement_level - 1)])

        # Also build a handful of units out of the ruins of the city
        for u in self.available_units:
            self.build_unit(game_state, u, override_civ=game_state.barbarians)

        # Call change_owner to do the cleanup on the previous civ ownership
        self.change_owner(game_state.barbarians, game_state)

        logger.info(f"****Barbarians Raze {self.name}****")
        # Any great people choices in this city are now invalid
        for level, city_id in old_civ._great_people_choices_queue.copy():
            if city_id == self.id:
                old_civ._great_people_choices_queue.remove((level, city_id))
        if old_civ._great_people_choices_city_id == self.id:
            old_civ._great_people_choices_city_id = None
            old_civ.great_people_choices = []

        assert self.hex.city is not None

        self.hex.city = None
        game_state.register_camp(Camp(game_state.barbarians, unit=best_unit, hex=self.hex, turn_spawned=game_state.turn_num))
        for player in game_state.game_player_by_player_num.values():
            player.fog_camp_coords_with_turn[self.hex.coords] = game_state.turn_num
            if self.hex.coords in player.fog_cities:
                del player.fog_cities[self.hex.coords]

        if self.is_trade_hub():
            self.civ.trade_hub_id = None
        del game_state.cities_by_id[self.id]

    def capture(self, sess, civ: Civ, game_state: 'GameState') -> None:
        if civ == game_state.barbarians:
            self.barbarian_capture(game_state)
            return

        logger.info(f"****Captured {self.name}****")
        self.capital = False

        if civ.id not in self.ever_controlled_by_civ_ids:
            civ.gain_vps(CITY_CAPTURE_REWARD, "City Capture (5/city)")

            if civ.has_ability('ExtraVpsPerCityCaptured'):
                civ.gain_vps(civ.numbers_of_ability('ExtraVpsPerCityCaptured')[0], civ.template.name)

            for ability, building in civ.passive_building_abilities_of_name("ExtraVpsForCityCapture", game_state):
                amount = ability.numbers[0]
                civ.gain_vps(amount, building.building_name)

        self.change_owner(civ, game_state)

        game_state.add_animation_frame(sess, {
            "type": "CityCapture",
            "civ": civ.template.name,
            "city": self.name,
            "vpReward": CITY_CAPTURE_REWARD,
        }, hexes_must_be_visible=[self.hex])

    def capitalize(self, game_state: 'GameState') -> None:
        civ = self.civ
        self.capital = True

        for game_player in game_state.game_player_by_player_num.values():
            if self.hex.coords in game_player.fog_cities:
                game_player.fog_cities[self.hex.coords]["capital"] = True
                
        if civ.has_ability('StartWithResources'):
            if civ.numbers_of_ability('StartWithResources')[0] == 'food':
                self.food += civ.numbers_of_ability('StartWithResources')[1]
                self.civ.city_power += civ.numbers_of_ability('StartWithResources')[1]

            elif civ.numbers_of_ability('StartWithResources')[0] == 'metal':
                self.metal += civ.numbers_of_ability('StartWithResources')[1]

            elif civ.numbers_of_ability('StartWithResources')[0] == 'wood':
                self.wood += civ.numbers_of_ability('StartWithResources')[1]
            
            elif civ.numbers_of_ability('StartWithResources')[0] == 'science':
                self.civ.science += civ.numbers_of_ability('StartWithResources')[1]
            
            else:
                raise ValueError(f"Invalid resource type for StartWithResources: {civ.numbers_of_ability('StartWithResources')[0]}")

    def bot_pick_wonder(self, choices: list[WonderTemplate], game_state: 'GameState') -> Optional[WonderTemplate]:
        affordable_ages: set[int] = {age for age in game_state.wonders_by_age.keys() if BASE_WONDER_COST[age] <= self.projected_total_wood}
        if affordable_ages == set():
            return None
        points_by_age = {age: game_state.wonder_vp_chunks(age) for age in affordable_ages}
        most_points = max(points_by_age.values())
        best_ages = [age for age in affordable_ages if points_by_age[age] == most_points]
        affordable_choices: list[WonderTemplate] = [choice for choice in choices if choice.advancement_level in best_ages]
        if len(affordable_choices) == 0:
            return None
        # Build the highest age one we can afford
        return max(affordable_choices, key=lambda x: (x.advancement_level, random.random()))

    def bot_evaluate_yields(self, yields: Yields, game_state: 'GameState') -> float:
        projected_unhappiness = self.projected_income.unhappiness + self.unhappiness + yields.unhappiness
        if projected_unhappiness >= game_state.unhappiness_threshold:
            unhappiness_value = -2.0
        elif game_state.unhappiness_threshold - projected_unhappiness > 25:
            unhappiness_value = -0.7
        else:
            unhappiness_value = -1.5

        AI_VALUE = {
            "food_for_growth": 0.4,
            "science": 1,
            "wood": 1.25,
            "metal": 1,
            "city_power": 0.4,
            "unhappiness": unhappiness_value,
        }
        y = yields.to_json()
        food = y.pop('food')
        y['food_for_growth'] = food
        y['unhappiness'] -= min(self.projected_income.unhappiness, food)
        y['city_power'] += food - y['unhappiness']
        return sum([AI_VALUE[k] * v for k, v in y.items()])

    def bot_pick_economic_building(self, choices: list[BuildingTemplate], remaining_wood: float, game_state: 'GameState') -> Optional[BuildingTemplate]:
        if self.empty_slots(BuildingType.RURAL, include_in_queue=True) <= 0:
            choices = [b for b in choices if b.type != BuildingType.RURAL]
        if self.empty_slots(BuildingType.URBAN, include_in_queue=True) <= 0:
            choices = [b for b in choices if b.type != BuildingType.URBAN]

        # Don't build libraries
        if self.civ.get_advancement_level() > 2:
            choices = [b for b in choices if b != BUILDINGS.LIBRARY]
        # Don't build husbandry centers by themself
        if self.focus != "food" and self.urban_slots < 2:
            choices = [b for b in choices if b != BUILDINGS.HUSBANDRY_CENTER]
        # Only one of these per city
        if any([len(building.passive_building_abilities_of_name("IncreaseFocusYieldsPerPopulation")) > 0 for building in self.buildings]):
            choices = [b for b in choices if not any (a.name == "IncreaseFocusYieldsPerPopulation" for a in b.abilities)]
        if len(choices) > 0:
            ACCEPTABLE_PAYOFF_TURNS = 6
            payoff_turns: dict[BuildingTemplate, float] = {}
            for building in choices:
                desc = self.building_descriptions[building.name]
                total_yesvitality_yields = desc.building_yields + desc.pseudoyields_for_ai_yesvitality
                total_nonvitality_yields = desc.non_vitality_yields + desc.pseudoyields_for_ai_nonvitality + desc.instant_yields * 0.25
                if building.type == BuildingType.URBAN:
                    total_yesvitality_yields.science -= 2
                if building.type == BuildingType.RURAL:
                    total_yesvitality_yields.food -= 1
                total_yesvitality_value = self.bot_evaluate_yields(total_yesvitality_yields, game_state)
                total_nonvitality_value = self.bot_evaluate_yields(total_nonvitality_yields, game_state)
                if total_yesvitality_value + total_nonvitality_value > 0:
                    payoff_turns[building] = self.calculate_payoff_time(yields=total_yesvitality_value, vitality_exempt_yields=total_nonvitality_value, cost=building.cost)
                    turns_to_build = max(0, (building.cost - remaining_wood) / max(self.projected_income.wood, 0.01))
                    payoff_turns[building] += turns_to_build * 1.5  # Count extra to discount future yields compared to present.
            if len(payoff_turns) > 0:
                # calulcate the argmin of the payoff turns
                best_building = min(payoff_turns, key=lambda x: (payoff_turns.get(x, 99), -x.cost, x.name))
                if payoff_turns[best_building] < ACCEPTABLE_PAYOFF_TURNS:
                    return best_building

        return None

    def is_threatened_city(self, game_state: 'GameState') -> bool:
        return self.hex.is_threatened(game_state, self.civ)

    def bot_single_move(self, game_state: 'GameState', move_type: MoveType, move_data: dict, abbreviated_midturn_update: bool = False) -> None:
        """
        abbreviated_midturn_update: if True, the midturn update will be abbreviated to only update this city. Use for speeding up AI moves.
        """
        move_data['city_id'] = self.id
        game_state.resolve_move(move_type, move_data, civ=self.civ, do_midturn_update=not abbreviated_midturn_update)
        if abbreviated_midturn_update:
            parent = self.get_territory_parent(game_state) or self
            parent.midturn_update(game_state)
        

    def _bot_effective_advancement_level(self, unit: UnitTemplate, slingers_better_than_warriors=False) -> float:
        # treat my civ's unique unit as +1 adv level.
        if self.civ.unique_unit is not None:
            if unit.name == self.civ.unique_unit.name:
                return unit.advancement_level + 1
        if unit == UNITS.SLINGER and slingers_better_than_warriors:
            return 0.5
        return unit.advancement_level

    def bot_move(self, game_state: 'GameState') -> None:
        logger.info(f"{self.name} -- City planning AI move.")

        if self.civ.has_ability('OnDevelop'):
            favorite_development = self.civ.numbers_of_ability('OnDevelop')[0]
        elif self.civ.has_ability('DevelopCheap'):
            favorite_development = self.civ.numbers_of_ability('DevelopCheap')[0]
        else:
            favorite_development = None

        if self.can_develop(BuildingType.URBAN) \
            and (random.random() < AI.CHANCE_URBANIZE or favorite_development == "urban") \
            and self.empty_slots(BuildingType.URBAN, include_in_queue=True) <= 1:
            self.bot_single_move(game_state, MoveType.DEVELOP, {'type': 'urban'}, abbreviated_midturn_update=True)
        if self.can_develop(BuildingType.UNIT) \
            and (random.random() < AI.CHANCE_MILITARIZE or favorite_development == "unit") \
            and self.empty_slots(BuildingType.UNIT, include_in_queue=True) <= 0:
            self.bot_single_move(game_state, MoveType.DEVELOP, {'type': 'unit'}, abbreviated_midturn_update=True)
        if self.can_develop(BuildingType.RURAL) \
            and self.empty_slots(BuildingType.RURAL, include_in_queue=True) <= 1 \
            and (random.random() < AI.CHANCE_EXPAND or favorite_development == "rural"):
            self.bot_single_move(game_state, MoveType.DEVELOP, {'type': 'rural'}, abbreviated_midturn_update=True)

        self.clear_unit_builds()
        available_units = [unit for unit in self.available_units if unit.movement > 0 or self.is_threatened_city(game_state)]
        if len(available_units) > 0:
            highest_level = max([self._bot_effective_advancement_level(unit, slingers_better_than_warriors=True) for unit in available_units])
            if highest_level < self.civ.get_advancement_level() - 2 and not self.is_threatened_city(game_state):
                logger.info(f"  not building units because the best I can built is level {highest_level} units and I'm at tech level {self.civ.get_advancement_level()}")
                build_units = []
            elif highest_level < self.civ.get_advancement_level() - 4:
                logger.info(f"  not building units even though threatened, because the best I can built is level {highest_level} units and I'm at tech level {self.civ.get_advancement_level()}")
                build_units = []
            else:
                build_units = [unit for unit in available_units if self._bot_effective_advancement_level(unit, slingers_better_than_warriors=True) >= highest_level - 1]
        else:
            build_units = []
        for u in self.unit_buildings:
            if (u.template in build_units) != u.active:
                self.bot_single_move(game_state, MoveType.SELECT_INFINITE_QUEUE, {'unit_name': u.template.name}, abbreviated_midturn_update=True)
        
        # Clear the queue
        for entry in self.buildings_queue:
            self.bot_single_move(game_state, MoveType.CANCEL_BUILDING, {'building_name': entry.template.name}, abbreviated_midturn_update=False)  # Need full midturn_update to tell other cities they can build it.
        buildings, i_want_wood = self.bot_choose_building_queue(game_state)
        for b in buildings:
            self.bot_single_move(game_state, MoveType.CHOOSE_BUILDING, {'building_name': b.name})
        if not self.is_threatened_city(game_state) and any(isinstance(b.template, UnitTemplate) for b in self.buildings_queue):
            logger.info(f"  not building units to wait for new military building.")
            self.clear_unit_builds()
        self.bot_choose_focus(game_state, parent_wants_wood=i_want_wood)
        for city in self.get_puppets(game_state):
            city.bot_choose_focus(game_state, parent_wants_wood=i_want_wood)

    def bot_choose_building_queue(self, game_state) -> tuple[list[BuildingTemplate], bool]:
        q = []
        # Never steal from another city's queue
        wonders: list[WonderTemplate] = [w for w in self.available_wonders if w.name not in self.civ.buildings_in_all_queues]
        economic_buildings: list[BuildingTemplate] = [b for b in self.available_city_buildings if b.name not in self.civ.buildings_in_all_queues]
        military_buildings: list[UnitTemplate] = [u for u in self.available_unit_buildings if u.movement > 0 and u.name not in self.civ.buildings_in_all_queues]

        lotsa_wood: bool = self.projected_income_base.value.wood > self.projected_income_base.value.metal * 2
        if len(military_buildings) > 0:
            # Choose buildings first by effective advancement level, then randomly
            best_military_building = max(military_buildings, key=lambda building: (
                self._bot_effective_advancement_level(building, slingers_better_than_warriors=lotsa_wood), 
                random.random()
                ))
            best_military_building_age = self._bot_effective_advancement_level(best_military_building, slingers_better_than_warriors=lotsa_wood)
        else:
            best_military_building = None
            best_military_building_age = -1
        
        remaining_wood_budget = self.projected_total_wood
        for item in self.buildings_queue:
            remaining_wood_budget -= item.get_cost(game_state)
            if isinstance(item.template, BuildingTemplate):
                for effect in item.template.on_build:
                    if isinstance(effect, GainResourceEffect) and effect.resource == "wood":
                        remaining_wood_budget += effect.amount
        best_current_available_unit_age = max([self._bot_effective_advancement_level(u, slingers_better_than_warriors=lotsa_wood) for u in self.available_units]) if len(self.available_units) > 0 else -1
        if best_military_building is not None \
                and best_military_building_age > best_current_available_unit_age \
                and remaining_wood_budget > best_military_building.wood_cost:
            q.append(best_military_building)
            remaining_wood_budget -= best_military_building.wood_cost
            logger.info(f"  overwrote building queue because of new military unit (lvl {self._bot_effective_advancement_level(best_military_building, slingers_better_than_warriors=lotsa_wood)}): {q}")
        while len(wonders) > 0 and (wonder_choice := self.bot_pick_wonder(wonders, game_state)) is not None and remaining_wood_budget > (cost := BASE_WONDER_COST[wonder_choice.advancement_level]):
            wonders.remove(wonder_choice)
            remaining_wood_budget -= cost
            q.append(wonder_choice)
            logger.info(f"  adding wonder to buildings queue: {q}")
        while len(economic_buildings) > 0 and (econ_bldg_choice := self.bot_pick_economic_building(economic_buildings, remaining_wood_budget, game_state)) is not None and remaining_wood_budget > 0:
            q.append(econ_bldg_choice)
            economic_buildings.remove(econ_bldg_choice)
            remaining_wood_budget -= econ_bldg_choice.cost
            for effect in econ_bldg_choice.on_build:
                if isinstance(effect, GainResourceEffect) and effect.resource == "wood":
                    remaining_wood_budget += effect.amount
            if econ_bldg_choice.type == BuildingType.URBAN and self.empty_slots(BuildingType.URBAN, include_in_queue=True) <= len([b for b in q if isinstance(b, BuildingTemplate) and b.type == BuildingType.URBAN]):
                economic_buildings = [b for b in economic_buildings if b.type != BuildingType.URBAN]
            if econ_bldg_choice.type == BuildingType.RURAL and self.empty_slots(BuildingType.RURAL, include_in_queue=True) <= len([b for b in q if isinstance(b, BuildingTemplate) and b.type == BuildingType.RURAL]):
                economic_buildings = [b for b in economic_buildings if b.type != BuildingType.RURAL]
            logger.info(f"  adding economic building {econ_bldg_choice.name} to buildings queue: {q}")
        
        i_want_wood = len([b for b in economic_buildings if b.type == BuildingType.URBAN and b.cost > remaining_wood_budget]) > 0
        return q, i_want_wood

    def bot_choose_focus(self, game_state, parent_wants_wood: bool):
        self.bot_single_move(game_state, MoveType.CHOOSE_FOCUS, {'focus': 'wood'}, abbreviated_midturn_update=True)
        if self.civ_to_revolt_into is not None or self.unhappiness + self.projected_income.unhappiness > game_state.unhappiness_threshold:
            choice = 'food'
            logger.info(f"  chose focus: {self.focus} to prevent revolt")
        
        else:
            parent = self.get_territory_parent(game_state)
            production_city: City = self if parent is None else parent

            plausible_focuses = ["food", "wood", "metal", "science"]
            if self.growth_cost() >= 30:
                # At some point it's time to use our pop
                plausible_focuses.remove('food')
            if self.civ.researching_tech is None:
                plausible_focuses.remove('science')
            if production_city.wood >= 150:
                plausible_focuses.remove('wood')
                
            max_yields = max(self.projected_income_focus[focus] for focus in plausible_focuses)
            focuses_with_best_yields = [focus for focus in plausible_focuses if max_yields - self.projected_income_focus[focus] < 2]
            if "food" in focuses_with_best_yields and len(focuses_with_best_yields) > 1:
                focuses_with_best_yields.remove("food")
            if len(production_city.active_unit_buildings) > 0 and 'metal' in focuses_with_best_yields and production_city.is_threatened_city(game_state):
                choice = 'metal'
            elif 'wood' in focuses_with_best_yields and production_city.empty_slots(BuildingType.URBAN, include_in_queue=True) > 0 and parent_wants_wood:
                choice = 'wood'
            else:
                choice = random.choice(focuses_with_best_yields)
            logger.info(f"  chose focus: {choice} (max yield choices were {focuses_with_best_yields})")

        self.bot_single_move(game_state, MoveType.CHOOSE_FOCUS, {'focus': choice}, abbreviated_midturn_update=True)

    def to_json(self, include_civ_details: bool = False) -> dict:
        return {
            **super().to_json(),
            "id": self.id,
            **({"civ": self.civ.to_json()} if include_civ_details else {}),
            "ever_controlled_by_civ_ids": self.ever_controlled_by_civ_ids,
            "name": self.name,
            "population": self.population,
            "food": self.food,
            "metal": self.metal,
            "wood": self.wood,
            "focus": self.focus,
            "rural_slots": self.rural_slots,
            "urban_slots": self.urban_slots,
            "military_slots": self.military_slots,
            "hex": self.hex.coords,
            "icon_unit_name": sorted(self.active_unit_buildings, key=lambda u: u.template.advancement_level, reverse=True)[0].template.name if len(self.active_unit_buildings) > 0 else None,
            "buildings_queue": [building.to_json() for building in self.buildings_queue],
            "buildings": [building.to_json() for building in self.buildings],
            "unit_buildings": [building.to_json() for building in self.unit_buildings],
            "available_buildings_payoff_times": self.available_buildings_payoff_times,
            "building_descriptions": {name: desc.to_json() for name, desc in self.building_descriptions.items()},
            "available_wonders": [w.name for w in self.available_wonders if not self.building_in_queue(w)],
            "available_unit_building_names": [template.name for template in self.available_unit_buildings if not self.building_in_queue(template)],
            "available_urban_building_names": [template.name for template in self.available_city_buildings if not self.building_in_queue(template) and template.type==BuildingType.URBAN],
            "available_rural_building_names": [template.name for template in self.available_city_buildings if not self.building_in_queue(template) and template.type==BuildingType.RURAL],
            "building_slots_full": {
                "rural": self.empty_slots(BuildingType.RURAL, include_in_queue=True) <= 0,
                "urban": self.empty_slots(BuildingType.URBAN, include_in_queue=True) <= 0,
                "military": self.empty_slots(BuildingType.UNIT, include_in_queue=True) <= 0,
            },
            "capital": self.capital,
            "available_units": [u.name for u in self.available_units],
            "projected_income": self.projected_income.to_json(),
            "projected_income_base": self.projected_income_base.to_json(),
            "projected_income_focus": self.projected_income_focus.to_json(),
            "projected_income_puppets": self.projected_income_puppets,
            "projected_income_city_center": self.projected_income_city_center.to_json(),
            "projected_on_decline_leaderboard": self.projected_on_decline_leaderboard,
            "projected_build_queue_depth": self.projected_build_queue_depth,
            "max_units_in_build_queue": self.military_slots <= len([entry for entry in self.buildings_queue if isinstance(entry.template, UnitTemplate)]),
            "growth_cost": self.growth_cost(),
            "terrains_dict": {terrain.name: count for terrain, count in self.terrains_dict.items()},
            "develops_this_civ": {d.value: self.develops_this_civ[d] for d in BuildingType},
            "develop_costs": {d.value: self.develop_cost(d) for d in BuildingType},
            "show_develop_buttons": {d.value: self.show_develop_button(d) for d in BuildingType},
            "cant_develop_reason": {d.value: self.cant_develop_reason(d) for d in BuildingType},

            "territory_parent_id": self._territory_parent_id,
            "territory_parent_coords": self._territory_parent_coords,

            "revolting_starting_vitality": self.revolting_starting_vitality,
            "unhappiness": self.unhappiness,
            "civ_to_revolt_into": self.civ_to_revolt_into.name if self.civ_to_revolt_into else None,
            "is_decline_view_option": self.is_decline_view_option,
            "food_demand": self.food_demand.to_json(),
            "food_demand_reduction_recent_owner_change": self.food_demand_reduction_recent_owner_change,
            "revolt_unit_count": self.revolt_unit_count,
            "founded_turn": self.founded_turn,
            "revolting_to_rebels_this_turn": self.revolting_to_rebels_this_turn,

            "is_trade_hub": self.is_trade_hub(),
            "bot_favorite_builds": [b.name for b in self.bot_favorite_builds],
            "region": self.region.value,
            "last_owner_civ_id": self.last_owner_civ_id,
        }

    @staticmethod
    def from_json(json: dict) -> "City":
        city = City(
            civ=Civ.from_json(json['civ']) if 'civ' in json else None,
            name=json["name"],
            region=Region(json["region"]),
        )
        super(City, city).from_json(json)
        city.id = json["id"]
        city.ever_controlled_by_civ_ids = json["ever_controlled_by_civ_ids"].copy()
        city.population = json["population"]
        city.buildings = [Building.from_json(building) for building in json["buildings"]]
        city.unit_buildings = [UnitBuilding.from_json(building) for building in json["unit_buildings"]]
        city.food = json["food"]
        city.metal = json["metal"]
        city.wood = json["wood"]
        city.rural_slots = json["rural_slots"]
        city.urban_slots = json["urban_slots"]
        city.military_slots = json["military_slots"]
        city.capital = json["capital"]
        city.buildings_queue = [QueueEntry.from_json(entry) for entry in json["buildings_queue"]]
        city.building_descriptions = {name: BuildingDescription.from_json(desc) for name, desc in json["building_descriptions"].items()}
        city.available_buildings_payoff_times = json["available_buildings_payoff_times"]
        city.available_units = [UNITS.by_name(unit) for unit in json["available_units"]]
        city.focus = json["focus"]
        city.projected_income = Yields(**json["projected_income"])
        city.projected_income_base = DetailedYields.from_json(json["projected_income_base"])
        city.projected_income_focus = Yields(**json["projected_income_focus"])
        city.projected_income_city_center = Yields(**json["projected_income_city_center"])
        city.projected_on_decline_leaderboard = json["projected_on_decline_leaderboard"]
        city.projected_build_queue_depth = json["projected_build_queue_depth"]
        city.terrains_dict = {TERRAINS.by_name(terrain): count for terrain, count in json["terrains_dict"].items()}
        city.develops_this_civ = {BuildingType(k): v for k, v in json["develops_this_civ"].items()}
        city.civ_to_revolt_into = CIVS.by_name(json["civ_to_revolt_into"]) if json["civ_to_revolt_into"] else None
        city.revolting_starting_vitality = json["revolting_starting_vitality"]
        city.unhappiness = json["unhappiness"]
        city.is_decline_view_option = json["is_decline_view_option"]
        city.revolt_unit_count = json["revolt_unit_count"]
        city._territory_parent_id = json["territory_parent_id"]
        city._territory_parent_coords = json["territory_parent_coords"]
        city.founded_turn = json["founded_turn"]
        city.food_demand = DetailedNumber.from_json(json["food_demand"])
        city.food_demand_reduction_recent_owner_change = json["food_demand_reduction_recent_owner_change"]
        city.last_owner_civ_id = json["last_owner_civ_id"]

        return city

CITY_NAMES = {
    "Miami",
    "Lothlorien",
    "Leningrad",
    "Los Angeles",
    "Tikal",
    "Karakorum",
    "Khartoum",
    "Ravnica",
    "Tokyo",
    "Delhi",
    "Berkeley",
    "Munich",
    "Qarth",
    "Cuzco",
    "Meereen",
    "New Capenna",
    "The Hive",
    "Nairobi",
    "Barcelona",
    "Toronto",
    "Coruscant",
    "Zigatvar",
    "Wuhan",
    "Cape Town",
    "Tel Aviv",
    "Sunspear",
    "Moscow",
    "Osgiliath",
    "Oldtown",
    "Bern",
    "Lannisport",
    "Nineveh",
    "Atlanta",
    "Tehran",
    "Aleppo",
    "Pune",
    "Oslo",
    "Tijuana",
    "Palenque",
    "Myr",
    "Santiago",
    "Uskdarler",
    "Mos Eisley",
    "Caemlyn",
    "Riga",
    "Nimrud",
    "White Harbor",
    "Dublin",
    "Theed",
    "Venice",
    "Tar Valon",
    "Calgary",
    "Kaposvar",
    "Lagos",
    "Pyongyang",
    "Sarvahr",
    "Marseilles",
    "Ankara",
    "Montreal",
    "Noah's Rainbow",
    "Arrakeen",
    "Chichen Itza",
    "Nassau",
    "Hong Kong",
    "Baikonur",
    "Bunker 118",
    "Braavos",
    "Dardogar",
    "New Jericho",
    "Jimboomba",
    "Winterfell",
    "Chongqing",
    "Tenochtitlan",
    "Jakarta",
    "Temesvar",
    "Kistel",
    "Cairo",
    "Addis Ababa",
    "Riyadh",
    "Kinshasa",
    "Almaty",
    "Merv",
    "Boston",
    "Wakanda",
    "Carthag",
    "Zirc",
    "Caracas",
    "Havana",
    "Ingulath",
    "New York",
    "Budapest",
    "Buenos Aires",
    "Bogota",
    "Lima",
    "Sao Paulo",
    "Mexico City",
    "Bangkok",
    "Manila",
    "Kuala Lumpur",
    "Singapore",
    "Hanoi",
    "Luanda",
    "Mombasa",
    "Kigali",
    "Sydney",
    "Shanghai",
    "Beijing",
}


def generate_random_city_name(already_taken_names: set[str]) -> str:
    names = CITY_NAMES - already_taken_names
    return random.choice(list(names))

def get_city_name_for_civ(civ: Civ, game_state: 'GameState') -> str:
    already_taken_names = set(city.name for city in list(game_state.cities_by_id.values()) + list(game_state.fresh_cities_for_decline.values()))
    city_names = CITY_NAMES_BY_CIV[civ.template.name]

    for city_name in city_names:
        if city_name not in already_taken_names:
            return city_name

    return generate_random_city_name(already_taken_names)