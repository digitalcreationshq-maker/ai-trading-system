from typing import Protocol

from app.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    Platform,
    TerminalStatus,
)


class ExecutionAdapter(Protocol):
    """Platform-neutral contract implemented by MT4 and MT5 adapters."""

    platform: Platform

    def status(self) -> TerminalStatus:
        ...

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        ...

    def reconcile(self) -> None:
        ...
