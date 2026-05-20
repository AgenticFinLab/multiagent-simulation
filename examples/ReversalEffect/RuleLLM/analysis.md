# ReversalEffect RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate RuleLLM rule adherence during overshoot and reversal.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Overshoot Magnitude | `compute_overshoot_magnitude()` | `analysis-bases.md §2.1` | Compare with Rule |
| Reversal Return | `compute_reversal_return()` | `analysis-bases.md §2.2` | LLM-mediated correction |
| Contrarian Volume | `compute_contrarian_volume()` | `analysis-bases.md §2.3` | Prompt-rule fidelity |
| Momentum Delay | `compute_momentum_delay()` | `analysis-bases.md §2.4` | Continuation before correction |
| Value Anchor Strength | `compute_value_anchor_strength()` | `analysis-bases.md §2.5` | Fundamental prompt effect |
| Reversal Onset | `compute_reversal_onset()` | `analysis-bases.md §2.6` | Timing vs Rule |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Strategy pressure |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM to Rule for direction, timing, and quantity. Large differences
should be checked against prompt adherence and parser quality.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Prompt-rule adherence | LLM follows contrarian/value/momentum direction |
| Bounded discretion | Quantity varies without reversing intended rule |
| Clean structure | Low parse/fallback counts in Level-2 audit |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM mechanism derives from
`../simulation-bases.md §9`.
