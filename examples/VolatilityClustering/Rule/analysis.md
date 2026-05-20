# Volatility Clustering Rule Analysis Plan

## §1 Objectives

This analysis checks whether the Rule variant produces a complete, analyzable Volatility Clustering trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Price or state deviation | `def compute_deviation(series, reference) -> float` | `analysis-bases.md §2.1` |
| Phenomenon intensity | `def compute_intensity(path, events) -> float` | `analysis-bases.md §2.2` |
| Volatility or dispersion | `def compute_dispersion(series, window) -> float` | `analysis-bases.md §2.3` |
| Agent wealth or state exposure | `def compute_agent_exposure(records) -> dict` | `analysis-bases.md §2.4` |
| Volume or activity | `def compute_activity(decisions) -> float` | `analysis-bases.md §2.5` |
| Scenario-specific diagnostic | `def compute_volatilityclustering_diagnostic(data) -> float` | `analysis-bases.md §2.6` |

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant. The main comparison is whether Rule preserves price deviation and mechanism intensity while changing the distribution of order flow relative to the deterministic baseline.

## §4 Phase Analysis

The phase framework follows `analysis-bases.md §4`: initialization, mechanism activation, amplification or correction, and terminal stabilization. Each phase should be measured with state, activity, and dispersion metrics listed in §2.

## §5 Cross-Variant Comparison

Compare Rule, LLM, RuleLLM, and Rag on mechanism timing, peak intensity, final state, activity level, and structural quality. LLM-family variants should be reviewed for parse failures, explicit fallback counts, and whether stochastic decisions remain coherent.

## §6 Expected Results and Validation Criteria

Expected ranges and failure signs are defined in `analysis-bases.md §6`. A full experiment should record 200 rounds, finite state values, non-trivial agent activity, and scenario-specific behavior consistent with the mechanism in `simulation-bases.md`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png` or the scenario-equivalent agent-state plot, `01_volatilityclustering_dynamics.png`, `02_volatilityclustering_analysis.png`, and `03_summary.png`. Special-schema scenarios may relabel plot content while preserving the fixed output set.
