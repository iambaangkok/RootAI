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
        self.board: Board = Board()
        self.areas: list[Area] = [
            Area(Vector2(Board.rect.x + Board.rect.width*0.12, Board.rect.y + Board.rect.height*0.18))
        ]

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

        for area in self.areas:
            area.draw(self.screen)

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
