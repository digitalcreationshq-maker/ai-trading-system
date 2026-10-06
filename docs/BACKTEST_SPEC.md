# Backtest Specification v0.1.0

## Required execution semantics
1. Sort historical data strictly by UTC timestamp.
2. Generate a signal only from information available at its signal timestamp.
3. Default fill is the next bar open with declared spread/slippage adjustments.
4. If stop and target are both touched inside one bar, assume the stop occurred first.
5. Every simulated trade has an immutable ID.
6. Costs are deducted from P&L and cannot be silently omitted.
7. Training and test windows are explicit; test observations cannot choose the training configuration.

## Leakage controls
The research pipeline must reject or flag non-monotonic timestamps, duplicated candles, future-dated feature joins, same-bar close-to-close fills, unversioned datasets, undocumented missing periods, and test observations used during model/parameter selection.

## Validation interpretation
Walk-forward testing strengthens temporal out-of-sample validation but does not repair contaminated source data or guarantee future performance. Historical backtesting is evidence for decision-making, not authorization for live money.
