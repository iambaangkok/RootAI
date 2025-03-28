from __future__ import annotations

import logging
from enum import StrEnum

import pygame
from pygame import Color, Vector2, Surface

from config import Config, Colors
from game.FactionBoardLogic import FactionBoardLogic, FactionBoard
from game.Card import Card, CardPhase
from utils.utils import get_card
from game.Suit import Suit
from utils import text_utils

LOGGER = logging.getLogger('logger')


class DecreeAction(StrEnum):
    RECRUIT = "RECRUIT"
    MOVE = "MOVE"
    BATTLE = "BATTLE"
    BUILD = "BUILD"


eyrie_leader_mapping: dict[str, int] = {
    "COMMANDER": 0,
    "DESPOT": 1,
    "BUILDER": 2,
    "CHARISMATIC": 3
}

eyrie_leader_mapping_reversed = [key for key in eyrie_leader_mapping]


class EyrieLeader(StrEnum):
    COMMANDER = "COMMANDER"
    DESPOT = "DESPOT"
    BUILDER = "BUILDER"
    CHARISMATIC = "CHARISMATIC"

    def to_number(self) -> int:
        return eyrie_leader_mapping[self.name]

    def to_eyrie_leader(leader_id: int) -> EyrieLeader:
        return EyrieLeader[eyrie_leader_mapping_reversed[leader_id]]


leader_status_mapping: dict[str, int] = {
    "ACTIVE": 0,
    "INACTIVE": 1,
    "USED": 2,
}

leader_status_mapping_reversed = [key for key in leader_status_mapping]


class LeaderStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    USED = "USED"

    def to_number(self) -> int:
        return leader_status_mapping[self.name]

    def to_leader_status(status_id: int) -> LeaderStatus:
        return LeaderStatus[leader_status_mapping_reversed[status_id]]


LOYAL_VIZIER = Card(0, "Loyal Vizier", Suit.BIRD, CardPhase.IMMEDIATE)


def count_decree_action_static(decree: {DecreeAction: list[Card]}, decree_action: DecreeAction | str,
                               suit: Suit | str) -> int:
    return len([x for x in decree[decree_action] if x.suit == suit])


class EyrieBoardLogic(FactionBoardLogic):
    ROOST_REWARD_VP: list[int] = [0, 0, 1, 2, 3, 4, 4, 5]
    ROOST_REWARD_CARD: list[int] = [0, 0, 0, 1, 1, 1, 2, 2]

    def __init__(self, reserved_warriors: int):
        super().__init__(reserved_warriors)
        self.roost_tracker: int = 0
        self.leaders: {EyrieLeader: LeaderStatus} = {
            EyrieLeader.COMMANDER: LeaderStatus.INACTIVE,
            EyrieLeader.DESPOT: LeaderStatus.INACTIVE,
            EyrieLeader.BUILDER: LeaderStatus.INACTIVE,
            EyrieLeader.CHARISMATIC: LeaderStatus.INACTIVE
        }
        self.decree: {DecreeAction: list[Card]} = {
            DecreeAction.RECRUIT: [],
            DecreeAction.MOVE: [],
            DecreeAction.BATTLE: [],
            DecreeAction.BUILD: []
        }

    def get_state_as_num_array(self):
        prev_arr = super().get_state_as_num_array()

        n_features: int = 3
        arr: list = prev_arr + [[]] * n_features

        arr[7] = self.roost_tracker
        arr[8] = [
            self.leaders[leader].to_number() for leader in self.leaders
        ]
        arr[9] = [
            [card.card_id for card in self.decree[decree_action]] for decree_action in self.decree
        ]

        return arr

    def set_state_from_num_array(self,
                                 arr: list = None,
                                 cards: list[Card] = None):
        super().set_state_from_num_array(arr, cards)
        self.__set_state_from_num_arrays(arr[7], arr[8], arr[9], cards)

    def __set_state_from_num_arrays(self,
                                    roost_tracker: list[int] = None,
                                    leader_statuses: list[int] = None,
                                    decree: list = None,
                                    cards: list[Card] = None):

        self.roost_tracker = roost_tracker

        self.a_new_generation()
        for i, leader in enumerate(self.leaders):
            self.leaders[leader] = LeaderStatus.to_leader_status(leader_statuses[i])

        self.decree = {
            DecreeAction.RECRUIT: [get_card(i, cards) for i in decree[0]],
            DecreeAction.MOVE: [get_card(i, cards) for i in decree[1]],
            DecreeAction.BATTLE: [get_card(i, cards) for i in decree[2]],
            DecreeAction.BUILD: [get_card(i, cards) for i in decree[3]]
        }

    def set_crafting_piece_count(self,
                                 crafting_pieces_count: {Suit: int}):
        self.crafting_pieces_count = crafting_pieces_count

    def get_active_leader(self) -> EyrieLeader | None:
        for leader in self.leaders.keys():
            if self.leaders[leader] == LeaderStatus.ACTIVE:
                return leader

        return None

    def get_inactive_leader(self) -> list[EyrieLeader]:
        inactive_leaders: list[EyrieLeader] = []
        for leader in self.leaders.keys():
            if self.leaders[leader] == LeaderStatus.INACTIVE:
                inactive_leaders.append(leader)
        return inactive_leaders

    def deactivate_current_leader(self):
        self.leaders[self.get_active_leader()] = LeaderStatus.USED

    def a_new_generation(self):
        for leader in self.leaders.keys():
            self.leaders[leader] = LeaderStatus.INACTIVE

    def reset_decree(self):
        self.decree = {
            DecreeAction.RECRUIT: [],
            DecreeAction.MOVE: [],
            DecreeAction.BATTLE: [],
            DecreeAction.BUILD: []
        }

    def activate_leader(self, leader: EyrieLeader) -> bool:
        if self.leaders[leader] == LeaderStatus.USED:
            LOGGER.warning("{} is already {}".format(leader, LeaderStatus.USED))
            return False

        self.leaders[leader] = LeaderStatus.ACTIVE
        if leader == EyrieLeader.COMMANDER:
            self.decree[DecreeAction.MOVE].append(LOYAL_VIZIER)
            self.decree[DecreeAction.BATTLE].append(LOYAL_VIZIER)
        elif leader == EyrieLeader.DESPOT:
            self.decree[DecreeAction.MOVE].append(LOYAL_VIZIER)
            self.decree[DecreeAction.BUILD].append(LOYAL_VIZIER)
        elif leader == EyrieLeader.BUILDER:
            self.decree[DecreeAction.RECRUIT].append(LOYAL_VIZIER)
            self.decree[DecreeAction.MOVE].append(LOYAL_VIZIER)
        elif leader == EyrieLeader.CHARISMATIC:
            self.decree[DecreeAction.RECRUIT].append(LOYAL_VIZIER)
            self.decree[DecreeAction.BATTLE].append(LOYAL_VIZIER)

        return True

    def count_card_in_decree_with_suit(self, suit: Suit | str) -> int:
        return sum([self.count_decree_action_with_suit(decree_action, suit) for decree_action in DecreeAction])

    def count_decree_action_with_suit(self, decree_action: DecreeAction | str, suit: Suit | str) -> int:
        return count_decree_action_static(self.decree, decree_action, suit)


class EyrieBoard(FactionBoard):

    def __init__(self, eyrie_board_logic: EyrieBoardLogic,
                 name: str, color: Color, starting_point: Vector2):
        super().__init__(eyrie_board_logic, name, color, starting_point)
        self.logic = eyrie_board_logic

    def draw(self, screen: Surface):
        super().draw(screen)

        self.draw_roost_tracker(screen,
                                self.starting_point + Vector2(5, 45 * 6 + 25 + self.text_surface.get_height() + 20))
        self.draw_decree(screen, self.starting_point + Vector2(5, 45 * 7 + 10 + self.text_surface.get_height() + 20))
        self.draw_leader(screen, self.starting_point + Vector2(5, 45 * 8 + 10 + self.text_surface.get_height() + 20))

    def draw_roost_tracker(self, screen: Surface, starting_point: Vector2):

        # Text
        title_text = Config.FONT_SM_BOLD.render("roost", True, Colors.BLUE)
        shift: Vector2 = Vector2(10)

        screen.blit(title_text, starting_point + shift)

        img_size: Vector2 = Vector2(40)

        alpha = 200
        img = pygame.image.load("./assets/images/eyrie/roost.png")
        img = pygame.transform.scale(img, img_size)
        img.set_alpha(alpha)
        alpha = 64
        img_dimmed = img.copy()
        img_dimmed.set_alpha(alpha)

        gap = 5
        offset_x = 75

        for j in range(7):
            if j < self.logic.roost_tracker:
                draw_img = img_dimmed
            else:
                draw_img = img
            screen.blit(draw_img,
                        (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))
            if EyrieBoardLogic.ROOST_REWARD_VP[j] > 0:
                reward_vp = Config.FONT_SM_BOLD.render("+" + str(EyrieBoardLogic.ROOST_REWARD_VP[j]), True,
                                                       (206, 215, 132))
                reward_vp = text_utils.add_outline(reward_vp, 2, Colors.GREY_DARK_2)

                screen.blit(reward_vp, (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))

            if EyrieBoardLogic.ROOST_REWARD_CARD[j] > 0:
                reward_card = Config.FONT_SM_BOLD.render("+" + str(EyrieBoardLogic.ROOST_REWARD_CARD[j]), True,
                                                         (206, 215, 132))
                reward_card = text_utils.add_outline(reward_card, 2, Colors.BLUE)

                screen.blit(reward_card, (starting_point.x + (img_size.x + gap) * j + gap + offset_x,
                                          starting_point.y + img_size.y - Config.FONT_SM_BOLD.get_height()))

    def draw_leader(self, screen: Surface, starting_point: Vector2):
        shift = Vector2(FactionBoardLogic.dimension.x * 0.05, - FactionBoardLogic.dimension.y * 0.04)
        text = Config.FONT_1.render("{}".format("leader"), True, Colors.BLUE)
        screen.blit(text, starting_point + shift)
        shift = Vector2(FactionBoardLogic.dimension.x * 0.05, 0)
        text = Config.FONT_1.render("{}".format(self.logic.get_active_leader()), True, Colors.BLUE)
        screen.blit(text, starting_point + shift)

    def draw_decree(self, screen: Surface, starting_point: Vector2):

        # DecreeAction
        width = FactionBoardLogic.dimension.x / len(self.logic.decree) - FactionBoardLogic.dimension.x * 0.08
        offset_x = FactionBoardLogic.dimension.x * 0.3
        offset_y = Config.FONT_1.get_height()

        for index, decree_action in enumerate(self.logic.decree.keys()):
            title_text = Config.FONT_1.render(decree_action, True, Colors.BLUE)
            shift: Vector2 = Vector2(index * width + offset_x, offset_y)

            screen.blit(title_text, starting_point + shift)

        for i, suit in enumerate(Suit):
            color = Colors.BIRD
            if suit == Suit.FOX:
                color = Colors.FOX
            elif suit == Suit.MOUSE:
                color = Colors.MOUSE
            elif suit == Suit.RABBIT:
                color = Colors.RABBIT

            for j, decree_action in enumerate(self.logic.decree.keys()):
                title_text = Config.FONT_1.render(str(self.logic.count_decree_action_with_suit(decree_action, suit)),
                                                  True, color)
                shift: Vector2 = Vector2(j * width + offset_x, (i + 2) * offset_y)

                screen.blit(title_text, starting_point + shift)
