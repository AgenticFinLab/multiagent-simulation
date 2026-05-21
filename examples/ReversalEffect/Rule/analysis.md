# Reversal Effect Rule Analysis Plan

## §1 Objectives

This analysis checks whether the deterministic baseline produces complete
reversal dynamics: measurable overshoot, nonzero order flow, contrarian/value
correction pressure, and finite 200-round market series.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Overshoot magnitude | `def compute_overshoot_magnitude(prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.1` |
| Reversal return | `def compute_reversal_return(prices: list[float], onset: int, extreme: int) -> float` | `analysis-bases.md §2.2` |
| Contrarian order share | `def compute_contrarian_order_share(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Momentum delay | `def compute_momentum_delay(prices: list[float], orders: list[dict]) -> int` | `analysis-bases.md §2.4` |
| Agent attribution | `def compute_agent_attribution(orders: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.6` |

## §3 Analysis Dimensions

Review price deviation, reversal timing, order flow by strategy, and portfolio
exposure. The Rule variant is the reference path for later API comparisons.

## §4 Phase Analysis

Split the run into initialization, overreaction buildup, continuation pressure,
contrarian/value correction, and terminal stabilization. The baseline should
make these phases interpretable without API quality confounds.

## §5 Cross-Variant Comparison

Compare Rule against LLM, RuleLLM, and Rag on overshoot, correction strength,
activity, and terminal deviation. Rule has the most complete role set because it
includes IndexTracker.

## §6 Expected Results and Validation Criteria

A valid full run records 200 rounds, finite prices, nonzero volume, and a price
path that moves away from and then at least partially back toward fundamental
value.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_reversaleffect_dynamics.png`, `02_reversaleffect_analysis.png`, and
`03_summary.png`.
