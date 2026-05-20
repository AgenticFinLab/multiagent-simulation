# RumorSpread LLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether persona-only LLM agents create plausible rumor spread,
distortion, and correction dynamics under the special information-action schema.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | LLM Notes |
|---|---|---|---|
| Belief Level | `compute_belief_level()` | `analysis-bases.md §2.1` | Persona-driven belief path |
| Spread Velocity | `compute_spread_velocity()` | `analysis-bases.md §2.2` | LLM spread intensity |
| Distortion Index | `compute_distortion_index()` | `analysis-bases.md §2.3` | Narrative mutation |
| Correction Lag | `compute_correction_lag()` | `analysis-bases.md §2.4` | Delayed correction |
| Skepticism Effect | `compute_skepticism_effect()` | `analysis-bases.md §2.5` | Skeptical persona effect |
| Fact-Check Strength | `compute_fact_check_strength()` | `analysis-bases.md §2.6` | Correction strength |
| Agent Action Share | `compute_agent_action_share()` | `analysis-bases.md §2.7` | Action attribution |

## §3 Dimension-by-Dimension Analysis

Review whether LLM-generated actions remain valid special-schema actions and
whether narratives produce plausible spread/correction behavior.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Narrative amplification | Spreaders produce high-intensity spread actions |
| Distortion language | Relayers increase mutation |
| Special parser quality | No trading-schema assumptions appear |

## §5 References

Metrics derive from `../analysis-bases.md §2`; LLM mechanism derives from
`../simulation-bases.md §9`.
