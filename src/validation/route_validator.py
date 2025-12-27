"""
Deterministic verification of planned routes against
environment constraints.
"""

from enum import Enum
from typing import List, Optional

from src.environment.grid import GridMap, Position


class RouteInvalidReason(Enum):
    # Reasons why a route can be rejected
    EMPTY_ROUTE = "empty_route"
    OUT_OF_BOUNDS = "out_of_bounds"
    OBSTACLE = "obstacle"
    NO_FLY_ZONE = "no_fly_zone"


class RouteValidationResult:
    # Holds the outcome of route validation
    def __init__(
        self,
        valid: bool,
        reason: Optional[RouteInvalidReason] = None,
        failing_position: Optional[Position] = None,
    ):
        self.valid = valid
        self.reason = reason
        self.failing_position = failing_position

    def __bool__(self) -> bool:
        # Allows `if result:` style checks
        return self.valid

    def __repr__(self) -> str:
        # Helpful string for logs and debugging
        if self.valid:
            return "RouteValidationResult(valid=True)"
        return (
            "RouteValidationResult("
            f"valid=False, reason={self.reason}, "
            f"failing_position={self.failing_position})"
        )


class RouteValidator:
    # Validates routes against the current environment state
    def __init__(self, env: GridMap):
        self.env = env

    def validate(self, route: List[Position]) -> RouteValidationResult:
        # Reject missing or empty routes early
        if route is None or len(route) == 0:
            return RouteValidationResult(
                valid=False,
                reason=RouteInvalidReason.EMPTY_ROUTE,
            )

        # Snapshot once to keep validation consistent
        grid = self.env.snapshot()

        for pos in route:
            # Route must stay within grid bounds
            if not self.env.in_bounds(pos):
                return RouteValidationResult(
                    valid=False,
                    reason=RouteInvalidReason.OUT_OF_BOUNDS,
                    failing_position=pos,
                )

            cell_state = grid[pos]

            # Obstacles are non-traversable
            if cell_state == self.env.OBSTACLE:
                return RouteValidationResult(
                    valid=False,
                    reason=RouteInvalidReason.OBSTACLE,
                    failing_position=pos,
                )

            # No-fly zones represent restricted airspace
            if cell_state == self.env.NO_FLY:
                return RouteValidationResult(
                    valid=False,
                    reason=RouteInvalidReason.NO_FLY_ZONE,
                    failing_position=pos,
                )

        # All checks passed
        return RouteValidationResult(valid=True)
