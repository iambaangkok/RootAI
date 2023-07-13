from numpy import ones, vstack
from numpy.linalg import lstsq
from pygame import Vector2


def get_path_points(a: Vector2, b: Vector2, shift_size: float) -> [Vector2, Vector2]:
    new_a: Vector2 = a.move_towards(b, shift_size)
    new_b: Vector2 = b.move_towards(a, shift_size)
    return new_a, new_b

