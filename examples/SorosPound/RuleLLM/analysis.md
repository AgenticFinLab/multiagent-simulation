# SorosPound RuleLLM Analysis Plan

## §1 Objectives

The RuleLLM analysis checks whether explicit prompt rules preserve the retained
attack/defense thresholds while allowing natural-language API reasoning.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Peg pressure | `def compute_peg_pressure(prices: list[float], peg_value: float) -> list[float]` | `analysis-bases.md §2.1` |
| Attack volume | `def compute_attack_volume(orders: list[dict]) -> float` | `analysis-bases.md §2.2` |
| Defense volume | `def compute_defense_volume(orders: list[dict]) -> float` | `analysis-bases.md §2.3` |
| Credibility loss | `def compute_credibility_loss(states: list[dict], peg_value: float) -> float` | `analysis-bases.md §2.4` |
| Herding share | `def compute_herding_share(orders: list[dict]) -> float` | `analysis-bases.md §2.5` |
| Break round | `def compute_break_round(peg_pressure: list[float], threshold: float) -> int` | `analysis-bases.md §2.6` |
| Defense effectiveness | `def compute_defense_effectiveness(defense_volume: float, attack_volume: float) -> float` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Review rule fidelity, attack/defense timing, herding share, reasoning
consistency, parser fallback rate, and quantity-order payload quality.

## §4 Phase Analysis

Use `analysis-bases.md §4`. RuleLLM should preserve the same phase ordering as
Rule unless stochastic output changes quantities within the documented role
rules.

## §5 Cross-Variant Comparison

Compare RuleLLM against Rule for threshold fidelity and against LLM for reduced
schema and mechanism drift.

## §6 Expected Results and Validation Criteria

A full RuleLLM sample should complete 200 rounds, preserve current-market
quantity payloads, and keep parser fallback within the documented quality gate.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_sorospound_dynamics.png`, `02_sorospound_analysis.png`, and
`03_summary.png`.
