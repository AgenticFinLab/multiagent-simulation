# Market Crash RuleLLM Analysis Plan

## §1 Objectives

Verify that explicit rule text keeps the API variant close to the Rule crash
mechanism while still allowing stochastic response variation.

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

Analyze market path, investor-type sell pressure, liquidity provision, and
fallback frequency.

## §4 Phase Analysis

Pre-crash positioning, volatility jump, deleveraging cascade, liquidity stress,
and stabilization attempt.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to check whether RuleLLM remains closer to Rule than
LLM on directionality of selling and liquidity withdrawal.

## §6 Expected Results And Validation Criteria

Successful runs should complete 200 rounds, preserve the canonical order
contract including `provides_liquidity`, and show crash dynamics consistent
with the Rule baseline.

## §7 Visualization Catalogue

Outputs must include `summary.json`, `00_investor_bids.png`,
`01_marketcrash_dynamics.png`, `02_marketcrash_analysis.png`, and
`03_summary.png`.
