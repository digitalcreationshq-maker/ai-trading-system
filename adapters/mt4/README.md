# MT4 adapter

The MT4 adapter will be an MQL4 Expert Advisor.

Responsibilities:
1. report terminal/account status;
2. expose broker symbol specifications;
3. synchronize quotes and positions;
4. receive only authenticated, validated execution requests;
5. independently enforce broker-side constraints;
6. report execution/reconciliation results.

The first implementation is read-only/safe-reject. Automated order placement remains disabled.
