# Market Crash RuleLLM Analysis Plan

## §1 Objectives

Verify that explicit rule text keeps the API variant close to the Rule crash
mechanism while still allowing stochastic response variation.

## §2 Core Metrics

| Metric | Interpretation |
|---|---|
| Maximum drawdown | Crash severity |
| Largest one-round drop | Crash velocity |
| Volatility spike | Stress amplification |
| Forced-selling pressure | Rule-guided deleveraging intensity |
| Liquidity withdrawal | MarketMaker participation through `provides_liquidity` |
| Bottom-fisher absorption | Contrarian stabilization after discount triggers |

## §3 Analysis Dimensions

Analyze market path, investor-type sell pressure, liquidity provision, and
fallback frequency.

## §4 Phase Analysis

Pre-crash positioning, volatility jump, deleveraging cascade, liquidity stress,
and stabilization attempt.

## §5 Cross-Variant Comparison

RuleLLM should remain closer to Rule than LLM on directionality of selling and
liquidity withdrawal.

## §6 Expected Results And Validation Criteria

Successful runs should complete 200 rounds, preserve the canonical order
contract including `provides_liquidity`, and show crash dynamics consistent with
the Rule baseline.

## §7 Visualization Catalogue

Outputs must include `summary.json`, `00_investor_bids.png`,
`01_marketcrash_dynamics.png`, `02_marketcrash_analysis.png`, and
`03_summary.png`.
