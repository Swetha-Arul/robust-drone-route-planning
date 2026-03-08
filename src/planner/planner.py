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

                dx = neighbor[0] - current[0]
                dy = neighbor[1] - current[1]
                dz = neighbor[2] - current[2]

                if dx != 0 and dy != 0:
                    if not self.env.is_traversable((current[0] + dx, current[1], current[2])):
                        continue
                    if not self.env.is_traversable((current[0], current[1] + dy, current[2])):
                        continue

                if dx != 0 and dz != 0:
                    if not self.env.is_traversable((current[0] + dx, current[1], current[2])):
                        continue
                    if not self.env.is_traversable((current[0], current[1], current[2] + dz)):
                        continue

                if dy != 0 and dz != 0:
                    if not self.env.is_traversable((current[0], current[1] + dy, current[2])):
                        continue
                    if not self.env.is_traversable((current[0], current[1], current[2] + dz)):
                        continue

                step_cost = self._movement_cost(current, neighbor)
                tentative_g = g_cost[current] + step_cost

                if neighbor not in g_cost or tentative_g < g_cost[neighbor]:

                    came_from[neighbor] = current
                    g_cost[neighbor] = tentative_g

                    f_cost = tentative_g + self._heuristic(neighbor, goal)

                    heapq.heappush(open_set, (f_cost, neighbor))

        return None

    def _neighbors_3d(self, pos: Position):

        x, y, z = pos
        neighbors = []

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):

                    if dx == 0 and dy == 0 and dz == 0:
                        continue

                    neighbor = (x + dx, y + dy, z + dz)

                    if self.env.in_bounds(neighbor):
                        neighbors.append(neighbor)

        return neighbors

    def _movement_cost(self, a: Position, b: Position):

        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        dz = abs(a[2] - b[2])

        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def _heuristic(self, a: Position, b: Position):

        return math.dist(a, b)

    def _reconstruct_path(self, came_from, current):

        path = [current]

        while current in came_from:
            current = came_from[current]
            path.append(current)

        path.reverse()
        return path