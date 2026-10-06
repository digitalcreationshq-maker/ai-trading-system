from dataclasses import dataclass

from .models import MarketSnapshot, Regime


@dataclass(frozen=True)
class RegimeResult:
    regime: Regime
    confidence: float
    rationale: tuple[str, ...]


def classify_regime(snapshot: MarketSnapshot) -> RegimeResult:
    """Deterministic, future-data-free regime classifier."""
    if snapshot.atr_pct <= 0:
        return RegimeResult("UNCERTAIN", 0.0, ("INVALID_VOLATILITY_INPUT",))

    if snapshot.atr_pct >= 2.0:
        return RegimeResult(
            "HIGH_VOLATILITY",
            min(1.0, snapshot.atr_pct / 4.0),
            ("ATR_PCT_ABOVE_HIGH_VOLATILITY_THRESHOLD",),
        )

    trend = abs(snapshot.trend_score)
    if trend >= 70:
        return RegimeResult(
            "TREND",
            min(1.0, trend / 100.0),
            ("TREND_SCORE_ABOVE_THRESHOLD",),
        )

    if trend <= 30:
        return RegimeResult(
            "RANGE",
            min(1.0, (100.0 - trend) / 100.0),
            ("TREND_SCORE_BELOW_RANGE_THRESHOLD",),
        )

    return RegimeResult("UNCERTAIN", 0.5, ("NO_CLEAR_REGIME",))
