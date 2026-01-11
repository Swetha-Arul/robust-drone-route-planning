"""
Binary recovery module.

Attempts replanning; if that fails, executes return-to-home.
"""

from typing import List, Optional

from src.environment.grid import Position
from src.planner.planner import GridPlanner
from src.execution.mission_executor import MissionExecutor
from src.execution.execution_state import MissionStatus


class Replanner:
    """
    Handles recovery when a route becomes invalid.
    """

    def __init__(self, planner: GridPlanner, home: Position):
        self.planner = planner
        self.home = home

    def replan_or_abort(
        self,
        executor: MissionExecutor,
        goal: Position,
    ) -> bool:

        if executor.status != MissionStatus.RUNNING:
            return False

        executor.pause()
        current_pos = executor.current_position()

        print("🔁 Attempting replanning to goal...")
        new_route: Optional[List[Position]] = self.planner.plan(
            current_pos, goal
        )

        if new_route:
            executor.replace_route(new_route)
            executor.resume()
            print("✅ Replanning successful")
            return True

        print("🏠 Replanning failed — attempting return-to-home")
        return_route: Optional[List[Position]] = self.planner.plan(
            current_pos, self.home
        )

        if return_route:
            executor.replace_route(return_route)
            executor.resume()
            print("↩️ Returning to home")
            return False

        executor.abort(reason="replanning_and_return_home_failed")
        return False
