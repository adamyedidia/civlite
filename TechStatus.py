from enum import Enum


class TechStatus(Enum):
    RESEARCHED = 'researched'
    UNAVAILABLE = 'unavailable'
    DISCARDED = 'discarded'
    AVAILABLE = 'available'
    RESEARCHING = 'researching'