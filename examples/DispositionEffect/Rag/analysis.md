# DispositionEffect Rag Variant — analysis.md

## §1 Overview

The Rag variant reuses the shared DispositionEffect financial metrics from
`Rule/analysis.py` and adds retrieval-health reporting through
`Rag/analysis.py::analyze_rag_knowledge_effect()`.

## §2 Metrics and Functions

| Metric | Function | analysis-bases.md Ref |
|---|---|---|
| Proportion of Gains Realized (PGR) | `Rule.analysis.calculate_pgr_plr()` | §2.1 |
| Proportion of Losses Realized (PLR) | `Rule.analysis.calculate_pgr_plr()` | §2.2 |
| Disposition Coefficient (DC) | `Rule.analysis.generate_summary()` | §2.3 |
| PGR/PLR Ratio | `Rule.analysis.calculate_pgr_plr()` | §2.4 |
| Holding Period Asymmetry (HPA) | `Rag.analysis.holding_period_asymmetry()` | §2.5 |
| Performance Drag Index (PDI) | `Rag.analysis.terminal_wealth()` + `calculate_extended_metrics()` | §2.6 |
| Bias-awareness effect | `summary.json` comparison against LLM and RuleLLM | §5 |
| Tax Reversal Index (TRI) | `Rag.analysis.calculate_extended_metrics()` | §2.7 |
| RAG retrieval health | `analyze_rag_knowledge_effect()` | §7 |

## §3 Data Loading Contract

`Rag/analysis.py` calls `load_simulation_data(config)` from the Rule analysis
module. RAG order payloads must contain canonical trading fields and should also
record `rag_context` so retrieval coverage and fallback rates are auditable.

## §4 Rag Variant Notes

- Retrieval context is injected into each investor prompt before LLM inference.
- `rag_context` is recorded in the order payload for post-run retrieval quality
  analysis; this field does not change market clearing.
- If no knowledge is retrieved, `_RAG_FALLBACK` records the explicit fallback
  context string.
- RAG behavior should be compared with RuleLLM to isolate the effect of external
  domain knowledge.

## §5 Output Files

The Rag variant writes the same `summary.json` and seven figures as the Rule
variant. `summary.json` additionally includes `rag_knowledge_effect`, containing
payload count, context coverage, fallback count, retrieval rate, fallback rate,
and whether the 70% retrieval target was met.

## §6 Validation Criteria

A valid Rag run completes 200 rounds, preserves required trading fields, and
records auditable retrieval context. Retrieval quality is acceptable when the
retrieval rate is at least 70% and fallback context does not dominate decisions.

## §7 References

Metric definitions and DOI references are centralized in `analysis-bases.md §2`.
Investor theory references are centralized in `simulation-bases.md §4.1–§4.5`.
RAG retrieval expectations follow `simulation-bases.md §9` and the project
variant construction rules.
