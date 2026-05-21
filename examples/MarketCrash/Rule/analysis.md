# Market Crash Rule Analysis Plan

## §1 Objectives

Verify that the deterministic baseline produces a coherent crash path with
observable deleveraging, panic selling, liquidity stress, and limited
stabilizing demand.

## §2 Core Metrics

| Metric | Interpretation |
|---|---|
| Maximum drawdown | Peak-to-trough crash severity |
| Largest one-round drop | Crash velocity |
| Volatility spike | Stress amplification |
| Forced-selling pressure | Mechanical selling by RiskParityFund and LeveragedHedgeFund |
| Panic-selling volume | Behavioral amplification by PanicSeller |
| Bottom-fisher absorption | Stabilizing demand after deep discount |

## §3 Analysis Dimensions

Analyze by round, by investor class, by crash phase, and by aggregate market
state.

## §4 Phase Analysis

Pre-crash positioning, volatility onset, forced deleveraging, liquidity stress,
and attempted stabilization.

## §5 Cross-Variant Comparison

This baseline defines the reference crash shape for LLM, RuleLLM, and Rag.

## §6 Expected Results And Validation Criteria

The Rule run should show a clear drawdown episode, elevated volatility during
the crash, meaningful sell pressure from leveraged and panic actors, and only
partial stabilization from BottomFisher and PassiveInvestor.

## §7 Visualization Catalogue

Outputs must include `summary.json`, `00_investor_bids.png`,
`01_marketcrash_dynamics.png`, `02_marketcrash_analysis.png`, and
`03_summary.png`.
