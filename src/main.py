import logging

from src.game.Game import Game

logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)

game = Game()
game.run()
