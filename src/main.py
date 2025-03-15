import logging
import sys

import pygame
import yaml
from pygame import Surface

from config import Config
from roottrainer.RootTrainer import RootTrainer

if __name__ == "__main__":
    config_path: str = ""
    if len(sys.argv) > 1:
        config_path = str(sys.argv[1])
    if config_path == "":
        config_path = "./config/config.yml"
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
