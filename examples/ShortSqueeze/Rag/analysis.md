# Short Squeeze Rag Analysis Plan

## §1 Objectives

Verify that retrieved short-squeeze knowledge changes urgency, order sizing, or
liquidity provision only through the documented RuleLLM-style trading schema and
that retrieval coverage is auditable.

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

Analyze squeeze mechanics, liquidity flags, role-level order flow, parser
quality, conservative fallback events, and retrieval coverage.

## §4 Phase Analysis

Use `analysis-bases.md §4` and inspect whether retrieved GameStop/VW-style
context changes forced-covering urgency, retail demand, or value resistance.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to compare Rag against RuleLLM and isolate retrieval
effects while checking broader mechanism preservation against Rule and LLM.

## §6 Expected Results And Validation Criteria

A valid Rag sample records 200 rounds, finite prices, order-level liquidity
fields, `rag_context`, `rag_stats.json`, and low parse/fallback rates.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_shortsqueeze_dynamics.png`, `02_shortsqueeze_analysis.png`,
`03_summary.png`, and `rag_stats.json`.
