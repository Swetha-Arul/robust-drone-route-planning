import numpy as np
import pyvista as pv
import random
import time

from src.environment.grid import GridMap
from src.planner.planner import GridPlanner


class DroneSimulator:

    def __init__(self, env: GridMap, planner: GridPlanner, start, goal):

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

    def build_ground(self):

        rows, cols, _ = self.env._grid.shape

        plane = pv.Plane(
            center=(cols/2, rows/2, 0),
            i_size=cols,
            j_size=rows,
            i_resolution=cols,
            j_resolution=rows
        )

        self.plotter.add_mesh(plane, color="#1f2937", show_edges=True)

    def generate_buildings(self):

        x_size, y_size, _ = self.env._grid.shape

        for _ in range(30):

            x = random.randint(2, x_size-3)
            y = random.randint(2, y_size-3)

            if (x,y)==(self.start[0],self.start[1]) or (x,y)==(self.goal[0],self.goal[1]):
                continue

            height = random.randint(3,7)

            building = pv.Box(
                bounds=(y-0.5,y+0.5,x-0.5,x+0.5,0,height)
            )

            self.plotter.add_mesh(building,color="lightgray")

            for z in range(height+1):
                self.env.add_obstacle((x,y,z))

    def generate_trees(self):

        for _ in range(20):

            x=random.uniform(0,20)
            y=random.uniform(0,20)

            trunk=pv.Cylinder(center=(y,x,0.5),radius=0.1,height=1)
            leaves=pv.Sphere(center=(y,x,1.5),radius=0.4)

            self.plotter.add_mesh(trunk,color="brown")
            self.plotter.add_mesh(leaves,color="green")

            gx=int(x)
            gy=int(y)

            for z in range(3):
                if self.env.in_bounds((gx,gy,z)):
                    self.env.add_obstacle((gx,gy,z))

    def draw_path(self):

        if self.path is None:
            return

        pts=[[p[1],p[0],p[2]+1] for p in self.path]

        spline=pv.Spline(np.array(pts),200)

        self.plotter.add_mesh(
            spline,
            color="lime",
            line_width=5,
            name="planned_path"
        )

    def create_drone(self):

        drone=pv.Sphere(radius=0.3)

        self.drone_actor=self.plotter.add_mesh(drone,color="red")

        self.drone_actor.SetPosition(
            self.start[1],
            self.start[0],
            self.start[2] + 1
        )

    def update_trail(self,point):

        self.trail_points.append(point)

        trail=pv.PolyData(np.array(self.trail_points,dtype=np.float32))

        if self.trail_actor:
            self.plotter.remove_actor(self.trail_actor)

        self.trail_actor=self.plotter.add_mesh(
            trail,
            color="cyan",
            line_width=3
        )

    def enable_interaction(self):

        def add_obstacle(point):

            gx=int(np.floor(point[1]))
            gy=int(np.floor(point[0]))

            print("🚧 Obstacle added:",(gx,gy))

            height = 6

            for z in range(height):
                if self.env.in_bounds((gx,gy,z)):
                    self.env.add_obstacle((gx,gy,z))

            cube=pv.Box(
                bounds=(gy-0.5,gy+0.5,gx-0.5,gx+0.5,0,height)
            )

            self.plotter.add_mesh(cube,color="red")

        self.plotter.enable_point_picking(callback=add_obstacle)

    def obstacle_ahead(self):

        lookahead = 2

        for i in range(1,lookahead+1):

            if self.route_index+i >= len(self.path):
                return False

            cell = self.path[self.route_index+i]

            if not self.env.is_traversable(cell):
                return True

        return False

    def run(self):

        self.build_ground()
        self.generate_buildings()
        self.generate_trees()

        self.path=self.planner.plan(self.start,self.goal)

        if self.path is None:
            raise RuntimeError("No path")

        self.route_index=0

        self.draw_path()

        self.create_drone()
        self.enable_interaction()

        self.plotter.show(interactive_update=True)

        while self.current_pos!=self.goal:

            if self.route_index>=len(self.path)-1:
                break

            # Detect obstacle ahead
            if self.obstacle_ahead():

                print("🚨 Obstacle detected ahead")
                print("⏸ Drone stopping for replanning")

                time.sleep(0.5)

                new_path = self.planner.plan(self.current_pos,self.goal)

                if new_path is None:
                    print("❌ No alternate path")
                    break

                print("🔁 New route calculated")

                self.path = new_path
                self.route_index = 0
                self.current_pos = new_path[0]

                self.plotter.remove_actor("planned_path")
                self.draw_path()

                continue

            next_pos=self.path[self.route_index+1]

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

                interp=start_xyz+(end_xyz-start_xyz)*(i/15)

                self.drone_actor.SetPosition(*interp)

                self.plotter.update()
                time.sleep(0.03)

            self.current_pos=next_pos
            self.route_index+=1

            self.update_trail(end_xyz)

        print("✅ Goal reached")

        self.plotter.show()