import pygame
from pygame import Rect, Color, Surface, Vector2

from src.config import Config, Colors
from src.game.Building import Building
from src.game.Item import Item
from src.utils import text_utils
from src.utils.draw_utils import draw_key_value, draw_cards


class FactionBoard:
    dimension = (Config.SCREEN_WIDTH * 0.25, Config.SCREEN_HEIGHT * 0.5)

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
        self.crafted_cards: [int] = [1, 55, 32, 2, 4, 15, 25, 35, 45, 99, 66, 22, 3, 5, 5, 2]
        # = []
        self.cards_in_hand: [int] = [1, 55, 32, 2, 4, 15, 25, 35, 45, 99, 66, 22, 3, 5, 5, 2]
        # = []

        self.reserved_warriors: int = reserved_warriors
        self.starting_point: Vector2 = starting_point

        self.text_surface: Surface = Config.FONT_MD_BOLD.render(name, True, color)

    def draw(self, screen: Surface):
        pygame.draw.rect(screen, self.color, Rect(self.starting_point,
                                                  (screen.get_width() * 0.25, screen.get_height() * 0.5)), width=3)

        # Text
        shift: Vector2 = Vector2(10, 10)

        screen.blit(self.text_surface, self.starting_point + shift)

        self.draw_crafted_items(screen, self.starting_point + Vector2(5, 45 * 0 + self.text_surface.get_height() + 20))

        self.draw_crafted_cards(screen, self.starting_point + Vector2(5, 45 * 2 + self.text_surface.get_height() + 20))
        self.draw_crafted_cards_count(screen, self.starting_point + Vector2(5, 45 * 3 + self.text_surface.get_height() + 20))

        self.draw_cards_in_hand(screen, self.starting_point + Vector2(5, 45 * 4 + self.text_surface.get_height() + 20))
        self.draw_cards_in_hand_count(screen, self.starting_point + Vector2(5, 45 * 5 + self.text_surface.get_height() + 20))

        self.draw_reserved_warriors(screen, self.starting_point + Vector2(5, 45 * 5 + 25 + self.text_surface.get_height() + 20))

    def draw_crafted_items(self, screen: Surface, starting_point: Vector2):
        # Text
        title_text = Config.FONT_SM_BOLD.render("Crafted Items", True, self.color)
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
        draw_cards(screen, starting_point, self.color, "Crafted Cards:", self.crafted_cards)

    def draw_crafted_cards_count(self, screen: Surface, starting_point):
        draw_key_value(screen, starting_point, self.color, "Crafted Cards Count", len(self.crafted_cards))

    def draw_cards_in_hand(self, screen: Surface, starting_point: Vector2):
        draw_cards(screen, starting_point, self.color, "Cards In-Hand:", self.cards_in_hand)

    def draw_cards_in_hand_count(self, screen: Surface, starting_point):
        draw_key_value(screen, starting_point, self.color, "Cards In-Hand Count", len(self.cards_in_hand))

    def draw_reserved_warriors(self, screen: Surface, starting_point: Vector2):
        title_text = Config.FONT_SM_BOLD.render("Reserved Warriors: {}".format(self.reserved_warriors), True, self.color)
        shift: Vector2 = Vector2(10, 10)
        screen.blit(title_text, starting_point + shift)

        pass
