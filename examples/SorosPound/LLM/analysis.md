# SorosPound LLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether persona-only LLM agents create speculative attack pressure,
defense narratives, and opportunistic herding consistent with the scenario.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | LLM Notes |
|---|---|---|---|
| Peg Pressure | `compute_peg_pressure()` | `analysis-bases.md §2.1` | Narrative-driven pressure |
| Attack Volume | `compute_attack_volume()` | `analysis-bases.md §2.2` | LLM macro/opportunistic sells |
| Defense Volume | `compute_defense_volume()` | `analysis-bases.md §2.3` | LLM defense actions |
| Credibility Loss | `compute_credibility_loss()` | `analysis-bases.md §2.4` | Persistence of pressure |
| Herding Share | `compute_herding_share()` | `analysis-bases.md §2.5` | Opportunistic joining |
| Break Round | `compute_break_round()` | `analysis-bases.md §2.6` | Timing of peg break |
| Defense Effectiveness | `compute_defense_effectiveness()` | `analysis-bases.md §2.7` | LLM defense vs attack |

## §3 Dimension-by-Dimension Analysis

Compare LLM with Rule for attack timing, defense persistence, and convergence
failure.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Macro narrative | LLM explanations cite peg sustainability |
| Defense mandate | PegDefender reasons about support capacity |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; LLM mechanism derives from
`../simulation-bases.md §9`.

