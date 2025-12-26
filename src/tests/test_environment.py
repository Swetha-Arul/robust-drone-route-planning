"""Demo showing basic GridMap usage."""

from src.environment.grid import GridMap
from src.environment.constraints import (
    add_obstacle_line,
    add_rectangular_no_fly_zone,
)

# Create a 20x20 grid
env = GridMap(20, 20)

# Add a vertical obstacle line and a small no-fly rectangle
add_obstacle_line(env, (5, 8), (10, 8))
add_rectangular_no_fly_zone(env, (2, 2), (4, 4))

# Quick checks (expected: True, False, False)
print(env.is_traversable((0, 0)))
print(env.is_traversable((5, 8)))
print(env.is_route_valid([(0, 0), (1, 1), (2, 2)]))
