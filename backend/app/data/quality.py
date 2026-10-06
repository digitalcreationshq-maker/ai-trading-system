from dataclasses import dataclass
from datetime import datetime
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
    completeness_pct: float
    duplicate_pct: float
    invalid_price_count: int
    invalid_timestamp_count: int
    mapped_symbol_count: int
    required_live_fields_present_pct: float
    passed: bool
    reasons: tuple[str, ...]


def validate_candles(
    candles: Iterable[Candle],
    *,
    expected_count: int | None = None,
    mapped_symbols: set[str] | None = None,
    required_live_fields_present_pct: float = 100.0,
) -> DataQualityReport:
    rows = list(candles)
    reasons: list[str] = []
    invalid_prices = 0
    invalid_timestamps = 0

    for c in rows:
        if min(c.open, c.high, c.low, c.close) <= 0 or c.high < max(c.open, c.close) or c.low > min(c.open, c.close):
            invalid_prices += 1
        if c.timestamp.tzinfo is None:
            invalid_timestamps += 1

    keys = [(c.symbol, c.timestamp) for c in rows]
    duplicate_count = len(keys) - len(set(keys))
    duplicate_pct = (duplicate_count / len(rows) * 100) if rows else 100.0
    completeness_pct = 100.0 if expected_count in (None, 0) and rows else (
        len(rows) / expected_count * 100 if expected_count else 0.0
    )
    mapped_count = sum(1 for c in rows if mapped_symbols is None or c.symbol in mapped_symbols)

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
        completeness_pct=completeness_pct,
        duplicate_pct=duplicate_pct,
        invalid_price_count=invalid_prices,
        invalid_timestamp_count=invalid_timestamps,
        mapped_symbol_count=mapped_count,
        required_live_fields_present_pct=required_live_fields_present_pct,
        passed=not reasons,
        reasons=tuple(reasons),
    )
