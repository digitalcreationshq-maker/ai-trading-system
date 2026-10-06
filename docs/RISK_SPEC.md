# Risk Specification — v0.1.0

## Precedence

BROKER/ACCOUNT HARD CONSTRAINTS → SYSTEM HARD RISK LIMITS → PORTFOLIO RISK → RISK ENGINE → STRATEGY PREFERENCES → AI OPTIMISATION

A lower layer may tighten restrictions but may never loosen a higher layer.

## Defaults

| Control | Default |
|---|---:|
| Risk/trade | 0.5% equity |
| Absolute standard risk ceiling | 1.0% equity |
| Daily loss limit | 2.0% |
| Weekly loss limit | 5.0% |
| Max total open risk | 2.0% |
| Max correlated exposure | 1.0% |
| Consecutive-loss pause | 3 |
| Max trades/day | 5 |
| Max trades/week | 20 |
| Standard setup threshold | 70/100 |
| Autonomous-live threshold | 80/100 |
| Preferred minimum R:R | 1:2 |
| Absolute R:R floor | 1:1.5 |
| High-water-mark suspension | 10% |

These are controls, not performance targets.

## Position sizing

Position size is based on equity, permitted risk, entry, stop distance, verified contract specification, tick value and broker volume constraints. It is never calculated from desired profit.

If contract specifications cannot be verified: **POSITION SIZE UNVERIFIED — ORDER BLOCKED**.

## Implementation limits

The first implementation cannot risk above 1.0% on a standard trade, exceed 2.0% total open risk or 1.0% correlated exposure, increase risk after losses, automatically increase leverage, or override broker margin requirements.
