import math
import sys

import pygame
from pygame import Rect, Color, Surface

from src.config import Config, Colors
from src.game.AreaLogic import AreaLogic, Area
from src.game.Faction import Faction
from src.game.Item import Item
from src.game.Suit import Suit
from src.utils.geometry_utils import get_path_points

import yaml

from src.utils.utils import faction_to_warrior

config_path: str = str(sys.argv[1])
config = yaml.safe_load(open(config_path))

FACTION_NAMES = ['Marquise de Cat', 'The Decree', 'Woodland Alliance', 'Vagabond']
FACTION_ALIAS = {
    Faction.MARQUISE: 'MC',
    Faction.EYRIE: 'EY'
}
FACTION_COLORS = {
    Faction.MARQUISE: Colors.ORANGE,
    Faction.EYRIE: Colors.BLUE
}
FACTION_SIZE = 4
ITEM_SUPPLY_RENDER = [
    [Item.BAG, Item.BOOTS, Item.CROSSBOW, Item.KNIFE, Item.KEG, Item.COIN],
    [Item.BAG, Item.BOOTS, Item.HAMMER, Item.KNIFE, Item.KEG, Item.COIN]
]
ITEM_SUPPLY_INDEX = {
    Item.BAG: [0, 6],
    Item.BOOTS: [1, 7],
    Item.CROSSBOW: [2],
    Item.KNIFE: [3, 9],
    Item.KEG: [4, 10],
    Item.COIN: [5, 11],
    Item.HAMMER: [8]
}


def add_tuple(a, b):
    return tuple(map(lambda i, j: i + j, a, b))


class BoardLogic:

    def __init__(self, area_logics: list[AreaLogic]):
        self.areas: list[AreaLogic] = area_logics
        self.paths: list[tuple[int, int]] = []
        self.faction_points = {
            Faction.MARQUISE: 0,
            Faction.EYRIE: 0
        }
        self.item_supply_available: list[bool] = [True, True, True, True, True, True, True, True, True, True, True,
                                                  True]
        self.turn_player: Faction | None = None
        self.turn_count: int = 0

    def get_state_as_num_array(self) -> list[list]:
        n_features = 3
        arr: list = [[]] * n_features

        arr[0] = [self.faction_points[Faction.MARQUISE], self.faction_points[Faction.EYRIE]]
        arr[1] = [area.get_state_as_num_array() for area in self.areas]
        arr[2] = [(1 if item_available else 0) for item_available in self.item_supply_available]

        return arr

    def set_state_from_num_array(self,
                                 arr: list):
        self.set_state_from_num_arrays(arr[0], arr[1], arr[2])

    def set_state_from_num_arrays(self,
                                  faction_points: list[int] = None,
                                  areas: list = None,
                                  item_supply_available: list[int] = None):
        self.faction_points = {
            Faction.MARQUISE: faction_points[0],
            Faction.EYRIE: faction_points[1]
        }

        for i in range(len(areas)):
            self.areas[i].set_state_from_num_array(areas[i])

        self.item_supply_available = [item_available == 1 for item_available in item_supply_available]

    def get_area(self, area_index: int) -> AreaLogic | None:
        for area in self.areas:
            if area.area_index == area_index:
                return area
        return None

    def add_path(self, area_1: int, area_2: int):
        if ((area_1, area_2) in self.paths) or \
                (self.areas[area_2] in self.areas[area_1].connected_clearings) or \
                (self.areas[area_1] in self.areas[area_2].connected_clearings):
            return

        self.paths.append((area_1, area_2))
        self.areas[area_1].connected_clearings.append(self.areas[area_2])
        self.areas[area_2].connected_clearings.append(self.areas[area_1])

    def get_min_warrior_areas(self) -> list[AreaLogic]:
        min_warrior = math.inf
        for area in self.areas:
            sum_warrior = area.sum_all_warriors()
            if min_warrior > sum_warrior:
                min_warrior = sum_warrior

        return [area for area in self.areas if area.sum_all_warriors() == min_warrior]

    def item_available(self, item: Item) -> bool:
        for item_index in ITEM_SUPPLY_INDEX[item]:
            if self.item_supply_available[item_index]:
                return True
        return False

    def remove_item_from_board(self, item: Item):
        for item_index in ITEM_SUPPLY_INDEX[item]:
            if self.item_supply_available[item_index]:
                self.item_supply_available[item_index] = False
                break

    def gain_vp(self, faction: Faction, vp: int):
        self.faction_points[faction] += vp

    def lose_vp(self, faction: Faction, vp: int):
        self.faction_points[faction] -= vp

    def count_ruling_clearing_by_faction_and_suit(self, faction: Faction, suit: Suit) -> int:
        warrior = faction_to_warrior(faction)

        return len([area for area in self.areas if area.ruler() == warrior and area.suit == suit])


class Board:
    dimension: float = 800
    rect: Rect = Rect(
        ((Config.NATIVE_SCREEN_WIDTH - dimension) / 2, (Config.NATIVE_SCREEN_HEIGHT - dimension) / 2 - 50),
        (dimension, dimension))

    def __init__(self, board_logic: BoardLogic, areas: list[Area]):
        self.name: str = "Forest"
        self.color: Color = Colors.GREEN
        self.logic: BoardLogic = board_logic
        self.areas: list[Area] = areas

    def draw(self, screen: Surface):
        pygame.draw.rect(screen, self.color, self.rect, width=1)

        self.draw_paths_clearing(screen)
        self.draw_areas(screen)
        self.draw_board_info(screen)

    def draw_areas(self, screen: Surface):
        for area in self.areas:
            area.draw(screen)

    def draw_paths_clearing(self, screen: Surface):
        for path in self.logic.paths:
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
        starting_point = ((Config.NATIVE_SCREEN_WIDTH - self.dimension) / 2, (Config.NATIVE_SCREEN_HEIGHT - 130))

        size = (self.dimension, 130)
        block_one_third = (size[0] / 3, size[1] / 3)
        block_full = (size[0] / 3, size[1])

        self.draw_victory_point_tracker(screen, starting_point, block_one_third)
        self.draw_turn_tracker(screen, add_tuple(starting_point, (size[0] / 3, 0)), block_one_third)
        self.draw_item_supply(screen, add_tuple(starting_point, (size[0] / 3 * 2, 0)), block_full)

        pass

    def draw_victory_point_tracker(self, screen, starting_point, size):
        # Box
        box = Rect(starting_point, size)
        pygame.draw.rect(screen, self.color, box, width=1)

        # Text
        points_text = Config.FONT_LG_BOLD.render("VPs", True, Colors.WHITE)
        shift = (10, size[1] / 2 - points_text.get_height() / 2)

        screen.blit(points_text, add_tuple(starting_point, shift))

        faction_pos_ind = 0
        for (faction, vp) in self.logic.faction_points.items():
            rendered_text = Config.FONT_LG_BOLD.render("{}".format(vp), True, FACTION_COLORS[faction])
            pos = (starting_point[0] + faction_pos_ind * 45 + points_text.get_width() + 20, starting_point[1])
            screen.blit(rendered_text, add_tuple(pos, shift))
            faction_pos_ind += 1

        pass

    def draw_turn_tracker(self, screen, starting_point, size):

        # Box
        box = Rect(starting_point, size)
        pygame.draw.rect(screen, self.color, box, width=1)

        turn_text = Config.FONT_MD_BOLD.render("Turn {}:".format(self.logic.turn_count), True, Colors.WHITE)
        shift = (10, size[1] / 2 - turn_text.get_height() / 2)

        screen.blit(turn_text, add_tuple(starting_point, shift))

        player_turn_text = Config.FONT_MD_BOLD.render("{}'s turn".format(FACTION_ALIAS[self.logic.turn_player]), True,
                                                      FACTION_COLORS[self.logic.turn_player])
        pos = (starting_point[0] + turn_text.get_width() + 10, starting_point[1])
        screen.blit(player_turn_text, add_tuple(pos, shift))

        pass

    def draw_item_supply(self, screen, starting_point, size):

        # Box
        box = Rect(starting_point, size)
        pygame.draw.rect(screen, self.color, box, width=1)

        item_supply_text = Config.FONT_MD_BOLD.render("Item Supply", True, Colors.WHITE)
        shift = (10, 10)

        screen.blit(item_supply_text, add_tuple(starting_point, shift))

        img_size = (40, 40)
        img_pos = add_tuple(starting_point, (10, item_supply_text.get_height() + 10))

        for i in range(len(self.logic.item_supply_available)):
            row = i // 6
            col = i % 6

            item_image = pygame.image.load("./assets/images/{}.png".format(ITEM_SUPPLY_RENDER[row][col]))
            item_image = pygame.transform.scale(item_image, img_size)

            if self.logic.item_supply_available[i]:
                screen.blit(item_image,
                            (img_pos[0] + img_size[0] * col, img_pos[1] + img_size[0] * row))
            else:
                alpha = 128
                item_image.set_alpha(alpha)
                screen.blit(item_image,
                            (img_pos[0] + img_size[0] * col, img_pos[1] + img_size[0] * row))
