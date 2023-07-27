from pygame import Surface, Vector2, Color, Rect
from pygame.font import Font

from src.config import Config, Colors
from src.game.PlayingCard import PlayingCard
from src.utils import text_utils


def draw_key_value(screen: Surface, font: Font, starting_point: Vector2, shift: Vector2, color: Color, key: str, value: any):
    text = font.render("{}: {}".format(key, value), True, color)
    screen.blit(text, starting_point + shift)


def draw_key_multi_value(screen: Surface, font: Font, starting_point: Vector2, shift: Vector2, gap: int, color: Color, key: str, values: [str]):
    key_text = font.render("{}:".format(key), True, color)
    screen.blit(key_text, starting_point + shift)

    for index, value in enumerate(values):
        value_text = font.render("{}".format(value), True, color)
        screen.blit(value_text, starting_point + shift + index * gap)


def draw_cards(screen: Surface, starting_point: Vector2, color: Color, text: str, cards: list[PlayingCard]):
    # Text
    title_text = Config.FONT_SM_BOLD.render(text, True, color)
    shift: Vector2 = Vector2(10, 10)

    screen.blit(title_text, starting_point + shift)

    block_size: Vector2 = Vector2(20, 20)

    ind = 0

    for key in cards:
        row = ind // 8
        col = ind % 8

        card_ind = Config.FONT_SM_BOLD.render('{0:02d}'.format(key.card_id), True, (206, 215, 132))
        card_ind = text_utils.add_outline(card_ind, 2, Colors.GREY_DARK_2)
        screen.blit(card_ind, (starting_point.x + (block_size.x + 10) * col + 10 + 150, starting_point.y + (block_size.x + 5) * row))
        ind = ind + 1


# This one has text-wrapping
def draw_text_in_rect(surface: Surface, text: str, color: Color, rect: Rect, font: Font, aa: bool = False, bkg: Color | None = None) -> str:
    rect = Rect(rect)
    y = rect.top
    line_spacing = -2

    # get the height of the font
    font_height = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + font_height > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += font_height + line_spacing

        # remove the text we just blitted
        text = text[i:]

    return text
