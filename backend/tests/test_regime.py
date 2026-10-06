from datetime import datetime, timezone

from app.strategy.models import MarketSnapshot
from app.strategy.regime import classify_regime


def snap(**overrides):
    values = dict(
        symbol="EURUSD",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        close=1.1,
        atr=0.01,
        atr_pct=1.0,
        spread_points=10,
        session="LONDON",
        trend_score=80,
        momentum_score=70,
        structure_score=80,
        volatility_score=70,
        regime="TREND",
    )
    values.update(overrides)
    return MarketSnapshot(**values)


def test_trend_regime():
    assert classify_regime(snap()).regime == "TREND"


def test_high_volatility_regime():
    assert classify_regime(snap(atr_pct=2.5)).regime == "HIGH_VOLATILITY"


def test_uncertain_when_inputs_are_invalid():
    assert classify_regime(snap(atr_pct=0)).regime == "UNCERTAIN"
