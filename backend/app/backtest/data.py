import csv
import hashlib
from datetime import datetime
from pathlib import Path

from app.data.quality import Candle
from .models import DatasetManifest

def load_ohlcv_csv(path: str | Path, *, symbol: str, timeframe: str, version: str, source: str = "csv") -> tuple[list[Candle], DatasetManifest]:
    p = Path(path)
    raw = p.read_bytes()
    rows: list[Candle] = []
    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"timestamp", "open", "high", "low", "close", "volume"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV columns: {sorted(missing)}")
        for row in reader:
            ts = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            rows.append(Candle(symbol, ts, float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]), float(row["volume"])))
    rows.sort(key=lambda c: c.timestamp)
    if not rows:
        raise ValueError("Historical dataset is empty")
    manifest = DatasetManifest(
        dataset_id=f"{symbol}:{timeframe}:{version}",
        version=version,
        symbol=symbol,
        timeframe=timeframe,
        start=rows[0].timestamp,
        end=rows[-1].timestamp,
        candle_count=len(rows),
        sha256=hashlib.sha256(raw).hexdigest(),
        source=source,
    )
    return rows, manifest
