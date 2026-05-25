# Flash Crash Rule Analysis Plan

## §1 Objectives

This analysis checks whether the Rule variant produces a complete, analyzable Flash Crash trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Crash Depth | `def crash_depth(price_history: list, fundamental: float) -> float` | `analysis-bases.md §2` |
| Liquidity Vacuum Duration | `def liquidity_vacuum_duration(liquidity_history: list, low_threshold: float = 50.0) -> int` | `analysis-bases.md §2` |
| Stop-Loss Cascade Volume | `def stop_loss_cascade_volume(orders_history: list) -> float` | `analysis-bases.md §2` |
| Recovery Speed | `def recovery_speed(price_history: list, trough_round: int, fundamental: float, recovery_threshold: float = 0.02) -> int` | `analysis-bases.md §2` |
| Liquidity Provider Withdrawal Fraction | `def liquidity_provider_withdrawal_fraction(provides_liquidity_history: list, crash_start: int, crash_end: int) -> float` | `analysis-bases.md §2` |
| Price Amplification Ratio | `def price_amplification_ratio(observed_max_drop: float, baseline_max_drop: float) -> float` | `analysis-bases.md §2` |

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant. The main comparison is whether Rule preserves price deviation and mechanism intensity while changing the distribution of order flow relative to the deterministic baseline.

## §4 Phase Analysis

The phase framework follows `analysis-bases.md §4`: initialization, mechanism activation, amplification or correction, and terminal stabilization. Each phase should be measured with state, activity, and dispersion metrics listed in §2.

## §5 Cross-Variant Comparison

Compare Rule, LLM, RuleLLM, and Rag on mechanism timing, peak intensity, final state, activity level, and structural quality. LLM-family variants should be reviewed for parse failures, explicit fallback counts, and whether stochastic decisions remain coherent.

## §6 Expected Results and Validation Criteria

Expected ranges and failure signs are defined in `analysis-bases.md §6`. A full experiment should record 200 rounds, finite state values, non-trivial agent activity, and scenario-specific behavior consistent with the mechanism in `simulation-bases.md`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`, `01_flashcrash_dynamics.png`, `02_flashcrash_analysis.png`, and `03_summary.png`.
