import pygame
from pygame import Color, Vector2, Surface, Rect

from src.config import Config, Colors
from src.game.Building import Building
from src.game.FactionBoard import FactionBoard
from src.game.Suit import Suit
from src.utils import text_utils

BUILDING_TRACKER_NAME = [Building.SAWMILL, Building.WORKSHOP, Building.RECRUITER]


class MarquiseBoard(FactionBoard):
    def __init__(self, name: str, color: Color, reserved_warriors: int, starting_point: Vector2):
        super().__init__(name, color, reserved_warriors, starting_point)

        self.building_trackers: {Building, int} = {
            Building.SAWMILL: 1,
            Building.WORKSHOP: 1,
            Building.RECRUITER: 1
        }

        self.building_cost = [0, 1, 2, 3, 3, 4]
        self.building_reward = {
            Building.SAWMILL: [0, 1, 2, 3, 4, 5],
            Building.WORKSHOP: [0, 2, 2, 3, 4, 5],
            Building.RECRUITER: [0, 1, 2, 3, 3, 4]
        }

        self.building_reward_card = {
            Building.SAWMILL: [0, 0, 0, 0, 0, 0],
            Building.WORKSHOP: [0, 0, 0, 0, 0, 0],
            Building.RECRUITER: [0, 0, 1, 1, 2, 2]
        }

    def get_reward(self, building):
        return self.building_reward[building][self.building_trackers[building]]

    def get_reward_card(self):
        return self.building_reward_card[Building.RECRUITER][min(self.building_trackers[Building.RECRUITER], 5)]

    def build_action_update(self, building):
        cost = self.building_cost[self.building_trackers[building]]
        self.building_trackers[building] = self.building_trackers[building] + 1
        return cost

    def draw(self, screen: Surface):
        super().draw(screen)

        for i in range(3):
            self.draw_tracker(screen, BUILDING_TRACKER_NAME[i],
                              self.starting_point + Vector2(5, 45 * (i + 6) + 25 + self.text_surface.get_height() + 20))

        # self.marquise_action.draw(screen)

    def draw_tracker(self, screen: Surface, title: Building, starting_point: Vector2):

        # Text
        title_text = Config.FONT_SM_BOLD.render(str(title), True, Colors.ORANGE)
        shift: Vector2 = Vector2(10, 10)

        screen.blit(title_text, starting_point + shift)

        img_size: Vector2 = Vector2(40, 40)

        alpha = 200
        img = pygame.image.load("../assets/images/marquise/{}.png".format(title))
        img = pygame.transform.scale(img, img_size)
        img.set_alpha(alpha)
        alpha = 64
        new_img = img.copy()
        new_img.set_alpha(alpha)

        gap = 10
        offset_x = 100

        for j in range(6):
            if j < self.building_trackers[title]:
                draw_img = new_img
            else:
                draw_img = img
            screen.blit(draw_img,
                        (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))

            if self.building_reward[title][j] > 0:
                reward = Config.FONT_SM_BOLD.render("+" + str(self.building_reward[title][j]), True, (206, 215, 132))
                reward = text_utils.add_outline(reward, 2, Colors.GREY_DARK_2)

                screen.blit(reward, (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))

            if self.building_reward_card[title][j] > 0:
                reward = Config.FONT_SM_BOLD.render("+" + str(self.building_reward_card[title][j]), True,
                                                    (206, 215, 132))
                reward = text_utils.add_outline(reward, 2, Colors.BLUE)

                screen.blit(reward, (starting_point.x + (img_size.x + gap) * j + gap + offset_x,
                                     starting_point.y + img_size.y - Config.FONT_SM_BOLD.get_height()))
