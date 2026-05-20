# Short Squeeze Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | Short Squeeze |
| Decision Mechanism | deterministic rule-based trading orders |
| Theory Reference | `examples/ShortSqueeze/simulation-bases.md` |
| Market Broadcast | `configs/ShortSqueeze/Rule/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 ShortSeller (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `ShortSeller` in `examples/ShortSqueeze/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/ShortSqueeze/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |
### §2.2 MomentumBuyer (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `MomentumBuyer` in `examples/ShortSqueeze/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/ShortSqueeze/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |
### §2.3 RetailTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RetailTrader` in `examples/ShortSqueeze/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/ShortSqueeze/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |
### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `ValueInvestor` in `examples/ShortSqueeze/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/ShortSqueeze/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |
### §2.5 InstitutionalHolder (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `InstitutionalHolder` in `examples/ShortSqueeze/Rule/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/ShortSqueeze/Rule/players.yml` through `extras`. |
| Variant-specific decision mechanism | deterministic rule-based trading orders. |

## §3 Market Mechanism

The coordinator mechanism is the final implementation in `examples/ShortSqueeze/Rule/players.py` and its configured counterpart in `configs/ShortSqueeze/Rule/players.yml`. It broadcasts scenario state each round, receives agent decisions, updates state variables, and records the series required by `analysis-bases.md`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/ShortSqueeze/Rule/players.py` |
| Prompt module | Not applicable for Rule baseline |
| Inference | No remote model call is used in the Rule baseline. |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/ShortSqueeze/Rule/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/ShortSqueeze/Rule/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/ShortSqueeze/Rule/topology.yml` | Message routing between coordinator and agents. |
| `configs/ShortSqueeze/Rule/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/ShortSqueeze/Rule/run_short_squeeze.py -c configs/ShortSqueeze/Rule/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/ShortSqueeze/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/ShortSqueeze/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
