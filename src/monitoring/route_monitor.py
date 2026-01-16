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
        self.env = env

    def validate_remaining_route(
        self, executor: MissionExecutor
    ) -> Optional[RouteValidationResult]:

        if executor.status != MissionStatus.RUNNING:
            return None

        print("🔍 Validating remaining route...")
        remaining_route = executor.route[executor.index:]
        result = self.validator.validate(remaining_route)

        if result.valid:
            print("✅ Remaining route: VALID")
        else:
            print(
                f"❌ Remaining route: INVALID "
                f"({result.reason.value} at {result.failing_position})"
            )

        return result


    def current_position_invalid(self, executor: MissionExecutor) -> bool:
        """Hard safety check: current voxel must be valid."""
        pos = executor.current_position()
        return self.env.is_constrained(pos)
