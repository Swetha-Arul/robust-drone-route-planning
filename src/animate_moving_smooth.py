import matplotlib.pyplot as plt
import numpy as np
import time

from src.environment.grid import GridMap
from src.planner.planner import GridPlanner


# =========================
# ENVIRONMENT
# =========================
ROWS, COLS = 20, 20
env = GridMap(ROWS, COLS)
planner = GridPlanner(env)

start = (0, 0)
goal = (19, 19)


# =========================
# PATH SMOOTHING (LOS)
# =========================
def has_line_of_sight(a, b):
    r1, c1 = a
    r2, c2 = b
    steps = max(abs(r2 - r1), abs(c2 - c1))
    for i in range(steps + 1):
        r = int(r1 + (r2 - r1) * i / steps)
        c = int(c1 + (c2 - c1) * i / steps)
        if not env.is_traversable((r, c)):
            return False
    return True


def smooth_path(path):
    if path is None or len(path) < 3:
        return path
    result = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1:
            if has_line_of_sight(path[i], path[j]):
                break
            j -= 1
        result.append(path[j])
        i = j
    return result


# =========================
# ENEMY DRONE (MOVING)
# =========================
enemy_row = 10
enemy_col = 0
enemy_dir = 1

def move_enemy():
    global enemy_col, enemy_dir

    env.clear_cell((enemy_row, enemy_col))

    enemy_col += enemy_dir
    if enemy_col == COLS - 1 or enemy_col == 0:
        enemy_dir *= -1

    env.add_obstacle((enemy_row, enemy_col))
    return (enemy_row, enemy_col)


# =========================
# INITIAL PLAN
# =========================
path = smooth_path(planner.plan(start, goal))
current_pos = start


# =========================
# VISUALIZATION
# =========================
plt.ion()
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_title("Moving Obstacle + Replanning + Path Smoothing")

def draw(enemy_pos, drone_pos):
    ax.clear()
    ax.imshow(env.snapshot(), cmap="gray_r")

    ax.set_xticks(range(COLS))
    ax.set_yticks(range(ROWS))
    ax.grid(True)
    ax.invert_yaxis()

    # Start & goal
    ax.plot(start[1], start[0], "go", markersize=10)
    ax.plot(goal[1], goal[0], "bo", markersize=10)

    # Enemy drone (BLUE)
    ax.plot(enemy_pos[1], enemy_pos[0], "bs", markersize=10)

    # Our drone (RED)
    ax.plot(drone_pos[1], drone_pos[0], "ro", markersize=10)


# =========================
# MAIN LOOP
# =========================
enemy_pos = (enemy_row, enemy_col)

while current_pos != goal:

    # 1️⃣ Move enemy every frame
    enemy_pos = move_enemy()

    # 2️⃣ Replan ONLY if enemy blocks next move
    if path and enemy_pos in path[:3]:
        print("⚠️ Enemy ahead → replanning")
        path = smooth_path(planner.plan(current_pos, goal))
        if path is None:
            print("❌ No path possible")
            break

    # 3️⃣ Move our drone
    if path and len(path) > 1:
        current_pos = path[1]
        path.pop(0)

    # 4️⃣ Draw everything
    draw(enemy_pos, current_pos)
    plt.pause(0.4)

plt.ioff()
plt.show()
