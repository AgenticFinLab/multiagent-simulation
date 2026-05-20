# SouthSeaBubble LLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether persona-only LLM agents produce narrative demand, insider
timing, skeptical resistance, and arbitrage correction.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | LLM Notes |
|---|---|---|---|
| Bubble Magnitude | `compute_bubble_magnitude()` | `analysis-bases.md §2.1` | LLM-driven overpricing |
| Narrative Demand | `compute_narrative_demand()` | `analysis-bases.md §2.2` | Narrative persona demand |
| Insider Timing Profit | `compute_insider_timing_profit()` | `analysis-bases.md §2.3` | Timing advantage |
| Skeptical Resistance | `compute_skeptical_resistance()` | `analysis-bases.md §2.4` | Skeptic persona pressure |
| Arbitrage Correction | `compute_arbitrage_correction()` | `analysis-bases.md §2.5` | Arbitrage persona pressure |
| Crash Round | `compute_crash_round()` | `analysis-bases.md §2.6` | Bubble transition |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Contribution by persona |

## §3 Dimension-by-Dimension Analysis

Compare LLM with Rule to evaluate whether natural-language narrative reasoning
changes bubble magnitude or correction timing.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Narrative rationalization | LLM explanations cite monopoly or promotional stories |
| Fundamental skepticism | Skeptical persona resists high premiums |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; LLM mechanism derives from
`../simulation-bases.md §9`.

