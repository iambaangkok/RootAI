import pygame
from pygame import Rect, Color, Surface, Vector2

from src.config import Config, Colors
from src.game.Building import Building
from src.game.Item import Item
from src.utils import text_utils
from src.utils.draw_utils import draw_key_value, draw_cards

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


class MarquiseBoard:

    dimension = (0, 0)

    BUILDING_TRACKER = {
        Building.SAWMILL: 2,
        Building.WORKSHOP: 5,
        Building.RECRUITER: 3
    }

    def __init__(self, name: str, color: Color, reserved_warriors: int, starting_point: Vector2):
        self.name: str = name
        self.color: Color = color
        self.items: {Item: int} = {
            Item.KEG: 5,
            Item.BAG: 7,
            Item.KNIFE: 4,
            Item.BOOTS: 3,
            Item.HAMMER: 2,
            Item.CROSSBOW: 1,
            Item.COIN: 0,
            Item.TORCH: 3,
        }
        # = {}
        self.crafted_cards: list[int] = [1, 55, 32, 2, 4, 15, 25, 35, 45, 99, 66, 22, 3, 5, 5, 2]
        # = []
        self.cards_in_hand: list[int] = [1, 55, 32, 2, 4, 15, 25, 35, 45, 99, 66, 22, 3, 5, 5, 2]
        # = []

        self.reserved_warriors: int = reserved_warriors
        self.starting_point: Vector2 = starting_point

    def draw(self, screen: Surface):
        self.dimension = (screen.get_width() * 0.25, screen.get_height() * 0.5)
        pygame.draw.rect(screen, self.color, Rect(self.starting_point,
                                                  (screen.get_width() * 0.25, screen.get_height() * 0.5)), width=3)

        # Text
        points_text = Config.FONT_MD_BOLD.render("Marquise de Cat", True, Colors.ORANGE)
        shift: Vector2 = Vector2(10, 10)

        screen.blit(points_text, self.starting_point + shift)

        self.draw_crafted_items(screen, self.starting_point + Vector2(5, 45 * 0 + points_text.get_height() + 20))

        self.draw_crafted_cards(screen, self.starting_point + Vector2(5, 45 * 2 + points_text.get_height() + 20))
        self.draw_crafted_cards_count(screen, self.starting_point + Vector2(5, 45 * 3 + points_text.get_height() + 20))

        self.draw_cards_in_hand(screen, self.starting_point + Vector2(5, 45 * 4 + points_text.get_height() + 20))
        self.draw_cards_in_hand_count(screen, self.starting_point + Vector2(5, 45 * 5 + points_text.get_height() + 20))

        self.draw_reserved_warriors(screen, self.starting_point + Vector2(5, 45 * 5 + 25 + points_text.get_height() + 20))

        for i in range(3):
            self.draw_tracker(screen, BUILDING_TRACKER_NAME[i], self.starting_point + Vector2(5, 45 * (i+6) + 25 + points_text.get_height() + 20))

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
        alpha = 128
        new_img = img.copy()
        new_img.set_alpha(alpha)

        for j in range(6):
            if j < self.BUILDING_TRACKER[title]:
                draw_img = new_img
            else:
                draw_img = img
            screen.blit(draw_img,
                        (starting_point.x + (img_size.x + 10) * j + 10 + 100, starting_point.y))

            reward = Config.FONT_SM_BOLD.render("+" + str(BUILDING_REWARD[title][j]), True, (206, 215, 132))
            reward = text_utils.add_outline_to_image(reward, 2, Colors.GREY_DARK_2)

            screen.blit(reward, (starting_point.x + (img_size.x + 10) * j + 10 + 100, starting_point.y))

    def draw_crafted_items(self, screen: Surface, starting_point: Vector2):

        # Text
        title_text = Config.FONT_SM_BOLD.render("Crafted Items", True, Colors.ORANGE)
        shift: Vector2 = Vector2(10, 10)

        screen.blit(title_text, starting_point + shift)

        img_size: Vector2 = Vector2(40, 40)

        ind = 0
        for key in self.items:
            value = self.items[key]
            row = ind // 5
            col = ind % 5

            img = pygame.image.load("../assets/images/{}.png".format(key))
            img = pygame.transform.scale(img, img_size)

            screen.blit(img,
                        (starting_point.x + (img_size.x + 10) * col + 10 + 150, starting_point.y + (img_size.x + 5) * row))

            quantity = Config.FONT_SM_BOLD.render("x{}".format(value), True, (206, 215, 132))
            quantity = text_utils.add_outline_to_image(quantity, 2, Colors.GREY_DARK_2)
            screen.blit(quantity, (starting_point.x + (img_size.x + 10) * col + 10 + 150, starting_point.y + (img_size.x + 5) * row))
            ind = ind + 1

    def draw_crafted_cards(self, screen: Surface, starting_point: Vector2):
        draw_cards(screen, starting_point, "Crafted Cards:", self.crafted_cards)

    def draw_crafted_cards_count(self, screen: Surface, starting_point):
        draw_key_value(screen, starting_point, "Crafted Cards Count", len(self.crafted_cards))

    def draw_cards_in_hand(self, screen: Surface, starting_point: Vector2):
        draw_cards(screen, starting_point, "Cards In-Hand:", self.cards_in_hand)

    def draw_cards_in_hand_count(self, screen: Surface, starting_point):
        draw_key_value(screen, starting_point, "Cards In-Hand Count", len(self.cards_in_hand))

    def draw_reserved_warriors(self, screen: Surface, starting_point: Vector2):
        title_text = Config.FONT_SM_BOLD.render("Reserved Warriors: {}".format(self.reserved_warriors), True, Colors.ORANGE)
        shift: Vector2 = Vector2(10, 10)
        screen.blit(title_text, starting_point + shift)

        pass



