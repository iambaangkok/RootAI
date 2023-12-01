import logging
from enum import StrEnum

import pygame
from pygame import Color, Vector2, Surface

from src.config import Config, Colors
from src.game.FactionBoard import FactionBoard
from src.game.PlayingCard import PlayingCard, PlayingCardPhase
from src.game.Suit import Suit
from src.utils import text_utils

LOGGER = logging.getLogger('logger')


class DecreeAction(StrEnum):
    RECRUIT = "RECRUIT"
    MOVE = "MOVE"
    BATTLE = "BATTLE"
    BUILD = "BUILD"


class EyrieLeader(StrEnum):
    COMMANDER = "COMMANDER"
    DESPOT = "DESPOT"
    BUILDER = "BUILDER"
    CHARISMATIC = "CHARISMATIC"

    def to_number(self) -> int:
        mapping: dict[str, int] = {
            "None": -1,
            "COMMANDER": 0,
            "DESPOT": 1,
            "BUILDER": 2,
            "CHARISMATIC": 3
        }
        return mapping[self.name]


class LeaderStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    USED = "USED"


LOYAL_VIZIER = PlayingCard(0, "Loyal Vizier", Suit.BIRD, PlayingCardPhase.IMMEDIATE)


def count_decree_action_static(decree: {DecreeAction: list[PlayingCard]}, decree_action: DecreeAction | str, suit: Suit | str) -> int:
    return len([x for x in decree[decree_action] if x.suit == suit])


class EyrieBoard(FactionBoard):
    ROOST_REWARD_VP: list[int] = [0, 0, 1, 2, 3, 4, 4, 5]
    ROOST_REWARD_CARD: list[int] = [0, 0, 0, 1, 1, 1, 2, 2]

    def __init__(self, name: str, color: Color, reserved_warriors: int, starting_point: Vector2):
        super().__init__(name, color, reserved_warriors, starting_point)
        self.roost_tracker: int = 0
        self.leaders: {EyrieLeader: LeaderStatus} = {
            EyrieLeader.COMMANDER: LeaderStatus.INACTIVE,
            EyrieLeader.DESPOT: LeaderStatus.INACTIVE,
            EyrieLeader.BUILDER: LeaderStatus.INACTIVE,
            EyrieLeader.CHARISMATIC: LeaderStatus.INACTIVE
        }
        self.decree: {DecreeAction: list[PlayingCard]} = {
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
        arr[8] = self.get_active_leader().to_number()
        arr[9] = [
            [card.card_id for card in self.decree[decree_action]] for decree_action in DecreeAction
        ]

        return arr

    def get_active_leader(self) -> EyrieLeader | str:
        for leader in self.leaders.keys():
            if self.leaders[leader] == LeaderStatus.ACTIVE:
                return leader

        return "None"

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

    def draw(self, screen: Surface):
        super().draw(screen)

        self.draw_roost_tracker(screen, self.starting_point + Vector2(5, 45 * 6 + 25 + self.text_surface.get_height() + 20))
        self.draw_decree(screen, self.starting_point + Vector2(5, 45 * 7 + 10 + self.text_surface.get_height() + 20))
        self.draw_leader(screen, self.starting_point + Vector2(5, 45 * 8 + 10 + self.text_surface.get_height() + 20))

    def draw_roost_tracker(self, screen: Surface, starting_point: Vector2):

        # Text
        title_text = Config.FONT_SM_BOLD.render("roost", True, Colors.BLUE)
        shift: Vector2 = Vector2(10)

        screen.blit(title_text, starting_point + shift)

        img_size: Vector2 = Vector2(40)

        alpha = 200
        img = pygame.image.load("../assets/images/eyrie/roost.png")
        img = pygame.transform.scale(img, img_size)
        img.set_alpha(alpha)
        alpha = 64
        img_dimmed = img.copy()
        img_dimmed.set_alpha(alpha)

        gap = 5
        offset_x = 75

        for j in range(7):
            if j < self.roost_tracker:
                draw_img = img_dimmed
            else:
                draw_img = img
            screen.blit(draw_img,
                        (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))
            if EyrieBoard.ROOST_REWARD_VP[j] > 0:
                reward_vp = Config.FONT_SM_BOLD.render("+" + str(EyrieBoard.ROOST_REWARD_VP[j]), True, (206, 215, 132))
                reward_vp = text_utils.add_outline(reward_vp, 2, Colors.GREY_DARK_2)

                screen.blit(reward_vp, (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))

            if EyrieBoard.ROOST_REWARD_CARD[j] > 0:
                reward_card = Config.FONT_SM_BOLD.render("+" + str(EyrieBoard.ROOST_REWARD_CARD[j]), True, (206, 215, 132))
                reward_card = text_utils.add_outline(reward_card, 2, Colors.BLUE)

                screen.blit(reward_card, (starting_point.x + (img_size.x + gap) * j + gap + offset_x,
                                          starting_point.y + img_size.y - Config.FONT_SM_BOLD.get_height()))

    def draw_leader(self, screen: Surface, starting_point: Vector2):
        shift = Vector2(FactionBoard.dimension.x * 0.05, - FactionBoard.dimension.y * 0.04)
        text = Config.FONT_1.render("{}".format("leader"), True, Colors.BLUE)
        screen.blit(text, starting_point + shift)
        shift = Vector2(FactionBoard.dimension.x * 0.05, 0)
        text = Config.FONT_1.render("{}".format(self.get_active_leader()), True, Colors.BLUE)
        screen.blit(text, starting_point + shift)

    def draw_decree(self, screen: Surface, starting_point: Vector2):

        # DecreeAction
        width = FactionBoard.dimension.x / len(self.decree) - FactionBoard.dimension.x * 0.08
        offset_x = FactionBoard.dimension.x * 0.3
        offset_y = Config.FONT_1.get_height()

        for index, decree_action in enumerate(self.decree.keys()):
            title_text = Config.FONT_1.render(decree_action, True, Colors.BLUE)
            shift: Vector2 = Vector2(index * width + offset_x, offset_y)

            screen.blit(title_text, starting_point + shift)

        for i, suit in enumerate(Suit):
            # draw_key_multi_value(screen, Config.FONT_1, starting_point,
            #                         Vector2(shift.x, index * offset_y ), width, Colors.BLUE, "Bird", self.decree[decree_action])
            color = Colors.BIRD
            if suit == Suit.FOX:
                color = Colors.FOX
            elif suit == Suit.MOUSE:
                color = Colors.MOUSE
            elif suit == Suit.RABBIT:
                color = Colors.RABBIT

            for j, decree_action in enumerate(self.decree.keys()):
                title_text = Config.FONT_1.render(str(self.count_decree_action_with_suit(decree_action, suit)), True, color)
                shift: Vector2 = Vector2(j * width + offset_x, (i + 2) * offset_y)

                screen.blit(title_text, starting_point + shift)
