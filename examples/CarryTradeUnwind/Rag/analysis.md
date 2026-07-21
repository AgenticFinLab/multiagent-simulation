# CarryTradeUnwind Rag Variant — Analysis Guide

## §1 Overview

| Item | Description |
|---|---|
| Analysis script | `examples/CarryTradeUnwind/Rag/analysis.py` |
| Output location | `EXPERIMENT/CarryTradeUnwind/Rag/records/analysis/` |
| Imported functions | Reuses `Rule/analysis.py` for core metrics and adds `analyze_rag_knowledge_effect()` |
| Variant consideration | Interpret market outcomes together with retrieval-hit and retrieval-miss statistics from recorded `rag_context` |

## §2 Metric Implementation

| Metric | Function | analysis-bases.md ref |
|---|---|---|
| Maximum Drawdown | `_compute_max_drawdown(prices_list)` | §2 Metric 1 |
| Unwind Velocity | `_compute_unwind_velocity(prices_list)` | §2 Metric 2 |
| Unwind Duration | `_compute_unwind_duration(prices_list, fundamental)` | §2 Metric 3 |
| Crisis Onset Round | `_compute_cascade_onset(prices_list, fundamental)` | §2 Metric 4 |
| Recovery Ratio | `_compute_recovery_ratio(prices_list)` | §2 Metric 5 |
| Return Autocorrelation AC(1) | `_compute_autocorrelation(prices_list, lag=1)` | §2 Metric 6 |
| Annualized Volatility | `_compute_peak_rolling_volatility(prices_list)` | §2 Metric 7 |
| Retrieval Coverage | `analyze_rag_knowledge_effect(investor_payloads)` | §5 Cross-Variant Comparison |

## §3 Dimension-by-Dimension Analysis

| Dimension | Implementation and Interpretation |
|---|---|
| Crash Severity and Cascade Dynamics | Compare drawdown, velocity, and volatility with RuleLLM to estimate knowledge-context effects. |
| Cascade Attribution | Inspect `rag_context` alongside order payloads to see whether retrieved crisis context coincides with leveraged selling or stabilizer buying. |
| Recovery Analysis | Compare recovery ratio and AC(1) with RuleLLM; useful retrieval should improve stabilization interpretation. |
| Timing and Sophistication | Compare crisis onset and action timing with RuleLLM to identify earlier recognition of carry-stress analogies. |
| Cross-Variant Comparison | Use `summary.json` and `rag_stats.json` under `analysis-bases.md §5`. |

## §4 Variant-Specific Observable Phenomena

Rag-specific evidence includes non-empty retrieved context, retrieval-hit rates by agent, explicit retrieval-miss marker rounds, and reasoning traces that use retrieved carry-crisis context without violating the canonical trading schema.

### Retrieval Fallback Sentinel

When `KnowledgeStore.query()` returns no documents, Rag agents inject the exact string:

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

into the `{rag_context}` prompt slot. This sentinel is defined in `Rag/players.py` and used by `Rag/analysis.py::analyze_rag_knowledge_effect()` to classify each round as a retrieval success (context differs from sentinel) or retrieval failure (context equals sentinel).

The `rag_stats.json` output audit is:
- `retrieval_success_rate` = success_rounds / total_rag_rounds — target ≥ 0.70 per agent
- `retrieval_failure_rate` = failure_rounds / total_rag_rounds
- `meets_target` = `retrieval_success_rate >= 0.70`

A retrieval failure rate above 30% indicates the knowledge base or query formulation needs review before economic interpretation of that agent's decisions.

## §5 Scaling and Sensitivity Analysis

Runtime scales with API latency, embedding/index load time, retrieval `top_k`, and agent count. Retrieval quality is sensitive to document coverage, embedding availability, and query phrasing. High retrieval-miss rates require quality review even when the simulation exits successfully.

## §6 Output Files Reference

| File | Contents |
|---|---|
| `00_investor_bids.png` | Market price, fundamental value, and per-agent bid traces |
| `01_carrytradeunwind_dynamics.png` | FX rate, fundamental anchor, deviation, and crisis thresholds |
| `02_carrytradeunwind_analysis.png` | Rolling volatility and per-round FX returns |
| `03_summary.png` | Agent VWAP and total trading-volume summary |
| `summary.json` | Core metrics, validation, and nested `rag_knowledge_effect` |
| `rag_stats.json` | Per-agent retrieval success and retrieval-miss statistics |

## §7 Cross-Variant Comparison Notes

Rag should be compared primarily against RuleLLM because it keeps the same persona/rule prompt and only adds retrieved knowledge. A valid sample must complete all configured rounds, preserve canonical order fields, record `rag_context`, and report retrieval quality in `rag_stats.json`.
