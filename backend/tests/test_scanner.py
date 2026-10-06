from datetime import datetime, timezone

from app.scanner.scanner import MarketScanner
from app.strategy.models import MarketSnapshot
from app.strategy.signal_engine import SignalEngine


def snap(symbol="EURUSD"):
    return MarketSnapshot(
        symbol=symbol,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        close=1.1,
        atr=0.01,
        atr_pct=1.0,
        spread_points=10,
        session="LONDON",
        trend_score=90,
        momentum_score=80,
        structure_score=90,
        volatility_score=80,
        regime="TREND",
    )


def test_scanner_deduplicates_signal_ids():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = MarketScanner(SignalEngine()).scan([snap(), snap()], now)
    assert result.scanned == 2
    assert len(result.signals) == 1
