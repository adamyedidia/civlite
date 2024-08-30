from ai_game import ai_game
import argparse
import logging

# Configure logger
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='scripts/output/ai_game_debug.log',
                    filemode='w')

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)s - %(message)s')
console_handler.setFormatter(formatter)

# Add console handler to the root logger
logging.getLogger('').addHandler(console_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=int, required=True)
    parser.add_argument('--num_players', type=int, default=4)
    args = parser.parse_args()
    ai_game(args.id, args.num_players)