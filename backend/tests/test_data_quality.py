from datetime import datetime, timezone

from app.data.quality import Candle, validate_candles


def candle(symbol="EURUSD", minute=0):
    return Candle(
        symbol=symbol,
        timestamp=datetime(2026, 1, 1, 0, minute, tzinfo=timezone.utc),
        open=1.10,
        high=1.11,
        low=1.09,
        close=1.105,
        volume=100,
    )


def test_valid_data_passes():
    report = validate_candles([candle()], mapped_symbols={"EURUSD"})
    assert report.passed


def test_invalid_price_blocks():
    c = candle()
    bad = Candle(c.symbol, c.timestamp, 1.1, 1.0, 1.09, 1.105, 100)
    report = validate_candles([bad], mapped_symbols={"EURUSD"})
    assert not report.passed
    assert "INVALID_PRICES" in report.reasons


def test_duplicate_rate_is_detected():
    report = validate_candles([candle(), candle()], mapped_symbols={"EURUSD"})
    assert not report.passed
    assert "DUPLICATE_CANDLE_RATE_ABOVE_THRESHOLD" in report.reasons


def test_naive_timestamp_is_rejected():
    c = candle()
    bad = Candle(c.symbol, c.timestamp.replace(tzinfo=None), c.open, c.high, c.low, c.close, c.volume)
    report = validate_candles([bad], mapped_symbols={"EURUSD"})
    assert not report.passed
    assert "INVALID_TIMESTAMPS" in report.reasons


def test_missing_live_fields_block():
    report = validate_candles([candle()], mapped_symbols={"EURUSD"}, required_live_fields_present_pct=99.0)
    assert not report.passed
