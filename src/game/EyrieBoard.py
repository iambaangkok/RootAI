import pygame
from pygame import Color, Vector2, Surface

from src.game.FactionBoard import FactionBoard


class EyrieBoard(FactionBoard):
    def __init__(self, name: str, color: Color, reserved_warriors: int, starting_point: Vector2):
        super().__init__(name, color, reserved_warriors, starting_point)

    def draw(self, screen: Surface):
        super().draw(screen)
