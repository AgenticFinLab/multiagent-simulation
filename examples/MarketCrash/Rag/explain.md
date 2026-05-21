# Market Crash Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | MarketCrash |
| Decision Mechanism | Rule-guided API orders augmented with retrieved reference context |
| Theory Reference | `examples/MarketCrash/simulation-bases.md` |
| Market Broadcast | `configs/MarketCrash/Rag/topology.yml` |

This variant keeps the same five configured investor archetypes as RuleLLM and
records per-round `rag_context` in player artifacts. `PassiveInvestor` is not
configured in this API variant.

## §2 Theory -> Implementation Mapping

### §2.1 RiskParityFund (simulation-bases.md §4.1)

Implemented by `RagLLMRiskParityFund` in
`examples/MarketCrash/Rag/players.py`.

### §2.2 LeveragedHedgeFund (simulation-bases.md §4.2)

Represented by `RagLLMLeveragedFund`.

### §2.3 MarketMaker (simulation-bases.md §4.3)

Implemented by `RagLLMMarketMaker`.

### §2.4 PassiveInvestor (simulation-bases.md §4.4)

Omitted from this configured variant.

### §2.5 PanicSeller (simulation-bases.md §4.5)

Implemented by `RagLLMPanicSeller`.

### §2.6 BottomFisher (simulation-bases.md §4.6)

Implemented by `RagLLMBottomFisher` with
`RAGLLM_BOTTOM_FISHER_SYS`; this replaces the previous incorrect
PassiveInvestor prompt binding.

## §3 Market Mechanism

The Rag market matches the RuleLLM liquidity-sensitive coordinator and
explicitly consumes `order["provides_liquidity"]`. Each player also retrieves
top-k knowledge snippets and stores the resolved `rag_context` in run records.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/MarketCrash/Rag/players.py` |
| Prompt module | `examples/MarketCrash/Rag/prompts.py` |
| Retrieval | Unified knowledge stack under `masim.knowledge.*` |
| Inference | ARK API model plus Hunyuan embedding configuration |
| Error handling | Explicit retry; conservative logged fallback hold on repeated parse failure |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/MarketCrash/Rag/simulation.yml` | Full simulation entry point |
| `configs/MarketCrash/Rag/players.yml` | RAG settings, prompts, models |
| `configs/MarketCrash/Rag/topology.yml` | Message routing |
| `configs/MarketCrash/Rag/persona.yml` | Recording metadata |

## §6 Running Instructions

```bash
python examples/MarketCrash/Rag/run_market_crash_ragllm.py -c configs/MarketCrash/Rag/simulation.yml
```

## §7 Expected Behavior

Rag should preserve the RuleLLM crash contract while allowing retrieved crisis
material to affect timing, urgency, and liquidity reasoning. Because
`rag_context` is now recorded and analyzed via `rag_stats.json`, successful Rag
samples should be audited both for market structure and retrieval quality.

## §8 References

See `examples/MarketCrash/simulation-bases.md §2`.

## §9 Variant Comparison

Use Rag to test whether external crisis knowledge changes crash propagation or
stabilization relative to RuleLLM.
