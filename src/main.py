from src.environment.grid import GridMap
from src.environment.constraints import add_cuboid_no_fly_zone
from src.planner.planner import GridPlanner
from src.validation.route_validator import RouteValidator
from src.decision.preflight_checker import PreflightChecker, PreflightDecision
from src.execution.mission_executor import MissionExecutor
from src.execution.execution_state import MissionStatus
from src.monitoring.route_monitor import RouteMonitor
from src.recovery.replanner import Replanner


def run_mission():
    # -----------------------------
    # 1. 3D VOXEL ENVIRONMENT
    # -----------------------------
    env = GridMap(30, 30, 10)  # x, y, z

    # Add a 3D no-fly cuboid
    add_cuboid_no_fly_zone(
        env,
        min_corner=(10, 10, 3),
        max_corner=(15, 15, 7),
    )

    start = (0, 0, 2)
    goal = (29, 29, 6)
    home = start

    print("🌍 3D Voxel Environment initialized")

    # -----------------------------
    # 2. 3D PLANNING
    # -----------------------------
    planner = GridPlanner(env)
    route = planner.plan(start, goal)

    # -----------------------------
    # 3. PREFLIGHT
    # -----------------------------
    validator = RouteValidator(env)
    preflight = PreflightChecker(validator, max_route_length=300)

    result = preflight.check(route)
    if result.decision != PreflightDecision.GO:
        print("❌ Preflight rejected:", result)
        return

    print("✅ Preflight approved")

    # -----------------------------
    # 4. EXECUTION SETUP
    # -----------------------------
    executor = MissionExecutor(route)
    monitor = RouteMonitor(env)
    replanner = Replanner(planner, home)

    step_counter = 0
    goal_blocked = False

    # -----------------------------
    # 5. MISSION LOOP
    # -----------------------------
    while executor.status in (MissionStatus.RUNNING, MissionStatus.PAUSED):

        print(
            f"➡️ Step {step_counter} | "
            f"State={executor.status.value} | "
            f"Pos={executor.current_position()}"
        )

        # Inject dynamic failure
        if step_counter == 8 and not goal_blocked:
            env.add_obstacle(goal)
            goal_blocked = True
            print(f"🚧 Goal voxel blocked at {goal}")

            print("🚨 Immediate replan triggered due to goal blockage")
            recovered = replanner.replan_or_abort(executor, goal)
            if not recovered:
                print("🛑 Immediate recovery failed")
                break


        # HARD SAFETY CHECK
        if monitor.current_position_invalid(executor):
            print("🛑 Current voxel invalid — aborting")
            executor.abort(reason="current_voxel_invalid")
            break

        validation = monitor.validate_remaining_route(executor)

        if validation and not validation.valid:
            print("🚨 Route invalidated — triggering replanning")

            recovered = replanner.replan_or_abort(executor, goal)
            if recovered:
                continue
            else:
                print("🛑 Recovery failed")
                break

        executor.step()
        step_counter += 1

    # -----------------------------
    # 6. FINAL STATE
    # -----------------------------
    print("🏁 Final Mission Status:", executor.status.value)
    if executor.status == MissionStatus.ABORTED:
        print("❌ Abort reason:", executor.abort_reason)


if __name__ == "__main__":
    run_mission()
