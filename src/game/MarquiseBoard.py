import pygame
from pygame import Rect, Color, Surface

from src.config import Config, Colors
from src.utils import text

BUILDING_TRACKER = {
    "sawmill": 2,
    "workshop": 5,
    "recruiter": 3
}

BUILDING_COST = [0, 1, 2, 3, 3, 4]
BUILDING_REWARD = {
    "sawmill": [0, 1, 2, 3, 4, 5],
    "workshop": [0, 2, 2, 3, 4, 5],
    "recruiter": [0, 1, 2, 3, 3, 4]
}

BUILDING_DRAW_REWARD = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 1, 0],
]
BUILDING_TRACKER_NAME = ["sawmill", "workshop", "recruiter"]


def add_tuple(a, b):
    return tuple(map(lambda i, j: i + j, a, b))


class MarquiseBoard:
    dimension: float = 400
    starting_point = (20, 30)
    rect: Rect = Rect(starting_point,
                      (dimension, dimension))

    def __init__(self):
        self.name: str = "Forest"
        self.color: Color = Colors.ORANGE

    def draw(self, screen: Surface):
        pygame.draw.rect(screen, self.color, MarquiseBoard.rect, width=3)

        # Text
        points_text = Config.FONT_MD_BOLD.render("Marquise", True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(points_text, add_tuple(self.starting_point, shift))

        for i in range(3):
            self.draw_tracker(screen, BUILDING_TRACKER_NAME[i], add_tuple(self.starting_point, (10, 20 + 110 * i + points_text.get_height())),
                              (380, 100))

        self.draw_crafted_items()
        self.draw_crafted_cards()

    def draw_tracker(self, screen, title, starting_point, size):
        # Box
        box = Rect(starting_point, size)
        pygame.draw.rect(screen, self.color, box, width=1)

        # Text
        points_text = Config.FONT_SM_BOLD.render(title, True, Colors.ORANGE)
        shift = (10, 10)

        screen.blit(points_text, add_tuple(starting_point, shift))

        img_size = (50, 50)

        alpha = 200
        img = pygame.image.load("../assets/images/marquise/{}.png".format(title))
        img = pygame.transform.scale(img, img_size)
        img.set_alpha(alpha)

        for j in range(6):
            if j < BUILDING_TRACKER[title]:
                alpha = 128
                new_img = img.copy()
                new_img.set_alpha(alpha)
                screen.blit(new_img,
                            (starting_point[0] + (img_size[0] + 10) * j + 10, starting_point[1] + 20 + points_text.get_height()))
            else:
                screen.blit(img,
                            (starting_point[0] + (img_size[0] + 10) * j + 10, starting_point[1] + 20 + points_text.get_height()))

            reward = Config.FONT_SM_BOLD.render("+" + str(BUILDING_REWARD[title][j]), True, (206, 215, 132))
            reward = text.add_outline_to_image(reward, 2, Colors.GREY_DARK_2)

            screen.blit(reward, (starting_point[0] + (img_size[0] + 10) * j + 10, starting_point[1] + 20 + points_text.get_height()))

    def draw_crafted_items(self):
        pass

    def draw_crafted_cards(self):
        pass
