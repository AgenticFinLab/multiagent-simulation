# Herding Information Cascade Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | Herding Information Cascade |
| Decision Mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema |
| Theory Reference | `examples/HerdingInformation/simulation-bases.md` |
| Market Broadcast | `configs/HerdingInformation/Rag/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 CascadeFollower (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RagLLMCascadeFollower` uses `RAGLLM_CASCADE_FOLLOWER_SYS` and retrieved cascade literature to evaluate deviation-following orders. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rag/players.yml:cascadefollower.config.extras` supplies portfolio state, ARK model policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK output parsed into `action`, `bid_price`, `quantity`, and `reasoning`; `players.py` executes the parsed action and quantity. |
### §2.2 ReputationHerder (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RagLLMReputationHerder` uses `RAGLLM_REPUTATION_HERDER_SYS` and retrieved career-concern context to decide whether to follow consensus. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rag/players.yml:reputationherder.config.extras` supplies portfolio state, ARK model policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK output parsed into the shared trading schema. |
### §2.3 IndependentThinker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RagLLMIndependentThinker` uses `RAGLLM_INDEPENDENT_THINKER_SYS` and retrieved cascade-fragility context to preserve private-signal reasoning. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rag/players.yml:independentthinker.config.extras` supplies portfolio state, ARK model policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK output parsed into the shared trading schema. |
### §2.4 Contrarian (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RagLLMContrarian` uses `RAGLLM_CONTRARIAN_SYS` and retrieved overreaction context to oppose crowd direction. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rag/players.yml:contrarian.config.extras` supplies portfolio state, ARK model policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK output parsed into the shared trading schema. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RagLLMNoiseTrader` uses `RAGLLM_NOISE_TRADER_SYS` with retrieved context while retaining unsystematic noise-trader behavior. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rag/players.yml:noisetrader.config.extras` supplies portfolio state, ARK model policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK output parsed into the shared trading schema. |

## §3 Market Mechanism

The Rag variant reuses the Rule `Market` class. The market broadcasts `price`, `fundamental`, `deviation`, and `round`; RAG investors retrieve information-cascade context, submit parsed buy/sell/hold orders, and the market aggregates them using the Rule baseline price equation.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/HerdingInformation/Rag/players.py` |
| Prompt module | `examples/HerdingInformation/Rag/prompts.py` |
| Inference | ARK LLM via `LangChainAPIInference`; retrieval uses the project Hunyuan/LiteLLM embedding policy and configured local RAG index. |
| Retrieval audit | `RagLLMInvestor.decide()` records retrieved context as `rag_context`; `analysis.py` summarizes retrieval availability in `rag_stats.json`. |
| Output parsing | `parse_llm_response_with_thinking()` parses `<analysis>` and `<decision>` blocks; parse failures are retried three times and then fail fast. |
| Error handling | Deterministic config/schema/retrieval-contract errors fail fast; retrieval availability is audited through `rag_context` and `rag_stats.json`. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/HerdingInformation/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/HerdingInformation/Rag/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/HerdingInformation/Rag/topology.yml` | Message routing between coordinator and agents. |
| `configs/HerdingInformation/Rag/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/HerdingInformation/Rag/run_herdinginformation_rag.py -c configs/HerdingInformation/Rag/simulation.yml
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
