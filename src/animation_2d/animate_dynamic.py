import matplotlib.pyplot as plt
import numpy as np

from src.environment.grid import GridMap
from src.environment.constraints import add_rectangular_no_fly_zone
from src.planner.planner import GridPlanner


# =========================
# 1. CREATE ENVIRONMENT
# =========================
ROWS, COLS = 20, 20
env = GridMap(ROWS, COLS)

# Static no-fly zone
add_rectangular_no_fly_zone(env, (8, 8), (12, 12))

planner = GridPlanner(env)

start = (0, 0)
goal = (19, 19)

path = planner.plan(start, goal)

if path is None:
    print("❌ No initial path found")
    exit()


# =========================
# 2. VISUALIZATION SETUP
# =========================
plt.ion()
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_title("Dynamic Drone Replanning using A*")

def draw_grid():
    ax.clear()
    grid = env.snapshot()
    ax.imshow(grid, cmap="gray_r")

    ax.set_xticks(range(COLS))
    ax.set_yticks(range(ROWS))
    ax.grid(True)

    # Fix coordinate orientation
    ax.invert_yaxis()

    # Start & Goal
    ax.plot(start[1], start[0], "go", markersize=10, label="Start")
    ax.plot(goal[1], goal[0], "bo", markersize=10, label="Goal")

draw_grid()


# =========================
# 3. DRONE MOVEMENT + REPLANNING
# =========================
current_pos = start
dynamic_obstacle_added = False
step_count = 0

while current_pos != goal:

    if path is None or len(path) < 2:
        print("❌ No valid path available")
        break

    next_pos = path[1]

    # 🚨 FORCE obstacle directly in front of drone
    if step_count == 8 and not dynamic_obstacle_added:
        print(f"⚠️ Dynamic obstacle detected at {next_pos}! Replanning...")
        env.add_obstacle(next_pos)
        dynamic_obstacle_added = True

        draw_grid()
        path = planner.plan(current_pos, goal)
        continue

    # Move drone
    current_pos = next_pos
    path.pop(0)
    step_count += 1

    ax.plot(current_pos[1], current_pos[0], "ro")
    plt.pause(0.3)


plt.ioff()
plt.legend()
plt.show()
