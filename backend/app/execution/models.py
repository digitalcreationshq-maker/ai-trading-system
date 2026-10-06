from dataclasses import dataclass
from typing import Literal


Platform = Literal["MT4", "MT5"]


@dataclass(frozen=True)
class ExecutionRequest:
    request_id: str
    platform: Platform
    symbol: str
    side: Literal["BUY", "SELL"]
    volume: float
    entry: float
    stop_loss: float
    take_profit: float
    risk_pct: float
    idempotency_key: str


@dataclass(frozen=True)
class ExecutionResult:
    request_id: str
    platform: Platform
    accepted: bool
    status: Literal["BLOCKED", "AUTHORIZED", "SUBMITTED", "FILLED", "REJECTED"]
    broker_ticket: str | None
    reason: str


@dataclass(frozen=True)
class TerminalStatus:
    platform: Platform
    connected: bool
    trade_allowed: bool
    account_id: str | None
    broker_server: str | None
    terminal_version: str | None
