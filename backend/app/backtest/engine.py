from collections import defaultdict

from app.data.quality import Candle
from app.strategy.signal_engine import SignalEngine

from .features import build_snapshots
from .models import BacktestConfig, BacktestReport, BacktestTrade, CostModel, DatasetManifest

def _tradable(candle: Candle) -> bool:
    return candle.volume > 0 or not (candle.open == candle.high == candle.low == candle.close)

def run_backtest(candles: list[Candle], manifest: DatasetManifest, *, config: BacktestConfig = BacktestConfig(), costs: CostModel = CostModel(), strategy: SignalEngine | None = None) -> BacktestReport:
    if config.initial_equity <= 0 or config.risk_per_trade_pct <= 0:
        raise ValueError("Backtest capital and risk must be positive")
    if not config.fill_on_next_bar_open:
        raise ValueError("Phase 4 requires next-bar-open fills to block same-bar look-ahead")
    strategy = strategy or SignalEngine()
    ordered = [c for c in sorted(candles, key=lambda c: c.timestamp) if _tradable(c)]
    if not ordered:
        raise ValueError("Backtest dataset contains no tradable candles")
    snapshots = build_snapshots(ordered)
    index_by_time = {c.timestamp: i for i, c in enumerate(ordered)}
    equity = config.initial_equity
    peak = equity
    max_dd = 0.0
    trades: list[BacktestTrade] = []
    lookahead_violations = 0
    cooldown_until = None

    for i, snapshot in enumerate(snapshots[:-1]):
        signal = strategy.generate(snapshot)
        if signal is None: continue
        next_i = index_by_time.get(snapshots[i + 1].timestamp)
        if next_i is None or ordered[next_i].timestamp <= signal.created_at:
            lookahead_violations += 1
            continue
        next_candle = ordered[next_i]
        if cooldown_until and next_candle.timestamp < cooldown_until: continue
        risk_distance = abs(signal.entry - signal.stop_loss)
        if risk_distance <= 0: continue
        risk_amount = equity * config.risk_per_trade_pct / 100.0
        direction = 1 if signal.side == "BUY" else -1
        entry = next_candle.open + direction * (costs.slippage_price + costs.spread_price / 2.0)
        stop = entry - direction * risk_distance
        target = entry + direction * risk_distance * signal.risk_reward
        quantity = risk_amount / (risk_distance * config.point_value)
        total_cost = (costs.commission_per_unit + costs.spread_price / 2.0 + costs.slippage_price) * quantity
        exit_price = next_candle.close
        exit_time = next_candle.timestamp
        exit_reason = "MAX_BARS"
        held_bars = 1
        end_i = min(len(ordered), next_i + config.max_bars_in_trade)
        for future in ordered[next_i:end_i]:
            if signal.side == "BUY": hit_stop, hit_target = future.low <= stop, future.high >= target
            else: hit_stop, hit_target = future.high >= stop, future.low <= target
            if hit_stop and hit_target:
                exit_price, exit_time, exit_reason = stop, future.timestamp, "STOP_FIRST_CONSERVATIVE"; break
            if hit_stop:
                exit_price, exit_time, exit_reason = stop, future.timestamp, "STOP"; break
            if hit_target:
                exit_price, exit_time, exit_reason = target, future.timestamp, "TARGET"; break
            exit_price, exit_time = future.close, future.timestamp
            held_bars += 1
        total_cost += costs.financing_per_bar_per_unit * quantity * held_bars
        gross_r = direction * (exit_price - entry) / risk_distance
        net_pnl = gross_r * risk_amount - total_cost
        net_r = net_pnl / risk_amount
        equity += net_pnl
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak - equity) / peak * 100.0 if peak else 0.0)
        trades.append(BacktestTrade(f"{signal.signal_id}:{exit_time.isoformat()}", signal.symbol, signal.side, signal.created_at, next_candle.timestamp, exit_time, entry, exit_price, stop, target, gross_r, total_cost, net_r, net_pnl, exit_reason))
        cooldown_until = exit_time

    wins = sum(t.net_pnl > 0 for t in trades)
    losses = sum(t.net_pnl < 0 for t in trades)
    breakeven = len(trades) - wins - losses
    gross_profit = sum(t.net_pnl for t in trades if t.net_pnl > 0)
    gross_loss = -sum(t.net_pnl for t in trades if t.net_pnl < 0)
    profit_factor = gross_profit / gross_loss if gross_loss else (float("inf") if gross_profit else 0.0)
    expectancy = sum(t.net_r for t in trades) / len(trades) if trades else 0.0
    month_profit = defaultdict(float)
    instrument_profit = defaultdict(float)
    for t in trades:
        month_profit[t.exit_time.strftime("%Y-%m")] += t.net_pnl
        instrument_profit[t.symbol] += t.net_pnl
    total_profit = sum(t.net_pnl for t in trades)
    concentration_base = total_profit if total_profit > 0 else 0.0
    return BacktestReport(manifest.dataset_id, strategy.strategy_version, config.initial_equity, equity, total_profit, expectancy, profit_factor, max_dd, wins/len(trades)*100.0 if trades else 0.0, len(trades), wins, losses, breakeven, _max_losing_streak(trades), max(month_profit.values(), default=0.0)/concentration_base*100.0 if concentration_base else 0.0, max(instrument_profit.values(), default=0.0)/concentration_base*100.0 if concentration_base else 0.0, max((t.net_pnl for t in trades), default=0.0)/concentration_base*100.0 if concentration_base else 0.0, lookahead_violations, tuple(trades))

def _max_losing_streak(trades: list[BacktestTrade]) -> int:
    best = current = 0
    for trade in trades:
        if trade.net_pnl < 0: current += 1; best = max(best, current)
        else: current = 0
    return best