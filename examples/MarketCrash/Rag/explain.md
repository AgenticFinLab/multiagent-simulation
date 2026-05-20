# Market Crash Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | Market Crash |
| Decision Mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema |
| Theory Reference | `examples/MarketCrash/simulation-bases.md` |
| Market Broadcast | `configs/MarketCrash/Rag/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 RiskParityFund (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RagLLMRiskParityFund` in `examples/MarketCrash/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |
### §2.2 LeveragedHedgeFund (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `configured player class family` in `examples/MarketCrash/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |
### §2.3 MarketMaker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RagLLMMarketMaker` in `examples/MarketCrash/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |
### §2.4 PassiveInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RagLLMInvestor` in `examples/MarketCrash/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |
### §2.5 PanicSeller (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RagLLMPanicSeller` in `examples/MarketCrash/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |
### §2.6 BottomFisher (simulation-bases.md §4.6)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.6 | `RagLLMBottomFisher` in `examples/MarketCrash/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/MarketCrash/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema. |

## §3 Market Mechanism

The coordinator mechanism is the final implementation in `examples/MarketCrash/Rag/players.py` and its configured counterpart in `configs/MarketCrash/Rag/players.yml`. It broadcasts scenario state each round, receives agent decisions, updates state variables, and records the series required by `analysis-bases.md`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/MarketCrash/Rag/players.py` |
| Prompt module | `examples/MarketCrash/Rag/prompts.py` |
| Inference | Uses the project ARK LLM policy; RAG variants also use the project Hunyuan/LiteLLM embedding policy. |
| Output parsing | Explicit parser contract in players.py and prompts.py |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MarketCrash/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/MarketCrash/Rag/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/MarketCrash/Rag/topology.yml` | Message routing between coordinator and agents. |
| `configs/MarketCrash/Rag/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/MarketCrash/Rag/run_market_crash_ragllm.py -c configs/MarketCrash/Rag/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/MarketCrash/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/MarketCrash/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
