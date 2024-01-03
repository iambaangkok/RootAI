from __future__ import annotations

import logging
import random
from copy import deepcopy
from enum import StrEnum
from itertools import combinations
from random import shuffle, randint

from pygame import Vector2, Surface

from src.config import Config, Colors
from src.game.Area import Area
from src.game.Board import Board
from src.game.Building import Building
from src.game.EyrieBoard import EyrieBoard, DecreeAction, EyrieLeader, LOYAL_VIZIER, \
    count_decree_action_static
from src.game.Faction import Faction
from src.game.FactionBoard import FactionBoard
from src.game.MarquiseBoard import MarquiseBoard
from src.game.Card import Card, CardName, CardPhase, build_card
from src.game.Suit import Suit
from src.game.Token import Token
from src.game.Warrior import Warrior
from src.utils.utils import perform, faction_to_warrior, faction_to_tokens, faction_to_buildings, get_card

import yaml

config = yaml.safe_load(open("config/config.yml"))

LOGGER = logging.getLogger('game_logger')

phase_mapping: dict[str, int] = {
    "BIRDSONG": 0,
    "DAYLIGHT": 1,
    "EVENING": 2,
    "TURMOIL": 3
}

phase_mapping_reversed = [key for key in phase_mapping]


class Phase(StrEnum):
    BIRDSONG = "BIRDSONG"
    DAYLIGHT = "DAYLIGHT"
    EVENING = "EVENING"
    TURMOIL = "TURMOIL"

    def to_number(self) -> int:
        return phase_mapping[self.name]

    def to_phase(phase_id: int) -> Phase:
        return Phase[phase_mapping_reversed[phase_id]]


class Action:
    def __init__(self, name: str, function: any = None):
        self.name: str = name
        self.function: any = function

    def __str__(self):
        return "Action {}".format(self.name)

    def get(self):
        return self.name, self.function

    def __eq__(self, other: Action):
        return self.name == other.name


class Game:
    def __init__(self):
        self.running: bool = True

        # Game Data
        self.turn_count: int = 0
        self.ui_turn_player: Faction = Faction.MARQUISE
        self.turn_player: Faction = Faction.MARQUISE
        self.phase: Phase = Phase.BIRDSONG
        self.sub_phase = 10001
        self.is_in_action_sub_phase: bool = False

        # Board Game Components
        self.draw_pile: list[Card] = [build_card(i) for i in range(0, 54)]
        self.discard_pile: list[Card] = []
        self.discard_pile_dominance: list[Card] = []

        # Board, Areas (Clearings)
        areas_offset_y = 0.05
        areas_radius = Board.rect.width * Area.size_ratio
        areas: list[Area] = [
            Area(0, Vector2(Board.rect.x + Board.rect.width * 0.12,
                            Board.rect.y + Board.rect.height * (0.20 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.EMPTY]),
            Area(1, Vector2(Board.rect.x + Board.rect.width * 0.55,
                            Board.rect.y + Board.rect.height * (0.15 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.EMPTY, Building.EMPTY]),
            Area(2, Vector2(Board.rect.x + Board.rect.width * 0.88,
                            Board.rect.y + Board.rect.height * (0.25 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.EMPTY, Building.EMPTY]),

            Area(3, Vector2(Board.rect.x + Board.rect.width * 0.43,
                            Board.rect.y + Board.rect.height * (0.35 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.EMPTY]),

            Area(4, Vector2(Board.rect.x + Board.rect.width * 0.10,
                            Board.rect.y + Board.rect.height * (0.45 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.EMPTY, Building.EMPTY]),
            Area(5, Vector2(Board.rect.x + Board.rect.width * 0.34,
                            Board.rect.y + Board.rect.height * (0.58 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.EMPTY]),
            Area(6, Vector2(Board.rect.x + Board.rect.width * 0.66,
                            Board.rect.y + Board.rect.height * (0.53 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.EMPTY, Building.EMPTY]),
            Area(7, Vector2(Board.rect.x + Board.rect.width * 0.90,
                            Board.rect.y + Board.rect.height * (0.56 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.WORKSHOP]),

            Area(8, Vector2(Board.rect.x + Board.rect.width * 0.12,
                            Board.rect.y + Board.rect.height * (0.83 - areas_offset_y)), areas_radius,
                 Suit.RABBIT, [Building.EMPTY]),
            Area(9, Vector2(Board.rect.x + Board.rect.width * 0.39,
                            Board.rect.y + Board.rect.height * (0.88 - areas_offset_y)), areas_radius,
                 Suit.FOX, [Building.EMPTY, Building.EMPTY]),
            Area(10, Vector2(Board.rect.x + Board.rect.width * 0.62,
                             Board.rect.y + Board.rect.height * (0.80 - areas_offset_y)), areas_radius,
                 Suit.MOUSE, [Building.RECRUITER, Building.EMPTY]),
            Area(11, Vector2(Board.rect.x + Board.rect.width * 0.84,
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
        self.actions: list[Action] = []
        self.agent_actions: list[Action] = []
        self.set_actions(self.get_legal_actions())
        self.set_agent_actions(self.actions)

        # Marquise variables
        self.marquise_action_count = 3
        self.marquise_march_count = 2
        self.marquise_recruit_count = 1
        self.distance_from_the_keep_list = [4, 3, 2, 3, 3, 2, 1, 1, 3, 2, 1, 0]
        self.distance_from_the_keep = {}

        for i in range(0, len(self.board.areas)):
            self.distance_from_the_keep[self.board.areas[i]] = self.distance_from_the_keep_list[i]

        # Eyrie variables
        self.selected_clearing = None

        # Battle variables
        self.attacker = None
        self.defender = None
        self.attacking_clearing: Area | None = None
        self.continuation_func = None

        self.attacker_roll: int = 0
        self.defender_roll: int = 0
        self.defender_defenseless_extra_hits: int = 0
        self.attacker_extra_hits: int = 0
        self.defender_extra_hits: int = 0

        self.redirect_func = None
        self.attacker_remaining_hits: int = 0
        self.defender_remaining_hits: int = 0
        self.marquise_removed_warrior: int = 0

        self.selecting_piece_to_remove_faction = None

        # Cards
        self.cards_daylight_continuation_func = None
        self.cards_birdsong_continuation_func = None

        # # Add Card To Decree variables
        self.selected_card: Card | None = None
        self.added_bird_card: bool = False
        self.addable_count: int = 2

        # # Resolve Decree variables
        self.decree_counter: {DecreeAction: list[Card]} = {
            DecreeAction.RECRUIT: [],
            DecreeAction.MOVE: [],
            DecreeAction.BATTLE: [],
            DecreeAction.BUILD: []
        }

        self.prompt = "If hand empty, draw 1 card"

        # Setup Game
        self.setup_board()

    def get_state_as_num_array(self) -> list:
        n_features: int = 37
        arr: list = [[]] * n_features

        arr[0] = 1 if self.running else 0

        arr[1] = self.turn_count
        arr[2] = 1 if self.ui_turn_player == Faction.MARQUISE else 0
        arr[3] = 1 if self.turn_player == Faction.MARQUISE else 0
        arr[4] = self.phase.to_number()  # 0, 1, 2, 3
        arr[5] = self.sub_phase
        arr[6] = 1 if self.is_in_action_sub_phase else 0

        arr[7] = [card.card_id for card in self.draw_pile]
        arr[8] = [card.card_id for card in self.discard_pile]
        arr[9] = [card.card_id for card in self.discard_pile_dominance]

        arr[10] = self.board.get_state_as_num_array()

        arr[11] = self.marquise.get_state_as_num_array()
        arr[12] = self.eyrie.get_state_as_num_array()

        arr[13] = self.marquise_action_count
        arr[14] = self.marquise_march_count
        arr[15] = self.marquise_recruit_count

        arr[16] = self.selected_clearing.area_index if self.selected_clearing is not None else -1

        arr[17] = self.selected_card.card_id if self.selected_card is not None else -1
        arr[18] = 1 if self.added_bird_card else 0
        arr[19] = self.addable_count
        arr[20] = [
            [card.card_id for card in self.decree_counter[decree_action]] for decree_action in self.decree_counter
        ]

        arr[21] = 1 if self.attacker == Faction.MARQUISE else 0
        arr[22] = 1 if self.defender == Faction.MARQUISE else 0
        arr[23] = 0 if self.attacking_clearing is None else self.attacking_clearing.area_index

        continuation_func_map = {
            None: -1,
            self.marquise_daylight_2: 0,
            self.eyrie_resolve_battle: 1,
            self.marquise_daylight: 2,
            self.eyrie_daylight_craft: 3
        }

        arr[24] = continuation_func_map[self.continuation_func]
        arr[25] = self.attacker_roll
        arr[26] = self.defender_roll
        arr[27] = self.defender_defenseless_extra_hits
        arr[28] = self.attacker_extra_hits
        arr[29] = self.defender_extra_hits
        arr[30] = 0 if self.redirect_func is None else 1
        arr[31] = self.attacker_remaining_hits
        arr[32] = self.defender_remaining_hits
        arr[33] = self.marquise_removed_warrior
        arr[34] = 1 if self.selecting_piece_to_remove_faction == Faction.MARQUISE else 0

        cards_birdsong_continuation_func_map = {
            None: -1,
            self.marquise_birdsong_cards: 0,
            self.eyrie_start_to_add_to_decree: 1
        }

        arr[35] = cards_birdsong_continuation_func_map[self.cards_birdsong_continuation_func]

        cards_daylight_continuation_func_map = {
            None: -1,
            self.marquise_daylight: 0,
            self.eyrie_daylight_craft: 1,
            self.eyrie_pre_move: 2,
            self.eyrie_pre_recruit: 3,
            self.eyrie_pre_battle: 4,
            self.eyrie_pre_build: 5,
            self.marquise_daylight_2: 6
        }

        arr[36] = cards_daylight_continuation_func_map[self.cards_daylight_continuation_func]

        return arr

    def set_state_from_num_array(self,
                                 arr: list = None):
        self.set_state_from_num_arrays(
            arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6], arr[7], arr[8],
            arr[9], arr[10], arr[11], arr[12], arr[13], arr[14], arr[15], arr[16],
            arr[17], arr[18], arr[19], arr[20], arr[21], arr[22], arr[23], arr[24],
            arr[25], arr[26], arr[27], arr[28], arr[29], arr[30], arr[31], arr[32],
            arr[33], arr[34], arr[35], arr[36]
        )

    def set_state_from_num_arrays(self,
                                  running: int = 0,
                                  turn_count: int = 0,
                                  ui_turn_player: int = 1,
                                  turn_player: int = 1,
                                  phase: int = 0,
                                  sub_phase: int = 0,
                                  is_in_action_sub_phase: int = 0,
                                  draw_pile_card_ids: list[int] = None,
                                  discard_pile_card_ids: list[int] = None,
                                  discard_pile_dominance_card_ids: list[int] = None,
                                  board: list = None,
                                  marquise_board: list = None,
                                  eyrie_board: list = None,
                                  marquise_action_count: int = 3,
                                  marquise_march_count: int = 2,
                                  marquise_recruit_count: int = 1,
                                  selected_clearing_area_index: int = 0,
                                  selected_card_id: int = 0,
                                  added_bird_card: int = 0,
                                  addable_count: int = 2,
                                  decree_counter: list[list[int]] = None,
                                  attacker: int = 0,
                                  defender: int = 0,
                                  attacking_clearing: int = 0,
                                  continuation_func: int = 0,
                                  attacker_roll: int = 0,
                                  defender_roll: int = 0,
                                  defender_defenseless_extra_hits: int = 0,
                                  attacker_extra_hits: int = 0,
                                  defender_extra_hits: int = 0,
                                  redirect_func: int = 0,
                                  attacker_remaining_hits: int = 0,
                                  defender_remaining_hits: int = 0,
                                  marquise_removed_warrior: int = 0,
                                  selecting_piece_to_remove_faction: int = 0,
                                  cards_birdsong_continuation_func=None,
                                  cards_daylight_continuation_func=None,
                                  ):

        continuation_func_remap = {
            -1: None,
            0: self.marquise_daylight_2,
            1: self.eyrie_resolve_battle,
            2: self.marquise_daylight,
            3: self.eyrie_daylight_craft
        }

        cards_birdsong_continuation_func_remap = {
            -1: None,
            0: self.marquise_birdsong_cards,
            1: self.eyrie_start_to_add_to_decree
        }

        cards_daylight_continuation_func_remap = {
            -1: None,
            0: self.marquise_daylight,
            1: self.eyrie_daylight_craft,
            2: self.eyrie_pre_move,
            3: self.eyrie_pre_recruit,
            4: self.eyrie_pre_battle,
            5: self.eyrie_pre_build,
            6: self.marquise_daylight_2
        }

        self.set_state(
            running == 1,
            turn_count,
            Faction.MARQUISE if ui_turn_player == 1 else Faction.EYRIE,
            Faction.MARQUISE if turn_player == 1 else Faction.EYRIE,
            Phase.to_phase(phase),
            sub_phase,
            is_in_action_sub_phase == 1,
            draw_pile_card_ids,
            discard_pile_card_ids,
            discard_pile_dominance_card_ids,
            board,
            marquise_board,
            eyrie_board,
            marquise_action_count,
            marquise_march_count,
            marquise_recruit_count,
            selected_clearing_area_index == 1,
            selected_card_id,
            added_bird_card == 1,
            addable_count,
            decree_counter,
            Faction.MARQUISE if attacker == 1 else Faction.EYRIE,
            Faction.MARQUISE if defender == 1 else Faction.EYRIE,
            attacking_clearing,
            continuation_func_remap[continuation_func],
            attacker_roll,
            defender_roll,
            defender_defenseless_extra_hits,
            attacker_extra_hits,
            defender_extra_hits,
            None if redirect_func == 0 else self.roll_dice,
            attacker_remaining_hits,
            defender_remaining_hits,
            marquise_removed_warrior,
            Faction.MARQUISE if selecting_piece_to_remove_faction == 1 else Faction.EYRIE,
            cards_birdsong_continuation_func_remap[cards_birdsong_continuation_func],
            cards_daylight_continuation_func_remap[cards_daylight_continuation_func]
        )

    def set_state(self,
                  running: bool = True,
                  turn_count: int = 0,
                  ui_turn_player: Faction = Faction.MARQUISE,
                  turn_player: Faction = Faction.MARQUISE,
                  phase: Phase = Phase.BIRDSONG,
                  sub_phase: int = 0,
                  is_in_action_sub_phase: bool = False,
                  draw_pile_card_ids: list[int] = None,
                  discard_pile_card_ids: list[int] = None,
                  discard_pile_dominance_card_ids: list[int] = None,
                  board: list = None,
                  marquise_board: list = None,
                  eyrie_board: list = None,
                  marquise_action_count: int = 3,
                  marquise_march_count: int = 2,
                  marquise_recruit_count: int = 1,
                  selected_clearing_area_index: int = 0,
                  selected_card_id: int = 0,
                  added_bird_card: bool = False,
                  addable_count: int = 2,
                  decree_counter: list[list[int]] = None,
                  attacker: Faction = Faction.MARQUISE,
                  defender: Faction = Faction.EYRIE,
                  attacking_clearing: int = 0,
                  continuation_func=None,
                  attacker_roll: int = 0,
                  defender_roll: int = 0,
                  defender_defenseless_extra_hits: int = 0,
                  attacker_extra_hits: int = 0,
                  defender_extra_hits: int = 0,
                  redirect_func=None,
                  attacker_remaining_hits: int = 0,
                  defender_remaining_hits: int = 0,
                  marquise_removed_warrior: int = 0,
                  selecting_piece_to_remove_faction: Faction = Faction.MARQUISE,
                  cards_birdsong_continuation_func=None,
                  cards_daylight_continuation_func=None,
                  ):

        CARDS: list[Card] = [build_card(i) for i in range(0, 54)]

        self.running = running

        # Game Data
        self.turn_count = turn_count
        self.ui_turn_player = ui_turn_player
        self.turn_player = turn_player
        self.phase = phase
        self.sub_phase = sub_phase
        self.is_in_action_sub_phase = is_in_action_sub_phase

        # Board Game Components
        self.draw_pile = [get_card(i, CARDS) for i in draw_pile_card_ids]
        self.discard_pile = [get_card(i, CARDS) for i in discard_pile_card_ids]
        self.discard_pile_dominance = [get_card(i, CARDS) for i in discard_pile_dominance_card_ids]

        # Board, Areas (Clearings)
        self.board.set_state_from_num_array(board)

        # Faction Board
        self.marquise.set_state_from_num_array(marquise_board, CARDS)
        self.eyrie.set_state_from_num_array(eyrie_board, CARDS)

        # Marquise variables
        self.marquise_action_count = marquise_action_count
        self.marquise_march_count = marquise_march_count
        self.marquise_recruit_count = marquise_recruit_count

        # Eyrie variables
        self.selected_clearing = self.get_area(selected_clearing_area_index)

        # Battle variables
        self.attacker = attacker
        self.defender = defender
        self.attacking_clearing: Area | None = self.board.areas[attacking_clearing]
        self.continuation_func = continuation_func

        self.attacker_roll: int = attacker_roll
        self.defender_roll: int = defender_roll
        self.defender_defenseless_extra_hits: int = defender_defenseless_extra_hits
        self.attacker_extra_hits: int = attacker_extra_hits
        self.defender_extra_hits: int = defender_extra_hits

        self.redirect_func = redirect_func
        self.attacker_remaining_hits: int = attacker_remaining_hits
        self.defender_remaining_hits: int = defender_remaining_hits
        self.marquise_removed_warrior: int = marquise_removed_warrior

        self.selecting_piece_to_remove_faction = selecting_piece_to_remove_faction

        # Cards
        self.cards_daylight_continuation_func = cards_daylight_continuation_func
        self.cards_birdsong_continuation_func = cards_birdsong_continuation_func

        # # Add Card To Decree variables
        self.selected_card = get_card(selected_card_id, CARDS)
        self.added_bird_card = added_bird_card
        self.addable_count = addable_count

        # # Resolve Decree variables
        self.decree_counter = {
            DecreeAction.RECRUIT: [get_card(i, CARDS) for i in decree_counter[0]],
            DecreeAction.MOVE: [get_card(i, CARDS) for i in decree_counter[1]],
            DecreeAction.BATTLE: [get_card(i, CARDS) for i in decree_counter[2]],
            DecreeAction.BUILD: [get_card(i, CARDS) for i in decree_counter[3]]
        }

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
    # Actions

    def get_legal_actions(self) -> list[Action]:
        """
        Returns list of legal actions for agent from the current state of the game.

        :return: list of legal actions
        """
        actions: list[Action] = []

        match self.sub_phase:

            # Marquise
            case 10001:  # marquise_birdsong
                actions.extend(
                    self.generate_actions_agent_cards_birdsong(Faction.MARQUISE, self.marquise_birdsong_cards)
                    + [Action('Next', perform(self.marquise_pre_daylight))]
                )
            case 10002:  # marquise_pre_daylight
                actions.extend(
                    self.generate_actions_command_warren(Faction.MARQUISE, self.marquise_daylight)
                    + [Action('Next', self.marquise_daylight)]
                )
            case 10003:  # marquise_daylight
                actions.extend(
                    self.generate_actions_craft_cards(Faction.MARQUISE) +
                    self.generate_actions_agent_cards_daylight(Faction.MARQUISE,
                                                               self.marquise_daylight)
                    + [Action('Next', perform(self.marquise_daylight_2))]
                )
            case 10004:  # marquise_daylight_2
                agent_actions = []
                if self.marquise_action_count == 0:
                    if self.marquise_hawks_for_hire_check():
                        agent_actions.append(Action('Hawks for hire (discard BIRD suit card to gain extra action)',
                                                    perform(self.marquise_daylight_hawks_for_hire_select_card)))
                else:
                    agent_actions += (
                            self.generate_actions_agent_marquise_march(self.marquise_daylight_agent_resolve_march) +
                            self.generate_actions_agent_marquise_build() +
                            self.generate_actions_agent_marquise_recruit() +
                            self.generate_actions_agent_marquise_overwork() +
                            self.generate_actions_agent_marquise_battle()
                    )
                actions.extend(
                    agent_actions
                    + self.generate_actions_cards_daylight(Faction.MARQUISE,
                                                           self.marquise_daylight_2)
                    + [Action('Next', perform(self.marquise_pre_evening))]
                )

            case 10014:  # marquise_daylight_agent_resolve_march
                actions += (self.generate_actions_agent_marquise_march(self.marquise_daylight_2) + [
                    Action('Next', perform(self.marquise_daylight_2))])

            case 10024:  # marquise_daylight_hawks_for_hire_select_card
                actions += (self.generate_actions_select_card_hawks_for_hire())

            case 10005:  # marquise_pre_evening
                actions.extend(
                    self.generate_actions_agent_cobbler(Faction.MARQUISE)
                    + [Action('Next', self.marquise_evening_draw_card)]
                )

            case 10006:  # marquise_evening_draw_card
                actions.extend(
                    [Action('Next', perform(self.marquise_evening_discard_card))]
                )

            case 10007:  # marquise_evening_discard_card
                card_in_hand_count = len(self.marquise.cards_in_hand)
                if card_in_hand_count > 5:
                    actions.extend(
                        self.generate_actions_select_card_to_discard(Faction.MARQUISE)
                    )
                else:
                    actions.extend(
                        [Action('End turn', perform(self.eyrie_start))]
                    )
            case 10017:  # select_card_to_discard
                actions.extend(self.generate_actions_select_card_to_discard(Faction.MARQUISE))

            case 20001:  # start as eyrie
                actions.append(Action('Next, Eyrie start', perform(self.eyrie_start)))
            case 20002:  # eyrie_start -> eyrie_start_to_add_to_decree
                if self.addable_count == 2:
                    actions += self.generate_actions_agent_add_card_to_decree() \
                               + self.generate_actions_agent_cards_birdsong(Faction.EYRIE,
                                                                            self.eyrie_start_to_add_to_decree)

                elif self.addable_count == 1:
                    actions += self.generate_actions_agent_add_card_to_decree() \
                               + [
                                   Action("Skip", perform(self.eyrie_add_to_the_decree_additional_skip))
                               ] \
                               + self.generate_actions_agent_cards_birdsong(Faction.EYRIE,
                                                                            self.eyrie_start_to_add_to_decree)
            case 20003:
                actions += self.generate_actions_place_roost_and_3_warriors() \
                           + self.generate_actions_agent_cards_birdsong(Faction.EYRIE,
                                                                        self.eyrie_start_to_add_to_decree)
            case 20004:
                actions.append(Action('Next, to Daylight', perform(self.eyrie_birdsong_to_daylight)))
            case 20005:
                actions += self.generate_actions_command_warren(Faction.EYRIE, self.eyrie_daylight_craft) \
                           + [Action('Next, to Craft', self.eyrie_daylight_craft)]
            case 20006:
                actions += self.generate_actions_craft_cards(Faction.EYRIE) \
                           + self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_daylight_craft) \
                           + self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_daylight_craft) \
                           + self.generate_actions_agent_cards_daylight(Faction.EYRIE, self.eyrie_daylight_craft) \
                           + [Action('Next, to Resolve Decree',
                                     perform(self.eyrie_daylight_craft_to_resolve_the_decree))]
            case 20007:
                actions += self.generate_actions_eyrie_recruit() \
                           + self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_pre_recruit) \
                           + self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_pre_recruit) \
                           + self.generate_actions_agent_cards_daylight(Faction.EYRIE, self.eyrie_pre_recruit)
            case 20008:
                actions += self.generate_actions_agent_eyrie_move() \
                           + self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_pre_move) \
                           + self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_pre_move) \
                           + self.generate_actions_agent_cards_daylight(Faction.EYRIE, self.eyrie_pre_move)
            case 20009:
                actions += self.generate_actions_agent_eyrie_battle() \
                           + self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_pre_battle) \
                           + self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_pre_battle) \
                           + self.generate_actions_agent_cards_daylight(Faction.EYRIE, self.eyrie_pre_battle)
            case 20010:

                actions.extend(
                    self.generate_actions_eyrie_build() +
                    self.generate_actions_activate_dominance_card(Faction.EYRIE, self.eyrie_pre_build) +
                    self.generate_actions_take_dominance_card(Faction.EYRIE, self.eyrie_pre_build) +
                    self.generate_actions_agent_cards_daylight(Faction.EYRIE, self.eyrie_pre_build)
                )

            case 20011:
                actions += self.generate_actions_agent_cobbler(Faction.EYRIE) \
                           + [Action('Next, to Evening', self.eyrie_evening)]
            # TURMOIL
            case 21001:
                actions += self.generate_actions_eyrie_select_new_leader(self.eyrie.get_inactive_leader())
            case 21002:
                if len(self.eyrie.cards_in_hand) > 5:
                    actions += self.generate_actions_select_card_to_discard(Faction.EYRIE)
                else:
                    self.eyrie_evening_to_marquise()
            case 21003:
                actions += [Action('Next, to Marquise', perform(self.marquise_birdsong_start))]

            case 30001:  # cobbler_agent
                if self.turn_player == Faction.MARQUISE:
                    actions.extend(
                        self.generate_actions_agent_move_with_cont_func(Faction.MARQUISE,
                                                                        self.marquise_evening_draw_card)
                    )
                else:
                    aas = self.generate_actions_agent_move_with_cont_func(Faction.EYRIE, self.eyrie_evening)
                    LOGGER.warning(len(aas))
                    actions.extend(
                        aas
                    )

            case 30002:  # codebreakers
                actions.extend(
                    [Action('Next', self.cards_daylight_continuation_func)]
                )

            case 40001:  # defender_use_ambush
                def_ambush_actions = []

                defender_board = self.faction_to_faction_board(self.defender)
                def_ambush = [card for card in defender_board.cards_in_hand if
                              card.name == CardName.AMBUSH and (
                                      card.suit == Suit.BIRD or card.suit == self.attacking_clearing.suit)]
                for card in def_ambush:
                    def_ambush_actions.append(Action('Discard {} ({})'.format(card.name, card.suit),
                                                     perform(self.attacker_use_ambush, card)))

                actions.extend(
                    def_ambush_actions +
                    [Action('Skip', perform(self.roll_dice))]
                )

            case 40002:  # attacker_use_ambush
                atk_ambush_actions = []

                attacker_board = self.faction_to_faction_board(self.attacker)
                atk_ambush = [card for card in attacker_board.cards_in_hand if card.name == CardName.AMBUSH]
                for card in atk_ambush:
                    atk_ambush_actions.append(Action('Discard {} ({})'.format(card.name, card.suit),
                                                     perform(self.foil_ambush, card)))

                actions.extend(
                    atk_ambush_actions +
                    [Action('Skip', perform(self.resolve_hits, self.roll_dice))]
                )

            case 40003:  # attacker_activate_battle_ability_card
                attacker_faction_board = self.faction_to_faction_board(self.attacker)

                atk_brutal_tactics = [card for card in attacker_faction_board.crafted_cards if
                                      card.name == CardName.BRUTAL_TACTICS]
                atk_armorers = [card for card in attacker_faction_board.crafted_cards if card.name == CardName.ARMORERS]

                atk_actions = []

                if len(atk_brutal_tactics) > 0 and attacker_faction_board.activated_card.count(
                        atk_brutal_tactics[0]) < 1:
                    brutal_tactics_card = atk_brutal_tactics[0]
                    atk_actions.append(Action('Use {} ({})'.format(brutal_tactics_card.name, brutal_tactics_card.suit),
                                              perform(self.brutal_tactics, brutal_tactics_card)))

                if len(atk_armorers) > 0 and attacker_faction_board.activated_card.count(atk_armorers[0]) < 1:
                    armorers_card = atk_armorers[0]
                    atk_actions.append(Action('Use {} ({})'.format(armorers_card.name, armorers_card.suit),
                                              perform(self.armorers, self.attacker, armorers_card)))

                actions.extend(
                    atk_actions +
                    [Action('Skip', perform(self.defender_activate_battle_ability_card))]
                )

            case 40004:  # defender_activate_battle_ability_card
                defender_faction_board = self.faction_to_faction_board(self.defender)

                def_sappers = [card for card in defender_faction_board.crafted_cards if card.name == CardName.SAPPERS]
                def_armorers = [card for card in defender_faction_board.crafted_cards if card.name == CardName.ARMORERS]

                def_actions = []

                if len(def_sappers) > 0 and defender_faction_board.activated_card.count(def_sappers[0]) < 1:
                    sappers_card = def_sappers[0]
                    def_actions.append(Action('Use {} ({})'.format(sappers_card.name, sappers_card.suit),
                                              perform(self.sappers, sappers_card)))

                if len(def_armorers) > 0 and defender_faction_board.activated_card.count(def_armorers[0]) < 1:
                    armorers_card = def_armorers[0]
                    def_actions.append(Action('Use {} ({})'.format(armorers_card.name, armorers_card.suit),
                                              perform(self.armorers, self.defender, armorers_card)))

                actions.extend(
                    def_actions +
                    [Action('Skip', perform(self.resolve_hits))]
                )

            case 40005:  # resolve_marquise_field_hospital
                actions.extend(
                    self.generate_actions_field_hospital_select_card_to_discard()
                    + [Action('Next', perform(self.resolve_remaining_hits))]
                )

            case 40006:  # select_piece_to_remove
                actions.extend(
                    self.generate_actions_select_piece_to_remove()
                )
        LOGGER.debug("get_legal_actions:{}: len(actions) {}, actions {}".format(self.sub_phase, len(actions), [a.name for a in actions]))
        return actions

    def get_actions(self) -> list[Action]:
        return self.get_legal_actions()

    def get_agent_actions(self) -> list[Action]:
        return self.get_legal_actions()

    def set_actions(self, actions: list[Action] = None):
        self.actions = actions

    def set_agent_actions(self, actions: list[Action] = None):
        if actions is not None:
            self.agent_actions = actions
        else:
            raise Exception("set_agent_actions did not receive any parameters")

    #####
    # Win Condition
    def gain_vp(self, faction: Faction, vp: int):
        if self.faction_to_faction_board(faction).dominance_card is not None:
            return
        self.board.gain_vp(faction, vp)
        self.check_win_condition(faction)

    def check_win_condition(self, faction: Faction, no_end_action: bool = False) -> tuple[
                                                                                        int, int] | Card | None:
        faction_board = self.faction_to_faction_board(faction)
        if faction_board.dominance_card is None:
            return self.check_win_condition_vp(faction, no_end_action)
        else:
            return self.check_win_condition_dominance(faction, no_end_action)

    def check_win_condition_vp(self, faction: Faction, no_end_action: bool = False) -> tuple[int, int] | None:
        if self.board.faction_points[faction] >= config['game']['victory-point-limit']:
            if not no_end_action:
                LOGGER.debug(
                    "GAME_END:VP:MARQUISE {} vs EYRIE {}".format(self.board.faction_points[Faction.MARQUISE],
                                                                 self.board.faction_points[Faction.EYRIE]))
                self.end_game()
            return self.board.faction_points[Faction.MARQUISE], self.board.faction_points[Faction.EYRIE]

    def check_win_condition_dominance(self, faction: Faction, no_end_action: bool = False) -> Card | None:
        faction_board = self.faction_to_faction_board(faction)
        warrior = faction_to_warrior(faction)

        areas = self.board.areas

        winning_dominance: Card | None = None

        if faction_board.dominance_card.name == CardName.DOMINANCE_BIRD:
            if (areas[0].ruler() == warrior and areas[11].ruler() == warrior) or (
                    areas[2].ruler() == warrior and areas[8].ruler() == warrior):
                winning_dominance = faction_board.dominance_card
        elif self.board.count_ruling_clearing_by_faction_and_suit(faction, faction_board.dominance_card.suit) >= 3:
            winning_dominance = faction_board.dominance_card

        if not no_end_action:
            if winning_dominance is not None:
                LOGGER.debug(
                    "GAME_END:DOMINANCE:{}, {} Wins".format(winning_dominance.name,
                                                            faction))
                self.end_game()
        return winning_dominance

    def end_game(self):
        self.running = False

    #####
    # Utils

    def get_area(self, area_index: int) -> Area | None:
        return self.board.get_area(area_index)

    def faction_to_faction_board(self, faction: Faction) -> FactionBoard:
        if faction == Faction.MARQUISE:
            return self.marquise
        if faction == Faction.EYRIE:
            return self.eyrie

    def get_end_game_data(self) -> tuple[Faction | None, str, int, Faction, int, int, None | Card] | None:
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
        winning_dominance: None | Card = self.check_win_condition_dominance(winning_faction,
                                                                            True) if self.faction_to_faction_board(
            winning_faction).dominance_card is not None else None
        winning_condition: str = "vp" if winning_dominance is None else "dominance"

        return winning_faction, winning_condition, turns_played, turn_player, vp_marquise, vp_eyrie, winning_dominance

    #####
    # MARQUISE
    def marquise_birdsong_start(self):  # 10001
        self.phase = Phase.BIRDSONG
        self.sub_phase = 10001

        LOGGER.debug("{}:{}:{}:MARQUISE's turn begins".format(self.ui_turn_player, self.phase, self.sub_phase))
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
        LOGGER.debug("{}:{}:{}:Enter marquise_birdsong_cards".format(self.ui_turn_player, self.phase, self.sub_phase))
        if len(self.generate_actions_cards_birdsong(Faction.MARQUISE, self.marquise_birdsong_cards)) == 0:
            self.marquise_pre_daylight()
        else:
            self.prompt = "Do you want to use Birdsong card's action?"
            self.set_actions(self.generate_actions_cards_birdsong(Faction.MARQUISE, self.marquise_birdsong_cards) + [
                Action('Next', perform(self.marquise_pre_daylight))])

    def marquise_pre_daylight(self):  # 10002
        self.phase = Phase.DAYLIGHT
        self.sub_phase = 10002

        LOGGER.debug("{}:{}:{}:Enter marquise_pre_daylight".format(self.ui_turn_player, self.phase, self.sub_phase))

        actions = self.generate_actions_command_warren(Faction.MARQUISE, self.marquise_daylight)
        if not actions:
            self.marquise_daylight()
        else:
            self.prompt = 'Want to use Command Warren card effect?'
            self.set_actions(actions + [Action('Next', self.marquise_daylight)])

    def marquise_daylight(self):  # 10003
        LOGGER.debug("{}:{}:{}:Enter marquise_daylight".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.sub_phase = 10003

        craftable_cards = self.generate_actions_craft_cards(Faction.MARQUISE)
        action_cards = self.generate_actions_cards_daylight(Faction.MARQUISE, self.marquise_daylight)
        if not craftable_cards and not action_cards:
            self.marquise_daylight_2()
        else:
            self.prompt = "Want to craft something, squire?"
            self.set_actions(self.generate_actions_craft_cards(Faction.MARQUISE) +
                             self.generate_actions_cards_daylight(Faction.MARQUISE
                                                                  , self.marquise_daylight) + [
                                 Action('Next', perform(self.marquise_daylight_2))])

    def marquise_daylight_2(self):  # 10004
        LOGGER.debug("{}:{}:{}:Enter marquise_daylight_2".format(self.ui_turn_player, self.phase, self.sub_phase))
        actions = []
        agent_actions = []
        self.prompt = "Select Actions (Remaining Action: {})".format(self.marquise_action_count)
        self.ui_turn_player = Faction.MARQUISE
        self.phase = Phase.DAYLIGHT
        self.sub_phase = 10004

        if self.marquise_action_count == 0:
            self.prompt = "No action remaining. Proceed to next phase.".format(self.marquise_action_count)
            if self.marquise_hawks_for_hire_check():
                self.prompt = "No action remaining. Discard BIRD suit card to gain extra action.".format(
                    self.marquise_action_count)
                actions.append(Action('Hawks for hire (discard BIRD suit card to gain extra action)',
                                      perform(self.marquise_daylight_hawks_for_hire_select_card)))
                agent_actions.append(Action('Hawks for hire (discard BIRD suit card to gain extra action)',
                                            perform(self.marquise_daylight_hawks_for_hire_select_card)))
        else:
            if self.marquise_march_check():
                self.marquise_march_count = 2
                actions.append(Action('March', perform(self.marquise_daylight_march)))
            if self.marquise_build_check():
                actions.append(Action('Build', perform(self.marquise_daylight_build_select_clearing)))
            if self.marquise_recruit_check():
                actions.append(Action('Recruit', perform(self.marquise_daylight_recruit)))
            if self.marquise_overwork_check():
                actions.append(Action('Overwork', perform(self.marquise_daylight_overwork_select_clearing)))
            if self.marquise_battle_check():
                actions.append(Action('Battle', perform(self.marquise_daylight_battle)))
            agent_actions += (
                # self.generate_actions_agent_marquise_march(self.marquise_daylight_agent_resolve_march) +
                    self.generate_actions_agent_marquise_build() +
                    self.generate_actions_agent_marquise_recruit() +
                    self.generate_actions_agent_marquise_overwork()
                # self.generate_actions_agent_marquise_battle()
            )

        self.set_actions(actions
                         + self.generate_actions_activate_dominance_card(Faction.MARQUISE,
                                                                         self.marquise_daylight_2)
                         + self.generate_actions_take_dominance_card(Faction.MARQUISE,
                                                                     self.marquise_daylight_2)
                         + self.generate_actions_cards_daylight(Faction.MARQUISE,
                                                                self.marquise_daylight_2)
                         + [Action('Next', perform(self.marquise_pre_evening))]
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
        return len(self.generate_actions_select_clearing_battle(Faction.MARQUISE, None, True)) > 0

    def marquise_daylight_hawks_for_hire_select_card(self):  # 10024
        self.sub_phase = 10024
        LOGGER.debug(
            "{}:{}:{}:Enter marquise_daylight_hawks_for_hire_select_card".format(self.ui_turn_player, self.phase,
                                                                                 self.sub_phase))

        self.prompt = "Select card to discard"
        self.set_actions(self.generate_actions_select_card_hawks_for_hire())

    def marquise_daylight_march(self):
        self.select_clearing_src_move(Faction.MARQUISE, self.marquise_daylight_resolve_march)

    def marquise_daylight_resolve_march(self):
        self.marquise_march_count -= 1
        LOGGER.debug(
            "{}:{}:{}:MARQUISE's remaining march action: {}".format(self.ui_turn_player, self.phase,
                                                                    self.sub_phase, self.marquise_march_count))
        if self.marquise_march_count > 0 and len(
                self.generate_actions_select_src_clearing(Faction.MARQUISE, None, False)) > 0:
            self.prompt = "The warriors has been moved. (Remaining march action: {})".format(
                self.marquise_march_count)
            self.set_actions([Action('Next', perform(self.marquise_daylight_march))])
        else:
            self.marquise_action_count -= 1
            self.prompt = "The warriors has been moved. (Remaining march action: {})".format(
                self.marquise_march_count)
            self.set_actions([Action('Next', perform(self.marquise_daylight_2))])

    def generate_actions_agent_marquise_march(self, cont_func):
        actions: list[Action] = []

        can_move_from_clearing = self.find_available_source_clearings(Faction.MARQUISE, False)
        for src in can_move_from_clearing:
            dests = self.find_available_destination_clearings(Faction.MARQUISE, src)
            for dest in dests:
                for num_of_warriors in range(1, src.warrior_count[faction_to_warrior(Faction.MARQUISE)] + 1):
                    actions.append(Action("Move {} warriors from {} to {}".format(
                        num_of_warriors, src.area_index, dest.area_index),
                        perform(self.move_warriors,
                                Faction.MARQUISE, src, dest,
                                num_of_warriors, cont_func)))
        return actions

    def marquise_daylight_agent_resolve_march(self):  # 10014
        self.marquise_action_count -= 1
        self.sub_phase = 10014
        LOGGER.debug(
            "{}:{}:{}:MARQUISE's remaining march action: {}".format(self.ui_turn_player, self.phase,
                                                                    self.sub_phase, 1))

    def marquise_daylight_build_select_clearing(self):
        LOGGER.debug("{}:{}:{}:Enter marquise_daylight_build_select_clearing".format(self.ui_turn_player, self.phase,
                                                                                     self.sub_phase))

        self.prompt = "Let's build. Select clearing"
        self.set_actions(self.generate_actions_select_buildable_clearing(Faction.MARQUISE))

    def marquise_daylight_build_select_building(self, clearing):
        LOGGER.debug("{}:{}:{}:Enter marquise_daylight_build_select_building".format(self.ui_turn_player, self.phase,
                                                                                     self.sub_phase))

        self.prompt = "Select Building"
        self.set_actions(self.generate_actions_select_building(Faction.MARQUISE, clearing))

    def generate_actions_agent_marquise_build(self):
        actions = []
        buildable_clearings = self.get_buildable_clearings(Faction.MARQUISE)

        for clearing in buildable_clearings:
            buildings = self.get_buildable_buildings(Faction.MARQUISE, clearing)
            for building in buildings:
                actions.append(
                    Action("Builds {} in clearing #{}".format(building, clearing),
                           perform(self.build, Faction.MARQUISE, clearing, building)))

        return actions

    def marquise_daylight_recruit(self):
        LOGGER.debug("{}:{}:{}:Enter marquise_daylight_recruit".format(self.ui_turn_player, self.phase, self.sub_phase))

        LOGGER.debug("{}:{}:{}:MARQUISE recruit.".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.prompt = "Recruit warrior"

        if self.marquise.reserved_warriors >= self.marquise.building_trackers[Building.RECRUITER]:
            self.recruit(Faction.MARQUISE)
            self.marquise_daylight_2()
        else:
            clearing_with_recruiter = [clearing for clearing in self.board.areas for _ in
                                       range(clearing.buildings.count(Building.RECRUITER))]
            self.marquise_daylight_recruit_some_clearings(clearing_with_recruiter)

    def marquise_daylight_recruit_some_clearings(self, clearing_with_recruiter):
        LOGGER.debug("{}:{}:{}:Enter marquise_daylight_recruit_some_clearings".format(self.ui_turn_player, self.phase,
                                                                                      self.sub_phase))

        if clearing_with_recruiter is [] or self.marquise.reserved_warriors == 0:
            self.marquise_recruit_count -= 1
            self.marquise_action_count -= 1
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
        LOGGER.debug("{}:{}:{}:Enter recruit_single_clearing".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.add_warrior(Faction.MARQUISE, clearing, 1)
        LOGGER.debug(
            "{}:{}:{}:MARQUISE adds warrior in clearing #{}".format(self.ui_turn_player, self.phase,
                                                                    self.sub_phase,
                                                                    clearing.area_index))
        self.marquise_daylight_recruit_some_clearings(remaining_clearing_with_recruiter)

    def generate_actions_agent_marquise_recruit(self):
        actions = []
        if self.marquise_recruit_count == 0:
            return actions

        if self.marquise.reserved_warriors >= self.marquise.building_trackers[Building.RECRUITER]:
            actions.append(Action("Recruit", perform(self.marquise_daylight_recruit)))
        else:
            clearing_with_recruiter = [clearing for clearing in self.board.areas for _ in
                                       range(clearing.buildings.count(Building.RECRUITER))]
            all_possible_clearing_combinations = combinations(clearing_with_recruiter, self.marquise.reserved_warriors)
            for combination in list(all_possible_clearing_combinations):
                actions.append(Action("Recruit in clearing {}".format([c.area_index for c in combination]),
                                      perform(self.recruit_many_clearings, combination)))

        return actions

    def recruit_many_clearings(self, clearings):
        self.marquise_recruit_count -= 1
        self.marquise_action_count -= 1
        for clearing in clearings:
            self.add_warrior(Faction.MARQUISE, clearing, 1)
            LOGGER.debug(
                "{}:{}:{}:MARQUISE adds warrior in clearing #{}".format(self.ui_turn_player, self.phase,
                                                                        self.sub_phase,
                                                                        clearing.area_index))
        self.marquise_daylight_2()

    def marquise_daylight_battle(self):
        LOGGER.debug("{}:{}:{}:Enter marquise_daylight_battle".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.marquise_action_count -= 1
        self.select_clearing_battle(Faction.MARQUISE, self.marquise_daylight_2)

    def generate_actions_agent_marquise_battle(self):
        attacker = Faction.MARQUISE
        clearings = self.get_battlable_clearing(attacker, False)
        actions = []

        for clearing in clearings:
            enemy_factions: list[Faction] = self.get_available_enemy_tokens_from_clearing(attacker, clearing)

            for enemy_faction in enemy_factions:
                actions.append(
                    Action("Attack {} in area {}".format(enemy_faction, clearing.area_index),
                           perform(self.marquise_agent_initiate_battle, attacker, enemy_faction, clearing,
                                   self.marquise_daylight_2)))

        return actions

    def marquise_agent_initiate_battle(self, attacker, defender, clearing, continuation_func):
        self.marquise_action_count -= 1

        self.initiate_battle(attacker, defender, clearing, continuation_func)

    def marquise_daylight_overwork_select_clearing(self):
        LOGGER.debug("{}:{}:{}:Enter marquise_daylight_overwork_select_clearing".format(self.ui_turn_player, self.phase,
                                                                                        self.sub_phase))

        self.prompt = "Select Clearing"
        self.set_actions(self.generate_actions_overwork_select_clearing())

    def marquise_daylight_overwork_select_card_to_discard(self, clearing):
        LOGGER.debug(
            "{}:{}:{}:Enter marquise_daylight_overwork_select_card_to_discard".format(self.ui_turn_player, self.phase,
                                                                                      self.sub_phase))

        self.prompt = "Select Card"
        self.set_actions(self.generate_actions_overwork_select_card(clearing))

    def marquise_overwork(self, clearing: Area, card):
        LOGGER.debug("{}:{}:{}:Enter marquise_overwork".format(self.ui_turn_player, self.phase, self.sub_phase))

        LOGGER.debug("{}:{}:{}:MARQUISE overwork on clearing #{}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                         clearing.area_index))
        self.discard_card(self.marquise.cards_in_hand, card)
        clearing.token_count[Token.WOOD] += 1

        self.prompt = "Overwork complete"
        self.marquise_action_count -= 1
        self.set_actions([Action('Next', self.marquise_daylight_2)])

    def generate_actions_agent_marquise_overwork(self):
        available_clearing = self.find_available_overwork_clearings()
        actions = []

        for clearing in available_clearing:
            discardable_card = [card for card in self.marquise.cards_in_hand if card.suit == clearing.suit]

            for card in discardable_card:
                actions.append(Action('Overwork: Discard {} ({})'.format(card.name, card.suit),
                                      perform(self.marquise_overwork, clearing, card)))

        return actions

    def marquise_pre_evening(self):  # 10005
        self.phase = Phase.EVENING
        self.sub_phase = 10005
        LOGGER.debug("{}:{}:{}:Enter marquise_pre_evening".format(self.ui_turn_player, self.phase, self.sub_phase))
        actions = self.generate_actions_cobbler(Faction.MARQUISE, self.marquise_evening_draw_card)

        if not actions:
            self.marquise_evening_draw_card()
        else:
            self.prompt = 'Want to move your warriors?'
            self.set_actions(actions + [Action('Next', self.marquise_evening_draw_card)])

    def marquise_evening_draw_card(self):  # 10006
        LOGGER.debug("{}:{}:{}:Enter marquise_evening_draw_card".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.sub_phase = 10006

        self.prompt = "Draw one card, plus one card per draw bonus"
        number_of_card_to_be_drawn = self.marquise.get_reward_card() + 1
        self.take_card_from_draw_pile(Faction.MARQUISE, number_of_card_to_be_drawn)

        self.set_actions([Action('Next', perform(self.marquise_evening_discard_card))])

    def marquise_evening_discard_card(self):  # 10007
        self.sub_phase = 10007

        LOGGER.debug(
            "{}:{}:{}:Enter marquise_evening_discard_card".format(self.ui_turn_player, self.phase, self.sub_phase))

        card_in_hand_count = len(self.marquise.cards_in_hand)
        if card_in_hand_count > 5:
            self.prompt = "Select card to discard down to 5 cards (currently {} cards in hand)".format(
                card_in_hand_count)
            self.set_actions(self.generate_actions_select_card_to_discard(Faction.MARQUISE))
        else:
            self.prompt = "End Turn"
            self.set_actions([Action('Next', perform(self.eyrie_start))])

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

        self.marquise_daylight_2()

    #####
    # Eyrie
    def eyrie_start(self):  # 20001
        LOGGER.debug("{}:{}:{}:eyrie turn begins".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.turn_count += 1

        self.check_win_condition(Faction.EYRIE)
        self.eyrie.clear_activated_cards()
        self.better_burrow_bank(Faction.EYRIE)

        if len(self.eyrie.cards_in_hand) == 0:
            LOGGER.debug("{}:{}:{}:eyrie_emergency_orders".format(self.ui_turn_player, self.phase, self.sub_phase))
            self.take_card_from_draw_pile(Faction.EYRIE)

        self.ui_turn_player = Faction.EYRIE
        self.turn_player = Faction.EYRIE
        self.phase = Phase.BIRDSONG
        self.sub_phase = 20001

        self.added_bird_card = False
        self.addable_count = 2
        self.eyrie_start_to_add_to_decree()

    def eyrie_start_to_add_to_decree(self):  # 20002
        LOGGER.debug(
            "{}:{}:{}:eyrie_start_to_add_to_decree addable_count = {}".format(self.ui_turn_player, self.phase,
                                                                              self.sub_phase, self.addable_count))
        self.sub_phase = 20002
        if self.addable_count == 2:
            self.prompt = "Select Card To Add To Decree"
        elif self.addable_count == 1:
            self.prompt = "Select ANOTHER card to add to the Decree"
        else:
            self.eyrie_a_new_roost()

    def generate_actions_agent_add_card_to_decree(self) -> list[Action]:
        actions: list[Action] = []
        if self.addable_count <= 0:
            return actions
        for card in self.eyrie.cards_in_hand:
            if self.added_bird_card and card.suit == Suit.BIRD:
                continue
            for decree_action in DecreeAction:
                actions.append(Action('{} ({}) to {}'.format(card.name, card.suit, decree_action),
                                      perform(self.agent_add_card_to_decree, card, decree_action)))

        return actions

    def agent_add_card_to_decree(self, card: Card, decree_action: DecreeAction | str):
        self.select_card(card)
        self.select_decree_to_add_card_to(decree_action)

    def generate_actions_add_to_the_decree_first(self) -> list[Action]:
        actions: list[Action] = []
        if self.addable_count > 0:
            for card in self.eyrie.cards_in_hand:
                if self.added_bird_card and card.suit == Suit.BIRD:
                    continue
                actions.append(Action('{} ({})'.format(card.name, card.suit),
                                      perform(self.select_card_to_add_to_the_decree, card)))
        LOGGER.debug(
            "{}:{}:{}:generate_actions_add_to_the_decree_first {}".format(self.ui_turn_player, self.phase,
                                                                          self.sub_phase,
                                                                          len(actions)))
        return actions

    def select_card_to_add_to_the_decree(self, card: Card):
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

        LOGGER.debug(
            "{}:{}:{}:Added card '{}' to {} decree".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                           self.selected_card.name, decree_action))
        self.eyrie_start_to_add_to_decree()

    def eyrie_add_to_the_decree_additional_skip(self):
        LOGGER.debug(
            "{}:{}:{}:eyrie_add_to_the_decree_additional_skip".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.eyrie_a_new_roost()

    def eyrie_a_new_roost(self):  # 20003
        LOGGER.debug(
            "{}:{}:{}:eyrie_a_new_roost".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.sub_phase = 20003

        if self.eyrie.roost_tracker == 0 and len(self.get_areas_with_min_warrior_and_empty_building()) > 0:
            self.prompt = "If you have no roost, place a roost and 3 warriors in the clearing with the fewest total warriors. (Select Clearing)"
        else:
            self.eyrie_birdsong_to_daylight()

    def get_areas_with_min_warrior_and_empty_building(self) -> list[Area]:
        min_warrior_areas: list[Area] = self.board.get_min_warrior_areas()
        return [area for area in min_warrior_areas if Building.EMPTY in area.buildings]

    def generate_actions_place_roost_and_3_warriors(self) -> list[Action]:
        actions: list[Action] = []
        min_token_areas = self.get_areas_with_min_warrior_and_empty_building()
        for area in min_token_areas:
            actions.append(Action("Area {}".format(area.area_index), perform(self.place_roost_and_3_warriors, area)))

        return actions

    def place_roost_and_3_warriors(self, area: Area):  # 20004
        self.sub_phase = 20004
        LOGGER.debug(
            "{}:{}:{}:place_roost_and_3_warriors at area#{}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                    area.area_index))

        self.add_warrior(Faction.EYRIE, area, 3)
        self.build_roost(area)

    def build_roost(self, clearing: Area):
        building_slot_index = clearing.buildings.index(Building.EMPTY)
        clearing.buildings[building_slot_index] = Building.ROOST
        self.eyrie.roost_tracker += 1

        LOGGER.debug(
            "{}:{}:{}:build_roost built {} in clearing #{}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                   Building.ROOST, clearing.area_index))

    def eyrie_birdsong_to_daylight(self):  # 20005
        self.sub_phase = 20005
        LOGGER.debug("{}:{}:{}:eyrie_birdsong_to_daylight".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.phase = Phase.DAYLIGHT

        self.eyrie.set_crafting_piece_count(self.get_building_count_by_suit(Building.ROOST))

        self.prompt = 'Use Command Warren / Craft'

    def eyrie_daylight_craft(self):  # 20006
        self.sub_phase = 20006
        self.prompt = "Craft Cards"

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
        LOGGER.debug(
            "{}:{}:{}:eyrie_daylight_craft_to_resolve_the_decree".format(self.ui_turn_player, self.phase,
                                                                         self.sub_phase))

        self.decree_counter = deepcopy(self.eyrie.decree)
        self.eyrie_pre_recruit()

    def eyrie_pre_recruit(self):  # 20007
        self.sub_phase = 20007
        LOGGER.debug("{}:{}:{}:eyrie_pre_recruit".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.update_prompt_eyrie_decree(DecreeAction.RECRUIT)
        self.prompt += " Recruit in Area:"

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
        LOGGER.debug("{}:{}:{}:turmoil:humiliate: {} bird cards in the decree, lost {} vp(s)".format(self.ui_turn_player,
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
        LOGGER.debug(
            "{}:{}:{}:turmoil:purge: discarded all decree cards except loyal viziers".format(self.ui_turn_player,
                                                                                             self.phase,
                                                                                             self.sub_phase))

    def eyrie_turmoil_depose(self):  # 21001
        self.sub_phase = 21001
        current_leader = self.eyrie.get_active_leader()

        self.eyrie.deactivate_current_leader()
        inactive_leaders = self.eyrie.get_inactive_leader()

        if len(inactive_leaders) == 0:
            self.eyrie.a_new_generation()

        LOGGER.debug(
            "{}:{}:{}:turmoil:depose: {} deposed".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                         current_leader))
        self.prompt = "Select New Eyrie Leader:"

    def generate_actions_eyrie_select_new_leader(self, inactive_leaders: list[EyrieLeader]) -> list[Action]:
        actions: list[Action] = []

        for leader in inactive_leaders:
            actions.append(Action("{}".format(leader),
                                  perform(self.eyrie_select_new_leader, leader)))

        return actions

    def eyrie_select_new_leader(self, leader: EyrieLeader):
        self.eyrie.activate_leader(leader)
        LOGGER.debug(
            "{}:{}:{}:turmoil:depose: {} selected as new leader".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                        leader))
        self.eyrie_turmoil_rest()

    def eyrie_turmoil_rest(self):
        LOGGER.debug("{}:{}:{}:turmoil:rest".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.phase = Phase.EVENING
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

        LOGGER.debug(
            "{}:{}:{}:{} recruited in area {}".format(self.ui_turn_player, self.phase, self.sub_phase, Faction.EYRIE,
                                                      area.area_index))

        self.eyrie_pre_recruit()

    def eyrie_pre_move(self):  # 20008
        self.sub_phase = 20008

        LOGGER.debug("{}:{}:{}:eyrie_pre_move".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.update_prompt_eyrie_decree(DecreeAction.MOVE)
        self.prompt += " Choose area to move from."

    def generate_actions_agent_eyrie_move(self) -> list[Action]:
        decree_action = DecreeAction.MOVE
        faction = Faction.EYRIE
        actions: list[Action] = self.generate_actions_agent_move(faction)

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                actions.append(Action("Turmoil", self.eyrie_turmoil))
            else:
                actions.append(Action("Next, To BATTLE", self.eyrie_pre_battle))

        return actions

    def generate_actions_eyrie_move(self) -> list[Action]:
        actions: list[Action] = self.generate_actions_select_src_clearing(Faction.EYRIE, self.eyrie_resolve_move, True)
        decree_action = DecreeAction.MOVE

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                actions.append(Action("Turmoil", self.eyrie_turmoil))
            else:
                actions.append(Action("Next, To BATTLE", self.eyrie_pre_battle))

        return actions

    def eyrie_resolve_move(self):
        decree_action = DecreeAction.MOVE
        self.remove_decree_counter(decree_action, self.selected_clearing.suit)
        self.update_prompt_eyrie_decree(decree_action)
        self.eyrie_pre_move()

    def eyrie_pre_battle(self):  # 20009
        self.sub_phase = 20009

        LOGGER.debug("{}:{}:{}:eyrie_pre_battle".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.update_prompt_eyrie_decree(DecreeAction.BATTLE)
        self.prompt += " Choose area to battle in."

    def generate_actions_agent_eyrie_battle(self) -> list[Action]:
        actions: list[Action] = self.generate_actions_agent_battle(Faction.EYRIE, self.eyrie_resolve_battle,
                                                                   True)
        decree_action: DecreeAction = DecreeAction.BATTLE

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                actions.append(Action("Turmoil", self.eyrie_turmoil))
            else:
                actions.append(Action("Next, To BUILD", self.eyrie_pre_build))

        return actions

    def generate_actions_eyrie_battle(self) -> list[Action]:
        actions: list[Action] = self.generate_actions_select_clearing_battle(Faction.EYRIE, self.eyrie_resolve_battle,
                                                                             True)

        decree_action: DecreeAction = DecreeAction.BATTLE

        if len(actions) == 0:
            if len(self.decree_counter[decree_action]) > 0:
                actions.append(Action("Turmoil", self.eyrie_turmoil))
            else:
                actions.append(Action("Next, To BUILD", self.eyrie_pre_build))

        return actions

    def eyrie_resolve_battle(self):
        decree_action = DecreeAction.BATTLE

        self.remove_decree_counter(decree_action, self.selected_clearing.suit)
        self.update_prompt_eyrie_decree(decree_action)
        self.eyrie_pre_battle()

    def eyrie_pre_build(self):  # 20010
        self.sub_phase = 20010

        LOGGER.debug("{}:{}:{}:eyrie_pre_build".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.update_prompt_eyrie_decree(DecreeAction.BUILD)

        self.ui_turn_player = Faction.EYRIE
        self.prompt += " Choose area to build roost in."

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
        self.eyrie_pre_build()

    def eyrie_build_to_evening(self):  # 20011
        self.sub_phase = 20011
        self.prompt = 'Want to move your warriors?'

    def eyrie_evening(self):
        # score points
        roost_tracker = self.eyrie.roost_tracker
        vp = EyrieBoard.ROOST_REWARD_VP[roost_tracker]
        card_to_draw = 1 + EyrieBoard.ROOST_REWARD_CARD[roost_tracker]
        self.gain_vp(Faction.EYRIE, vp)
        LOGGER.debug(
            "{}:{}:{}:eyrie_evening: roost tracker {}, scored {} vps".format(self.ui_turn_player, self.phase,
                                                                             self.sub_phase, self.eyrie.roost_tracker,
                                                                             vp))
        self.take_card_from_draw_pile(Faction.EYRIE, card_to_draw)
        self.eyrie_evening_discard()

    def eyrie_evening_discard(self):  # 21002
        self.sub_phase = 21002

        card_in_hand_count = len(self.eyrie.cards_in_hand)
        if card_in_hand_count > 5:
            self.prompt = "Select card to discard down to 5 cards (currently {} cards in hand)".format(
                card_in_hand_count)
        else:
            self.eyrie_evening_to_marquise()

    def eyrie_evening_to_marquise(self):  # 21003
        self.sub_phase = 21003
        LOGGER.debug("{}:{}:{}:eyrie_evening_to_marquise".format(self.ui_turn_player, self.phase, self.sub_phase))
        self.ui_turn_player = Faction.MARQUISE
        self.turn_player = Faction.MARQUISE
        self.phase = Phase.BIRDSONG
        self.prompt = "Marquise's Turn"

    def get_decree_card_to_use(self, decree_action: DecreeAction, suit: Suit) -> Card:
        eligible_cards = [card for card in self.decree_counter[decree_action] if card.suit == suit]
        bird_cards = [card for card in self.decree_counter[decree_action] if card.suit == Suit.BIRD]
        LOGGER.debug("after {} {}".format(len(eligible_cards), len(bird_cards)))
        if len(eligible_cards) > 0:
            return eligible_cards[0]
        else:
            return bird_cards[0]

    def activate_leader(self, leader: EyrieLeader):
        if self.eyrie.activate_leader(leader):
            LOGGER.debug(
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

    def craft_card(self, faction: Faction, card: Card):
        LOGGER.debug("{}:{}:{}:Crafted {} card".format(self.ui_turn_player, self.phase, self.sub_phase, card.name))
        if faction == Faction.MARQUISE:
            if card.phase == CardPhase.IMMEDIATE:
                self.gain_vp(faction, card.reward_vp)
                if card.reward_item is not None:
                    self.marquise.items[card.reward_item] += 1
                    self.board.remove_item_from_board(card.reward_item)
                elif card.name == CardName.FAVOR_OF_THE_FOXES:
                    self.favor_card(faction, Suit.FOX)
                elif card.name == CardName.FAVOR_OF_THE_MICE:
                    self.favor_card(faction, Suit.MOUSE)
                elif card.name == CardName.FAVOR_OF_THE_RABBITS:
                    self.favor_card(faction, Suit.RABBIT)
                self.discard_card(self.marquise.cards_in_hand, card)
            else:
                self.marquise.cards_in_hand.remove(card)
                self.marquise.crafted_cards.append(card)

            for suit in card.craft_requirement.keys():
                self.marquise.spend_crafting_piece(suit, card.craft_requirement[suit])

            self.prompt = "{} has been crafted.".format(card.name)
            self.set_actions([Action("Next", self.marquise_daylight)])

        elif faction == Faction.EYRIE:
            if card.phase == CardPhase.IMMEDIATE:
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
                elif card.name == CardName.FAVOR_OF_THE_FOXES:
                    self.favor_card(faction, Suit.FOX)
                elif card.name == CardName.FAVOR_OF_THE_MICE:
                    self.favor_card(faction, Suit.MOUSE)
                elif card.name == CardName.FAVOR_OF_THE_RABBITS:
                    self.favor_card(faction, Suit.RABBIT)

                self.discard_card(self.eyrie.cards_in_hand, card)
            else:
                self.eyrie.cards_in_hand.remove(card)
                self.eyrie.crafted_cards.append(card)

            for suit in card.craft_requirement.keys():
                self.marquise.spend_crafting_piece(suit, card.craft_requirement[suit])
            self.eyrie_daylight_craft()

    def get_craftable_cards(self, faction: Faction) -> list[Card]:
        craftable_cards: list[Card] = []

        cards_in_hand: list[Card] = []
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
                elif self.duplicated_crafted_cards(faction, card):
                    can_craft = False
            if can_craft:
                craftable_cards.append(card)

        return craftable_cards

    def duplicated_crafted_cards(self, faction, card):
        faction_board = self.faction_to_faction_board(faction)
        for crafted_card in faction_board.crafted_cards:
            if card.name == crafted_card.name:
                return True
        return False

    def select_card(self, card: Card):
        self.selected_card = card

    def can_take_card_from_draw_pile(self, amount: int = 1) -> bool:
        return len(self.draw_pile) >= amount

    def take_card_from_draw_pile(self, faction: Faction, amount: int = 1):
        faction_board = self.marquise

        if faction == Faction.EYRIE:
            faction_board = self.eyrie

        if self.can_take_card_from_draw_pile(amount):
            faction_board.cards_in_hand.extend(self.draw_pile[0:amount])
            self.draw_pile = self.draw_pile[amount:]
            LOGGER.debug(
                "{}:{}:{}:{} drawn {} card(s)".format(self.ui_turn_player, self.phase, self.sub_phase, faction, amount))
        else:
            lesser_amount = min(len(self.draw_pile), amount)
            faction_board.cards_in_hand.extend(self.draw_pile[0:lesser_amount])
            self.draw_pile = self.draw_pile[lesser_amount:]
            LOGGER.debug(
                "{}:{}:{}:{} drawn {} card(s)".format(self.ui_turn_player, self.phase, self.sub_phase, faction,
                                                      lesser_amount))

            self.shuffle_discard_pile_into_draw_pile()

            remaining_amount = amount - lesser_amount
            faction_board.cards_in_hand.extend(self.draw_pile[0:remaining_amount])
            self.draw_pile = self.draw_pile[remaining_amount:]
            LOGGER.debug(
                "{}:{}:{}:{} drawn {} card(s)".format(self.ui_turn_player, self.phase, self.sub_phase, faction,
                                                      remaining_amount))

    def shuffle_discard_pile_into_draw_pile(self):
        self.draw_pile.extend(self.discard_pile)
        self.discard_pile = []
        self.shuffle_draw_pile()

    def discard_card(self, discard_from: list[Card], card: Card):
        discard_from.remove(card)
        if card.name in Card.DOMINANCE_CARD_NAMES:
            self.discard_pile_dominance.append(card)
        else:
            self.discard_pile.append(card)

    def generate_actions_agent_move(self, faction: Faction) -> list[Action]:
        actions: list[Action] = []

        can_move_from_clearing = self.find_available_source_clearings(faction, decree=(faction == Faction.EYRIE))
        for src in can_move_from_clearing:
            dests = self.find_available_destination_clearings(faction, src)
            for dest in dests:
                for num_of_warriors in range(1, src.warrior_count[faction_to_warrior(faction)] + 1):
                    actions.append(Action("Move {} warriors from {} to {}".format(
                        num_of_warriors, src.area_index, dest.area_index),
                        perform(self.move_warriors,
                                faction, src, dest,
                                num_of_warriors, self.eyrie_resolve_move)))
        return actions

    def generate_actions_agent_move_with_cont_func(self, faction: Faction, cont_func) -> list[Action]:
        actions: list[Action] = []

        can_move_from_clearing = self.find_available_source_clearings(faction, decree=False)  # TODO: investigate this generating 0 actions
        for src in can_move_from_clearing:
            dests = self.find_available_destination_clearings(faction, src)
            for dest in dests:
                for num_of_warriors in range(1, src.warrior_count[faction_to_warrior(faction)] + 1):
                    actions.append(Action("Move {} warriors from {} to {}".format(
                        num_of_warriors, src.area_index, dest.area_index),
                        perform(self.move_warriors,
                                faction, src, dest,
                                num_of_warriors, cont_func)))
        return actions

    def select_clearing_src_move(self, faction, continuation_func, decree=False):
        actions = self.generate_actions_select_src_clearing(faction, continuation_func, decree)
        self.prompt = "Choose area to move from."
        self.set_actions(actions)

    def generate_actions_select_src_clearing(self, faction, continuation_func, decree) -> list[Action]:
        can_move_from_clearing = self.find_available_source_clearings(faction, decree)
        actions = []

        for clearing in can_move_from_clearing:
            actions.append(
                Action("{}".format(clearing),
                       perform(self.select_clearing_dest_move, faction, clearing, continuation_func)))

        return actions

    def select_clearing_dest_move(self, faction, src, continuation_func):
        actions = self.generate_actions_select_dest_clearing(faction, src, continuation_func)
        self.prompt = "Choose area to move to."
        self.set_actions(actions)

    def generate_actions_select_dest_clearing(self, faction, src, continuation_func) -> list[Action]:
        dests = self.find_available_destination_clearings(faction, src)
        actions = []

        for dest in dests:
            actions.append(
                Action("{}".format(dest),
                       perform(self.select_warriors, faction, src, dest, continuation_func)))

        return actions

    def select_warriors(self, faction, src, dest, continuation_func):
        actions = self.generate_actions_select_warriors(faction, src, dest, continuation_func)
        self.prompt = "Choose number of warriors to move."
        self.set_actions(actions)

    def generate_actions_select_warriors(self, faction, src: Area, dest: Area, continuation_func) -> list[
        Action]:
        actions = []

        for num_of_warriors in range(1, src.warrior_count[faction_to_warrior(faction)] + 1):
            actions.append(Action("{}".format(num_of_warriors),
                                  perform(self.move_warriors, faction, src, dest, num_of_warriors, continuation_func)))

        return actions

    def move_warriors(self, faction, src: Area, dest: Area, num, continuation_func):
        LOGGER.debug(
            "{}:{}:{}:{} move {} warrior(s) from Clearing #{} to Clearing #{}".format(self.ui_turn_player, self.phase,
                                                                                      self.sub_phase, faction,
                                                                                      num, src,
                                                                                      dest))
        self.selected_clearing = src
        src.remove_warrior(faction_to_warrior(faction), num)
        dest.add_warrior(faction_to_warrior(faction), num)

        continuation_func()

    def find_available_source_clearings(self, faction: Faction, decree=False) -> list[Area]:
        movable_clearings: list[Area] = []

        if (faction == Faction.MARQUISE) or (faction == Faction.EYRIE and not decree):
            for area in self.board.areas:
                if len(self.find_available_destination_clearings(faction, area)) <= 0:
                    continue
                if area.ruler() == faction_to_warrior(faction) and area.warrior_count[faction_to_warrior(faction)] > 0:
                    movable_clearings.append(area)
                else:
                    for connected_area in area.connected_clearings:
                        if area.warrior_count[
                            faction_to_warrior(faction)] > 0 and connected_area.ruler() == faction_to_warrior(faction):
                            movable_clearings.append(area)
                            break
        elif faction == Faction.EYRIE and decree:
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

    def find_available_destination_clearings(self, faction: Faction, src: Area) -> list[Area]:
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
            self.marquise_recruit_count -= 1
            self.marquise_action_count -= 1
            for area in self.board.areas:
                total_recruiters = area.buildings.count(Building.RECRUITER)
                if total_recruiters > 0:
                    self.add_warrior(faction, area, min(total_recruiters, self.marquise.reserved_warriors))
                    LOGGER.debug(
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

            LOGGER.debug(
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

    def generate_actions_agent_battle(self, attacker, continuation_func, decree) -> list[Action]:
        clearings = self.get_battlable_clearing(attacker, decree)

        actions: list[Action] = []
        for clearing in clearings:
            enemy_factions: list[Faction] = self.get_available_enemy_tokens_from_clearing(attacker, clearing)

            for enemy_faction in enemy_factions:
                actions.append(
                    Action("Attack {} in area {}".format(enemy_faction, clearing.area_index),
                           perform(self.initiate_battle, attacker, enemy_faction, clearing, continuation_func)))

        return actions

    def select_clearing_battle(self, attacker, continuation_func, decree=True):
        actions = self.generate_actions_select_clearing_battle(attacker, continuation_func, decree)
        self.prompt = "Select Clearing"
        self.set_actions(actions)

    def generate_actions_select_clearing_battle(self, attacker, continuation_func, decree) -> list[Action]:
        clearings = self.get_battlable_clearing(attacker, decree)
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

    def get_battlable_clearing(self, faction, decree):
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
                if decree and decree_can_battle_in[area.suit] == 0 and decree_can_battle_in[Suit.BIRD] == 0:
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

    def reset_battle_variables(self):
        self.attacker = None
        self.defender = None
        self.attacking_clearing = None
        self.continuation_func = None

        self.attacker_roll = 0
        self.defender_roll = 0
        self.defender_defenseless_extra_hits = 0
        self.attacker_extra_hits = 0
        self.defender_extra_hits = 0

        self.redirect_func = None
        self.attacker_remaining_hits = 0
        self.defender_remaining_hits = 0
        self.marquise_removed_warrior = 0

        self.selecting_piece_to_remove_faction = None

    def initiate_battle(self, attacker, defender, clearing: Area, continuation_func):
        self.reset_battle_variables()
        self.selected_clearing = clearing

        self.attacker = attacker
        self.defender = defender
        self.attacking_clearing = clearing
        self.continuation_func = continuation_func

        LOGGER.debug(
            "{}:{}:{}:battle:{} initiate battle on {} in clearing #{}".format(self.ui_turn_player, self.phase,
                                                                              self.sub_phase,
                                                                              attacker, defender, clearing.area_index))
        attacker_board = self.faction_to_faction_board(attacker)
        defender_board = self.faction_to_faction_board(defender)
        atk_scouting_party = [card for card in attacker_board.crafted_cards if
                              card.name == CardName.SCOUTING_PARTY]
        def_ambush = [card for card in defender_board.cards_in_hand if
                      card.name == CardName.AMBUSH and (card.suit == Suit.BIRD or card.suit == clearing.suit)]

        if len(atk_scouting_party) > 0 or len(def_ambush) == 0:
            self.roll_dice()
        else:
            self.defender_use_ambush()

    def defender_use_ambush(self):  # 40001
        self.sub_phase = 40001
        self.ui_turn_player = self.defender
        self.prompt = "{}: Use Ambush Card?".format(self.defender)

        defender_board = self.faction_to_faction_board(self.defender)
        def_ambush_actions = []
        def_ambush = [card for card in defender_board.cards_in_hand if
                      card.name == CardName.AMBUSH and (
                              card.suit == Suit.BIRD or card.suit == self.attacking_clearing.suit)]
        for card in def_ambush:
            def_ambush_actions.append(Action('Discard {} ({})'.format(card.name, card.suit),
                                             perform(self.attacker_use_ambush, card)))

        self.set_actions(
            def_ambush_actions + [
                Action('Skip', perform(self.roll_dice))])

    def attacker_use_ambush(self, ambush_discarded):  # 40002
        LOGGER.debug(
            "{}:{}:{}:battle:{} discard AMBUSH".format(self.ui_turn_player, self.phase, self.sub_phase, self.defender))
        defender_board = self.faction_to_faction_board(self.defender)
        self.discard_card(defender_board.cards_in_hand, ambush_discarded)

        self.ui_turn_player = self.attacker
        self.prompt = "{}: Use Ambush Card?".format(self.attacker)

        attacker_board = self.faction_to_faction_board(self.attacker)
        atk_ambush = [card for card in attacker_board.cards_in_hand if card.name == CardName.AMBUSH]

        self.defender_extra_hits += 2

        if len(atk_ambush) == 0:
            self.resolve_hits(self.roll_dice)
        else:
            self.sub_phase = 40002
            atk_ambush_actions = []
            for card in atk_ambush:
                atk_ambush_actions.append(Action('Discard {} ({})'.format(card.name, card.suit),
                                                 perform(self.foil_ambush, card)))
            self.set_actions(
                atk_ambush_actions
                + [Action('Skip',
                          perform(self.resolve_hits, self.roll_dice))]
            )

    def foil_ambush(self, ambush_discarded):
        LOGGER.debug(
            "{}:{}:{}:battle:{} discard AMBUSH".format(self.ui_turn_player, self.phase, self.sub_phase, self.attacker))
        self.defender_extra_hits -= 2
        attacker_board = self.faction_to_faction_board(self.attacker)
        self.discard_card(attacker_board.cards_in_hand, ambush_discarded)
        self.roll_dice()

    def roll_dice(self):

        # After ambush, check if there are remaining attacker's warrior.
        if self.attacking_clearing.warrior_count[faction_to_warrior(self.attacker)] == 0:
            self.continuation_func()
        else:
            dices: list[int] = [randint(0, 3), randint(0, 3)]
            self.attacker_roll = max(dices)
            self.defender_roll = min(dices)

            self.defender_defenseless_extra_hits = 1 if (
                    self.attacking_clearing.get_warrior_count(faction_to_warrior(self.defender)) == 0) else 0

            self.attacker_extra_hits = ((1 if (
                    self.attacker == Faction.EYRIE and self.eyrie.get_active_leader() == EyrieLeader.COMMANDER) else 0)
                                        + self.defender_defenseless_extra_hits)
            self.defender_extra_hits = 0

            LOGGER.debug(
                "{}:{}:{}:battle:{} rolls {}, {} rolls {}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                  self.attacker, self.attacker_roll, self.defender,
                                                                  self.defender_roll))

            self.attacker_activate_battle_ability_card()

    def attacker_activate_battle_ability_card(self):  # 40003
        LOGGER.debug(
            "{}:{}:{}:battle: Total hits: {}: ({}+{}) hits, {}: ({}+{}) hits".format(self.ui_turn_player, self.phase,
                                                                                     self.sub_phase,
                                                                                     self.attacker,
                                                                                     self.attacker_roll + self.attacker_extra_hits,
                                                                                     self.attacker_roll,
                                                                                     self.attacker_extra_hits,
                                                                                     self.defender,
                                                                                     self.defender_roll + self.defender_extra_hits,
                                                                                     self.defender_roll,
                                                                                     self.defender_extra_hits))

        attacker_faction_board = self.faction_to_faction_board(self.attacker)

        atk_brutal_tactics = [card for card in attacker_faction_board.crafted_cards if
                              card.name == CardName.BRUTAL_TACTICS]
        atk_armorers = [card for card in attacker_faction_board.crafted_cards if card.name == CardName.ARMORERS]

        atk_actions = []

        if len(atk_brutal_tactics) > 0 and attacker_faction_board.activated_card.count(atk_brutal_tactics[0]) < 1:
            brutal_tactics_card = atk_brutal_tactics[0]
            atk_actions.append(Action('Use {} ({})'.format(brutal_tactics_card.name, brutal_tactics_card.suit),
                                      perform(self.brutal_tactics, brutal_tactics_card)))

        if len(atk_armorers) > 0 and attacker_faction_board.activated_card.count(atk_armorers[0]) < 1:
            armorers_card = atk_armorers[0]
            atk_actions.append(Action('Use {} ({})'.format(armorers_card.name, armorers_card.suit),
                                      perform(self.armorers, self.attacker, armorers_card)))

        if len(atk_actions) > 0:
            self.sub_phase = 40003
            self.ui_turn_player = self.attacker
            self.prompt = "{}: Activate Battle Ability Card?".format(self.attacker)
            self.set_actions(atk_actions + [Action('Skip',
                                                   perform(self.defender_activate_battle_ability_card))])
        else:
            self.defender_activate_battle_ability_card()

    def defender_activate_battle_ability_card(self):  # 40004
        LOGGER.debug(
            "{}:{}:{}:battle: Total hits: {}: ({}+{}) hits, {}: ({}+{}) hits".format(self.ui_turn_player, self.phase,
                                                                                     self.sub_phase,
                                                                                     self.attacker,
                                                                                     self.attacker_roll + self.attacker_extra_hits,
                                                                                     self.attacker_roll,
                                                                                     self.attacker_extra_hits,
                                                                                     self.defender,
                                                                                     self.defender_roll + self.defender_extra_hits,
                                                                                     self.defender_roll,
                                                                                     self.defender_extra_hits))

        defender_faction_board = self.faction_to_faction_board(self.defender)

        def_sappers = [card for card in defender_faction_board.crafted_cards if card.name == CardName.SAPPERS]
        def_armorers = [card for card in defender_faction_board.crafted_cards if card.name == CardName.ARMORERS]

        def_actions = []

        if len(def_sappers) > 0 and defender_faction_board.activated_card.count(def_sappers[0]) < 1:
            sappers_card = def_sappers[0]
            def_actions.append(Action('Use {} ({})'.format(sappers_card.name, sappers_card.suit),
                                      perform(self.sappers, sappers_card)))

        if len(def_armorers) > 0 and defender_faction_board.activated_card.count(def_armorers[0]) < 1:
            armorers_card = def_armorers[0]
            def_actions.append(Action('Use {} ({})'.format(armorers_card.name, armorers_card.suit),
                                      perform(self.armorers, self.defender, armorers_card)))

        if len(def_actions) > 0:
            self.sub_phase = 40004
            self.ui_turn_player = self.defender
            self.prompt = "{}: Activate Battle Ability Card?".format(self.defender)
            self.set_actions(def_actions + [Action('Skip',
                                                   perform(self.resolve_hits))])
        else:
            self.resolve_hits()

    def brutal_tactics(self, brutal_tactics_card):
        LOGGER.debug(
            "{}:{}:{}:battle:{} use BRUTAL TACTICS".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                           self.attacker))
        attacker_faction_board = self.faction_to_faction_board(self.attacker)
        attacker_faction_board.activated_card.append(brutal_tactics_card)
        self.gain_vp(self.defender, 1)
        self.attacker_extra_hits += 1
        self.attacker_activate_battle_ability_card()

    def armorers(self, faction, armorers_card):
        LOGGER.debug(
            "{}:{}:{}:battle:{} discard ARMORERS".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                         faction))

        faction_board = self.faction_to_faction_board(faction)
        faction_board.activated_card.append(armorers_card)
        self.discard_card(faction_board.crafted_cards, armorers_card)

        if faction == self.attacker:
            self.defender_roll = 0
            self.attacker_activate_battle_ability_card()
        elif faction == self.defender:
            self.attacker_roll = 0
            self.defender_activate_battle_ability_card()

    def sappers(self, sappers_card):
        LOGGER.debug(
            "{}:{}:{}:battle:{} discard BRUTAL TACTICS".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                               self.defender))

        defender_faction_board = self.faction_to_faction_board(self.defender)
        defender_faction_board.activated_card.append(sappers_card)
        self.discard_card(defender_faction_board.crafted_cards, sappers_card)
        self.defender_extra_hits += 1
        self.defender_activate_battle_ability_card()

    def resolve_hits(self, redirect_func=None):

        self.redirect_func = redirect_func

        attacker_faction_board = self.faction_to_faction_board(self.attacker)
        defender_faction_board = self.faction_to_faction_board(self.defender)

        attacker_total_hits: int = min(self.attacker_roll, self.attacking_clearing.get_warrior_count(
            faction_to_warrior(self.attacker))) + self.attacker_extra_hits
        defender_total_hits: int = min(self.attacker_roll,
                                       self.attacking_clearing.get_warrior_count(
                                           faction_to_warrior(self.defender))) + self.defender_extra_hits

        # deal hits
        self.attacker_remaining_hits = attacker_total_hits
        self.defender_remaining_hits = defender_total_hits
        # to attacker
        removed_attacker_warriors = self.attacking_clearing.remove_warrior(faction_to_warrior(self.attacker),
                                                                           self.defender_remaining_hits)
        self.defender_remaining_hits -= removed_attacker_warriors
        attacker_faction_board.reserved_warriors += removed_attacker_warriors
        # to defender
        removed_defender_warriors = self.attacking_clearing.remove_warrior(faction_to_warrior(self.defender),
                                                                           self.attacker_remaining_hits)
        self.attacker_remaining_hits -= removed_defender_warriors
        defender_faction_board.reserved_warriors += removed_defender_warriors

        # score
        attacker_total_vp = removed_defender_warriors
        defender_total_vp = removed_attacker_warriors

        self.gain_vp(self.attacker, attacker_total_vp)
        self.gain_vp(self.defender, defender_total_vp)

        LOGGER.debug(
            "{}:{}:{}:battle: {} vs {}, total hits {}:{}, vps gained {}:{}".format(self.ui_turn_player, self.phase,
                                                                                   self.sub_phase,
                                                                                   self.attacker, self.defender,
                                                                                   attacker_total_hits,
                                                                                   defender_total_hits,
                                                                                   attacker_total_vp, defender_total_vp)
        )

        if self.attacker == Faction.MARQUISE and removed_attacker_warriors > 0 and self.marquise_field_hospital_check(
                self.attacking_clearing):
            self.marquise_removed_warrior = removed_attacker_warriors
            self.resolve_marquise_field_hospital()
        elif self.defender == Faction.MARQUISE and removed_defender_warriors > 0 and self.marquise_field_hospital_check(
                self.attacking_clearing):
            self.marquise_removed_warrior = removed_defender_warriors
            self.resolve_marquise_field_hospital()
        else:
            self.resolve_remaining_hits()

    def resolve_marquise_field_hospital(self):  # 40005
        self.sub_phase = 40005
        self.ui_turn_player = Faction.MARQUISE
        self.prompt = "MARQUISE: Discard a card matching warrior's clearing to bring {} warriors back to the keep.".format(
            self.marquise_removed_warrior)
        self.set_actions(
            self.generate_actions_field_hospital_select_card_to_discard()
            + [Action('Next', perform(self.resolve_remaining_hits))]
        )

    def marquise_field_hospital_check(self, clearing: Area):
        return len(self.marquise_field_hospital_get_cards(clearing)) > 0

    def marquise_field_hospital_get_cards(self, clearing):
        return [card for card in self.marquise.cards_in_hand if card.suit == clearing.suit]

    def generate_actions_field_hospital_select_card_to_discard(self):
        discardable_cards = self.marquise_field_hospital_get_cards(self.attacking_clearing)
        actions = []

        for card in discardable_cards:
            actions.append(
                Action("{} ({})".format(card.name, card.suit),
                       perform(self.marquise_field_hospital, card)))

        return actions

    def marquise_field_hospital(self, card):
        LOGGER.debug(
            "{}:{}:{}:battle:{} use field hospital, discarding {} ({})".format(self.ui_turn_player, self.phase,
                                                                               self.sub_phase,
                                                                               Faction.MARQUISE,
                                                                               card.name, card.suit))

        self.discard_card(self.marquise.cards_in_hand, card)
        for clearing in self.board.areas:
            if clearing.token_count[Token.CASTLE] > 0:
                clearing.add_warrior(Warrior.MARQUISE, self.marquise_removed_warrior)
                break

        self.resolve_remaining_hits()

    def resolve_remaining_hits(self):
        LOGGER.debug(
            "{}:{}:{}:battle: {} vs {}, remaining hits {}:{}".format(self.ui_turn_player, self.phase,
                                                                     self.sub_phase,
                                                                     self.attacker, self.defender,
                                                                     self.attacker_remaining_hits,
                                                                     self.defender_remaining_hits)
        )
        if self.attacker_remaining_hits == 0 and self.defender_remaining_hits == 0:
            if self.redirect_func is not None:
                self.redirect_func()
            else:
                self.continuation_func()
        elif self.defender_remaining_hits > 0:
            self.selecting_piece_to_remove_faction = self.attacker
            self.select_piece_to_remove()
        elif self.attacker_remaining_hits > 0:
            self.selecting_piece_to_remove_faction = self.defender
            self.select_piece_to_remove()

    def select_piece_to_remove(self):  # 40006
        self.ui_turn_player = self.selecting_piece_to_remove_faction
        self.prompt = "{}: Select Piece to Remove".format(self.selecting_piece_to_remove_faction)
        actions = self.generate_actions_select_piece_to_remove()

        if len(actions) == 0:
            if self.selecting_piece_to_remove_faction == self.attacker:
                self.defender_remaining_hits = 0
                self.resolve_remaining_hits()
            elif self.selecting_piece_to_remove_faction == self.defender:
                self.attacker_remaining_hits = 0
                self.resolve_remaining_hits()
        else:
            self.sub_phase = 40006
            self.set_actions(actions)

    def generate_actions_select_piece_to_remove(self):
        actions = []
        buildings = faction_to_buildings(self.selecting_piece_to_remove_faction)
        tokens = faction_to_tokens(self.selecting_piece_to_remove_faction)

        if self.selecting_piece_to_remove_faction == Faction.MARQUISE:
            for token in tokens:
                if token == Token.WOOD and self.attacking_clearing.token_count[token] > 0:
                    actions.append(
                        Action("Wood",
                               perform(self.remove_piece, Token.WOOD))
                    )
            for building in buildings:
                if self.attacking_clearing.buildings.count(building) > 0:
                    actions.append(
                        Action(building.name,
                               perform(self.remove_piece, building))
                    )

        elif self.selecting_piece_to_remove_faction == Faction.EYRIE:
            for building in buildings:
                if self.attacking_clearing.buildings.count(building) > 0:
                    actions.append(
                        Action(building.name,
                               perform(self.remove_piece, building))
                    )

        return actions

    def remove_piece(self, piece):
        if isinstance(piece, Building):
            if self.selecting_piece_to_remove_faction == Faction.MARQUISE:
                self.marquise.building_trackers[piece] -= 1
            elif self.selecting_piece_to_remove_faction == Faction.EYRIE:
                self.eyrie.roost_tracker -= 1
            self.attacking_clearing.remove_building(piece)
        elif isinstance(piece, Token):
            self.attacking_clearing.remove_token(piece)

        if self.selecting_piece_to_remove_faction == self.attacker:
            LOGGER.debug(
                "{}:{}:{}:battle:{} remove {}'s {}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                           self.defender, self.attacker, piece))
            self.gain_vp(self.defender, 1)
            self.defender_remaining_hits -= 1
            self.resolve_remaining_hits()
        else:
            LOGGER.debug(
                "{}:{}:{}:battle:{} remove {}'s {}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                           self.attacker, self.defender, piece))
            self.gain_vp(self.attacker, 1)
            self.attacker_remaining_hits -= 1
            self.resolve_remaining_hits()

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

    def select_card_to_discard(self, faction: Faction, card: Card):  # 10017
        faction_board = self.faction_to_faction_board(faction)
        LOGGER.debug(
            "{}:{}:{}:{}:{} ({}) discarded".format(self.ui_turn_player, self.phase, self.sub_phase, faction,
                                                   card.name, card.suit))
        self.discard_card(faction_board.cards_in_hand, card)
        card_in_hand_count = len(faction_board.cards_in_hand)
        if card_in_hand_count > 5:
            self.prompt = "Select card to discard down to 5 cards (currently {} cards in hand)".format(
                card_in_hand_count)
            self.set_actions(self.generate_actions_select_card_to_discard(faction))
            if faction == Faction.MARQUISE:
                self.sub_phase = 10017
        else:
            if faction == Faction.MARQUISE:
                self.marquise_evening_discard_card()
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
            if card.name not in Card.DOMINANCE_CARD_NAMES:
                continue
            actions.append(Action("Activate {}".format(card.name),
                                  perform(self.activate_dominance_card, faction, card, perform(continuation_func))))

        return actions

    def activate_dominance_card(self, faction: Faction, card: Card, continuation_func: any):
        if config['game']['allow-dominance-card']:
            LOGGER.debug(
                "{}:{}:{}:{}:activate_dominance_card {} ".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                 faction,
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

    def take_dominance_card(self, faction: Faction, dominance_card: Card, card_to_spend: Card,
                            continuation_func: any):
        LOGGER.debug(
            "{}:{}:{}:{}:take_dominance_card {} by spending {}".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                       faction,
                                                                       dominance_card.name, card_to_spend.name))

        faction_board = self.faction_to_faction_board(faction)

        self.discard_card(faction_board.cards_in_hand, card_to_spend)

        faction_board.cards_in_hand.append(dominance_card)
        self.discard_pile_dominance.remove(dominance_card)

        continuation_func()

    def generate_actions_cards_birdsong(self, faction, continuation_func):
        self.cards_birdsong_continuation_func = continuation_func
        actions = []
        faction_board = self.faction_to_faction_board(faction)
        for card in faction_board.crafted_cards:
            if faction_board.activated_card.count(card) > 0:
                continue
            if card.name == CardName.ROYAL_CLAIM:
                actions.append(Action('Discard {}'.format(card.name),
                                      perform(self.royal_claim, faction, card)))
            if card.name == CardName.STAND_AND_DELIVER and self.stand_and_deliver_check(faction):
                actions.append(
                    Action('Use {} effect'.format(card.name),
                           perform(self.stand_and_deliver_select_faction, faction, card)))
        return actions

    def generate_actions_agent_cards_birdsong(self, faction, continuation_func):
        self.cards_birdsong_continuation_func = continuation_func
        actions = []
        faction_board = self.faction_to_faction_board(faction)
        for card in faction_board.crafted_cards:
            if faction_board.activated_card.count(card) > 0:
                continue
            if card.name == CardName.ROYAL_CLAIM:
                actions.append(Action('Discard {}'.format(card.name),
                                      perform(self.royal_claim, faction, card)))
            if card.name == CardName.STAND_AND_DELIVER and self.stand_and_deliver_check(faction):
                actions = actions + self.generate_actions_agent_stand_and_deliver(faction, card)
        return actions

    def royal_claim(self, faction, card):
        LOGGER.debug("{}:{}:{}:Enter royal_claim".format(self.ui_turn_player, self.phase, self.sub_phase))
        faction_board = self.faction_to_faction_board(faction)

        self.discard_card(faction_board.crafted_cards, card)

        gained_vp = 0
        for clearing in self.board.areas:
            if clearing.ruler() == faction_to_warrior(faction):
                gained_vp += 1
        self.gain_vp(faction, gained_vp)

        LOGGER.debug(
            "{}:{}:{}:{} discard ROYAL_CLAIM, {} vp gained".format(self.ui_turn_player, self.phase, self.sub_phase,
                                                                   faction, gained_vp))

        self.cards_daylight_continuation_func()

    def stand_and_deliver_check(self, faction):
        LOGGER.debug("{}:{}:{}:Enter stand_and_deliver_check".format(self.ui_turn_player, self.phase, self.sub_phase))

        available = False
        available_faction = [Faction.MARQUISE, Faction.EYRIE]
        available_faction.remove(faction)

        for enemy_faction in available_faction:
            if len(self.faction_to_faction_board(enemy_faction).cards_in_hand) > 0:
                available = True
        return available

    def stand_and_deliver_select_faction(self, faction, card):
        LOGGER.debug(
            "{}:{}:{}:Enter stand_and_deliver_select_faction".format(self.ui_turn_player, self.phase, self.sub_phase))

        self.prompt = "Select Faction"
        self.set_actions(self.generate_actions_stand_and_deliver_select_faction(faction, card))

    def generate_actions_agent_stand_and_deliver(self, faction, card) -> list[Action]:
        LOGGER.debug(
            "{}:{}:{}:Enter generate_actions_agent_stand_and_deliver".format(self.ui_turn_player, self.phase,
                                                                             self.sub_phase))

        actions: list[Action] = []
        available_faction: list[Faction] = [Faction.MARQUISE, Faction.EYRIE]
        available_faction.remove(faction)

        for enemy_faction in available_faction:
            if len(self.faction_to_faction_board(enemy_faction).cards_in_hand) > 0:
                actions.append(
                    Action('Use {} card on {}'.format(card.name, enemy_faction),
                           perform(self.stand_and_deliver, faction, enemy_faction, card)))
        return actions

    def generate_actions_stand_and_deliver_select_faction(self, faction, card) -> list[Action]:
        LOGGER.debug(
            "{}:{}:{}:Enter generate_actions_stand_and_deliver_select_faction".format(self.ui_turn_player, self.phase,
                                                                                      self.sub_phase))

        actions: list[Action] = []
        available_faction: list[Faction] = [Faction.MARQUISE, Faction.EYRIE]
        available_faction.remove(faction)

        for enemy_faction in available_faction:
            if len(self.faction_to_faction_board(enemy_faction).cards_in_hand) > 0:
                actions.append(
                    Action('{}'.format(enemy_faction),
                           perform(self.stand_and_deliver, faction, enemy_faction, card)))
        return actions

    def stand_and_deliver(self, faction, stolen_faction, card):
        LOGGER.debug("{}:{}:{}:Enter stand_and_deliver".format(self.ui_turn_player, self.phase, self.sub_phase))

        faction_board = self.faction_to_faction_board(faction)
        stolen_faction_board = self.faction_to_faction_board(stolen_faction)

        faction_board.activated_card.append(card)

        random_card = random.choice(stolen_faction_board.cards_in_hand)

        self.discard_card(stolen_faction_board.cards_in_hand, random_card)
        faction_board.cards_in_hand.append(random_card)

        self.gain_vp(stolen_faction, 1)

        self.cards_birdsong_continuation_func()

    def better_burrow_bank(self,
                           faction):  # There is only 2 faction. So when this effect activate, both faction draws a card.
        faction_board = self.faction_to_faction_board(faction)
        cards = [card for card in faction_board.crafted_cards if card.name == CardName.BETTER_BURROW_BANK]
        if len(cards) > 0:
            for faction in [Faction.MARQUISE, Faction.EYRIE]:
                self.take_card_from_draw_pile(faction)

    def generate_actions_agent_cards_daylight(self, faction, continuation_func):
        self.cards_daylight_continuation_func = continuation_func
        actions = []
        faction_board = self.faction_to_faction_board(faction)
        for card in faction_board.crafted_cards:
            if faction_board.activated_card.count(card) > 0:
                continue
            if card.name == CardName.TAX_COLLECTOR and self.tax_collector_check(faction):
                actions += self.generate_actions_agent_tax_collector(faction, card)
            if card.name == CardName.CODEBREAKERS:
                actions.append(Action('* Use {} card'.format(card.name),
                                      perform(self.codebreakers, faction, card)))

        return actions

    def generate_actions_cards_daylight(self, faction, continuation_func):
        self.cards_daylight_continuation_func = continuation_func
        actions = []
        faction_board = self.faction_to_faction_board(faction)
        for card in faction_board.crafted_cards:
            if faction_board.activated_card.count(card) > 0:
                continue
            if card.name == CardName.TAX_COLLECTOR and self.tax_collector_check(faction):
                actions.append(Action('* Use {} card'.format(card.name),
                                      perform(self.tax_collector_select_clearing, faction, card)))
            if card.name == CardName.CODEBREAKERS:
                actions.append(Action('* Use {} card'.format(card.name),
                                      perform(self.codebreakers, faction, card)))

        return actions

    def generate_actions_command_warren(self, faction, continuation_func):
        actions = []
        faction_board = self.faction_to_faction_board(faction)

        for card in faction_board.crafted_cards:
            if card.name == CardName.COMMAND_WARREN and len(
                    self.generate_actions_select_clearing_battle(faction, continuation_func, False)) != 0:
                actions.append(
                    Action('Use {} card'.format(card.name),
                           perform(self.command_warren, card, faction, continuation_func)))

        return actions

    def command_warren(self, card, faction, continuation_func):
        faction_board = self.faction_to_faction_board(faction)
        faction_board.activated_card.append(card)
        self.select_clearing_battle(faction, continuation_func, False)

    def tax_collector_check(self, faction):
        available = False
        for clearing in self.board.areas:
            if clearing.warrior_count[faction_to_warrior(faction)] > 0:
                available = True
        return available

    def tax_collector_select_clearing(self, faction, card):
        self.prompt = "Select Clearing"
        self.set_actions(self.generate_actions_tax_collector_select_clearing(faction, card))

    def generate_actions_agent_tax_collector(self, faction, card) -> list[Action]:
        actions: list[Action] = []

        for clearing in self.board.areas:
            if clearing.warrior_count[faction_to_warrior(faction)] > 0:
                actions.append(Action('* Use Tax Collector: remove 1 warrior from {}'.format(clearing.area_index),
                                      perform(self.tax_collector, faction, clearing, card)))

        return actions

    def generate_actions_tax_collector_select_clearing(self, faction, card) -> list[Action]:
        actions: list[Action] = []

        for clearing in self.board.areas:
            if clearing.warrior_count[faction_to_warrior(faction)] > 0:
                actions.append(Action('{}'.format(clearing.area_index),
                                      perform(self.tax_collector, faction, clearing, card)))

        return actions

    def tax_collector(self, faction, clearing, card):
        LOGGER.debug("{}:{}:{}:Enter tax_collector".format(self.ui_turn_player, self.phase, self.sub_phase))
        faction_board = self.faction_to_faction_board(faction)
        warrior = faction_to_warrior(faction)

        clearing.remove_warrior(warrior, 1)
        faction_board.reserved_warriors += 1

        self.take_card_from_draw_pile(faction, 1)
        faction_board.activated_card.append(card)

        self.cards_daylight_continuation_func()

    def codebreakers(self, faction, card):  # 30002
        self.sub_phase = 30002
        LOGGER.debug("{}:{}:{}:Enter codebreakers".format(self.ui_turn_player, self.phase, self.sub_phase))

        if faction == Faction.MARQUISE:
            enemy_faction = Faction.EYRIE
        else:
            enemy_faction = Faction.MARQUISE

        faction_board = self.faction_to_faction_board(faction)
        enemy_faction_board = self.faction_to_faction_board(enemy_faction)

        prompt_str = ""
        for card_in_hand in enemy_faction_board.cards_in_hand:
            prompt_str = prompt_str + "{} ({}), ".format(card_in_hand.name, card_in_hand.suit)
        faction_board.activated_card.append(card)

        self.prompt = prompt_str
        self.set_actions([Action('Next', self.cards_daylight_continuation_func)])

    def generate_actions_cobbler(self, faction, continuation_func):
        actions = []
        faction_board = self.faction_to_faction_board(faction)

        for card in faction_board.crafted_cards:
            if card.name == CardName.COBBLER and len(
                    self.generate_actions_select_src_clearing(faction, continuation_func, False)) != 0:
                actions.append(
                    Action('Use {} card'.format(card.name),
                           perform(self.cobbler, card, faction, continuation_func)))

        return actions

    def generate_actions_agent_cobbler(self, faction):
        actions = []
        faction_board = self.faction_to_faction_board(faction)

        for card in faction_board.crafted_cards:
            if card.name == CardName.COBBLER and len(
                    self.generate_actions_select_src_clearing(faction, None, False)) != 0:
                actions.append(
                    Action('Use {} card'.format(card.name),
                           perform(self.cobbler_agent, card, faction)))

        return actions

    def cobbler(self, card, faction, continuation_func):
        faction_board = self.faction_to_faction_board(faction)
        faction_board.activated_card.append(card)
        self.select_clearing_src_move(faction, continuation_func)

    def cobbler_agent(self, card, faction):
        self.sub_phase = 30001

        faction_board = self.faction_to_faction_board(faction)
        faction_board.activated_card.append(card)

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

    def favor_card(self, faction, suit):
        for clearing in self.board.areas:
            if clearing.suit == suit:
                if faction == Faction.MARQUISE:
                    while True:
                        try:
                            clearing.remove_building(Building.ROOST)
                        except ValueError:
                            break
                        self.eyrie.roost_tracker -= 1
                        self.gain_vp(faction, 1)
                    num_warriors_removed = clearing.warrior_count[Warrior.EYRIE]
                    clearing.remove_warrior(Warrior.EYRIE, num_warriors_removed)
                    self.eyrie.reserved_warriors += num_warriors_removed
                    self.gain_vp(faction, num_warriors_removed)

                elif faction == Faction.EYRIE:
                    while True:
                        try:
                            clearing.remove_building(Building.SAWMILL)
                        except ValueError:
                            break
                        self.marquise.building_trackers[Building.SAWMILL] -= 1
                        self.gain_vp(faction, 1)
                    while True:
                        try:
                            clearing.remove_building(Building.RECRUITER)
                        except ValueError:
                            break
                        self.marquise.building_trackers[Building.RECRUITER] -= 1
                        self.gain_vp(faction, 1)
                    while True:
                        try:
                            clearing.remove_building(Building.WORKSHOP)
                        except ValueError:
                            break
                        self.marquise.building_trackers[Building.WORKSHOP] -= 1
                        self.gain_vp(faction, 1)
                    num_tokens_removed = clearing.token_count[Token.WOOD]
                    num_warriors_removed = clearing.warrior_count[Warrior.MARQUISE]
                    clearing.remove_token(Token.WOOD, num_tokens_removed)
                    clearing.remove_warrior(Warrior.MARQUISE, num_warriors_removed)
                    self.marquise.reserved_warriors += num_warriors_removed
                    self.gain_vp(faction, num_tokens_removed + num_warriors_removed)
