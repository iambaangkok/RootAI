import logging
from random import randint

import pygame
import yaml
from pygame import Surface, Vector2, Rect
from pygame.time import Clock

from src.config import Config, Colors
from src.game.Faction import Faction
from src.game.Game import Action, Game
from src.utils.draw_utils import draw_text_in_rect

config = yaml.safe_load(open("config/config.yml"))

LOGGER = logging.getLogger('logger')


class RootTrainer:
    def __init__(self):
        pygame.init()
        self.screen: Surface = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.clock: Clock = pygame.time.Clock()
        self.running: bool = True

        self.delta_time: float = 0.0
        self.fps: float = 0.0

        # Game
        self.game: Game = Game()

        # Action Board
        self.action_arrow_pos = Vector2(0, 0)
        self.action_row_width = 16
        self.action_col_width = 100
        self.action_col = 1

        self.current_action: Action | None = None
        self.actions: list[Action] = self.game.get_actions()
        self.reset_arrow()

    def run(self):
        while self.running:
            self.init()
            self.update()
            self.render()

            # flip() the display to put your work on screen
            pygame.display.flip()

            self.delta_time = self.clock.tick(config['simulation']['framerate']) / 1000

        pygame.quit()

    #####
    # Init
    def init(self):
        self.actions = self.game.get_actions()
        pass

    #####
    # Update
    def update(self):
        keys = pygame.key.get_pressed()  # Checking pressed (hold) keys

        if self.game.running:
            if keys[pygame.K_f]:
                if config['simulation']['f-key-action'] == 'current':
                    self.current_action.function()
                    self.reset_arrow()

                elif config['simulation']['f-key-action'] == 'random':
                    self.random_arrow()
                    self.current_action.function()
                    self.reset_arrow()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.game.running:
                if event.type == pygame.KEYDOWN:
                    self.move_arrow(event.key)

                    if event.key == pygame.K_r:
                        self.random_arrow()

                    # Whose turn is this?
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.current_action.function()
                        self.reset_arrow()
            elif not self.game.running:
                if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_n:
                            self.game = Game()
                        case pygame.K_q:
                            self.running = False

        self.fps = self.calculate_fps()

    def random_arrow(self):
        self.reset_arrow()

        row = len(self.actions)
        rand = randint(0, row - 1)

        self.action_arrow_pos += Vector2(0, rand)
        self.current_action = self.actions[int(self.action_arrow_pos.y)]

    def move_arrow(self, direction):
        update_arrow = {
            pygame.K_UP: Vector2(0, -1),
            pygame.K_DOWN: Vector2(0, 1)
            # pygame.K_LEFT: Vector2(-1, 0),
            # pygame.K_RIGHT: Vector2(1, 0)
        }

        row = len(self.actions) // self.action_col + 1

        if direction in update_arrow.keys():
            new_arrow_index = self.action_arrow_pos + update_arrow[direction]
            if len(self.actions) > new_arrow_index[0] + new_arrow_index[1] * self.action_col >= 0 \
                    and self.action_col > new_arrow_index[0] >= 0 \
                    and row > new_arrow_index[1] >= 0:
                self.action_arrow_pos = new_arrow_index
                self.current_action = self.actions[int(self.action_arrow_pos.y)]

    def reset_arrow(self):
        self.action_arrow_pos.y = 0
        self.current_action = self.actions[int(self.action_arrow_pos.y)]

    def calculate_fps(self):
        if self.delta_time != 0:
            return 1.0 / self.delta_time
        else:
            return 0.0

    #####
    # RENDER
    def render(self):
        # Fill Black
        self.screen.fill("black")

        self.game.draw(self.screen)

        self.draw_fps_text()
        self.draw_delta_time_text()
        self.draw_action(self.screen)

        if not self.game.running:
            self.draw_game_ended(self.screen)

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
        # Phase
        color = Colors.ORANGE
        if self.game.turn_player == Faction.EYRIE:
            color = Colors.BLUE
        phase = Config.FONT_MD_BOLD.render("{} ({})".format(self.game.phase, self.game.sub_phase), True, color)
        phase_rect = phase.get_rect()
        starting_point = Vector2(0.75 * Config.SCREEN_WIDTH, 0.0 * Config.SCREEN_HEIGHT)
        shift = Vector2(10, 0.05 * Config.SCREEN_HEIGHT)
        phase_rect.topleft = starting_point + shift
        screen.blit(phase, phase_rect)

        # Action
        action = Config.FONT_1.render("({})".format(self.current_action.name), True, Colors.WHITE)
        action_rect = action.get_rect()
        shift = Vector2(10, 0)
        action_rect.bottomleft = phase_rect.bottomright + shift
        screen.blit(action, action_rect)

        # Prompt
        prompt_rect = Rect(0, 0, Config.SCREEN_WIDTH - phase_rect.left, Config.SCREEN_HEIGHT * 0.1)
        shift = Vector2(0, 8)
        prompt_rect.topleft = phase_rect.bottomleft + shift
        # screen.blit(prompt, prompt_rect)
        draw_text_in_rect(screen, "{}".format(self.game.prompt), Colors.WHITE, prompt_rect, Config.FONT_1, True)

        self.draw_arrow(screen, starting_point)
        self.draw_action_list(screen, starting_point)

    def draw_arrow(self, screen, starting_point):
        arrow = Config.FONT_1.render(">", True, Colors.WHITE)
        shift = Vector2(10, 0.15 * Config.SCREEN_HEIGHT)
        screen.blit(arrow, starting_point + shift + Vector2(self.action_arrow_pos[0] * self.action_col_width,
                                                            self.action_arrow_pos[1] * self.action_row_width))

    def draw_action_list(self, screen, starting_point):
        shift = Vector2(10 + 16, 0.15 * Config.SCREEN_HEIGHT)

        ind = 0
        for action in self.actions:
            action_text = Config.FONT_1.render(action.name, True, Colors.WHITE)
            screen.blit(action_text, starting_point + shift + Vector2(ind % self.action_col * self.action_col_width,
                                                                      ind // self.action_col * self.action_row_width))
            ind = ind + 1

    def draw_game_ended(self, screen: Surface):
        position = Vector2(Config.SCREEN_WIDTH/2, Config.SCREEN_HEIGHT/2)
        shift = Vector2(0, -0.05 * Config.SCREEN_HEIGHT)

        text = Config.FONT_XL.render("Game Ended", True, Colors.WHITE)
        rect = text.get_rect()
        rect.center = position + shift
        screen.blit(text, rect)

        shift = Vector2(0, 0)

        text = Config.FONT_MD.render("[N]ew game / [Q]uit", True, Colors.WHITE)
        rect = text.get_rect()
        rect.center = position + shift
        screen.blit(text, rect)