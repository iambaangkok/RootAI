import math

import pygame
from pygame import Color, Vector2, Surface, Rect

from src.config import Config, Colors
from src.game.Building import Building
from src.game.Faction import Faction
from src.game.Suit import Suit
from src.game.Token import Token
from src.game.Warrior import Warrior


class Area:
    area_count: int = 0
    size_ratio: float = 0.07

    def __init__(self, position: Vector2, radius: float, suit: Suit, buildings: list[Building]):
        self.position: Vector2 = position
        self.radius: float = radius
        self.suit: Suit = suit
        self.buildings: list[Building] = buildings

        self.color: Color = Colors.WHITE

        self.connected_clearings: list = []
        self.connected_forests: list = []

        self.area_index: int = Area.area_count
        Area.area_count += 1

        self.token_count = {}
        for token in Token:
            self.token_count[token] = 0

        self.warrior_count = {}
        for warrior in Warrior:
            self.warrior_count[warrior] = 0

    def __del__(self):
        Area.area_count -= 1

    def draw(self, screen: Surface):
        # circle
        pygame.draw.circle(screen, self.color, self.position, self.radius, width=1)

        # buildings
        self.draw_buildings(screen)

        # suit
        self.draw_suit(screen)

        # ruler
        self.draw_ruler(screen)

        # warriors
        self.draw_warriors(screen)

        # tokens
        self.draw_tokens(screen)

        # text: area_index
        margin_top = 4
        text = str(self.area_index)

        surface = Config.FONT_1.render(text, True, Colors.WHITE)
        surface_rect = surface.get_rect()
        surface_rect.centerx = self.position.x
        surface_rect.top = self.position.y + self.radius + margin_top
        screen.blit(surface, surface_rect)

    def draw_buildings(self, screen: Surface):
        size_ratio: float = 0.3
        gap_size_ratio: float = 0.1
        y_offset_ratio: float = 0.5

        dimension = size_ratio * self.radius
        gap = gap_size_ratio * self.radius

        count = len(self.buildings)
        starting_offset: Vector2 = Vector2(
            -1 * (count * dimension + max((count - 1), 0) * gap) / 2,
            -1 * y_offset_ratio * self.radius
        )

        for i, building in enumerate(self.buildings):
            rect = Rect(0, 0, dimension, dimension)
            rect.topleft = self.position + starting_offset + Vector2(i * dimension + i * gap, 0)

            color = Colors.WHITE
            width = 1
            text = ""
            if building is Building.EMPTY:
                color = Colors.WHITE
            elif building is Building.RUIN:
                color = Colors.GREY
                width = 0
            elif building in [Building.SAWMILL, Building.WORKSHOP, Building.RECRUITER]:
                color = Colors.ORANGE
                if building is Building.SAWMILL:
                    text = "S"
                elif building is Building.WORKSHOP:
                    text = "W"
                elif building is Building.RECRUITER:
                    text = "R"
            elif building is Building.ROOST:
                color = Colors.BLUE
                text = "R"
            elif building is Building.BASE:
                color = Colors.GREEN
                text = "B"

            pygame.draw.rect(screen, color, rect, width)

            # text
            surface = Config.FONT_1.render(text, True, color)
            surface_rect = surface.get_rect()
            surface_rect.center = rect.center

            screen.blit(surface, surface_rect)

    def draw_suit(self, screen):
        size_ratio: float = 0.15

        radius = size_ratio * self.radius
        color = Colors.WHITE
        width = 0
        text = ""

        offset: Vector2 = Vector2(self.radius - radius)
        position = self.position + offset

        if self.suit is Suit.MOUSE:
            color = Colors.MOUSE
            text = "M"
        elif self.suit is Suit.RABBIT:
            color = Colors.RABBIT
            text = "R"
        if self.suit is Suit.FOX:
            color = Colors.FOX
            text = "F"

        pygame.draw.circle(screen, color, position, radius, width)

        # text
        surface = Config.FONT_1.render(text, True, Colors.BLACK)
        surface_rect = surface.get_rect()
        surface_rect.center = position

        screen.blit(surface, surface_rect)

    def draw_ruler(self, screen):
        size_ratio: float = 0.15

        radius = size_ratio * self.radius
        color = Colors.WHITE
        width = 0
        text = ""

        offset: Vector2 = Vector2(self.radius - radius, -1 * (self.radius - radius))
        position = self.position + offset

        ruler = self.ruler()
        if ruler is Warrior.MARQUISE:
            color = Colors.ORANGE
            text = "M"
        elif ruler is Warrior.EYRIE:
            color = Colors.BLUE
            text = "E"

        pygame.draw.circle(screen, color, position, radius, width)

        # text
        surface = Config.FONT_1.render(text, True, color)
        surface_rect = surface.get_rect()
        surface_rect.center = position

        screen.blit(surface, surface_rect)

    def draw_warriors(self, screen):
        gap_size_ratio: float = 0.5
        y_offset_ratio: float = 0.5

        gap = gap_size_ratio * self.radius

        count = 2
        starting_offset: Vector2 = Vector2(
            -1 * ((count - 1) * gap) / 2,
            y_offset_ratio * self.radius
        )

        # text Marquis
        if self.warrior_count[Warrior.MARQUISE] > 0:
            color = Colors.ORANGE
            text = str(self.warrior_count[Warrior.MARQUISE])

            surface = Config.FONT_SM.render(text, True, color)
            surface_rect = surface.get_rect()
            surface_rect.center = Rect(self.position + starting_offset + (Vector2(gap * 0, 0)), (0, 0)).center

            screen.blit(surface, surface_rect)

        # text Eyrie
        if self.warrior_count[Warrior.EYRIE] > 0:
            color = Colors.BLUE
            text = str(self.warrior_count[Warrior.EYRIE])

            surface = Config.FONT_SM.render(text, True, color)
            surface_rect = surface.get_rect()
            surface_rect.center = Rect(self.position + starting_offset + (Vector2(gap * 1, 0)), (0, 0)).center

            screen.blit(surface, surface_rect)

    def draw_tokens(self, screen):
        size_ratio: float = 0.2
        offset_ratio: float = 0.8

        radius = size_ratio * self.radius

        # Wood
        if self.token_count[Token.WOOD] > 0:
            rad = math.radians(45)
            offset = Vector2(math.cos(rad) * offset_ratio * self.radius,
                             -1 * math.sin(rad) * offset_ratio * self.radius)
            position = self.position + offset

            color = Colors.ORANGE
            width = 1
            text = "w" + str(self.token_count[Token.WOOD])
            pygame.draw.circle(screen, color, position, radius, width)
            # text
            surface = Config.FONT_1.render(text, True, Colors.ORANGE)
            surface_rect = surface.get_rect()
            surface_rect.center = position

            screen.blit(surface, surface_rect)
        # Castle
        if self.token_count[Token.CASTLE] > 0:
            rad = math.radians(10)
            offset = Vector2(math.cos(rad) * offset_ratio * self.radius,
                             -1 * math.sin(rad) * offset_ratio * self.radius)
            position = self.position + offset

            color = Colors.ORANGE
            width = 1
            text = "C"
            pygame.draw.circle(screen, color, position, radius, width)
            # text
            surface = Config.FONT_1.render(text, True, Colors.ORANGE)
            surface_rect = surface.get_rect()
            surface_rect.center = position

            screen.blit(surface, surface_rect)

    def ruler(self) -> str | Warrior:
        # only for MARQUIS vs DECREE
        marquise_presence = self.warrior_count[Warrior.MARQUISE] \
                            + self.buildings.count(Building.SAWMILL) \
                            + self.buildings.count(Building.RECRUITER) \
                            + self.buildings.count(Building.WORKSHOP)

        eyrie_presence = self.warrior_count[Warrior.EYRIE] \
                         + self.buildings.count(Building.ROOST)

        if marquise_presence == 0 and eyrie_presence == 0:
            return "None"
        if marquise_presence > eyrie_presence:
            return Warrior.MARQUISE
        else:
            return Warrior.EYRIE

    def add_warrior(self, warrior_type: Warrior, amount: int = 1):
        self.warrior_count[warrior_type] += amount

    def remove_warrior(self, warrior_type: Warrior, amount: int = 1):
        """
        Removes `amount` warrior of `warrior_type` from this clearing.
        If `amount` is more than warriors present, remove all.

        :param amount: amount of warriors to be removed
        :param warrior_type: type of warriors to be removed
        :return: numbers of removed warrior
        """
        pre_removed_warrior_count: int = self.warrior_count[warrior_type]
        self.warrior_count[warrior_type] = max(0, self.warrior_count[warrior_type] - amount)
        return pre_removed_warrior_count - self.warrior_count[warrior_type]

    def add_token(self, token_type: Token, amount: int = 1):
        self.token_count[token_type] += amount

    def remove_token(self, token_type: Token, amount: int = 1):
        self.token_count[token_type] = max(0, self.token_count[token_type] - amount)

    def add_building(self, building: Building):
        self.buildings.append(building)

    def remove_building(self, building):
        self.buildings.remove(building)

    def sum_all_pieces(self) -> int:
        sum_of_pieces = 0

        for token in self.token_count.keys():
            sum_of_pieces += self.token_count[token]
        sum_of_pieces += self.sum_all_warriors()
        sum_of_pieces += len(self.buildings) - self.buildings.count(Building.EMPTY)

        return sum_of_pieces

    def sum_all_warriors(self) -> int:
        return sum([self.warrior_count[warrior] for warrior in self.warrior_count.keys()])

    def get_warrior_count(self, warrior: Warrior) -> int:
        return self.warrior_count[warrior]

    def get_tokens_count(self, tokens: list[Token]) -> int:
        return sum([self.token_count[token] for token in tokens])

    def get_buildings_count(self, buildings: list[Building]) -> int:
        return sum([self.buildings.count(building) for building in buildings])

    def __str__(self):
        return str(self.area_index)
