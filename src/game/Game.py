import logging
import random
from copy import copy, deepcopy
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

import yaml

config = yaml.safe_load(open("config/config.yml"))

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
        self.running: bool = True

        # Game Data
        self.turn_count: int = 0  # TODO: increase this on birdsong of both faction
        self.ui_turn_player: Faction = Faction.MARQUISE
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
            PlayingCard(3, PlayingCardName.ARMORERS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.FOX: 1}),
            PlayingCard(4, PlayingCardName.ARMORERS, Suit.BIRD, PlayingCardPhase.BATTLE, {Suit.FOX: 1}),
            PlayingCard(5, PlayingCardName.WOODLAND_RUNNERS, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1,
                        Item.BOOTS),
            PlayingCard(6, PlayingCardName.ARMS_TRADER, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2,
                        Item.KNIFE),
            PlayingCard(7, PlayingCardName.CROSSBOW, Suit.BIRD, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}, 1,
                        Item.CROSSBOW),
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
            PlayingCard(37, PlayingCardName.FAVOR_OF_THE_RABBITS, Suit.RABBIT, PlayingCardPhase.IMMEDIATE,
                        {Suit.RABBIT: 3}),

            PlayingCard(38, PlayingCardName.AMBUSH, Suit.MOUSE, PlayingCardPhase.BATTLE),
            PlayingCard(39, PlayingCardName.MOUSE_IN_A_SACK, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 1,
                        Item.BAG),
            PlayingCard(40, PlayingCardName.ROOT_TEA, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 1}, 2,
                        Item.KEG),
            PlayingCard(41, PlayingCardName.TRAVEL_GEAR, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 1}, 1,
                        Item.BOOTS),
            PlayingCard(42, PlayingCardName.INVESTMENTS, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.RABBIT: 2}, 3,
                        Item.COIN),
            PlayingCard(43, PlayingCardName.SWORD, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 2}, 2,
                        Item.KNIFE),
            PlayingCard(44, PlayingCardName.CROSSBOW, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.FOX: 1}, 1,
                        Item.CROSSBOW),
            PlayingCard(45, PlayingCardName.SCOUTING_PARTY, Suit.MOUSE, PlayingCardPhase.BATTLE, {Suit.MOUSE: 2}),
            PlayingCard(46, PlayingCardName.SCOUTING_PARTY, Suit.MOUSE, PlayingCardPhase.BATTLE, {Suit.MOUSE: 2}),
            PlayingCard(47, PlayingCardName.CODEBREAKERS, Suit.MOUSE, PlayingCardPhase.DAYLIGHT, {Suit.MOUSE: 1}),
            PlayingCard(48, PlayingCardName.CODEBREAKERS, Suit.MOUSE, PlayingCardPhase.DAYLIGHT, {Suit.MOUSE: 1}),
            PlayingCard(49, PlayingCardName.FAVOR_OF_THE_MICE, Suit.MOUSE, PlayingCardPhase.IMMEDIATE, {Suit.MOUSE: 3}),

            PlayingCard(50, PlayingCardName.DOMINANCE_RABBIT, Suit.RABBIT, PlayingCardPhase.DAYLIGHT),
            PlayingCard(51, PlayingCardName.DOMINANCE_MOUSE, Suit.MOUSE, PlayingCardPhase.DAYLIGHT),
            PlayingCard(52, PlayingCardName.DOMINANCE_BIRD, Suit.BIRD, PlayingCardPhase.DAYLIGHT),
            PlayingCard(53, PlayingCardName.DOMINANCE_FOX, Suit.FOX, PlayingCardPhase.DAYLIGHT),
        ]
        self.discard_pile: list[PlayingCard] = []
        self.discard_pile_dominance: list[PlayingCard] = []

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
        self.marquise = MarquiseBoard("Marquise de Cat", Colors.ORANGE, 25 - 11, Vector2(0, 0.0 * Config.SCREEN_HEIGHT))
        self.eyrie = EyrieBoard("Eyrie Dynasties", Colors.BLUE, 20 - 6, Vector2(0, 0.5 * Config.SCREEN_HEIGHT))

        # Actions
        self.marquise_base_actions: {Phase: [[Action]]} = {
            Phase.BIRDSONG: [[Action('Next', perform(self.marquise_birdsong_start))]],
            Phase.DAYLIGHT: [
                [Action('Craft', perform(self.marquise_daylight_craft)),
                 Action('Next', perform(self.marquise_daylight_2))],
                [Action('Battle'), Action('March', perform(self.marquise_daylight_march_move_from)), Action('Recruit'),
                 Action('Build'),
                 Action('Overwork'),
                 Action('Next', perform(self.marquise_evening_draw_card))]
            ],
            Phase.EVENING: [[Action('Next', perform(self.marquise_evening_discard_card))],
                            [Action('End turn', perform(self.eyrie_start))]]
        }
        self.eyrie_base_actions: {Phase: [[Action]]} = {
            Phase.BIRDSONG: [
                [Action('Next', perform(self.eyrie_start))],
                [],
                []
            ],
            Phase.DAYLIGHT: [
                [],
                []
            ],
            Phase.EVENING: [[Action('Next')]]
        }
        self.actions: list[Action] = []
        self.set_actions()

        # Marquise variables
        self.marquise_action_count = 3
        self.marquise_march_count = 2
        self.marquise_recruit_count = 1
        self.marquise_recruit_action_used = False
        self.distance_from_the_keep_list = [4, 3, 2, 3, 3, 2, 1, 1, 3, 2, 1, 0]
        self.distance_from_the_keep = {}

        # Battle variables
        self.sappers_enable = {
            Faction.MARQUISE: False,
            Faction.EYRIE: False
        }
        self.brutal_tactics_enable = {
            Faction.MARQUISE: False,
            Faction.EYRIE: False
        }

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

        self.prompt = "If hand empty, draw 1 card"

        # Setup Game
        self.setup_board()

    #####
    # Setup Board
    def setup_board(self):
        self.board.areas[-1].add_token(Token.CASTLE)

        for i in range(1, len(self.board.areas)):
            self.board.areas[i].add_warrior(Warrior.MARQUISE, 1)

        for i in range(0, len(self.board.areas)):
            self.distance_from_the_keep[self.board.areas[i]] = self.distance_from_the_keep_list[i]

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

    def get_actions(self) -> list[Action]:
        return self.actions

    def gain_vp(self, faction: Faction, vp: int):
        if self.faction_to_faction_board(faction).dominance_card is not None:
            return
        self.board.gain_vp(faction, vp)
        self.check_win_condition(faction)

    def check_win_condition(self, faction: Faction, no_end_action: bool = False) -> tuple[
                                                                                        int, int] | PlayingCard | None:
        faction_board = self.faction_to_faction_board(faction)
        if faction_board.dominance_card is None:
            return self.check_win_condition_vp(faction, no_end_action)
        else:
            return self.check_win_condition_dominance(faction, no_end_action)

    def check_win_condition_vp(self, faction: Faction, no_end_action: bool = False) -> tuple[int, int] | None:
        if self.board.faction_points[faction] >= config['game']['victory-point-limit']:
            if not no_end_action:
                LOGGER.info(
                    "GAME_END:VP:MARQUISE {} vs EYRIE {}".format(self.board.faction_points[Faction.MARQUISE],
                                                                 self.board.faction_points[Faction.EYRIE]))
                self.end_game()
            return self.board.faction_points[Faction.MARQUISE], self.board.faction_points[Faction.EYRIE]

    def check_win_condition_dominance(self, faction: Faction, no_end_action: bool = False) -> PlayingCard | None:
        faction_board = self.faction_to_faction_board(faction)
        warrior = faction_to_warrior(faction)

        areas = self.board.areas

        winning_dominance: PlayingCard | None = None

        if faction_board.dominance_card.name == PlayingCardName.DOMINANCE_BIRD:
            if (areas[0].ruler() == warrior and areas[11].ruler() == warrior) or (
                    areas[2].ruler() == warrior and areas[8].ruler() == warrior):
                winning_dominance = faction_board.dominance_card
        elif self.board.count_ruling_clearing_by_faction_and_suit(faction, faction_board.dominance_card.suit) >= 3:
            winning_dominance = faction_board.dominance_card

        if not no_end_action:
            if winning_dominance is not None:
                LOGGER.info(
                    "GAME_END:DOMINANCE:{}, {} Wins".format(winning_dominance.name,
                                                            faction))
                self.end_game()
        return winning_dominance

    def end_game(self):
        self.running = False

    def get_end_game_data(self) -> tuple[Faction | None, str, int, Faction, int, int, None | PlayingCard] | None:
        """
        Should only be called with the game has already ended.
        :return: Winning faction, winning condition, turns played, current player, marquise's vp, eyrie's vp,
        winning dominance card if the game has ended. Otherwise, returns None.
        """

        winning_faction: None | Faction = None
        if self.check_win_condition(Faction.MARQUISE, True):
            winning_faction = Faction.MARQUISE
        elif self.check_win_condition(Faction.EYRIE, True):
            winning_faction = Faction.EYRIE

        turns_played: int = self.turn_count
        turn_player: Faction = self.ui_turn_player
        vp_marquise: int = self.board.faction_points[Faction.MARQUISE]
        vp_eyrie: int = self.board.faction_points[Faction.EYRIE]
        winning_dominance: None | PlayingCard = self.check_win_condition_dominance(winning_faction,
                                                                                   True) if self.faction_to_faction_board(
            winning_faction).dominance_card is not None else None
        winning_condition: str = "vp" if winning_dominance is None else "dominance"

        return winning_faction, winning_condition, turns_played, turn_player, vp_marquise, vp_eyrie, winning_dominance

    #####
    # MARQUISE

    def marquise_birdsong_start(self):
        LOGGER.info("{}:{}:{}:MARQUISE's turn begins".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.turn_count += 1

        self.check_win_condition(Faction.MARQUISE)
        self.marquise.clear_activated_cards()
        self.better_burrow_bank(Faction.MARQUISE)

        self.marquise_action_count = 3
        self.marquise_recruit_count = 1
        # Place one wood at each sawmill
        for area in self.board.areas:
            area.token_count[Token.WOOD] += area.buildings.count(Building.SAWMILL)

        self.marquise.crafting_pieces_count = self.get_workshop_count_by_suit()

        self.marquise_birdsong_cards()

    def marquise_birdsong_cards(self):
        if len(self.generate_actions_cards_birdsong(Faction.MARQUISE, self.marquise_birdsong_cards)) == 0:
            self.marquise_daylight()
        else:
            self.prompt = "Do you want to use Birdsong card's action?"
            self.set_actions(self.generate_actions_cards_birdsong(Faction.MARQUISE, self.marquise_birdsong_cards) + [
                Action('Next', perform(self.marquise_daylight))])

    def marquise_daylight(self):
        self.phase = Phase.DAYLIGHT

        craftable_cards = self.generate_actions_craft_cards(Faction.MARQUISE)
        if not craftable_cards:
            self.marquise_daylight_2()
        else:
            self.prompt = "Want to craft something, squire?"
            self.set_actions(self.generate_actions_craft_cards(Faction.MARQUISE) + [
                Action('Next', perform(self.marquise_daylight_2))])

    def marquise_daylight_craft(self):
        self.prompt = "What cards do you want to craft?"
        self.set_actions(self.generate_actions_craft_cards(Faction.MARQUISE)
                         + self.generate_actions_activate_dominance_card(Faction.MARQUISE, self.marquise_daylight_craft)
                         + self.generate_actions_take_dominance_card(Faction.MARQUISE, self.marquise_daylight_craft)
                         + [Action('Next', perform(self.marquise_daylight_2))])

    def marquise_daylight_2(self):
        actions = []
        self.prompt = "Select Actions (Remaining Action: {})".format(self.marquise_action_count)
        self.ui_turn_player = Faction.MARQUISE
        self.phase = Phase.DAYLIGHT
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
                self.marquise_march_count = 2
                actions.append(Action('March', perform(self.marquise_daylight_march_move_from)))
            if self.marquise_build_check():
                actions.append(Action('Build', perform(self.marquise_daylight_build_select_clearing)))
            if self.marquise_recruit_check():
                actions.append(Action('Recruit', perform(self.marquise_daylight_recruit)))
            if self.marquise_overwork_check():
                actions.append(Action('Overwork', perform(self.marquise_daylight_overwork_select_clearing)))
            if self.marquise_battle_check():
                actions.append(Action('Battle', perform(self.marquise_daylight_battle)))

        actions.append(Action('Next', perform(self.marquise_evening_draw_card)))
        self.set_actions(actions
                         + self.generate_actions_activate_dominance_card(Faction.MARQUISE,
                                                                         self.marquise_daylight_2)
                         + self.generate_actions_take_dominance_card(Faction.MARQUISE,
                                                                     self.marquise_daylight_2)
                         )

    def marquise_hawks_for_hire_check(self):
        return len([card for card in self.marquise.cards_in_hand if card.suit == Suit.BIRD]) > 0

    def marquise_march_check(self):
        return len(self.find_available_source_clearings(Faction.MARQUISE)) > 0

    def marquise_build_check(self):
        return len(self.get_buildable_clearings(Faction.MARQUISE)) > 0

    def marquise_recruit_check(self):
        return self.count_buildings(Building.RECRUITER) > 0 and self.marquise_recruit_count > 0

    def marquise_overwork_check(self):
        return len(self.find_available_overwork_clearings()) > 0

    def marquise_battle_check(self):
        return len(self.get_battlable_clearing(Faction.MARQUISE)) > 0

    def marquise_daylight_hawks_for_hire_select_card(self):
        self.prompt = "Select card to discard"
        self.set_actions(self.generate_actions_select_card_hawks_for_hire())

    def marquise_daylight_march_move_from(self):
        self.prompt = "Let's march. Choose area to move from. (Remaining march action: {})".format(
            self.marquise_march_count)
        self.set_actions(self.generate_actions_select_src_clearing(Faction.MARQUISE))

    def marquise_daylight_march_move_to(self, faction, src):
        self.prompt = "Choose area to move to. (Remaining march action: {})".format(
            self.marquise_march_count)
        self.set_actions(self.generate_actions_select_dest_clearing(faction, src))

    def marquise_daylight_march_select_warriors(self, faction, src, dest):
        self.prompt = "Choose number of warriors to move. (Remaining march action: {})".format(
            self.marquise_march_count)
        self.set_actions(self.generate_actions_select_warriors(faction, src, dest))

    def marquise_daylight_build_select_clearing(self):
        self.prompt = "Let's build. Select clearing"
        self.set_actions(self.generate_actions_select_buildable_clearing(Faction.MARQUISE))

    def marquise_daylight_build_select_building(self, clearing):
        self.prompt = "Select Building"
        self.set_actions(self.generate_actions_select_building(Faction.MARQUISE, clearing))

    def marquise_daylight_recruit(self):
        self.marquise_recruit_count -= 1
        self.marquise_action_count -= 1
        LOGGER.info("{}:{}:{}:MARQUISE recruit.".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.prompt = "Recruit warrior"

        if self.marquise.reserved_warriors >= self.marquise.building_trackers[Building.RECRUITER]:
            self.recruit(Faction.MARQUISE)
            self.marquise_daylight_2()
        else:
            clearing_with_recruiter = [clearing for clearing in self.board.areas for _ in
                                       range(clearing.buildings.count(Building.RECRUITER))]
            self.marquise_daylight_recruit_some_clearings(clearing_with_recruiter)

    def marquise_daylight_recruit_some_clearings(self, clearing_with_recruiter):
        if clearing_with_recruiter is [] or self.marquise.reserved_warriors == 0:
            self.marquise_daylight_2()
        else:
            actions = self.generate_actions_select_recruiter(clearing_with_recruiter)
            self.set_actions(actions)
            self.prompt = 'Select Clearing to add warriors'

    def generate_actions_select_recruiter(self, clearing_with_recruiter):
        actions = []

        for clearing in clearing_with_recruiter:
            remaining_clearing = clearing_with_recruiter.copy()
            remaining_clearing.remove(clearing)
            actions.append(Action('{}'.format(clearing.area_index), perform(self.recruit_single_clearing, clearing,
                                                                            remaining_clearing)))

        return actions

    def recruit_single_clearing(self, clearing, remaining_clearing_with_recruiter):
        self.add_warrior(Faction.MARQUISE, clearing, 1)
        LOGGER.info(
            "{}:{}:{}:MARQUISE adds warrior in clearing #{}".format(self.ui_turn_player, self.phase,
                                                                    self.sub_phase,
                                                                    clearing.area_index))
        self.marquise_daylight_recruit_some_clearings(remaining_clearing_with_recruiter)

    def marquise_daylight_battle(self):
        self.marquise_action_count -= 1
        self.prompt = "Select Clearing"
        self.set_actions(self.generate_actions_select_clearing_battle(Faction.MARQUISE,
                                                                      self.marquise_daylight_2))

    # def marquise_daylight_battle_select_faction(self, clearing):
    #     self.prompt = "Select Faction"
    #     self.set_actions(
    #         self.generate_actions_select_faction_battle(Faction.MARQUISE, clearing, self.marquise_daylight_2))

    def marquise_daylight_overwork_select_clearing(self):
        self.prompt = "Select Clearing"
        self.set_actions(self.generate_actions_overwork_select_clearing())

    def marquise_daylight_overwork_select_card_to_discard(self, clearing):
        self.prompt = "Select Card"
        self.set_actions(self.generate_actions_overwork_select_card(clearing))

    def marquise_overwork(self, clearing: Area, card):
        LOGGER.info("{}:{}:{}:MARQUISE overwork on clearing #{}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                        clearing.area_index))
        self.discard_card(self.marquise.cards_in_hand, card)
        clearing.token_count[Token.WOOD] += 1

        self.prompt = "Overwork complete"
        self.marquise_action_count -= 1
        self.set_actions([Action('Next', self.marquise_daylight_2)])

    def marquise_evening_draw_card(self):
        self.prompt = "Draw one card, plus one card per draw bonus"
        number_of_card_to_be_drawn = self.marquise.get_reward_card() + 1
        self.take_card_from_draw_pile(Faction.MARQUISE, number_of_card_to_be_drawn)

        self.phase = Phase.EVENING
        self.sub_phase = 0
        self.set_actions()

    def marquise_evening_discard_card(self):
        self.phase = Phase.EVENING
        self.sub_phase = 1
        card_in_hand_count = len(self.marquise.cards_in_hand)
        if card_in_hand_count > 5:
            self.prompt = "Select card to discard down to 5 cards (currently {} cards in hand)".format(
                card_in_hand_count)
            self.set_actions(self.generate_actions_select_card_to_discard(Faction.MARQUISE))
        else:
            self.ui_turn_player = Faction.EYRIE
            self.turn_player = Faction.EYRIE
            self.phase = Phase.BIRDSONG
            self.sub_phase = 0
            self.prompt = "Eyrie's Turn"
            self.set_actions()

    def get_workshop_count_by_suit(self) -> {Suit: int}:
        return self.get_building_count_by_suit(Building.WORKSHOP)

    def count_woods_from_clearing(self, clearing):
        return self.marquise_bfs_count_wood(clearing)

    def marquise_bfs_count_wood(self, clearing: Area):
        visited = []
        order: list[tuple[int, tuple[int, Area]]] = []
        queue: list[tuple[int, Area]] = [(0, clearing)]

        total_wood = 0

        while queue:
            dist, u = queue.pop(0)
            if u in visited:
                continue
            visited.append(u)
            order.append((dist, (self.distance_from_the_keep[u], u)))
            total_wood += u.token_count[Token.WOOD]

            for v in u.connected_clearings:
                if v.ruler() == Warrior.MARQUISE:
                    queue.append((dist + 1, v))

        def hash_value(item: tuple[int, tuple[int, Area]]):
            return item[0] * 10 + item[1][0]

        order.sort(key=hash_value)

        return order, total_wood

    def marquise_get_min_cost_building(self):
        cost = self.marquise.building_cost
        building_tracker = self.marquise.building_trackers

        min_cost = float('inf')

        for building, tracker in building_tracker.items():
            if tracker < 6:
                min_cost = min(cost[tracker], min_cost)

        return min_cost

    def remove_wood(self, number, orders: list[tuple[int, tuple[int, Area]]]):
        remaining_wood = number
        for order in orders:
            clearing = order[1][1]
            remaining_wood = self.remove_wood_from_clearing(clearing, remaining_wood)
            if remaining_wood == 0:
                break

    def remove_wood_from_clearing(self, clearing,
                                  number):
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

    def generate_actions_overwork_select_clearing(self):
        available_clearing = self.find_available_overwork_clearings()
        actions: list[Action] = []

        for clearing in available_clearing:
            actions.append(
                Action("{}".format(clearing.area_index),
                       perform(self.marquise_daylight_overwork_select_card_to_discard, clearing)))

        return actions

    def generate_actions_overwork_select_card(self, clearing):
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
        self.set_actions([Action('Next', self.marquise_daylight_2)])

    #####
    # Eyrie
    def eyrie_start(self):
        LOGGER.info("{}:{}:{}:eyrie turn begins".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.turn_count += 1

        self.check_win_condition(Faction.EYRIE)
        self.eyrie.clear_activated_cards()
        self.better_burrow_bank(Faction.EYRIE)

        if len(self.eyrie.cards_in_hand) == 0:
            LOGGER.info("{}:{}:{}:eyrie_emergency_orders".format(self.ui_turn_player, self.phase, self.sub_phase))
            self.take_card_from_draw_pile(Faction.EYRIE)

        self.ui_turn_player = Faction.EYRIE
        self.turn_player = Faction.EYRIE
        self.phase = Phase.BIRDSONG
        self.sub_phase = 1

        self.added_bird_card = False
        self.addable_count = 2

        self.prompt = "Select Card To Add To Decree"
        actions: list[Action] = self.generate_actions_add_to_the_decree_first()
        if len(actions) == 0:
            self.eyrie_a_new_roost()
        else:
            self.set_actions(actions)

    def generate_actions_add_to_the_decree_first(self) -> list[Action]:
        actions: list[Action] = []
        if self.addable_count > 0:
            for card in self.eyrie.cards_in_hand:
                if self.added_bird_card and card.suit == Suit.BIRD:
                    continue
                actions.append(Action('{} ({})'.format(card.name, card.suit),
                                      perform(self.select_card_to_add_to_the_decree, card)))
        LOGGER.info(
            "{}:{}:{}:generate_actions_add_to_the_decree_first {}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                          len(actions)))
        return actions

    def select_card_to_add_to_the_decree(self, card: PlayingCard):
        self.select_card(card)

        self.prompt = "Select Decree ({} ({}))".format(card.name, card.suit)
        self.set_actions(self.generate_actions_add_to_the_decree())

    def generate_actions_add_to_the_decree(self) -> list[Action]:
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
            "{}:{}:{}:Added card '{}' to {} decree".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                           self.selected_card.name, decree_action))

        if self.addable_count != 0:
            self.prompt = "Select ANOTHER card to add to the Decree"
            self.set_actions(self.generate_actions_add_to_the_decree_first() + [
                Action("Skip", perform(self.eyrie_add_to_the_decree_additional_skip))
            ])
        else:
            self.eyrie_a_new_roost()

    def eyrie_add_to_the_decree_additional_skip(self):
        LOGGER.info(
            "{}:{}:{}:eyrie_add_to_the_decree_additional_skip".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.eyrie_a_new_roost()

    def eyrie_a_new_roost(self):
        LOGGER.info(
            "{}:{}:{}:eyrie_a_new_roost".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.sub_phase = 2

        if self.eyrie.roost_tracker == 0:
            self.prompt = "If you have no roost, place a roost and 3 warriors in the clearing with the fewest total warriors. (Select Clearing)"
            actions: list[Action] = self.generate_actions_place_roost_and_3_warriors()
            if len(actions) == 0:
                self.eyrie_birdsong_to_daylight()
            else:
                self.set_actions(actions)
        else:
            self.eyrie_birdsong_to_daylight()

    def generate_actions_place_roost_and_3_warriors(self) -> list[Action]:
        actions: list[Action] = []
        min_token_areas = [area for area in self.board.get_min_warrior_areas() if Building.EMPTY in area.buildings]
        for area in min_token_areas:
            actions.append(Action("Area {}".format(area.area_index), perform(self.place_roost_and_3_warriors, area)))

        return actions

    def place_roost_and_3_warriors(self, area: Area):
        LOGGER.info(
            "{}:{}:{}:place_roost_and_3_warriors at area#{}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                    area.area_index))
        self.add_warrior(Faction.EYRIE, area, 3)
        self.build_roost(area)

        self.set_actions([Action('Next, to Daylight', perform(self.eyrie_birdsong_to_daylight))])

    def build_roost(self, clearing: Area):
        building_slot_index = clearing.buildings.index(Building.EMPTY)
        clearing.buildings[building_slot_index] = Building.ROOST
        self.eyrie.roost_tracker += 1

        LOGGER.info(
            "{}:{}:{}:build_roost built {} in clearing #{}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                   Building.ROOST, clearing.area_index))

    def eyrie_birdsong_to_daylight(self):  # TODO: Eyrie Royal Claim
        LOGGER.info("{}:{}:{}:eyrie_birdsong_to_daylight".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.phase = Phase.DAYLIGHT
        self.sub_phase = 0

        self.eyrie.crafting_pieces_count = self.get_building_count_by_suit(Building.ROOST)

        self.eyrie_daylight_craft()

    def eyrie_daylight_craft(self):
        self.prompt = "Craft Cards"
        self.set_actions(self.generate_actions_craft_cards(Faction.EYRIE)
                         + self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_daylight_craft)
                         + self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_daylight_craft)
                         + [Action('Next', perform(self.eyrie_daylight_craft_to_resolve_the_decree))])

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

    def eyrie_daylight_craft_to_resolve_the_decree(self):
        LOGGER.info(
            "{}:{}:{}:eyrie_daylight_craft_to_resolve_the_decree".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.sub_phase = 1

        self.decree_counter = deepcopy(self.eyrie.decree)
        self.eyrie_pre_recruit()

    def eyrie_pre_recruit(self):
        LOGGER.info("{}:{}:{}:eyrie_pre_recruit".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.update_prompt_eyrie_decree(DecreeAction.RECRUIT)
        self.prompt += " Recruit in Area:"
        self.set_actions(self.generate_actions_eyrie_recruit()
                         + self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_pre_recruit)
                         + self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_pre_recruit))

    def eyrie_turmoil(self):
        # humiliate
        self.eyrie_turmoil_humiliate()
        # purge
        self.eyrie_turmoil_purge()
        # depose, then rest
        self.eyrie_turmoil_depose()

    def eyrie_turmoil_humiliate(self):
        bird_card_in_decree_count = self.eyrie.count_card_in_decree_with_suit(Suit.BIRD)
        vp_lost = min(self.board.faction_points[Faction.EYRIE],
                      bird_card_in_decree_count)
        self.board.lose_vp(Faction.EYRIE, vp_lost)
        LOGGER.info("{}:{}:{}:turmoil:humiliate: {} bird cards in the decree, lost {} vp(s)".format(self.ui_turn_player,
                                                                                                    self.phase,
                                                                                                    self.sub_phase,
                                                                                                    bird_card_in_decree_count,
                                                                                                    vp_lost))

    def eyrie_turmoil_purge(self):
        for decree in DecreeAction:
            for card in self.eyrie.decree[decree]:
                if card.name is not LOYAL_VIZIER.name:
                    self.discard_card(self.eyrie.decree[decree], card)

        self.eyrie.reset_decree()
        LOGGER.info("{}:{}:{}:turmoil:purge: discarded all decree cards except loyal viziers".format(self.ui_turn_player,
                                                                                                     self.phase,
                                                                                                     self.sub_phase))

    def eyrie_turmoil_depose(self):
        current_leader = self.eyrie.get_active_leader()

        self.eyrie.deactivate_current_leader()
        inactive_leaders = self.eyrie.get_inactive_leader()

        if len(inactive_leaders) == 0:
            self.eyrie.a_new_generation()
            inactive_leaders = self.eyrie.get_inactive_leader()

        LOGGER.info(
            "{}:{}:{}:turmoil:depose: {} deposed".format(self.ui_turn_player, self.phase, self.sub_phase, current_leader))
        self.prompt = "Select New Eyrie Leader:"
        self.set_actions(self.generate_actions_eyrie_select_new_leader(inactive_leaders))

    def generate_actions_eyrie_select_new_leader(self, inactive_leaders: list[EyrieLeader]) -> list[Action]:
        actions: list[Action] = []

        for leader in inactive_leaders:
            actions.append(Action("{}".format(leader),
                                  perform(self.eyrie_select_new_leader, leader)))

        return actions

    def eyrie_select_new_leader(self, leader: EyrieLeader):
        self.eyrie.activate_leader(leader)
        LOGGER.info(
            "{}:{}:{}:turmoil:depose: {} selected as new leader".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                        leader))
        self.eyrie_turmoil_rest()

    def eyrie_turmoil_rest(self):
        LOGGER.info("{}:{}:{}:turmoil:rest".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.phase = Phase.EVENING
        self.sub_phase = 1
        self.eyrie_evening()

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
                actions.append(Action("Turmoil", self.eyrie_turmoil))
            else:
                actions.append(Action("Next, to MOVE", self.eyrie_pre_move))

        return actions

    def eyrie_recruit(self, area: Area):
        decree_action = DecreeAction.RECRUIT
        self.recruit(Faction.EYRIE, area)
        # remove decree counter
        self.remove_decree_counter(decree_action, area.suit)

        LOGGER.info(
            "{}:{}:{}:{} recruited in area {}".format(self.ui_turn_player, self.phase, self.sub_phase, Faction.EYRIE,
                                                      area.area_index))

        self.eyrie_pre_recruit()

    def eyrie_pre_move(self):
        LOGGER.info("{}:{}:{}:eyrie_pre_move".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.update_prompt_eyrie_decree(DecreeAction.MOVE)
        self.prompt += " Choose area to move from."
        self.set_actions(self.generate_actions_eyrie_move()
                         + self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_pre_move)
                         + self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_pre_move))

    def generate_actions_eyrie_move(self) -> list[Action]:
        actions: list[Action] = self.generate_actions_select_src_clearing(Faction.EYRIE)

        decree_action = DecreeAction.MOVE

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                actions.append(Action("Turmoil", self.eyrie_turmoil))
            else:
                actions.append(Action("Next, To BATTLE", self.eyrie_pre_battle))

        return actions

    def eyrie_choose_move_from(self, faction, src):
        LOGGER.info("{}:{}:{}:eyrie_choose_move_from area {}".format(self.ui_turn_player, self.phase, self.sub_phase, src))

        self.update_prompt_eyrie_decree(DecreeAction.MOVE)
        self.prompt += " Choose area to move to."
        self.set_actions(self.generate_actions_select_dest_clearing(faction, src))

    def eyrie_choose_move_to(self, faction, src, dest):
        LOGGER.info(
            "{}:{}:{}:eyrie_choose_move_to area {}".format(self.ui_turn_player, self.phase, self.sub_phase, src, dest))

        self.update_prompt_eyrie_decree(DecreeAction.MOVE)
        self.prompt += " Choose number of warriors to move."
        self.set_actions(self.generate_actions_select_warriors(faction, src, dest))

    def eyrie_pre_battle(self):
        LOGGER.info("{}:{}:{}:eyrie_pre_battle".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.update_prompt_eyrie_decree(DecreeAction.BATTLE)
        self.prompt += " Choose area to battle in."

        self.set_actions(self.generate_actions_eyrie_battle()
                         + self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_pre_battle) \
                         + self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_pre_battle))

    def generate_actions_eyrie_battle(self) -> list[Action]:
        actions: list[Action] = self.generate_actions_select_clearing_battle(Faction.EYRIE, self.eyrie_pre_build)

        decree_action: DecreeAction = DecreeAction.BATTLE

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                actions.append(Action("Turmoil", self.eyrie_turmoil))
            else:
                actions.append(Action("Next, To BUILD", self.eyrie_pre_build))

        return actions

    def eyrie_pre_build(self):
        LOGGER.info("{}:{}:{}:eyrie_pre_battle".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.update_prompt_eyrie_decree(DecreeAction.BUILD)

        self.ui_turn_player = Faction.EYRIE
        self.prompt += " Choose area to build roost in."
        self.set_actions(self.generate_actions_eyrie_build()
                         + self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_pre_build)
                         + self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_pre_build))

    def generate_actions_eyrie_build(self):
        actions: list[Action] = self.generate_actions_select_buildable_clearing(Faction.EYRIE)

        decree_action: DecreeAction = DecreeAction.BUILD

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                actions.append(Action("Turmoil", self.eyrie_turmoil))
            else:
                actions.append(Action("Next, To Evening", self.eyrie_build_to_evening))

        return actions

    def eyrie_build(self, clearing: Area):
        self.build_roost(clearing)
        self.remove_decree_counter(DecreeAction.BUILD, clearing.suit)

        self.update_prompt_eyrie_decree(DecreeAction.BUILD)
        self.set_actions(self.generate_actions_eyrie_build())

    def eyrie_build_to_evening(self):
        self.eyrie_evening()

    def eyrie_evening(self):
        # score points
        roost_tracker = self.eyrie.roost_tracker
        vp = EyrieBoard.ROOST_REWARD_VP[roost_tracker]
        card_to_draw = 1 + EyrieBoard.ROOST_REWARD_CARD[roost_tracker]
        self.gain_vp(Faction.EYRIE, vp)
        LOGGER.info(
            "{}:{}:{}:eyrie_evening: roost tracker {}, scored {} vps".format(self.ui_turn_player, self.phase,
                                                                             self.sub_phase, self.eyrie.roost_tracker,
                                                                             vp))
        # draw and discard
        self.take_card_from_draw_pile(Faction.EYRIE, card_to_draw)
        card_in_hand_count = len(self.eyrie.cards_in_hand)
        if card_in_hand_count > 5:
            self.prompt = "Select card to discard down to 5 cards (currently {} cards in hand)".format(
                card_in_hand_count)
            self.set_actions(self.generate_actions_select_card_to_discard(Faction.EYRIE))
        else:
            self.eyrie_evening_to_marquise()

    def eyrie_evening_to_marquise(self):
        LOGGER.info("{}:{}:{}:eyrie_evening_to_marquise".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.ui_turn_player = Faction.MARQUISE
        self.turn_player = Faction.MARQUISE
        self.phase = Phase.BIRDSONG
        self.sub_phase = 0
        self.prompt = "Marquise's Turn"
        self.set_actions()  # to marquise

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
                "{}:{}:{}:{} selected as new leader".format(self.ui_turn_player, self.phase, self.sub_phase, leader))

    def remove_decree_counter(self, decree_action: DecreeAction | str, suit: Suit | str):
        self.decree_counter[decree_action].remove(
            self.get_decree_card_to_use(decree_action, suit)
        )

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

    def craft_card(self, faction: Faction, card: PlayingCard):  # TODO: no such duplicate cards can be crafted
        LOGGER.info("{}:{}:{}:Crafted {} card".format(self.ui_turn_player, self.phase, self.sub_phase, card.name))
        if faction == Faction.MARQUISE:
            if card.phase == PlayingCardPhase.IMMEDIATE:
                self.gain_vp(faction, card.reward_vp)
                if card.reward_item is not None:
                    self.marquise.items[card.reward_item] += 1
                    self.board.remove_item_from_board(card.reward_item)
                self.discard_card(self.marquise.cards_in_hand, card)
            else:
                self.marquise.cards_in_hand.remove(card)
                self.marquise.crafted_cards.append(card)

            for suit in card.craft_requirement.keys():
                self.marquise.spend_crafting_piece(suit, card.craft_requirement[suit])

            # print("MARQUISE", [card.name for card in self.marquise.cards_in_hand],[card.name for card in self.marquise.crafted_cards])
            self.prompt = "{} has been crafted.".format(card.name)
            self.set_actions([Action("Next", self.marquise_daylight)])

        elif faction == Faction.EYRIE:
            if card.phase == PlayingCardPhase.IMMEDIATE:
                # Gain VP
                if card.reward_vp > 0:
                    if self.eyrie.get_active_leader() == EyrieLeader.BUILDER:
                        self.gain_vp(faction, card.reward_vp)
                    else:
                        self.gain_vp(faction, 1)

                # Gain Item
                if card.reward_item is not None:
                    self.eyrie.items[card.reward_item] += 1
                    self.board.remove_item_from_board(card.reward_item)

                self.discard_card(self.eyrie.cards_in_hand, card)
            else:
                self.eyrie.cards_in_hand.remove(card)
                self.eyrie.crafted_cards.append(card)

            for suit in card.craft_requirement.keys():
                self.marquise.spend_crafting_piece(suit, card.craft_requirement[suit])
            self.eyrie_daylight_craft()

    def get_craftable_cards(self, faction: Faction) -> list[PlayingCard]:
        craftable_cards: list[PlayingCard] = []

        cards_in_hand: list[PlayingCard] = []
        faction_board = self.faction_to_faction_board(faction)
        if faction == Faction.MARQUISE:
            cards_in_hand = self.marquise.cards_in_hand
        elif faction == Faction.EYRIE:
            cards_in_hand = self.eyrie.cards_in_hand

        for card in cards_in_hand:
            if card.craft_requirement is None:
                continue

            can_craft = True
            for suit in card.craft_requirement.keys():
                if not faction_board.can_spend_crafting_piece(suit, card.craft_requirement[suit]):
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
            if self.ui_turn_player == Faction.MARQUISE:
                self.actions = self.marquise_base_actions[self.phase][self.sub_phase]
            elif self.ui_turn_player == Faction.EYRIE:
                self.actions = self.eyrie_base_actions[self.phase][self.sub_phase]

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
                "{}:{}:{}:{} drawn {} card(s)".format(self.ui_turn_player, self.phase, self.sub_phase, faction, amount))
        else:
            lesser_amount = min(len(self.draw_pile), amount)
            faction_board.cards_in_hand.extend(self.draw_pile[0:lesser_amount])
            self.draw_pile = self.draw_pile[lesser_amount:]
            LOGGER.info(
                "{}:{}:{}:{} drawn {} card(s)".format(self.ui_turn_player, self.phase, self.sub_phase, faction, lesser_amount))

            self.shuffle_discard_pile_into_draw_pile()

            remaining_amount = amount - lesser_amount
            faction_board.cards_in_hand.extend(self.draw_pile[0:remaining_amount])
            self.draw_pile = self.draw_pile[remaining_amount:]
            LOGGER.info(
                "{}:{}:{}:{} drawn {} card(s)".format(self.ui_turn_player, self.phase, self.sub_phase, faction, remaining_amount))

    def shuffle_discard_pile_into_draw_pile(self):
        self.draw_pile.extend(self.discard_pile)
        self.discard_pile = []
        self.shuffle_draw_pile()

    def discard_card(self, discard_from: list[PlayingCard], card: PlayingCard):
        discard_from.remove(card)
        if card.name in PlayingCard.DOMINANCE_CARD_NAMES:
            self.discard_pile_dominance.append(card)
        else:
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
            "{}:{}:{}:{} move {} warrior(s) from Clearing #{} to Clearing #{}".format(self.ui_turn_player, self.phase,
                                                                                      self.sub_phase, faction,
                                                                                      num, src,
                                                                                      dest))

        if faction == Faction.MARQUISE:
            src.remove_warrior(Warrior.MARQUISE, num)
            dest.add_warrior(Warrior.MARQUISE, num)

            self.marquise_march_count -= 1
            LOGGER.info(
                "{}:{}:{}:MARQUISE's remaining march action: {}".format(self.ui_turn_player, self.phase,
                                                                        self.sub_phase, self.marquise_march_count))
            if self.marquise_march_count > 0:
                self.prompt = "The warriors has been moved. (Remaining march action: {})".format(
                    self.marquise_march_count)
                self.set_actions([Action('Next', perform(self.marquise_daylight_march_move_from))])
            else:
                self.marquise_action_count -= 1
                self.prompt = "The warriors has been moved. (Remaining march action: {})".format(
                    self.marquise_march_count)
                self.set_actions([Action('Next', perform(self.marquise_daylight_2))])
        elif faction == Faction.EYRIE:
            src.remove_warrior(Warrior.EYRIE, num)
            dest.add_warrior(Warrior.EYRIE, num)
            decree_action = DecreeAction.MOVE

            self.remove_decree_counter(decree_action, src.suit)

            self.update_prompt_eyrie_decree(decree_action)
            self.set_actions(self.generate_actions_eyrie_move())

    def find_available_source_clearings(self, faction: Faction):
        movable_clearings = []

        if faction == Faction.MARQUISE:
            for area in self.board.areas:
                if len(self.find_available_destination_clearings(faction, area)) <= 0:
                    continue
                if area.ruler() == Warrior.MARQUISE and area.warrior_count[Warrior.MARQUISE] > 0:
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
                if len(self.find_available_destination_clearings(faction, area)) <= 0:
                    continue
                if area.ruler() == Warrior.EYRIE and area.warrior_count[Warrior.EYRIE] > 0:
                    movable_clearings.append(area)
                else:
                    for connected_area in area.connected_clearings:
                        if area.warrior_count[Warrior.EYRIE] > 0 and connected_area.ruler() == Warrior.EYRIE:
                            movable_clearings.append(area)
                            break

        return movable_clearings

    def find_available_destination_clearings(self, faction: Faction, src: Area):
        dests: list[Area] = []
        warrior: Warrior = faction_to_warrior(faction)

        if src.ruler() == warrior:
            for connect_area in src.connected_clearings:
                if src == connect_area:
                    continue
                dests.append(connect_area)
        else:
            for connect_area in src.connected_clearings:
                if src == connect_area:
                    continue
                if connect_area.ruler() == warrior:
                    dests.append(connect_area)

        return dests

    def recruit(self, faction: Faction, area: Area = None):
        if faction == Faction.MARQUISE:
            for area in self.board.areas:
                total_recruiters = area.buildings.count(Building.RECRUITER)
                if total_recruiters > 0:
                    self.add_warrior(faction, area, min(total_recruiters, self.marquise.reserved_warriors))
                    LOGGER.info(
                        "{}:{}:{}:MARQUISE adds warrior in clearing #{}".format(self.ui_turn_player, self.phase,
                                                                                self.sub_phase,
                                                                                area.area_index))
        elif faction == Faction.EYRIE:
            amount = 1
            if self.eyrie.get_active_leader() == EyrieLeader.CHARISMATIC:
                amount = 2
            if self.eyrie.reserved_warriors >= amount:
                self.add_warrior(faction, area, amount)

    def generate_actions_select_buildable_clearing(self, faction):
        buildable_clearings = self.get_buildable_clearings(faction)
        actions = []

        if faction == Faction.MARQUISE:
            for clearing in buildable_clearings:
                actions.append(
                    Action("{}".format(clearing),
                           perform(self.marquise_daylight_build_select_building, clearing)))

        elif faction == Faction.EYRIE:
            for clearing in buildable_clearings:
                actions.append(
                    Action("{}".format(clearing),
                           perform(self.eyrie_build, clearing)))

        return actions

    def generate_actions_select_building(self, faction, clearing):
        buildings = self.get_buildable_buildings(faction, clearing)
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

            self.gain_vp(Faction.MARQUISE, self.marquise.get_reward(building))
            wood_cost = self.marquise.build_action_update(building)

            self.remove_wood(wood_cost, self.count_woods_from_clearing(clearing)[0])

            LOGGER.info(
                "{}:{}:{}:MARQUISE builds {} in clearing #{}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                     building, clearing.area_index))
            self.prompt = "The {} has been build at clearing #{}.".format(building, clearing.area_index)
            self.marquise_action_count -= 1
            self.set_actions([Action('Next', perform(self.marquise_daylight_2))])
        elif faction == Faction.EYRIE:
            self.eyrie_build(clearing)

    def get_buildable_clearings(self, faction) -> list[Area]:
        buildable_clearings: list[Area] = []

        if faction == Faction.MARQUISE:
            for clearing in self.board.areas:
                if clearing.ruler() == Warrior.MARQUISE and clearing.buildings.count(
                        Building.EMPTY) > 0 and self.marquise_get_min_cost_building() <= \
                        self.count_woods_from_clearing(clearing)[1]:
                    buildable_clearings.append(clearing)

        elif faction == Faction.EYRIE:
            decree_can_build_in: {Suit: bool} = {}
            for suit in Suit:
                decree_can_build_in[suit] = count_decree_action_static(self.decree_counter, DecreeAction.BUILD, suit)

            for clearing in self.board.areas:
                if self.eyrie.roost_tracker >= 7:  # roost tracker in range [0, 7]
                    break
                if clearing.ruler() != Warrior.EYRIE:
                    continue
                if clearing.buildings.count(Building.EMPTY) == 0:
                    continue
                if clearing.buildings.count(Building.ROOST) != 0:
                    continue
                if decree_can_build_in[clearing.suit] == 0 and decree_can_build_in[Suit.BIRD] == 0:
                    continue
                buildable_clearings.append(clearing)

        return buildable_clearings

    def get_buildable_buildings(self, faction, clearing):
        buildings = []

        if faction == Faction.MARQUISE:
            woods = self.count_woods_from_clearing(clearing)[1]
            cost = self.marquise.building_cost
            building_tracker = self.marquise.building_trackers

            for building, tracker in building_tracker.items():
                if tracker < 6 and woods >= cost[tracker]:
                    buildings.append(building)
        elif faction == Faction.EYRIE:
            buildings.append(Building.ROOST)
        return buildings

    def count_buildings(self, building):
        total = 0
        for area in self.board.areas:
            total += area.buildings.count(building)
        return total

    def select_clearing_battle(self, attacker, continuation_func):
        actions = self.generate_actions_select_clearing_battle(attacker, continuation_func)
        self.prompt = "Select Clearing"
        self.set_actions(actions)

    def generate_actions_select_clearing_battle(self, attacker, continuation_func) -> list[Action]:
        clearings = self.get_battlable_clearing(attacker)
        actions = []

        for clearing in clearings:
            actions.append(
                Action("{}".format(clearing),
                       perform(self.select_enemy_faction_battle, attacker, clearing, continuation_func)))

        return actions

    def select_enemy_faction_battle(self, attacker, clearing, continuation_func):
        actions = self.generate_actions_select_enemy_faction_battle(attacker, clearing, continuation_func)
        self.prompt = "Select Enemy Faction"
        self.set_actions(actions)

    def generate_actions_select_enemy_faction_battle(self, faction: Faction, clearing: Area, continuation_func) -> list[
        Action]:
        enemy_factions: list[Faction] = self.get_available_enemy_tokens_from_clearing(faction, clearing)
        actions: list[Action] = []

        for enemy_faction in enemy_factions:
            actions.append(
                Action("{}".format(enemy_faction),
                       perform(self.initiate_battle, faction, enemy_faction, clearing, continuation_func)))

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

    def initiate_battle(self, attacker, defender, clearing: Area, continuation_func):
        LOGGER.info(
            "{}:{}:{}:battle:{} initiate battle on {} in clearing #{}".format(self.ui_turn_player, self.phase,
                                                                              self.sub_phase,
                                                                              attacker, defender, clearing.area_index))
        attacker_board = self.faction_to_faction_board(attacker)
        defender_board = self.faction_to_faction_board(defender)
        atk_scouting_party = [card for card in attacker_board.crafted_cards if
                              card.name == PlayingCardName.SCOUTING_PARTY]
        def_ambush = [card for card in defender_board.cards_in_hand if
                      card.name == PlayingCardName.AMBUSH and (card.suit == Suit.BIRD or card.suit == clearing.suit)]

        if len(atk_scouting_party) > 0 or len(def_ambush) == 0:
            self.roll_dice(attacker, defender, clearing, continuation_func)
        else:
            self.defender_use_ambush(attacker, defender, clearing, continuation_func)

    def defender_use_ambush(self, attacker, defender, clearing, continuation_func):
        self.ui_turn_player = defender
        self.prompt = "{}: Use Ambush Card?".format(defender)

        defender_board = self.faction_to_faction_board(defender)
        def_ambush_actions = []
        def_ambush = [card for card in defender_board.cards_in_hand if
                      card.name == PlayingCardName.AMBUSH and (card.suit == Suit.BIRD or card.suit == clearing.suit)]
        for card in def_ambush:
            def_ambush_actions.append(Action('Discard {} ({})'.format(card.name, card.suit),
                                             perform(self.attacker_use_ambush, card, attacker, defender, clearing,
                                                     continuation_func)))

        self.set_actions(
            def_ambush_actions + [
                Action('Skip', perform(self.roll_dice, attacker, defender, clearing, continuation_func))])

    def attacker_use_ambush(self, ambush_discarded, attacker, defender, clearing, continuation_func):
        LOGGER.info(
            "{}:{}:{}:battle:{} discard AMBUSH".format(self.ui_turn_player, self.phase, self.sub_phase, defender))
        defender_board = self.faction_to_faction_board(defender)
        self.discard_card(defender_board.cards_in_hand, ambush_discarded)

        self.ui_turn_player = attacker
        self.prompt = "{}: Use Ambush Card?".format(attacker)

        attacker_board = self.faction_to_faction_board(attacker)
        atk_ambush = [card for card in attacker_board.cards_in_hand if card.name == PlayingCardName.AMBUSH]

        if len(atk_ambush) == 0:
            self.resolve_hits(attacker, defender, 0, 0, 0, 2, clearing, continuation_func, self.roll_dice)
        else:
            atk_ambush_actions = []
            for card in atk_ambush:
                atk_ambush_actions.append(Action('Discard {} ({})'.format(card.name, card.suit),
                                                 perform(self.foil_ambush, card, attacker, defender, clearing,
                                                         continuation_func)))
            self.set_actions(
                atk_ambush_actions
                + [Action('Skip',
                          perform(self.resolve_hits, attacker, defender, 0, 0, 0, 2, clearing, continuation_func,
                                  self.roll_dice))]
            )

    def foil_ambush(self, ambush_discarded, attacker, defender, clearing, continuation_func):
        LOGGER.info(
            "{}:{}:{}:battle:{} discard AMBUSH".format(self.ui_turn_player, self.phase, self.sub_phase, attacker))
        attacker_board = self.faction_to_faction_board(attacker)
        self.discard_card(attacker_board.cards_in_hand, ambush_discarded)
        self.roll_dice(attacker, defender, clearing, continuation_func)

    def roll_dice(self, attacker, defender, clearing, continuation_func):

        # After ambush, check if there are remaining attacker's warrior.
        if clearing.warrior_count[faction_to_warrior(attacker)] == 0:
            continuation_func()
        else:
            dices: list[int] = [randint(0, 3), randint(0, 3)]
            attacker_roll: int = max(dices)
            defender_roll: int = min(dices)

            defender_defenseless_extra_hits: int = 1 if (
                    clearing.get_warrior_count(faction_to_warrior(defender)) == 0) else 0

            attacker_extra_hits: int = 1 if (
                    attacker == Faction.EYRIE and self.eyrie.get_active_leader() == EyrieLeader.COMMANDER) else 0
            defender_extra_hits: int = 0

            LOGGER.info(
                "{}:{}:{}:battle:{} rolls {}, {} rolls {}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                  attacker, attacker_roll, defender, defender_roll))

            self.attacker_activate_battle_ability_card(attacker, defender, attacker_roll, defender_roll,
                                                       attacker_extra_hits + defender_defenseless_extra_hits,
                                                       defender_extra_hits, clearing,
                                                       continuation_func)

    def attacker_activate_battle_ability_card(self, attacker, defender, attacker_rolled_hits, defender_rolled_hits,
                                              attacker_extra_hits,
                                              defender_extra_hits, clearing, continuation_func):
        LOGGER.info(
            "{}:{}:{}:battle: Total hits: {}: ({}+{}) hits, {}: ({}+{}) hits".format(self.ui_turn_player, self.phase,
                                                                                     self.sub_phase,
                                                                                     attacker,
                                                                                     attacker_rolled_hits + attacker_extra_hits,
                                                                                     attacker_rolled_hits,
                                                                                     attacker_extra_hits,
                                                                                     defender,
                                                                                     defender_rolled_hits + defender_extra_hits,
                                                                                     defender_rolled_hits,
                                                                                     defender_extra_hits))

        attacker_faction_board = self.faction_to_faction_board(attacker)

        atk_brutal_tactics = [card for card in attacker_faction_board.crafted_cards if
                              card.name == PlayingCardName.BRUTAL_TACTICS]
        atk_armorers = [card for card in attacker_faction_board.crafted_cards if card.name == PlayingCardName.ARMORERS]

        atk_actions = []

        if len(atk_brutal_tactics) > 0 and attacker_faction_board.activated_card.count(atk_brutal_tactics[0]) < 1:
            brutal_tactics_card = atk_brutal_tactics[0]
            atk_actions.append(Action('Use {} ({})'.format(brutal_tactics_card.name, brutal_tactics_card.suit),
                                      perform(self.brutal_tactics, brutal_tactics_card, attacker, defender,
                                              attacker_rolled_hits, defender_rolled_hits, attacker_extra_hits,
                                              defender_extra_hits, clearing, continuation_func)))

        if len(atk_armorers) > 0 and attacker_faction_board.activated_card.count(atk_armorers[0]) < 1:
            armorers_card = atk_armorers[0]
            atk_actions.append(Action('Use {} ({})'.format(armorers_card.name, armorers_card.suit),
                                      perform(self.armorers, attacker, armorers_card, attacker, defender,
                                              attacker_rolled_hits, defender_rolled_hits, attacker_extra_hits,
                                              defender_extra_hits, clearing, continuation_func,
                                              self.attacker_activate_battle_ability_card)))

        if len(atk_actions) > 0:
            self.ui_turn_player = attacker
            self.prompt = "{}: Activate Battle Ability Card?".format(attacker)
            self.set_actions(atk_actions + [Action('Skip',
                                                   perform(self.defender_activate_battle_ability_card, attacker,
                                                           defender,
                                                           attacker_rolled_hits, defender_rolled_hits,
                                                           attacker_extra_hits,
                                                           defender_extra_hits, clearing, continuation_func))])
        else:
            self.defender_activate_battle_ability_card(attacker, defender, attacker_rolled_hits, defender_rolled_hits,
                                                       attacker_extra_hits,
                                                       defender_extra_hits, clearing, continuation_func)

    def defender_activate_battle_ability_card(self, attacker, defender, attacker_rolled_hits, defender_rolled_hits,
                                              attacker_extra_hits,
                                              defender_extra_hits, clearing, continuation_func):
        LOGGER.info(
            "{}:{}:{}:battle: Total hits: {}: ({}+{}) hits, {}: ({}+{}) hits".format(self.ui_turn_player, self.phase,
                                                                                     self.sub_phase,
                                                                                     attacker,
                                                                                     attacker_rolled_hits + attacker_extra_hits,
                                                                                     attacker_rolled_hits,
                                                                                     attacker_extra_hits,
                                                                                     defender,
                                                                                     defender_rolled_hits + defender_extra_hits,
                                                                                     defender_rolled_hits,
                                                                                     defender_extra_hits))

        defender_faction_board = self.faction_to_faction_board(defender)

        def_sappers = [card for card in defender_faction_board.crafted_cards if card.name == PlayingCardName.SAPPERS]
        def_armorers = [card for card in defender_faction_board.crafted_cards if card.name == PlayingCardName.ARMORERS]

        def_actions = []

        if len(def_sappers) > 0 and defender_faction_board.activated_card.count(def_sappers[0]) < 1:
            sappers_card = def_sappers[0]
            def_actions.append(Action('Use {} ({})'.format(sappers_card.name, sappers_card.suit),
                                      perform(self.sappers, sappers_card, attacker, defender,
                                              attacker_rolled_hits, defender_rolled_hits, attacker_extra_hits,
                                              defender_extra_hits, clearing, continuation_func)))

        if len(def_armorers) > 0 and defender_faction_board.activated_card.count(def_armorers[0]) < 1:
            armorers_card = def_armorers[0]
            def_actions.append(Action('Use {} ({})'.format(armorers_card.name, armorers_card.suit),
                                      perform(self.armorers, defender, armorers_card, attacker, defender,
                                              attacker_rolled_hits, defender_rolled_hits, attacker_extra_hits,
                                              defender_extra_hits, clearing, continuation_func,
                                              self.defender_activate_battle_ability_card)))

        if len(def_actions) > 0:
            self.ui_turn_player = defender
            self.prompt = "{}: Activate Battle Ability Card?".format(defender)
            self.set_actions(def_actions + [Action('Skip',
                                                   perform(self.resolve_hits, attacker, defender,
                                                           attacker_rolled_hits, defender_rolled_hits,
                                                           attacker_extra_hits,
                                                           defender_extra_hits, clearing, continuation_func))])
        else:
            self.resolve_hits(attacker, defender, attacker_rolled_hits, defender_rolled_hits,
                              attacker_extra_hits,
                              defender_extra_hits, clearing, continuation_func)

    def brutal_tactics(self, brutal_tactics_card, attacker, defender, attacker_rolled_hits, defender_rolled_hits,
                       attacker_extra_hits,
                       defender_extra_hits, clearing, continuation_func):
        LOGGER.info(
            "{}:{}:{}:battle:{} use BRUTAL TACTICS".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                           attacker))
        attacker_faction_board = self.faction_to_faction_board(attacker)
        attacker_faction_board.activated_card.append(brutal_tactics_card)
        self.gain_vp(defender, 1)
        self.attacker_activate_battle_ability_card(attacker, defender, attacker_rolled_hits, defender_rolled_hits,
                                                   attacker_extra_hits + 1,
                                                   defender_extra_hits, clearing, continuation_func)

    def armorers(self, faction, armorers_card, attacker, defender,
                 attacker_rolled_hits, defender_rolled_hits, attacker_extra_hits,
                 defender_extra_hits, clearing, continuation_func, redirect_func):
        LOGGER.info(
            "{}:{}:{}:battle:{} discard ARMORERS".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                         faction))

        faction_board = self.faction_to_faction_board(faction)
        faction_board.activated_card.append(armorers_card)
        self.discard_card(faction_board.crafted_cards, armorers_card)

        if faction == attacker:
            redirect_func(attacker, defender,
                          attacker_rolled_hits, 0, attacker_extra_hits,
                          defender_extra_hits, clearing, continuation_func)
        elif faction == defender:
            redirect_func(attacker, defender,
                          0, defender_rolled_hits, attacker_extra_hits,
                          defender_extra_hits, clearing, continuation_func)

    def sappers(self, sappers_card, attacker, defender, attacker_rolled_hits, defender_rolled_hits, attacker_extra_hits,
                defender_extra_hits, clearing, continuation_func):
        LOGGER.info(
            "{}:{}:{}:battle:{} discard BRUTAL TACTICS".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                               defender))

        defender_faction_board = self.faction_to_faction_board(defender)
        defender_faction_board.activated_card.append(sappers_card)
        self.discard_card(defender_faction_board.crafted_cards, sappers_card)
        self.defender_activate_battle_ability_card(attacker, defender, attacker_rolled_hits, defender_rolled_hits,
                                                   attacker_extra_hits,
                                                   defender_extra_hits + 1, clearing, continuation_func)

    def resolve_hits(self, attacker, defender, attacker_rolled_hits, defender_rolled_hits, attacker_extra_hits,
                     defender_extra_hits, clearing, continuation_func,
                     redirect_func=None):

        attacker_faction_board = self.faction_to_faction_board(attacker)
        defender_faction_board = self.faction_to_faction_board(defender)

        attacker_total_hits: int = min(attacker_rolled_hits, clearing.get_warrior_count(
            faction_to_warrior(attacker))) + attacker_extra_hits
        defender_total_hits: int = min(defender_rolled_hits,
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

        self.gain_vp(attacker, attacker_total_vp)
        self.gain_vp(defender, defender_total_vp)

        LOGGER.info(
            "{}:{}:{}:battle: {} vs {}, total hits {}:{}, vps gained {}:{}".format(self.ui_turn_player, self.phase,
                                                                                   self.sub_phase,
                                                                                   attacker, defender,
                                                                                   attacker_total_hits,
                                                                                   defender_total_hits,
                                                                                   attacker_total_vp, defender_total_vp)
        )

        if attacker == Faction.MARQUISE and removed_attacker_warriors > 0 and self.marquise_field_hospital_check(
                clearing):
            self.resolve_marquise_field_hospital(attacker, defender, attacker_remaining_hits, defender_remaining_hits,
                                                 removed_attacker_warriors, clearing, continuation_func, redirect_func)
        elif defender == Faction.MARQUISE and removed_defender_warriors > 0 and self.marquise_field_hospital_check(
                clearing):
            self.resolve_marquise_field_hospital(attacker, defender, attacker_remaining_hits, defender_remaining_hits,
                                                 removed_defender_warriors, clearing, continuation_func, redirect_func)
        else:
            self.resolve_remaining_hits(attacker, defender, attacker_remaining_hits, defender_remaining_hits, clearing,
                                        continuation_func, redirect_func)

    def resolve_marquise_field_hospital(self, attacker, defender, attacker_remaining_hits, defender_remaining_hits,
                                        removed_warriors, clearing, continuation_func,
                                        redirect_func):  # TODO: if attacker == marquise, marquise field hospital trigger immediately , otherwise , trigger at the birdsong
        self.ui_turn_player = Faction.MARQUISE
        self.prompt = "MARQUISE: Discard a card matching warrior's clearing to bring {} warriors back to the keep.".format(
            removed_warriors)
        self.set_actions(
            self.generate_actions_field_hospital_select_card_to_discard(removed_warriors, attacker,
                                                                        defender, attacker_remaining_hits,
                                                                        defender_remaining_hits,
                                                                        clearing, continuation_func, redirect_func)
            + [Action('Next', perform(self.resolve_remaining_hits, attacker, defender, attacker_remaining_hits,
                                      defender_remaining_hits, clearing, continuation_func, redirect_func))]
        )

    def marquise_field_hospital_check(self, clearing: Area):
        return len(self.marquise_field_hospital_get_cards(clearing)) > 0

    def marquise_field_hospital_get_cards(self, clearing):
        return [card for card in self.marquise.cards_in_hand if card.suit == clearing.suit]

    def generate_actions_field_hospital_select_card_to_discard(self, removed_warriors, attacker, defender,
                                                               attacker_remaining_hits, defender_remaining_hits,
                                                               clearing, continuation_func, redirect_func):
        discardable_cards = self.marquise_field_hospital_get_cards(clearing)
        actions = []

        for card in discardable_cards:
            actions.append(
                Action("{} ({})".format(card.name, card.suit),
                       perform(self.marquise_field_hospital, card, removed_warriors, attacker, defender,
                               attacker_remaining_hits,
                               defender_remaining_hits, clearing, continuation_func, redirect_func)))

        return actions

    def marquise_field_hospital(self, card, removed_warriors, attacker, defender, attacker_remaining_hits,
                                defender_remaining_hits, battle_clearing, continuation_func, redirect_func):
        LOGGER.info(
            "{}:{}:{}:battle:{} use field hospital, discarding {} ({})".format(self.ui_turn_player, self.phase,
                                                                               self.sub_phase,
                                                                               Faction.MARQUISE,
                                                                               card.name, card.suit))

        self.discard_card(self.marquise.cards_in_hand, card)
        for clearing in self.board.areas:
            if clearing.token_count[Token.CASTLE] > 0:
                clearing.add_warrior(Warrior.MARQUISE, removed_warriors)
                break

        self.resolve_remaining_hits(attacker, defender, attacker_remaining_hits, defender_remaining_hits,
                                    battle_clearing,
                                    continuation_func, redirect_func)

    def resolve_remaining_hits(self, attacker, defender, attacker_remaining_hits, defender_remaining_hits, clearing,
                               continuation_func, redirect_func):
        LOGGER.info(
            "{}:{}:{}:battle: {} vs {}, remaining hits {}:{}".format(self.ui_turn_player, self.phase,
                                                                     self.sub_phase,
                                                                     attacker, defender,
                                                                     attacker_remaining_hits,
                                                                     defender_remaining_hits)
        )
        if attacker_remaining_hits == 0 and defender_remaining_hits == 0:
            if redirect_func is not None:
                redirect_func(attacker, defender, clearing, continuation_func)
            else:
                continuation_func()
        elif defender_remaining_hits > 0:
            self.select_piece_to_remove(attacker, attacker, defender,
                                        attacker_remaining_hits,
                                        defender_remaining_hits,
                                        clearing, continuation_func, redirect_func)
        elif attacker_remaining_hits > 0:
            self.select_piece_to_remove(defender, attacker, defender,
                                        attacker_remaining_hits,
                                        defender_remaining_hits,
                                        clearing, continuation_func, redirect_func)

    def select_piece_to_remove(self, selecting_faction, attacker, defender, attacker_remaining_hits,
                               defender_remaining_hits, clearing,
                               continuation_func, redirect_func):
        self.ui_turn_player = selecting_faction
        self.prompt = "{}: Select Piece to Remove".format(selecting_faction)
        actions = self.generate_actions_select_piece_to_remove(selecting_faction, attacker, defender,
                                                               attacker_remaining_hits,
                                                               defender_remaining_hits,
                                                               clearing, continuation_func, redirect_func)
        if len(actions) == 0:
            if selecting_faction == attacker:
                self.resolve_remaining_hits(attacker, defender, attacker_remaining_hits, 0, clearing,
                                            continuation_func, redirect_func)
            elif selecting_faction == defender:
                self.resolve_remaining_hits(attacker, defender, 0, defender_remaining_hits, clearing,
                                            continuation_func, redirect_func)
        else:
            self.set_actions(actions)

    def generate_actions_select_piece_to_remove(self, selecting_faction, attacker, defender, attacker_remaining_hits,
                                                defender_remaining_hits, clearing,
                                                continuation_func, redirect_func):
        actions = []
        buildings = faction_to_buildings(selecting_faction)
        tokens = faction_to_tokens(selecting_faction)

        if selecting_faction == Faction.MARQUISE:
            for token in tokens:
                if token == Token.WOOD and clearing.token_count[token] > 0:
                    actions.append(
                        Action("Wood",
                               perform(self.remove_piece, selecting_faction, Token.WOOD, attacker, defender,
                                       attacker_remaining_hits, defender_remaining_hits, clearing,
                                       continuation_func, redirect_func))
                    )
            for building in buildings:
                if clearing.buildings.count(building) > 0:
                    actions.append(
                        Action(building.name,
                               perform(self.remove_piece, selecting_faction, building, attacker, defender,
                                       attacker_remaining_hits, defender_remaining_hits, clearing,
                                       continuation_func, redirect_func))
                    )

        elif selecting_faction == Faction.EYRIE:
            for building in buildings:
                if clearing.buildings.count(building) > 0:
                    actions.append(
                        Action(building.name,
                               perform(self.remove_piece, selecting_faction, building, attacker, defender,
                                       attacker_remaining_hits, defender_remaining_hits, clearing,
                                       continuation_func, redirect_func))
                    )

        return actions

    def remove_piece(self, selecting_faction, piece, attacker, defender,
                     attacker_remaining_hits, defender_remaining_hits, clearing,
                     continuation_func, redirect_func):

        if isinstance(piece, Building):
            if selecting_faction == Faction.MARQUISE:
                self.marquise.building_trackers[piece] -= 1
            elif selecting_faction == Faction.EYRIE:
                self.eyrie.roost_tracker -= 1
            clearing.remove_building(piece)
        elif isinstance(piece, Token):
            clearing.remove_token(piece)

        if selecting_faction == attacker:
            LOGGER.info(
                "{}:{}:{}:battle:{} remove {}'s {}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                           defender, attacker, piece))
            self.gain_vp(defender, 1)
            self.resolve_remaining_hits(attacker, defender, attacker_remaining_hits, defender_remaining_hits - 1,
                                        clearing,
                                        continuation_func, redirect_func)
        else:
            LOGGER.info(
                "{}:{}:{}:battle:{} remove {}'s {}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                           attacker, defender, piece))
            self.gain_vp(attacker, 1)
            self.resolve_remaining_hits(attacker, defender, attacker_remaining_hits - 1, defender_remaining_hits,
                                        clearing,
                                        continuation_func, redirect_func)

    def get_building_count_by_suit(self, building: Building | str) -> {Suit: int}:
        building_count: {Suit: int} = {
            Suit.BIRD: 0,
            Suit.FOX: 0,
            Suit.RABBIT: 0,
            Suit.MOUSE: 0
        }

        for clearing in self.board.areas:
            if building in clearing.buildings:
                building_count[clearing.suit] += clearing.buildings.count(building)

        return building_count

    def generate_actions_select_card_to_discard(self, faction):
        faction_board = self.faction_to_faction_board(faction)
        actions = []

        for card in faction_board.cards_in_hand:
            actions.append(Action('Discard {} ({})'.format(card.name, card.suit),
                                  perform(self.select_card_to_discard, faction, card)))

        return actions

    def select_card_to_discard(self, faction: Faction, card: PlayingCard):
        faction_board = self.faction_to_faction_board(faction)
        LOGGER.info(
            "{}:{}:{}:{}:{} ({}) discarded".format(self.ui_turn_player, self.phase, self.sub_phase, faction,
                                                   card.name, card.suit))
        self.discard_card(faction_board.cards_in_hand, card)
        card_in_hand_count = len(faction_board.cards_in_hand)
        if card_in_hand_count > 5:
            self.prompt = "Select card to discard down to 5 cards (currently {} cards in hand)".format(
                card_in_hand_count)
            self.set_actions(self.generate_actions_select_card_to_discard(faction))
        else:
            if faction == Faction.MARQUISE:
                self.marquise_evening_discard_card()
                pass
            elif faction == Faction.EYRIE:
                self.eyrie_evening_to_marquise()

    def generate_actions_activate_dominance_card(self, faction: Faction, continuation_func: any) -> list[Action]:
        actions: list[Action] = []
        faction_board = self.faction_to_faction_board(faction)

        if self.board.faction_points[faction] < 10:
            return []

        if faction_board.dominance_card is not None:
            return []

        for card in faction_board.cards_in_hand:
            if card.name not in PlayingCard.DOMINANCE_CARD_NAMES:
                continue
            actions.append(Action("Activate {}".format(card.name),
                                  perform(self.activate_dominance_card, faction, card, perform(continuation_func))))

        return actions

    def activate_dominance_card(self, faction: Faction, card: PlayingCard, continuation_func: any):
        if config['game']['allow-dominance-card']:
            LOGGER.info(
                "{}:{}:{}:{}:activate_dominance_card {} ".format(self.ui_turn_player, self.phase, self.sub_phase, faction,
                                                                 card.name))

            faction_board = self.faction_to_faction_board(faction)

            faction_board.dominance_card = card
            faction_board.cards_in_hand.remove(card)

        continuation_func()

    def generate_actions_take_dominance_card(self, faction: Faction, continuation_func: any) -> list[Action]:
        actions: list[Action] = []
        faction_board = self.faction_to_faction_board(faction)

        if faction_board.dominance_card is not None:
            return []

        for card in faction_board.cards_in_hand:
            for dominance_card in self.discard_pile_dominance:
                if dominance_card.suit == card.suit:
                    actions.append(Action("Take {} by spending {}".format(dominance_card.name, card.name),
                                          perform(self.take_dominance_card, faction, dominance_card, card,
                                                  perform(continuation_func))))

        return actions

    def take_dominance_card(self, faction: Faction, dominance_card: PlayingCard, card_to_spend: PlayingCard,
                            continuation_func: any):
        LOGGER.info(
            "{}:{}:{}:{}:take_dominance_card {} by spending {}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                       faction,
                                                                       dominance_card.name, card_to_spend.name))

        faction_board = self.faction_to_faction_board(faction)

        self.discard_card(faction_board.cards_in_hand, card_to_spend)

        faction_board.cards_in_hand.append(dominance_card)
        self.discard_pile_dominance.remove(dominance_card)

        continuation_func()

    def generate_actions_cards_birdsong(self, faction, continuation_func):
        actions = []
        faction_board = self.faction_to_faction_board(faction)
        for card in faction_board.crafted_cards:
            if faction_board.activated_card.count(card) > 0:
                continue
            if card.name == PlayingCardName.ROYAL_CLAIM:
                actions.append(Action('Discard {}'.format(card.name),
                                      perform(self.royal_claim, faction, card, continuation_func)))
            if card.name == PlayingCardName.STAND_AND_DELIVER:
                actions.append(
                    Action('Use {} effect'.format(card.name),
                           perform(self.stand_and_deliver_select_faction, faction, card, continuation_func)))
        return actions

    def royal_claim(self, faction, card, continuation_func):
        faction_board = self.faction_to_faction_board(faction)

        self.discard_card(faction_board.crafted_cards, card)

        gained_vp = 0
        for clearing in self.board.areas:
            if clearing.ruler() == faction_to_warrior(faction):
                gained_vp += 1
        self.gain_vp(faction, gained_vp)

        continuation_func()

    def stand_and_deliver_select_faction(self, faction, card, continuation_func):
        faction_board = self.faction_to_faction_board(faction)
        faction_board.activated_card.append(card)
        self.prompt = "Select Faction"
        self.set_actions(self.generate_actions_stand_and_deliver_select_faction(faction, continuation_func))

    def generate_actions_stand_and_deliver_select_faction(self, faction, continuation_func):
        actions = []
        available_faction = [Faction.MARQUISE, Faction.EYRIE]
        available_faction.remove(faction)

        for enemy_faction in available_faction:
            if len(self.faction_to_faction_board(enemy_faction).cards_in_hand) > 0:
                actions.append(
                    Action('{}'.format(enemy_faction),
                           perform(self.stand_and_deliver, faction, enemy_faction, continuation_func)))
        return actions

    def stand_and_deliver(self, faction, stolen_faction, continuation_func):
        faction_board = self.faction_to_faction_board(faction)
        stolen_faction_board = self.faction_to_faction_board(stolen_faction)

        random_card = random.choice(stolen_faction_board.cards_in_hand)

        self.discard_card(stolen_faction_board.cards_in_hand, random_card)
        faction_board.cards_in_hand.append(random_card)

        self.gain_vp(stolen_faction, 1)

        continuation_func()

    def better_burrow_bank(self,
                           faction):  # There is only 2 faction. So when this effect activate, both faction draws a card.
        faction_board = self.faction_to_faction_board(faction)
        cards = [card for card in faction_board.crafted_cards if card.name == PlayingCardName.BETTER_BURROW_BANK]
        if len(cards) > 0:
            for faction in [Faction.MARQUISE, Faction.EYRIE]:
                self.take_card_from_draw_pile(faction)

    def generate_actions_cards_daylight(self, faction, continuation_func):
        actions = []
        faction_board = self.faction_to_faction_board(faction)
        for card in faction_board.crafted_cards:
            if faction_board.activated_card.count(card) > 0:
                continue
            if card.name == PlayingCardName.TAX_COLLECTOR:
                actions.append(Action('Use {} effect'.format(card.name),
                                      perform(self.tax_collector_select_clearing, faction, continuation_func)))
            # if card.name == PlayingCardName.COMMAND_WARREN:
            #     actions.append(Action('Use {} effect'.format(card.name),
            #                           perform(self.command_warren, faction, continuation_func)))

        return actions

    # def command_warren(self, faction, continuation_func):
    #     self.set_actions(self.generate_actions_select_clearing_battle(faction))

    def tax_collector_select_clearing(self, faction, continuation_func):
        self.prompt = "Select Clearing"
        self.set_actions(self.generate_actions_tax_collector_select_clearing(faction, continuation_func))

    def generate_actions_tax_collector_select_clearing(self, faction, continuation_func):
        actions = []

        for clearing in self.board.areas:
            if clearing.warrior_count[faction_to_warrior(faction)] > 0:
                actions.append(Action('{}'.format(clearing.area_index),
                                      perform(self.tax_collector, faction, clearing, continuation_func)))

        return actions

    def tax_collector(self, faction, clearing, continuation_func):
        warrior = faction_to_warrior(faction)
        clearing.remove_warrior(warrior, 1)
        self.take_card_from_draw_pile(faction, 1)

        continuation_func()

    def faction_to_faction_board(self, faction: Faction) -> FactionBoard:
        if faction == Faction.MARQUISE:
            return self.marquise
        if faction == Faction.EYRIE:
            return self.eyrie

    #####
    # DRAW
    def draw(self, screen: Surface):
        # Fill Black
        screen.fill("black")

        self.board.turn_player = self.ui_turn_player
        self.board.turn_count = self.turn_count

        self.board.draw(screen)
        self.marquise.draw(screen)
        self.eyrie.draw(screen)
