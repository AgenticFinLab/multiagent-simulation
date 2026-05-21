# SunkCostFallacy Rule — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether deterministic sunk-cost and commitment rules produce holding
of losing positions, averaging-down demand, and distinguishable rational
counterpressure.

## §2 Metric To Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Losing Position Holding Rate | `compute_losing_holding_rate()` | `analysis-bases.md §2.1` | Direct sunk-cost inertia metric. |
| Escalation Volume | `compute_escalation_volume()` | `analysis-bases.md §2.2` | Commitment buy pressure after losses. |
| Rational Cut Volume | `compute_rational_cut_volume()` | `analysis-bases.md §2.3` | Forward-looking correction volume. |
| Opportunity Reallocation | `compute_opportunity_reallocation()` | `analysis-bases.md §2.4` | Opportunity-cost trade volume. |
| Performance Drag | `compute_performance_drag()` | `analysis-bases.md §2.5` | Biased-vs-rational final-value gap. |
| Loss Onset Round | `compute_loss_onset()` | `analysis-bases.md §2.6` | First loss-state round. |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Signed pressure by agent type. |

## §3 Dimension-By-Dimension Analysis

Use `summary.json` and fixed PNG outputs to inspect structural market quality.
Use the scenario-specific functions in §2 for sunk-cost and escalation validity.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Sunk-cost holding | `SunkCostHolder` does not sell losing states. |
| Escalation | `CommitmentEscalator` buys after negative deviation. |
| Rational benchmark | `RationalCutter` and `OpportunityCostTrader` trade on valuation. |

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

Report Rule as the deterministic baseline. API variants should be compared only
after parser and output-quality checks pass.
