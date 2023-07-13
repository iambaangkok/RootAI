import pygame
from pygame import Rect, Color, Surface

from src.config import Config, Colors
from src.game.Building import Building
from src.game.Item import Item
from src.utils import text

BUILDING_COST = [0, 1, 2, 3, 3, 4]
BUILDING_REWARD = {
    Building.SAWMILL: [0, 1, 2, 3, 4, 5],
    Building.WORKSHOP: [0, 2, 2, 3, 4, 5],
    Building.RECRUITER: [0, 1, 2, 3, 3, 4]
}

BUILDING_DRAW_REWARD = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 1, 0],
]
BUILDING_TRACKER_NAME = [Building.SAWMILL, Building.WORKSHOP, Building.RECRUITER]


def add_tuple(a, b):
    return tuple(map(lambda i, j: i + j, a, b))


class MarquiseBoard:
    starting_point = (0, 0)
    dimension = (0, 0)

    BUILDING_TRACKER = {
        Building.SAWMILL: 2,
        Building.WORKSHOP: 5,
        Building.RECRUITER: 3
    }

    def __init__(self):
        self.items = None
        self.name: str = "Marquise de Cat"
        self.color: Color = Colors.ORANGE

    def draw(self, screen: Surface):
        self.dimension = (screen.get_width() * 0.25, screen.get_height() * 0.5)
        pygame.draw.rect(screen, self.color, Rect(self.starting_point,
                                                  (screen.get_width() * 0.25, screen.get_height() * 0.5)), width=3)

        # Text
        points_text = Config.FONT_MD_BOLD.render("Marquise de Cat", True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(points_text, add_tuple(self.starting_point, shift))

        for i in range(3):
            self.draw_tracker(screen, BUILDING_TRACKER_NAME[i], add_tuple(self.starting_point, (5, 45 * i + points_text.get_height() + 20))
                              )

        self.draw_crafted_items(screen, add_tuple(self.starting_point, (5, 45 * 3 + points_text.get_height() + 20)))
        self.draw_crafted_cards(screen, add_tuple(self.starting_point, (5, 45 * 5 + points_text.get_height() + 20)))
        self.draw_warriors_reserve(screen, add_tuple(self.starting_point, (5, 45 * 6 + 25 + points_text.get_height() + 20)))
        self.draw_cards_in_hand(screen, add_tuple(self.starting_point, (5, 45 * 6 + 50 + points_text.get_height() + 20)))

    def draw_tracker(self, screen, title, starting_point):

        # Text
        title_text = Config.FONT_SM_BOLD.render(str(title), True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(title_text, add_tuple(starting_point, shift))

        img_size = (40, 40)

        alpha = 200
        img = pygame.image.load("../assets/images/marquise/{}.png".format(title))
        img = pygame.transform.scale(img, img_size)
        img.set_alpha(alpha)
        alpha = 100
        new_img = img.copy()
        new_img.set_alpha(alpha)

        for j in range(6):
            if j < self.BUILDING_TRACKER[title]:
                draw_img = new_img
            else:
                draw_img = img
            screen.blit(draw_img,
                        (starting_point[0] + (img_size[0] + 10) * j + 10 + 100, starting_point[1]))

            reward = text.sm_bold_outline("+" + str(BUILDING_REWARD[title][j]), (206, 215, 132), True)

            screen.blit(reward, (starting_point[0] + (img_size[0] + 10) * j + 10 + 100, starting_point[1]))

    def draw_crafted_items(self, screen, starting_point):

        self.items = {
            Item.KEG: 5,
            Item.BAG: 7,
            Item.KNIFE: 4,
            Item.BOOTS: 3,
            Item.HAMMER: 2,
            Item.CROSSBOW: 1,
            Item.COIN: 0,
            Item.TORCH: 3,
        }

        # Text
        title_text = Config.FONT_SM_BOLD.render("Crafted Items", True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(title_text, add_tuple(starting_point, shift))

        img_size = (40, 40)

        ind = 0
        for key in self.items:
            value = self.items[key]
            row = ind // 5
            col = ind % 5

            img = pygame.image.load("../assets/images/{}.png".format(key))
            img = pygame.transform.scale(img, img_size)

            screen.blit(img,
                        (starting_point[0] + (img_size[0] + 10) * col + 10 + 150, starting_point[1] + (img_size[0] + 5) * row))

            quantity = text.sm_bold_outline("x{}".format(value), Colors.WHITE, True)
            screen.blit(quantity, (starting_point[0] + (img_size[0] + 10) * col + 10 + 150, starting_point[1] + (img_size[0] + 5) * row))
            ind = ind + 1

    def draw_crafted_cards(self, screen, starting_point):

        self.card_list = [1, 55, 32, 2, 4, 15, 25, 35, 45, 99, 66, 22, 3, 5, 5, 2, 54, 8, 9, 58, 48, 2, 82, 98]
        # Text
        title_text = Config.FONT_SM_BOLD.render("Crafted Cards", True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(title_text, add_tuple(starting_point, shift))

        block_size = (20, 20)

        ind = 0

        for key in self.card_list:
            row = ind // 8
            col = ind % 8

            card_ind = text.sm_bold_outline('{0:02d}'.format(key), Colors.WHITE, True)
            screen.blit(card_ind, (starting_point[0] + (block_size[0] + 10) * col + 10 + 150, starting_point[1] + (block_size[0] + 5) * row))
            ind = ind + 1
        pass

    def draw_warriors_reserve(self, screen, starting_point):
        title_text = Config.FONT_SM_BOLD.render("Reserved Warriors: {}".format(69), True, Colors.ORANGE)
        shift = (10, 10)
        screen.blit(title_text, add_tuple(starting_point, shift))

        pass

    def draw_cards_in_hand(self, screen, starting_point):
        title_text = Config.FONT_SM_BOLD.render("Cards in Hand: {}".format(69), True, Colors.ORANGE)
        shift = (10, 10)
        screen.blit(title_text, add_tuple(starting_point, shift))

        pass
