# RepresentativenessBias Rule — Analysis Documentation

## §1 Analysis Objectives

Measure deterministic base-rate neglect, pattern-driven volume, mispricing, and
Bayesian/contrarian correction.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Base-Rate Neglect Index | `compute_base_rate_neglect()` | `analysis-bases.md §2.1` | Bias strength |
| Pattern-Driven Volume | `compute_pattern_volume()` | `analysis-bases.md §2.2` | Pattern/category order flow |
| Mispricing Magnitude | `compute_mispricing()` | `analysis-bases.md §2.3` | Price deviation from fundamental |
| Bayesian Correction | `compute_bayesian_correction()` | `analysis-bases.md §2.4` | Rational benchmark pressure |
| Contrarian Profitability | `compute_contrarian_profitability()` | `analysis-bases.md §2.5` | Statistical correction outcome |
| Bias Onset Round | `compute_bias_onset()` | `analysis-bases.md §2.6` | First material divergence |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Strategy contribution |

## §3 Dimension-by-Dimension Analysis

Rule output should show biased pattern/category traders moving price away from
base-rate-consistent value, followed by Bayesian and contrarian correction.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Base-rate neglect | PatternMatcher overweights salient pattern |
| Category extrapolation | CategoryOvergeneralizer adds directional pressure |
| Rational correction | BayesianUpdater and ContrarianStatistical offset mispricing |

## §5 References

Metrics derive from `../analysis-bases.md §2`; mechanisms derive from
`../simulation-bases.md §4`.
