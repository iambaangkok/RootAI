import pygame
from pygame import Rect, Color, Surface, Vector2

from src.config import Config, Colors
from src.game.Area import Area


class Board:
    margin_x: float = 240
    margin_top: float = 40
    margin_bottom: float = 120
    rect: Rect = Rect((margin_x, margin_top),
                      (Config.SCREEN_WIDTH - margin_x * 2, Config.SCREEN_HEIGHT - margin_top - margin_bottom))

    def __init__(self, areas: list[Area]):
        self.name: str = "Forest"
        self.color: Color = Colors.GREEN
        self.areas: list[Area] = areas
        self.paths: list[tuple[int, int]] = []

    def add_path(self, area_1: int, area_2: int):
        if ((area_1, area_2) in self.paths) or \
                (self.areas[area_2] in self.areas[area_1].connected_clearings) or \
                (self.areas[area_1] in self.areas[area_2].connected_clearings):
            return

        self.paths.append((area_1, area_2))
        self.areas[area_1].connected_clearings.append(self.areas[area_2])
        self.areas[area_2].connected_clearings.append(self.areas[area_1])

    def draw(self, screen: Surface):
        pygame.draw.rect(screen, self.color, Board.rect, width=1)

        self.draw_areas(screen)

    def draw_areas(self, screen: Surface):
        for area in self.areas:
            area.draw(screen)

    def draw_paths_clearing(self, screen: Surface):
        for path in self.paths:
            pygame.draw.line(
                screen, Colors.WHITE,
                self.areas[path[0]].position,
                self.areas[path[1]].position
            )
        pass
