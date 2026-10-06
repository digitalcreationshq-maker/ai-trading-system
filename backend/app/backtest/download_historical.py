#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import time
from pathlib import Path

SYMBOLS = ["eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "nzdusd", "usdcad", "xauusd"]
FROM = "2018-01-01"
TO = "2026-10-01"
OUT = Path("research-data")
CACHE = OUT / ".dukascopy-cache"

MAX_ATTEMPTS = 5
INITIAL_BACKOFF = 30
MAX_BACKOFF = 180
BETWEEN_SYMBOLS = 15
BATCH_SIZE = 5
BATCH_PAUSE_MS = 3000
RETRY_COUNT = 4
RETRY_PAUSE_MS = 5000

def symbol_files(symbol: str) -> list[Path]:
    return sorted(OUT.glob(f"{symbol.upper()}-*.csv"))

def valid_output(symbol: str) -> list[Path]:
    valid: list[Path] = []
    for path in symbol_files(symbol):
        if not path.is_file() or path.stat().st_size <= 0:
            continue
        try:
            with path.open("r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                fields = set(reader.fieldnames or [])
                required = {"timestamp", "open", "high", "low", "close", "volume"}
                if not required.issubset(fields):
                    continue
                row_count = sum(1 for _ in reader)
                if row_count >= 1000:
                    valid.append(path)
        except (OSError, UnicodeError, csv.Error):
            continue
    return valid

def run_download(symbol: str) -> tuple[int, str]:
    for path in symbol_files(symbol):
        path.unlink(missing_ok=True)
    cmd = [
        "npx", "--yes", "dukascopy-node", "-i", symbol, "-from", FROM, "-to", TO,
        "-t", "h1", "-p", "bid", "-v", "--flats", "-f", "csv", "-dir", str(OUT),
        "--batch-size", str(BATCH_SIZE), "--batch-pause", str(BATCH_PAUSE_MS),
        "--cache", "--cache-path", str(CACHE), "--retries", str(RETRY_COUNT),
        "--retry-pause", str(RETRY_PAUSE_MS), "--retry-on-empty",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict] = {}
    failures = 0
    for index, symbol in enumerate(SYMBOLS):
        print(f"=== Downloading {symbol.upper()} H1 {FROM} -> {TO} ===", flush=True)
        success = False
        last_output = ""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            code, output = run_download(symbol)
            last_output = output[-5000:]
            files = valid_output(symbol)
            if code == 0 and files:
                results[symbol.upper()] = {
                    "status": "downloaded",
                    "attempt": attempt,
                    "files": [p.name for p in files],
                    "bytes": sum(p.stat().st_size for p in files),
                    "validated_files": len(files),
                }
                success = True
                print(f"{symbol.upper()}: verified {len(files)} CSV file(s) on attempt {attempt}", flush=True)
                break
            print(f"{symbol.upper()}: attempt {attempt}/{MAX_ATTEMPTS} failed (exit={code}, valid_files={len(files)}).", flush=True)
            if attempt < MAX_ATTEMPTS:
                delay = min(INITIAL_BACKOFF * (2 ** (attempt - 1)), MAX_BACKOFF)
                print(f"Backing off for {delay}s before retrying {symbol.upper()}.", flush=True)
                time.sleep(delay)
        if not success:
            failures += 1
            results[symbol.upper()] = {
                "status": "failed",
                "attempts": MAX_ATTEMPTS,
                "last_output": last_output,
            }
            print(f"{symbol.upper()}: PERMANENT DOWNLOAD FAILURE", flush=True)
        if index < len(SYMBOLS) - 1:
            time.sleep(BETWEEN_SYMBOLS)
    manifest = {
        "source": "Dukascopy public historical feed",
        "from": FROM,
        "to": TO,
        "timeframe": "H1",
        "price_type": "bid",
        "include_flats": True,
        "expected_symbols": [s.upper() for s in SYMBOLS],
        "results": results,
        "download_failures": failures,
        "status": "COMPLETE" if failures == 0 else "INCOMPLETE",
    }
    Path("research-data/download-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    Path("research-data/download-failures.txt").write_text("\n".join(
        f"{symbol}: {info.get('last_output', '')}"
        for symbol, info in results.items() if info["status"] == "failed"
    ) + "\n", encoding="utf-8")
    return 0 if failures == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())