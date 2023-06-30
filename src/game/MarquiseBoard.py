import pygame
from pygame import Rect, Color, Surface

from src.config import Config, Colors
from src.game.Area import Area

BUILDING_TRACKER = [0, 0, 0]
BUILDING_COST = [0, 1, 2, 3, 3, 4]
BUILDING_REWARD = [
    [0, 1, 2, 3, 4, 5],
    [0, 2, 2, 3, 4, 5],
    [0, 1, 2, 3, 3, 4]
]
BUILDING_DRAW_REWARD = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 1, 0],
]
BUILDING_TRACKER_NAME = ["Sawmills", "Workshops", "Recruiters"]


def add_tuple(a, b):
    return tuple(map(lambda i, j: i + j, a, b))


class MarquiseBoard:
    dimension: float = 400
    starting_point = (20, 30)
    rect: Rect = Rect(starting_point,
                      (dimension, dimension))

    def __init__(self):
        self.name: str = "Forest"
        self.color: Color = Colors.ORANGE

    def draw(self, screen: Surface):
        pygame.draw.rect(screen, self.color, MarquiseBoard.rect, width=3)

        # Text
        points_text = Config.FONT_MD_BOLD.render("Marquise", True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(points_text, add_tuple(self.starting_point, shift))

        for i in range(3):
            self.draw_tracker(screen, BUILDING_TRACKER_NAME[i], add_tuple(self.starting_point, (10, 20 + 110 * i + points_text.get_height())), (380, 100))

    def draw_tracker(self, screen, title, starting_point, size):
        # Box
        box = Rect(starting_point, size)
        pygame.draw.rect(screen, self.color, box, width=1)

        # Text
        points_text = Config.FONT_SM_BOLD.render(title, True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(points_text, add_tuple(starting_point, shift))
