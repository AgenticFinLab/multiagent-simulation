# RumorSpread Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved context changes rumor spread, distortion, skepticism,
or correction under the special information-action schema.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Belief Level | `compute_belief_level()` | `analysis-bases.md §2.1` | Knowledge-informed belief path |
| Spread Velocity | `compute_spread_velocity()` | `analysis-bases.md §2.2` | Spread intensity |
| Distortion Index | `compute_distortion_index()` | `analysis-bases.md §2.3` | Mutation effect |
| Correction Lag | `compute_correction_lag()` | `analysis-bases.md §2.4` | Retrieval-supported correction timing |
| Skepticism Effect | `compute_skepticism_effect()` | `analysis-bases.md §2.5` | Skeptical evaluation |
| Fact-Check Strength | `compute_fact_check_strength()` | `analysis-bases.md §2.6` | Fact-check effect |
| Agent Action Share | `compute_agent_action_share()` | `analysis-bases.md §2.7` | Action attribution |

## §3 Dimension-by-Dimension Analysis

Compare Rag against RuleLLM. Useful differences should be traceable to retrieved
evidence and not to invalid parser output.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Knowledge-supported correction | FactChecker and SkepticalEvaluator correct earlier or stronger |
| Knowledge-amplified salience | Spreaders may increase intensity if context reinforces rumor |
| Retrieval quality | Irrelevant/no retrieval is marked in post-run retrieval review |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag mechanism derives from
`../simulation-bases.md §9`.
