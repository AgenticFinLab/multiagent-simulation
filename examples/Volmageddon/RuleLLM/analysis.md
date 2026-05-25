# Volmageddon RuleLLM Analysis Plan

## §1 Objectives

The RuleLLM analysis checks whether explicit prompt rules keep API decisions
close to the deterministic Volmageddon threshold logic while retaining
natural-language reasoning and stochastic quantity variation.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Volatility spike magnitude | `def compute_vol_spike_magnitude(vol_series: list[float]) -> float` | `analysis-bases.md §2.1` |
| Rebalance pressure | `def compute_rebalance_pressure(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Short-vol covering | `def compute_short_vol_covering(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Equity de-risking volume | `def compute_equity_derisking_volume(orders: list[dict]) -> float` | `analysis-bases.md §2.4` |
| Arbitrage stabilization | `def compute_arbitrage_stabilization(orders: list[dict], deviation_series: list[float]) -> float` | `analysis-bases.md §2.5` |
| Spike onset round | `def compute_spike_onset(vol_series: list[float], threshold: float) -> int` | `analysis-bases.md §2.6` |
| Feedback intensity | `def compute_feedback_intensity(vol_series: list[float], orders: list[dict]) -> float` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review threshold-rule fidelity, procyclical feedback attribution, stabilizer
activity, reasoning consistency, parser fallback rate, and whether explicit
rules reduce stochastic drift compared with LLM.

## §4 Phase Analysis

Use `analysis-bases.md §4`. RuleLLM should preserve the same calm, trigger,
feedback, and stabilization phases as Rule unless stochastic model output
changes quantity timing within the documented role constraints.

## §5 Cross-Variant Comparison

Compare RuleLLM against Rule for rule fidelity and against LLM for reduced
schema drift and more stable feedback-channel expression.

## §6 Expected Results and Validation Criteria

A full RuleLLM sample should complete 200 rounds, preserve current-market
quantity payloads, include explicit reasoning, and keep parser fallback within
the documented quality gate.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_volmageddon_dynamics.png`, `02_volmageddon_analysis.png`, and
`03_summary.png`.
