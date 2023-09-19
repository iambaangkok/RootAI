import logging
from copy import copy
from enum import StrEnum
from random import shuffle, randint
from typing import List

import pygame
from pygame import Vector2, Surface, Rect
from pygame.time import Clock

from src.config import Config, Colors
from src.game.Area import Area
from src.game.Board import Board
from src.game.Building import Building
from src.game.EyrieBoard import EyrieBoard, DecreeAction, EyrieLeader, LeaderStatus, LOYAL_VIZIER, \
    count_decree_action_static
from src.game.Faction import Faction
from src.game.FactionBoard import FactionBoard
from src.game.Item import Item
from src.game.MarquiseBoard import MarquiseBoard
from src.game.PlayingCard import PlayingCard, PlayingCardName, PlayingCardPhase
from src.game.Suit import Suit
from src.game.Token import Token
from src.game.Warrior import Warrior
from src.utils.draw_utils import draw_text_in_rect
from src.utils.utils import perform, faction_to_warrior, faction_to_tokens, faction_to_buildings

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

    def get(self):
        return self.name, self.function


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
        self.phase: Phase = Phase.BIRDSONG
        self.sub_phase = 0
        self.is_in_action_sub_phase: bool = False

        # Board Game Components
        self.draw_pile: list[PlayingCard] = [
            PlayingCard(0, PlayingCardName.AMBUSH, Suit.BIRD, PlayingCardPhase.BATTLE),
            PlayingCard(1, PlayingCardName.AMBUSH, Suit.BIRD, PlayingCardPhase.BATTLE),
            PlayingCard(2, PlayingCardName.BIRDY_HANDLE, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 1,
                        Item.BAG),
            PlayingCard(3, PlayingCardName.ARMORERS, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}),
            PlayingCard(4, PlayingCardName.CROSSBOW, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}, 1,
                        Item.CROSSBOW),
            PlayingCard(5, PlayingCardName.WOODLAND_RUNNERS, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1,
                        Item.BOOTS),
            PlayingCard(6, PlayingCardName.ARMS_TRADER, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2,
                        Item.KNIFE),
            PlayingCard(7, PlayingCardName.ARMS_TRADER, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2,
                        Item.KNIFE),
            PlayingCard(8, PlayingCardName.SAPPERS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.MOUSE: 1}),
            PlayingCard(9, PlayingCardName.SAPPERS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.MOUSE: 1}),
            PlayingCard(10, PlayingCardName.BRUTAL_TACTICS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.FOX: 2}),
            PlayingCard(11, PlayingCardName.BRUTAL_TACTICS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.FOX: 2}),
            PlayingCard(12, PlayingCardName.ROYAL_CLAIM, Suit.BIRD, PlayingCardPhase.BIRDSONG, {Suit.BIRD: 4}),

            PlayingCard(13, PlayingCardName.AMBUSH, Suit.FOX, PlayingCardPhase.BATTLE),
            PlayingCard(14, PlayingCardName.GENTLY_USED_KNAPSACK, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1},
                        1, Item.BAG),
            PlayingCard(15, PlayingCardName.ROOT_TEA, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2,
                        Item.KEG),
            PlayingCard(16, PlayingCardName.TRAVEL_GEAR, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1,
                        Item.BOOTS),
            PlayingCard(17, PlayingCardName.PROTECTION_RACKET, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 2},
                        3, Item.COIN),
            PlayingCard(18, PlayingCardName.FOXFOLK_STEEL, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2,
                        Item.KNIFE),
            PlayingCard(19, PlayingCardName.ANVIL, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}, 2, Item.HAMMER),
            PlayingCard(20, PlayingCardName.STAND_AND_DELIVER, Suit.FOX, PlayingCardPhase.BIRDSONG, {Suit.MOUSE: 3}),
            PlayingCard(21, PlayingCardName.STAND_AND_DELIVER, Suit.FOX, PlayingCardPhase.BIRDSONG, {Suit.MOUSE: 3}),
            PlayingCard(22, PlayingCardName.TAX_COLLECTOR, Suit.FOX, PlayingCardPhase.DAYLIGHT,
                        {Suit.FOX: 1, Suit.RABBIT: 1, Suit.MOUSE: 1}),
            PlayingCard(23, PlayingCardName.TAX_COLLECTOR, Suit.FOX, PlayingCardPhase.DAYLIGHT,
                        {Suit.FOX: 1, Suit.RABBIT: 1, Suit.MOUSE: 1}),
            PlayingCard(24, PlayingCardName.TAX_COLLECTOR, Suit.FOX, PlayingCardPhase.DAYLIGHT,
                        {Suit.FOX: 1, Suit.RABBIT: 1, Suit.MOUSE: 1}),
            PlayingCard(25, PlayingCardName.FAVOR_OF_THE_FOXES, Suit.FOX, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 3}),

            PlayingCard(26, PlayingCardName.AMBUSH, Suit.RABBIT, PlayingCardPhase.BATTLE),
            PlayingCard(27, PlayingCardName.SMUGGLERS_TRAIL, Suit.RABBIT, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1},
                        1, Item.BAG),
            PlayingCard(28, PlayingCardName.ROOT_TEA, Suit.RABBIT, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2,
                        Item.KEG),
            PlayingCard(29, PlayingCardName.A_VISIT_TO_FRIENDS, Suit.RABBIT, PlayingCardPhase.IMMEDIATE,
                        {Suit.RABBIT: 1}, 1, Item.BOOTS),
            PlayingCard(30, PlayingCardName.BAKE_SALE, Suit.RABBIT, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 2}, 3,
                        Item.COIN),
            PlayingCard(31, PlayingCardName.COMMAND_WARREN, Suit.RABBIT, PlayingCardPhase.DAYLIGHT, {Suit.RABBIT: 2}),
            PlayingCard(32, PlayingCardName.COMMAND_WARREN, Suit.RABBIT, PlayingCardPhase.DAYLIGHT, {Suit.RABBIT: 2}),
            PlayingCard(33, PlayingCardName.BETTER_BURROW_BANK, Suit.RABBIT, PlayingCardPhase.BIRDSONG,
                        {Suit.RABBIT: 2}),
            PlayingCard(34, PlayingCardName.BETTER_BURROW_BANK, Suit.RABBIT, PlayingCardPhase.BIRDSONG,
                        {Suit.RABBIT: 2}),
            PlayingCard(35, PlayingCardName.COBBLER, Suit.RABBIT, PlayingCardPhase.EVENING, {Suit.RABBIT: 2}),
            PlayingCard(36, PlayingCardName.COBBLER, Suit.RABBIT, PlayingCardPhase.EVENING, {Suit.RABBIT: 2}),
            PlayingCard(37, PlayingCardName.COBBLER, Suit.RABBIT, PlayingCardPhase.EVENING, {Suit.RABBIT: 2}),
            PlayingCard(38, PlayingCardName.FAVOR_OF_THE_RABBITS, Suit.RABBIT, PlayingCardPhase.IMMEDIATE,
                        {Suit.RABBIT: 3}),

            PlayingCard(39, PlayingCardName.AMBUSH, Suit.MOUSE, PlayingCardPhase.BATTLE),
            PlayingCard(40, PlayingCardName.MOUSE_IN_A_SACK, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 1,
                        Item.BAG),
            PlayingCard(41, PlayingCardName.ROOT_TEA, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2,
                        Item.KEG),
            PlayingCard(42, PlayingCardName.TRAVEL_GEAR, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1,
                        Item.BOOTS),
            PlayingCard(43, PlayingCardName.INVESTMENTS, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 2}, 3,
                        Item.COIN),
            PlayingCard(44, PlayingCardName.SWORD, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2,
                        Item.KNIFE),
            PlayingCard(45, PlayingCardName.CROSSBOW, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}, 1,
                        Item.CROSSBOW),
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
            Area(Vector2(Board.rect.x + Board.rect.width * 0.12,
                         Board.rect.y + Board.rect.height * (0.20 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.55,
                         Board.rect.y + Board.rect.height * (0.15 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.EMPTY, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.88,
                         Board.rect.y + Board.rect.height * (0.25 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.EMPTY, Building.EMPTY]),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.43,
                         Board.rect.y + Board.rect.height * (0.35 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.EMPTY]),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.10,
                         Board.rect.y + Board.rect.height * (0.45 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.EMPTY, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.34,
                         Board.rect.y + Board.rect.height * (0.58 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.66,
                         Board.rect.y + Board.rect.height * (0.53 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.EMPTY, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.90,
                         Board.rect.y + Board.rect.height * (0.56 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.WORKSHOP]),

            Area(Vector2(Board.rect.x + Board.rect.width * 0.12,
                         Board.rect.y + Board.rect.height * (0.83 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.39,
                         Board.rect.y + Board.rect.height * (0.88 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.EMPTY, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.62,
                         Board.rect.y + Board.rect.height * (0.80 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.RECRUITER, Building.EMPTY]),
            Area(Vector2(Board.rect.x + Board.rect.width * 0.84,
                         Board.rect.y + Board.rect.height * (0.88 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.SAWMILL]),
        ]

        self.board: Board = Board(areas)

        paths = [(0, 1), (0, 3), (0, 4), (1, 2), (2, 3), (2, 7), (3, 5), (4, 5), (4, 8), (5, 6), (5, 8), (5, 10),
                 (6, 7), (6, 11), (7, 11), (8, 9),
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
        self.marquise_base_actions: {Phase: [[Action]]} = {
            Phase.BIRDSONG: [[Action('Next', perform(self.marquise_birdsong_next))]],
            Phase.DAYLIGHT: [
                [Action('Craft', perform(self.marquise_daylight_craft)),
                 Action('Next', perform(self.marquise_daylight_1_next))],
                [Action('Battle'), Action('March', perform(self.marquise_daylight_march_move_from)), Action('Recruit'),
                 Action('Build'),
                 Action('Overwork'),
                 Action('Next', perform(self.marquise_daylight_2_next))]
            ],
            Phase.EVENING: [[Action('End turn', perform(self.marquise_evening_next))]]
        }
        self.eyrie_base_actions: {Phase: [[Action]]} = {
            Phase.BIRDSONG: [
                [Action('Next', perform(self.marquise_evening_next))],
                [],
                [Action('Next', perform(self.eyrie_birdsong_3_next))]],
            Phase.DAYLIGHT: [
                [Action('Next', perform(self.eyrie_daylight_1_next))],
                [Action('Resolve the Decree'), Action('Next')]
            ],
            Phase.EVENING: [[Action('Next')]]
        }
        self.actions: list[Action] = []
        self.set_actions()

        # Marquise variables
        self.marquise_action_count = 3
        self.marquise_recruit_action_used = False

        # # Add Card To Decree variables
        self.selected_card: PlayingCard | None = None
        self.added_bird_card: bool = False
        self.addable_count: int = 2

        # # Resolve Decree variables
        self.decree_counter: {DecreeAction: list[PlayingCard]} = {
            DecreeAction.RECRUIT: [],
            DecreeAction.MOVE: [],
            DecreeAction.BATTLE: [],
            DecreeAction.BUILD: []
        }

        self.current_action: Action = self.actions[0]
        self.prompt = "If hand empty, draw 1 card"

        # Setup Game
        self.setup_board()

    #####
    # Setup Board
    def setup_board(self):
        self.board.areas[-1].add_token(Token.CASTLE)

        for i in range(1, len(self.board.areas)):
            self.board.areas[i].add_warrior(Warrior.MARQUISE, 1)

        self.build_roost(self.board.areas[0])
        self.board.areas[0].add_warrior(Warrior.EYRIE, 6)
        self.activate_leader(EyrieLeader.CHARISMATIC)

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

    #####
    # MARQUISE
    def check_event_marquise(self, event: pygame.event.Event):
        self.current_action.function()

    def marquise_birdsong_next(self):
        # set marquise action count to 3
        self.marquise_action_count = 3
        # Place one wood at each sawmill
        for area in self.board.areas:
            area.token_count[Token.WOOD] += area.buildings.count(Building.SAWMILL)
        # Next phase
        self.marquise.workshop_count = self.get_workshop_count_by_suit()

        self.phase = Phase.DAYLIGHT
        self.prompt = "Want to craft something, squire?"

        craftable_cards = self.generate_actions_craft_cards(Faction.MARQUISE)

        if not craftable_cards:
            self.set_actions([Action('Nope', perform(self.marquise_daylight_1_next))])
        else:
            self.set_actions()

    def marquise_daylight_craft(self):
        self.prompt = "What cards do you want to craft?"
        self.set_actions(self.generate_actions_craft_cards(Faction.MARQUISE) + [
            Action('Next', perform(self.marquise_daylight_1_next))])

    def marquise_daylight_1_next(self):
        actions = []
        self.prompt = "Select Actions (Remaining Action: {})".format(self.marquise_action_count)
        self.sub_phase = 1

        if self.marquise_action_count == 0:
            self.prompt = "No action remaining. Proceed to next phase.".format(self.marquise_action_count)
            if self.marquise_hawks_for_hire_check():
                self.prompt = "No action remaining. Discard BIRD suit card to gain extra action.".format(
                    self.marquise_action_count)
                actions.append(Action('Hawks for hire (discard BIRD suit card to gain extra action)',
                                      perform(self.marquise_daylight_hawks_for_hire_select_card)))
        else:
            if self.marquise_march_check():
                actions.append(Action('March', perform(self.marquise_daylight_march_move_from)))
            if self.marquise_build_check():
                actions.append(Action('Build', perform(self.marquise_daylight_build_select_clearing)))
            if self.marquise_recruit_check():
                actions.append(Action('Recruit', perform(self.marquise_daylight_recruit)))
            if self.marquise_overwork_check():
                actions.append(Action('Overwork', perform(self.marquise_daylight_overwork_1)))
            if self.marquise_battle_check():
                actions.append(Action('Battle', perform(self.marquise_daylight_battle_1)))

        actions.append(Action('Next', perform(self.marquise_daylight_2_next)))
        self.set_actions(actions)

    def marquise_hawks_for_hire_check(self):
        return len([card for card in self.marquise.cards_in_hand if card.suit == Suit.BIRD]) > 0

    def marquise_march_check(self):
        return len(self.find_available_source_clearings(Faction.MARQUISE)) > 0

    def marquise_build_check(self):
        return len(self.get_buildable_clearing(Faction.MARQUISE)) > 0

    def marquise_recruit_check(self):
        return self.count_buildings(Building.RECRUITER) > 0

    def marquise_overwork_check(self):
        return len(self.find_available_overwork_clearings()) > 0

    def marquise_battle_check(self):
        return len(self.get_battlable_clearing(Faction.MARQUISE)) > 0

    def marquise_daylight_hawks_for_hire_select_card(self):
        self.prompt = "Select card to discard"
        self.set_actions(self.generate_actions_select_card_hawks_for_hire())

    def marquise_daylight_march_move_from(self):
        self.prompt = "Let's march. Choose area to move from."
        self.set_actions(self.generate_actions_select_src_clearing(Faction.MARQUISE))

    def marquise_daylight_march_move_to(self, faction, src):
        self.prompt = "Choose area to move to."
        self.set_actions(self.generate_actions_select_dest_clearing(faction, src))

    def marquise_daylight_march_select_warriors(self, faction, src, dest):
        self.prompt = "Choose number of warriors to move."
        self.set_actions(self.generate_actions_select_warriors(faction, src, dest))

    def marquise_daylight_build_select_clearing(self):
        self.prompt = "Let's build. Select clearing"
        self.set_actions(self.generate_actions_select_buildable_clearing(Faction.MARQUISE))

    def marquise_daylight_build_select_building(self, clearing):
        self.prompt = "Select Building"
        self.set_actions(self.generate_actions_select_building(Faction.MARQUISE, clearing))

    def marquise_daylight_recruit(self):
        self.recruit(Faction.MARQUISE)
        self.prompt = "The Marquise warriors are coming to town."
        self.marquise_action_count -= 1
        self.set_actions([Action('Next', self.marquise_daylight_1_next)])

    def marquise_daylight_battle_1(self):  # TODO: Refactor Battle Method
        self.prompt = "Select Clearing"
        self.set_actions(self.generate_actions_select_clearing_battle(Faction.MARQUISE))

    def marquise_daylight_battle_2(self, clearing):  # TODO: Refactor Battle Method
        self.prompt = "Select Faction"
        self.set_actions(self.generate_actions_select_faction_battle(Faction.MARQUISE, clearing))

    def marquise_daylight_overwork_1(self):
        self.prompt = "Select Clearing"
        self.set_actions(self.generate_actions_select_clearing_overwork())

    def marquise_daylight_overwork_2(self, clearing):
        self.prompt = "Select Card"
        self.set_actions(self.generate_actions_select_card_overwork(clearing))

    def marquise_overwork(self, clearing, card):
        self.discard_card(self.marquise.cards_in_hand, card)
        clearing.token_count[Token.WOOD] += 1

        self.prompt = "Overwork: Done"
        self.marquise_action_count -= 1
        self.set_actions([Action('Next', self.marquise_daylight_1_next)])

    def marquise_daylight_2_next(self):  # TODO: Draw cards
        self.prompt = "Draw one card, plus one card per draw bonus"
        number_of_card_to_be_drawn = self.marquise.get_reward_card() + 1
        self.take_card_from_draw_pile(Faction.MARQUISE, number_of_card_to_be_drawn)

        self.phase = Phase.EVENING
        self.sub_phase = 0
        self.set_actions()

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

    def count_woods_from_clearing(self, clearing):
        return self.marquise_bfs_count_wood(clearing)

    def marquise_bfs_count_wood(self, clearing: Area):
        visited = []
        queue: list[Area] = [clearing]

        total_wood = 0

        while queue:
            u = queue.pop(0)
            if u in visited:
                continue
            visited.append(u)
            total_wood += u.token_count[Token.WOOD]

            for v in u.connected_clearings:
                if v.ruler() == Warrior.MARQUISE:
                    queue.append(v)

        return visited, total_wood

    def marquise_get_min_cost_building(self):
        cost = self.marquise.building_cost
        building_tracker = self.marquise.building_trackers

        min_cost = float('inf')

        for building, tracker in building_tracker.items():
            min_cost = min(cost[tracker], min_cost)

        return min_cost

    def remove_wood(self, number, order):
        remaining_wood = number
        for clearing in order:
            remaining_wood = self.remove_wood_from_clearing(clearing, remaining_wood)
            if remaining_wood == 0:
                break

    def remove_wood_from_clearing(self, clearing, number):  # TODO
        remaining_wood = max(number - clearing.token_count[Token.WOOD], 0)
        clearing.token_count[Token.WOOD] -= (
            min(number, clearing.token_count[Token.WOOD]))
        return remaining_wood

    def find_available_overwork_clearings(self) -> list[Area]:
        clearings_with_sawmill: list[Area] = [clearing for clearing in filter(self.sawmill_clearing, self.board.areas)]
        card_suit_list = set([card.suit for card in self.marquise.cards_in_hand])
        return [clearing for clearing in clearings_with_sawmill if clearing.suit in card_suit_list]

    def sawmill_clearing(self, area):
        return area.buildings.count(Building.SAWMILL) > 0

    def generate_actions_select_clearing_overwork(self):
        available_clearing = self.find_available_overwork_clearings()
        actions: list[Action] = []

        for clearing in available_clearing:
            actions.append(
                Action("{}".format(clearing.area_index),
                       perform(self.marquise_daylight_overwork_2, clearing)))

        return actions

    def generate_actions_select_card_overwork(self, clearing):
        discardable_card = [card for card in self.marquise.cards_in_hand if card.suit == clearing.suit]
        actions: list[Action] = []

        for card in discardable_card:
            actions.append(Action('{} ({})'.format(card.name, card.suit),
                                  perform(self.marquise_overwork, clearing, card)))

        return actions

    def generate_actions_select_card_hawks_for_hire(self):
        cards = [card for card in self.marquise.cards_in_hand if card.suit == Suit.BIRD]
        actions: list[Action] = []

        for card in cards:
            actions.append(Action('{} ({})'.format(card.name, card.suit),
                                  perform(self.marquise_hawks_for_hire, card)))

        return actions

    def marquise_hawks_for_hire(self, card):
        self.discard_card(self.marquise.cards_in_hand, card)
        self.marquise_action_count += 1

        self.prompt = "Gain 1 extra action."
        self.set_actions([Action('Next', self.marquise_daylight_1_next)])

    #####
    # Eyrie
    def check_event_eyrie(self, event: pygame.event.Event):
        self.current_action.function()

    def marquise_evening_next(self):
        self.turn_player = Faction.EYRIE
        self.phase = Phase.BIRDSONG
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
                actions.append(Action('{} ({})'.format(card.name, card.suit),
                                      perform(self.select_card_to_add_to_decree_one, card)))

        return actions

    def select_card_to_add_to_decree_one(self, card: PlayingCard):
        self.select_card(card)

        self.prompt = "Select Decree ({} ({}))".format(card.name, card.suit)
        self.set_actions(self.generate_actions_add_to_decree())

    def generate_actions_add_to_decree(self) -> list[Action]:
        actions: list[Action] = []
        for decree_action in DecreeAction:
            actions.append(
                Action("{}".format(decree_action), perform(self.select_decree_to_add_card_to, decree_action)))

        return actions

    def select_decree_to_add_card_to(self, decree_action: DecreeAction | str):
        self.eyrie.decree[decree_action].append(self.selected_card)
        self.eyrie.cards_in_hand.remove(self.selected_card)

        self.addable_count -= 1
        if self.selected_card.suit == Suit.BIRD:
            self.added_bird_card = True

        LOGGER.info(
            "{}:{}:{}:Added card '{}' to {} decree".format(self.turn_player, self.phase, self.sub_phase,
                                                           self.selected_card.name, decree_action))

        if self.addable_count != 0:
            self.prompt = "Select ANOTHER card to add to the Decree"
            self.set_actions(self.generate_actions_add_card_to_decree() + [
                Action("Skip", perform(self.eyrie_birdsong_2_card_2_skip))
            ])
        else:
            self.eyrie_birdsong_2_to_sub_phase_3()

    def eyrie_birdsong_2_card_2_skip(self):
        LOGGER.info("{}:{}:{}:card_2_skip".format(self.turn_player, self.phase, self.sub_phase))
        self.eyrie_birdsong_2_to_sub_phase_3()

    def eyrie_birdsong_2_to_sub_phase_3(self):
        self.sub_phase = 2
        self.prompt = """
            If you have no roost, place a roost and 3 warriors in 
            the clearing with the fewest total pieces. (Select Clearing)
        """

        if self.eyrie.roost_tracker == 0:
            self.set_actions(self.generate_actions_place_roost_and_3_warriors() + [
                self.eyrie_base_actions[self.phase][self.sub_phase][0]
            ])
        else:
            self.set_actions()

    def generate_actions_place_roost_and_3_warriors(self) -> list[Action]:
        actions: list[Action] = []
        min_token_areas = [area for area in self.board.get_min_token_areas() if Building.EMPTY in area.buildings]
        for area in min_token_areas:
            actions.append(Action("Area {}".format(area.area_index), perform(self.place_roost_and_3_warriors, area)))

        return actions

    def place_roost_and_3_warriors(self, area: Area):
        self.add_warrior(Faction.EYRIE, area, 3)
        self.build_roost(area)

    def build_roost(self, area: Area):
        LOGGER.info("{}:{}:{}:{} built {} at area#{}".format(
            self.turn_player, self.phase, self.sub_phase, Faction.EYRIE, Building.ROOST,
            area.buildings.index(Building.EMPTY)))

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

        self.decree_counter = copy(self.eyrie.decree)
        self.update_prompt_eyrie_decree(DecreeAction.RECRUIT)
        self.set_actions(self.generate_actions_eyrie_recruit())

    def update_prompt_eyrie_decree(self, decree_action: DecreeAction):
        self.prompt = "Resolve the Decree: {} BIRD/FOX/RABBIT/MOUSE {}/{}/{}/{}".format(
            decree_action,
            count_decree_action_static(self.decree_counter, decree_action, Suit.BIRD),
            count_decree_action_static(self.decree_counter, decree_action, Suit.FOX),
            count_decree_action_static(self.decree_counter, decree_action, Suit.RABBIT),
            count_decree_action_static(self.decree_counter, decree_action, Suit.MOUSE)
        )

    def generate_actions_eyrie_recruit(self) -> list[Action]:
        actions: list[Action] = []

        decree_action = DecreeAction.RECRUIT

        can_recruit: {Suit: bool} = {}
        for suit in Suit:
            can_recruit[suit] = count_decree_action_static(self.decree_counter, decree_action, suit)

        for area in self.board.areas:
            if Building.ROOST in area.buildings and (can_recruit[Suit.BIRD] or can_recruit[area.suit]):
                actions.append(Action("Recruit in area {}".format(area.area_index), perform(self.eyrie_recruit, area)))

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                # TODO: turmoil
                actions.append(Action("Turmoil"))
            else:
                actions.append(Action("Next", self.eyrie_recruit_next))

        return actions

    def eyrie_recruit(self, area: Area):
        decree_action = DecreeAction.RECRUIT
        self.recruit(Faction.EYRIE, area)
        self.decree_counter[decree_action].remove(
            self.get_decree_card_to_use(decree_action, area.suit)
        )
        LOGGER.info(
            "{}:{}:{}:{} recruited in area {}".format(self.turn_player, self.phase, self.sub_phase, Faction.EYRIE,
                                                      area.area_index))

        self.update_prompt_eyrie_decree(decree_action)
        self.set_actions(self.generate_actions_eyrie_recruit())

    def eyrie_recruit_next(self):
        LOGGER.info("{}:{}:{}:recruit_next".format(self.turn_player, self.phase, self.sub_phase))
        self.update_prompt_eyrie_decree(DecreeAction.MOVE)
        self.set_actions(self.generate_actions_eyrie_move())

    def generate_actions_eyrie_move(self) -> list[Action]:
        actions: list[Action] = self.generate_actions_select_src_clearing(Faction.EYRIE)

        decree_action = DecreeAction.MOVE

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                # TODO: turmoil
                actions.append(Action("Turmoil"))
            else:
                # TODO: next, to BATTLE
                actions.append(Action("Next", self.eyrie_move_next))

        return actions

    def eyrie_choose_move_from(self, faction, src):
        LOGGER.info("{}:{}:{}:eyrie_choose_move_from area {}".format(self.turn_player, self.phase, self.sub_phase, src))

        self.update_prompt_eyrie_decree(DecreeAction.MOVE)
        self.prompt += " Choose area to move to."
        self.set_actions(self.generate_actions_select_dest_clearing(faction, src))

    def eyrie_choose_move_to(self, faction, src, dest):
        LOGGER.info(
            "{}:{}:{}:eyrie_choose_move_to area {}".format(self.turn_player, self.phase, self.sub_phase, src, dest))

        self.update_prompt_eyrie_decree(DecreeAction.MOVE)
        self.prompt += " Choose number of warriors to move."
        self.set_actions(self.generate_actions_select_warriors(faction, src, dest))

    def eyrie_move_next(self):
        LOGGER.info("{}:{}:{}:move_next".format(self.turn_player, self.phase, self.sub_phase))
        self.update_prompt_eyrie_decree(DecreeAction.BATTLE)
        self.prompt += " Choose area to battle in."

        self.set_actions(self.generate_actions_eyrie_battle())

    def generate_actions_eyrie_battle(self) -> list[Action]:
        actions: list[Action] = self.generate_actions_select_clearing_battle(Faction.EYRIE)

        decree_action = DecreeAction.BATTLE

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                # TODO: turmoil
                actions.append(Action("Turmoil"))
            else:
                # TODO: next, to BUILD
                actions.append(Action("Next"))

        return actions

    def eyrie_choose_battle_in(self, clearing: Area):
        LOGGER.info(
            "{}:{}:{}:eyrie_choose_battle_in area {}".format(self.turn_player, self.phase, self.sub_phase, clearing))

        self.update_prompt_eyrie_decree(DecreeAction.BATTLE)
        self.prompt += " Choose enemy faction to battle."
        self.set_actions(self.generate_actions_select_faction_battle(Faction.EYRIE, clearing))

    # TODO: eyrie resolve decree: BATTLE, BUILD
    # TODO: eyrie turmoil

    def get_decree_card_to_use(self, decree_action: DecreeAction, suit: Suit) -> PlayingCard:
        eligible_cards = [card for card in self.decree_counter[decree_action] if card.suit == suit]
        bird_cards = [card for card in self.decree_counter[decree_action] if card.suit == Suit.BIRD]
        if len(eligible_cards) > 0:
            return eligible_cards[0]
        else:
            return bird_cards[0]

    def activate_leader(self, leader: EyrieLeader):
        if self.eyrie.activate_leader(leader):
            LOGGER.info(
                "{}:{}:{}:{} selected as new leader".format(self.turn_player, self.phase, self.sub_phase, leader))

    #####
    # Neutral

    def add_warrior(self, faction: Faction, area: Area, amount: int = 1):
        faction_board = self.marquise
        warrior_type = Warrior.MARQUISE
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
                actions.append(Action('{} ({})'.format(card.name, card.suit), perform(self.craft_card, faction, card)))
        elif faction == Faction.EYRIE:
            for card in craftable_cards:
                actions.append(Action('{} ({})'.format(card.name, card.suit), perform(self.craft_card, faction, card)))

        return actions

    def craft_card(self, faction: Faction, card: PlayingCard):
        if faction == Faction.MARQUISE:
            LOGGER.info("{}:{}:{}:Crafted {} card".format(self.turn_player, self.phase, self.sub_phase, card.name))
            if card.phase == PlayingCardPhase.IMMEDIATE:
                self.board.faction_points[Faction.MARQUISE] += card.reward_vp
                if card.reward_item is not None:
                    self.marquise.items[card.reward_item] += 1
                self.discard_card(self.marquise.cards_in_hand, card)
            else:
                self.discard_card(self.marquise.cards_in_hand, card)
                self.marquise.crafted_cards.append(card)

            for requirement in card.craft_requirement:
                self.marquise.workshop_count[requirement] -= 1

            self.prompt = "{} has been crafted.".format(card.name)
            self.set_actions([Action("Next", self.marquise_daylight_craft)])

        elif faction == Faction.EYRIE:
            LOGGER.info("{}:{}:{}:Crafted {} card".format(self.turn_player, self.phase, self.sub_phase, card.name))

            if card.phase == PlayingCardPhase.IMMEDIATE:
                # Gain VP
                if self.eyrie.get_active_leader() == EyrieLeader.BUILDER:
                    self.board.faction_points[Warrior.EYRIE] += card.reward_vp
                else:
                    self.board.faction_points[Warrior.EYRIE] += 1

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
            crafting_station = self.marquise.workshop_count
        elif faction == Faction.EYRIE:
            cards_in_hand = self.eyrie.cards_in_hand
            crafting_station = self.get_roost_count_by_suit()

        for card in cards_in_hand:
            can_craft = True
            if card.craft_requirement is None:
                continue
            for suit in card.craft_requirement.keys():
                if card.craft_requirement[suit] > crafting_station[suit]:
                    can_craft = False
                elif (card.reward_item is not None) and (not self.board.item_available(card.reward_item)):
                    can_craft = False
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
                self.actions = self.marquise_base_actions[self.phase][self.sub_phase]
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
            LOGGER.info(
                "{}:{}:{}:{} drawn {} card(s)".format(self.turn_player, self.phase, self.sub_phase, faction, amount))

    def discard_card(self, discard_from: list[PlayingCard], card: PlayingCard):
        discard_from.remove(card)
        self.discard_pile.append(card)

    def generate_actions_select_src_clearing(self, faction) -> list[Action]:
        movable_clearings = self.find_available_source_clearings(faction)
        actions = []

        if faction == Faction.MARQUISE:
            for movable_clearing in movable_clearings:
                actions.append(
                    Action("{}".format(movable_clearing),
                           perform(self.marquise_daylight_march_move_to, faction, movable_clearing)))

            return actions
        elif faction == Faction.EYRIE:
            for movable_clearing in movable_clearings:
                actions.append(
                    Action("{}".format(movable_clearing),
                           perform(self.eyrie_choose_move_from, faction, movable_clearing)))
            return actions

    def generate_actions_select_dest_clearing(self, faction, src) -> list[Action]:
        dests = self.find_available_destination_clearings(faction, src)
        actions = []

        if faction == Faction.MARQUISE:
            for dest in dests:
                actions.append(
                    Action("{}".format(dest),
                           perform(self.marquise_daylight_march_select_warriors, faction, src, dest)))

        elif faction == Faction.EYRIE:
            for dest in dests:
                actions.append(
                    Action("{}".format(dest),
                           perform(self.eyrie_choose_move_to, faction, src, dest)))

        return actions

    def generate_actions_select_warriors(self, faction, src: Area, dest: Area) -> list[Action]:
        actions = []

        if faction == Faction.MARQUISE:
            for num_of_warriors in range(1, src.warrior_count[Warrior.MARQUISE] + 1):
                actions.append(Action("{}".format(num_of_warriors),
                                      perform(self.move_warriors, faction, src, dest, num_of_warriors)))

        elif faction == Faction.EYRIE:
            for num_of_warriors in range(1, src.warrior_count[Warrior.EYRIE] + 1):
                actions.append(Action("{}".format(num_of_warriors),
                                      perform(self.move_warriors, faction, src, dest, num_of_warriors)))

        return actions

    def move_warriors(self, faction, src: Area, dest: Area, num):
        LOGGER.info(
            "{}:{}:{}:{} move {} warrior(s) from Clearing #{} to Clearing #{}".format(self.turn_player, self.phase,
                                                                                      self.sub_phase, self.turn_player,
                                                                                      num, src,
                                                                                      dest))

        if faction == Faction.MARQUISE:
            src.remove_warrior(Warrior.MARQUISE, num)
            dest.add_warrior(Warrior.MARQUISE, num)

            self.prompt = "The warriors has been moved."
            self.marquise_action_count -= 1
            self.set_actions([Action('Next', perform(self.marquise_daylight_1_next))])
        elif faction == Faction.EYRIE:
            src.remove_warrior(Warrior.EYRIE, num)
            dest.add_warrior(Warrior.EYRIE, num)
            decree_action = DecreeAction.MOVE

            self.decree_counter[decree_action].remove(
                self.get_decree_card_to_use(decree_action, src.suit)
            )

            self.update_prompt_eyrie_decree(decree_action)
            self.set_actions(self.generate_actions_eyrie_recruit())

            self.eyrie_recruit_next()

    def find_available_source_clearings(self, faction: Faction):
        movable_clearings = []

        if faction == Faction.MARQUISE:
            for area in self.board.areas:
                if area.ruler() == Warrior.MARQUISE:
                    movable_clearings.append(area)
                else:
                    for connected_area in area.connected_clearings:
                        if area.warrior_count[Warrior.MARQUISE] > 0 and connected_area.ruler() == Warrior.MARQUISE:
                            movable_clearings.append(area)
                            break
        elif faction == Faction.EYRIE:
            decree_can_move_from: {Suit: bool} = {}
            for suit in Suit:
                decree_can_move_from[suit] = count_decree_action_static(self.decree_counter, DecreeAction.MOVE, suit)

            for area in self.board.areas:
                if decree_can_move_from[area.suit] == 0 and decree_can_move_from[Suit.BIRD] == 0:
                    continue
                if area.ruler() == Warrior.EYRIE:
                    movable_clearings.append(area)
                else:
                    for connected_area in area.connected_clearings:
                        if area.warrior_count[Warrior.EYRIE] > 0 and connected_area.ruler() == Warrior.EYRIE:
                            movable_clearings.append(area)
                            break

        return movable_clearings

    def find_available_destination_clearings(self, faction: Faction, src: Area):
        dests = []

        if faction == Faction.MARQUISE:
            if src.ruler() == Warrior.MARQUISE:
                for connect_area in src.connected_clearings:
                    dests.append(connect_area)
            else:
                for connect_area in src.connected_clearings:
                    if connect_area.ruler() == Warrior.MARQUISE:
                        dests.append(connect_area)

        elif faction == Faction.EYRIE:
            if src.ruler() == Warrior.EYRIE:
                for connect_area in src.connected_clearings:
                    dests.append(connect_area)
            else:
                for connect_area in src.connected_clearings:
                    if connect_area.ruler() == Warrior.EYRIE:
                        dests.append(connect_area)

        return dests

    def recruit(self, faction: Faction, area: Area = None):
        if faction == Faction.MARQUISE:
            for area in self.board.areas:
                total_recruiters = area.buildings.count(Building.RECRUITER)
                if total_recruiters > 0:
                    self.add_warrior(faction, area, min(total_recruiters, self.marquise.reserved_warriors))
                    LOGGER.info(
                        "{}:{}:{}:MARQUISE adds warrior in clearing #{}".format(self.turn_player, self.phase,
                                                                                self.sub_phase,
                                                                                area.area_index))
        elif faction == Faction.EYRIE:
            amount = 1
            if self.eyrie.get_active_leader() == EyrieLeader.CHARISMATIC:
                amount = 2
            if self.eyrie.reserved_warriors >= amount:
                self.add_warrior(faction, area, amount)

    def generate_actions_select_buildable_clearing(self, faction):
        clearings = self.get_buildable_clearing(faction)
        actions = []

        if faction == Faction.MARQUISE:
            for clearing in clearings:
                actions.append(
                    Action("{}".format(clearing),
                           perform(self.marquise_daylight_build_select_building, clearing)))

        elif faction == Faction.EYRIE:
            pass

        return actions

    def generate_actions_select_building(self, faction, clearing):
        buildings = self.get_buildable_building(faction, clearing)
        actions = []

        if faction == Faction.MARQUISE:
            for building in buildings:
                actions.append(
                    Action("{}".format(building),
                           perform(self.build, faction, clearing, building)))
        elif faction == Faction.EYRIE:
            pass

        return actions

    def build(self, faction, clearing: Area, building):
        if faction == Faction.MARQUISE:
            ind = clearing.buildings.index(Building.EMPTY)
            clearing.buildings[ind] = building

            self.board.gain_vp(Faction.MARQUISE, self.marquise.get_reward(building))
            wood_cost = self.marquise.build_action_update(building)

            self.remove_wood(wood_cost, self.count_woods_from_clearing(clearing)[0])

            LOGGER.info(
                "{}:{}:{}:MARQUISE builds {} in clearing #{}".format(self.turn_player, self.phase, self.sub_phase,
                                                                     building, clearing.area_index))
            self.prompt = "The {} has been build at clearing #{}.".format(building, clearing.area_index)
            self.marquise_action_count -= 1
            self.set_actions([Action('Next', perform(self.marquise_daylight_1_next))])
        elif faction == Faction.EYRIE:
            pass

    def get_buildable_clearing(self, faction):
        buildable_clearing = []

        if faction == Faction.MARQUISE:
            for clearing in self.board.areas:
                if clearing.ruler() == Warrior.MARQUISE and clearing.buildings.count(
                        Building.EMPTY) > 0 and self.marquise_get_min_cost_building() <= \
                        self.count_woods_from_clearing(clearing)[1]:
                    buildable_clearing.append(clearing)
            return buildable_clearing
        elif faction == Faction.EYRIE:
            pass

    def get_buildable_building(self, faction, clearing):
        buildings = []

        if faction == Faction.MARQUISE:
            woods = self.count_woods_from_clearing(clearing)[1]
            cost = self.marquise.building_cost
            building_tracker = self.marquise.building_trackers

            for building, tracker in building_tracker.items():
                if woods >= cost[tracker]:
                    buildings.append(building)

            return buildings
        elif faction == Faction.EYRIE:
            pass

    def count_buildings(self, building):
        total = 0
        for area in self.board.areas:
            total += area.buildings.count(building)
        return total

    def generate_actions_select_clearing_battle(self, faction) -> list[Action]:
        clearings = self.get_battlable_clearing(faction)
        actions = []

        if faction == Faction.MARQUISE:
            for clearing in clearings:
                # TODO: if
                actions.append(
                    Action("{}".format(clearing),
                           perform(self.marquise_daylight_battle_2, clearing)))
        elif faction == Faction.EYRIE:
            for clearing in clearings:
                actions.append(
                    Action("{}".format(clearing),
                           perform(self.eyrie_choose_battle_in, clearing)))
        return actions

    def generate_actions_select_faction_battle(self, faction: Faction, clearing: Area) -> list[Action]:
        enemy_factions: list[Faction] = self.get_available_enemy_tokens_from_clearing(faction, clearing)
        actions: list[Action] = []

        if faction == Faction.MARQUISE:
            for enemy_faction in enemy_factions:
                actions.append(
                    Action("{}".format(enemy_faction),
                           perform(self.battle, faction, clearing, enemy_faction)))

        elif faction == Faction.EYRIE:
            for enemy_faction in enemy_factions:
                actions.append(
                    Action("{}".format(enemy_faction),
                           perform(self.battle, faction, clearing, enemy_faction)))

        return actions

    def get_battlable_clearing(self, faction):
        clearings = []
        if faction == Faction.MARQUISE:
            for area in self.board.areas:
                total_enemy_warriors = area.warrior_count[Warrior.EYRIE] + area.warrior_count[Warrior.ALLIANCE] + \
                                       area.warrior_count[Warrior.VAGABOND]
                total_enemy_buildings = area.buildings.count(Building.ROOST)
                if area.warrior_count[
                    Warrior.MARQUISE] > 0 and total_enemy_warriors + total_enemy_buildings > 0:
                    clearings.append(area)
        elif faction == Faction.EYRIE:
            decree_can_battle_in: {Suit: bool} = {}
            for suit in Suit:
                decree_can_battle_in[suit] = count_decree_action_static(self.decree_counter, DecreeAction.BATTLE, suit)

            for area in self.board.areas:
                if decree_can_battle_in[area.suit] == 0 and decree_can_battle_in[Suit.BIRD] == 0:
                    continue
                if area.warrior_count[Warrior.EYRIE] == 0:
                    continue
                if area.warrior_count[Warrior.MARQUISE] + area.warrior_count[Warrior.ALLIANCE] + area.warrior_count[
                    Warrior.VAGABOND] == 0:
                    continue

                clearings.append(area)

        return clearings

    def get_available_enemy_tokens_from_clearing(self, faction: Faction, clearing: Area) -> list[Faction]:
        factions: list[Faction] = []
        our_warrior = faction_to_warrior(faction)

        for enemy_faction in Faction:

            enemy_warrior = faction_to_warrior(Faction[enemy_faction])
            if enemy_warrior == our_warrior:
                continue

            enemy_tokens = faction_to_tokens(Faction[enemy_faction])
            enemy_buildings = faction_to_buildings(Faction[enemy_faction])

            enemy_warrior_count = clearing.get_warrior_count(enemy_warrior)
            enemy_tokens_count = clearing.get_tokens_count(enemy_tokens)
            enemy_buildings_count = clearing.get_buildings_count(enemy_buildings)

            if enemy_warrior_count + enemy_tokens_count + enemy_buildings_count == 0:
                continue
            factions.append(Faction[enemy_faction])

        return factions

    def battle(self, attacker: Faction, clearing: Area, defender: Faction):
        # TODO: ambush and foil ambush logic

        attacker_faction_board = self.faction_to_faction_board(attacker)
        defender_faction_board = self.faction_to_faction_board(defender)

        # roll dice and add extra hits
        dices: list[int] = [randint(0, 4), randint(0, 4)]
        attacker_roll: int = max(dices)
        defender_roll: int = min(dices)
        # TODO: add marquise extra_hit logic, if there is any

        defender_defenseless_extra_hits: int = 1 if (
                clearing.get_warrior_count(faction_to_warrior(defender)) == 0) else 0

        attacker_extra_hits: int = 1 if (
                attacker == Faction.EYRIE and self.eyrie.get_active_leader() == EyrieLeader.COMMANDER) else 0
        defender_extra_hits: int = 0

        attacker_total_hits: int = min(attacker_roll, clearing.get_warrior_count(
            faction_to_warrior(attacker))) + attacker_extra_hits + defender_defenseless_extra_hits
        defender_total_hits: int = min(defender_roll,
                                       clearing.get_warrior_count(faction_to_warrior(defender))) + defender_extra_hits

        # deal hits
        attacker_remaining_hits = attacker_total_hits
        defender_remaining_hits = defender_total_hits
        # to attacker
        removed_attacker_warriors = clearing.remove_warrior(faction_to_warrior(attacker), defender_remaining_hits)
        defender_remaining_hits -= removed_attacker_warriors
        attacker_faction_board.reserved_warriors += removed_attacker_warriors
        # to defender
        removed_defender_warriors = clearing.remove_warrior(faction_to_warrior(defender), attacker_remaining_hits)
        attacker_remaining_hits -= removed_defender_warriors
        defender_faction_board.reserved_warriors += removed_defender_warriors

        # score
        attacker_total_vp = removed_defender_warriors
        defender_total_vp = removed_attacker_warriors

        attacker_faction_board.victory_point += attacker_total_vp  # @DarkTXYZ do we use this vp
        self.board.gain_vp(attacker, attacker_total_vp)  # or this vp?
        defender_faction_board.victory_point += defender_total_vp
        self.board.gain_vp(defender, defender_total_vp)
        # TODO: score for tokens and buildings removed

        LOGGER.info(
            "{}:{}:{}:battle: {} vs {}, total hits {}:{}, vps gained {}:{}".format(self.turn_player, self.phase,
                                                                                   self.sub_phase,
                                                                                   attacker, defender,
                                                                                   attacker_total_hits,
                                                                                   defender_total_hits,
                                                                                   attacker_total_vp, defender_total_vp)
        )

        # TODO: for excess damage from warriors, choose tokens or buildings to remove
        # TODO: continue to next action

        if attacker_remaining_hits == defender_remaining_hits == 0:
            if self.turn_player == Faction.MARQUISE:
                self.marquise_action_count -= 1
                self.prompt = "Battle Completed. Proceed to next action".format(attacker)
                self.set_actions([Action('Next',
                                         perform(self.marquise_daylight_1_next))])
            elif self.turn_player == Faction.EYRIE:
                pass

        else:
            self.prompt = "Battle Completed. Proceed to removing pieces phase."
            self.set_actions(
                [Action("Next", perform(self.post_battle, attacker, defender, attacker_remaining_hits,
                                        defender_remaining_hits, clearing))])

    def post_battle(self, attacker: Faction, defender: Faction, attacker_remaining_hits, defender_remaining_hits,
                    clearing: Area):
        if attacker_remaining_hits == defender_remaining_hits == 0:
            if self.turn_player == Faction.MARQUISE:
                self.marquise_action_count -= 1
                self.prompt = "Both faction have no remaining hits. Proceed to next action".format(attacker)
                self.set_actions([Action('Next',
                                         perform(self.marquise_daylight_1_next))])
            elif self.turn_player == Faction.EYRIE:
                pass
        elif attacker_remaining_hits > 0:
            actions = self.generate_actions_select_tokens_warriors_to_remove(attacker, defender,
                                                                             attacker_remaining_hits,
                                                                             defender_remaining_hits,
                                                                             clearing)
            if len(actions) == 0:
                self.prompt = "{}: No Token/Building can be removed.".format(defender)
                self.set_actions([Action('Next',
                                         perform(self.post_battle, defender, attacker, defender_remaining_hits, 0,
                                                 clearing))])
            else:
                self.prompt = "{}: Select Token/Building to be removed (Remaining: {})".format(defender,
                                                                                               attacker_remaining_hits)
                self.set_actions(actions)

        elif attacker_remaining_hits == 0:
            self.post_battle(defender, attacker, defender_remaining_hits, attacker_remaining_hits, clearing)

    def generate_actions_select_tokens_warriors_to_remove(self, attacker: Faction, defender: Faction,
                                                          attacker_remaining_hits, defender_remaining_hits,
                                                          clearing: Area):
        actions = []
        buildings = faction_to_buildings(defender)
        tokens = faction_to_tokens(defender)

        if defender == Faction.MARQUISE:
            for token in tokens:
                if token == Token.WOOD and clearing.token_count[token] > 0:
                    actions.append(
                        Action("Wood",
                               perform(self.remove_token_building, attacker, defender, attacker_remaining_hits,
                                       defender_remaining_hits, clearing,
                                       Token.WOOD))
                    )
            for building in buildings:
                if clearing.buildings.count(building) > 0:
                    actions.append(
                        Action(building.name,
                               perform(self.remove_token_building, attacker, defender, attacker_remaining_hits,
                                       defender_remaining_hits, clearing,
                                       building))
                    )

        elif defender == Faction.EYRIE:
            for building in buildings:
                if clearing.buildings.count(building) > 0:
                    actions.append(
                        Action(building.name,
                               perform(self.remove_token_building, attacker, defender, attacker_remaining_hits,
                                       defender_remaining_hits, clearing,
                                       building))
                    )

        return actions

    def remove_token_building(self, attacker: Faction, defender: Faction, attacker_remaining_hits,
                              defender_remaining_hits, clearing: Area,
                              token_building):

        if isinstance(token_building, Building):
            clearing.remove_building(token_building)
        elif isinstance(token_building, Token):
            clearing.remove_token(token_building)

        self.board.gain_vp(attacker, 1)

        self.prompt = "Remove {} successfully.".format(token_building.name)
        self.set_actions([Action('Next', perform(self.post_battle, attacker, defender, attacker_remaining_hits - 1,
                                                 defender_remaining_hits, clearing))])

    def faction_to_faction_board(self, faction: Faction) -> FactionBoard:
        if faction == Faction.MARQUISE:
            return self.marquise
        if faction == Faction.EYRIE:
            return self.eyrie

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

        self.board.turn_player = self.turn_player
        self.board.turn_count = self.turn_count

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
