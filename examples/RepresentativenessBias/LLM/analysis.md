# RepresentativenessBias LLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether persona-only LLM agents produce base-rate neglect and
category-driven mispricing without explicit rule prompts.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | LLM Notes |
|---|---|---|---|
| Base-Rate Neglect Index | `compute_base_rate_neglect()` | `analysis-bases.md §2.1` | Persona bias strength |
| Pattern-Driven Volume | `compute_pattern_volume()` | `analysis-bases.md §2.2` | Pattern/category LLM pressure |
| Mispricing Magnitude | `compute_mispricing()` | `analysis-bases.md §2.3` | Price effect of bias |
| Bayesian Correction | `compute_bayesian_correction()` | `analysis-bases.md §2.4` | Rational persona correction |
| Contrarian Profitability | `compute_contrarian_profitability()` | `analysis-bases.md §2.5` | Correction outcome |
| Bias Onset Round | `compute_bias_onset()` | `analysis-bases.md §2.6` | Timing of belief divergence |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare LLM with Rule. LLM may create stronger narratives, weaker base-rate
discipline, or delayed correction.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Narrative overclassification | LLM category agents explain trades through prototypes |
| Bayesian restraint | Bayesian persona tempers vivid signals |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; LLM mechanism derives from
`../simulation-bases.md §9`.

## §6 Quality Checks

- Confirm the run completed the configured round count.
- Audit parse failures, retry counts, and fallback behavior before acceptance.
- Confirm LLM orders preserve valid action and quantity fields.

## §7 Reporting Notes

Report market outcomes together with LLM output-quality diagnostics. Any parse
failure after retries should fail the sample rather than silently entering a
hold action.
