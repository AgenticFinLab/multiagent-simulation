# SorosPound Rule Analysis Plan

## §1 Objectives

The Rule analysis checks whether the deterministic/stochastic baseline produces
a coherent speculative attack around an overvalued currency peg.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Peg pressure | `def compute_peg_pressure(prices: list[float], peg_value: float) -> list[float]` | `analysis-bases.md §2.1` |
| Attack volume | `def compute_attack_volume(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Defense volume | `def compute_defense_volume(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Credibility loss | `def compute_credibility_loss(states: list[dict], peg_value: float) -> float` | `analysis-bases.md §2.4` |
| Herding share | `def compute_herding_share(orders: list[dict]) -> float` | `analysis-bases.md §2.5` |
| Break round | `def compute_break_round(peg_pressure: list[float], threshold: float) -> int` | `analysis-bases.md §2.6` |
| Defense effectiveness | `def compute_defense_effectiveness(defense_volume: float, attack_volume: float) -> float` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review peg stress, attack flow, defender intervention, convergence/noise
background activity, herding contribution, and finite state values.

## §4 Phase Analysis

Use the phases in `analysis-bases.md §4`: stable peg, pressure buildup, defense,
attack/break, and post-break adjustment.

## §5 Cross-Variant Comparison

Rule is the baseline for comparing stochastic API variants on attack pressure,
defense effectiveness, herding share, and break timing.

## §6 Expected Results and Validation Criteria

A full Rule sample should complete 200 rounds, maintain finite state values,
record non-trivial order activity, and show measurable attack/defense dynamics.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_sorospound_dynamics.png`, `02_sorospound_analysis.png`, and
`03_summary.png`.
