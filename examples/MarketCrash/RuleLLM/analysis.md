# MarketCrash RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether the LLM preserves the explicit crash-feedback rules while
introducing bounded reasoning and quantity variation.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Maximum Drawdown | `compute_max_drawdown()` | `analysis-bases.md §2.1` | Compare to Rule baseline |
| Crash Velocity | `compute_crash_velocity()` | `analysis-bases.md §2.2` | Check whether LLM delays/accelerates cascade |
| Volatility Spike | `compute_volatility_spike()` | `analysis-bases.md §2.3` | Should rise during feedback phase |
| Forced-Selling Share | `compute_forced_selling_share()` | `analysis-bases.md §2.4` | Rule fidelity for mechanical sellers |
| Liquidity Withdrawal | `compute_liquidity_withdrawal()` | `analysis-bases.md §2.5` | MarketMaker rule adherence |
| Panic-Selling Volume | `compute_panic_selling_volume()` | `analysis-bases.md §2.6` | Panic prompt effect |
| Stabilization Ratio | `compute_stabilization_ratio()` | `analysis-bases.md §2.7` | BottomFisher response |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM against Rule for crash depth, onset, and agent attribution.
Investigate any large deviation by inspecting LLM decisions and prompt
adherence.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule adherence | LLM actions align with embedded crash rules |
| Bounded variation | Quantities vary without reversing rule direction |
| Prompt failures | Any parse/fallback events must be counted separately |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM mechanism derives from
`../simulation-bases.md §9`.
