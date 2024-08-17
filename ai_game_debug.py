from ai_game_unit_stats import ai_game
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


ai_game(269, 4)