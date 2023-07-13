from enum import StrEnum

import pygame
from pygame import Color, Vector2, Surface

from src.config import Config, Colors
from src.game.FactionBoard import FactionBoard
from src.utils import text_utils

ROOST_REWARD_VP = [0, 1, 2, 3, 4, 4, 5]
ROOST_REWARD_CARD = [0, 0, 1, 1, 1, 2, 2]


class DecreeAction(StrEnum):
    RECRUIT = "recruit"
    MOVE = "move"
    BATTLE = "battle"
    BUILD = "build"


class EyrieLeader(StrEnum):
    COMMANDER = "commander"
    DESPOT = "despot"
    BUILDER = "builder"
    CHARISMATIC = "charismatic"


class LeaderStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    USED = "used"


class EyrieBoard(FactionBoard):
    def __init__(self, name: str, color: Color, reserved_warriors: int, starting_point: Vector2):
        super().__init__(name, color, reserved_warriors, starting_point)
        self.roost_tracker: int = 1
        self.leaders: {EyrieLeader: LeaderStatus} = {
            EyrieLeader.COMMANDER: LeaderStatus.INACTIVE,
            EyrieLeader.DESPOT: LeaderStatus.INACTIVE,
            EyrieLeader.BUILDER: LeaderStatus.INACTIVE,
            EyrieLeader.CHARISMATIC: LeaderStatus.ACTIVE
        }
        self.decree: {DecreeAction: [int]} = {
            DecreeAction.RECRUIT: [],
            DecreeAction.MOVE: [],
            DecreeAction.BATTLE: [],
            DecreeAction.BUILD: []
        }

    def draw(self, screen: Surface):
        super().draw(screen)

        self.draw_roost_tracker(screen, self.starting_point + Vector2(5, 45 * 6 + 25 + self.text_surface.get_height() + 20))

    def draw_roost_tracker(self, screen: Surface, starting_point: Vector2):

        # Text
        title_text = Config.FONT_SM_BOLD.render("roost", True, Colors.BLUE)
        shift: Vector2 = Vector2(10)

        screen.blit(title_text, starting_point + shift)

        img_size: Vector2 = Vector2(40)

        alpha = 200
        img = pygame.image.load("../assets/images/marquise/sawmill.png")
        img = pygame.transform.scale(img, img_size)
        img.set_alpha(alpha)
        alpha = 128
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
            if ROOST_REWARD_VP[j] > 0:
                reward_vp = Config.FONT_SM_BOLD.render("+" + str(ROOST_REWARD_VP[j]), True, (206, 215, 132))
                reward_vp = text_utils.add_outline_to_image(reward_vp, 2, Colors.GREY_DARK_2)

                screen.blit(reward_vp, (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))

            if ROOST_REWARD_CARD[j] > 0:
                reward_card = Config.FONT_SM_BOLD.render("+" + str(ROOST_REWARD_CARD[j]), True, (206, 215, 132))
                reward_card = text_utils.add_outline_to_image(reward_card, 2, Colors.BLUE)

                screen.blit(reward_card, (starting_point.x + (img_size.x + gap) * j + gap + offset_x,
                                          starting_point.y + img_size.y - Config.FONT_SM_BOLD.get_height()))
