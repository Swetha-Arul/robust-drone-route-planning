"""
Handles stepwise progression through a pre-approved route.
"""

from typing import List
from src.environment.grid import Position
from .execution_state import MissionStatus


class MissionExecutor:
    def __init__(self, route: List[Position]):
        if route is None or len(route) == 0:
            raise ValueError("Cannot execute an empty route")

        self.route = route
        self.index = 0
        self.status = MissionStatus.RUNNING

    def current_position(self) -> Position:
        # Return the current waypoint
        return self.route[self.index]

    def step(self) -> None:
        """
        Moves to the next waypoint
        Marks mission as completed at the final waypoint
        """

        if self.status != MissionStatus.RUNNING:
            return

        # If already at the final waypoint, complete the mission
        if self.index == len(self.route) - 1:
            self.status = MissionStatus.COMPLETED
            return

        # Advance to next waypoint
        self.index += 1

    def abort(self, reason: str | None = None) -> None:
        """
        Abort the mission immediately.
        """
        self.status = MissionStatus.ABORTED
