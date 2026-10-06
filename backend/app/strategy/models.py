from dataclasses import dataclass
from datetime import datetime
from typing import Literal


Regime = Literal["TREND", "RANGE", "HIGH_VOLATILITY", "LOW_VOLATILITY", "UNCERTAIN"]
Side = Literal["BUY", "SELL"]


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    timestamp: datetime
    close: float
    atr: float
    atr_pct: float
    spread_points: float
    session: str
    trend_score: float
    momentum_score: float
    structure_score: float
    volatility_score: float
    regime: Regime


@dataclass(frozen=True)
class Signal:
    signal_id: str
    strategy_version: str
    symbol: str
    side: Side
    created_at: datetime
    expires_at: datetime
    entry: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    score: int
    regime: Regime
    rationale: tuple[str, ...]
    valid: bool = True
    invalidation_reason: str | None = None
