from app.execution.models import ExecutionRequest
from app.execution.safety import block_execution


def request(platform: str) -> ExecutionRequest:
    return ExecutionRequest(
        request_id="req-1",
        platform=platform,  # type: ignore[arg-type]
        symbol="EURUSD",
        side="BUY",
        volume=0.01,
        entry=1.1,
        stop_loss=1.09,
        take_profit=1.12,
        risk_pct=0.5,
        idempotency_key="idem-1",
    )


def test_mt4_execution_is_blocked_by_default() -> None:
    result = block_execution(request("MT4"), "execution not authorized")
    assert result.accepted is False
    assert result.status == "BLOCKED"


def test_mt5_execution_is_blocked_by_default() -> None:
    result = block_execution(request("MT5"), "execution not authorized")
    assert result.accepted is False
    assert result.status == "BLOCKED"
