# Volatility Clustering Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | Volatility Clustering |
| Decision Mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema |
| Theory Reference | `examples/VolatilityClustering/simulation-bases.md` |
| Market Broadcast | `configs/VolatilityClustering/Rag/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 Fundamentalist (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RagLLMFundamentalist` in `examples/VolatilityClustering/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/VolatilityClustering/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |
### §2.2 TrendFollower (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RagLLMTrendFollower` in `examples/VolatilityClustering/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/VolatilityClustering/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |
### §2.3 NoiseTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RagLLMNoiseTrader` in `examples/VolatilityClustering/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/VolatilityClustering/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |
### §2.4 SlowAdapter (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RagLLMSlowAdapter` in `examples/VolatilityClustering/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/VolatilityClustering/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |
### §2.5 VolatilityTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RagLLMVolatilityTrader` in `examples/VolatilityClustering/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/VolatilityClustering/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |

## §3 Market Mechanism

The coordinator mechanism is the final implementation in `examples/VolatilityClustering/Rag/players.py` and its configured counterpart in `configs/VolatilityClustering/Rag/players.yml`. It broadcasts scenario state each round, receives agent decisions, updates state variables, and records the series required by `analysis-bases.md`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/VolatilityClustering/Rag/players.py` |
| Prompt module | `examples/VolatilityClustering/Rag/prompts.py` |
| Inference | Uses the project ARK LLM policy; RAG variants also use the project Hunyuan/LiteLLM embedding policy. |
| Output parsing | Explicit parser contract in players.py and prompts.py |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/VolatilityClustering/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/VolatilityClustering/Rag/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/VolatilityClustering/Rag/topology.yml` | Message routing between coordinator and agents. |
| `configs/VolatilityClustering/Rag/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/VolatilityClustering/Rag/run_volatility_clustering_ragllm.py -c configs/VolatilityClustering/Rag/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/VolatilityClustering/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/VolatilityClustering/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
