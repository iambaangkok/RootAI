import logging

import pygame
from pygame import Surface

from src.config import Config
from src.roottrainer.RootTrainer import RootTrainer

if __name__ == "__main__":

    logging.basicConfig(level=logging.NOTSET)
    logging.getLogger('game_logger').setLevel(logging.INFO)
    logging.getLogger('trainer_logger').setLevel(logging.INFO)
    logging.getLogger('mcts_logger').setLevel(logging.INFO)

    pygame.init()
    screen: Surface = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))

    trainer = RootTrainer(screen)
    trainer.run()
