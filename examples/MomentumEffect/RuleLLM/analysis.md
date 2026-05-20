# MomentumEffect RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether explicit momentum/reversion/fundamental rules survive LLM
reasoning and how RuleLLM differs from deterministic Rule.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Return Autocorrelation | `compute_return_autocorrelation()` | `analysis-bases.md §2.1` | Compare with Rule continuation |
| Momentum Order Imbalance | `compute_momentum_order_imbalance()` | `analysis-bases.md §2.2` | Prompt-rule adherence |
| Trend Duration | `compute_trend_duration()` | `analysis-bases.md §2.3` | LLM may shorten/extend trend |
| Reversal Strength | `compute_reversal_strength()` | `analysis-bases.md §2.4` | Contrarian prompt effect |
| Fundamental Deviation | `compute_fundamental_deviation()` | `analysis-bases.md §2.5` | Fundamental anchor preservation |
| Agent Volume Share | `compute_agent_volume_share()` | `analysis-bases.md §2.6` | LLM-mediated strategy attribution |
| Momentum Profitability | `compute_momentum_profitability()` | `analysis-bases.md §2.7` | Trend-follower outcome |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM against Rule for trend persistence, order direction, and
fundamental correction. Inspect LLM logs for parse failures or rule violations.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule fidelity | LLM actions follow embedded momentum/reversion rules |
| Bounded discretion | Quantities vary but do not invert rule direction |
| Parser quality | Output remains canonical JSON without fallback-heavy behavior |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM mechanism derives from
`../simulation-bases.md §9`.
