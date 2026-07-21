# Credit Cycle Rag Analysis Plan

## §1 Objectives

This analysis checks whether the Rag variant produces a complete, analyzable Credit Cycle trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Leverage Amplitude Index | `_compute_leverage_amplitude_index(peak, trough) -> float` | `analysis-bases.md §2.1` |
| Minsky Fragility Score | `_compute_minsky_fragility_score(investor_payloads, prices_list, fundamental, crisis_threshold=-0.05) -> float` | `analysis-bases.md §2.2` |
| Credit Contraction Speed | `_compute_credit_contraction_speed(prices_list) -> float` | `analysis-bases.md §2.3` |
| Counter-Cyclical Offset Ratio | `_compute_counter_cyclical_offset_ratio(investor_payloads, prices_list, fundamental, bust_threshold=-0.05) -> float` | `analysis-bases.md §2.4` |
| Phase Duration Ratio | `_compute_phase_duration_ratio(prices_list, fundamental, threshold=0.02) -> float` | `analysis-bases.md §2.5` |
| Retrieval quality | `analyze_rag_knowledge_effect(investor_payloads) -> dict` writes `rag_stats.json` | `analysis-bases.md §7` |

### Retrieval Fallback Sentinel

When `KnowledgeStore.query()` returns no documents, Rag agents inject the exact string:

    _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

into the `{rag_context}` prompt slot. This sentinel is defined in `Rag/players.py` and used by `Rag/analysis.py::analyze_rag_knowledge_effect()` to classify each round as a retrieval success (context differs from sentinel) or retrieval failure (context equals sentinel).

The `rag_stats.json` output audit is:
- `retrieval_success_rate` = success_rounds / total_rag_rounds — target ≥ 0.70 per agent
- `retrieval_failure_rate` = failure_rounds / total_rag_rounds
- `meets_target` = `retrieval_success_rate >= 0.70`

A retrieval failure rate above 30% indicates the knowledge base or query formulation needs review before economic interpretation of that agent's decisions.

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant. The main comparison is whether Rag preserves price deviation and mechanism intensity while changing the distribution of order flow relative to the deterministic baseline.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Description | How to Observe | Contrast with Baseline |
|---|---|---|---|
| Knowledge-anchored credit expansion | ProCyclicalLender bids reference retrieved credit-boom precedents (e.g., 2005-2007 mortgage cycle); expansion tempo modulated by document strength | Investor payloads' `rag_context` includes historical passages; `01_price_dynamics.png` peaks slightly later than Rule | Cycles delayed 2-4 rounds relative to Rule |
| Precedent-driven Minsky pivot | MinskyBorrower deleveraging accelerates when retrieved documents describe past crises (Minsky moment case studies) | `02_cycle_dynamics.png` shows a bust cliff similar to Rule when retrieval succeeds | CCS approaches Rule when retrieval is healthy |
| Retrieval sentinel signalling degraded reasoning | When `KnowledgeStore.query()` returns no documents, the exact string `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` is injected into `{rag_context}`; these rounds should be counted and audited | `rag_stats.json → retrieval_failure_rate` per agent; expect ≤ 0.30 for a valid run | Rag-specific — no analogue in Rule/LLM |
| Retrieval-conditioned CCOR | CounterCyclicalLender bids track retrieved counter-cyclical policy precedents; CCOR variance depends on knowledge coverage rather than sampling temperature | Compare CCOR across seeds vs `retrieval_success_rate` per seed | CCOR variance correlates with retrieval quality |

Rag replaces persona-only reasoning with retrieval-grounded reasoning; every economic interpretation must be cross-referenced with `rag_stats.json` retrieval quality.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 100 | 1-2 cycles; retrieval statistics estimable | Low | Quick testing |
| 200 | 3-5 cycles; retrieval failure rate stabilizes | Medium | Standard runs |
| 500 | Mann-Whitney vs Rule + retrieval-quality regression viable | High | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| 40 | Cycles noisy; retrieval budget concentrated on fewer agents may inflate success rate | Low order density; retrieval quality dominates variance |
| 100 | Full mechanism; retrieval failure rate ≤ 0.30 across agent types | Balanced knowledge coverage across ProCyclical/Minsky/CounterCyclical personas |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| Knowledge store top-k | +50 % | Higher `retrieval_success_rate`; cycles converge toward Rule shape |
| Knowledge store top-k | −50 % | `retrieval_failure_rate` may exceed 0.30; softer, delayed cycles |
| Knowledge store size (documents) | −50 % | Retrieval failure rate rises sharply; interpret metrics with caution |
| `MinskyBorrower.leverage_ratio` | +50 % | Higher MFS but only when retrieved precedents corroborate the shift |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/CreditCycle/Rag/analysis/`.

| Output File | Generated By | Contents | How to Interpret |
|---|---|---|---|
| `summary.json` | `main()` | Metrics + validation + `llm_diagnostics` | Metrics valid only if `rag_stats.json → retrieval_failure_rate ≤ 0.30` |
| `rag_stats.json` | `analyze_rag_knowledge_effect(investor_payloads)` | Per-agent `retrieval_success_rate`, `retrieval_failure_rate`, `meets_target` (target ≥ 0.70 success) | Failures counted against the `_RAG_FALLBACK` sentinel; failure rate > 0.30 blocks economic interpretation |
| `00_investor_bids.png` | `_write_standard_named_outputs()` | Per-round bids grouped by agent type | Bid distribution reflects retrieved-precedent themes |
| `01_price_dynamics.png` | `plot_price_dynamics()` | Price vs fundamental with phase shading | Cycles similar to LLM but timing anchored by retrieved precedents |
| `02_cycle_dynamics.png` | `plot_cycle_dynamics()` | Deviation, leverage proxy, counter-cyclical activity | Bust cliff sharpness correlates with retrieval quality |
| `03_summary.png` | `plot_summary()` | Metric bar chart with validation bands | Report retrieval quality alongside metric bars |

---

## §7 Cross-Variant Comparison Notes

Rag is compared against Rule via Mann-Whitney U on 10 independent trials, conditioning on retrieval quality (see `analysis-bases.md §5`).

| Comparison Axis | Rag's Expected Position | Reason |
|---|---|---|
| Leverage Amplitude Index | Between LLM and Rule when retrieval healthy | Retrieved precedents temper narrative excess |
| Minsky Fragility Score | Near Rule when retrieval healthy; below LLM otherwise | Historical precedents recover trigger sharpness |
| Credit Contraction Speed | Near Rule when retrieval healthy | Precedents encode cascade timing |
| Counter-Cyclical Offset Ratio | Variance driven by retrieval success rate, not sampling temperature | Retrieval-grounded discretion replaces persona sampling noise |
| Retrieval quality | New axis: `retrieval_success_rate` should be ≥ 0.70; `retrieval_failure_rate` ≤ 0.30 | Below this band, all other Rag metrics are unreliable |
| Behavioral realism | Highest | Retrieval-grounded reasoning mirrors real-world analyst behaviour |
| Decision quality | Near-optimal when retrieval healthy; degrades gracefully via `_RAG_FALLBACK` when not | Sentinel makes retrieval failures explicit and auditable |
