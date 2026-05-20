# ReversalEffect Rule — Analysis Documentation

## §1 Analysis Objectives

Measure deterministic overshoot, momentum delay, contrarian/value correction,
and reversal timing.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Overshoot Magnitude | `compute_overshoot_magnitude()` | `analysis-bases.md §2.1` | Maximum mispricing before correction |
| Reversal Return | `compute_reversal_return()` | `analysis-bases.md §2.2` | Correction after overshoot |
| Contrarian Volume | `compute_contrarian_volume()` | `analysis-bases.md §2.3` | Direct reversal pressure |
| Momentum Delay | `compute_momentum_delay()` | `analysis-bases.md §2.4` | Continuation before reversal |
| Value Anchor Strength | `compute_value_anchor_strength()` | `analysis-bases.md §2.5` | Fundamental correction |
| Reversal Onset | `compute_reversal_onset()` | `analysis-bases.md §2.6` | First sustained correction round |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Continuation vs reversal pressure |

## §3 Dimension-by-Dimension Analysis

Rule output should show an initial overshoot, trend extension from
momentum/overconfidence, and then contrarian/value-driven correction.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Overshoot | Price deviates from fundamental |
| Momentum delay | Momentum agents trade with the move before correction |
| Reversal | Contrarian and value agents dominate later pressure |

## §5 References

Metrics derive from `../analysis-bases.md §2`; mechanisms derive from
`../simulation-bases.md §4`.
