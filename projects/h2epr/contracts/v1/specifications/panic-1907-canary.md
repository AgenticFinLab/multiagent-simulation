# H2EPR-0288 Rule canary

The first future canary uses the Panic of 1907 to prove an engineering loop:

```text
construction bundle -> participant artifacts -> runtime bundle
-> deterministic Rule interaction -> sealed trace -> Generated EPG
-> minimal offline structural/temporal alignment
```

Before implementation, the project owner must freeze `t0`, the participant
roster/aggregation decisions, the external construction anchor, and the chosen
tick-barrier/reducer contract. The canary policy is deterministic Rule only;
model, API, retrieval, and environment loading are disabled. Success is
defined by information-boundary enforcement, auditable dispositions and state
changes, deterministic replay, seal closure, and compiler traceability—not by
a high fidelity score.

A full-draft target demo may close the engineering loop quickly but remains
permanently demo-only. A later clean-prefix strict rerun is required for
continuation claims.

H2EPR-0616 then reuses the same contracts to test a network-security event. It
must work without treating price, cash, holdings, or orders as universal world
state. Failure of that gate blocks expansion to the remaining development
events.

