# MomentumEffect Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved momentum/behavioral-finance context changes trend
persistence, contrarian response, or fundamental anchoring.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Return Autocorrelation | `compute_return_autocorrelation()` | `analysis-bases.md §2.1` | Knowledge-informed continuation |
| Momentum Order Imbalance | `compute_momentum_order_imbalance()` | `analysis-bases.md §2.2` | Trend conviction with retrieval |
| Trend Duration | `compute_trend_duration()` | `analysis-bases.md §2.3` | Compare against RuleLLM |
| Reversal Strength | `compute_reversal_strength()` | `analysis-bases.md §2.4` | Retrieved overreaction context |
| Fundamental Deviation | `compute_fundamental_deviation()` | `analysis-bases.md §2.5` | Valuation-anchor effect |
| Agent Volume Share | `compute_agent_volume_share()` | `analysis-bases.md §2.6` | Agent attribution |
| Momentum Profitability | `compute_momentum_profitability()` | `analysis-bases.md §2.7` | Strategy outcome |

## §3 Dimension-by-Dimension Analysis

Compare Rag to RuleLLM. Useful differences should come from retrieved context,
not schema drift or parser failures.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Knowledge-informed momentum | Trend agents cite or reflect retrieved momentum context |
| Knowledge-informed correction | Contrarian/fundamental agents may respond earlier |
| Retrieval quality | Low retrieval quality should be marked in Level-2 review |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RAG mechanism derives from
`../simulation-bases.md §9`.
