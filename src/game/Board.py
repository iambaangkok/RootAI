import pygame
from pygame import Rect, Color, Surface

from src.config import Config, Colors
from src.game.Area import Area
from src.game.Item import Item
from src.utils.geometry import get_path_points

FACTION_NAMES = ['Marquise de Cat', 'The Decree', 'Woodland Alliance', 'Vagabond']
FACTION_ALIAS = ['MC', 'D', 'WA', 'V']
FACTION_COLORS = [Colors.ORANGE, Colors.BLUE, Colors.GREEN, Colors.GREY]
FACTION_SIZE = 4
ITEM_SUPPLY = [['bag', 'boots', 'crossbow', 'knife', 'keg', 'coin'], ['bag', 'boots', 'hammer', 'knife', 'keg', 'coin']]

ITEM = [[Item.BAG, Item.BOOTS, Item.CROSSBOW, Item.KNIFE, Item.KEG, Item.COIN], ['bag', 'boots', 'hammer', 'knife', 'keg', 'coin']]


def add_tuple(a, b):
    return tuple(map(lambda i, j: i + j, a, b))


class Board:
    dimension: float = 800
    rect: Rect = Rect(((Config.SCREEN_WIDTH - dimension) / 2, (Config.SCREEN_HEIGHT - dimension) / 2 - 50),
                      (dimension, dimension))

    def __init__(self, areas: list[Area]):
        self.name: str = "Forest"
        self.color: Color = Colors.GREEN
        self.areas: list[Area] = areas
        self.paths: list[tuple[int, int]] = []
        self.faction_points: list[int] = [0, 0, 0, 0]

    def add_path(self, area_1: int, area_2: int):
        if ((area_1, area_2) in self.paths) or \
                (self.areas[area_2] in self.areas[area_1].connected_clearings) or \
                (self.areas[area_1] in self.areas[area_2].connected_clearings):
            return

        self.paths.append((area_1, area_2))
        self.areas[area_1].connected_clearings.append(self.areas[area_2])
        self.areas[area_2].connected_clearings.append(self.areas[area_1])

    def draw(self, screen: Surface):
        pygame.draw.rect(screen, self.color, Board.rect, width=1)

        self.draw_paths_clearing(screen)
        self.draw_areas(screen)
        self.draw_board_info(screen)

    def draw_areas(self, screen: Surface):
        for area in self.areas:
            area.draw(screen)

    def draw_paths_clearing(self, screen: Surface):
        for path in self.paths:
            area_a = self.areas[path[0]]
            area_b = self.areas[path[1]]
            additional_shift = 5
            line_width = 5
            pos_a, pos_b = get_path_points(area_a.position, area_b.position, area_a.radius + additional_shift)

            pygame.draw.line(
                screen, Colors.GREY_DARK_2, pos_a, pos_b, line_width
            )
        pass

    def draw_board_info(self, screen):
        starting_point = ((Config.SCREEN_WIDTH - self.dimension) / 2, (Config.SCREEN_HEIGHT - 130))

        size = (self.dimension, 130)
        block_one_third = (size[0] / 3, size[1] / 3)
        block_full = (size[0] / 3, size[1])

        self.draw_victory_point_tracker(screen, starting_point, block_one_third)
        self.draw_turn_tracker(screen, add_tuple(starting_point, (size[0] / 3, 0)), block_one_third)
        self.draw_item_supply(screen, add_tuple(starting_point, (size[0] / 3 * 2, 0)), block_full)

        pass

    def draw_victory_point_tracker(self, screen, starting_point, size):

        self.faction_points = [25, 80, 15, 50]

        # Box
        box = Rect(starting_point, size)
        pygame.draw.rect(screen, self.color, box, width=1)

        # Text
        points_text = Config.FONT_LG_BOLD.render("VPs", True, Colors.WHITE)
        shift = (10, size[1] / 2 - points_text.get_height() / 2)

        screen.blit(points_text, add_tuple(starting_point, shift))

        # 2*2 Grid
        for ind in range(4):
            rendered_text = Config.FONT_LG_BOLD.render("{}".format(self.faction_points[ind]), True, FACTION_COLORS[ind])
            pos = (starting_point[0] + ind * 45 + points_text.get_width() + 20, starting_point[1])
            screen.blit(rendered_text, add_tuple(pos, shift))

        pass
        # 1 * 4 Grid
        # margin_left = 150
        # for ind in range(4):
        #     rendered_text = Config.FONT_LG.render("{}".format(self.faction_points[ind]), True, FACTION_COLORS[ind])
        #     screen.blit(rendered_text,
        #                 (((Config.SCREEN_WIDTH - self.dimension) // 2 + margin_left) + (self.dimension - margin_left) // 4 * ind,
        #                  (Config.SCREEN_HEIGHT - 40) - rendered_text.get_height() // 2 + 10))

        # 4 * 1 Grid
        # for ind in range(4):
        #     rendered_text = Config.FONT_MD.render("\t\tVP: {}".format(self.faction_points[ind]), True, FACTION_COLORS[ind])
        #     screen.blit(rendered_text,
        #                 (((Config.SCREEN_WIDTH - self.dimension) // 2),
        #                  (Config.SCREEN_HEIGHT - 90) - rendered_text.get_height() // 2 + (90//4 + 3) * ind))

    def draw_turn_tracker(self, screen, starting_point, size):

        # Box
        box = Rect(starting_point, size)
        pygame.draw.rect(screen, self.color, box, width=1)

        # Get from Game.py
        turn_faction = 0
        turn_num = 2

        turn_text = Config.FONT_MD_BOLD.render("Turn {}:".format(turn_num), True, Colors.WHITE)
        shift = (10, size[1] / 2 - turn_text.get_height() / 2)

        screen.blit(turn_text, add_tuple(starting_point, shift))

        player_turn_text = Config.FONT_MD_BOLD.render("{}'s turn".format(FACTION_ALIAS[turn_faction]), True, FACTION_COLORS[turn_faction])
        pos = (starting_point[0] + turn_text.get_width() + 10, starting_point[1])
        screen.blit(player_turn_text, add_tuple(pos, shift))

        pass

    def draw_item_supply(self, screen, starting_point, size):

        available = [[True, False, True, True, False, True], [False, False, True, True, True, False]]

        # Box
        box = Rect(starting_point, size)
        pygame.draw.rect(screen, self.color, box, width=1)

        item_supply_text = Config.FONT_MD_BOLD.render("Item Supply", True, Colors.WHITE)
        shift = (10, 10)

        screen.blit(item_supply_text, add_tuple(starting_point, shift))

        img_size = (40, 40)
        img_pos = add_tuple(starting_point, (10, item_supply_text.get_height() + 10))

        for i in range(2):
            for j in range(6):
                item_image = pygame.image.load("../assets/images/{}.png".format(ITEM_SUPPLY[i][j]))
                item_image = pygame.transform.scale(item_image, img_size)
                if available[i][j]:
                    screen.blit(item_image,
                                (img_pos[0] + img_size[0] * j, img_pos[1] + img_size[0] * i))
                else:
                    alpha = 128
                    item_image.set_alpha(alpha)
                    screen.blit(item_image,
                                (img_pos[0] + img_size[0] * j, img_pos[1] + img_size[0] * i))

        pass
