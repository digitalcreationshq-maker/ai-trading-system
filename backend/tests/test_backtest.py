from datetime import datetime, timedelta, timezone

from app.backtest.engine import run_backtest
from app.backtest.models import BacktestConfig, CostModel, DatasetManifest
from app.backtest.features import build_snapshots
from app.data.quality import Candle, validate_candles


def make_candle(ts, close, symbol="EURUSD"):
    return Candle(
        symbol=symbol,
        timestamp=ts,
        open=close - 0.001,
        high=close + 0.006,
        low=close - 0.006,
        close=close,
        volume=100,
    )


def test_session_aware_quality_does_not_count_weekend_as_missing():
    start = datetime(2026, 1, 2, 20, tzinfo=timezone.utc)  # Friday
    rows = [
        make_candle(start, 1.10),
        make_candle(start + timedelta(hours=1), 1.101),
        make_candle(datetime(2026, 1, 4, 22, tzinfo=timezone.utc), 1.102),
        make_candle(datetime(2026, 1, 4, 23, tzinfo=timezone.utc), 1.103),
    ]
    report = validate_candles(rows, mapped_symbols={"EURUSD"}, timeframe_minutes=60)
    assert report.gap_count == 0



def test_session_calendar_follows_us_dst_not_europe_dst():
    # 2026-03-20 is after US DST begins but before European DST begins.
    # Dukascopy therefore settles at 21:00 UTC; 21:00 Friday is closed.
    rows = [
        make_candle(datetime(2026, 3, 20, 20, tzinfo=timezone.utc), 1.10),
        make_candle(datetime(2026, 3, 22, 21, tzinfo=timezone.utc), 1.101),
    ]
    report = validate_candles(rows, mapped_symbols={"EURUSD"}, timeframe_minutes=60)
    assert report.gap_count == 0
    assert report.expected_count == 2

def test_genuine_intraday_missing_h1_bar_is_detected():
    rows = [
        make_candle(datetime(2026, 1, 5, hour, tzinfo=timezone.utc), 1.10 + hour * 0.001)
        for hour in (0, 1, 3, 4)
    ]
    report = validate_candles(rows, mapped_symbols={"EURUSD"}, timeframe_minutes=60)
    assert report.gap_count == 1
    assert report.expected_count == 5
    assert report.completeness_pct < 99.5


def test_backtest_features_produce_deterministic_regimes_and_trades():
    start = datetime(2026, 1, 5, tzinfo=timezone.utc)
    candles = []
    price = 1.10
    for i in range(120):
        price += 0.006
        candles.append(make_candle(start + timedelta(hours=i), price))

    snapshots = build_snapshots(candles)
    assert snapshots
    assert any(snapshot.regime != "UNCERTAIN" for snapshot in snapshots)

    manifest = DatasetManifest(
        dataset_id="EURUSD:H1:test",
        version="test",
        symbol="EURUSD",
        timeframe="H1",
        start=candles[0].timestamp,
        end=candles[-1].timestamp,
        candle_count=len(candles),
        sha256="test",
        source="unit-test",
    )
    report = run_backtest(
        candles,
        manifest,
        config=BacktestConfig(initial_equity=10_000, risk_per_trade_pct=0.5),
        costs=CostModel(),
    )
    assert report.trade_count > 0
    assert report.lookahead_violations == 0


def test_financing_cost_is_applied():
    start = datetime(2026, 1, 5, tzinfo=timezone.utc)
    candles = []
    price = 1.10
    for i in range(120):
        price += 0.002
        candles.append(make_candle(start + timedelta(hours=i), price))

    manifest = DatasetManifest(
        dataset_id="EURUSD:H1:financing",
        version="test",
        symbol="EURUSD",
        timeframe="H1",
        start=candles[0].timestamp,
        end=candles[-1].timestamp,
        candle_count=len(candles),
        sha256="test",
        source="unit-test",
    )
    free = run_backtest(candles, manifest, costs=CostModel())
    financed = run_backtest(
        candles,
        manifest,
        costs=CostModel(financing_per_bar_per_unit=0.000001),
    )
    assert financed.final_equity < free.final_equity
