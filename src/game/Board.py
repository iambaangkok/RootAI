import pygame
from pygame import Rect, Color

from src.config import Config, Colors


class Board:
    def __init__(self):
        margin = 160

        self.name = "Forest"
        self.rect = Rect((margin, margin), (Config.SCREEN_WIDTH - margin*2, Config.SCREEN_HEIGHT - margin*2))
        self.color = Colors.GREEN

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, width=1)
