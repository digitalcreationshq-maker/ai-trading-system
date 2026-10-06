from dataclasses import dataclass
from datetime import datetime

from app.strategy.models import MarketSnapshot, Signal
from app.strategy.signal_engine import SignalEngine


@dataclass(frozen=True)
class ScanResult:
    scanned: int
    signals: tuple[Signal, ...]
    rejected: int
    scanned_at: datetime


class MarketScanner:
    def __init__(self, signal_engine: SignalEngine) -> None:
        self.signal_engine = signal_engine

    def scan(self, snapshots: list[MarketSnapshot], scanned_at: datetime) -> ScanResult:
        signals: list[Signal] = []
        seen: set[str] = set()

        for snapshot in snapshots:
            signal = self.signal_engine.generate(snapshot)
            if signal is None or signal.signal_id in seen:
                continue
            seen.add(signal.signal_id)
            signals.append(signal)

        return ScanResult(
            scanned=len(snapshots),
            signals=tuple(signals),
            rejected=len(snapshots) - len(signals),
            scanned_at=scanned_at,
        )
