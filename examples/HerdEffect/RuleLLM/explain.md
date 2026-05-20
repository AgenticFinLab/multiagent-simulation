# Herd Effect RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | Herd Effect |
| Decision Mechanism | LLM-generated trading orders constrained by explicit scenario rules |
| Theory Reference | `examples/HerdEffect/simulation-bases.md` |
| Market Broadcast | `configs/HerdEffect/RuleLLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 MomentumInvestor (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RuleLLMMomentumInvestor` in `examples/HerdEffect/RuleLLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdEffect/RuleLLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders constrained by explicit scenario rules. |
### §2.2 ContrarianInvestor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RuleLLMContrarianInvestor` in `examples/HerdEffect/RuleLLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdEffect/RuleLLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders constrained by explicit scenario rules. |
### §2.3 RiskAverseInvestor (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RuleLLMRiskAverseInvestor` in `examples/HerdEffect/RuleLLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdEffect/RuleLLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders constrained by explicit scenario rules. |
### §2.4 NoiseTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RuleLLMNoiseTrader` in `examples/HerdEffect/RuleLLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdEffect/RuleLLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders constrained by explicit scenario rules. |
### §2.5 AggressiveInvestor (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RuleLLMAggressiveInvestor` in `examples/HerdEffect/RuleLLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdEffect/RuleLLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders constrained by explicit scenario rules. |

## §3 Market Mechanism

The coordinator mechanism is the final implementation in `examples/HerdEffect/RuleLLM/players.py` and its configured counterpart in `configs/HerdEffect/RuleLLM/players.yml`. It broadcasts scenario state each round, receives agent decisions, updates state variables, and records the series required by `analysis-bases.md`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/HerdEffect/RuleLLM/players.py` |
| Prompt module | `examples/HerdEffect/RuleLLM/prompts.py` |
| Inference | Uses the project ARK LLM policy; RAG variants also use the project Hunyuan/LiteLLM embedding policy. |
| Output parsing | Explicit parser contract in players.py and prompts.py |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/HerdEffect/RuleLLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/HerdEffect/RuleLLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/HerdEffect/RuleLLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/HerdEffect/RuleLLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/HerdEffect/RuleLLM/run_herd_rulellm.py -c configs/HerdEffect/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/HerdEffect/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/HerdEffect/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
