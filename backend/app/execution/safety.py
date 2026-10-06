from app.execution.models import ExecutionRequest, ExecutionResult


def block_execution(request: ExecutionRequest, reason: str) -> ExecutionResult:
    """Safe default: terminal adapters cannot execute until authorization is enabled."""
    return ExecutionResult(
        request_id=request.request_id,
        platform=request.platform,
        accepted=False,
        status="BLOCKED",
        broker_ticket=None,
        reason=reason,
    )
