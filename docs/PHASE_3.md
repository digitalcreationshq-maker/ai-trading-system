# Phase 3 — Market Scanner & Deterministic Strategy Foundation

## Objective

Create a transparent, reproducible analysis layer that can scan the approved universe, classify basic market regime states, score setups from 0–100, and produce explicit trade plans without sending orders.

## Strategy boundary

This is a baseline research strategy, not a claim of profitability. It uses only information present in the supplied market snapshot; no future observations are accessed.

## Regime states

- TREND
- RANGE
- HIGH_VOLATILITY
- LOW_VOLATILITY
- UNCERTAIN

The current deterministic classifier deliberately falls back to UNCERTAIN when the supplied features do not support a clear classification.

## Score

The baseline score is bounded to 0–100:
- trend: 35%
- momentum: 25%
- structure: 25%
- volatility: 15%

Thresholds:
- standard setup: 70/100
- autonomous-live: 80/100

A score below the configured threshold produces NO TRADE.

## Signal contract

Every generated signal contains:
- deterministic signal ID
- strategy version
- symbol
- side
- timestamp and expiry
- entry
- stop loss
- take profit
- risk/reward
- score
- regime
- rationale

## Explicit limitations

This phase does not claim that the feature weights are optimal. It does not contain ML, fundamental-event ingestion, broker execution, or profit guarantees. Those require later validation and gates.

## Gate status

Gate 4–6 remain **BLOCKED** until the full data, out-of-sample, reproducibility, and risk-validation evidence specified in GATE_SPEC.md is produced.
