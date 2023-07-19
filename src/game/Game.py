from enum import StrEnum

import pygame
from pygame import Vector2, Surface
from pygame.time import Clock

from src.config import Config, Colors
from src.game.Area import Area
from src.game.Board import Board
from src.game.Building import Building
from src.game.EyrieBoard import EyrieBoard
from src.game.FactionBoard import FactionBoard
from src.game.MarquiseBoard import MarquiseBoard
from src.game.Suit import Suit
from src.game.Token import Token
from src.game.Warrior import Warrior


class Faction(StrEnum):
    MARQUISE = "marquise"
    EYRIE = "eyrie"


class Phase(StrEnum):
    BIRDSONG = "birdsong"
    DAYLIGHT = "daylight"
    EVENING = "evening"
    TURMOIL = "turmoil"


MARQUISE_ACTIONS = {
    Phase.BIRDSONG: [['Next']],
    Phase.DAYLIGHT: [
        ['Craft', 'Next'],
        ['Battle', 'March', 'Recruit', 'Build', 'Overwork', 'Next']
    ],
    Phase.EVENING: [['Next']]
}


class Game:
    def __init__(self):
        pygame.init()
        self.screen: Surface = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.clock: Clock = pygame.time.Clock()
        self.running: bool = True

        self.delta_time: float = 0.0
        self.fps: float = 0.0

        # Game Data
        self.turn_count: int = 0
        self.turn_player: Faction = Faction.MARQUISE
        self.phase: Phase = Phase.DAYLIGHT
        self.sub_phase = 1
        # Board Game Components

        areas_offset_y = 0.05
        areas_radius = Board.rect.width * Area.size_ratio
        areas: [Area] = [
            Area(Vector2(Board.rect.x + Board.rect.width * 0.12, Board.rect.y + Board.rect.height * (0.20 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.ROOST]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.55, Board.rect.y + Board.rect.height * (0.15 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.EMPTY, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.88, Board.rect.y + Board.rect.height * (0.25 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.EMPTY, Building.EMPTY]),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.43, Board.rect.y + Board.rect.height * (0.35 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.EMPTY]),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.10, Board.rect.y + Board.rect.height * (0.45 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.EMPTY, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.34, Board.rect.y + Board.rect.height * (0.58 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.66, Board.rect.y + Board.rect.height * (0.53 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.EMPTY, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.90, Board.rect.y + Board.rect.height * (0.56 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.WORKSHOP]),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.12, Board.rect.y + Board.rect.height * (0.83 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.39, Board.rect.y + Board.rect.height * (0.88 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.EMPTY, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.62, Board.rect.y + Board.rect.height * (0.80 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.RECRUITER, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.84, Board.rect.y + Board.rect.height * (0.88 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.SAWMILL]),
        ]

        areas[-1].add_token(Token.CASTLE)
        areas[-1].add_token(Token.WOOD, 3)

        for i in range(1, len(areas)):
            areas[i].add_warrior(Warrior.MARQUIS, 1)

        areas[0].add_warrior(Warrior.EYRIE, 6)

        self.board: Board = Board(areas)

        paths = [(0, 1), (0, 3), (0, 4), (1, 2), (2, 3), (2, 7), (3, 5), (4, 5), (4, 8), (5, 6), (5, 8), (5, 10), (6, 7), (6, 11), (7, 11), (8, 9),
                 (9, 10), (10, 11)]
        for path in paths:
            self.board.add_path(path[0], path[1])

        self.marquise = MarquiseBoard("Marquise de Cat", Colors.ORANGE, 14, Vector2(0, 0.0 * Config.SCREEN_HEIGHT))
        self.eyrie = EyrieBoard("Eyrie Dynasties", Colors.BLUE, 24, Vector2(0, 0.5 * Config.SCREEN_HEIGHT))

        # Action Board
        self.action_arrow_pos = Vector2(0, 0)
        self.action_row_width = 16
        self.action_col_width = 100
        self.action_col = 1

    def init(self):
        pass

    def update(self):

        # 1. whose turn is this?
        # 2.

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.move_arrow(event.key)
            if self.turn_player == Faction.MARQUISE:
                self.check_event_marquise(event)
            else:
                self.check_event_eyrie(event)
        self.fps = self.calculate_fps()

    def check_event_marquise(self, event: pygame.event.Event):

        # which phase
        phase = 'Daylight'

        if phase == 'Daylight':
            # Place one wood at each sawmill
            for area in self.board.areas:
                area.token_count[Token.WOOD] += area.buildings.count(Building.SAWMILL)


        # elif phase == 'Daylight':

        # daylight
        # move
        # from where
        # to where
        # how many

        pass

    def check_event_eyrie(self, event: pygame.event.Event):

        pass

    def calculate_fps(self):
        if self.delta_time != 0:
            return 1.0 / self.delta_time
        else:
            return 0.0

    def render(self):
        # Fill Black
        self.screen.fill("black")

        self.board.draw(self.screen)
        self.marquise.draw(self.screen)
        self.eyrie.draw(self.screen)
        self.draw_action(self.screen)
        # self.marquise_action.draw(self.screen)

        self.draw_fps_text()
        self.draw_delta_time_text()

    def draw_fps_text(self):
        margin_right = 20
        margin_top = 20
        text = "fps: {fps:.2f}".format(fps=self.fps)

        surface = Config.FONT_1.render(text, True, Colors.WHITE)
        surface_rect = surface.get_rect()
        surface_rect.right = Config.SCREEN_WIDTH - margin_right
        surface_rect.top = margin_top

        self.screen.blit(surface, surface_rect)

    def draw_delta_time_text(self):
        margin_right = 20
        margin_top = 40
        text = "delta_time: {delta_time:.3f}".format(delta_time=self.delta_time)

        surface = Config.FONT_1.render(text, True, Colors.WHITE)
        surface_rect = surface.get_rect()
        surface_rect.right = Config.SCREEN_WIDTH - margin_right
        surface_rect.top = margin_top

        self.screen.blit(surface, surface_rect)

    def draw_action(self, screen: Surface):

        phase = Config.FONT_MD_BOLD.render("{}".format(self.phase), True, Colors.ORANGE)
        starting_point = Vector2(0.75 * Config.SCREEN_WIDTH, 0.0 * Config.SCREEN_HEIGHT)
        shift = Vector2(10, 0.05 * Config.SCREEN_HEIGHT)
        screen.blit(phase, starting_point + shift)

        self.draw_arrow(screen, starting_point)
        self.draw_action_list(screen, starting_point)

    def move_arrow(self, direction):

        UPDATE_ARROW = {
            pygame.K_UP: Vector2(0, -1),
            pygame.K_DOWN: Vector2(0, 1),
            pygame.K_LEFT: Vector2(-1, 0),
            pygame.K_RIGHT: Vector2(1, 0)
        }

        row = len(MARQUISE_ACTIONS[self.phase][self.sub_phase]) // self.action_col + 1

        if direction in UPDATE_ARROW.keys():
            new_arrow_index = self.action_arrow_pos + UPDATE_ARROW[direction]
            if len(MARQUISE_ACTIONS[self.phase][self.sub_phase]) > new_arrow_index[0] + new_arrow_index[1] * self.action_col >= 0 \
                    and self.action_col > new_arrow_index[0] >= 0 \
                    and row > new_arrow_index[1] >= 0:
                self.action_arrow_pos = new_arrow_index

    def draw_arrow(self, screen, starting_point):
        arrow = Config.FONT_1.render(">", True, Colors.WHITE)
        shift = Vector2(10, 0.09 * Config.SCREEN_HEIGHT)
        screen.blit(arrow, starting_point + shift + Vector2(self.action_arrow_pos[0] * self.action_col_width,
                                                            self.action_arrow_pos[1] * self.action_row_width))

    def draw_action_list(self, screen, starting_point):
        shift = Vector2(10 + 16, 0.09 * Config.SCREEN_HEIGHT)

        actions = MARQUISE_ACTIONS[self.phase][self.sub_phase]

        ind = 0
        for action in actions:
            action_text = Config.FONT_1.render(action, True, Colors.WHITE)
            screen.blit(action_text, starting_point + shift + Vector2(ind % self.action_col * self.action_col_width,
                                                                      ind // self.action_col * self.action_row_width))
            ind = ind + 1

    # Game Loop
    def run(self):
        while self.running:
            self.init()
            self.update()
            self.render()

            # flip() the display to put your work on screen
            pygame.display.flip()

            self.delta_time = self.clock.tick(Config.FRAME_RATE) / 1000

        pygame.quit()
