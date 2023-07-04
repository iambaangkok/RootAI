import pygame
from pygame import Rect, Color, Surface

from src.config import Config, Colors
from src.game.Building import Building
from src.game.Item import Item
from src.utils import text

BUILDING_TRACKER = {
    Building.SAWMILL: 2,
    Building.WORKSHOP: 5,
    Building.RECRUITER: 3
}

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

    def __init__(self):
        self.items = None
        self.name: str = "Marquise"
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
            self.draw_tracker(screen, BUILDING_TRACKER_NAME[i], add_tuple(self.starting_point, (5, 50 * i + points_text.get_height() + 20))
                              )

        self.draw_crafted_items(screen, add_tuple(self.starting_point, (5, 50 * 3 + points_text.get_height() + 20)))
        self.draw_crafted_cards(screen, add_tuple(self.starting_point, (5, 50 * 4 + points_text.get_height() + 20)))
        self.draw_warriors_reserve(screen, add_tuple(self.starting_point, (5, 50 * 4 + 25 + points_text.get_height() + 20)))
        self.draw_cards_in_hand(screen, add_tuple(self.starting_point, (5, 50 * 5 + points_text.get_height() + 20)))

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
        alpha = 128
        new_img = img.copy()
        new_img.set_alpha(alpha)

        for j in range(6):
            if j < BUILDING_TRACKER[title]:
                draw_img = new_img
            else:
                draw_img = img
            screen.blit(draw_img,
                        (starting_point[0] + (img_size[0] + 10) * j + 10 + 100, starting_point[1]))

            reward = Config.FONT_SM_BOLD.render("+" + str(BUILDING_REWARD[title][j]), True, (206, 215, 132))
            reward = text.add_outline_to_image(reward, 2, Colors.GREY_DARK_2)

            screen.blit(reward, (starting_point[0] + (img_size[0] + 10) * j + 10 + 100, starting_point[1]))

    def draw_crafted_items(self, screen, starting_point):

        self.items = [Item.KEG, Item.KNIFE]

        # Text
        title_text = Config.FONT_SM_BOLD.render("Crafted Items", True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(title_text, add_tuple(starting_point, shift))

        img_size = (40, 40)

        ind = 0
        for j in self.items:
            img = pygame.image.load("../assets/images/{}.png".format(j))
            img = pygame.transform.scale(img, img_size)

            screen.blit(img,
                        (starting_point[0] + (img_size[0] + 10) * ind + 10 + 150, starting_point[1]))
            ind = ind + 1

    def draw_crafted_cards(self, screen, starting_point):

        self.card_list = [1,55,32,2]
        # Text
        title_text = Config.FONT_SM_BOLD.render("Crafted Cards: {}".format(self.card_list), True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(title_text, add_tuple(starting_point, shift))
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
