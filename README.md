# AI Trading System

Safety-first AI-assisted trading research and execution architecture for MT4/MT5.

## Safety mode

- orders_enabled=false
- kill_switch=true
- mode=research

Mission: survival -> capital preservation -> consistency -> positive expectancy -> controlled scaling.

## Current build stage

Phase 4 historical research is the active gate. The research workflow uses per-symbol historical acquisition with retry/backoff protection against provider rate limits, then runs data-quality, baseline, out-of-sample, walk-forward, and Monte Carlo evidence gates. Historical evidence remains BLOCKED until the machine-readable report proves `"phase_4_verdict": "PASS"`.

The dashboard must not be promoted ahead of the Phase 4 gate.

## Research data policy

Historical downloads are treated as external-source acquisition, not evidence by themselves. A download failure, missing symbol, incomplete dataset, or failed quality check blocks the corresponding Phase 4 evidence gate. No quality threshold is weakened to accommodate missing data.
