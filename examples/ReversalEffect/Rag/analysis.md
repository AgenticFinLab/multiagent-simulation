# ReversalEffect Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved overreaction/value context changes reversal timing,
overshoot magnitude, or agent attribution.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Overshoot Magnitude | `compute_overshoot_magnitude()` | `analysis-bases.md §2.1` | Knowledge-informed overreaction |
| Reversal Return | `compute_reversal_return()` | `analysis-bases.md §2.2` | Correction after retrieved context |
| Contrarian Volume | `compute_contrarian_volume()` | `analysis-bases.md §2.3` | Contrarian knowledge effect |
| Momentum Delay | `compute_momentum_delay()` | `analysis-bases.md §2.4` | Continuation vs correction |
| Value Anchor Strength | `compute_value_anchor_strength()` | `analysis-bases.md §2.5` | Fundamental context effect |
| Reversal Onset | `compute_reversal_onset()` | `analysis-bases.md §2.6` | Timing vs RuleLLM |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Strategy attribution |

## §3 Dimension-by-Dimension Analysis

Compare Rag against RuleLLM and inspect whether differences align with retrieved
knowledge rather than parser or retrieval failures.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Knowledge-informed correction | Contrarian/value agents cite or reflect reversal evidence |
| Knowledge-informed continuation | Momentum/overconfidence may be moderated |
| Retrieval quality | Low retrieval or fallback should be marked in quality review |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag mechanism derives from
`../simulation-bases.md §9`.
