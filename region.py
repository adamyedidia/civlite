from enum import Enum


class Region(Enum):
    BARBARIAN = 1
    MEDITERRANEAN = 2
    MIDDLE_EAST = 3
    SOUTH_ASIA = 4
    EAST_ASIA = 5
    AMERICAS = 6
    EUROPE = 7  # None at age 0
    AFRICA = 8  # None at age 0
    GLOBAL = 9