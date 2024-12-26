import math
import os

# Do we crash judiciously on any inconsistency? (Good for debugging, bad for prod.)
STRICT_MODE = False

CITY_CAPTURE_REWARD = 5
UNIT_KILL_REWARD = 1
CAMP_CLEAR_VP_REWARD = 5
CAMP_CLEAR_CITY_POWER_REWARD = 50
CAMPS_PER_TURN_PER_HEX = 0.01

DAMAGE_EQUAL_STR = 40
# Str ratio of 2 does 100 damage
DAMAGE_DOUBLE_EXPONENT = math.log(math.log(100, DAMAGE_EQUAL_STR), 2)

BASE_FOOD_COST_OF_POP = 4
ADDITIONAL_PER_POP_FOOD_COST = 2

VITALITY_DECAY_RATE = 0.08

MAP_HOMOGENEITY_LEVEL = 0.8
PER_PLAYER_AREA_MIN = 25
PER_PLAYER_AREA_MAX = 32

NUM_STARTING_LOCATION_OPTIONS = 3
MAX_PLAYERS = 8

STARTING_CIV_VITALITY = 1.2
REVOLT_VITALITY_PER_TURN = 0.00
REVOLT_VITALITY_PER_UNHAPPINESS = 0.01
FRESH_CITY_VITALITY_PER_TURN = 0.02

FOOD_DEMAND_REDUCTION_RECENT_OWNER_CHANGE = 30
FOOD_DEMAND_REDUCTION_RECENT_OWNER_CHANGE_DECAY = 10
MIN_UNHAPPINESS_THRESHOLD = 5.0

GOOD_HEX_PROBABILITY = 0.2

TECH_VP_REWARD = 2
AGE_THRESHOLDS = {
    0: 0,
    1: 1,
    2: 3,
    3: 7,
    4: 13,
    5: 21,
    6: 31,
    7: 43,
    8: 57,
    9: 73,
    10: 91,
    11: 9999,
}

GAME_END_SCORE = 300
EXTRA_GAME_END_SCORE_PER_PLAYER = 100

DATABASE_URL = "postgresql://cl:cl@localhost:5432/cl"

LOCAL = False
GOD_MODE = False

BASE_CITY_POWER_INCOME = 10.0

BASE_SURVIVAL_BONUS = 8
SURVIVAL_BONUS_PER_AGE = 4

WONDER_VPS = 5
BASE_WONDER_COST = {
    0: 30,
    1: 60,
    2: 90,
    3: 140,
    4: 200,
    5: 250,
    6: 300,
    7: 400,
    8: 600,
    9: 1000,
}

WONDER_COUNT_FOR_PLAYER_NUM = {
    1: 2,
    2: 2,
    3: 2,
    4: 3,
    5: 4,
    6: 4,
    7: 5,
    8: 6,
}

UNIT_BUILDING_BONUSES = {
    1: [1.0],
    2: [0.9, 0.6],
    3: [0.8, 0.6, 0.6],
    4: [0.7, 0.6, 0.6, 0.6],
}

MAX_SLOTS = 8
DEVELOP_COST = {'rural': 50, 'urban': 100, 'unit': 100}
MAX_SLOTS_OF_TYPE = {'urban': 4, 'unit': 4}
DEVELOP_VPS = 2

class AI():
    """
    Settings for the AI
    """
    CHANCE_MOVE_FLAG = 0.2

    CHANCE_URBANIZE = 0.5
    CHANCE_MILITARIZE=0.1
    CHANCE_EXPAND=1.0

    RURAL_SLOT_VALUE = 3
    URBAN_SLOT_VALUE = lambda pop: max(4, pop/2)

    DECLINE_YIELD_RATIO_THRESHOLD = 1.5


if os.path.exists('local_settings.py'):
    from local_settings import *