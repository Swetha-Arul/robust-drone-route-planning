import numpy as np
import pyvista as pv
import random
import time


class DroneSimulator:

    def __init__(self, env, planner, start, goal, battery_capacity):

        self.env = env
        self.planner = planner

        self.start = start
        self.goal = goal

        self.current_pos = start

        self.plotter = pv.Plotter()
        self.plotter.set_background("#0b0f17")

        self.path = None
        self.route_index = 0

        self.trail_points = []
        self.trail_actor = None

        self.rain_systems = []

        # 🔋 Battery system
        self.battery_capacity = battery_capacity
        self.battery_remaining = battery_capacity
        self.payload_weight = planner.payload_weight

    # ------------------- ENVIRONMENT -------------------

    def build_ground(self):

        rows, cols, _ = self.env._grid.shape

        plane = pv.Plane(
            center=(cols/2, rows/2, 0),
            i_size=cols,
            j_size=rows,
            i_resolution=cols,
            j_resolution=rows
        )

        self.plotter.add_mesh(
            plane,
            color="#1f2937",
            show_edges=True,
            pickable=True
        )

    def generate_buildings(self):

        x_size, y_size, _ = self.env._grid.shape

        for _ in range(30):

            x = random.randint(2, x_size-3)
            y = random.randint(2, y_size-3)

            if (x, y) == (self.start[0], self.start[1]) or (x, y) == (self.goal[0], self.goal[1]):
                continue

            height = random.randint(3, 7)

            building = pv.Box(
                bounds=(y-0.5, y+0.5, x-0.5, x+0.5, 0, height)
            )

            self.plotter.add_mesh(building, color="lightgray")

            for z in range(height+1):
                self.env.add_obstacle((x, y, z))

    def generate_trees(self):

        for _ in range(20):

            x = random.uniform(0, 20)
            y = random.uniform(0, 20)

            trunk = pv.Cylinder(center=(y, x, 0.5), radius=0.1, height=1)
            leaves = pv.Sphere(center=(y, x, 1.5), radius=0.4)

            self.plotter.add_mesh(trunk, color="brown")
            self.plotter.add_mesh(leaves, color="green")

            gx = int(x)
            gy = int(y)

            for z in range(3):
                if self.env.in_bounds((gx, gy, z)):
                    self.env.add_obstacle((gx, gy, z))

    # ------------------- WEATHER -------------------

    def draw_weather(self):

        if not hasattr(self.planner, "weather"):
            return

        weather = self.planner.weather

        if weather is None:
            return

        for cx, cy, radius, typ in weather.zones:

            if typ != "rain":
                continue

            points = np.random.uniform(-radius, radius, (300, 3))

            points[:, 0] += cy
            points[:, 1] += cx
            points[:, 2] = np.random.uniform(3, 7, 300)

            rain = pv.PolyData(points)

            self.plotter.add_mesh(
                rain,
                color="lightblue",
                point_size=3,
                render_points_as_spheres=True
            )

            self.rain_systems.append(rain)

    def update_rain(self):

        for rain in self.rain_systems:

            pts = rain.points
            pts[:, 2] -= 0.2

            reset = pts[:, 2] < 0
            pts[reset, 2] = np.random.uniform(5, 8, np.sum(reset))

            rain.points = pts

    # ------------------- PATH -------------------

    def draw_path(self):

        pts = [[p[1], p[0], p[2]+1] for p in self.path]

        spline = pv.Spline(np.array(pts), 200)

        self.plotter.add_mesh(
            spline,
            color="lime",
            line_width=5,
            name="planned_path"
        )

    # ------------------- DRONE -------------------

    def create_drone(self):

        drone = pv.Sphere(radius=0.3)

        self.drone_actor = self.plotter.add_mesh(drone, color="green")

        self.drone_actor.SetPosition(
            self.start[1],
            self.start[0],
            self.start[2] + 1
        )

    # ------------------- ENERGY -------------------

    def compute_energy(self, a, b):

        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        dz = abs(a[2] - b[2])

        distance = np.sqrt(dx*dx + dy*dy + dz*dz)

        payload_factor = 1 + (self.payload_weight * 0.15)
        altitude_factor = 1.8 if dz > 0 else 1

        return distance * payload_factor * altitude_factor

    def update_battery_display(self):

        percentage = self.battery_remaining / self.battery_capacity

        bar_length = 20
        filled = int(bar_length * percentage)

        bar = "█" * filled + "-" * (bar_length - filled)

        print(f"🔋 Battery: [{bar}] {percentage*100:.1f}%")

    # ------------------- INTERACTION -------------------

    def enable_interaction(self):

        def add_obstacle(mesh):

            if mesh is None:
                return

            point = self.plotter.pick_mouse_position()

            if point is None:
                return

            world_x, world_y, world_z = point

            grid_x = int(np.floor(world_y))
            grid_y = int(np.floor(world_x))

            grid_x = max(0, min(grid_x, self.env.x_size - 1))
            grid_y = max(0, min(grid_y, self.env.y_size - 1))

            print("🚧 Obstacle added:", (grid_x, grid_y))

            height = 6

            for z in range(height):
                if self.env.in_bounds((grid_x, grid_y, z)):
                    self.env.add_obstacle((grid_x, grid_y, z))

            cube = pv.Box(bounds=(
                grid_y - 0.5, grid_y + 0.5,
                grid_x - 0.5, grid_x + 0.5,
                0, height
            ))

            self.plotter.add_mesh(cube, color="red")

        self.plotter.enable_mesh_picking(callback=add_obstacle)

    # ------------------- TRAIL -------------------

    def update_trail(self, point):

        self.trail_points.append(point)

        trail = pv.PolyData(np.array(self.trail_points, dtype=np.float32))

        if self.trail_actor:
            self.plotter.remove_actor(self.trail_actor)

        self.trail_actor = self.plotter.add_mesh(
            trail,
            color="cyan",
            line_width=3
        )

    # ------------------- OBSTACLE DETECTION -------------------

    def obstacle_ahead(self):

        lookahead = 2

        for i in range(1, lookahead+1):

            if self.route_index + i >= len(self.path):
                return False

            cell = self.path[self.route_index + i]

            if not self.env.is_traversable(cell):
                return True

        return False

    # ------------------- MAIN LOOP -------------------

    def run(self):

        self.build_ground()
        self.generate_buildings()
        self.generate_trees()
        self.draw_weather()

        self.path = self.planner.plan(self.start, self.goal)

        if self.path is None:
            raise RuntimeError("No path")

        self.route_index = 0

        self.draw_path()
        self.create_drone()
        self.enable_interaction()

        self.plotter.show(interactive_update=True)

        while self.current_pos != self.goal:

            if self.route_index >= len(self.path) - 1:
                break

            if self.obstacle_ahead():

                print("🚨 Obstacle detected ahead")
                print("⏸ Replanning...")

                new_path = self.planner.plan(self.current_pos, self.goal)

                if new_path is None:
                    print("❌ No alternate path")
                    break

                self.path = new_path
                self.route_index = 0

                self.plotter.remove_actor("planned_path")
                self.draw_path()

                continue

            next_pos = self.path[self.route_index + 1]

            # 🔋 ENERGY UPDATE
            energy = self.compute_energy(self.current_pos, next_pos)
            self.battery_remaining -= energy

            self.update_battery_display()

            # 🎨 COLOR CHANGE
            ratio = self.battery_remaining / self.battery_capacity

            if ratio > 0.6:
                color = "green"
            elif ratio > 0.3:
                color = "yellow"
            else:
                color = "red"

            self.drone_actor.GetProperty().SetColor(*pv.Color(color).float_rgb)

            if self.battery_remaining <= 0:
                print("🔴 Battery depleted! Drone stopped.")
                break

            if self.battery_remaining < 50:
                print("⚠️ Low battery!")

            start_xyz = np.array([
                self.current_pos[1],
                self.current_pos[0],
                self.current_pos[2] + 1
            ])

            end_xyz = np.array([
                next_pos[1],
                next_pos[0],
                next_pos[2] + 1
            ])

            for i in range(15):

                interp = start_xyz + (end_xyz - start_xyz) * (i / 15)

                self.drone_actor.SetPosition(*interp)
                self.update_rain()

                self.plotter.update()
                time.sleep(0.03)

            self.current_pos = next_pos
            self.route_index += 1

            self.update_trail(end_xyz)

        print("✅ Simulation complete")

        self.plotter.show()