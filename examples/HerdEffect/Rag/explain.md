# Herd Effect Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | Herd Effect |
| Decision Mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema |
| Theory Reference | `examples/HerdEffect/simulation-bases.md` |
| Market Broadcast | `configs/HerdEffect/Rag/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 MomentumInvestor (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RagLLMMomentumInvestor` uses `RAG_MOMENTUM_SYS` and the retrieved knowledge context to evaluate recent return and submit positive-feedback trades. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rag/players.yml:ragllm_momentum.config.extras` supplies portfolio state, ARK policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK decision parsed into `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`. |
### §2.2 ContrarianInvestor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RagLLMContrarianInvestor` uses `RAG_CONTRARIAN_SYS` to combine mean-reversion reasoning with retrieved reversal literature. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rag/players.yml:ragllm_contrarian.config.extras` supplies portfolio state, ARK policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK decision parsed into `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`. |
### §2.3 RiskAverseInvestor (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RagLLMRiskAverseInvestor` uses `RAG_RISK_AVERSE_SYS` to make volatility-aware exposure decisions informed by retrieved risk-management context. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rag/players.yml:ragllm_risk_averse.config.extras` supplies portfolio state, ARK policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK decision parsed into `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`. |
### §2.4 NoiseTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RagLLMNoiseTrader` uses `RAG_NOISE_SYS` to preserve stochastic order-flow behavior while conditioning on retrieved market-fragility context. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rag/players.yml:ragllm_noise.config.extras` supplies portfolio state, ARK policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK decision parsed into `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`. |
### §2.5 AggressiveInvestor (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RagLLMAggressiveInvestor` uses `RAG_AGGRESSIVE_SYS` to evaluate acceleration-based momentum with retrieved positive-feedback evidence. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rag/players.yml:ragllm_aggressive.config.extras` supplies portfolio state, ARK policy, and RAG retrieval configuration. |
| Variant-specific decision mechanism | RAG-augmented ARK decision parsed into `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`. |

## §3 Market Mechanism

The coordinator mechanism is implemented in `examples/HerdEffect/Rag/players.py` as a liquidity-aware extension of the order-book market. It collects signed quantities, reads each order's `provides_liquidity` flag, increases price impact when available liquidity falls below `low_liquidity_threshold`, and broadcasts `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, and `liquidity_factor`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/HerdEffect/Rag/players.py` |
| Prompt module | `examples/HerdEffect/Rag/prompts.py` |
| Inference | ARK LLM via `examples.llm_utils.call_llm`; retrieval uses the project Hunyuan/LiteLLM embedding policy and configured local RAG index. |
| Retrieval audit | `RagLLMInvestor._build_prompt()` stores the last retrieved context as `rag_context`; `analysis.py` summarizes retrieval availability in `rag_stats.json`. |
| Output parsing | `parse_llm_response_with_thinking()` parses `<analysis>` and `<decision>` blocks with `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`; parse failures are retried up to three times and then fail fast. |
| Error handling | Deterministic config/schema/retrieval-contract errors fail fast; retrieval availability is audited through `rag_context` and `rag_stats.json`. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/HerdEffect/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/HerdEffect/Rag/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/HerdEffect/Rag/topology.yml` | Message routing between coordinator and agents. |
| `configs/HerdEffect/Rag/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/HerdEffect/Rag/run_herd_effect_ragllm.py -c configs/HerdEffect/Rag/simulation.yml
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
