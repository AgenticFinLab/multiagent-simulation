# StatusQuoBias Rule — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether deterministic status quo and default-following rules produce
high hold rates, delayed price adjustment, and clear agent-level attribution.

## §2 Metric To Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Inertia Rate | `compute_inertia_rate()` | `analysis-bases.md §2.1` | Hold frequency from deterministic orders. |
| Default Adherence | `compute_default_adherence()` | `analysis-bases.md §2.2` | Optional allocation-state diagnostic. |
| Active Rebalance Volume | `compute_active_rebalance_volume()` | `analysis-bases.md §2.3` | Corrective benchmark volume. |
| Underreaction Lag | `compute_underreaction_lag()` | `analysis-bases.md §2.4` | Signal-price response delay. |
| Momentum Offset | `compute_momentum_offset()` | `analysis-bases.md §2.5` | Trend-following pressure. |
| Price Deviation | `compute_price_deviation()` | `analysis-bases.md §2.6` | Fundamental gap. |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Signed order pressure by class. |

## §3 Dimension-By-Dimension Analysis

Use `summary.json` and the fixed PNG outputs to inspect price dynamics, volume,
and bid curves. Scenario-specific diagnostics use the functions in §2.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Status quo inertia | `InertialHolder` holds inside `change_threshold`. |
| Default effect | `DefaultFollower` holds inside `active_deviation`. |
| Active correction | `ActiveRebalancer` trades when the 5% rebalancing band is crossed. |
| Momentum offset | `MomentumTrader` follows deviation sign beyond `entry_threshold`. |

## §5 References

Metric definitions come from `../analysis-bases.md §2`; behavioral targets come
from `../simulation-bases.md §4` and `../simulation-bases.md §6`.

## §6 Quality Checks

- Confirm the run completed the configured 200 rounds for final samples.
- Confirm `summary.json.validation.is_valid` is true.
- Confirm fixed PNG outputs exist in the analysis directory.
- Confirm orders contain `action`, `bid_price`, `quantity`, `agent_type`, and
  `reasoning`.

## §7 Reporting Notes

Report Rule as the deterministic baseline. Compare API variants against this
baseline only after parser, retry, and RAG diagnostics pass their quality gates.
