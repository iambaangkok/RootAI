import pygame
from pygame import Rect, Color, Surface, Vector2

from src.config import Config, Colors
from src.game.Area import Area
from src.utils.geometry import get_path_points


class Board:
    dimension: float = 800
    rect: Rect = Rect(((Config.SCREEN_WIDTH - dimension)/2, (Config.SCREEN_HEIGHT - dimension)/2),
                      (dimension, dimension))

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

        self.draw_paths_clearing(screen)
        self.draw_areas(screen)

    def draw_areas(self, screen: Surface):
        for area in self.areas:
            area.draw(screen)

    def draw_paths_clearing(self, screen: Surface):
        for path in self.paths:
            area_a = self.areas[path[0]]
            area_b = self.areas[path[1]]
            additional_shift = 5
            pos_a, pos_b = get_path_points(area_a.position, area_b.position, area_a.radius + additional_shift)

            pygame.draw.line(
                screen, Colors.WHITE, pos_a, pos_b, width=5
            )
        pass

