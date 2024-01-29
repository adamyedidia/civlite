from IPython import embed
from database import SessionLocal
from game import Game
from game_state import GameState
from civ import Civ
from civ_template import CivTemplate
from game_player import GamePlayer
from tech_template import TechTemplate
from tech import Tech
from unit_template import UnitTemplate
from unit import Unit
from hex import Hex
from city import City
from building_template import BuildingTemplate
from building import Building
from animation_frame import AnimationFrame
from game_state import GameState, update_staged_moves, get_most_recent_game_state


def main():
    sess = SessionLocal()

    # add objects that you want to use in the shell to this dictionary
    user_ns = {
        "sess": sess, 
        "Game": Game,
        "GameState": GameState,
        "Civ": Civ,
        "CivTemplate": CivTemplate,
        "GamePlayer": GamePlayer,
        "TechTemplate": TechTemplate,
        "Tech": Tech,
        "UnitTemplate": UnitTemplate,
        "Unit": Unit,
        "Hex": Hex,
        "City": City,
        "BuildingTemplate": BuildingTemplate,
        "Building": Building,
        "AnimationFrame": AnimationFrame,
        "get_most_recent_game_state": get_most_recent_game_state,
        "update_staged_moves": update_staged_moves,
    }

    embed(user_ns=user_ns)

    sess.close()

if __name__ == "__main__":
    main()
