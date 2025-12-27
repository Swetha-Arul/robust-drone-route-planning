import time
import matplotlib.pyplot as plt
import numpy as np

from src.environment.grid import GridMap
from src.environment.constraints import add_obstacle_line, add_rectangular_no_fly_zone
from src.planner.planner import GridPlanner

# -------- Create Environment --------
rows, cols = 20, 20
env = GridMap(rows, cols)

# Obstacles
add_obstacle_line(env, (5, 8), (15, 8))
add_rectangular_no_fly_zone(env, (10, 2), (13, 5))

# -------- Plan Path --------
planner = GridPlanner(env)
start = (0, 0)
goal = (19, 19)

path = planner.plan(start, goal)

if path is None:
    print("No path found")
    exit()

# -------- Visualization Grid --------
grid = np.zeros((rows, cols))

for r in range(rows):
    for c in range(cols):
        if not env.is_traversable((r, c)):
            grid[r, c] = 1  # obstacle

# -------- Matplotlib Setup --------
plt.ion()
fig, ax = plt.subplots()
ax.set_title("2D Drone Route Planning (A*)")

ax.imshow(grid, cmap="gray_r")
ax.set_xticks(range(cols))
ax.set_yticks(range(rows))
ax.grid(True)

# -------- Animate Drone --------
for (r, c) in path:
    ax.plot(c, r, "ro")   # drone position
    plt.pause(0.2)

plt.ioff()
plt.show()
