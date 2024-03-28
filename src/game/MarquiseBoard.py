import pygame
from pygame import Color, Vector2, Surface

from src.config import Config, Colors
from src.game.Building import Building
from src.game.Card import Card
from src.game.FactionBoardLogic import FactionBoardLogic, FactionBoard
from src.utils import text_utils

BUILDING_TRACKER_NAME = [Building.SAWMILL, Building.WORKSHOP, Building.RECRUITER]


class MarquiseBoardLogic(FactionBoardLogic):

    def __init__(self, reserved_warriors: int):
        super().__init__(reserved_warriors)

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

    def get_state_as_num_array(self):
        prev_arr = super().get_state_as_num_array()

        n_features: int = 1
        arr: list = prev_arr + [[]] * n_features

        arr[7] = [self.building_trackers[building] for building in
                  [Building.SAWMILL, Building.WORKSHOP, Building.RECRUITER]]

        return arr

    def set_state_from_num_array(self,
                                 arr: list = None,
                                 cards: list[Card] = None):
        super().set_state_from_num_array(arr, cards)
        self.__set_state_from_num_arrays(arr[7])

    def __set_state_from_num_arrays(self,
                                    building_trackers: list[int] = None):
        for i, building in enumerate(self.building_trackers):
            self.building_trackers[building] = building_trackers[i]

    def get_reward(self, building):
        return self.building_reward[building][self.building_trackers[building]]

    def get_reward_card(self):
        return self.building_reward_card[Building.RECRUITER][min(self.building_trackers[Building.RECRUITER], 5)]

    def build_action_update(self, building):
        cost = self.building_cost[self.building_trackers[building]]
        self.building_trackers[building] = self.building_trackers[building] + 1
        return cost


class MarquiseBoard(FactionBoard):

    def __init__(self, marquise_board_logic: MarquiseBoardLogic,
                 name: str, color: Color, starting_point: Vector2):
        super().__init__(marquise_board_logic, name, color, starting_point)
        self.logic = marquise_board_logic

    def draw(self, screen: Surface):
        super().draw(screen)

        for i in range(3):
            self.draw_tracker(screen, BUILDING_TRACKER_NAME[i],
                              self.starting_point + Vector2(5, 45 * (i + 6) + 25 + self.text_surface.get_height() + 20))

    def draw_tracker(self, screen: Surface, title: Building, starting_point: Vector2):

        # Text
        title_text = Config.FONT_SM_BOLD.render(str(title), True, Colors.ORANGE)
        shift: Vector2 = Vector2(10, 10)

        screen.blit(title_text, starting_point + shift)

        img_size: Vector2 = Vector2(40, 40)

        alpha = 200
        img = pygame.image.load("./assets/images/marquise/{}.png".format(title))
        img = pygame.transform.scale(img, img_size)
        img.set_alpha(alpha)
        alpha = 64
        new_img = img.copy()
        new_img.set_alpha(alpha)

        gap = 10
        offset_x = 100

        for j in range(6):
            if j < self.logic.building_trackers[title]:
                draw_img = new_img
            else:
                draw_img = img
            screen.blit(draw_img,
                        (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))

            if self.logic.building_reward[title][j] > 0:
                reward = Config.FONT_SM_BOLD.render("+" + str(self.logic.building_reward[title][j]), True,
                                                    (206, 215, 132))
                reward = text_utils.add_outline(reward, 2, Colors.GREY_DARK_2)

                screen.blit(reward, (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))

            if self.logic.building_reward_card[title][j] > 0:
                reward = Config.FONT_SM_BOLD.render("+" + str(self.logic.building_reward_card[title][j]), True,
                                                    (206, 215, 132))
                reward = text_utils.add_outline(reward, 2, Colors.BLUE)

                screen.blit(reward, (starting_point.x + (img_size.x + gap) * j + gap + offset_x,
                                     starting_point.y + img_size.y - Config.FONT_SM_BOLD.get_height()))
