# Herding Information Cascade LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | Herding Information Cascade |
| Decision Mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning |
| Theory Reference | `examples/HerdingInformation/simulation-bases.md` |
| Market Broadcast | `configs/HerdingInformation/LLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 CascadeFollower (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `LLMCascadeFollower` in `examples/HerdingInformation/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdingInformation/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |
### §2.2 ReputationHerder (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `LLMReputationHerder` in `examples/HerdingInformation/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdingInformation/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |
### §2.3 IndependentThinker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `LLMIndependentThinker` in `examples/HerdingInformation/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdingInformation/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |
### §2.4 Contrarian (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `LLMContrarian` in `examples/HerdingInformation/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdingInformation/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `LLMNoiseTrader` in `examples/HerdingInformation/LLM/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/HerdingInformation/LLM/players.yml` through `extras`. |
| Variant-specific decision mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning. |

## §3 Market Mechanism

The coordinator mechanism is the final implementation in `examples/HerdingInformation/LLM/players.py` and its configured counterpart in `configs/HerdingInformation/LLM/players.yml`. It broadcasts scenario state each round, receives agent decisions, updates state variables, and records the series required by `analysis-bases.md`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/HerdingInformation/LLM/players.py` |
| Prompt module | `examples/HerdingInformation/LLM/prompts.py` |
| Inference | Uses the project ARK LLM policy; RAG variants also use the project Hunyuan/LiteLLM embedding policy. |
| Output parsing | Explicit parser contract in players.py and prompts.py |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/HerdingInformation/LLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/HerdingInformation/LLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/HerdingInformation/LLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/HerdingInformation/LLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/HerdingInformation/LLM/run_herdinginformation_llm.py -c configs/HerdingInformation/LLM/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/HerdingInformation/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/HerdingInformation/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
