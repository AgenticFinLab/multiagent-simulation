# SorosPound LLM Analysis Plan

## §1 Objectives

The LLM analysis checks whether persona-conditioned API decisions preserve the
SorosPound attack/defense mechanism while introducing stochastic differences in
conviction, quantity, and reasoning.

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

Review mechanism preservation, role attribution, order quantity distribution,
reasoning consistency, explicit parser fallback rate, and payload completeness.

## §4 Phase Analysis

Use `analysis-bases.md §4` and compare whether LLM decisions accelerate, delay,
or mute the pressure buildup and attack/break phases relative to Rule.

## §5 Cross-Variant Comparison

Compare LLM with Rule for mechanism drift and with RuleLLM for the stabilizing
effect of explicit prompt rules.

## §6 Expected Results and Validation Criteria

A full LLM sample should complete 200 rounds with valid `action`, `quantity`,
`agent_type`, `reasoning`, and explicit parser fallback fields. Fallback must be
within the documented quality gate.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_sorospound_dynamics.png`, `02_sorospound_analysis.png`, and
`03_summary.png`.
