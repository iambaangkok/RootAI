import pygame
from pygame import Color, Vector2, Surface

from src.config import Config, Colors
from src.game.Board import Board


class Area:
    area_count: int = 0
    size_ratio: float = 0.07

    def __init__(self, position: Vector2):

        self.position: Vector2 = position
        self.radius: float = Board.rect.width * Area.size_ratio
        self.color: Color = Colors.WHITE

        self.connected_clearings: list = []
        self.connected_forests: list = []

        self.area_index: int = Area.area_count
        Area.area_count += 1

    def __del__(self):
        Area.area_count -= 1

    def draw(self, screen: Surface):
        pygame.draw.circle(screen, self.color, self.position, self.radius, width=1)

        # Text: area_index
        margin_top = 4
        text = str(self.area_index)

        surface = Config.FONT_1.render(text, True, Colors.WHITE)
        surface_rect = surface.get_rect()
        surface_rect.centerx = self.position.x
        surface_rect.top = self.position.y + self.radius + margin_top
        screen.blit(surface, surface_rect)

