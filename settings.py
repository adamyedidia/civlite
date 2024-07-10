import os

# Do we crash judiciously on any inconsistency? (Good for debugging, bad for prod.)
STRICT_MODE = False

CITY_CAPTURE_REWARD = 5
UNIT_KILL_REWARD = 1
CAMP_CLEAR_VP_REWARD = 5
CAMP_CLEAR_CITY_POWER_REWARD = 20

BASE_FOOD_COST_OF_POP = 6
ADDITIONAL_PER_POP_FOOD_COST = 2

VITALITY_DECAY_RATE = 0.92

MAP_HOMOGENEITY_LEVEL = 1.0

NUM_STARTING_LOCATION_OPTIONS = 3

PER_PLAYER_AREA = 30
STARTING_CIV_VITALITY = 1.3

GOOD_HEX_PROBABILITY = 0.2

TECH_VP_REWARD = 2
RENAISSANCE_VP_REWARD = 25

GAME_END_SCORE = 250
EXTRA_GAME_END_SCORE_PER_PLAYER = 100

DATABASE_URL = "postgresql://cl:cl@localhost:5432/cl"

LOCAL = False

BASE_CITY_POWER_INCOME = 10.0

BASE_SURVIVAL_BONUS = 8
SURVIVAL_BONUS_PER_AGE = 4

BASE_WONDER_COST = {
    0: 20,
    1: 40,
    2: 60,
    3: 90,
    4: 120,
    5: 160,
    6: 200,
    7: 250,
    8: 400,
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
    2: [0.8, 0.55],
    3: [0.7, 0.55, 0.45],
    4: [0.65, 0.55, 0.45, 0.35],
}

MAX_SLOTS = 8
DEVELOP_COST = {'rural': 25, 'urban': 100, 'unit': 100}
MAX_SLOTS_OF_TYPE = {'urban': 4, 'unit': 4}
DEVELOP_VPS = 2

class AI():
    """
    Settings for the AI
    """
    CHANCE_MOVE_FLAG = 0.2

    CHANCE_URBANIZE = 0.7
    CHANCE_MILITARIZE=0.2
    CHANCE_EXPAND=0.2

    RURAL_SLOT_VALUE = 4

    DECLINE_YIELD_RATIO_THRESHOLD = 1.5


if os.path.exists('local_settings.py'):
    from local_settings import *