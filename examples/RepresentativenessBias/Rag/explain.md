# RepresentativenessBias Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Simulation | RepresentativenessBias |
| Decision Mechanism | RuleLLM prompts plus retrieved behavioral-finance context |
| Theory Reference | `simulation-bases.md §2` and `§4` |
| Market Broadcast | Same Market implementation as Rule |

## §2 Theory → Implementation Mapping

### §2.1 RagLLMPatternMatcher (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Prototype matching | Inherits `RULELLM_PATTERN_MATCHER_SYS` |
| Retrieved context | `_retrieve_rag_context()` queries representativeness/base-rate material |
| Runtime path | Recorded `rag_context` supports retrieval-quality audit |

### §2.2 RagLLMCategoryOvergeneralizer (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Category extrapolation | Inherits category overgeneralization decision rules |
| Small-sample warning | Retrieved context may surface sample-size and base-rate cautions |
| Runtime path | Decision JSON is validated before order submission |

### §2.3 RagLLMBayesianUpdater (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Bayesian correction | Inherits base-rate disciplined prompt rules |
| Retrieved context | Retrieval can strengthen statistical prior reasoning |
| Runtime path | `rag_stats.json` measures whether context was available |

### §2.4 RagLLMContrarianStatistical (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Contrarian correction | Inherits contrarian threshold rules |
| Knowledge effect | Retrieved context may identify representativeness-driven mispricing |
| Runtime path | Canonical order includes `bid_price`, `quantity`, and `reasoning` |

### §2.5 RagLLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Uninformed liquidity | Inherits neutral noise-trader prompt |
| Retrieval neutrality | Context should not turn the agent into a biased prototype trader |
| Runtime path | Records fallback context if no index is available |

## §3 Market Mechanism

Rag preserves the Rule market. Retrieval changes the information supplied to
LLM investors before they submit orders.

## §4 Variant Architecture

```text
Market state -> KnowledgeStore query -> RAG user prompt -> LLM -> validated order -> Market
```

`Rag/analysis.py` adds `analyze_rag_knowledge_effect()` and writes
`rag_stats.json`.

## §5 Config Reference

Primary config: `configs/RepresentativenessBias/Rag/players.yml`.
RAG settings live under `private_knowledge.rag` and use
`openai/hunyuan-embedding` through LiteLLM.

## §6 Running Instructions

```bash
python examples/RepresentativenessBias/Rag/run_representativenessbias_rag.py \
  -c configs/RepresentativenessBias/Rag/simulation.yml
```

## §7 Expected Behavior

Retrieved base-rate evidence should reduce uncontrolled pattern extrapolation
without eliminating the representativeness mechanism entirely.

## §8 References

See `simulation-bases.md §2` for full citations.

## §9 Variant Comparison

See `simulation-bases.md §9`.
