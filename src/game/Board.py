import pygame
from pygame import Rect, Color, Surface

from src.config import Config, Colors


class Board:
    margin_x: float = 240
    margin_top: float = 40
    margin_bottom: float = 120
    rect: Rect = Rect((margin_x, margin_top),
                      (Config.SCREEN_WIDTH - margin_x * 2, Config.SCREEN_HEIGHT - margin_top - margin_bottom))

    def __init__(self):
        self.name: str = "Forest"
        self.color: Color = Colors.GREEN

    def draw(self, screen: Surface):
        pygame.draw.rect(screen, self.color, Board.rect, width=1)
