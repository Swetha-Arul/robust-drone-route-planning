from typing import Dict, List, Optional, Tuple
import heapq
import math

from src.environment.grid import GridMap, Position


class GridPlanner:
    def __init__(self, environment: GridMap):
        self.env = environment

    def plan(self, start: Position, goal: Position) -> Optional[List[Position]]:
        if not self.env.is_traversable(start) or not self.env.is_traversable(goal):
            return None

        open_set: List[Tuple[float, Position]] = []
        heapq.heappush(open_set, (0.0, start))

        came_from: Dict[Position, Position] = {}
        g_cost: Dict[Position, float] = {start: 0.0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current)

            for neighbor in self._neighbors_3d(current):
                if not self.env.is_traversable(neighbor):
                    continue

                step_cost = self._movement_cost(current, neighbor)
                tentative_g = g_cost[current] + step_cost

                if neighbor not in g_cost or tentative_g < g_cost[neighbor]:
                    came_from[neighbor] = current
                    g_cost[neighbor] = tentative_g
                    f_cost = tentative_g + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_cost, neighbor))

        return None

    def _neighbors_3d(self, pos: Position) -> List[Position]:
        x, y, z = pos
        neighbors = []

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if dx == dy == dz == 0:
                        continue
                    neighbors.append((x + dx, y + dy, z + dz))

        return neighbors

    def _movement_cost(self, a: Position, b: Position) -> float:
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        dz = abs(a[2] - b[2])
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def _heuristic(self, a: Position, b: Position) -> float:
        return math.dist(a, b)

    def _reconstruct_path(
        self, came_from: Dict[Position, Position], current: Position
    ) -> List[Position]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
