# Phase 2 — Broker Discovery & Market Data Foundation

## Objective

Establish a read-only account/broker discovery boundary and deterministic market-data quality checks before any strategy or execution work.

## Deliverables

- Read-only broker/account discovery protocol.
- Broker symbol specification validation.
- Data-quality validator.
- Basic health endpoints.
- Automated tests.
- No broker order API.

## Safety boundary

This phase cannot place, modify, or close broker orders. A broker connection is not treated as trading authorization.

## Gate for progression

The phase remains BLOCKED if required account/symbol specifications cannot be verified or if data-quality controls do not meet the thresholds defined in GATE_SPEC.md.
