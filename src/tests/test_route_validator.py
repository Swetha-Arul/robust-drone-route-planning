from src.environment.grid import GridMap
from src.validation.route_validator import (
    RouteValidator,
    RouteInvalidReason,
)

def test_route_validation():
    env = GridMap(5, 5)
    env.add_obstacle((2, 2))
    env.add_no_fly_zone((3, 3))

    validator = RouteValidator(env)

    # 1. Empty route
    result = validator.validate([])
    assert not result.valid
    assert result.reason == RouteInvalidReason.EMPTY_ROUTE

    # 2. Out-of-bounds
    result = validator.validate([(10, 10)])
    assert not result.valid
    assert result.reason == RouteInvalidReason.OUT_OF_BOUNDS

    # 3. Obstacle cell
    result = validator.validate([(2, 2)])
    assert not result.valid
    assert result.reason == RouteInvalidReason.OBSTACLE

    # 4. No-fly zone
    result = validator.validate([(3, 3)])
    assert not result.valid
    assert result.reason == RouteInvalidReason.NO_FLY_ZONE

    # 5. Valid route
    result = validator.validate([(0, 0), (0, 1), (0, 2)])
    assert result.valid

    print("RouteValidator: all tests passed.")


if __name__ == "__main__":
    test_route_validation()
