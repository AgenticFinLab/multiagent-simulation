# Short Squeeze Rule Analysis Plan

## §1 Objectives

Verify that the deterministic baseline produces a coherent short-squeeze path:
forced covering, retail/momentum amplification, float scarcity, and valuation
resistance are all visible in complete 200-round records.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Squeeze magnitude | `def compute_squeeze_magnitude(prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.1` |
| Covering volume | `def compute_covering_volume(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Retail demand share | `def compute_retail_demand_share(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Momentum amplification | `def compute_momentum_amplification(orders: list[dict], returns: list[float]) -> float` | `analysis-bases.md §2.4` |
| Float constraint proxy | `def compute_float_constraint(orders: list[dict], institutional_holdings: list[float]) -> float` | `analysis-bases.md §2.5` |
| Value resistance | `def compute_value_resistance(orders: list[dict], prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.6` |
| API and retrieval quality | `def compute_api_and_retrieval_quality(events: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.7`; reported as not applicable for Rule |

## §3 Analysis Dimensions

Analyze price premium, short-covering order flow, retail/momentum demand, value
resistance, institutional holding, and final market state.

## §4 Phase Analysis

Use `analysis-bases.md §4`: short buildup, initial rally, forced covering,
retail/momentum amplification, peak squeeze, and stabilization or reversal.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to treat Rule as the deterministic benchmark for
LLM, RuleLLM, and Rag.

## §6 Expected Results And Validation Criteria

A valid Rule sample records 200 rounds, finite prices, nonzero volume, positive
peak premium, and observable cover buying after price increases.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_shortsqueeze_dynamics.png`, `02_shortsqueeze_analysis.png`, and
`03_summary.png`.
