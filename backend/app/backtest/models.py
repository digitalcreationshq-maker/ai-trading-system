from dataclasses import dataclass
from datetime import datetime
from typing import Literal

@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    version: str
    symbol: str
    timeframe: str
    start: datetime
    end: datetime
    candle_count: int
    sha256: str
    source: str
    missing_periods: tuple[str, ...] = ()

@dataclass(frozen=True)
class CostModel:
    spread_price: float = 0.0
    slippage_price: float = 0.0
    commission_per_unit: float = 0.0
    financing_per_bar_per_unit: float = 0.0

@dataclass(frozen=True)
class BacktestConfig:
    initial_equity: float = 10_000.0
    risk_per_trade_pct: float = 0.5
    max_bars_in_trade: int = 96
    point_value: float = 1.0
    fill_on_next_bar_open: bool = True

@dataclass(frozen=True)
class BacktestTrade:
    trade_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    signal_time: datetime
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    stop_loss: float
    take_profit: float
    gross_r: float
    costs: float
    net_r: float
    net_pnl: float
    exit_reason: str

@dataclass(frozen=True)
class BacktestReport:
    dataset_id: str
    strategy_version: str
    initial_equity: float
    final_equity: float
    net_profit: float
    expectancy_r: float
    profit_factor: float
    max_drawdown_pct: float
    win_rate_pct: float
    trade_count: int
    wins: int
    losses: int
    breakeven: int
    max_consecutive_losses: int
    monthly_profit_concentration_pct: float
    instrument_profit_concentration_pct: float
    largest_trade_profit_pct: float
    lookahead_violations: int
    trades: tuple[BacktestTrade, ...]

@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime

@dataclass(frozen=True)
class MonteCarloSummary:
    simulations: int
    seed: int
    probability_of_ruin_pct: float
    median_final_equity: float
    worst_final_equity: float
    median_max_drawdown_pct: float
    worst_max_drawdown_pct: float
