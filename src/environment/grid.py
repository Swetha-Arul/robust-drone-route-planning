"""Small grid utilities for route planning.

All coordinates in GridMap are zero-indexed and follow the format (row, col),
where (0, 0) refers to the top-left cell of the environment grid.
"""

from typing import Tuple, List
import numpy as np

Position = Tuple[int, int]  # (row, col)


class GridMap:
    """Minimal grid holding cell states (FREE, OBSTACLE, NO_FLY).

    Stores environment constraints only; planning lives elsewhere.
    """

    # Cell state constants
    FREE = 0
    OBSTACLE = 1
    NO_FLY = 2

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self._grid = np.zeros((rows, cols), dtype=int)

    
    
    

    def in_bounds(self, pos: Position) -> bool:
        """True if pos is inside the grid."""
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_traversable(self, pos: Position) -> bool:
        """True if pos is in bounds and marked FREE."""
        if not self.in_bounds(pos):
            return False
        return self._grid[pos] == self.FREE

    def is_constrained(self, pos: Position) -> bool:
        """True if pos is obstacle/no-fly or out-of-bounds."""
        if not self.in_bounds(pos):
            return True
        return self._grid[pos] in (self.OBSTACLE, self.NO_FLY)

    def add_obstacle(self, pos: Position):
        """Mark pos as an obstacle (no-op if out-of-bounds)."""
        if self.in_bounds(pos):
            self._grid[pos] = self.OBSTACLE

    def add_no_fly_zone(self, pos: Position):
        """Mark pos as a no-fly zone (no-op if out-of-bounds)."""
        if self.in_bounds(pos):
            self._grid[pos] = self.NO_FLY

    def clear_cell(self, pos: Position):
        """Clear constraints at pos (make it FREE)."""
        if self.in_bounds(pos):
            self._grid[pos] = self.FREE



    def snapshot(self) -> np.ndarray:
        """Return a safe copy of the internal grid array."""
        return self._grid.copy()
