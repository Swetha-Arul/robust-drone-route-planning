from src.environment.grid import GridMap
from src.environment.constraints import add_rectangular_no_fly_zone
from src.planner.planner import GridPlanner
from src.validation.route_validator import RouteValidator
from src.decision.preflight_checker import PreflightChecker, PreflightDecision
from src.execution.mission_executor import MissionExecutor
from src.execution.execution_state import MissionStatus
from src.monitoring.route_monitor import RouteMonitor
from src.recovery.replanner import Replanner


def run_mission():
    # -----------------------------
    # 1. Environment
    # -----------------------------
    env = GridMap(20, 20)
    add_rectangular_no_fly_zone(env, (8, 8), (12, 12))

    start = (0, 0)
    goal = (19, 19)
    home = start

    print("🌍 Environment initialized")

    # -----------------------------
    # 2. Planning
    # -----------------------------
    planner = GridPlanner(env)
    route = planner.plan(start, goal)

    # -----------------------------
    # 3. Preflight
    # -----------------------------
    validator = RouteValidator(env)
    preflight = PreflightChecker(validator, max_route_length=100)

    result = preflight.check(route)
    if result.decision != PreflightDecision.GO:
        print("❌ Preflight rejected:", result)
        return

    print("✅ Preflight approved")

    # -----------------------------
    # 4. Execution setup
    # -----------------------------
    executor = MissionExecutor(route)
    monitor = RouteMonitor(env)
    replanner = Replanner(planner, home)

    step_counter = 0
    goal_blocked = False

    # -----------------------------
    # 5. Mission loop
    # -----------------------------
    while executor.status in (MissionStatus.RUNNING, MissionStatus.PAUSED):
        print(
            f"➡️ Step {step_counter} | "
            f"State={executor.status.value} | "
            f"Pos={executor.current_position()}"
        )

        # 🚨 GUARANTEED CORE 8 TRIGGER
        if step_counter == 8 and not goal_blocked:
            env.add_obstacle(goal)
            goal_blocked = True
            print(f"🚧 Goal blocked at {goal}")

        validation = monitor.validate_remaining_route(executor)

        if validation and not validation.valid:
            print("🚨 Route invalidated — Core 8 triggered")

            recovered = replanner.replan_or_abort(executor, goal)
            if recovered:
                print("🔁 Replanning succeeded")
                continue
            else:
                print("🛑 Mission aborted or returning home")
                break

        executor.step()
        step_counter += 1

    # -----------------------------
    # 6. Final state
    # -----------------------------
    print("🏁 Final Mission Status:", executor.status.value)
    if executor.status == MissionStatus.ABORTED:
        print("❌ Abort reason:", executor.abort_reason)


if __name__ == "__main__":
    run_mission()
