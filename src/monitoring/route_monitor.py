"""
Monitors an executing mission for route invalidation.
"""

from typing import List, Optional

from src.environment.grid import GridMap, Position
from src.validation.route_validator import RouteValidator, RouteValidationResult
from src.execution.mission_executor import MissionExecutor
from src.execution.execution_state import MissionStatus


class RouteMonitor:
    """
    Validates the remaining route against current environment constraints.
    """

    def __init__(self, env: GridMap):
        self.validator = RouteValidator(env)

    def validate_remaining_route(
        self, executor: MissionExecutor
    ) -> Optional[RouteValidationResult]:

        if executor.status != MissionStatus.RUNNING:
            return None

        print("🔍 Validating remaining route...")
        remaining_route: List[Position] = executor.route[executor.index :]
        return self.validator.validate(remaining_route)

    def abort_if_invalid(self, executor: MissionExecutor) -> bool:
        result = self.validate_remaining_route(executor)

        if result is None or result.valid:
            return False

        print(
            f"❌ Route invalid: {result.reason} "
            f"at {result.failing_position}"
        )

        executor.abort(reason=result.reason.value)
        return True
