from enum import Enum

class MoveType(Enum):
    CHOOSE_STARTING_CITY = "choose_starting_city"
    CHOOSE_TECH = "choose_tech"
    CHOOSE_TENET = "choose_tenet"
    CHOOSE_BUILDING = "choose_building"
    CANCEL_BUILDING = "cancel_building"
    SELECT_INFINITE_QUEUE = "select_infinite_queue"
    DEVELOP = "develop"
    ADD_TARGET = "add_target"
    SET_ALL_TARGETS = "set_all_targets"
    REMOVE_TARGET = "remove_target"
    CHOOSE_FOCUS = "choose_focus"
    MAKE_TERRITORY = "make_territory"
    TRADE_HUB = "trade_hub"
    SELECT_GREAT_PERSON = "select_great_person"
    FOUND_CITY = "found_city"
    CHOOSE_DECLINE_OPTION = "choose_decline_option"