# Asset Bubble RuleLLM Analysis Plan

## §1 Objectives

This analysis checks whether the RuleLLM variant produces a complete, analyzable Asset Bubble trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function / implementation | Source |
|---|---|---|
| Price deviation from fundamental | Delegates to `Rule/analysis.py::analyze_bubble()` and `calculate_price_deviation(...)` | `analysis-bases.md §2` |
| Bubble magnitude | `calculate_bubble_magnitude(market_prices, fundamental_value)` | `analysis-bases.md §2` |
| Rolling volatility | `calculate_rolling_volatility(market_prices, window=10)` | `analysis-bases.md §2` |
| Maximum drawdown | `calculate_max_drawdown(prices_list)` | `analysis-bases.md §2` |
| Return autocorrelation | `calculate_autocorrelation(returns_list, max_lag=5)` | `analysis-bases.md §2` |
| Rule-following order validity | `players.py::RuleLLMInvestor.decide()` parses rule-grounded `<decision>` JSON and calls `validate_order(order)` | `analysis-bases.md §6` |
| Agent order flow | `_load_data(results)` extracts `quantity`, `bid_price`, and portfolio fields from turn records | `analysis-bases.md §3` |

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant.
The main comparison is whether explicit rule text keeps LLM behavior closer to
the deterministic Rule baseline than the persona-only LLM variant.

## §4 Phase Analysis

The phase framework follows `analysis-bases.md §4`: initialization, mechanism activation, amplification or correction, and terminal stabilization. Each phase should be measured with state, activity, and dispersion metrics listed in §2.

## §5 Cross-Variant Comparison

Compare Rule, LLM, RuleLLM, and Rag on mechanism timing, peak intensity, final state, activity level, and structural quality. LLM-family variants should be reviewed for parse failures, explicit fallback counts, and whether stochastic decisions remain coherent.

## §6 Expected Results and Validation Criteria

Expected ranges and failure signs are defined in `analysis-bases.md §6`. A full experiment should record 200 rounds, finite state values, non-trivial agent activity, and scenario-specific behavior consistent with the mechanism in `simulation-bases.md`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_assetbubble_dynamics.png`, `02_assetbubble_analysis.png`, and
`03_summary.png`.
