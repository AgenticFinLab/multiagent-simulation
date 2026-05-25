# Momentum Effect RuleLLM Analysis Plan

## §1 Objectives

Verify that explicit momentum, contrarian, technical, trend-following, and
fundamental rules keep API decisions aligned with the intended mechanism.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Return autocorrelation | `def compute_return_autocorrelation(returns: list[float], lag: int = 1) -> float` | `analysis-bases.md §2.1` |
| Momentum order imbalance | `def compute_momentum_order_imbalance(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Contrarian offset | `def compute_contrarian_offset(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Trend duration | `def compute_trend_duration(prices: list[float]) -> int` | `analysis-bases.md §2.4` |
| Fundamental deviation | `def compute_fundamental_deviation(prices: list[float], fundamentals: list[float]) -> list[float]` | `analysis-bases.md §2.5` |
| Agent volume share | `def compute_agent_volume_share(orders: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.6` |
| Retrieval coverage | `def compute_rag_retrieval_coverage(rag_payloads: dict[str, dict[int, dict]]) -> dict` | `analysis-bases.md §2.7`; reported as not applicable for RuleLLM |

## §3 Analysis Dimensions

Analyze continuation pressure, `provides_liquidity` quality, parser quality,
and role-level trade direction.

## §4 Phase Analysis

Signal formation, rule-guided continuation, crowded trend following, offset,
and stabilization or reversal.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to check whether RuleLLM is closer to Rule than LLM
in directional consistency while retaining API-level variation.

## §6 Expected Results And Validation Criteria

A valid RuleLLM sample should complete 200 rounds, preserve the
`provides_liquidity` contract, and avoid hidden parser/schema failures.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_momentumeffect_dynamics.png`, `02_momentumeffect_analysis.png`, and
`03_summary.png`.
