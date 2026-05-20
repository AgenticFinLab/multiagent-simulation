# Credit Cycle Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | Credit Cycle |
| Decision Mechanism | deterministic rule-based trading orders |
| Theory Reference | `examples/CreditCycle/simulation-bases.md` |
| Market Broadcast | `configs/CreditCycle/Rule/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 ProCyclicalLender (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `ProCyclicalLender` in `examples/CreditCycle/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/CreditCycle/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |
### §2.2 MinskyBorrower (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `MinskyBorrower` in `examples/CreditCycle/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/CreditCycle/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |
### §2.3 CounterCyclicalLender (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `CounterCyclicalLender` in `examples/CreditCycle/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/CreditCycle/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |
### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `ValueInvestor` in `examples/CreditCycle/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/CreditCycle/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `NoiseTrader` in `examples/CreditCycle/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/CreditCycle/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |

## §3 Market Mechanism

The coordinator mechanism is the final implementation in `examples/CreditCycle/Rule/players.py` and its configured counterpart in `configs/CreditCycle/Rule/players.yml`. It broadcasts scenario state each round, receives agent decisions, updates state variables, and records the series required by `analysis-bases.md`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/CreditCycle/Rule/players.py` |
| Prompt module | Not applicable for Rule baseline |
| Inference | No remote model call is used in the Rule baseline. |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/CreditCycle/Rule/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/CreditCycle/Rule/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/CreditCycle/Rule/topology.yml` | Message routing between coordinator and agents. |
| `configs/CreditCycle/Rule/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/CreditCycle/Rule/run_creditcycle.py -c configs/CreditCycle/Rule/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/CreditCycle/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/CreditCycle/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
