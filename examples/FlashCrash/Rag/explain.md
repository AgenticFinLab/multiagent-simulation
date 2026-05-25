# Flash Crash Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | Flash Crash |
| Decision Mechanism | RAG-augmented trading orders using retrieved domain knowledge and the liquidity-aware schema |
| Theory Reference | `examples/FlashCrash/simulation-bases.md` |
| Market Broadcast | `configs/FlashCrash/Rag/topology.yml` |

This variant extends RuleLLM with per-agent retrieval. Each investor retrieves relevant flash-crash knowledge, injects it into the user prompt, and emits `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`. The run records `rag_context` for Level-2 retrieval audit.

## §2 Theory -> Implementation Mapping

### §2.1 HighFrequencyTrader

| Theory Component | Implementation |
|---|---|
| HFT positive-feedback trading | `RagLLMHighFrequencyTrader` uses the HFT rule prompt plus retrieved context from its knowledge store. |
| Market effect | It can react to short-term momentum while retrieved history may temper or reinforce the response. |
| Config source | `configs/FlashCrash/Rag/players.yml` with `RAG_HFT_SYS`, `RAG_USER_TEMPLATE`, and `knowledge_config`. |

### §2.2 MarketMaker

| Theory Component | Implementation |
|---|---|
| Liquidity provision and withdrawal | `RagLLMMarketMaker` uses market-maker rules and retrieved context about liquidity stress and historical withdrawal. |
| Market effect | Its `provides_liquidity` decision is consumed directly by the coordinator. |
| Config source | `configs/FlashCrash/Rag/players.yml` with `RAG_MARKET_MAKER_SYS`. |

### §2.3 AlgorithmicTrader

| Theory Component | Implementation |
|---|---|
| Trend-following algorithm | `RagLLMAlgorithmicTrader` combines trend rules with retrieved crash-pattern context. |
| Market effect | It can continue or dampen trend-following behavior depending on retrieved context and current signals. |
| Config source | `configs/FlashCrash/Rag/players.yml` with `RAG_ALGO_SYS`. |

### §2.4 StopLossTrader

| Theory Component | Implementation |
|---|---|
| Stop-loss cascade | `RagLLMStopLossTrader` combines stop-loss rules with retrieved examples of cascade selling. |
| Market effect | It can produce liquidation pressure while documenting the retrieved context used for the decision. |
| Config source | `configs/FlashCrash/Rag/players.yml` with `RAG_STOP_LOSS_SYS`. |

### §2.5 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| Fundamental recovery force | `RagLLMFundamentalTrader` combines value thresholds with retrieved recovery and liquidity-stabilization context. |
| Market effect | It supplies retrieval-informed demand near undervaluation. |
| Config source | `configs/FlashCrash/Rag/players.yml` with `RAG_FUNDAMENTAL_SYS`. |

### §2.6 RetailTrader

| Theory Component | Implementation |
|---|---|
| Noise-trader background flow | The Rag variant does not instantiate a separate RetailTrader class; it focuses retrieval and API calls on the five mechanism-critical flash-crash roles. |
| Market effect | Background variation is represented by market noise and LLM sizing dispersion. |
| Config source | `configs/FlashCrash/Rag/players.yml` configured players. |

## §3 Market Mechanism

`Market.decide()` uses the same liquidity-aware coordinator as RuleLLM. Retrieval does not bypass the market contract: RAG decisions must request the liquidity-aware order fields, including `provides_liquidity`. If the stochastic API response omits only `provides_liquidity`, the player logs an explicit conservative default of `false` and records `liquidity_field_missing`; malformed numeric or JSON fields still fail through the parse/retry path.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/FlashCrash/Rag/players.py` |
| Prompt module | `examples/FlashCrash/Rag/prompts.py` |
| Retrieval | `masim.knowledge` loaders, stores, and query manager configured by `knowledge_config`. |
| Inference | Uses the project ARK LLM policy and the configured embedding policy. |
| Output parsing | `parse_llm_response_with_thinking()` plus explicit required-field checks in `players.py`. |
| Error handling | Retrieval fallback context and missing-liquidity conservative defaults are explicit and auditable; API parse failures are retried; deterministic schema/config errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/FlashCrash/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/FlashCrash/Rag/players.yml` | Player class paths, prompt paths, model name, rule parameters, and retrieval configuration. |
| `configs/FlashCrash/Rag/topology.yml` | Message routing between coordinator and agents. |
| `configs/FlashCrash/Rag/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/FlashCrash/Rag/run_flash_crash_ragllm.py -c configs/FlashCrash/Rag/simulation.yml
```

## §7 Expected Behavior

- RAG agents should preserve the RuleLLM liquidity-aware order schema.
- `rag_context` should be recorded for each investor decision when retrieval is attempted.
- `rag_stats.json` should summarize retrieval coverage and fallback-context frequency; Level-2 audit should also inspect any `liquidity_field_missing` records.
- A successful full experiment must pass Level-1 execution, Level-2 structural quality review, and RAG retrieval audit.

## §8 References

See `examples/FlashCrash/simulation-bases.md §2` for the cited market microstructure and flash-crash literature.

## §9 Variant Comparison

See `examples/FlashCrash/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
