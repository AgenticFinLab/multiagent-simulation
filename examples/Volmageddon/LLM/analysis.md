# Volmageddon LLM Analysis Plan

## §1 Objectives

The LLM analysis checks whether persona-conditioned API decisions preserve the
Volmageddon mechanism while introducing stochastic variation in quantity,
urgency, and reasoning. Execution success is not enough: the analysis must also
review parse fallback rates and payload completeness.

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

Review mechanism preservation, role attribution, order quantity distribution,
reasoning consistency, explicit parser fallback rate, and structural quality of
the current-market quantity schema.

## §4 Phase Analysis

Use `analysis-bases.md §4`. LLM outputs should be checked for whether they
accelerate, delay, mute, or exaggerate the trigger and feedback phases relative
to Rule.

## §5 Cross-Variant Comparison

Compare LLM against Rule for mechanism drift and against RuleLLM for the value
of explicit decision rules. Any accepted LLM sample must document fallback rate
and whether fallback decisions affected market state.

## §6 Expected Results and Validation Criteria

A full LLM sample should complete 200 rounds with valid `action`, `quantity`,
`agent_type`, and `reasoning` fields. Stochastic parse fallback must be visible,
conservative, and within the project quality gate before the sample is accepted.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_volmageddon_dynamics.png`, `02_volmageddon_analysis.png`, and
`03_summary.png`.
