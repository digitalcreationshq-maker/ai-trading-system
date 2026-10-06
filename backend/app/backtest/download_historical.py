#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
import time
from pathlib import Path

SYMBOLS = ["eurusd", "gbpusd", "usdjpy", "usdchf", "audusd", "nzdusd", "usdcad", "xauusd"]
FROM = "2018-01-01"
TO = "2026-10-01"
OUT = Path("research-data")
MAX_ATTEMPTS = 8
INITIAL_BACKOFF = 20
MAX_BACKOFF = 180
BETWEEN_SYMBOLS = 20

def symbol_files(symbol: str) -> list[Path]:
    return sorted(OUT.glob(f"{symbol.upper()}-*.csv"))

def valid_output(symbol: str) -> list[Path]:
    return [p for p in symbol_files(symbol) if p.is_file() and p.stat().st_size > 0]

def run_download(symbol: str) -> tuple[int, str]:
    for path in symbol_files(symbol):
        path.unlink(missing_ok=True)
    cmd = [
        "npx", "--yes", "dukascopy-node", "-i", symbol, "-from", FROM, "-to", TO,
        "-t", "h1", "-f", "csv", "-v", "-dir", str(OUT),
        "--batch-size", "2", "--batch-pause", "10000", "--retries", "8",
        "--retry-pause", "10000", "--retry-on-empty",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    failures = 0
    for index, symbol in enumerate(SYMBOLS):
        print(f"=== Downloading {symbol.upper()} H1 {FROM} -> {TO} ===", flush=True)
        success = False
        last_output = ""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            code, output = run_download(symbol)
            last_output = output[-4000:]
            files = valid_output(symbol)
            if code == 0 and files:
                results[symbol.upper()] = {"status": "downloaded", "attempt": attempt, "files": [p.name for p in files], "bytes": sum(p.stat().st_size for p in files)}
                success = True
                print(f"{symbol.upper()}: download verified on attempt {attempt}", flush=True)
                break
            print(f"{symbol.upper()}: attempt {attempt}/{MAX_ATTEMPTS} failed (exit={code}, files={len(files)}).", flush=True)
            if attempt < MAX_ATTEMPTS:
                delay = min(INITIAL_BACKOFF * (2 ** (attempt - 1)), MAX_BACKOFF)
                print(f"Backing off for {delay}s before retrying {symbol.upper()}.", flush=True)
                time.sleep(delay)
        if not success:
            failures += 1
            results[symbol.upper()] = {"status": "failed", "attempts": MAX_ATTEMPTS, "last_output": last_output}
            print(f"{symbol.upper()}: PERMANENT DOWNLOAD FAILURE", flush=True)
        if index < len(SYMBOLS) - 1:
            time.sleep(BETWEEN_SYMBOLS)
    manifest = {
        "source": "Dukascopy public historical feed",
        "from": FROM,
        "to": TO,
        "timeframe": "H1",
        "expected_symbols": [s.upper() for s in SYMBOLS],
        "results": results,
        "download_failures": failures,
        "status": "COMPLETE" if failures == 0 else "INCOMPLETE",
    }
    Path("research-data/download-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    Path("research-data/download-failures.txt").write_text(
        "\n".join(f"{symbol}: {info.get('last_output', '')}" for symbol, info in results.items() if info["status"] == "failed") + "\n",
        encoding="utf-8",
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
