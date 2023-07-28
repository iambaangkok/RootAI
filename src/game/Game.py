import logging
from copy import copy
from enum import StrEnum
from random import shuffle

import pygame
from pygame import Vector2, Surface, Rect
from pygame.time import Clock

from src.config import Config, Colors
from src.game.Area import Area
from src.game.Board import Board
from src.game.Building import Building
from src.game.EyrieBoard import EyrieBoard, DecreeAction, EyrieLeader
from src.game.Faction import Faction
from src.game.FactionBoard import FactionBoard
from src.game.Item import Item
from src.game.MarquiseBoard import MarquiseBoard
from src.game.PlayingCard import PlayingCard, PlayingCardName, PlayingCardPhase
from src.game.Suit import Suit
from src.game.Token import Token
from src.game.Warrior import Warrior
from src.utils.draw_utils import draw_text_in_rect

LOGGER = logging.getLogger('logger')


class Phase(StrEnum):
    BIRDSONG = "BIRDSONG"
    DAYLIGHT = "DAYLIGHT"
    EVENING = "EVENING"
    TURMOIL = "TURMOIL"


class Action:
    def __init__(self, name: str, function: any = None):
        self.name: str = name
        self.function: any = function


MARQUISE_ACTIONS = {
    Phase.BIRDSONG: [['Next']],
    Phase.DAYLIGHT: [
        ['Craft', 'Next'],
        ['Battle', 'March', 'Recruit', 'Build', 'Overwork', 'Next']
    ],
    Phase.EVENING: [['End']]
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
        self.turn_player: Faction = Faction.EYRIE
        self.phase: Phase = Phase.BIRDSONG
        self.sub_phase = 0
        self.is_in_action_sub_phase: bool = False

        # Board Game Components
        self.draw_pile: list[PlayingCard] = [
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
        self.discard_pile: list[PlayingCard] = []

        # Board, Areas (Clearings)
        areas_offset_y = 0.05
        areas_radius = Board.rect.width * Area.size_ratio
        areas: list[Area] = [
            Area(Vector2(Board.rect.x + Board.rect.width * 0.12, Board.rect.y + Board.rect.height * (0.20 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.EMPTY]),
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

        self.board: Board = Board(areas)

        paths = [(0, 1), (0, 3), (0, 4), (1, 2), (2, 3), (2, 7), (3, 5), (4, 5), (4, 8), (5, 6), (5, 8), (5, 10), (6, 7), (6, 11), (7, 11), (8, 9),
                 (9, 10), (10, 11)]
        for path in paths:
            self.board.add_path(path[0], path[1])

        # Faction Board
        self.marquise = MarquiseBoard("Marquise de Cat", Colors.ORANGE, 14, Vector2(0, 0.0 * Config.SCREEN_HEIGHT))
        self.eyrie = EyrieBoard("Eyrie Dynasties", Colors.BLUE, 24, Vector2(0, 0.5 * Config.SCREEN_HEIGHT))

        # Action Board
        self.action_arrow_pos = Vector2(0, 0)
        self.action_row_width = 16
        self.action_col_width = 100
        self.action_col = 1

        # Actions
        self.marquise_actions: {Phase: [[Action]]} = {
            Phase.BIRDSONG: [[Action('Next', self.marquise_birdsong_next)]],
            Phase.DAYLIGHT: [
                [Action('Craft'), Action('Next')],
                [Action('Battle'), Action('March'), Action('Recruit'), Action('Build'), Action('Overwork'), Action('Next')]
            ],
            Phase.EVENING: [[Action('Next')]]
        }
        self.eyrie_base_actions: {Phase: [[Action]]} = {
            Phase.BIRDSONG: [
                [Action('Next', lambda: self.eyrie_birdsong_1_next())],
                [],
                [Action('Next', lambda: self.eyrie_birdsong_3_next())]],
            Phase.DAYLIGHT: [
                [Action('Next', lambda: self.eyrie_daylight_1_next())],
                [Action('Resolve the Decree'), Action('Next')]
            ],
            Phase.EVENING: [[Action('Next')]]
        }
        self.actions: list[Action] = []
        self.set_actions()

        # # Add Card To Decree variables
        self.selected_card: PlayingCard | None = None
        self.added_bird_card: bool = False
        self.addable_count: int = 2

        self.current_action: Action = self.actions[0]
        self.prompt = "If hand empty, draw 1 card"

        # Setup Game
        self.setup_board()

    #####
    # Setup Board
    def setup_board(self):
        self.board.areas[-1].add_token(Token.CASTLE)

        for i in range(1, len(self.board.areas)):
            self.board.areas[i].add_warrior(Warrior.MARQUIS, 1)

        self.build_roost(self.board.areas[0])
        self.board.areas[0].add_warrior(Warrior.EYRIE, 6)

        # Take Cards
        self.shuffle_draw_pile()
        starting_card_amount: int = 5
        self.take_card_from_draw_pile(Faction.MARQUISE, starting_card_amount)
        self.take_card_from_draw_pile(Faction.EYRIE, starting_card_amount)

    def shuffle_draw_pile(self):
        shuffle(self.draw_pile)

    #####

    def init(self):
        pass

    #####
    # Update
    def update(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                self.move_arrow(event.key)

                # Whose turn is this?
                if event.key == pygame.K_RETURN:
                    if self.turn_player == Faction.MARQUISE:
                        self.check_event_marquise(event)
                    elif self.turn_player == Faction.EYRIE:
                        self.check_event_eyrie(event)

        self.fps = self.calculate_fps()

    def move_arrow(self, direction):
        update_arrow = {
            pygame.K_UP: Vector2(0, -1),
            pygame.K_DOWN: Vector2(0, 1),
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

    #####
    # MARQUISE
    def check_event_marquise(self, event: pygame.event.Event):
        self.current_action.function()

    def other(self):
        action = MARQUISE_ACTIONS[self.phase][self.sub_phase][int(self.action_arrow_pos.x) * self.action_col + int(self.action_arrow_pos.y)]
        move_available_clearing = []
        battle_available_clearing = []
        build_available_clearing = []
        overwork_available = []

        for area in self.board.areas:
            if area.ruler() == Warrior.MARQUIS:
                move_available_clearing.append([(area, connected_area) for connected_area in area.connected_clearings])
                build_available_clearing.append(area)
            else:
                for connected_area in area.connected_clearings:
                    if connected_area.ruler() == Warrior.MARQUIS:
                        move_available_clearing.append((area, connected_area))

            if area.warrior_count[Warrior.MARQUIS] > 0 and area.warrior_count[Warrior.EYRIE] > 0:
                battle_available_clearing.append(area)

            # if area.buildings.count(Building.SAWMILL) > 0 and len(list(filter(lambda x: (x.suit == area.suit), self.marquise.cards_in_hand))) > 0:
            #     overwork_available.append([(area, card) for card in list(filter(lambda x: (x.suit == area.suit), self.marquise.cards_in_hand))])

        # print(move_available_clearing)
        # print(battle_available_clearing)
        # print(build_available_clearing)
        # which phase

        if self.phase == Phase.BIRDSONG:
            # Place one wood at each sawmill
            for area in self.board.areas:
                area.token_count[Token.WOOD] += area.buildings.count(Building.SAWMILL)
            if action == 'Next':
                self.phase = Phase.DAYLIGHT
                self.sub_phase = 0
                self.action_arrow_pos = Vector2(0, 0)
        elif self.phase == Phase.DAYLIGHT:
            if self.sub_phase == 0:
                if action == 'Next':
                    self.sub_phase = 1
                    self.action_arrow_pos = Vector2(0, 0)
            elif self.sub_phase == 1:
                # if action == 'march':
                # elif action == 'battle':
                # elif action == 'recruit':
                # elif action == 'build':
                # elif action == 'overwork':
                # else
                if action == 'Next':
                    self.phase = Phase.EVENING
                    self.sub_phase = 0
                    self.action_arrow_pos = Vector2(0, 0)
        else:
            # Draw card
            if action == 'End':
                self.turn_player = Faction.EYRIE
                self.phase = Phase.DAYLIGHT
                self.sub_phase = 0
                self.action_arrow_pos = Vector2(0, 0)
        # elif phase == 'Daylight':
        # Which phase
        # if self.phase == Phase.BIRDSONG:
        #     if event.type == pygame.K_RETURN:
        #         self.current_action.function()
        #
        # elif self.phase == Phase.DAYLIGHT:
        #     pass
        # daylight
        # move
        # from where
        # to where
        # how many

        pass

    def marquise_birdsong_next(self):
        # Place one wood at each sawmill
        for area in self.board.areas:
            area.token_count[Token.WOOD] += area.buildings.count(Building.SAWMILL)
        # Next phase
        self.phase = Phase.DAYLIGHT

    def get_workshop_count_by_suit(self) -> {Suit: int}:
        workshop_count: {Suit: int} = {
            Suit.BIRD: 0,
            Suit.FOX: 0,
            Suit.RABBIT: 0,
            Suit.MOUSE: 0
        }

        for clearing in self.board.areas:
            if Building.WORKSHOP in clearing.buildings:
                workshop_count[clearing.suit] += clearing.buildings.count(Building.WORKSHOP)

        return workshop_count

    #####
    # Eyrie
    def check_event_eyrie(self, event: pygame.event.Event):
        self.current_action.function()

    def eyrie_birdsong_1_next(self):
        LOGGER.info("{}:{}:{}:next".format(self.turn_player, self.phase, self.sub_phase))

        if len(self.eyrie.cards_in_hand) == 0:
            self.take_card_from_draw_pile(Faction.EYRIE)

        self.sub_phase = 1

        self.prompt = "Select Card To Add To Decree"
        self.set_actions(self.generate_actions_add_card_to_decree())

    def generate_actions_add_card_to_decree(self) -> list[Action]:
        actions: list[Action] = []
        if self.addable_count > 0:
            for card in self.eyrie.cards_in_hand:
                if self.added_bird_card and card.suit == Suit.BIRD:
                    continue
                actions.append(Action('{} ({})'.format(card.name, card.suit), lambda: self.select_card_to_add_to_decree_one(card)))

        return actions

    def select_card_to_add_to_decree_one(self, card: PlayingCard):
        self.select_card(card)

        self.prompt = "Select Decree ({} ({}))".format(card.name, card.suit)
        self.set_actions(self.generate_actions_add_to_decree())

    def generate_actions_add_to_decree(self) -> list[Action]:
        actions: [Action] = []
        for decree_action in DecreeAction:
            actions.append(Action("{}".format(decree_action), lambda: self.select_decree_to_add_card_to(decree_action)))

        return actions

    def select_decree_to_add_card_to(self, decree_action: DecreeAction | str):
        self.eyrie.decree[decree_action].append(self.selected_card)
        self.eyrie.cards_in_hand.remove(self.selected_card)

        self.addable_count -= 1
        if self.selected_card.suit == Suit.BIRD:
            self.added_bird_card = True

        LOGGER.info(
            "{}:{}:{}:Added card '{}' to {} decree".format(self.turn_player, self.phase, self.sub_phase, self.selected_card.name, decree_action))

        if self.addable_count != 0:
            self.prompt = "Select ANOTHER card to add to the Decree"
            self.set_actions(self.generate_actions_add_card_to_decree() + [
                Action("Skip", lambda: self.eyrie_birdsong_2_card_2_skip())
            ])
        else:
            self.eyrie_birdsong_2_to_sub_phase_3()

    def eyrie_birdsong_2_card_2_skip(self):
        LOGGER.info("{}:{}:{}:card_2_skip".format(self.turn_player, self.phase, self.sub_phase))
        self.eyrie_birdsong_2_to_sub_phase_3()

    def eyrie_birdsong_2_to_sub_phase_3(self):
        self.sub_phase = 2
        self.prompt = "If you have no roost, place a roost and 3 warriors in the clearing with the fewest total pieces. (Select Clearing)"

        if self.eyrie.roost_tracker == 0:
            self.set_actions(self.generate_actions_place_roost_and_3_warriors() + [
                self.eyrie_base_actions[self.phase][self.sub_phase][0]
            ])
        else:
            self.set_actions()

    def generate_actions_place_roost_and_3_warriors(self) -> list[Action]:
        actions: [Action] = []
        min_token_areas = [area for area in self.board.get_min_token_areas() if Building.EMPTY in area.buildings]
        for area in min_token_areas:
            actions.append(Action("Area {}".format(area.area_index), lambda: self.place_roost_and_3_warriors(area)))

        return actions

    def place_roost_and_3_warriors(self, area: Area):
        self.add_warrior(Faction.EYRIE, area, 3)
        self.build_roost(area)

    def build_roost(self, area: Area):
        LOGGER.info("{}:{}:{}:{} built {} at area#{}".format(
            self.turn_player, self.phase, self.sub_phase, Faction.EYRIE, Building.ROOST, area.buildings.index(Building.EMPTY)))

        self.eyrie.roost_tracker += 1
        area.buildings[area.buildings.index(Building.EMPTY)] = Building.ROOST

    def eyrie_birdsong_3_next(self):
        LOGGER.info("{}:{}:{}:next".format(self.turn_player, self.phase, self.sub_phase))

        self.phase = Phase.DAYLIGHT
        self.sub_phase = 0

        self.prompt = "Craft Cards"
        self.set_actions()

    def get_roost_count_by_suit(self) -> {Suit: int}:
        roost_count: {Suit: int} = {
            Suit.BIRD: 0,
            Suit.FOX: 0,
            Suit.RABBIT: 0,
            Suit.MOUSE: 0
        }

        for clearing in self.board.areas:
            if Building.ROOST in clearing.buildings:
                roost_count[clearing.suit] += 1

        return roost_count

    def eyrie_daylight_1_next(self):
        LOGGER.info("{}:{}:{}:next".format(self.turn_player, self.phase, self.sub_phase))

        self.sub_phase = 1

        self.prompt = "Resolve the Decree"
        self.set_actions()

    # TODO: eyrie resolve decree
    # TODO: eyrie turmoil

    #####

    def add_warrior(self, faction: Faction, area: Area, amount: int = 1):
        faction_board = self.marquise
        warrior_type = Warrior.MARQUIS
        if faction == Faction.EYRIE:
            faction_board = self.eyrie
            warrior_type = Warrior.EYRIE

        faction_board.reserved_warriors -= amount
        area.add_warrior(warrior_type, amount)

    def generate_actions_craft_cards(self, faction: Faction):
        actions: [Action] = []
        craftable_cards = self.get_craftable_cards(faction)

        if faction == Faction.MARQUISE:
            for card in craftable_cards:
                actions.append(Action("Craft {}".format(card.name), lambda: self.craft_card(faction, card)))
        elif faction == Faction.EYRIE:
            for card in craftable_cards:
                actions.append(Action("Craft {}".format(card.name), lambda: self.craft_card(faction, card)))

        return actions

    def craft_card(self, faction: Faction, card: PlayingCard):
        if faction == Faction.MARQUISE:
            LOGGER.info("{}:{}:{}:Crafted {} card".format(self.turn_player, self.phase, self.sub_phase, card.name))
            if card.phase == PlayingCardPhase.IMMEDIATE:
                self.board.faction_points[0] += card.reward_vp
                self.marquise.items[card.reward_item] += 1
                self.discard_card(self.marquise.cards_in_hand, card)

            self.eyrie.cards_in_hand.remove(card)
            self.eyrie.crafted_cards.append(card)
        elif faction == Faction.EYRIE:
            LOGGER.info("{}:{}:{}:Crafted {} card".format(self.turn_player, self.phase, self.sub_phase, card.name))

            if card.phase == PlayingCardPhase.IMMEDIATE:
                # Gain VP
                if self.eyrie.get_active_leader() == EyrieLeader.BUILDER:
                    self.board.faction_points[1] += card.reward_vp
                else:
                    self.board.faction_points[1] += 1

                # Gain Item
                self.eyrie.items[card.reward_item] += 1

                self.discard_card(self.eyrie.cards_in_hand, card)
            else:
                self.eyrie.cards_in_hand.remove(card)
                self.eyrie.crafted_cards.append(card)

    def get_craftable_cards(self, faction: Faction) -> list[PlayingCard]:
        craftable_cards: list[PlayingCard] = []

        cards_in_hand: list[PlayingCard] = []
        crafting_station: {Suit: int} = {}
        if faction == Faction.MARQUISE:
            cards_in_hand = self.marquise.cards_in_hand
            crafting_station = self.get_workshop_count_by_suit()
        elif faction == Faction.EYRIE:
            cards_in_hand = self.eyrie.cards_in_hand
            crafting_station = self.get_roost_count_by_suit()

        for card in cards_in_hand:
            can_craft = True
            for suit in card.craft_requirement.keys():
                if card.craft_requirement[suit] > crafting_station[suit] or not self.board.item_available(card.reward_item):
                    can_craft = False
                    break
            if can_craft:
                craftable_cards.append(card)

        return craftable_cards

    def select_card(self, card: PlayingCard):
        self.selected_card = card

    def set_actions(self, actions: list[Action] = None):
        if actions is not None:
            self.actions = actions
        else:
            if self.turn_player == Faction.MARQUISE:
                self.actions = self.marquise_actions[self.phase][self.sub_phase]
            elif self.turn_player == Faction.EYRIE:
                self.actions = self.eyrie_base_actions[self.phase][self.sub_phase]
        self.reset_arrow()

    def can_take_card_from_draw_pile(self, amount: int = 1) -> bool:
        return len(self.draw_pile) >= amount

    def take_card_from_draw_pile(self, faction: Faction, amount: int = 1):
        faction_board = self.marquise

        if faction == Faction.EYRIE:
            faction_board = self.eyrie

        if self.can_take_card_from_draw_pile(amount):
            faction_board.cards_in_hand.extend(self.draw_pile[0:amount])
            self.draw_pile = self.draw_pile[amount:]
            LOGGER.info("{}:{}:{}:{} drawn {} card(s)".format(self.turn_player, self.phase, self.sub_phase, faction, amount))

    def discard_card(self, discard_from: list[PlayingCard], card: PlayingCard):
        discard_from.remove(card)
        self.discard_pile.append(card)

    def calculate_fps(self):
        if self.delta_time != 0:
            return 1.0 / self.delta_time
        else:
            return 0.0

    #####
    # GAME LOOP: RENDER
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
        # Phase
        color = Colors.ORANGE
        if self.turn_player == Faction.EYRIE:
            color = Colors.BLUE
        phase = Config.FONT_MD_BOLD.render("{} ({})".format(self.phase, self.sub_phase), True, color)
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
        draw_text_in_rect(screen, "{}".format(self.prompt), Colors.WHITE, prompt_rect, Config.FONT_1, True)

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

    #####
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


