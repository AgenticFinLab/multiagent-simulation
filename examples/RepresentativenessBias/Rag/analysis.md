# RepresentativenessBias Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved behavioral-finance knowledge changes base-rate
neglect, pattern-driven trading, or correction pressure.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Base-Rate Neglect Index | `compute_base_rate_neglect()` | `analysis-bases.md §2.1` | Knowledge effect on bias |
| Pattern-Driven Volume | `compute_pattern_volume()` | `analysis-bases.md §2.2` | Prototype-driven order flow |
| Mispricing Magnitude | `compute_mispricing()` | `analysis-bases.md §2.3` | Price impact |
| Bayesian Correction | `compute_bayesian_correction()` | `analysis-bases.md §2.4` | Retrieved statistical context |
| Contrarian Profitability | `compute_contrarian_profitability()` | `analysis-bases.md §2.5` | Correction outcome |
| Bias Onset Round | `compute_bias_onset()` | `analysis-bases.md §2.6` | Timing |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare Rag against RuleLLM and LLM. Any useful difference should be traceable
to retrieved context rather than invalid output or missing fields.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Knowledge-tempered bias | Bayesian/contrarian agents may correct earlier |
| Knowledge-amplified salience | Pattern agents may cite vivid prototypes |
| Retrieval quality | Missing/irrelevant retrieval is flagged in post-run retrieval review |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag mechanism derives from
`../simulation-bases.md §9`.

## §6 Quality Checks

- Confirm the run completed the configured round count.
- Audit retrieval context availability, parse failures, and retry counts.
- Confirm any RAG fallback context is explicitly recorded for post-run retrieval review.

## §7 Reporting Notes

Report RAG outcomes together with retrieval diagnostics. A row with missing or
placeholder retrieval context should be marked for quality review even if the
simulator exits successfully.
