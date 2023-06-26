import pygame
from pygame.font import Font

from src.config import Config, Colors
from src.game.Board import Board


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.delta_time = 0
        self.fps = 0.0

        # Board Game Components
        self.board = Board()

        # Misc UI
        self.font = Font("./assets/fonts/UbuntuMono-Regular.ttf", 16)

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

        surface = self.font.render(text, True, Colors.WHITE)
        surface_rect = surface.get_rect()
        surface_rect.right = Config.SCREEN_WIDTH - margin_right
        surface_rect.top = margin_top

        self.screen.blit(surface, surface_rect)

    def draw_delta_time_text(self):
        margin_right = 20
        margin_top = 40
        text = "delta_time: {delta_time:.2f}".format(delta_time=self.delta_time)

        surface = self.font.render(text, True, Colors.WHITE)
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
