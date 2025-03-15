import sys

import pygame.font
import yaml
from pygame.font import Font

config_path: str = ""
if len(sys.argv) > 1:
    config_path = str(sys.argv[1])
if config_path == "":
    config_path = "./config/config.yml"
config = yaml.safe_load(open(config_path))

SCREEN_WIDTH = config['screen']['width']
SCREEN_HEIGHT = config['screen']['height']
NATIVE_SCREEN_WIDTH = config['screen']['native-width']  # 1680
NATIVE_SCREEN_HEIGHT = config['screen']['native-height']  # 960

RENDER_ENABLE: bool = config['simulation']['rendering']['enable'] \
                      and not config['simulation']['command-line-mode']['enable']

GAME_RENDER_ENABLE: bool = config['game']['rendering']['enable'] \
                           and not config['simulation']['command-line-mode']['enable']

ACTIONS_RENDER_ENABLE: bool = config['simulation']['actions']['rendering']['enable'] \
                              and not config['simulation']['command-line-mode']['enable']

AUTO_NEXT_ROUND: bool = config['simulation']['auto-next-round'] \
                        or config['simulation']['command-line-mode']['enable']

AGENT_REQUIRE_KEY_HOLD: bool = config['agent']['require-key-hold'] \
                               and not config['simulation']['command-line-mode']['enable']

pygame.font.init()
FONT_1 = Font("./assets/fonts/UbuntuMono-Regular.ttf", 16)
FONT_SM = Font("./assets/fonts/UbuntuMono-Regular.ttf", 20)
FONT_SM_BOLD = Font("./assets/fonts/UbuntuMono-Bold.ttf", 20)
FONT_MD = Font("./assets/fonts/UbuntuMono-Regular.ttf", 28)
FONT_MD_BOLD = Font("./assets/fonts/UbuntuMono-Bold.ttf", 28)
FONT_LG = Font("./assets/fonts/UbuntuMono-Regular.ttf", 32)
FONT_LG_BOLD = Font("./assets/fonts/UbuntuMono-Bold.ttf", 32)
FONT_XL = Font("./assets/fonts/UbuntuMono-Regular.ttf", 40)
FONT_XL_BOLD = Font("./assets/fonts/UbuntuMono-Bold.ttf", 40)
