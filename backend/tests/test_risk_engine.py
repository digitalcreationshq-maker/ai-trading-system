from datetime import datetime, timedelta, timezone

from app.risk.engine import RiskEngine
from app.risk.models import AccountSnapshot, TradeRequest


def account(**overrides):
    values = dict(
        equity=10000,
        balance=10000,
        daily_start_equity=10000,
        weekly_start_equity=10000,
        high_water_mark=10000,
        open_risk_pct=0,
        correlated_exposure_pct=0,
        trades_today=0,
        trades_this_week=0,
        consecutive_losses=0,
    )
    values.update(overrides)
    return AccountSnapshot(**values)


def trade(**overrides):
    now = datetime.now(timezone.utc)
    values = dict(
        symbol="EURUSD",
        side="BUY",
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        risk_pct=0.5,
        setup_score=85,
        data_timestamp=now,
        now=now,
        autonomous=False,
        idempotency_key="test-001",
        estimated_margin=100,
        available_margin=1000,
        correlated_risk_pct=0.0,
        contract_verified=True,
        position_size_valid=True,
    )
    values.update(overrides)
    return TradeRequest(**values)


def test_default_research_trade_is_blocked():
    decision = RiskEngine().evaluate(account(), trade())
    assert not decision.allowed
    assert "KILL_SWITCH_ACTIVE" in decision.reasons
    assert "ORDERS_DISABLED" in decision.reasons


def live_engine():
    return RiskEngine(kill_switch=False, orders_enabled=True)


def test_valid_trade_passes_hard_risk_gate():
    decision = live_engine().evaluate(account(), trade())
    assert decision.allowed


def test_excessive_risk_is_rejected():
    decision = live_engine().evaluate(account(), trade(risk_pct=1.1))
    assert not decision.allowed


def test_stale_data_is_rejected():
    now = datetime.now(timezone.utc)
    decision = live_engine().evaluate(
        account(), trade(now=now, data_timestamp=now - timedelta(seconds=61))
    )
    assert not decision.allowed


def test_low_score_is_rejected():
    decision = live_engine().evaluate(account(), trade(setup_score=69))
    assert not decision.allowed


def test_autonomous_threshold_is_80():
    decision = live_engine().evaluate(account(), trade(setup_score=79, autonomous=True))
    assert not decision.allowed


def test_low_rr_is_rejected():
    decision = live_engine().evaluate(account(), trade(take_profit=1.106))
    assert not decision.allowed


def test_duplicate_key_is_rejected():
    decision = live_engine().evaluate(account(), trade(idempotency_key=""))
    assert not decision.allowed


def test_daily_loss_is_rejected():
    decision = live_engine().evaluate(account(daily_start_equity=10000, equity=8000), trade())
    assert not decision.allowed


def test_loss_streak_is_rejected():
    decision = live_engine().evaluate(account(consecutive_losses=3), trade())
    assert not decision.allowed
