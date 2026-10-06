from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable


@dataclass(frozen=True)
class Candle:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class DataQualityReport:
    candle_count: int
    expected_count: int
    completeness_pct: float
    duplicate_pct: float
    invalid_price_count: int
    invalid_timestamp_count: int
    mapped_symbol_count: int
    required_live_fields_present_pct: float
    gap_count: int
    largest_gap_minutes: int
    passed: bool
    reasons: tuple[str, ...]


def _infer_expected_h1_count(rows: list[Candle]) -> int:
    """Infer an H1 expectation only when the sample spans at least one full day."""
    if not rows:
        return 0

    start = rows[0].timestamp
    end = rows[-1].timestamp

    if start.tzinfo is None or end.tzinfo is None:
        return len(rows)

    # A short sample has no reliable basis for inferring a full-day expectation.
    # Long historical datasets still receive the weekday-based completeness check.
    if end - start < timedelta(days=1):
        return len(rows)

    total = 0
    day = start.date()
    while day <= end.date():
        if day.weekday() < 5:
            total += 24
        day += timedelta(days=1)
    return total


def validate_candles(
    candles: Iterable[Candle],
    *,
    expected_count: int | None = None,
    mapped_symbols: set[str] | None = None,
    required_live_fields_present_pct: float = 100.0,
    timeframe_minutes: int = 60,
) -> DataQualityReport:
    rows = sorted(candles, key=lambda c: c.timestamp)
    reasons: list[str] = []
    invalid_prices = 0
    invalid_timestamps = 0

    for c in rows:
        if (
            min(c.open, c.high, c.low, c.close) <= 0
            or c.high < max(c.open, c.close)
            or c.low > min(c.open, c.close)
        ):
            invalid_prices += 1
        if c.timestamp.tzinfo is None:
            invalid_timestamps += 1

    keys = [(c.symbol, c.timestamp) for c in rows]
    duplicate_count = len(keys) - len(set(keys))
    duplicate_pct = (duplicate_count / len(rows) * 100) if rows else 100.0

    inferred_expected = (
        _infer_expected_h1_count(rows) if timeframe_minutes == 60 else len(rows)
    )
    effective_expected = (
        expected_count if expected_count is not None else inferred_expected
    )
    completeness_pct = (
        (len(rows) / effective_expected * 100) if effective_expected else 0.0
    )

    gap_count = 0
    largest_gap_minutes = 0
    if len(rows) > 1:
        for previous, current in zip(rows, rows[1:]):
            delta_minutes = int(
                (current.timestamp - previous.timestamp).total_seconds() / 60
            )
            if delta_minutes > timeframe_minutes:
                gap_count += 1
                largest_gap_minutes = max(largest_gap_minutes, delta_minutes)

    mapped_count = sum(
        1 for c in rows if mapped_symbols is None or c.symbol in mapped_symbols
    )

    if completeness_pct < 99.5:
        reasons.append("CANDLE_COMPLETENESS_BELOW_THRESHOLD")
    if duplicate_pct > 0.01:
        reasons.append("DUPLICATE_CANDLE_RATE_ABOVE_THRESHOLD")
    if invalid_prices:
        reasons.append("INVALID_PRICES")
    if invalid_timestamps:
        reasons.append("INVALID_TIMESTAMPS")
    if rows and mapped_count != len(rows):
        reasons.append("SYMBOL_MAPPING_INCOMPLETE")
    if required_live_fields_present_pct < 99.9:
        reasons.append("REQUIRED_LIVE_FIELDS_INCOMPLETE")

    return DataQualityReport(
        candle_count=len(rows),
        expected_count=effective_expected,
        completeness_pct=completeness_pct,
        duplicate_pct=duplicate_pct,
        invalid_price_count=invalid_prices,
        invalid_timestamp_count=invalid_timestamps,
        mapped_symbol_count=mapped_count,
        required_live_fields_present_pct=required_live_fields_present_pct,
        gap_count=gap_count,
        largest_gap_minutes=largest_gap_minutes,
        passed=not reasons,
        reasons=tuple(reasons),
    )
