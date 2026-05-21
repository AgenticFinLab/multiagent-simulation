# Momentum Effect LLM Analysis Plan

## §1 Objectives

Verify that persona-driven API decisions preserve a coherent momentum effect
with the five-role API population.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Return autocorrelation | `def compute_return_autocorrelation(returns: list[float], lag: int = 1) -> float` | `analysis-bases.md §2.1` |
| Momentum order imbalance | `def compute_momentum_order_imbalance(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Contrarian offset | `def compute_contrarian_offset(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Trend duration | `def compute_trend_duration(prices: list[float]) -> int` | `analysis-bases.md §2.4` |
| Fundamental deviation | `def compute_fundamental_deviation(prices: list[float], fundamentals: list[float]) -> list[float]` | `analysis-bases.md §2.5` |
| Agent volume share | `def compute_agent_volume_share(orders: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.6` |
| Retrieval coverage | `def compute_rag_retrieval_coverage(rag_payloads: dict[str, dict[int, dict]]) -> dict` | `analysis-bases.md §2.7`; reported as not applicable for LLM |

## §3 Analysis Dimensions

Analyze market path, role-level order flow, parser quality, fallback rate, and
whether TrendFollower amplifies continuation.

## §4 Phase Analysis

Signal formation, API trend conviction, crowded continuation, offset, and
stabilization or reversal.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to compare against Rule for mechanism shape and
against RuleLLM for the value of explicit rules.

## §6 Expected Results And Validation Criteria

A valid LLM sample should complete 200 rounds, retain finite market state, and
avoid excessive fallback holds under the project fallback policy.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_momentumeffect_dynamics.png`, `02_momentumeffect_analysis.png`, and
`03_summary.png`.
