# StatusQuoBias Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved behavioral-finance context changes inertia, default
adherence, active rebalancing, and momentum offset.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Inertia Rate | `compute_inertia_rate()` | `analysis-bases.md §2.1` | Context-informed inaction |
| Default Adherence | `compute_default_adherence()` | `analysis-bases.md §2.2` | Retrieved default-effect context |
| Active Rebalance Volume | `compute_active_rebalance_volume()` | `analysis-bases.md §2.3` | Rational benchmark |
| Underreaction Lag | `compute_underreaction_lag()` | `analysis-bases.md §2.4` | Delayed response |
| Momentum Offset | `compute_momentum_offset()` | `analysis-bases.md §2.5` | Trend offset |
| Price Deviation | `compute_price_deviation()` | `analysis-bases.md §2.6` | Fundamental gap |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare Rag with LLM to isolate whether retrieved domain evidence shifts
inertia or rebalancing behavior.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Retrieval relevance | Retrieved context should discuss defaults, inertia, or rebalancing |
| Domain-grounded reasoning | Explanations may cite behavioral evidence |
| Output quality | RAG retrieval and parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag design derives from
`../simulation-bases.md §9`.

