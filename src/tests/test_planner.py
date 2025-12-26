from typing import Dict, List, Optional, Tuple
import heapq

from src.environment.grid import GridMap, Position


class GridPlanner:
    """Grid-based path planner using A* search.

    Generates a feasible route from start to goal using environment
    constraint queries only. Does not perform optimization beyond
    shortest-path search.
    """

    def __init__(self, environment: GridMap):
        self.env = environment

    def plan(self, start: Position, goal: Position) -> Optional[List[Position]]:
        """Return a feasible route from start to goal, or None if no route exists."""
        if not self.env.is_traversable(start) or not self.env.is_traversable(goal):
            return None

        open_set: List[Tuple[int, Position]] = []
        heapq.heappush(open_set, (0, start))

        came_from: Dict[Position, Position] = {}
        g_cost: Dict[Position, int] = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current)

            for neighbor in self._neighbors(current):
                if not self.env.is_traversable(neighbor):
                    continue

                tentative_g = g_cost[current] + 1

                if neighbor not in g_cost or tentative_g < g_cost[neighbor]:
                    came_from[neighbor] = current
                    g_cost[neighbor] = tentative_g
                    f_cost = tentative_g + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_cost, neighbor))

        return None

    def _neighbors(self, pos: Position) -> List[Position]:
        r, c = pos
        return [
            (r - 1, c),
            (r + 1, c),
            (r, c - 1),
            (r, c + 1),
        ]

    def _heuristic(self, a: Position, b: Position) -> int:
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _reconstruct_path(
        self, came_from: Dict[Position, Position], current: Position
    ) -> List[Position]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
