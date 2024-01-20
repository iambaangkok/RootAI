import logging
from random import randint

import pygame
import yaml
from pygame import Surface, Vector2, Rect
from pygame.time import Clock

from src.config import Config, Colors
from src.game.Faction import Faction
from src.game.GameLogic import Action, GameLogic, Game
from src.roottrainer.agents.Agent import Agent
from src.roottrainer.CSVOutputWriter import CSVOutputWriter
from src.roottrainer.agents.MCTSAgent import MCTSAgent
from src.roottrainer.agents.RandomDecisionAgent import RandomDecisionAgent
from src.utils.draw_utils import draw_text_in_rect

config = yaml.safe_load(open("config/config.yml"))

LOGGER = logging.getLogger('trainer_logger')


class RootTrainer:
    def __init__(self, screen: Surface):

        self.fake_screen: Surface = screen.copy() if Config.RENDER_ENABLE else None
        self.screen: Surface = \
            pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)) \
            if Config.RENDER_ENABLE else None

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
        self.actions: list[Action] = []
        self.action_count: int = 0
        self.get_actions()
        self.reset_arrow()

        # Agent
        self.marquise_agent = self.init_agent(Faction.MARQUISE)
        self.eyrie_agent = self.init_agent(Faction.EYRIE)

        self.round_limit = config['simulation']['round']
        self.round = 0

        # Output
        self.collected_end_game_data = False

        self.winning_faction = ""
        self.winning_condition = ""
        self.turns_played = 0
        self.turn_player = ""
        self.vp_marquise = 0
        self.vp_eyrie = 0
        self.winning_dominance = ""

        self.output_writer = CSVOutputWriter(config['simulation']['output']['dir'])
        if config['simulation']['output']['enable']:
            self.output_writer.open()
            self.output_writer.write(['winner', 'condition', 'turn', 'current_player', 'vp_marquise', 'vp_eyrie', 'winning_dominance'])

        self.next_round()

    def __del__(self):
        # self.print_game_state()
        pass

    def init_agent(self, faction: Faction) -> Agent:
        match config['agent'][faction.lower()]['type']:
            case "random":
                return RandomDecisionAgent(faction)
            case "mcts":
                mcts_type = "one-depth"
                reward_function = "win"
                expand_count = 100
                rollout_no = 1
                time_limit = -1.0
                action_count_limit = -1

                if config['agent'][faction.lower()]['mcts']['type']:
                    mcts_type = config['agent'][faction.lower()]['mcts']['type']

                if config['agent'][faction.lower()]['mcts']['reward-function']:
                    reward_function = config['agent'][faction.lower()]['mcts']['reward-function']

                if config['agent'][faction.lower()]['mcts']['expand-count']:
                    expand_count = config['agent'][faction.lower()]['mcts']['expand-count']

                if config['agent'][faction.lower()]['mcts']['rollout-no']:
                    rollout_no = config['agent'][faction.lower()]['mcts']['rollout-no']

                if config['agent'][faction.lower()]['mcts']['time-limit']:
                    time_limit = config['agent'][faction.lower()]['mcts']['time-limit']

                if config['agent'][faction.lower()]['mcts']['action-count-limit']:
                    action_count_limit = config['agent'][faction.lower()]['mcts']['action-count-limit']

                return MCTSAgent(faction, mcts_type, reward_function, expand_count, rollout_no, time_limit, action_count_limit)

    def run(self):
        while self.running:
            self.init()
            self.update()
            if Config.RENDER_ENABLE:
                self.render()
                # flip() the display to put your work on screen
                pygame.display.flip()

            self.delta_time = self.clock.tick(config['simulation']['framerate']) / 1000

        pygame.quit()

    #####
    # Init
    def init(self):
        pass

    #####
    # Update
    def update(self):
        keys = pygame.key.get_pressed()  # Checking pressed (hold) keys

        if not self.get_game_logic().running and not self.collected_end_game_data:
            self.winning_faction, \
                self.winning_condition, \
                self.turns_played, \
                self.turn_player, \
                self.vp_marquise, \
                self.vp_eyrie, \
                self.winning_dominance = self.get_game_logic().get_end_game_data()

            if self.winning_dominance is None:
                self.winning_dominance = "none"
            else:
                self.winning_dominance = self.winning_dominance.suit.lower()

            self.collected_end_game_data = True
            if config['simulation']['output']['enable']:
                self.output_writer.write([
                    self.winning_faction, self.winning_condition, self.turns_played, self.turn_player,
                    self.vp_marquise, self.vp_eyrie, self.winning_dominance])

        if not self.get_game_logic().running:
            if self.round <= self.round_limit:
                if Config.AUTO_NEXT_ROUND:
                    self.next_round()
                else:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            match event.key:
                                case pygame.K_n:
                                    self.next_round()
                                case pygame.K_q:
                                    self.running = False
            else:
                self.running = False

        if self.get_game_logic().running:
            if keys[pygame.K_a] or (not Config.AGENT_REQUIRE_KEY_HOLD):
                LOGGER.log(21, "R{}/{}: action_count {}".format(self.round, self.round_limit, self.action_count))
                if self.get_game_logic().turn_player == Faction.MARQUISE and config['agent']['marquise']['enable']:
                    self.execute_agent_action(Faction.MARQUISE)
                elif self.get_game_logic().turn_player == Faction.EYRIE and config['agent']['eyrie']['enable']:
                    self.execute_agent_action(Faction.EYRIE)

                self.action_count += 1

            # elif keys[pygame.K_f]:
            #     if config['simulation']['f-key-action'] == 'current':
            #         self.current_action.function()
            #         self.actions = self.get_game().get_actions()
            #         self.reset_arrow()
            #
            if keys[pygame.K_f] and config['simulation']['f-key-action'] == 'random':
                if self.get_game_logic().turn_player == Faction.MARQUISE and not config['agent']['marquise']['enable']:
                    self.random_arrow()
                    self.execute_action()
                    self.get_actions()
                    self.reset_arrow()
                elif self.get_game_logic().turn_player == Faction.EYRIE and not config['agent']['eyrie']['enable']:
                    self.random_arrow()
                    self.execute_action()
                    self.get_actions()
                    self.reset_arrow()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.get_game_logic().running:
                if event.type == pygame.KEYDOWN:
                    self.move_arrow(event.key)

                    if event.key == pygame.K_r:
                        self.random_arrow()

                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.execute_action()
                        self.get_actions()
                        self.reset_arrow()

                    if event.key == pygame.K_o:
                        self.print_game_state()

                    if event.key == pygame.K_c:
                        self.new_game_from_current_game_state()

        self.fps = self.calculate_fps()

    def next_round(self):
        self.new_game()
        self.collected_end_game_data = False
        self.round += 1
        self.get_actions()
        self.reset_arrow()
        self.action_count = 0

        LOGGER.log(21, "Simulating Round {}/{}".format(self.round, self.round_limit))

    ###
    # Arrows
    def random_arrow(self):
        self.reset_arrow()

        row = len(self.actions)
        rand = randint(0, row - 1)

        self.action_arrow_pos += Vector2(0, rand)
        self.current_action = self.actions[int(self.action_arrow_pos.y)]

    def set_arrow(self, index: int):
        self.reset_arrow()

        self.action_arrow_pos += Vector2(0, index)
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

    def get_arrow_index(self) -> int:
        return int(self.action_arrow_pos.y)

    ###
    # Actions
    def execute_agent_action(self, faction: Faction):
        agent = self.faction_to_agent(faction)
        action = agent.choose_action(self.get_game_state(), self.actions)
        action_index = self.actions.index(action)
        self.set_arrow(action_index)
        decree_counter = self.get_game_logic().decree_counter
        self.execute_action()
        self.get_actions()
        self.reset_arrow()

    def get_actions(self):
        if self.get_game_logic().turn_player == Faction.MARQUISE and config['agent']['marquise']['enable']:
            self.actions = self.get_game_logic().get_agent_actions()
        elif self.get_game_logic().turn_player == Faction.EYRIE and config['agent']['eyrie']['enable']:
            self.actions = self.get_game_logic().get_agent_actions()
        else:
            self.actions = self.get_game_logic().get_actions()

    def execute_action(self):
        self.current_action.function()

    ###
    # Game

    def print_game_state(self):
        arr: list = self.get_game_as_num_array()
        print("[")
        for i in range(len(arr)):
            print(" ", str(arr[i]) + ",")
        print("]")

    def get_game_as_num_array(self):
        arr: list = []
        arr = self.get_game_logic().get_state_as_num_array()
        return arr

    def get_game_logic(self) -> GameLogic:
        return self.get_game().logic

    def get_game(self) -> Game:
        return self.game

    def new_game(self):
        self.game = Game()

    def set_game_state(self, arr: list = None):
        self.game.logic.set_state_from_num_array(arr)

    def get_game_state(self) -> list:
        return self.game.logic.get_state_as_num_array()

    def new_game_from_current_game_state(self):
        LOGGER.info("new_game_from_current_game_state")
        arr: list = self.get_game_state()
        self.new_game()
        self.set_game_state(arr)
        self.get_actions()
        self.reset_arrow()

    ###
    # Utils
    def faction_to_agent(self, faction: Faction):
        if faction == Faction.MARQUISE:
            return self.marquise_agent
        elif faction == Faction.EYRIE:
            return self.eyrie_agent

    def calculate_fps(self):
        if self.delta_time != 0:
            return 1.0 / self.delta_time
        else:
            return 0.0

    #####
    # RENDER
    def render(self):
        screen: Surface = self.fake_screen
        # Fill Black
        screen.fill("black")

        if Config.GAME_RENDER_ENABLE:
            self.get_game().draw(screen)

        self.draw_fps_text(screen)
        self.draw_delta_time_text(screen)
        self.draw_round_text(screen)
        if Config.ACTIONS_RENDER_ENABLE:
            self.draw_action(screen)

            if not self.get_game_logic().running:
                self.draw_game_ended(screen)

        self.screen.blit(pygame.transform.smoothscale(self.fake_screen, self.screen.get_rect().size), (0, 0))

    def draw_fps_text(self, screen: Surface):
        margin_right = 20
        margin_top = 20
        text = "fps: {fps:.2f}".format(fps=self.fps)

        surface = Config.FONT_1.render(text, True, Colors.WHITE)
        surface_rect = surface.get_rect()
        surface_rect.right = Config.NATIVE_SCREEN_WIDTH - margin_right
        surface_rect.top = margin_top

        screen.blit(surface, surface_rect)

    def draw_delta_time_text(self, screen: Surface):
        margin_right = 20
        margin_top = 40
        text = "delta_time: {delta_time:.3f}".format(delta_time=self.delta_time)

        surface = Config.FONT_1.render(text, True, Colors.WHITE)
        surface_rect = surface.get_rect()
        surface_rect.right = Config.NATIVE_SCREEN_WIDTH - margin_right
        surface_rect.top = margin_top

        screen.blit(surface, surface_rect)

    def draw_round_text(self, screen: Surface):
        margin_right = 120
        margin_top = 20

        text = "round: {}".format(self.round)
        surface = Config.FONT_1.render(text, True, Colors.WHITE)
        surface_rect = surface.get_rect()
        surface_rect.right = Config.NATIVE_SCREEN_WIDTH - margin_right
        surface_rect.top = margin_top
        # surface_rect.centerx = Config.SCREEN_WIDTH / 2
        # surface_rect.centery = Config.SCREEN_HEIGHT - margin_bottom

        screen.blit(surface, surface_rect)

    def draw_action(self, screen: Surface):
        # Phase
        color = Colors.ORANGE
        if self.get_game_logic().turn_player == Faction.EYRIE:
            color = Colors.BLUE
        phase = Config.FONT_MD_BOLD.render("{} ({})".format(self.get_game_logic().phase, self.get_game_logic().sub_phase), True, color)
        phase_rect = phase.get_rect()
        starting_point = Vector2(0.75 * Config.NATIVE_SCREEN_WIDTH, 0.0 * Config.NATIVE_SCREEN_HEIGHT)
        shift = Vector2(10, 0.05 * Config.NATIVE_SCREEN_HEIGHT)
        phase_rect.topleft = starting_point + shift
        screen.blit(phase, phase_rect)

        # Action
        action = Config.FONT_1.render("({})".format(self.current_action.name), True, Colors.WHITE)
        action_rect = action.get_rect()
        shift = Vector2(10, 0)
        action_rect.bottomleft = phase_rect.bottomright + shift
        screen.blit(action, action_rect)

        # Prompt
        prompt_rect = Rect(0, 0, Config.NATIVE_SCREEN_WIDTH - phase_rect.left, Config.NATIVE_SCREEN_HEIGHT * 0.1)
        shift = Vector2(0, 8)
        prompt_rect.topleft = phase_rect.bottomleft + shift
        # screen.blit(prompt, prompt_rect)
        draw_text_in_rect(screen, "{}".format(self.get_game_logic().prompt), Colors.WHITE, prompt_rect, Config.FONT_1, True)

        self.draw_arrow(screen, starting_point)
        self.draw_action_list(screen, starting_point)

    def draw_arrow(self, screen, starting_point):
        arrow = Config.FONT_1.render(">", True, Colors.WHITE)
        shift = Vector2(10, 0.15 * Config.NATIVE_SCREEN_HEIGHT)
        screen.blit(arrow, starting_point + shift + Vector2(self.action_arrow_pos[0] * self.action_col_width,
                                                            self.action_arrow_pos[1] * self.action_row_width))

    def draw_action_list(self, screen, starting_point):
        shift = Vector2(10 + 16, 0.15 * Config.NATIVE_SCREEN_HEIGHT)

        ind = 0
        for action in self.actions:
            action_text = Config.FONT_1.render(action.name, True, Colors.WHITE)
            screen.blit(action_text, starting_point + shift + Vector2(ind % self.action_col * self.action_col_width,
                                                                      ind // self.action_col * self.action_row_width))
            ind = ind + 1

    def draw_game_ended(self, screen: Surface):

        position = Vector2(Config.NATIVE_SCREEN_WIDTH / 2, Config.NATIVE_SCREEN_HEIGHT / 2)

        rect = Rect(0, 0, 0, 0)
        rect.width = 0.2 * Config.NATIVE_SCREEN_WIDTH
        rect.height = 0.35 * Config.NATIVE_SCREEN_HEIGHT
        rect.midtop = position + Vector2(0, -0.1 * Config.NATIVE_SCREEN_HEIGHT)
        surface = Surface(rect.size)
        surface.set_alpha(128)
        pygame.draw.rect(surface, Colors.BLACK, rect)
        screen.blit(surface, rect.topleft)
        # pygame.draw.rect(screen, Colors.BLACK_A_128, rect)

        ###
        shift = Vector2(0, -0.05 * Config.NATIVE_SCREEN_HEIGHT)
        text = Config.FONT_XL.render("Round {}/{} Ended".format(self.round, self.round_limit), True, Colors.WHITE)
        rect = text.get_rect()
        rect.center = position + shift
        screen.blit(text, rect)
        ###
        shift = Vector2(0, 0)
        text = Config.FONT_MD.render("[N]ew game / [Q]uit", True, Colors.WHITE)
        rect = text.get_rect()
        rect.center = position + shift
        screen.blit(text, rect)
        ###
        offset_x = 0.05 * Config.NATIVE_SCREEN_WIDTH
        gap_y = 0.03
        ###
        shift = Vector2(-offset_x, 1 * gap_y * Config.NATIVE_SCREEN_HEIGHT)
        text = Config.FONT_SM.render("winner: {}".format(self.winning_faction), True, Colors.WHITE)
        rect = text.get_rect()
        rect.midleft = position + shift
        screen.blit(text, rect)
        ###
        gap_y = 0.03
        offset_y = 0.05
        shift = Vector2(-offset_x, offset_y + 2 * gap_y * Config.NATIVE_SCREEN_HEIGHT)
        text = Config.FONT_SM.render("condition: {}".format(self.winning_condition), True, Colors.WHITE)
        rect = text.get_rect()
        rect.midleft = position + shift
        screen.blit(text, rect)
        ###
        shift = Vector2(-offset_x, offset_y + 3 * gap_y * Config.NATIVE_SCREEN_HEIGHT)
        text = Config.FONT_SM.render("turn count: {}".format(self.turns_played), True, Colors.WHITE)
        rect = text.get_rect()
        rect.midleft = position + shift
        screen.blit(text, rect)
        ###
        shift = Vector2(-offset_x, offset_y + 4 * gap_y * Config.NATIVE_SCREEN_HEIGHT)
        text = Config.FONT_SM.render("current player: {}".format(self.turn_player), True, Colors.WHITE)
        rect = text.get_rect()
        rect.midleft = position + shift
        screen.blit(text, rect)
        ###
        shift = Vector2(-offset_x, offset_y + 5 * gap_y * Config.NATIVE_SCREEN_HEIGHT)
        text = Config.FONT_SM.render("marquise vp: {}".format(self.vp_marquise), True, Colors.WHITE)
        rect = text.get_rect()
        rect.midleft = position + shift
        screen.blit(text, rect)
        ###
        shift = Vector2(-offset_x, offset_y + 6 * gap_y * Config.NATIVE_SCREEN_HEIGHT)
        text = Config.FONT_SM.render("eyrie vp: {}".format(self.vp_eyrie), True, Colors.WHITE)
        rect = text.get_rect()
        rect.midleft = position + shift
        screen.blit(text, rect)
        ###
        shift = Vector2(-offset_x, offset_y + 7 * gap_y * Config.NATIVE_SCREEN_HEIGHT)
        text = Config.FONT_SM.render(
            "winning dominance: {}".format(self.winning_dominance.lower()),
            True,
            Colors.WHITE)
        rect = text.get_rect()
        rect.midleft = position + shift
        screen.blit(text, rect)
