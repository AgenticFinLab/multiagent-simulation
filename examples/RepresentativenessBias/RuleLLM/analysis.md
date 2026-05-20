# RepresentativenessBias RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate prompt-rule fidelity for base-rate neglect, category extrapolation,
Bayesian correction, and contrarian response.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Base-Rate Neglect Index | `compute_base_rate_neglect()` | `analysis-bases.md §2.1` | Prompt-rule bias strength |
| Pattern-Driven Volume | `compute_pattern_volume()` | `analysis-bases.md §2.2` | Pattern/category order flow |
| Mispricing Magnitude | `compute_mispricing()` | `analysis-bases.md §2.3` | Price impact |
| Bayesian Correction | `compute_bayesian_correction()` | `analysis-bases.md §2.4` | Base-rate correction |
| Contrarian Profitability | `compute_contrarian_profitability()` | `analysis-bases.md §2.5` | Statistical correction outcome |
| Bias Onset Round | `compute_bias_onset()` | `analysis-bases.md §2.6` | Timing |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM to Rule for direction, timing, and magnitude. Deviations should
be traced to LLM reasoning or output quality.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule fidelity | Decisions follow embedded base-rate/pattern rules |
| Bounded variation | Quantity changes but role direction is preserved |
| Clean output | Low parse/fallback count |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM mechanism derives from
`../simulation-bases.md §9`.
