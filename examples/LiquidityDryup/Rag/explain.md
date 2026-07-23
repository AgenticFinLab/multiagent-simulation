# Liquidity Dry-up Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | Liquidity Dry-up |
| Decision Mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema |
| Theory Reference | `examples/LiquidityDryup/simulation-bases.md` |
| Market Broadcast | `configs/LiquidityDryup/Rag/topology.yml` |

This is a trading-schema scenario. API decisions emit `action`, `bid_price`, `quantity`, numeric `provides_liquidity`, `reasoning`, and recorded `rag_context` for retrieval-quality audit.

## §2 Theory -> Implementation Mapping

### §2.1 MarketMaker (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RagLLMMarketMaker` uses `RAGLLM_MARKET_MAKER_SYS` plus retrieved crisis-liquidity knowledge to decide withdrawal and numeric liquidity provision. |
| Mathematical model from simulation-bases.md §4.1 | Prompt requires withdrawal above 2% absolute return, normal depth around 30, and inventory rebalance around 30% stress / 20% normal. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rag/players.yml:ragllm_market_maker.config.extras` supplies portfolio state, ARK model policy, and RAG config. |
| Variant-specific decision mechanism | RAG-augmented formula-anchored order plus recorded retrieval context. |
### §2.2 LiquiditySeeker (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RagLLMLiquiditySeeker` uses `RAGLLM_LIQUIDITY_SEEKER_SYS` plus retrieved execution-stress knowledge. |
| Mathematical model from simulation-bases.md §4.2 | Prompt instructs demand around +/-15 shares, scaled by liquidity / 100, with zero liquidity provision. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rag/players.yml:ragllm_liquidity_seeker.config.extras` supplies portfolio state, ARK model policy, and RAG config. |
| Variant-specific decision mechanism | RAG-augmented constrained-execution order. |
### §2.3 ValueTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RagLLMValueTrader` uses `RAGLLM_VALUE_TRADER_SYS` plus retrieved post-crisis value/liquidity context. |
| Mathematical model from simulation-bases.md §4.3 | Prompt instructs liquidity around 20 above 5% absolute deviation and quantity about `deviation * 30` above 3%. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rag/players.yml:ragllm_value_trader.config.extras` supplies portfolio state, ARK model policy, and RAG config. |
| Variant-specific decision mechanism | RAG-augmented stabilizing value order. |
### §2.4 MomentumTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RagLLMMomentumTrader` uses `RAGLLM_MOMENTUM_TRADER_SYS` to implement momentum-trader behavior. |
| Mathematical model from simulation-bases.md §4.4 | Prompt instructs trend-following quantity about `return * 200` above 1% absolute return. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rag/players.yml:ragllm_value.config.extras` supplies portfolio state, ARK model policy, and RAG config. |
| Variant-specific decision mechanism | RAG-augmented trend-following order. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RagLLMNoiseTrader` uses `RAGLLM_NOISE_TRADER_SYS` to implement noise-trader behavior. |
| Mathematical model from simulation-bases.md §4.5 | Prompt instructs small noisy orders, quantity below about 15 shares, and zero liquidity provision. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rag/players.yml:ragllm_noise_trader.config.extras` supplies portfolio state, ARK model policy, and RAG config. |
| Variant-specific decision mechanism | RAG-augmented uninformed order flow. |

## §3 Market Mechanism

The Rag market uses the same liquidity-amplified price equation as RuleLLM and sums numeric `order["provides_liquidity"]`. Each investor retrieves top-k liquidity-crisis context through `KnowledgeStore`, injects it into `{rag_context}`, and records the retrieved context in the returned decision payload for `rag_stats.json`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/LiquidityDryup/Rag/players.py` |
| Prompt module | `examples/LiquidityDryup/Rag/prompts.py` |
| Inference | ARK LLM via `LangChainAPIInference` and Hunyuan/LiteLLM embedding through `KnowledgeStore`. |
| Output parsing | `parse_llm_response_with_thinking()` parses `<analysis>` and `<decision>` blocks; malformed responses are retried three times. |
| Retrieval audit | `RagLLMInvestor._build_prompt()` records `last_rag_context`; `Rag/analysis.py` summarizes retrieval success/failure in `rag_stats.json`. |
| Error handling | Deterministic config/schema/API errors fail fast; this variant does not silently fallback after malformed decisions. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/LiquidityDryup/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/LiquidityDryup/Rag/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/LiquidityDryup/Rag/topology.yml` | Message routing between coordinator and agents. |
| `configs/LiquidityDryup/Rag/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/LiquidityDryup/Rag/run_liquidity_dryup_ragllm.py -c configs/LiquidityDryup/Rag/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/LiquidityDryup/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/LiquidityDryup/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
