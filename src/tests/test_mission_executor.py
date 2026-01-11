from src.execution.mission_executor import MissionExecutor
from src.execution.execution_state import MissionStatus


def test_mission_execution():
    route = [(0, 0), (0, 1), (0, 2)]

    executor = MissionExecutor(route)

    # Initial state
    assert executor.status == MissionStatus.RUNNING
    assert executor.current_position() == (0, 0)

    # Step 1
    executor.step()
    assert executor.current_position() == (0, 1)
    assert executor.status == MissionStatus.RUNNING

    # Step 2
    executor.step()
    assert executor.current_position() == (0, 2)
    assert executor.status == MissionStatus.RUNNING

    # Final step completes mission
    executor.step()
    assert executor.status == MissionStatus.COMPLETED


def test_mission_abort():
    route = [(1, 1), (1, 2)]

    executor = MissionExecutor(route)
    executor.abort()

    assert executor.status == MissionStatus.ABORTED

    # Stepping after abort does nothing
    executor.step()
    assert executor.status == MissionStatus.ABORTED


def test_empty_route_rejected():
    try:
        MissionExecutor([])
        assert False, "Expected ValueError for empty route"
    except ValueError:
        pass
