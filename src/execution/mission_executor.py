"""
Handles stepwise progression through a pre-approved route.
"""

from typing import List, Optional
from src.environment.grid import Position
from .execution_state import MissionStatus


class MissionExecutor:
    """
    Executes a mission route waypoint by waypoint.
    """

    def __init__(self, route: List[Position]):
        if route is None or len(route) == 0:
            raise ValueError("Cannot execute an empty route")

        self.route = route
        self.index = 0
        self.status = MissionStatus.RUNNING
        self.abort_reason: Optional[str] = None

    def current_position(self) -> Position:
        return self.route[self.index]

    def step(self) -> None:
        if self.status != MissionStatus.RUNNING:
            return

        if self.index == len(self.route) - 1:
            self.status = MissionStatus.COMPLETED
            return

        self.index += 1

    # -----------------------------
    # State transitions
    # -----------------------------

    def pause(self) -> None:
        if self.status == MissionStatus.RUNNING:
            self.status = MissionStatus.PAUSED
            print("⏸️ Execution paused")

    def resume(self) -> None:
        if self.status == MissionStatus.PAUSED:
            self.status = MissionStatus.RUNNING
            print("▶️ Execution resumed")

    def replace_route(self, new_route: List[Position]) -> None:
        if new_route is None or len(new_route) == 0:
            raise ValueError("Cannot replace with an empty route")

        self.route = new_route
        self.index = 0
        print("🛣️ Route replaced")

    def abort(self, reason: Optional[str] = None) -> None:
        self.status = MissionStatus.ABORTED
        self.abort_reason = reason
        print(f"🛑 Mission aborted: {reason}")
