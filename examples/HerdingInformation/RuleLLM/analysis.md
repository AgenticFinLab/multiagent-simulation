# Herding Information Cascade RuleLLM Analysis Plan

## §1 Objectives

This analysis checks whether the RuleLLM variant produces a complete, analyzable Herding Information Cascade trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Cascade Concentration Index | `def cascade_concentration_index(trade_history: list, price_history: list, fundamental: float, activation_threshold: float = 0.02) -> float` | `analysis-bases.md §2.1` |
| Cascade Persistence Duration | `def cascade_persistence_duration(price_history: list, fundamental: float, activation_threshold: float = 0.02) -> float` | `analysis-bases.md §2.2` |
| Reputation Herding Index | `def reputation_herding_index(trade_history: list, price_history: list, fundamental: float, activation_threshold: float = 0.02) -> float` | `analysis-bases.md §2.3` |
| Information Cascade Efficiency | `def information_cascade_efficiency(trade_history: list, price_history: list, fundamental: float) -> float` | `analysis-bases.md §2.4` |
| Volatility Amplification Factor | `def volatility_amplification_factor(price_history: list, fundamental: float, activation_threshold: float = 0.02, min_obs: int = 5) -> float` | `analysis-bases.md §2.5` |
| Wealth Distribution Index | `def wealth_distribution_index(agent_states: list, final_price: float) -> float` | `analysis-bases.md §2.6` |

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant. The main comparison is whether RuleLLM preserves price deviation and mechanism intensity while changing the distribution of order flow relative to the deterministic baseline.

## §4 Phase Analysis

The phase framework follows `analysis-bases.md §4`: initialization, mechanism activation, amplification or correction, and terminal stabilization. Each phase should be measured with state, activity, and dispersion metrics listed in §2.

## §5 Cross-Variant Comparison

Compare Rule, LLM, RuleLLM, and Rag on mechanism timing, peak intensity, final state, activity level, and structural quality. LLM-family variants should be reviewed for parse failures, explicit fallback counts, and whether stochastic decisions remain coherent.

## §6 Expected Results and Validation Criteria

Expected ranges and failure signs are defined in `analysis-bases.md §6`. A full experiment should record 200 rounds, finite state values, non-trivial agent activity, and scenario-specific behavior consistent with the mechanism in `simulation-bases.md`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`, `01_herdinginformation_dynamics.png`, `02_herdinginformation_analysis.png`, and `03_summary.png`.
