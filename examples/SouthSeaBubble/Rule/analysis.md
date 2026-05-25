# SouthSeaBubble Rule Analysis Plan

## §1 Objectives

The Rule analysis checks whether the deterministic/stochastic baseline produces
a coherent narrative bubble and correction-pressure trajectory.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Bubble magnitude | `def compute_bubble_magnitude(prices: list[float], fundamental: float) -> float` | `analysis-bases.md §2.1` |
| Narrative demand | `def compute_narrative_demand(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Insider timing profit | `def compute_insider_timing_profit(values: list[float]) -> float` | `analysis-bases.md §2.3` |
| Skeptical resistance | `def compute_skeptical_resistance(orders: list[dict]) -> float` | `analysis-bases.md §2.4` |
| Arbitrage correction | `def compute_arbitrage_correction(orders: list[dict]) -> float` | `analysis-bases.md §2.5` |
| Crash round | `def compute_crash_round(prices: list[float], drawdown_threshold: float) -> int` | `analysis-bases.md §2.6` |
| Agent attribution | `def compute_agent_attribution(orders: list[dict]) -> dict[str, float]` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review bubble severity, insider/narrative demand, skeptical resistance,
arbitrage correction, crash timing, and role attribution.

## §4 Phase Analysis

Use `analysis-bases.md §4`: early accumulation, narrative boom, peak
overpricing, correction pressure, and collapse or stabilization.

## §5 Cross-Variant Comparison

Rule is the baseline for comparing API variants on bubble magnitude, narrative
demand, correction pressure, and crash timing.

## §6 Expected Results and Validation Criteria

A full Rule sample should complete 200 rounds, keep finite values, record
non-trivial role activity, and expose measurable bubble or correction pressure.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_southseabubble_dynamics.png`, `02_southseabubble_analysis.png`, and
`03_summary.png`.
