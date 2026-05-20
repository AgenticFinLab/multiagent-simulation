# ShortSqueeze Rule — Analysis Documentation

## §1 Analysis Objectives

Measure deterministic squeeze magnitude, covering volume, retail/momentum
amplification, float constraints, and value resistance.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Squeeze Magnitude | `compute_squeeze_magnitude()` | `analysis-bases.md §2.1` | Peak premium to fundamental |
| Covering Volume | `compute_covering_volume()` | `analysis-bases.md §2.2` | Forced ShortSeller buys |
| Retail Demand Share | `compute_retail_demand_share()` | `analysis-bases.md §2.3` | Crowd demand |
| Momentum Amplification | `compute_momentum_amplification()` | `analysis-bases.md §2.4` | Positive feedback |
| Float Constraint Proxy | `compute_float_constraint()` | `analysis-bases.md §2.5` | Sticky supply |
| Squeeze Onset | `compute_squeeze_onset()` | `analysis-bases.md §2.6` | First premium threshold crossing |
| Value Resistance | `compute_value_resistance()` | `analysis-bases.md §2.7` | Fundamental sell pressure |

## §3 Dimension-by-Dimension Analysis

Rule output should show covering and retail/momentum demand rising as price
increases, with value resistance near extreme overvaluation.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Forced covering | ShortSeller buy volume rises with price |
| Crowd amplification | Retail and momentum buys add to pressure |
| Float scarcity | Institutional holding limits sell supply |

## §5 References

Metrics derive from `../analysis-bases.md §2`; mechanisms derive from
`../simulation-bases.md §4`.
