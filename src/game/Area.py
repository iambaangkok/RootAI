import math

import pygame
from pygame import Color, Vector2, Surface, Rect

from src.config import Config, Colors
from src.game.Building import Building
from src.game.Suit import Suit
from src.game.Token import Token
from src.game.Warrior import Warrior


class Area:
    area_count: int = 0
    size_ratio: float = 0.07

    def __init__(self, position: Vector2, radius: float, suit: Suit, buildings: [Building]):
        self.position: Vector2 = position
        self.radius: float = radius
        self.suit: Suit = suit
        self.buildings: [Building] = buildings

        self.color: Color = Colors.WHITE

        self.connected_clearings: [] = []
        self.connected_forests: [] = []

        self.area_index: int = Area.area_count
        Area.area_count += 1

        self.token_count = {}
        for token in Token:
            self.token_count[token] = 0
        print(self.token_count)

        self.warrior_count = {}
        for warrior in Warrior:
            self.warrior_count[warrior] = 0
        print(self.warrior_count)

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
        if ruler is Warrior.MARQUIS:
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
            -1 * ((count-1) * gap) / 2,
            y_offset_ratio * self.radius
        )

        # text Marquis
        color = Colors.ORANGE
        text = str(self.warrior_count[Warrior.MARQUIS])

        surface = Config.FONT_SM.render(text, True, color)
        surface_rect = surface.get_rect()
        surface_rect.center = Rect(self.position + starting_offset + (Vector2(gap * 0, 0)), (0, 0)).center

        screen.blit(surface, surface_rect)

        # text Eyrie
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
            offset = Vector2(math.cos(rad) * offset_ratio * self.radius, -1 * math.sin(rad) * offset_ratio * self.radius)
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
            offset = Vector2(math.cos(rad) * offset_ratio * self.radius, -1 * math.sin(rad) * offset_ratio * self.radius)
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
        if self.warrior_count[Warrior.MARQUIS] == 0 and self.warrior_count[Warrior.EYRIE] == 0:
            return "None"
        if self.warrior_count[Warrior.MARQUIS] > self.warrior_count[Warrior.EYRIE]:
            return Warrior.MARQUIS
        else:
            return Warrior.EYRIE

    def add_warrior(self, warrior_type: Warrior, amount: int = 1):
        self.warrior_count[warrior_type] += amount

    def remove_warrior(self, warrior_type: Warrior, amount: int = 1):
        self.warrior_count[warrior_type] = max(0, self.warrior_count[warrior_type] - amount)

    def add_token(self, token_type: Token, amount: int = 1):
        self.token_count[token_type] += amount

    def remove_token(self, token_type: Token, amount: int = 1):
        self.token_count[token_type] = max(0, self.token_count[token_type] - amount)
