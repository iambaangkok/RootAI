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
from src.game.Item import Item
from src.game.MarquiseBoard import MarquiseBoard
from src.game.PlayingCard import PlayingCard, PlayingCardName, PlayingCardPhase
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

        # Board Game Components

        self.draw_pile: [PlayingCard] = [
            PlayingCard(0, PlayingCardName.AMBUSH, Suit.BIRD, PlayingCardPhase.BATTLE),
            PlayingCard(1, PlayingCardName.AMBUSH, Suit.BIRD, PlayingCardPhase.BATTLE),
            PlayingCard(2, PlayingCardName.BIRDY_HANDLE, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 1, Item.BAG),
            PlayingCard(3, PlayingCardName.ARMORERS, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}),
            PlayingCard(4, PlayingCardName.CROSSBOW, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}, 1, Item.CROSSBOW),
            PlayingCard(5, PlayingCardName.WOODLAND_RUNNERS, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1, Item.BOOTS),
            PlayingCard(6, PlayingCardName.ARMS_TRADER, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2, Item.KNIFE),
            PlayingCard(7, PlayingCardName.ARMS_TRADER, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2, Item.KNIFE),
            PlayingCard(8, PlayingCardName.SAPPERS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.MOUSE: 1}),
            PlayingCard(9, PlayingCardName.SAPPERS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.MOUSE: 1}),
            PlayingCard(10, PlayingCardName.BRUTAL_TACTICS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.FOX: 2}),
            PlayingCard(11, PlayingCardName.BRUTAL_TACTICS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.FOX: 2}),
            PlayingCard(12, PlayingCardName.ROYAL_CLAIM, Suit.BIRD, PlayingCardPhase.BIRDSONG, {Suit.BIRD: 4}),

            PlayingCard(13, PlayingCardName.AMBUSH, Suit.FOX, PlayingCardPhase.BATTLE),
            PlayingCard(14, PlayingCardName.GENTLY_USED_KNAPSACK, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 1, Item.BAG),
            PlayingCard(15, PlayingCardName.ROOT_TEA, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2, Item.KEG),
            PlayingCard(16, PlayingCardName.TRAVEL_GEAR, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1, Item.BOOTS),
            PlayingCard(17, PlayingCardName.PROTECTION_RACKET, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 2}, 3, Item.COIN),
            PlayingCard(18, PlayingCardName.FOXFOLK_STEEL, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2, Item.KNIFE),
            PlayingCard(19, PlayingCardName.ANVIL, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}, 2, Item.HAMMER),
            PlayingCard(20, PlayingCardName.STAND_AND_DELIVER, Suit.FOX, PlayingCardPhase.BIRDSONG, {Suit.MOUSE: 3}),
            PlayingCard(21, PlayingCardName.STAND_AND_DELIVER, Suit.FOX, PlayingCardPhase.BIRDSONG, {Suit.MOUSE: 3}),
            PlayingCard(22, PlayingCardName.TAX_COLLECTOR, Suit.FOX, PlayingCardPhase.DAYLIGHT, {Suit.FOX: 1, Suit.RABBIT: 1, Suit.MOUSE: 1}),
            PlayingCard(23, PlayingCardName.TAX_COLLECTOR, Suit.FOX, PlayingCardPhase.DAYLIGHT, {Suit.FOX: 1, Suit.RABBIT: 1, Suit.MOUSE: 1}),
            PlayingCard(24, PlayingCardName.TAX_COLLECTOR, Suit.FOX, PlayingCardPhase.DAYLIGHT, {Suit.FOX: 1, Suit.RABBIT: 1, Suit.MOUSE: 1}),
            PlayingCard(25, PlayingCardName.FAVOR_OF_THE_FOXES, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 3}),

            PlayingCard(26, PlayingCardName.AMBUSH, Suit.RABBIT, PlayingCardPhase.BATTLE),
            PlayingCard(27, PlayingCardName.SMUGGLERS_TRAIL, Suit.RABBIT, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 1, Item.BAG),
            PlayingCard(28, PlayingCardName.ROOT_TEA, Suit.RABBIT, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2, Item.KEG),
            PlayingCard(29, PlayingCardName.A_VISIT_TO_FRIENDS, Suit.RABBIT, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1, Item.BOOTS),
            PlayingCard(30, PlayingCardName.BAKE_SALE, Suit.RABBIT, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 2}, 3, Item.COIN),
            PlayingCard(31, PlayingCardName.COMMAND_WARREN, Suit.RABBIT, PlayingCardPhase.DAYLIGHT, {Suit.RABBIT: 2}),
            PlayingCard(32, PlayingCardName.COMMAND_WARREN, Suit.RABBIT, PlayingCardPhase.DAYLIGHT, {Suit.RABBIT: 2}),
            PlayingCard(33, PlayingCardName.BETTER_BURROW_BANK, Suit.RABBIT, PlayingCardPhase.BIRDSONG, {Suit.RABBIT: 2}),
            PlayingCard(34, PlayingCardName.BETTER_BURROW_BANK, Suit.RABBIT, PlayingCardPhase.BIRDSONG, {Suit.RABBIT: 2}),
            PlayingCard(35, PlayingCardName.COBBLER, Suit.RABBIT, PlayingCardPhase.EVENING, {Suit.RABBIT: 2}),
            PlayingCard(36, PlayingCardName.COBBLER, Suit.RABBIT, PlayingCardPhase.EVENING, {Suit.RABBIT: 2}),
            PlayingCard(37, PlayingCardName.COBBLER, Suit.RABBIT, PlayingCardPhase.EVENING, {Suit.RABBIT: 2}),
            PlayingCard(38, PlayingCardName.FAVOR_OF_THE_RABBITS, Suit.RABBIT, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 3}),

            PlayingCard(39, PlayingCardName.AMBUSH, Suit.MOUSE, PlayingCardPhase.BATTLE),
            PlayingCard(40, PlayingCardName.MOUSE_IN_A_SACK, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 1, Item.BAG),
            PlayingCard(41, PlayingCardName.ROOT_TEA, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2, Item.KEG),
            PlayingCard(42, PlayingCardName.TRAVEL_GEAR, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1, Item.BOOTS),
            PlayingCard(43, PlayingCardName.INVESTMENTS, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 2}, 3, Item.COIN),
            PlayingCard(44, PlayingCardName.SWORD, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2, Item.KNIFE),
            PlayingCard(45, PlayingCardName.CROSSBOW, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}, 1, Item.CROSSBOW),
            PlayingCard(46, PlayingCardName.SCOUTING_PARTY, Suit.MOUSE, PlayingCardPhase.BATTLE, {Suit.MOUSE: 2}),
            PlayingCard(47, PlayingCardName.SCOUTING_PARTY, Suit.MOUSE, PlayingCardPhase.BATTLE, {Suit.MOUSE: 2}),
            # PlayingCard(48, PlayingCardName.CODEBREAKERS, Suit.MOUSE, PlayingCardPhase.DAYLIGHT, {Suit.MOUSE: 1}),
            # PlayingCard(49, PlayingCardName.CODEBREAKERS, Suit.MOUSE, PlayingCardPhase.DAYLIGHT, {Suit.MOUSE: 1}),
            PlayingCard(50, PlayingCardName.FAVOR_OF_THE_MICE, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 3}),

        ]
        self.discard_pile: [PlayingCard] = []

        # Board and Areas
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
        # self.marquise_action = MarquiseActionBoard(Vector2(0.75 * Config.SCREEN_WIDTH, 0.0 * Config.SCREEN_HEIGHT))
        self.eyrie = EyrieBoard("Eyrie Dynasties", Colors.BLUE, 24, Vector2(0, 0.5 * Config.SCREEN_HEIGHT))

    def init(self):
        pass

    def update(self):

        # 1. whose turn is this?
        # 2.

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # if marquise turn
            if self.turn_player == Faction.MARQUISE:
                self.check_event_marquise(event)
            else:
                self.check_event_eyrie(event)
        self.fps = self.calculate_fps()

    def check_event_marquise(self, event: pygame.event.Event):

        # which phase
        phase = 'Daylight'

        if phase == 'Daylight':
            self.marquise.update_phase('Daylight', '1')
            # Place one wood at each sawmill
            for area in self.board.areas:
                area.token_count[Token.WOOD] += area.buildings.count(Building.SAWMILL)

        if event.type == pygame.KEYDOWN:
            self.marquise.move_arrow(event.key)
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
