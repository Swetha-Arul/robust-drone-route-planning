from src.environment.grid import GridMap
from src.validation.route_validator import RouteValidator
from src.decision.preflight_checker import (
    PreflightChecker,
    PreflightDecision,
    PreflightRejectReason,
)


def test_preflight_checker():
    env = GridMap(5, 5)
    env.add_obstacle((2, 2))

    validator = RouteValidator(env)
    checker = PreflightChecker(validator, max_route_length=5)

    # 1. No route
    result = checker.check(None)
    assert result.decision == PreflightDecision.NO_GO
    assert result.reason == PreflightRejectReason.NO_ROUTE

    # 2. Invalid route
    result = checker.check([(2, 2)])
    assert result.decision == PreflightDecision.NO_GO
    assert result.reason == PreflightRejectReason.INVALID_ROUTE

    # 3. Route too long
    long_route = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4)]
    result = checker.check(long_route)
    assert result.decision == PreflightDecision.NO_GO
    assert result.reason == PreflightRejectReason.COST_EXCEEDED

    # 4. Valid route
    valid_route = [(0, 0), (0, 1), (0, 2)]
    result = checker.check(valid_route)
    assert result.decision == PreflightDecision.GO

    print("PreflightChecker: all tests passed.")


if __name__ == "__main__":
    test_preflight_checker()
