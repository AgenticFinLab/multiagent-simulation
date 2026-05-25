# StatusQuoBias Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved behavioral-finance context changes status quo
inertia, default adherence, active rebalancing, and explanation quality.

## §2 Metric To Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Inertia Rate | `compute_inertia_rate()` | `analysis-bases.md §2.1` | Context-informed hold behavior. |
| Default Adherence | `compute_default_adherence()` | `analysis-bases.md §2.2` | Optional allocation-state diagnostic. |
| Active Rebalance Volume | `compute_active_rebalance_volume()` | `analysis-bases.md §2.3` | Active benchmark under RAG context. |
| Underreaction Lag | `compute_underreaction_lag()` | `analysis-bases.md §2.4` | Signal-price response delay. |
| Momentum Offset | `compute_momentum_offset()` | `analysis-bases.md §2.5` | Trend pressure with retrieved context. |
| Price Deviation | `compute_price_deviation()` | `analysis-bases.md §2.6` | Fundamental gap. |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Signed order pressure by class. |
| RAG Knowledge Effect | `analyze_rag_knowledge_effect()` | `analysis-bases.md §6` | Retrieval success and fallback context rates. |

## §3 Dimension-By-Dimension Analysis

Compare Rag with LLM and RuleLLM to isolate the effect of retrieved evidence.
The analysis must inspect both market metrics and retrieval diagnostics.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Retrieval relevance | `rag_context` contains behavioral-finance or default-effect context. |
| Domain-grounded reasoning | `reasoning` may cite retrieved inertia/default evidence. |
| Retrieval fallback | Explicit fallback context is counted in `rag_stats.json`. |
| Output quality | Invalid decision JSON fails after bounded retries. |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RAG diagnostics derive from
`../analysis-bases.md §6` and the historical cases in `../simulation-bases.md §8`.

## §6 Quality Checks

- Confirm the run completed the configured 200 rounds for final samples.
- Confirm `summary.json.validation.is_valid` is true.
- Confirm `rag_context` is recorded in accepted investor outputs.
- Confirm `rag_stats.json` reports total RAG rounds, retrieval success rounds,
  and fallback rounds.

## §7 Reporting Notes

Report Rag as the domain-knowledge condition. Retrieval fallback context is a
quality diagnostic and must not be treated as a hidden simulation fallback.
