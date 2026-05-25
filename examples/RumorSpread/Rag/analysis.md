# RumorSpread Rag Analysis

## §1 Overview

Rag analysis runs the same core belief/distortion analysis as Rule and adds
retrieval coverage through `analyze_rag_knowledge_effect()`.

## §2 Metric Mapping

| Metric | Root Reference | Implementation |
|---|---|---|
| Belief Level | `analysis-bases.md §2.1` | Rule loader and metrics. |
| Belief-Truth Divergence | `analysis-bases.md §2.2` | Rule `calculate_metrics()`. |
| Rumor Amplification Ratio | `analysis-bases.md §2.3` | Rule `calculate_metrics()`. |
| Distortion Index | `analysis-bases.md §2.4` | Rule `calculate_metrics()`. |
| Spread And Correction Activity | `analysis-bases.md §2.5` | Rule `calculate_metrics()`. |
| Correction Lag | `analysis-bases.md §2.6` | Rule `calculate_metrics()`. |
| RAG Retrieval Coverage | `analysis-bases.md §2.7` | `Rag/analysis.py::analyze_rag_knowledge_effect()`. |

## §3 Analysis Dimensions

Rag is analyzed by belief state, distortion, spread/correction activity, API
decision quality, and per-agent retrieval success.

## §4 Variant-Specific Observables

Each Rag action records `rag_context`. The analysis counts rounds where context
equals the canonical no-retrieval text versus rounds with retrieved content.

## §5 Cross-Variant Use

Rag is compared to RuleLLM to determine whether external knowledge changes
correction timing, distortion resistance, or reasoning quality.

## §6 Output Files

The analysis writes `summary.json`, `rag_stats.json`, and the four fixed PNG
outputs inherited from Rule analysis.

## §7 Validation

Full Rag experiments require 200 rounds, valid social-action payloads, and
`rag_context` availability for retrieval audit.
