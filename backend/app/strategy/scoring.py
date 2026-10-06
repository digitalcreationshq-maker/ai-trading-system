from dataclasses import dataclass

from .models import MarketSnapshot, Side


@dataclass(frozen=True)
class ScoreResult:
    score: int
    components: tuple[tuple[str, int], ...]
    reasons: tuple[str, ...]


def score_setup(snapshot: MarketSnapshot, side: Side) -> ScoreResult:
    """Transparent 0-100 score. Missing critical inputs cannot improve a score."""
    direction = 1 if side == "BUY" else -1
    trend = max(0, min(100, int(50 + direction * snapshot.trend_score / 2)))
    momentum = max(0, min(100, int(50 + direction * snapshot.momentum_score / 2)))
    structure = max(0, min(100, int(snapshot.structure_score)))
    volatility = max(0, min(100, int(snapshot.volatility_score)))

    weighted = (
        0.35 * trend
        + 0.25 * momentum
        + 0.25 * structure
        + 0.15 * volatility
    )
    score = max(0, min(100, int(round(weighted))))

    reasons = (
        f"TREND_COMPONENT={trend}",
        f"MOMENTUM_COMPONENT={momentum}",
        f"STRUCTURE_COMPONENT={structure}",
        f"VOLATILITY_COMPONENT={volatility}",
    )
    return ScoreResult(
        score=score,
        components=(
            ("trend", trend),
            ("momentum", momentum),
            ("structure", structure),
            ("volatility", volatility),
        ),
        reasons=reasons,
    )
