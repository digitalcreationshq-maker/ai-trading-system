# Architecture — v0.2.0

## Mission

The system is **mobile-first** and **dual-platform**: one shared Python trading/control plane can supervise MT4 and MT5 execution adapters while the operator uses an Android phone through a responsive web dashboard.

The phone is the control and observation surface. It is **not** the place where an MQL4/MQL5 Expert Advisor executes.

## System topology

```
Android phone
    |
    v
Mobile web dashboard
    |
    v
Secure API / authorization layer
    |
    v
Python control plane
    |
    +--> data / strategy / regime / scoring
    +--> risk / portfolio / journaling
    +--> authorization / kill switch
    |
    +--> MT4 execution adapter --> MQL4 EA --> MT4 terminal --> broker
    |
    +--> MT5 execution adapter --> MQL5 EA --> MT5 terminal --> broker
```

The core strategy and safety logic is shared. Only the terminal execution adapter is platform-specific.

## Control plane

Python 3.12+ is the quantitative/control layer. FastAPI exposes validated APIs. Pydantic v2 validates configuration and data. SQLAlchemy 2.x/Alembic target PostgreSQL 16+; TimescaleDB may be used for time-series data. Redis is transient state only.

Python owns:
- market-data normalization
- strategy and regime analysis
- signal scoring
- position sizing
- portfolio risk
- authorization
- state
- journaling
- analytics
- mobile API responses

The mobile UI never decides whether a trade is permitted.

## MT4 adapter

MT4 execution uses an MQL4 Expert Advisor as the terminal-side adapter. MT4 EAs are MQL4 programs loaded into the desktop client terminal and can perform automated trading when terminal auto-trading is enabled. The EA must independently enforce broker constraints and reject unsafe requests.

The adapter contract will cover:
- terminal/account identity
- symbol specification
- tick/quote data
- open positions and orders
- execution requests
- execution results
- reconciliation
- heartbeat
- idempotency
- kill-switch state

The MT4 adapter must never invent or loosen a risk decision produced by the control plane.

## MT5 adapter

MT5 execution uses an MQL5 Expert Advisor as the terminal-side adapter. The repository may additionally support the official MetaTrader5 Python package for read-only/account-data integration where appropriate, but the safety architecture treats terminal-side execution as an independent boundary.

The adapter contract will cover the same capabilities as MT4 so that the strategy engine remains platform-independent.

## Mobile operation

The mobile dashboard is the primary operator surface:
- account/terminal status
- signal review
- trade-plan details
- risk state
- open positions
- P/L and drawdown
- pause/resume controls
- kill switch
- authorization state
- audit log

The dashboard is responsive and designed for Android Chrome first.

A phone action is a **request**, not an unconditional broker command. The backend re-validates authorization, risk, broker constraints and idempotency before an execution request can cross the terminal boundary.

## Execution safety

Execution authority follows:

BROKER/ACCOUNT HARD CONSTRAINTS
-> SYSTEM HARD RISK LIMITS
-> PORTFOLIO RISK
-> RISK ENGINE
-> STRATEGY PREFERENCES
-> AI OPTIMISATION

Neither the mobile client, AI model, MT4 EA nor MT5 EA may loosen a higher-level constraint.

Initial execution remains disabled:
- research mode
- orders_enabled=false
- kill_switch=true
- explicit_live_authorization=false

The first terminal adapters are therefore intended for connection discovery, heartbeat, market/account synchronization and safe rejection behavior. Live order placement is a later gated capability.

## Deployment model

The mobile dashboard and Python API can run in a cloud environment. MT4/MT5 terminal execution requires a compatible desktop terminal environment, normally a Windows PC or Windows VPS. The operator does not need that machine physically present; the Android phone remains the control surface.

## Research and validation

Backtests must be reproducible from versioned data, configuration and strategy versions. Demo/forward execution must precede any live authorization.

## Initial build boundary

This repository is building the shared control plane and both execution-adapter contracts first. No real-money broker order placement is enabled by this architecture change.
