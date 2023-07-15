import pygame
from pygame import Color, Vector2, Surface, Rect

from src.config import Config, Colors
from src.game.Building import Building
from src.game.FactionBoard import FactionBoard
from src.utils import text_utils

MARQUISE_ACTIONS = {
    'Birdsong': [],
    'Daylight': {
        '1': ['Craft'],
        '2': ['Battle', 'March', 'Recruit', 'Build', 'Overwork']
    },
    'Evening': []
}


class MarquiseActionBoard:
    dimension = (Config.SCREEN_WIDTH * 0.25, Config.SCREEN_HEIGHT * 0.5)
    arrow_index = Vector2(0, 0)

    row_width = 30
    col_width = 200
    row = 3
    col = 2

    UPDATE_ARROW = {
        pygame.K_UP: Vector2(0, -1),
        pygame.K_DOWN: Vector2(0, 1),
        pygame.K_LEFT: Vector2(-1, 0),
        pygame.K_RIGHT: Vector2(1, 0)
    }

    def __init__(self, starting_point: Vector2):
        self.hasRecruited = False
        self.starting_point = starting_point
        pass

    def draw(self, screen: Surface):

        phase = Config.FONT_MD_BOLD.render("Daylight", True, Colors.WHITE)
        shift = Vector2(10, 0.05 * Config.SCREEN_HEIGHT)
        screen.blit(phase, self.starting_point + shift)

        self.draw_arrow(screen)
        self.draw_actions(screen)

    def move_arrow(self, direction):
        if direction in self.UPDATE_ARROW.keys():
            new_arrow_index = self.arrow_index + self.UPDATE_ARROW[direction]
            if len(MARQUISE_ACTIONS['Daylight']['2']) > new_arrow_index[0] + new_arrow_index[1] * self.col >= 0 \
                    and self.col > new_arrow_index[0] >= 0 \
                    and self.row > new_arrow_index[1] >= 0:
                self.arrow_index = new_arrow_index

    def draw_arrow(self, screen):
        arrow = Config.FONT_MD_BOLD.render("->", True, Colors.WHITE)
        shift = Vector2(10, 0.1 * Config.SCREEN_HEIGHT)
        screen.blit(arrow, self.starting_point + shift + Vector2(self.arrow_index[0] * self.col_width, self.arrow_index[1] * self.row_width))
        # print(Vector2(self.row_width, self.col_width))

    def draw_actions(self, screen):
        pass
