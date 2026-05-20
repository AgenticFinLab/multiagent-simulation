# SouthSeaBubble RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether formula-anchored LLM decisions preserve narrative bubble and
correction dynamics.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Bubble Magnitude | `compute_bubble_magnitude()` | `analysis-bases.md §2.1` | Rule-guided bubble size |
| Narrative Demand | `compute_narrative_demand()` | `analysis-bases.md §2.2` | Prompt-guided narrative demand |
| Insider Timing Profit | `compute_insider_timing_profit()` | `analysis-bases.md §2.3` | Insider timing |
| Skeptical Resistance | `compute_skeptical_resistance()` | `analysis-bases.md §2.4` | Fundamental correction |
| Arbitrage Correction | `compute_arbitrage_correction()` | `analysis-bases.md §2.5` | Mispricing correction |
| Crash Round | `compute_crash_round()` | `analysis-bases.md §2.6` | Bubble phase timing |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare RuleLLM with Rule and LLM to isolate the effect of explicit rule
instructions in narrative-bubble agents.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule adherence | Decisions should respect prompt thresholds |
| Explanation richness | Reasons should identify narrative or valuation logic |
| Output quality | Parse/fallback rates must be reviewed |

## §5 References

Metrics derive from `../analysis-bases.md §2`; RuleLLM design derives from
`../simulation-bases.md §9`.

