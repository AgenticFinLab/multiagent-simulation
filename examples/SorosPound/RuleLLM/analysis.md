# SorosPound RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether formula-anchored LLM decisions preserve speculative attack,
peg defense, and convergence dynamics.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Peg Pressure | `compute_peg_pressure()` | `analysis-bases.md §2.1` | Rule-guided pressure |
| Attack Volume | `compute_attack_volume()` | `analysis-bases.md §2.2` | Rule-aligned short pressure |
| Defense Volume | `compute_defense_volume()` | `analysis-bases.md §2.3` | Prompt-guided defense |
| Credibility Loss | `compute_credibility_loss()` | `analysis-bases.md §2.4` | Pressure persistence |
| Herding Share | `compute_herding_share()` | `analysis-bases.md §2.5` | Opportunistic joining |
| Break Round | `compute_break_round()` | `analysis-bases.md §2.6` | Threshold timing |
| Defense Effectiveness | `compute_defense_effectiveness()` | `analysis-bases.md §2.7` | Defense vs attack |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM with Rule and LLM to isolate the effect of rule-anchored
language instructions.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule adherence | Decisions should respect prompt thresholds |
| Explanation richness | Reasons should mention attack or defense logic |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM design derives from
`../simulation-bases.md §9`.

