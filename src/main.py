import logging

from src.game.Game import Game

logging.basicConfig(level=logging.NOTSET)
LOGGER = logging.getLogger('LOGGER')

game = Game()
game.run()
