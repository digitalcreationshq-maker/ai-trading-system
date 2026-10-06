from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo


DUKASCOPY_TZ = ZoneInfo("Europe/Zurich")
FX_SYMBOLS = {"EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD"}
DAILY_BREAK_SYMBOLS = {"XAUUSD", "XAGUSD"}


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


def _is_expected_h1_timestamp(timestamp: datetime, symbol: str) -> bool:
    """Return whether Dukascopy should normally have an H1 bar at this UTC timestamp.

    Dukascopy documents FX as 24/5, opening Sunday at 21:00 GMT in summer /
    22:00 GMT in winter and closing Friday at the same time. XAU/XAG have the
    same weekly session plus a daily one-hour trading break.
    """
    if timestamp.tzinfo is None:
        return False

    local = timestamp.astimezone(DUKASCOPY_TZ)
    weekday = local.weekday()
    hour = local.hour

    if weekday == 5:  # Saturday
        return False
    if weekday == 6:  # Sunday: session starts at 23:00 Zurich time.
        return hour >= 23
    if weekday == 4:  # Friday: session ends at 23:00 Zurich time.
        return hour < 23

    if symbol.upper() in DAILY_BREAK_SYMBOLS and hour == 23:
        return False

    return True


def _expected_h1_timestamps(rows: list[Candle], symbol: str) -> list[datetime]:
    if not rows:
        return []

    start = rows[0].timestamp
    end = rows[-1].timestamp
    if start.tzinfo is None or end.tzinfo is None:
        return []

    cursor = start.replace(minute=0, second=0, microsecond=0)
    end_hour = end.replace(minute=0, second=0, microsecond=0)
    expected: list[datetime] = []
    while cursor <= end_hour:
        if _is_expected_h1_timestamp(cursor, symbol):
            expected.append(cursor)
        cursor += timedelta(hours=1)
    return expected


def _infer_expected_h1_count(rows: list[Candle]) -> int:
    """Infer session-aware H1 expectation from the row symbol."""
    if not rows:
        return 0
    return len(_expected_h1_timestamps(rows, rows[0].symbol))


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

    if timeframe_minutes == 60 and rows and rows[0].timestamp.tzinfo is not None:
        expected_timestamps = _expected_h1_timestamps(rows, rows[0].symbol)
        inferred_expected = len(expected_timestamps)
        expected_set = set(expected_timestamps)
        observed_set = {c.timestamp for c in rows}
        missing_expected = sorted(expected_set - observed_set)
        gap_count = 0
        largest_gap_minutes = 0
        if missing_expected:
            previous = None
            for missing in missing_expected:
                if previous is None or missing - previous > timedelta(hours=1):
                    gap_count += 1
                previous = missing
            largest_gap_minutes = len(missing_expected) * timeframe_minutes
    else:
        inferred_expected = len(rows)
        missing_expected = []
        gap_count = 0
        largest_gap_minutes = 0

    effective_expected = expected_count if expected_count is not None else inferred_expected
    completeness_pct = (
        (len(rows) / effective_expected * 100) if effective_expected else 0.0
    )

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
