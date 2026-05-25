# Market Crash Rule Analysis Plan

## §1 Objectives

Verify that the deterministic baseline produces a coherent crash path with
observable deleveraging, panic selling, liquidity stress, and limited
stabilizing demand.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Maximum drawdown | `def compute_maximum_drawdown(prices: list[float]) -> float` | `analysis-bases.md §2.1` |
| Largest one-round drop | `def compute_largest_one_round_drop(prices: list[float]) -> float` | `analysis-bases.md §2.2` |
| Volatility spike | `def compute_volatility_spike(returns: list[float], window: int) -> float` | `analysis-bases.md §2.3` |
| Forced-selling pressure | `def compute_forced_selling_pressure(orders: list[dict]) -> float` | `analysis-bases.md §2.4` |
| Liquidity withdrawal | `def compute_liquidity_withdrawal(orders: list[dict], liquidity: list[float]) -> float` | `analysis-bases.md §2.5` |
| Panic contribution | `def compute_panic_contribution(orders: list[dict], returns: list[float]) -> float` | `analysis-bases.md §2.6` |
| Bottom-fisher absorption | `def compute_bottom_fisher_absorption(orders: list[dict]) -> float` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Analyze by round, by investor class, by crash phase, and by aggregate market
state. Rule is the deterministic reference path.

## §4 Phase Analysis

Pre-crash positioning, volatility onset, forced deleveraging, liquidity stress,
and attempted stabilization.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to compare the Rule baseline against LLM, RuleLLM,
and Rag on crash depth, speed, liquidity withdrawal, and stabilizing demand.

## §6 Expected Results And Validation Criteria

The Rule run should show a clear drawdown episode, elevated volatility during
the crash, meaningful sell pressure from leveraged and panic actors, and only
partial stabilization from BottomFisher and PassiveInvestor.

## §7 Visualization Catalogue

Outputs must include `summary.json`, `00_investor_bids.png`,
`01_marketcrash_dynamics.png`, `02_marketcrash_analysis.png`, and
`03_summary.png`.
