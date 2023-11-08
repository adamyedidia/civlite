import os


CITY_CAPTURE_REWARD = 5
UNIT_KILL_REWARD = 1

BASE_FOOD_COST_OF_POP = 8
ADDITIONAL_PER_POP_FOOD_COST = 1

FAST_VITALITY_DECAY_RATE = 0.8
VITALITY_DECAY_RATE = 0.95

MAP_HOMOGENEITY_LEVEL = 200

DATABASE_URL = "postgresql://cl:cl@localhost:5432/cl"

LOCAL = False

if os.path.exists('local_settings.py'):
    from local_settings import *