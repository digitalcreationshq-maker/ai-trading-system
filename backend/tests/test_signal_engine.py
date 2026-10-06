from datetime import datetime, timezone

from app.strategy.models import MarketSnapshot
from app.strategy.signal_engine import SignalEngine


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


def test_qualifying_snapshot_creates_signal():
    signal = SignalEngine().generate(snap())
    assert signal is not None
    assert signal.score >= 70
    assert signal.risk_reward >= 1.5
    assert signal.stop_loss != signal.entry


def test_uncertain_regime_creates_no_signal():
    assert SignalEngine().generate(snap(regime="UNCERTAIN")) is None


def test_low_score_creates_no_signal():
    assert SignalEngine(min_score=90).generate(snap(structure_score=10)) is None


def test_signal_has_expiry_and_version():
    signal = SignalEngine().generate(snap())
    assert signal is not None
    assert signal.expires_at > signal.created_at
    assert signal.strategy_version == "baseline-v1"


def test_signal_id_is_deterministic():
    a = SignalEngine().generate(snap())
    b = SignalEngine().generate(snap())
    assert a is not None and b is not None
    assert a.signal_id == b.signal_id
