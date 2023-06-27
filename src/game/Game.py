import pygame
from pygame import Vector2, Surface
from pygame.time import Clock

from src.config import Config, Colors
from src.game.Area import Area
from src.game.Board import Board


class Game:
    def __init__(self):
        pygame.init()
        self.screen: Surface = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.clock: Clock = pygame.time.Clock()
        self.running: bool = True

        self.delta_time: float = 0.0
        self.fps: float = 0.0

        # Board Game Components

        areas_offset_y = 0.05
        areas_radius = Board.rect.width * Area.size_ratio
        areas: list[Area] = [
            Area(Vector2(Board.rect.x + Board.rect.width * 0.12, Board.rect.y + Board.rect.height * (0.20 - areas_offset_y)), areas_radius),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.48, Board.rect.y + Board.rect.height * (0.15 - areas_offset_y)), areas_radius),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.88, Board.rect.y + Board.rect.height * (0.18 - areas_offset_y)), areas_radius),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.33, Board.rect.y + Board.rect.height * (0.33 - areas_offset_y)), areas_radius),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.70, Board.rect.y + Board.rect.height * (0.30 - areas_offset_y)), areas_radius),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.13, Board.rect.y + Board.rect.height * (0.47 - areas_offset_y)), areas_radius),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.55, Board.rect.y + Board.rect.height * (0.50 - areas_offset_y)), areas_radius),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.84, Board.rect.y + Board.rect.height * (0.45 - areas_offset_y)), areas_radius),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.32, Board.rect.y + Board.rect.height * (0.64 - areas_offset_y)), areas_radius),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.12, Board.rect.y + Board.rect.height * (0.80 - areas_offset_y)), areas_radius),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.53, Board.rect.y + Board.rect.height * (0.82 - areas_offset_y)), areas_radius),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.88, Board.rect.y + Board.rect.height * (0.80 - areas_offset_y)), areas_radius),
        ]

        self.board: Board = Board(areas)

        self.board.add_path(0, 1)
        self.board.add_path(0, 5)
        self.board.add_path(1, 2)
        self.board.add_path(1, 3)
        self.board.add_path(1, 4)
        self.board.add_path(2, 7)
        self.board.add_path(3, 4)
        self.board.add_path(3, 5)
        self.board.add_path(3, 6)
        self.board.add_path(4, 7)
        self.board.add_path(5, 8)
        self.board.add_path(5, 9)
        self.board.add_path(6, 8)
        self.board.add_path(6, 7)
        self.board.add_path(7, 11)
        self.board.add_path(8, 10)
        self.board.add_path(9, 10)
        self.board.add_path(10, 11)

    def init(self):
        pass

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        self.fps = self.calculate_fps()

    def calculate_fps(self):
        if self.delta_time != 0:
            return 1.0 / self.delta_time
        else:
            return 0.0

    def render(self):
        # Fill Black
        self.screen.fill("black")

        self.board.draw(self.screen)

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
