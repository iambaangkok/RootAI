import pygame

from src.config import Colors, Config


def sm_bold_outline(plain_text, color, antialias=True, background=None):
    text = Config.FONT_SM_BOLD.render(plain_text, antialias, color, background)
    outlined = add_outline(text, 2, Colors.GREY_DARK_2)
    return outlined


def add_outline(image: pygame.Surface, thickness: int, color: tuple,
                color_key: tuple = (255, 0, 255)) -> pygame.Surface:
    mask = pygame.mask.from_surface(image)
    mask_surf = mask.to_surface(setcolor=color)
    mask_surf.set_colorkey((0, 0, 0))

    new_img = pygame.Surface((image.get_width() + 2, image.get_height() + 2))
    new_img.fill(color_key)
    new_img.set_colorkey(color_key)

    for i in -thickness, thickness:
        new_img.blit(mask_surf, (i + thickness, thickness))
        new_img.blit(mask_surf, (thickness, i + thickness))
    new_img.blit(image, (thickness, thickness))

    return new_img
