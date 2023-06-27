import pygame
from pygame import Color, Vector2, Surface

from src.config import Config, Colors
from src.game.Building import Building
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

        # text: area_index
        margin_top = 4
        text = str(self.area_index)

        surface = Config.FONT_1.render(text, True, Colors.WHITE)
        surface_rect = surface.get_rect()
        surface_rect.centerx = self.position.x
        surface_rect.top = self.position.y + self.radius + margin_top
        screen.blit(surface, surface_rect)

    def draw_buildings(self, screen: Surface):

        pass

    def ruler(self) -> Warrior:
        # only for MARQUIS vs DECREE
        if self.warrior_count[Warrior.MARQUIS] > self.warrior_count[Warrior.DECREE]:
            return Warrior.MARQUIS
        else:
            return Warrior.DECREE
