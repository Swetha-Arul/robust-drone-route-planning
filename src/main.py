from src.environment.grid import GridMap
from src.environment.constraints import add_cuboid_no_fly_zone

from src.planner.planner import GridPlanner
from src.validation.route_validator import RouteValidator
from src.decision.preflight_checker import PreflightChecker, PreflightDecision

from src.visualization.simulator import DroneSimulator
from src.weather.weather_model import WeatherModel


def main():

    env = GridMap(20, 20, 10)

    add_cuboid_no_fly_zone(env, (10, 10, 2), (12, 12, 5))

    start = (0, 0, 2)
    goal = (19, 19, 3)

    # 🔥 USER INPUT
    try:
        payload_weight = float(input("📦 Enter payload weight (kg): "))
        battery_capacity = float(input("🔋 Enter battery capacity: "))

        if payload_weight < 0 or battery_capacity <= 0:
            raise ValueError

    except ValueError:
        print("❌ Invalid input! Using default values.")
        payload_weight = 3.0
        battery_capacity = 300

    print("\n--- Mission Parameters ---")
    print(f"📦 Payload: {payload_weight} kg")
    print(f"🔋 Battery: {battery_capacity}")

    if payload_weight > 5:
        print("⚠️ Heavy payload detected — higher energy consumption expected")

    # 🌧️ Weather
    weather = WeatherModel()
    weather.generate_weather(20, 20)

    # 🧠 Planner (energy-aware)
    planner = GridPlanner(env, weather, payload_weight)

    route = planner.plan(start, goal)

    if route is None:
        print("❌ No path found")
        return

    # ✅ Validation
    validator = RouteValidator(env)

    preflight = PreflightChecker(
        validator,
        max_route_length=500
    )

    result = preflight.check(route)

    if result.decision != PreflightDecision.GO:
        print("❌ Mission aborted before takeoff")
        print("Reason:", result)
        return

    print("\n✅ Preflight approved — mission starting\n")

    # 🚁 Simulation with battery system
    sim = DroneSimulator(env, planner, start, goal, battery_capacity)
    sim.run()


if __name__ == "__main__":
    main()