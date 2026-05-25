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

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant. The main comparison is whether Rag preserves price deviation and mechanism intensity while changing the distribution of order flow relative to the deterministic baseline.

## §4 Phase Analysis

The phase framework follows `analysis-bases.md §4`: initialization, mechanism activation, amplification or correction, and terminal stabilization. Each phase should be measured with state, activity, and dispersion metrics listed in §2.

## §5 Cross-Variant Comparison

Compare Rule, LLM, RuleLLM, and Rag on mechanism timing, peak intensity, final state, activity level, and structural quality. LLM-family variants should be reviewed for parse failures, explicit fallback counts, and whether stochastic decisions remain coherent.

## §6 Expected Results and Validation Criteria

Expected ranges and failure signs are defined in `analysis-bases.md §6`. A full experiment should record 200 rounds, finite state values, non-trivial agent activity, and scenario-specific behavior consistent with the mechanism in `simulation-bases.md`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`, `01_creditcycle_dynamics.png`, `02_creditcycle_analysis.png`, `03_summary.png`, and `rag_stats.json`.
