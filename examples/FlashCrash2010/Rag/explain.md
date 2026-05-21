# 2010 Flash Crash Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | 2010 Flash Crash |
| Decision Mechanism | RAG-augmented RuleLLM orders with class-mapped market agent types |
| Theory Reference | `examples/FlashCrash2010/simulation-bases.md` |
| Market Broadcast | `configs/FlashCrash2010/Rag/topology.yml` |

This variant extends RuleLLM with retrieval. Each investor retrieves flash-crash context, injects it into the decision prompt, emits a liquidity-aware order, and records `rag_context` for Level-2 retrieval audit.

## §2 Theory -> Implementation Mapping

### §2.1 HFTMarketMaker

| Theory Component | Implementation |
|---|---|
| HFT liquidity withdrawal | `RagLLMHFTMarketMaker` combines the RuleLLM HFT prompt with retrieved market-stress context. |
| Market effect | It is class-mapped to `agent_type="hft"` and contributes to depth-collapse calculations. |
| Config source | `configs/FlashCrash2010/Rag/players.yml` with `RAGLLM_HFT_MARKET_MAKER_SYS` and `knowledge_config`. |

### §2.2 MomentumChaser

| Theory Component | Implementation |
|---|---|
| Positive-feedback trading | `RagLLMMomentumChaser` combines trend rules with retrieved crash-pattern context. |
| Market effect | It is class-mapped to `agent_type="hft"` and supplies directional HFT order flow. |
| Config source | `configs/FlashCrash2010/Rag/players.yml` with `RAGLLM_MOMENTUM_CHASER_SYS`. |

### §2.3 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| Value-based stabilization | `RagLLMFundamentalTrader` combines value rules with retrieved recovery context. |
| Market effect | It is class-mapped to `agent_type="fundamental"`. |
| Config source | `configs/FlashCrash2010/Rag/players.yml` with `RAGLLM_FUNDAMENTAL_SYS`. |

### §2.4 StopLossTrader

| Theory Component | Implementation |
|---|---|
| Stop-loss cascade | `RagLLMStopLossTrader` combines stop-level rules with retrieved cascade examples. |
| Market effect | It is class-mapped to `agent_type="stoploss"`. |
| Config source | `configs/FlashCrash2010/Rag/players.yml` with `RAGLLM_STOP_LOSS_SYS`. |

### §2.5 NoiseTrader

| Theory Component | Implementation |
|---|---|
| Background order flow | `RagLLMNoiseTrader` combines random-trading rules with retrieved market context. |
| Market effect | It is class-mapped to `agent_type="noise"`. |
| Config source | `configs/FlashCrash2010/Rag/players.yml` with `RAGLLM_NOISE_TRADER_SYS`. |

## §3 Market Mechanism

The coordinator is imported from the Rule variant. Retrieval does not bypass the order-book contract: RAG orders are class-mapped to Rule `agent_type`, include `provides_liquidity` when emitted, and record conservative missing-liquidity defaults for audit.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/FlashCrash2010/Rag/players.py` |
| Prompt module | `examples/FlashCrash2010/Rag/prompts.py` |
| Retrieval | `masim.knowledge` loaders, stores, and resource manager configured by `knowledge_config`. |
| Inference | Uses the project ARK LLM policy and the configured embedding policy. |
| Output parsing | `parse_llm_response_with_thinking()` plus explicit class-based order enrichment in `players.py`. |
| Error handling | Retrieval fallback context, missing-liquidity conservative defaults, and LLM hold fallback are explicit and quality-auditable; deterministic config/schema errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/FlashCrash2010/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/FlashCrash2010/Rag/players.yml` | Player class paths, prompt paths, model name, rule parameters, and retrieval configuration. |
| `configs/FlashCrash2010/Rag/topology.yml` | Message routing between coordinator and agents. |
| `configs/FlashCrash2010/Rag/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/FlashCrash2010/Rag/run_flashcrash2010_rag.py -c configs/FlashCrash2010/Rag/simulation.yml
```

## §7 Expected Behavior

- RAG agents should preserve RuleLLM order schema and class-mapped `agent_type`.
- `rag_context` should be recorded for each investor decision when retrieval is attempted.
- `rag_stats.json` should summarize retrieval coverage and missing-liquidity markers.
- Level-2 audit should inspect parse-fallback and retrieval-fallback rates.

## §8 References

See `examples/FlashCrash2010/simulation-bases.md §2` for the cited market microstructure and May 6, 2010 sources.

## §9 Variant Comparison

See `examples/FlashCrash2010/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
