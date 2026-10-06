# Architecture — v0.1.0

## Control plane

Python 3.12+ is the quantitative/control layer. FastAPI exposes validated APIs. Pydantic v2 validates configuration and data. SQLAlchemy 2.x/Alembic target PostgreSQL 16+; TimescaleDB may be used for time-series data. Redis is transient state only.

## Execution boundary

Python Control Plane ↔ Secure Local/API Bridge ↔ MT5 Expert Advisor.

Python owns analysis, strategy, risk, authorization, state, journaling and analytics. The EA owns terminal-side execution and must independently reject invalid broker-side orders.

MT4 uses an equivalent MQL4 adapter where required; trading logic remains shared.

## Dashboard

Next.js + React + TypeScript. The frontend may display decisions and state but never independently determines whether a trade is permitted.

## Quant/research

NumPy, pandas, SciPy, scikit-learn and statsmodels are preferred. Backtests must be reproducible from versioned data, configuration and strategy versions.

## Initial build

This repository currently contains the safety foundation only. Broker order placement remains disabled until the specified validation gates are passed and explicit authorization controls are implemented.
