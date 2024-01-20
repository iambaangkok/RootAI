import pygame.font
import yaml
from pygame.font import Font

config = yaml.safe_load(open("config/config.yml"))

SCREEN_WIDTH = config['screen']['width']
SCREEN_HEIGHT = config['screen']['height']
NATIVE_SCREEN_WIDTH = config['screen']['native-width']  # 1680
NATIVE_SCREEN_HEIGHT = config['screen']['native-height']  # 960

pygame.font.init()
FONT_1 = Font("../assets/fonts/UbuntuMono-Regular.ttf", 16)
FONT_SM = Font("../assets/fonts/UbuntuMono-Regular.ttf", 20)
FONT_SM_BOLD = Font("../assets/fonts/UbuntuMono-Bold.ttf", 20)
FONT_MD = Font("../assets/fonts/UbuntuMono-Regular.ttf", 28)
FONT_MD_BOLD = Font("../assets/fonts/UbuntuMono-Bold.ttf", 28)
FONT_LG = Font("../assets/fonts/UbuntuMono-Regular.ttf", 32)
FONT_LG_BOLD = Font("../assets/fonts/UbuntuMono-Bold.ttf", 32)
FONT_XL = Font("../assets/fonts/UbuntuMono-Regular.ttf", 40)
FONT_XL_BOLD = Font("../assets/fonts/UbuntuMono-Bold.ttf", 40)
