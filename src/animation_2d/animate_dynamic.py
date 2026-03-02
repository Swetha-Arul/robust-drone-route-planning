import numpy as np
import pyvista as pv
import time

from src.environment.grid import GridMap
from src.environment.constraints import add_cuboid_no_fly_zone
from src.planner.planner import GridPlanner


# =========================
# 1. CREATE 3D ENVIRONMENT
# =========================
ROWS, COLS, HEIGHT = 20, 20, 5
env = GridMap(ROWS, COLS, HEIGHT)

# Add initial 3D cuboid obstacle
add_cuboid_no_fly_zone(env, (8, 8, 0), (12, 12, 2))

planner = GridPlanner(env)

start = (0, 0, 0)
goal = (19, 19, 0)

path = planner.plan(start, goal)

print("Obstacle cells:", np.sum(env.snapshot()))
print("Path:", path)
print("Path length:", 0 if path is None else len(path))

if path is None:
    print("❌ No initial path found")
    exit()


# =========================
# 2. PYVISTA SETUP
# =========================
plotter = pv.Plotter()
plotter.set_background("#0e1117")

# Ground plane
plane = pv.Plane(
    center=(COLS / 2, ROWS / 2, 0),
    i_size=COLS,
    j_size=ROWS,
    i_resolution=COLS,
    j_resolution=ROWS
)

plotter.add_mesh(plane, color="#1f2937", show_edges=True)


# =========================
# DRAW OBSTACLES
# =========================
def draw_obstacles():
    grid = env.snapshot()

    for x in range(ROWS):
        for y in range(COLS):
            for z in range(HEIGHT):
                if grid[x, y, z] == 1:
                    cube = pv.Cube(
                        center=(y, x, z + 0.5),
                        x_length=1,
                        y_length=1,
                        z_length=1
                    )
                    plotter.add_mesh(cube, color="orange")


draw_obstacles()


# =========================
# START & GOAL
# =========================
plotter.add_mesh(
    pv.Sphere(radius=0.4, center=(start[1], start[0], start[2] + 0.5)),
    color="green"
)

plotter.add_mesh(
    pv.Sphere(radius=0.4, center=(goal[1], goal[0], goal[2] + 0.5)),
    color="blue"
)


# =========================
# DRONE
# =========================
drone = pv.Sphere(radius=0.3)
drone_actor = plotter.add_mesh(drone, color="red")
drone_actor.SetPosition(start[1], start[0], start[2] + 0.5)

# Trail
trail_points = [np.array([start[1], start[0], start[2] + 0.5])]
trail = pv.PolyData(np.array(trail_points))
trail_actor = plotter.add_mesh(trail, color="cyan", line_width=3)

# IMPORTANT: correct animation mode
plotter.show(interactive_update=True)


# =========================
# 3. SMOOTH MOVEMENT + SAFE REPLANNING
# =========================
current_pos = start
dynamic_obstacle_added = False
step_count = 0

while current_pos != goal:

    if path is None or len(path) < 2:
        print("❌ No valid path available")
        break

    next_pos = path[1]

    # 🚨 Insert dynamic obstacle safely
    if step_count == 8 and not dynamic_obstacle_added:
        print(f"⚠️ Dynamic obstacle at {next_pos}! Replanning...")

        env.add_no_fly_zone(next_pos)
        dynamic_obstacle_added = True

        # Draw only the new obstacle cube (NO CLEAR)
        x, y, z = next_pos
        cube = pv.Cube(
            center=(y, x, z + 0.5),
            x_length=1,
            y_length=1,
            z_length=1
        )
        plotter.add_mesh(cube, color="red")

        # Replan safely
        path = planner.plan(current_pos, goal)

        if path is None:
            print("❌ No path after replanning")
            break

        continue

    # =========================
    # Smooth movement
    # =========================
    steps = 15

    start_xyz = np.array([current_pos[1], current_pos[0], current_pos[2] + 0.5])
    end_xyz = np.array([next_pos[1], next_pos[0], next_pos[2] + 0.5])

    for i in range(steps):
        interp = start_xyz + (end_xyz - start_xyz) * (i / steps)
        drone_actor.SetPosition(interp[0], interp[1], interp[2])
        plotter.update()
        time.sleep(0.02)

    current_pos = next_pos
    path.pop(0)
    step_count += 1

    # Update trail
    trail_points.append(end_xyz)
    trail = pv.PolyData(np.array(trail_points))
    plotter.remove_actor(trail_actor)
    trail_actor = plotter.add_mesh(trail, color="cyan", line_width=3)

    plotter.update()


print("✅ Reached Goal!")
plotter.show()
