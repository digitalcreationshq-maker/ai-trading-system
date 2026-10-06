from datetime import datetime, timezone

from app.strategy.models import MarketSnapshot
from app.strategy.scoring import score_setup


def snap(**overrides):
    values = dict(
        symbol="EURUSD",
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
    values.update(overrides)
    return MarketSnapshot(**values)


def test_score_is_bounded():
    result = score_setup(snap(), "BUY")
    assert 0 <= result.score <= 100


def test_buy_and_sell_direction_changes_trend_momentum():
    buy = score_setup(snap(), "BUY").score
    sell = score_setup(snap(), "SELL").score
    assert buy > sell
