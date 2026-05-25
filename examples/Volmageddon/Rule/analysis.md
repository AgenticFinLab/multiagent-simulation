# Volmageddon Rule Analysis Plan

## §1 Objectives

The Rule analysis checks whether the deterministic threshold baseline produces a
complete Volmageddon trajectory: volatility spike, inverse-ETN rebalance
pressure, short-vol covering, equity de-risking, and partial stabilization from
long-vol and arbitrage roles.

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

Review shock severity, mechanical feedback, crowded short-vol unwind,
cross-market equity de-risking, stabilizing arbitrage/hedging flow, and
structural completeness of the recorded quantity-order payloads.

## §4 Phase Analysis

Use the four-phase framework in `analysis-bases.md §4`: calm/carry, trigger,
feedback, and stabilization or persistence. The deterministic Rule run should
make phase boundaries easier to interpret than API variants.

## §5 Cross-Variant Comparison

Rule is the baseline for comparing LLM, RuleLLM, and Rag. The primary question
is whether API variants preserve the direction and timing of the feedback
mechanism while changing order size dispersion or reasoning.

## §6 Expected Results and Validation Criteria

A full Rule sample should record 200 rounds, finite non-negative proxy prices,
non-trivial role activity, observable procyclical buy pressure during stress,
and standardized analysis artifacts defined in `analysis-bases.md §7`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_volmageddon_dynamics.png`, `02_volmageddon_analysis.png`, and
`03_summary.png`.
