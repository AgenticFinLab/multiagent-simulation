# CarryTradeUnwind RuleLLM Variant — Analysis Guide

## §1 Overview

| Item | Description |
|---|---|
| Analysis script | `examples/CarryTradeUnwind/RuleLLM/analysis.py` |
| Output location | `EXPERIMENT/CarryTradeUnwind/RuleLLM/records/analysis/` |
| Imported functions | Delegates to `Rule/analysis.py` for loading, metrics, validation, plots, and `summary.json` |
| Variant consideration | Interpret metrics as LLM reasoning constrained by explicit `== DECISION RULES ==` carry-trade formulas |

## §2 Metric Implementation

| Metric | Function | analysis-bases.md ref |
|---|---|---|
| Maximum Drawdown | `_compute_max_drawdown(prices_list)` | §2 Metric 1 |
| Unwind Velocity | `_compute_unwind_velocity(prices_list)` | §2 Metric 2 |
| Unwind Duration | `_compute_unwind_duration(prices_list, fundamental)` | §2 Metric 3 |
| Crisis Onset Round | `_compute_cascade_onset(prices_list, fundamental)` | §2 Metric 4 |
| Recovery Ratio | `_compute_recovery_ratio(prices_list)` | §2 Metric 5 |
| Return Autocorrelation AC(1) | `_compute_autocorrelation(prices_list, lag=1)` | §2 Metric 6 |
| Annualized Volatility | `_compute_peak_rolling_volatility(prices_list)` | §2 Metric 7 |

## §3 Dimension-by-Dimension Analysis

| Dimension | Implementation and Interpretation |
|---|---|
| Crash Severity and Cascade Dynamics | Compare drawdown and velocity with Rule to test whether embedded rules preserve cascade severity. |
| Cascade Attribution | Check whether leveraged-fund sells dominate stabilizing buyer volume during crisis rounds. |
| Recovery Analysis | Use recovery ratio and AC(1) to determine whether rule-anchored reasoning changes post-trough stabilization. |
| Timing and Sophistication | Compare action timing with LLM; RuleLLM should reduce unconstrained deliberation and improve directional alignment. |
| Cross-Variant Comparison | Use `summary.json` under `analysis-bases.md §5` to compare Rule, LLM, RuleLLM, and Rag. |

## §4 Variant-Specific Observable Phenomena

RuleLLM-specific evidence comes from `<analysis>` reasoning that cites embedded carry-trade rules, valid canonical decision JSON, and quantity deviations within the prompt-defined ±20% discretion. LeveragedCarryFund reasoning should preserve the forced-sell sign when stop-loss conditions are reached.

## §5 Scaling and Sensitivity Analysis

Runtime follows API latency and total agent count. Market sensitivity remains governed by Rule parameters, while prompt-section clarity affects parse stability, directional fidelity, and quantity dispersion around the deterministic Rule baseline.

## §6 Output Files Reference

| File | Contents |
|---|---|
| `00_investor_bids.png` | Market price, fundamental value, and per-agent bid traces |
| `01_carrytradeunwind_dynamics.png` | FX rate, fundamental anchor, deviation, and crisis thresholds |
| `02_carrytradeunwind_analysis.png` | Rolling volatility and per-round FX returns |
| `03_summary.png` | Agent VWAP and total trading-volume summary |
| `summary.json` | Metrics, price summary, agent VWAP, and nested validation result |

## §7 Cross-Variant Comparison Notes

RuleLLM should sit between Rule and LLM: closer to Rule on direction and crisis timing, but still stochastic in reasoning and quantity. A valid sample must complete all configured rounds, preserve canonical order fields, and fail fast after retry exhaustion rather than substituting hidden hold orders.
