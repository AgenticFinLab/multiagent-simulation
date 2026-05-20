# ShortSqueeze RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether RuleLLM preserves short-covering and amplification rules while
allowing bounded LLM variation.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Squeeze Magnitude | `compute_squeeze_magnitude()` | `analysis-bases.md §2.1` | Compare with Rule |
| Covering Volume | `compute_covering_volume()` | `analysis-bases.md §2.2` | ShortSeller prompt fidelity |
| Retail Demand Share | `compute_retail_demand_share()` | `analysis-bases.md §2.3` | Retail narrative pressure |
| Momentum Amplification | `compute_momentum_amplification()` | `analysis-bases.md §2.4` | Trend continuation |
| Float Constraint Proxy | `compute_float_constraint()` | `analysis-bases.md §2.5` | Institutional holding |
| Squeeze Onset | `compute_squeeze_onset()` | `analysis-bases.md §2.6` | Timing vs Rule |
| Value Resistance | `compute_value_resistance()` | `analysis-bases.md §2.7` | Value prompt effect |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM against Rule for onset, peak premium, and agent attribution.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule adherence | LLM follows covering and momentum rules |
| Bounded discretion | Quantity varies without invalid schema |
| Clean output | Parse/fallback counts remain low |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM mechanism derives from
`../simulation-bases.md §9`.
