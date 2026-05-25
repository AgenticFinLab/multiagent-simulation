# Tulip Mania Rag Variant Explanation

## §1 Overview

The Rag variant augments RuleLLM-style TulipMania decisions with retrieved
historical bubble context while preserving the same market and quantity-order
schema.

## §2 Theory -> Implementation Mapping

| Investor | Theory Component | Implementation |
|---|---|---|
| `RagLLMTrendChaser` | `simulation-bases.md §4.1` | Prompt combines momentum persona, explicit rule, and retrieved mania context. |
| `RagLLMSocialProofFollower` | `simulation-bases.md §4.2` | Prompt combines social-proof persona, explicit rule, and crowd-history context. |
| `RagLLMIntrinsicValueTrader` | `simulation-bases.md §4.3` | Prompt combines fundamental persona, explicit rule, and valuation/collapse context. |
| `RagLLMEarlyExitTrader` | `simulation-bases.md §4.4` | Prompt combines early-exit persona, explicit rule, and historical timing context. |
| `RagLLMNoiseTrader` | `simulation-bases.md §4.5` | Prompt treats retrieved context as peripheral for low-information trading. |

## §3 Market Mechanism

The market is imported from the Rule variant and clears current-market
quantities. Retrieved text influences only the model decision, not the market
equation.

## §4 Variant Architecture

`RagLLMInvestor` initializes or loads a per-agent RAG index, retrieves top-k
context each round, records `rag_context`, validates the quantity decision, and
emits fallback audit fields.

## §5 Config Reference

`configs/TulipMania/Rag/players.yml` defines model settings, RAG knowledge
paths, embedding settings, and player classes. Topology mirrors the Rule
message flow.

## §6 Running Instructions

```bash
python examples/TulipMania/Rag/run_tulipmania_rag.py -c configs/TulipMania/Rag/simulation.yml
```

## §7 Expected Behavior

Rag should preserve role-specific trading while adding historically informed
reasoning. Retrieval coverage must be auditable through `rag_stats.json`.

## §8 References

See `simulation-bases.md §2` and `analysis-bases.md §2`; retrieved context is
used as decision support rather than a replacement for the scenario contract.

## §9 Variant Comparison

Compare Rag against RuleLLM to isolate the effect of retrieved historical
context.
