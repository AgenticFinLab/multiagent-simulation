# SouthSeaBubble Rule — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether deterministic insider, narrative, skeptical, arbitrage, and
noise rules generate narrative overpricing and correction dynamics.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Bubble Magnitude | `compute_bubble_magnitude()` | `analysis-bases.md §2.1` | Peak premium over fundamental |
| Narrative Demand | `compute_narrative_demand()` | `analysis-bases.md §2.2` | NarrativeBeliever pressure |
| Insider Timing Profit | `compute_insider_timing_profit()` | `analysis-bases.md §2.3` | Insider advantage |
| Skeptical Resistance | `compute_skeptical_resistance()` | `analysis-bases.md §2.4` | Fundamental skepticism |
| Arbitrage Correction | `compute_arbitrage_correction()` | `analysis-bases.md §2.5` | Mispricing correction |
| Crash Round | `compute_crash_round()` | `analysis-bases.md §2.6` | Bubble transition |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Agent contribution |

## §3 Dimension-by-Dimension Analysis

Compare narrative demand, insider timing, skeptical resistance, and arbitrage
correction over bubble phases.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Narrative bubble | NarrativeBeliever increases demand during overpricing |
| Insider advantage | InsiderAdvantaged enters or exits before crowd |
| Correction pressure | SkepticalAnalyst and Arbitrageur resist overvaluation |

## §5 References

Metrics derive from `../analysis-bases.md §2`; deterministic behavior derives
from `../simulation-bases.md §4` and `§9`.

