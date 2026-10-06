from collections import deque
from dataclasses import dataclass

from app.data.quality import Candle
from app.strategy.models import MarketSnapshot

@dataclass(frozen=True)
class FeatureConfig:
    atr_period: int = 14
    trend_period: int = 20
    momentum_period: int = 10

def build_snapshots(candles: list[Candle], config: FeatureConfig = FeatureConfig()) -> list[MarketSnapshot]:
    if config.atr_period < 2 or config.trend_period < 2 or config.momentum_period < 1:
        raise ValueError("Feature periods must be positive")
    ordered = sorted(candles, key=lambda c: c.timestamp)
    closes: deque[float] = deque(maxlen=max(config.trend_period, config.momentum_period) + 1)
    trs: deque[float] = deque(maxlen=config.atr_period)
    out: list[MarketSnapshot] = []
    previous_close = None
    for c in ordered:
        tr = max(c.high-c.low, abs(c.high-previous_close), abs(c.low-previous_close)) if previous_close is not None else c.high-c.low
        trs.append(tr)
        closes.append(c.close)
        previous_close = c.close
        if len(trs) < config.atr_period or len(closes) < config.trend_period + 1:
            continue
        vals = list(closes)
        atr = sum(trs) / len(trs)
        base = vals[-config.trend_period-1]
        trend = max(-100.0, min(100.0, ((c.close/base)-1.0)*1000.0))
        momentum_base = vals[-config.momentum_period-1] if len(vals) > config.momentum_period else base
        momentum = max(-100.0, min(100.0, ((c.close/momentum_base)-1.0)*1000.0))
        atr_pct = atr/c.close*100.0
        volatility = max(0.0, min(100.0, atr_pct*50.0))
        structure = max(0.0, min(100.0, 50.0+trend/2.0))
        out.append(MarketSnapshot(c.symbol, c.timestamp, c.close, atr, atr_pct, 0.0, _session(c.timestamp.hour), trend, momentum, structure, volatility, "UNCERTAIN"))
    return out

def _session(hour: int) -> str:
    if 7 <= hour < 12:
        return "LONDON"
    if 12 <= hour < 17:
        return "NEW_YORK"
    if hour >= 22 or hour < 7:
        return "ASIA"
    return "OVERLAP"
