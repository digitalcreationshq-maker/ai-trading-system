from datetime import timedelta

from .models import MarketSnapshot, Signal
from .regime import classify_regime
from .scoring import score_setup


class SignalEngine:
    """Deterministic signal generator. It never sends broker orders."""

    def __init__(
        self,
        *,
        strategy_version: str = "baseline-v1",
        min_score: int = 70,
        min_rr: float = 1.5,
        signal_ttl_minutes: int = 15,
    ) -> None:
        self.strategy_version = strategy_version
        self.min_score = min_score
        self.min_rr = min_rr
        self.signal_ttl_minutes = signal_ttl_minutes

    def generate(self, snapshot: MarketSnapshot) -> Signal | None:
        if snapshot.close <= 0 or snapshot.atr <= 0:
            return None
        if snapshot.spread_points < 0:
            return None
        # An upstream snapshot explicitly marked UNCERTAIN is a hard
        # no-trade state; it must not be silently replaced by a fresh
        # classification from the same feature set.
        if snapshot.regime == "UNCERTAIN":
            return None

        regime_result = classify_regime(snapshot)
        regime = regime_result.regime
        if regime == "UNCERTAIN":
            return None

        side = (
            "BUY"
            if snapshot.trend_score > 0 and snapshot.momentum_score > 0
            else "SELL"
        )
        score = score_setup(snapshot, side)

        if score.score < self.min_score:
            return None

        risk_distance = snapshot.atr
        reward_multiple = max(self.min_rr, 1.5)
        reward_distance = risk_distance * reward_multiple

        if side == "BUY":
            stop = snapshot.close - risk_distance
            target = snapshot.close + reward_distance
        else:
            stop = snapshot.close + risk_distance
            target = snapshot.close - reward_distance

        denominator = abs(snapshot.close - stop)
        if denominator <= 0:
            return None

        # The target and stop are constructed from the same risk distance,
        # so calculate R:R from those distances rather than introducing
        # avoidable floating-point cancellation.
        rr = reward_distance / risk_distance
        if rr + 1e-9 < self.min_rr:
            return None

        created = snapshot.timestamp
        expires = created + timedelta(minutes=self.signal_ttl_minutes)
        signal_id = (
            f"{self.strategy_version}:{snapshot.symbol}:{created.isoformat()}:"
            f"{side}:{snapshot.close:.10f}"
        )

        rationale = (
            *score.reasons,
            f"REGIME={regime}",
            f"REGIME_CONFIDENCE={regime_result.confidence:.3f}",
            *regime_result.rationale,
        )

        return Signal(
            signal_id=signal_id,
            strategy_version=self.strategy_version,
            symbol=snapshot.symbol,
            side=side,
            created_at=created,
            expires_at=expires,
            entry=snapshot.close,
            stop_loss=stop,
            take_profit=target,
            risk_reward=rr,
            score=score.score,
            regime=regime,
            rationale=rationale,
        )
