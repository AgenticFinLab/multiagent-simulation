# ShortSqueeze Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved squeeze context changes covering, retail/momentum
demand, or value resistance.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Squeeze Magnitude | `compute_squeeze_magnitude()` | `analysis-bases.md §2.1` | Knowledge-informed peak premium |
| Covering Volume | `compute_covering_volume()` | `analysis-bases.md §2.2` | Retrieved short constraint context |
| Retail Demand Share | `compute_retail_demand_share()` | `analysis-bases.md §2.3` | Retail precedent effect |
| Momentum Amplification | `compute_momentum_amplification()` | `analysis-bases.md §2.4` | Trend/crowd reinforcement |
| Float Constraint Proxy | `compute_float_constraint()` | `analysis-bases.md §2.5` | Institutional holding context |
| Squeeze Onset | `compute_squeeze_onset()` | `analysis-bases.md §2.6` | Timing vs RuleLLM |
| Value Resistance | `compute_value_resistance()` | `analysis-bases.md §2.7` | Valuation context |

## §3 Dimension-by-Dimension Analysis

Compare Rag to RuleLLM. Differences should be explained by retrieved context,
not by parser failures or invalid order schema.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Historical squeeze awareness | Agents reference covering/float dynamics |
| Knowledge-altered urgency | Covering or retail demand timing changes |
| Retrieval quality | Missing or poor retrieval is recorded in quality review |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag mechanism derives from
`../simulation-bases.md §9`.
