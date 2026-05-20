# SorosPound Rule — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether deterministic macro-attack, peg-defense, convergence, and
opportunistic rules reproduce pressure buildup, defense response, and peg-break
dynamics.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Peg Pressure | `compute_peg_pressure()` | `analysis-bases.md §2.1` | Price deviation from peg |
| Attack Volume | `compute_attack_volume()` | `analysis-bases.md §2.2` | Macro/opportunistic sell pressure |
| Defense Volume | `compute_defense_volume()` | `analysis-bases.md §2.3` | PegDefender support |
| Credibility Loss | `compute_credibility_loss()` | `analysis-bases.md §2.4` | Policy credibility decline |
| Herding Share | `compute_herding_share()` | `analysis-bases.md §2.5` | Opportunistic joining |
| Break Round | `compute_break_round()` | `analysis-bases.md §2.6` | First peg-failure threshold |
| Defense Effectiveness | `compute_defense_effectiveness()` | `analysis-bases.md §2.7` | Defense capacity vs attack |

## §3 Dimension-by-Dimension Analysis

Compare attack buildup, defense absorption, convergence failure, and the timing
of opportunistic participation.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule attack threshold | MacroHedgeFund sells when peg pressure is high |
| Defense response | PegDefender offsets sell pressure within capacity |
| Opportunistic herding | OpportunisticTrader joins after pressure is visible |

## §5 References

Metrics derive from `../analysis-bases.md §2`; deterministic behavior derives
from `../simulation-bases.md §4` and `§9`.

