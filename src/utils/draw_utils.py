from pygame import Surface, Vector2

from src.config import Config, Colors
from src.utils import text_utils


def draw_key_value(screen: Surface, starting_point: Vector2, key: str, value: int):
    title_text = Config.FONT_SM_BOLD.render("{}: {}".format(key, value), True, Colors.ORANGE)
    shift: Vector2 = Vector2(10, 10)
    screen.blit(title_text, starting_point + shift)


def draw_cards(screen: Surface, starting_point: Vector2, text: str, cards: list[int]):
    # Text
    title_text = Config.FONT_SM_BOLD.render(text, True, Colors.ORANGE)
    shift: Vector2 = Vector2(10, 10)

    screen.blit(title_text, starting_point + shift)

    block_size: Vector2 = Vector2(20, 20)

    ind = 0

    for key in cards:
        row = ind // 8
        col = ind % 8

        card_ind = Config.FONT_SM_BOLD.render('{0:02d}'.format(key), True, (206, 215, 132))
        card_ind = text_utils.add_outline_to_image(card_ind, 2, Colors.GREY_DARK_2)
        screen.blit(card_ind, (starting_point.x + (block_size.x + 10) * col + 10 + 150, starting_point.y + (block_size.x + 5) * row))
        ind = ind + 1
