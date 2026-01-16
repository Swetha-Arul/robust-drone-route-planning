from typing import Tuple
import numpy as np

Position = Tuple[int, int, int]  # (x, y, z)

class GridMap:
    FREE = 0
    OBSTACLE = 1
    NO_FLY = 2

    def __init__(self, x_size: int, y_size: int, z_size: int):
        self.x_size = x_size
        self.y_size = y_size
        self.z_size = z_size
        self._grid = np.zeros((x_size, y_size, z_size), dtype=int)

    def in_bounds(self, pos: Position) -> bool:
        x, y, z = pos
        return (
            0 <= x < self.x_size and
            0 <= y < self.y_size and
            0 <= z < self.z_size
        )

    def is_traversable(self, pos: Position) -> bool:
        return self.in_bounds(pos) and self._grid[pos] == self.FREE

    def is_constrained(self, pos: Position) -> bool:
        return not self.in_bounds(pos) or self._grid[pos] != self.FREE

    def add_obstacle(self, pos: Position):
        if self.in_bounds(pos):
            self._grid[pos] = self.OBSTACLE

    def add_no_fly_zone(self, pos: Position):
        if self.in_bounds(pos):
            self._grid[pos] = self.NO_FLY

    def snapshot(self) -> np.ndarray:
        return self._grid.copy()