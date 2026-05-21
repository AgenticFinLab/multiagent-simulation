# Market Crash LLM Analysis Plan

## §1 Objectives

Verify that the persona-driven API variant still produces a structurally
coherent crash despite stochastic decision-making and a reduced five-archetype
investor set.

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

Analyze market path, investor-type order flow, liquidity state, and parse or
fallback quality together.

## §4 Phase Analysis

Pre-stress positioning, early selloff, crash cascade, liquidity thinning, and
attempted recovery.

## §5 Cross-Variant Comparison

Use `analysis-bases.md §5` to compare against Rule for mechanism shape and
against RuleLLM for the effect of explicit rule text.

## §6 Expected Results And Validation Criteria

A valid sample should complete 200 rounds, avoid hidden structural breakage,
show non-trivial order flow, and preserve a recognizable crash mechanism.

## §7 Visualization Catalogue

Outputs must include `summary.json`, `00_investor_bids.png`,
`01_marketcrash_dynamics.png`, `02_marketcrash_analysis.png`, and
`03_summary.png`.
