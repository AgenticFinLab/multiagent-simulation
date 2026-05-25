# CarryTradeUnwind LLM Variant — Analysis Guide

## §1 Overview

| Item | Description |
|---|---|
| Analysis script | `examples/CarryTradeUnwind/LLM/analysis.py` |
| Output location | `EXPERIMENT/CarryTradeUnwind/LLM/records/analysis/` |
| Imported functions | Delegates to `Rule/analysis.py` for core loading, metrics, validation, plots, and `summary.json` |
| Variant consideration | Interpret metrics as stochastic persona-driven carry decisions under the same market mechanism as Rule |

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
| Crash Severity and Cascade Dynamics | Compare `max_drawdown_pct`, `unwind_velocity`, and `peak_rolling_vol_pct` against Rule to see whether persona reasoning delays or softens forced liquidation. |
| Cascade Attribution | Inspect per-agent action distributions and order payloads to verify leveraged carry personas sell during negative-deviation stress. |
| Recovery Analysis | Use `recovery_ratio` and AC(1) to detect whether LLM agents stabilize faster or remain hesitant after the trough. |
| Timing and Sophistication | Compare crisis onset and sell timing with Rule and RuleLLM; delayed action indicates persona deliberation. |
| Cross-Variant Comparison | Use `summary.json` fields from all four variants under `analysis-bases.md §5`. |

## §4 Variant-Specific Observable Phenomena

LLM-specific observations include reasoning quality in `<analysis>` tags, valid canonical decisions in `<decision>` JSON, stochastic quantity variation at temperature 0.3, and possible under-trading when agents interpret borderline deviation signals conservatively.

## §5 Scaling and Sensitivity Analysis

Runtime grows with agent count, API latency, and total rounds. Metric sensitivity follows the Rule variant for market parameters, but LLM temperature and prompt clarity affect quantity dispersion, parse-failure rate, and directional fidelity to the carry-trade role.

## §6 Output Files Reference

| File | Contents |
|---|---|
| `00_investor_bids.png` | Market price, fundamental value, and per-agent bid traces |
| `01_carrytradeunwind_dynamics.png` | FX rate, fundamental anchor, deviation, and crisis thresholds |
| `02_carrytradeunwind_analysis.png` | Rolling volatility and per-round FX returns |
| `03_summary.png` | Agent VWAP and total trading-volume summary |
| `summary.json` | Metrics, price summary, agent VWAP, and nested validation result |

## §7 Cross-Variant Comparison Notes

Expected LLM behavior is more variable than Rule: `max_drawdown_pct` and `unwind_velocity` may be lower if agents hesitate, while `crisis_onset_round` may be later. A valid LLM sample must complete all configured rounds, preserve canonical order fields, and fail fast after retry exhaustion rather than substituting hidden hold orders.
