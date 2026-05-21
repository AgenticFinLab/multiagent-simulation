# Short Squeeze RuleLLM Analysis Plan

## §1 Objectives

Verify that explicit short-covering, momentum, retail, value, and holding rules
preserve the squeeze mechanism under API generation and liquidity-aware market
impact.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Squeeze magnitude | `def compute_squeeze_magnitude(prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.1` |
| Covering volume | `def compute_covering_volume(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Retail demand share | `def compute_retail_demand_share(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Momentum amplification | `def compute_momentum_amplification(orders: list[dict], returns: list[float]) -> float` | `analysis-bases.md §2.4` |
| Float constraint proxy | `def compute_float_constraint(orders: list[dict], institutional_holdings: list[float]) -> float` | `analysis-bases.md §2.5` |
| Value resistance | `def compute_value_resistance(orders: list[dict], prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.6` |
| API and retrieval quality | `def compute_api_and_retrieval_quality(events: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Analyze price premium, liquidity-sensitive impact, `provides_liquidity` quality,
role-level order flow, parser quality, and explicit fallback events.

## §4 Phase Analysis

Use `analysis-bases.md §4`, with special attention to liquidity depth during
forced-covering and peak-squeeze phases.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to compare RuleLLM against LLM for rule anchoring
and against Rag for retrieval effects.

## §6 Expected Results And Validation Criteria

A valid RuleLLM sample records 200 rounds, finite prices, nonzero volume,
required liquidity flags, and low parse/fallback rates.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_shortsqueeze_dynamics.png`, `02_shortsqueeze_analysis.png`, and
`03_summary.png`.
