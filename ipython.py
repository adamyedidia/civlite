from IPython import embed
from database import SessionLocal
from game import Game
from game_state import GameState
from civ import Civ
from civ_template import CivTemplate
from game_player import GamePlayer
from tech_template import TechTemplate
from unit_template import UnitTemplate
from unit import Unit
from hex import Hex
from city import City
from building_template import BuildingTemplate
from building import Building
from animation_frame import AnimationFrame
from game_state import GameState
from sqlalchemy import func


def main():
    sess = SessionLocal()

    # add objects that you want to use in the shell to this dictionary
    user_ns = {
        "sess": sess, 
        "func": func,
        "Game": Game,
        "GameState": GameState,
        "Civ": Civ,
        "CivTemplate": CivTemplate,
        "GamePlayer": GamePlayer,
        "TechTemplate": TechTemplate,
        "UnitTemplate": UnitTemplate,
        "Unit": Unit,
        "Hex": Hex,
        "City": City,
        "BuildingTemplate": BuildingTemplate,
        "Building": Building,
        "AnimationFrame": AnimationFrame,
    }

    embed(user_ns=user_ns)

    sess.close()

if __name__ == "__main__":
    main()
