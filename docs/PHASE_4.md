# Phase 4 — Historical Data and Backtesting v0.1.0

## Objective
Build deterministic research infrastructure for versioned historical OHLCV ingestion, causal feature construction, conservative historical simulation, explicit transaction costs, walk-forward windows, and Monte Carlo diagnostics. Broker orders remain disabled.

## Information-set discipline
A signal generated from bar t is not filled using that same bar's close. The baseline simulator fills at the next available bar open, then evaluates subsequent bars. This blocks the classic same-bar close/fill look-ahead error. Walk-forward test windows are strictly after their training windows. Look-ahead prevention is a core backtesting requirement. 

## Dataset controls
Every imported dataset receives a dataset ID, version, symbol, timeframe, UTC start/end, candle count, SHA-256 hash, and source label. Missing periods remain explicit metadata and must be documented before historical evidence is accepted.

The Dukascopy acquisition step requests flat zero-volume filler candles so scheduled non-trading periods remain auditable in the raw H1 dataset. Flat fillers are excluded from technical indicators and simulated execution; they must never create synthetic trades or distort volatility.

## Cost model
The simulator accepts spread, slippage, commission-per-unit, and financing assumptions. Costs are explicit inputs rather than hidden constants. Broker-specific production assumptions must later come from MT4/MT5 symbol and account discovery.

## Reported metrics
The backtest report records final equity, net profit, expectancy in R, profit factor, maximum drawdown, win rate, trade count, losing streak, monthly concentration, instrument concentration, largest-trade concentration, and look-ahead violations.

## Validation
Walk-forward window generation and deterministic Monte Carlo resampling are implemented. Monte Carlo currently reports a simple 50%-of-starting-equity ruin diagnostic; it is not a forecast or guarantee.

## Gates
Gate 2 requires diverse historical regimes, data quality, zero look-ahead leakage, versioned data, and documented missing periods. Gate 3 requires at least 300 research trades where practical, positive post-cost expectancy, PF >= 1.20, max drawdown <= 20%, concentration controls, and measured losing streak/risk of ruin.

Gate 8 later requires realistic costs, IS/OOS separation, OOS >= 30% where practical, at least five walk-forward windows, at least 1,000 Monte Carlo simulations, robustness >= 70%, OOS PF >= 1.10, positive OOS expectancy after costs, and no catastrophic drawdown.

Gate 3 concentration checks are evaluated at the combined research-universe level, not independently per symbol. A single-symbol report would otherwise make instrument concentration mechanically equal to 100%.

## Status
BLOCKED until real historical datasets are ingested, quality-checked, and the resulting evidence meets the required thresholds.
