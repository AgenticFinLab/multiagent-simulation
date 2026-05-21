# Reversal Effect LLM Analysis Plan

## §1 Objectives

This analysis checks whether persona-driven API investors preserve the reversal
mechanism while producing complete, auditable trading records.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Overshoot magnitude | `def compute_overshoot_magnitude(prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.1` |
| Reversal return | `def compute_reversal_return(prices: list[float], onset: int, extreme: int) -> float` | `analysis-bases.md §2.2` |
| Contrarian order share | `def compute_contrarian_order_share(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Momentum delay | `def compute_momentum_delay(prices: list[float], orders: list[dict]) -> int` | `analysis-bases.md §2.4` |
| API quality | `def compute_api_quality(events: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review reversal behavior, role-level order flow, parse retry/fallback events,
and portfolio constraints. Any fallback must be conservative, visible, and
below the project quality threshold.

## §4 Phase Analysis

Use the same phase framework as Rule, then inspect whether API investors enter
or exit phases earlier because of prompt interpretation rather than formulaic
thresholds.

## §5 Cross-Variant Comparison

Compare LLM with Rule to isolate prompt-driven stochasticity, and with RuleLLM
to measure whether explicit rules reduce dispersion or parse risk.

## §6 Expected Results and Validation Criteria

A valid full run records 200 rounds, finite prices, structured order fields, and
low API parse/fallback rates. Deterministic schema failures invalidate the
sample.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_reversaleffect_dynamics.png`, `02_reversaleffect_analysis.png`, and
`03_summary.png`.
