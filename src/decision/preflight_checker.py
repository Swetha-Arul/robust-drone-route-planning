"""
Preflight decision module.

Decides whether a mission is allowed to start based on
route validity and simple mission constraints.
"""

from enum import Enum
from typing import Optional, List

from src.environment.grid import Position
from src.validation.route_validator import (
    RouteValidator,
    RouteValidationResult,
    RouteInvalidReason,
)


class PreflightDecision(Enum):
    # Final authorization outcome
    GO = "go"
    NO_GO = "no_go"


class PreflightRejectReason(Enum):
    # Reasons a mission can be rejected before execution
    NO_ROUTE = "no_route"
    INVALID_ROUTE = "invalid_route"
    COST_EXCEEDED = "cost_exceeded"


class PreflightResult:
    # Holds the outcome of a preflight check
    def __init__(
        self,
        decision: PreflightDecision,
        reason: Optional[PreflightRejectReason] = None,
        details: Optional[str] = None,
    ):
        self.decision = decision
        self.reason = reason
        self.details = details

    def approved(self) -> bool:
        # Convenience helper for GO / NO-GO checks
        return self.decision == PreflightDecision.GO

    def __repr__(self) -> str:
        # Readable output for logs and debugging
        if self.decision == PreflightDecision.GO:
            return "PreflightResult(decision=GO)"
        return (
            "PreflightResult("
            f"decision=NO_GO, reason={self.reason}, details={self.details})"
        )


class PreflightChecker:
    # Performs mission authorization before execution
    def __init__(
        self,
        validator: RouteValidator,
        max_route_length: int,
    ):
        self.validator = validator
        self.max_route_length = max_route_length

    def check(self, route: Optional[List[Position]]) -> PreflightResult:
        # Planner failed to produce any route
        if route is None or len(route) == 0:
            return PreflightResult(
                decision=PreflightDecision.NO_GO,
                reason=PreflightRejectReason.NO_ROUTE,
                details="Planner did not return a route",
            )

        # Validate route legality against environment constraints
        validation: RouteValidationResult = self.validator.validate(route)
        if not validation.valid:
            return PreflightResult(
                decision=PreflightDecision.NO_GO,
                reason=PreflightRejectReason.INVALID_ROUTE,
                details=f"{validation.reason} at {validation.failing_position}",
            )

        # Simple mission budget check using path length
        route_length = len(route) - 1
        if route_length >= self.max_route_length:
            return PreflightResult(
                decision=PreflightDecision.NO_GO,
                reason=PreflightRejectReason.COST_EXCEEDED,
                details=f"Route length {route_length} exceeds budget {self.max_route_length}",
            )

        # All preflight checks passed
        return PreflightResult(decision=PreflightDecision.GO)


