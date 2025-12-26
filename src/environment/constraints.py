"""Small helpers to add simple constraints to a GridMap."""

from typing import List, Tuple
from .grid import GridMap, Position


def add_obstacle_line(env: GridMap, start: Position, end: Position):
    """Add a straight obstacle line (horizontal or vertical)."""
    r1, c1 = start
    r2, c2 = end

    if r1 == r2:  # horizontal
        for c in range(min(c1, c2), max(c1, c2) + 1):
            env.add_obstacle((r1, c))
    elif c1 == c2:  # vertical
        for r in range(min(r1, r2), max(r1, r2) + 1):
            env.add_obstacle((r, c1))


def add_rectangular_no_fly_zone(env: GridMap, top_left: Position, bottom_right: Position):
    """Fill a rectangle with no-fly markers (inclusive bounds)."""
    r1, c1 = top_left
    r2, c2 = bottom_right

    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            env.add_no_fly_zone((r, c))
