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

---

## §4 Variant-Specific Observable Phenomena

Rag investors receive an injected `{rag_context}` slot on every prompt. When
retrieval returns no documents the sentinel

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

is used, and rounds where `rag_context == _RAG_FALLBACK` must be excluded
before attributing behavior to retrieved knowledge. Analysis should
distinguish retrieval-informed rounds from fallback rounds when explaining
disposition strength.

| Phenomenon | How to Observe | Contrast with Baseline |
|---|---|---|
| Retrieval-modulated disposition | `summary.json → strategy_comparison` shows PGR/PLR bands narrower than pure LLM; DispositionInvestor DC closer to Rule central value | Rule has no retrieval; LLM has no context |
| Fallback-triggered regression | Rounds with `_RAG_FALLBACK` show LLM-like variance; healthy runs keep the fallback share ≤ 30 % | High fallback fraction ⇒ knowledge-base gap |
| Prospect-theory reinforcement | Retrieved Kahneman & Tversky (1979) style passages can push `LLMLossAverse` PLR below the Rule floor | LLM without retrieval spreads more; Rule sits at threshold |
| Reasoning-quality lift | Order payload `reasoning` text explicitly cites retrieved evidence (e.g., "loss aversion", "reference point") | LLM reasoning is unanchored |
| RAG retrieval audit | `rag_stats.json` records per-agent retrieval rate; `retrieval_rate ≥ 0.70` required before economic interpretation | Rule and LLM lack this field |

Retrieval health drives interpretation: high fallback fractions imply that
observed behavior is closer to RuleLLM than to the intended Rag regime.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 100 | Retrieval coverage measurable; PGR/PLR direction visible | Low — thin retrieval sample | Retrieval-index smoke test |
| 200 | Full arc; per-agent retrieval statistics stabilize | Medium | Standard runs |
| 500 | Precise `retrieval_failure_rate` per agent; robust contrast against RuleLLM | High | Retrieval-quality and Rule/LLM contrast studies |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| Minimum viable (~5 per strategy) | Retrieval coverage per strategy noisy; sensitive to knowledge-base gaps | Retrieval variance dominates strategy-level metrics |
| Recommended (10–20 per strategy) | Stable retrieval rate; readable `fig7` violins; clear Rag vs RuleLLM contrast | Balanced retrieval load |
| Large (50+ per strategy) | Very tight strategy-level bands; RAG throughput becomes the cost driver | Retrieval-cost limited |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| Retrieval top-k | +50% | Lower `retrieval_failure_rate`; longer prompts; disposition strength closer to intended Rag band |
| Retrieval top-k | −50% | More `_RAG_FALLBACK` events; behavior regresses toward RuleLLM |
| Knowledge base breadth (document count) | +50% | Fewer fallback rounds; disposition metrics stabilize |
| Knowledge base breadth | −50% | Retrieval failures rise; disposition metrics widen |
| Query template specificity | +50% | Higher retrieval relevance; sharper reduction in PGR variance |

---

## §7 Cross-Variant Comparison Notes

Expected relative positions (see `analysis-bases.md §5`):

| Comparison Axis | Rag's Expected Position | Reason |
|---|---|---|
| PGR level | Moderated by retrieval; may be lower than pure LLM | Retrieved evidence discourages emotional over-eagerness |
| PLR level | May be lower than Rule (retrieved prospect-theory reinforces loss aversion) | Retrieval anchors loss reluctance |
| PGR/PLR ratio | Between Rule (tight) and LLM (wide) | Retrieval compresses LLM variance |
| Disposition coefficient (DC) | Moderate | Anchored by retrieved literature |
| HPA | Between Rule and LLM | Retrieved evidence tempers narrative bias |
| Performance drag (PDI) | May be lower than pure LLM (informed decisions) | Retrieval improves decision quality when retrieval succeeds |
| Retrieval health | Must be audited (`rag_stats.json`, `retrieval_rate ≥ 0.70`) | Analysis-critical for Rag interpretation |
| Variance across seeds | Lower than LLM, higher than Rule | Retrieval reduces LLM stochasticity but does not eliminate it |
