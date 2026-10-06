import random
from datetime import timedelta
from .models import BacktestTrade, MonteCarloSummary, WalkForwardWindow

def build_walk_forward_windows(start, end, *, train_days=365, test_days=90, step_days=90):
    if train_days <= 0 or test_days <= 0 or step_days <= 0:
        raise ValueError("Walk-forward periods must be positive")
    windows = []
    cursor = start
    while cursor + timedelta(days=train_days+test_days) <= end:
        train_end = cursor + timedelta(days=train_days)
        test_end = train_end + timedelta(days=test_days)
        windows.append(WalkForwardWindow(cursor, train_end, train_end, test_end))
        cursor += timedelta(days=step_days)
    return windows

def monte_carlo(trades: list[BacktestTrade], *, simulations=1000, seed=42, initial_equity=10000.0, risk_per_trade_pct=0.5):
    if simulations < 1:
        raise ValueError("simulations must be >= 1")
    if not trades:
        return MonteCarloSummary(simulations, seed, 100.0, initial_equity, initial_equity, 0.0, 0.0)
    rng = random.Random(seed)
    results = []
    risk = risk_per_trade_pct / 100.0
    for _ in range(simulations):
        shuffled = list(trades)
        rng.shuffle(shuffled)
        equity = initial_equity
        peak = equity
        max_dd = 0.0
        for trade in shuffled:
            equity += equity * risk * trade.net_r
            peak = max(peak, equity)
            max_dd = max(max_dd, (peak-equity)/peak*100.0 if peak else 0.0)
        results.append((equity, max_dd))
    finals = sorted(x[0] for x in results)
    dds = sorted(x[1] for x in results)
    ruin = sum(x <= initial_equity*0.5 for x in finals) / simulations * 100.0
    return MonteCarloSummary(simulations, seed, ruin, finals[len(finals)//2], finals[0], dds[len(dds)//2], dds[-1])
