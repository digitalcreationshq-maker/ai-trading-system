# Validation Gates — v0.1.0

## Gate 0 — Requirements/account discovery
PASS requires 100% mandatory configuration fields, verified broker/account identity, terminal, enabled symbol specifications, no plaintext credentials, accurate equity/balance, known risk currency and broker permissions.

## Gate 1 — Data integrity
PASS requires ≥99.5% candle completeness, ≤0.01% duplicate candles, 0% invalid timestamps/prices, 100% symbol mapping, ≥99.9% required live-field presence and 100% stale/data-failure blocking tests.

## Gate 2 — Historical evidence
PASS requires ≥5 market regimes, ≥3 major volatility conditions, Gate 1 quality, no look-ahead leakage, versioned dataset/date range and documented missing periods.

## Gate 3 — Baseline strategy
PASS requires ≥300 research trades where practical, positive expectancy after costs, PF ≥1.20, max drawdown ≤20%, no month >25% of total net profit, no instrument >60% of strategy profit, no trade >10% of total net profit, and measured losing streak/risk of ruin.

## Gate 4 — Regime engine
Deterministic reproduction; OOS accuracy/F1 ≥70% where ground truth exists; no future data; UNCERTAIN state; safe fallback.

## Gate 5 — Signal engine
100% required fields; 0% future information; 0% duplicate signals; explicit invalidation; valid SL for live-eligible signals; mandatory risk prerequisites enforced; deterministic replay.

## Gate 6 — Trade scoring
Score strictly 0–100; missing critical features cannot improve score; ≥99.9% reproducibility; threshold tests; below threshold = NO TRADE; autonomous-live below 80 = NO AUTONOMOUS TRADE.

## Gate 7 — Risk engine
100% deliberate hard-limit rejection, invalid-size rejection, insufficient-margin rejection, stale-data rejection, kill-switch blocking and duplicate prevention. Risk calculation error ≤0.1% versus an independent reference. No loss-driven risk increase. Any failed safety test = FAIL.

## Gate 8 — Backtesting
Realistic costs, documented slippage, IS/OOS separation, OOS ≥30% where practical, ≥5 walk-forward windows, ≥1,000 Monte Carlo simulations, robustness ≥70%, OOS PF ≥1.10, positive OOS expectancy after costs and no catastrophic drawdown.

## Gate 9 — MT4/MT5 execution
100% broker-constraint tests; invalid lot/SL/TP rejection; duplicate prevention; kill-switch blocking; ≥99.99% reconciliation; unique idempotency keys; deterministic partial fills; terminal restart recovery.

## Gate 10 — Demo/forward
≥500 qualifying signals or 8 continuous weeks, with 0 risk violations, 0 duplicate orders, 0 kill-switch failures, 0 unauthorised live orders, defensible expectancy, execution error ≤0.5%, critical software failure ≤1/1000 decisions and no risk-limit breach.

## Gate 11 — AI/ML adaptation
OOS improvement must be economically/statistically meaningful; expectancy improvement ≥10% versus baseline without material drawdown increase; multi-regime evidence; drift monitoring, versioning, rollback and reproducibility.

## Gate 12 — Academy
Every live/demo strategy must be explainable; trades can become case studies; curriculum separates fact, evidence, inference and uncertainty; no guaranteed-profit claims.

## Gate 13 — Dashboard
All mandatory modules load; research/simulation/demo/live states are distinct; risk and kill switch are visible; connection/status is explicit.

## Verdict

A build is either PASS or BLOCKED. Untested live capability must never be presented as ready.
