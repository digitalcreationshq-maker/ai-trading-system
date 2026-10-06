from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class AccountSnapshot:
    equity: float
    balance: float
    daily_start_equity: float
    weekly_start_equity: float
    high_water_mark: float
    open_risk_pct: float
    correlated_exposure_pct: float
    trades_today: int
    trades_this_week: int
    consecutive_losses: int


@dataclass(frozen=True)
class TradeRequest:
    symbol: str
    side: Literal["BUY", "SELL"]
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_pct: float
    setup_score: int
    data_timestamp: datetime
    now: datetime
    autonomous: bool = False
    idempotency_key: str = ""
    estimated_margin: float = 0.0
    available_margin: float = 0.0
    correlated_risk_pct: float = 0.0
    contract_verified: bool = False
    position_size_valid: bool = True


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reasons: tuple[str, ...]
