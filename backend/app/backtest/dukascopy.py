import csv
from datetime import datetime, timezone
from pathlib import Path

from app.data.quality import Candle

def read_dukascopy_csv(path: str | Path, *, symbol: str) -> list[Candle]:
    p = Path(path)
    rows: list[Candle] = []
    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        ts_key = "timestamp" if "timestamp" in fields else "Date" if "Date" in fields else None
        if ts_key is None:
            raise ValueError("Dataset must contain timestamp or Date")
        required = {"Open", "High", "Low", "Close", "Volume"}
        if required.issubset(fields):
            keys = {"open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"}
        else:
            required = {"open","high","low","close","volume"}
            if not required.issubset(fields):
                raise ValueError("Dataset is missing OHLCV columns")
            keys = {k:k for k in required}
        for row in reader:
            raw_ts = row[ts_key]
            if raw_ts.isdigit():
                ts = datetime.fromtimestamp(int(raw_ts)/1000, tz=timezone.utc)
            else:
                ts = datetime.fromisoformat(raw_ts.replace("Z","+00:00"))
            rows.append(Candle(symbol, ts, float(row[keys["open"]]), float(row[keys["high"]]), float(row[keys["low"]]), float(row[keys["close"]]), float(row[keys["volume"]])))
    return sorted(rows, key=lambda c: c.timestamp)
