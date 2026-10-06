# System Specification — v0.1.0

## Mission

Build a data-driven AI-assisted Forex and commodity trading system that optimises:

**SURVIVAL → CAPITAL PRESERVATION → CONSISTENCY → POSITIVE EXPECTANCY → CONTROLLED SCALING**

No profit, return, or winning-trade guarantee is permitted.

## First-build boundary

The first implementation is research/validation only. It must not place broker orders.

Required safety behaviour:
- unavailable or unreliable required data blocks a decision;
- stale live data blocks trading;
- hard risk controls cannot be overridden by AI;
- no martingale, loss-recovery sizing, revenge trading, automatic leverage increases, or silent live strategy changes;
- an independent kill switch blocks new orders.

## Initial universe

Forex: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, NZDUSD, USDCAD.

Commodities: XAUUSD, XAGUSD, WTI, Brent, subject to broker symbol validation.

## Authority

This specification is derived from the supplied trading-system master document. Where the master document is silent, implementation must stop or explicitly document the constraint rather than inventing a live-trading assumption.
