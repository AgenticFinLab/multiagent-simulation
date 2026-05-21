# Volatility Clustering Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Decision Mechanism | RuleLLM-style API orders augmented by retrieved knowledge |
| Scenario Contract | `action`, `bid_price`, `quantity`, `reasoning`, `provides_liquidity`, `rag_context` |
| Theory Reference | `examples/VolatilityClustering/simulation-bases.md` |

Rag keeps RuleLLM's liquidity-aware market and structured order contract, then
injects retrieved volatility-domain context into each investor prompt. It
records `rag_context` for retrieval-quality analysis. If an LLM omits
`provides_liquidity`, the player records the conservative default `false`.

## §2 Theory -> Implementation Mapping

| Theory Component | Implementation |
|---|---|
| Fundamentalist, `simulation-bases.md §4.1` | `RagLLMFundamentalist` uses fundamentalist rules plus retrieved context. |
| TrendFollower, `simulation-bases.md §4.2` | `RagLLMTrendFollower` uses trend rules plus retrieved context. |
| NoiseTrader, `simulation-bases.md §4.3` | `RagLLMNoiseTrader` uses noise-trader rules plus retrieved context. |
| SlowAdapter, `simulation-bases.md §4.4` | `RagLLMSlowAdapter` uses slow-adapter rules plus retrieved context. |
| VolatilityTrader, `simulation-bases.md §4.5` | `RagLLMVolatilityTrader` uses volatility-regime rules plus retrieved context. |

## §3 Market Mechanism

The Rag market is the same liquidity-aware coordinator as RuleLLM. RAG retrieval
changes only the information supplied to the API investor before it emits the
same structured order schema.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/VolatilityClustering/Rag/players.py` |
| Prompt module | `examples/VolatilityClustering/Rag/prompts.py` |
| Inference | Project ARK LLM policy plus Hunyuan/LiteLLM embedding policy |
| Output parsing | Canonical JSON parser; omitted liquidity flag defaults to conservative `false` |
| Retrieval audit | `rag_context` records and `rag_stats.json` |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/VolatilityClustering/Rag/simulation.yml` | Full 200-round entry point. |
| `configs/VolatilityClustering/Rag/players.yml` | Knowledge, embedding, market, and investor definitions. |
| `configs/VolatilityClustering/Rag/topology.yml` | Market broadcast and investor-order routing. |
| `configs/VolatilityClustering/Rag/persona.yml` | Recording/persona metadata. |

## §6 Running Instructions

```bash
python examples/VolatilityClustering/Rag/run_volatility_clustering_ragllm.py -c configs/VolatilityClustering/Rag/simulation.yml
```

## §7 Expected Behavior

Rag should preserve RuleLLM's volatility and liquidity mechanism while recording
auditable retrieved context. Retrieval failures are counted in `rag_stats.json`;
deterministic RAG configuration or embedding failures must fail fast.

## §8 References

See `examples/VolatilityClustering/simulation-bases.md §3` for the market
contract, `analysis-bases.md §2.7` for API/RAG quality, and
`analysis-bases.md §7` for required outputs.

## §9 Variant Comparison

Rag is compared against RuleLLM to isolate retrieval effects on volatility
interpretation, order flow, liquidity provision, and high-volatility duration.
