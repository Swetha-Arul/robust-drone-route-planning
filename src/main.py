from src.environment.grid import GridMap
from src.environment.constraints import add_cuboid_no_fly_zone

from src.planner.planner import GridPlanner
from src.validation.route_validator import RouteValidator
from src.decision.preflight_checker import PreflightChecker, PreflightDecision

from src.visualization.simulator import DroneSimulator
from src.weather.weather_model import WeatherModel


def main():

    env = GridMap(20, 20, 10)

    add_cuboid_no_fly_zone(env, (10,10,2), (12,12,5))

    start = (0,0,2)
    goal = (19,19,3)

    weather = WeatherModel()
    weather.generate_weather(20,20)

    planner = GridPlanner(env,weather)

    route = planner.plan(start, goal)

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

    print("✅ Preflight approved — mission starting")

    sim = DroneSimulator(env, planner, start, goal)

    sim.run()


if __name__ == "__main__":
    main()