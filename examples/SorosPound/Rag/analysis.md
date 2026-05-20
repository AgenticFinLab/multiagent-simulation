# SorosPound Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved currency-crisis context changes attack pressure,
defense persistence, and peg-break timing.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Peg Pressure | `compute_peg_pressure()` | `analysis-bases.md §2.1` | Context-informed pressure |
| Attack Volume | `compute_attack_volume()` | `analysis-bases.md §2.2` | Retrieved attack evidence |
| Defense Volume | `compute_defense_volume()` | `analysis-bases.md §2.3` | Retrieved defense evidence |
| Credibility Loss | `compute_credibility_loss()` | `analysis-bases.md §2.4` | Narrative persistence |
| Herding Share | `compute_herding_share()` | `analysis-bases.md §2.5` | Contextual herding |
| Break Round | `compute_break_round()` | `analysis-bases.md §2.6` | Historical timing effects |
| Defense Effectiveness | `compute_defense_effectiveness()` | `analysis-bases.md §2.7` | Defense vs attack |

## §3 Dimension-by-Dimension Analysis

Compare Rag with LLM to isolate whether retrieved domain context changes
currency-crisis behavior.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Retrieval relevance | Retrieved context should discuss currency crisis or peg defense |
| Domain-grounded reasoning | Explanations may reference reserves or speculative attacks |
| Output quality | RAG retrieval and parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag design derives from
`../simulation-bases.md §9`.

