import logging
import sys


import pygame
import yaml
from pygame import Surface

from src.config import Config
from src.roottrainer.RootTrainer import RootTrainer

if __name__ == "__main__":
    config_path: str = str(sys.argv[1])
    config = yaml.safe_load(open(config_path))

    logging.basicConfig(level=logging.NOTSET)
    logging.getLogger('game_logger').setLevel(config['logging']['game']['level'])
    logging.getLogger('trainer_logger').setLevel(config['logging']['trainer']['level'])
    logging.getLogger('mcts_logger').setLevel(config['logging']['mcts']['level'])

    screen: Surface | None = None
    pygame.init()
    if Config.RENDER_ENABLE:
        screen: Surface = pygame.display.set_mode((Config.NATIVE_SCREEN_WIDTH, Config.NATIVE_SCREEN_HEIGHT))

    trainer = RootTrainer(screen)
    trainer.run()
