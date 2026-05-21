# Reversal Effect Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Decision Mechanism | RuleLLM-style API orders augmented by retrieved knowledge |
| Scenario Contract | `action`, `bid_price`, `quantity`, `reasoning`, `provides_liquidity`, `rag_context` |
| Theory Reference | `examples/ReversalEffect/simulation-bases.md` |

Rag keeps the RuleLLM liquidity-aware market and structured order contract, then
injects retrieved domain context into each investor prompt. The variant records
`rag_context` for post-run retrieval quality analysis. If an LLM omits
`provides_liquidity`, the player records the conservative default `false` so
missing text output cannot inflate effective market depth.

## §2 Theory -> Implementation Mapping

| Theory Component | Implementation |
|---|---|
| ContrarianInvestor, `simulation-bases.md §4.1` | `RagLLMContrarianInvestor` uses contrarian rules plus retrieved context. |
| MomentumInvestor, `simulation-bases.md §4.2` | `RagLLMMomentumChaser` uses momentum rules plus retrieved context. |
| OverconfidentTrader, `simulation-bases.md §4.3` | `RagLLMOverconfidentTrader` uses overconfident rules plus retrieved context. |
| NoiseTrader, `simulation-bases.md §4.4` | `RagLLMNoiseTrader` uses noise-trader rules plus retrieved context. |
| ValueInvestor, `simulation-bases.md §4.5` | `RagLLMValueInvestor` uses value-investor rules plus retrieved context. |
| IndexTracker, `simulation-bases.md §4.6` | Not instantiated in this API variant. |

## §3 Market Mechanism

The Rag market is the same liquidity-aware coordinator as RuleLLM. It consumes
the same signed orders and `provides_liquidity` field while the player layer
adds retrieval before the LLM call.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/ReversalEffect/Rag/players.py` |
| Prompt module | `examples/ReversalEffect/Rag/prompts.py` |
| Inference | Project ARK LLM policy plus Hunyuan/LiteLLM embedding policy |
| Output parsing | Canonical JSON parser; omitted liquidity flag defaults to conservative `false` |
| Retrieval audit | `rag_context` records and `rag_stats.json` |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/ReversalEffect/Rag/simulation.yml` | Full 200-round entry point. |
| `configs/ReversalEffect/Rag/players.yml` | Knowledge, embedding, market, and investor definitions. |
| `configs/ReversalEffect/Rag/topology.yml` | Broadcast and order routing. |
| `configs/ReversalEffect/Rag/persona.yml` | Recording/persona metadata. |

## §6 Running Instructions

```bash
python examples/ReversalEffect/Rag/run_reversal_effect_ragllm.py -c configs/ReversalEffect/Rag/simulation.yml
```

## §7 Expected Behavior

Rag should preserve RuleLLM's reversal and liquidity mechanism while showing
auditable retrieved context. Retrieval failures should be counted in
`rag_stats.json`; deterministic RAG index or embedding configuration failures
must fail fast. The conservative liquidity default should be reviewed as API
quality, not treated as passive liquidity.

## §8 References

See `examples/ReversalEffect/simulation-bases.md §3` for the market contract,
`analysis-bases.md §2.7` for API quality, and `analysis-bases.md §7` for
required analysis outputs.

## §9 Variant Comparison

Rag is compared against RuleLLM to isolate the effect of retrieved domain
knowledge. Differences should be reviewed through order flow, reversal timing,
liquidity provision, and retrieval coverage.
