# Short Squeeze LLM Analysis Plan

## §1 Objectives

Verify that persona-driven API investors preserve the short-squeeze mechanism
while producing complete structured order records and auditable parser-quality
signals.

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

Analyze squeeze mechanics, role-level order flow, parser retries, explicit
fallback holds, and portfolio constraints.

## §4 Phase Analysis

Use `analysis-bases.md §4` and inspect whether LLM investors enter forced
covering, retail demand, or value-resistance phases earlier or later than Rule.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to compare LLM against Rule and RuleLLM, isolating
persona-driven variation from explicit-rule anchoring.

## §6 Expected Results And Validation Criteria

A valid LLM sample records 200 rounds, finite prices, structured order fields,
and a fallback rate within the project quality gate.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_shortsqueeze_dynamics.png`, `02_shortsqueeze_analysis.png`, and
`03_summary.png`.
