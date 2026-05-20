# RumorSpread Rule — Analysis Documentation

## §1 Analysis Objectives

Measure deterministic rumor belief, spread velocity, distortion, correction,
skepticism, and fact-checking effects.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Belief Level | `compute_belief_level()` | `analysis-bases.md §2.1` | Global rumor belief path |
| Spread Velocity | `compute_spread_velocity()` | `analysis-bases.md §2.2` | Spread actions per round |
| Distortion Index | `compute_distortion_index()` | `analysis-bases.md §2.3` | Leveling/sharpening effect |
| Correction Lag | `compute_correction_lag()` | `analysis-bases.md §2.4` | Delay before correction |
| Skepticism Effect | `compute_skepticism_effect()` | `analysis-bases.md §2.5` | Spread reduction from skeptics |
| Fact-Check Strength | `compute_fact_check_strength()` | `analysis-bases.md §2.6` | Correction effect |
| Agent Action Share | `compute_agent_action_share()` | `analysis-bases.md §2.7` | Action attribution |

## §3 Dimension-by-Dimension Analysis

Rule output should show initial spread, possible distortion, skeptical
resistance, and fact-check correction.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rumor amplification | Gullible and distorting agents increase belief |
| Distortion | Relayers increase mutation |
| Correction | Skeptical and fact-checking agents reduce belief |

## §5 References

Metrics derive from `../analysis-bases.md §2`; mechanisms derive from
`../simulation-bases.md §4`.
