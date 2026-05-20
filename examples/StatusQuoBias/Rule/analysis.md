# StatusQuoBias Rule — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether deterministic inertial, default-following, active rebalancing,
momentum, and noise rules produce underreaction and sticky allocations.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Inertia Rate | `compute_inertia_rate()` | `analysis-bases.md §2.1` | Hold frequency under signal |
| Default Adherence | `compute_default_adherence()` | `analysis-bases.md §2.2` | Closeness to default |
| Active Rebalance Volume | `compute_active_rebalance_volume()` | `analysis-bases.md §2.3` | Rational response |
| Underreaction Lag | `compute_underreaction_lag()` | `analysis-bases.md §2.4` | Signal-to-price delay |
| Momentum Offset | `compute_momentum_offset()` | `analysis-bases.md §2.5` | Trend pressure |
| Price Deviation | `compute_price_deviation()` | `analysis-bases.md §2.6` | Fundamental gap |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare inertia, default following, active response, momentum offset, and price
underreaction.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Status quo inertia | InertialHolder holds despite moderate signals |
| Default effect | DefaultFollower stays close to passive allocation |
| Active correction | ActiveRebalancer responds more directly |

## §5 References

Metrics derive from `../analysis-bases.md §2`; deterministic behavior derives
from `../simulation-bases.md §4` and `§9`.

## §6 Quality Checks

- Confirm the run completed the configured round count.
- Confirm investor orders contain valid action, quantity, and agent type fields.
- Confirm hold rates and active-rebalancing volume can be attributed by agent.

## §7 Reporting Notes

Report this variant as the deterministic baseline for status quo inertia.
Compare API variants only after parser and output-quality checks pass.
