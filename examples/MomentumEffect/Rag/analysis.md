# Momentum Effect Rag Analysis Plan

## §1 Objectives

Verify that the retrieval-augmented API variant preserves the RuleLLM momentum
contract and records usable retrieval evidence.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Return autocorrelation | `def compute_return_autocorrelation(returns: list[float], lag: int = 1) -> float` | `analysis-bases.md §2.1` |
| Momentum order imbalance | `def compute_momentum_order_imbalance(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Contrarian offset | `def compute_contrarian_offset(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Trend duration | `def compute_trend_duration(prices: list[float]) -> int` | `analysis-bases.md §2.4` |
| Fundamental deviation | `def compute_fundamental_deviation(prices: list[float], fundamentals: list[float]) -> list[float]` | `analysis-bases.md §2.5` |
| Agent volume share | `def compute_agent_volume_share(orders: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.6` |
| Retrieval coverage | `def compute_rag_retrieval_coverage(rag_payloads: dict[str, dict[int, dict]]) -> dict` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Analyze market continuation, role-level order flow, liquidity fields, parser
quality, and retrieval coverage.

## §4 Phase Analysis

Signal formation, retrieval-informed continuation, crowded trend following,
offset, and stabilization or reversal.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to compare Rag against RuleLLM and isolate the
effect of retrieved domain knowledge on momentum conviction and timing.

## §6 Expected Results And Validation Criteria

A valid Rag sample should complete 200 rounds, preserve `provides_liquidity`,
record `rag_context`, and produce `rag_stats.json`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_momentumeffect_dynamics.png`, `02_momentumeffect_analysis.png`,
`03_summary.png`, and `rag_stats.json`.
