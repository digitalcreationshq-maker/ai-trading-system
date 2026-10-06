import hashlib
import json
import sys
from datetime import timedelta
from pathlib import Path

from app.backtest.dukascopy import read_dukascopy_csv
from app.backtest.engine import run_backtest
from app.backtest.models import BacktestConfig, CostModel, DatasetManifest
from app.backtest.validation import build_walk_forward_windows, monte_carlo
from app.data.quality import validate_candles


RISK_PCT = 0.5
INITIAL_EQUITY = 10_000.0
COSTS = CostModel(
    spread_price=0.00005,
    slippage_price=0.00002,
    commission_per_unit=0.0,
)
CONFIG = BacktestConfig(
    initial_equity=INITIAL_EQUITY,
    risk_per_trade_pct=RISK_PCT,
    max_bars_in_trade=96,
    point_value=1.0,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_report(candles, manifest):
    return run_backtest(candles, manifest, config=CONFIG, costs=COSTS)


def compact_report(report):
    return {
        "trade_count": report.trade_count,
        "net_profit": report.net_profit,
        "expectancy_r": report.expectancy_r,
        "profit_factor": report.profit_factor,
        "max_drawdown_pct": report.max_drawdown_pct,
        "win_rate_pct": report.win_rate_pct,
        "max_consecutive_losses": report.max_consecutive_losses,
        "monthly_profit_concentration_pct": report.monthly_profit_concentration_pct,
        "instrument_profit_concentration_pct": report.instrument_profit_concentration_pct,
        "largest_trade_profit_pct": report.largest_trade_profit_pct,
        "lookahead_violations": report.lookahead_violations,
    }


def slice_candles(candles, start, end):
    return [c for c in candles if start <= c.timestamp < end]


def evaluate_validation(candles, manifest):
    start = candles[0].timestamp
    end = candles[-1].timestamp
    span = end - start
    split = start + span * 0.70
    train = [c for c in candles if c.timestamp < split]
    test = [c for c in candles if c.timestamp >= split]

    is_report = run_report(train, manifest)
    oos_report = run_report(test, manifest)

    windows = build_walk_forward_windows(
        start,
        end,
        train_days=365,
        test_days=180,
        step_days=180,
    )
    wf = []
    for window in windows:
        train_rows = slice_candles(candles, window.train_start, window.train_end)
        test_rows = slice_candles(candles, window.test_start, window.test_end)
        if not train_rows or not test_rows:
            continue
        test_report = run_report(test_rows, manifest)
        wf.append({
            "train_start": window.train_start.isoformat(),
            "train_end": window.train_end.isoformat(),
            "test_start": window.test_start.isoformat(),
            "test_end": window.test_end.isoformat(),
            "train_trade_count": len(run_report(train_rows, manifest).trades),
            "test": compact_report(test_report),
        })

    positive_windows = sum(
        1 for window in wf
        if window["test"]["net_profit"] > 0
        and window["test"]["expectancy_r"] > 0
    )
    robustness_pct = positive_windows / len(wf) * 100.0 if wf else 0.0

    return {
        "in_sample": compact_report(is_report),
        "out_of_sample": compact_report(oos_report),
        "oos_trade_count": oos_report.trade_count,
        "walk_forward": {
            "window_count": len(wf),
            "windows": wf,
            "positive_oos_windows": positive_windows,
            "robustness_pct": robustness_pct,
        },
    }


def evaluate_gates(reports):
    quality_results = [r for r in reports if r["status"] != "BLOCKED"]
    gate1 = {
        "status": "PASS" if reports and not any(r["quality"]["passed"] is False for r in reports) else "BLOCKED",
        "criteria": {
            "all_datasets_pass_quality": not any(r["quality"]["passed"] is False for r in reports),
            "duplicate_rate_max_pct": 0.01,
            "completeness_min_pct": 99.5,
            "invalid_timestamps": 0,
            "invalid_prices": 0,
        },
    }

    baseline_pass = False
    gate3_results = []
    for r in quality_results:
        b = r["backtest"]
        checks = {
            "trade_count": b["trade_count"] >= 300,
            "positive_expectancy": b["expectancy_r"] > 0,
            "profit_factor": b["profit_factor"] >= 1.20,
            "max_drawdown": b["max_drawdown_pct"] <= 20.0,
            "monthly_concentration": b["monthly_profit_concentration_pct"] <= 25.0,
            "instrument_concentration": b["instrument_profit_concentration_pct"] <= 60.0,
            "largest_trade_concentration": b["largest_trade_profit_pct"] <= 10.0,
            "lookahead": b["lookahead_violations"] == 0,
        }
        gate3_results.append({"symbol": r["symbol"], "checks": checks})
        baseline_pass = baseline_pass or all(checks.values())
    gate3 = {"status": "PASS" if quality_results and baseline_pass else "BLOCKED", "results": gate3_results}

    gate8_results = []
    for r in quality_results:
        v = r.get("validation", {})
        oos = v.get("out_of_sample", {})
        wf = v.get("walk_forward", {})
        checks = {
            "oos_trade_count": v.get("oos_trade_count", 0) >= 100,
            "oos_positive_expectancy": oos.get("expectancy_r", 0) > 0,
            "oos_profit_factor": oos.get("profit_factor", 0) >= 1.10,
            "five_walk_forward_windows": wf.get("window_count", 0) >= 5,
            "robustness_pct": wf.get("robustness_pct", 0) >= 70.0,
            "monte_carlo_1000": r.get("monte_carlo", {}).get("simulations", 0) >= 1000,
            "lookahead": r["backtest"]["lookahead_violations"] == 0,
        }
        gate8_results.append({"symbol": r["symbol"], "checks": checks})
    gate8 = {
        "status": "PASS" if gate8_results and all(all(x["checks"].values()) for x in gate8_results) else "BLOCKED",
        "results": gate8_results,
    }

    overall = "PASS" if all(g["status"] == "PASS" for g in (gate1, gate3, gate8)) else "BLOCKED"
    return {
        "gate_1_data_integrity": gate1,
        "gate_3_baseline_strategy": gate3,
        "gate_8_backtesting_validation": gate8,
        "phase_4_verdict": overall,
    }


def main() -> int:
    root = Path(sys.argv[1])
    reports = []

    for path in sorted(root.glob("*.csv")):
        symbol = path.name.split("-")[0].upper()
        candles = read_dukascopy_csv(path, symbol=symbol)
        quality = validate_candles(candles, mapped_symbols={symbol}, timeframe_minutes=60)
        dataset = {
            "file": path.name,
            "sha256": sha256_file(path),
            "symbol": symbol,
            "timeframe": "H1",
            "start": candles[0].timestamp.isoformat() if candles else None,
            "end": candles[-1].timestamp.isoformat() if candles else None,
            "candle_count": len(candles),
        }
        if not quality.passed:
            reports.append({
                "symbol": symbol,
                "dataset": dataset,
                "quality": quality.__dict__,
                "status": "BLOCKED",
            })
            continue

        manifest = DatasetManifest(
            dataset_id=f"{symbol}:H1:dukascopy-2018-2026",
            version="dukascopy-2018-2026",
            symbol=symbol,
            timeframe="H1",
            start=candles[0].timestamp,
            end=candles[-1].timestamp,
            candle_count=len(candles),
            sha256=dataset["sha256"],
            source="Dukascopy public historical feed",
        )
        report = run_report(candles, manifest)
        mc = monte_carlo(list(report.trades), simulations=1000, seed=42)
        reports.append({
            "symbol": symbol,
            "dataset": dataset,
            "quality": quality.__dict__,
            "backtest": compact_report(report),
            "validation": evaluate_validation(candles, manifest),
            "monte_carlo": mc.__dict__,
            "status": "RESEARCH_RESULT",
        })

    summary = {
        "status": "COMPLETED",
        "dataset_count": len(reports),
        "symbols": [item["symbol"] for item in reports],
        "blocked_symbols": [item["symbol"] for item in reports if item["status"] == "BLOCKED"],
        "gates": evaluate_gates(reports),
        "results": reports,
    }
    Path("research-report.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "phase_4_verdict": summary["gates"]["phase_4_verdict"],
        "gate_1": summary["gates"]["gate_1_data_integrity"]["status"],
        "gate_3": summary["gates"]["gate_3_baseline_strategy"]["status"],
        "gate_8": summary["gates"]["gate_8_backtesting_validation"]["status"],
        "blocked_symbols": summary["blocked_symbols"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
