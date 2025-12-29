from enum import Enum


class MissionStatus(Enum):
    # Mission is currently executing
    RUNNING = "running"

    # Mission reached the final waypoint
    COMPLETED = "completed"

    # Mission was terminated before completion
    ABORTED = "aborted"
