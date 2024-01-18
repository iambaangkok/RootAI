import pygame
from pygame import Rect, Color, Surface, Vector2

from src.config import Config, Colors
from src.utils.utils import get_card
from src.game.Item import Item
from src.game.Card import Card
from src.game.Suit import Suit
from src.utils import text_utils
from src.utils.draw_utils import draw_key_value, draw_cards


class FactionBoardLogic:
    dimension = Vector2(Config.SCREEN_WIDTH * 0.25, Config.SCREEN_HEIGHT * 0.5)

    def __init__(self, reserved_warriors: int):
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
        self.crafted_cards: list[Card] = []
        self.cards_in_hand: list[Card] = []
        self.activated_card: list[Card] = []
        self.dominance_card: Card | None = None

        self.crafting_pieces_count = {
            Suit.FOX: 0,
            Suit.RABBIT: 0,
            Suit.MOUSE: 0
        }

        self.reserved_warriors: int = reserved_warriors

    def get_state_as_num_array(self):
        n_features: int = 7
        arr: list = [[]] * n_features

        arr[0] = [self.items[item] for item in Item]
        arr[1] = [card.card_id for card in self.cards_in_hand]
        arr[2] = [card.card_id for card in self.crafted_cards]
        arr[3] = [card.card_id for card in self.activated_card]
        arr[4] = [-1 if self.dominance_card is None else self.dominance_card.card_id]
        arr[5] = [self.crafting_pieces_count[suit] for suit in [Suit.FOX, Suit.RABBIT, Suit.MOUSE]]
        arr[6] = self.reserved_warriors

        return arr

    def set_state_from_num_array(self,
                                 arr: list = None,
                                 cards: list[Card] = None):
        self.set_state_from_num_arrays(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], arr[6], cards)

    def set_state_from_num_arrays(self,
                                  item_count: list[int] = None,
                                  cards_in_hand_ids: list[int] = None,
                                  crafted_cards_ids: list[int] = None,
                                  activated_card_ids: list[int] = None,
                                  dominance_card_id: int = -1,
                                  crafting_pieces_count: list[int] = None,
                                  reserved_warriors: int = 0,
                                  cards: list[Card] = None):

        for i, item in enumerate(self.items):
            self.items[item] = item_count[i]

        self.cards_in_hand = [get_card(i, cards) for i in cards_in_hand_ids]
        self.crafted_cards = [get_card(i, cards) for i in crafted_cards_ids]
        self.activated_card = [get_card(i, cards) for i in activated_card_ids]
        self.dominance_card = get_card(dominance_card_id, cards)

        for i, suit in enumerate(self.crafting_pieces_count):
            self.crafting_pieces_count[suit] = crafting_pieces_count[i]

        self.reserved_warriors = reserved_warriors

    def clear_activated_cards(self):
        self.activated_card = []

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


class FactionBoard:
    def __init__(self, faction_board_logic: FactionBoardLogic,
                 name: str, color: Color, starting_point: Vector2):
        self.logic = faction_board_logic
        self.name: str = name
        self.color: Color = color
        self.starting_point: Vector2 = starting_point

        self.text_surface: Surface = Config.FONT_MD_BOLD.render(name, True, color)

    def draw(self, screen: Surface):
        pygame.draw.rect(screen, self.color, Rect(self.starting_point,
                                                  (FactionBoardLogic.dimension.x, FactionBoardLogic.dimension.y)), width=3)

        # Text
        shift: Vector2 = Vector2(10, 10)

        screen.blit(self.text_surface, self.starting_point + shift)

        self.draw_crafted_items(screen, self.starting_point + Vector2(5, 45 * 0 + self.text_surface.get_height() + 20))

        self.draw_crafted_cards(screen, self.starting_point + Vector2(5, 45 * 2 + self.text_surface.get_height() + 20))
        self.draw_crafted_cards_count(screen, self.starting_point + Vector2(5, 45 * 3 + self.text_surface.get_height() + 20))

        self.draw_cards_in_hand(screen, self.starting_point + Vector2(5, 45 * 4 + self.text_surface.get_height() + 20))
        self.draw_cards_in_hand_count(screen, self.starting_point + Vector2(5, 45 * 5 + self.text_surface.get_height() + 20))

        self.draw_reserved_warriors(screen, self.starting_point + Vector2(5, 45 * 5 + 25 + self.text_surface.get_height() + 20))

        self.draw_dominance_card(screen)

    def draw_dominance_card(self, screen):
        size_ratio: float = 0.03

        radius = size_ratio * Config.SCREEN_WIDTH / 4
        color = Colors.WHITE
        width = 1
        text = ""

        offset: Vector2 = Vector2(-radius - 2, radius + 2)
        position: Vector2 = Vector2(self.starting_point.x + Config.SCREEN_WIDTH / 4, self.starting_point.y) + offset

        if self.logic.dominance_card is not None:
            if self.logic.dominance_card.suit is Suit.MOUSE:
                color = Colors.MOUSE
                text = "M"
            elif self.logic.dominance_card.suit is Suit.RABBIT:
                color = Colors.RABBIT
                text = "R"
            elif self.logic.dominance_card.suit is Suit.FOX:
                color = Colors.FOX
                text = "F"
            elif self.logic.dominance_card.suit is Suit.BIRD:
                color = Colors.BIRD
                text = "B"

        pygame.draw.circle(screen, color, position, radius, width)

        # text
        surface = Config.FONT_1.render(text, True, color)
        surface_rect = surface.get_rect()
        surface_rect.center = position

        screen.blit(surface, surface_rect)

    def draw_crafted_items(self, screen: Surface, starting_point: Vector2):
        # Text
        title_text = Config.FONT_SM_BOLD.render("Crafted Items", True, self.color)
        shift: Vector2 = Vector2(10, 10)

        screen.blit(title_text, starting_point + shift)

        img_size: Vector2 = Vector2(40, 40)

        ind = 0
        for key in self.logic.items:
            value = self.logic.items[key]
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
        draw_cards(screen, starting_point, self.color, "Crafted Cards:", self.logic.crafted_cards)

    def draw_crafted_cards_count(self, screen: Surface, starting_point):
        draw_key_value(screen, Config.FONT_SM_BOLD, starting_point, Vector2(10, 10), self.color, "Crafted Cards Count", len(self.logic.crafted_cards))

    def draw_cards_in_hand(self, screen: Surface, starting_point: Vector2):
        draw_cards(screen, starting_point, self.color, "Cards In-Hand:", self.logic.cards_in_hand)

    def draw_cards_in_hand_count(self, screen: Surface, starting_point):
        draw_key_value(screen, Config.FONT_SM_BOLD, starting_point, Vector2(10, 10), self.color, "Cards In-Hand Count", len(self.logic.cards_in_hand))

    def draw_reserved_warriors(self, screen: Surface, starting_point: Vector2):
        title_text = Config.FONT_SM_BOLD.render("Reserved Warriors: {}".format(self.logic.reserved_warriors), True, self.color)
        shift: Vector2 = Vector2(10, 10)
        screen.blit(title_text, starting_point + shift)

        pass
