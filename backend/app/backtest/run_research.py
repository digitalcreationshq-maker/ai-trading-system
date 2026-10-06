import hashlib
import json
import sys
from pathlib import Path

from app.backtest.dukascopy import read_dukascopy_csv
from app.backtest.engine import run_backtest
from app.backtest.models import BacktestConfig, CostModel, DatasetManifest
from app.backtest.validation import monte_carlo
from app.data.quality import validate_candles


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
            reports.append({"symbol": symbol, "dataset": dataset, "quality": quality.__dict__, "status": "BLOCKED"})
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
        report = run_backtest(
            candles,
            manifest,
            config=BacktestConfig(
                initial_equity=10000.0,
                risk_per_trade_pct=0.5,
                max_bars_in_trade=96,
                point_value=1.0,
            ),
            costs=CostModel(
                spread_price=0.00005,
                slippage_price=0.00002,
                commission_per_unit=0.0,
            ),
        )
        mc = monte_carlo(list(report.trades), simulations=1000, seed=42)
        reports.append({
            "symbol": symbol,
            "dataset": dataset,
            "quality": quality.__dict__,
            "backtest": {
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
            },
            "monte_carlo": mc.__dict__,
            "status": "RESEARCH_RESULT",
        })

    summary = {
        "status": "COMPLETED",
        "dataset_count": len(reports),
        "symbols": [item["symbol"] for item in reports],
        "blocked_symbols": [item["symbol"] for item in reports if item["status"] == "BLOCKED"],
        "results": reports,
    }
    Path("research-report.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
