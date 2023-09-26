import pygame
from pygame import Rect, Color, Surface, Vector2

from src.config import Config, Colors
from src.game.Building import Building
from src.game.Item import Item
from src.game.PlayingCard import PlayingCard
from src.game.Suit import Suit
from src.utils import text_utils
from src.utils.draw_utils import draw_key_value, draw_cards


class FactionBoard:
    dimension = Vector2(Config.SCREEN_WIDTH * 0.25, Config.SCREEN_HEIGHT * 0.5)

    def __init__(self, name: str, color: Color, reserved_warriors: int, starting_point: Vector2):
        self.name: str = name
        self.color: Color = color
        self.items: {Item: int} = {
            Item.KEG: 0,
            Item.BAG: 0,
            Item.KNIFE: 0,
            Item.BOOTS: 0,
            Item.HAMMER: 0,
            Item.CROSSBOW: 0,
            Item.COIN: 0,
            Item.TORCH: 0,
        }
        self.crafted_cards: list[PlayingCard] = []
        self.cards_in_hand: list[PlayingCard] = []

        self.crafting_pieces_count = {
            Suit.FOX: 0,
            Suit.RABBIT: 0,
            Suit.MOUSE: 0
        }

        self.reserved_warriors: int = reserved_warriors

        self.victory_point = 0

        self.starting_point: Vector2 = starting_point

        self.text_surface: Surface = Config.FONT_MD_BOLD.render(name, True, color)

    def can_spend_crafting_piece(self, suit: Suit | str, amount: int) -> bool:
        if suit == Suit.BIRD:
            return sum([self.crafting_pieces_count[suit_] for suit_ in self.crafting_pieces_count.keys()]) >= amount
        else:
            return self.crafting_pieces_count[suit] >= amount

    def spend_crafting_piece(self, suit: Suit | str, amount: int):
        if suit == Suit.BIRD:
            # TODO: which suit to spend for ROYAL CLAIM BIRD suit requirement??, this is only a makeshift temporary implementation
            for _suit in self.crafting_pieces_count.keys():
                if amount != 0 and amount <= self.crafting_pieces_count[_suit]:
                    self.crafting_pieces_count[_suit] -= amount
                else:
                    amount -= self.crafting_pieces_count[Suit.FOX]
                    self.crafting_pieces_count[_suit] = 0
        else:
            self.crafting_pieces_count[suit] -= amount


    def draw(self, screen: Surface):
        pygame.draw.rect(screen, self.color, Rect(self.starting_point,
                                                  (FactionBoard.dimension.x, FactionBoard.dimension.y)), width=3)

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
            quantity = text_utils.add_outline(quantity, 2, Colors.GREY_DARK_2)
            screen.blit(quantity, (starting_point.x + (img_size.x + 10) * col + 10 + 150, starting_point.y + (img_size.x + 5) * row))
            ind = ind + 1

    def draw_crafted_cards(self, screen: Surface, starting_point: Vector2):
        draw_cards(screen, starting_point, self.color, "Crafted Cards:", self.crafted_cards)

    def draw_crafted_cards_count(self, screen: Surface, starting_point):
        draw_key_value(screen, Config.FONT_SM_BOLD, starting_point, Vector2(10, 10), self.color, "Crafted Cards Count", len(self.crafted_cards))

    def draw_cards_in_hand(self, screen: Surface, starting_point: Vector2):
        draw_cards(screen, starting_point, self.color, "Cards In-Hand:", self.cards_in_hand)

    def draw_cards_in_hand_count(self, screen: Surface, starting_point):
        draw_key_value(screen, Config.FONT_SM_BOLD, starting_point, Vector2(10, 10), self.color, "Cards In-Hand Count", len(self.cards_in_hand))

    def draw_reserved_warriors(self, screen: Surface, starting_point: Vector2):
        title_text = Config.FONT_SM_BOLD.render("Reserved Warriors: {}".format(self.reserved_warriors), True, self.color)
        shift: Vector2 = Vector2(10, 10)
        screen.blit(title_text, starting_point + shift)

        pass
