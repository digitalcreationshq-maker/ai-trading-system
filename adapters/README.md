# MT4 / MT5 execution adapters

The repository uses one shared trading brain and two terminal-specific adapters.

- mt4/ contains the MQL4 Expert Advisor boundary.
- mt5/ contains the MQL5 Expert Advisor boundary.
- Python remains the owner of strategy, risk, authorization and audit state.
- Terminal adapters independently reject invalid or unauthorized execution requests.

## Mobile-first operation

The Android phone is the operator surface. It talks to the backend/mobile API; it does not run the MQL4/MQL5 EA.

A compatible desktop terminal environment (normally Windows PC/VPS) is required for an EA to execute. The phone can remain the primary monitoring and authorization device.

## Safety state

The initial adapters are connection/heartbeat and rejection infrastructure only:

- research mode
- orders disabled
- kill switch enabled
- live authorization disabled

No adapter in this initial implementation may place a broker order.
