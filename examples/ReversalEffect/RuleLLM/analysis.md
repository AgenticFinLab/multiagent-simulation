# Reversal Effect RuleLLM Analysis Plan

## §1 Objectives

This analysis checks whether explicit rule prompts preserve reversal dynamics
under API generation and liquidity-sensitive market impact.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Overshoot magnitude | `def compute_overshoot_magnitude(prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.1` |
| Reversal return | `def compute_reversal_return(prices: list[float], onset: int, extreme: int) -> float` | `analysis-bases.md §2.2` |
| Contrarian order share | `def compute_contrarian_order_share(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Liquidity depth | `def compute_liquidity_depth(orders: list[dict], base_liquidity: float) -> float` | `analysis-bases.md §2.5` |
| API quality | `def compute_api_quality(events: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review reversal timing, order flow by strategy, effective liquidity, and parser
quality. The `provides_liquidity` field is a required market input.

## §4 Phase Analysis

Analyze whether low-liquidity phases amplify price moves before contrarian and
value orders stabilize the path.

## §5 Cross-Variant Comparison

Compare RuleLLM with LLM to assess the stabilizing effect of explicit rules, and
with Rag to isolate the incremental contribution of retrieved knowledge.

## §6 Expected Results and Validation Criteria

A valid full run records 200 rounds, finite prices, nonzero volume, required
liquidity flags, and low parse-failure rates.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_reversaleffect_dynamics.png`, `02_reversaleffect_analysis.png`, and
`03_summary.png`.
