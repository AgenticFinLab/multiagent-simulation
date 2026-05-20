# MomentumEffect Rule — Analysis Documentation

## §1 Analysis Objectives

Measure deterministic momentum formation, trend duration, contrarian offset,
fundamental anchoring, and agent attribution.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Return Autocorrelation | `compute_return_autocorrelation()` | `analysis-bases.md §2.1` | Core momentum indicator |
| Momentum Order Imbalance | `compute_momentum_order_imbalance()` | `analysis-bases.md §2.2` | Momentum/technical pressure |
| Trend Duration | `compute_trend_duration()` | `analysis-bases.md §2.3` | Persistence of directional movement |
| Reversal Strength | `compute_reversal_strength()` | `analysis-bases.md §2.4` | Contrarian correction |
| Fundamental Deviation | `compute_fundamental_deviation()` | `analysis-bases.md §2.5` | Distance from anchor |
| Agent Volume Share | `compute_agent_volume_share()` | `analysis-bases.md §2.6` | Strategy attribution |
| Momentum Profitability | `compute_momentum_profitability()` | `analysis-bases.md §2.7` | Trend-follower outcome |

## §3 Dimension-by-Dimension Analysis

Rule output should show a clear relationship between recent returns and
subsequent trend-following order flow, followed by reversion or anchoring when
contrarian/fundamental agents dominate.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Momentum continuation | Positive return autocorrelation in trend phases |
| Technical reinforcement | TechnicalTrader volume aligns with recent trend |
| Reversal pressure | Contrarian/Fundamental orders oppose extreme deviations |

## §5 References

Metrics derive from `../analysis-bases.md §2`; mechanisms derive from
`../simulation-bases.md §4`.
