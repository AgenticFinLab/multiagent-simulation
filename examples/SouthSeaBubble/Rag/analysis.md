# SouthSeaBubble Rag — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether retrieved bubble history changes narrative demand, insider
timing, skeptical resistance, and arbitrage correction.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rag Notes |
|---|---|---|---|
| Bubble Magnitude | `compute_bubble_magnitude()` | `analysis-bases.md §2.1` | Context-informed overpricing |
| Narrative Demand | `compute_narrative_demand()` | `analysis-bases.md §2.2` | Retrieved narrative salience |
| Insider Timing Profit | `compute_insider_timing_profit()` | `analysis-bases.md §2.3` | Timing interpretation |
| Skeptical Resistance | `compute_skeptical_resistance()` | `analysis-bases.md §2.4` | Fundamental context |
| Arbitrage Correction | `compute_arbitrage_correction()` | `analysis-bases.md §2.5` | Correction context |
| Crash Round | `compute_crash_round()` | `analysis-bases.md §2.6` | Historical timing effects |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare Rag with LLM to isolate whether retrieved domain context shifts bubble
formation or correction.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Retrieval relevance | Retrieved context should discuss bubbles, insiders, or valuation |
| Domain-grounded reasoning | Explanations may cite historical bubble logic |
| Output quality | RAG retrieval and parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; Rag design derives from
`../simulation-bases.md §9`.

