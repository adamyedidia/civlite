import os


CITY_CAPTURE_REWARD = 5
UNIT_KILL_REWARD = 1
CAMP_CLEAR_VP_REWARD = 5
CAMP_CLEAR_CITY_POWER_REWARD = 20

BASE_FOOD_COST_OF_POP = 6
ADDITIONAL_PER_POP_FOOD_COST = 2

FAST_VITALITY_DECAY_RATE = 0.80
VITALITY_DECAY_RATE = 0.96

MAP_HOMOGENEITY_LEVEL = 200

NUM_STARTING_LOCATION_OPTIONS = 3

PER_PLAYER_AREA = 40
STARTING_CIV_VITALITY = 2.0

GOOD_HEX_PROBABILITY = 0.2

TECH_VP_REWARD = 2

GAME_END_SCORE = 250
EXTRA_GAME_END_SCORE_PER_PLAYER = 100

# GAME_END_SCORE = 4
# EXTRA_GAME_END_SCORE_PER_PLAYER = 0

DATABASE_URL = "postgresql://cl:cl@localhost:5432/cl"

LOCAL = False

BASE_CITY_POWER_INCOME = 10.0

SURVIVAL_BONUS = 25

MULLIGAN_PENALTY = 5

if os.path.exists('local_settings.py'):
    from local_settings import *