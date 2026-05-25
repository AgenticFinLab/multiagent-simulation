# SorosPound Rag Analysis Plan

## §1 Objectives

The Rag analysis checks both speculative-attack mechanism quality and retrieval
quality. It verifies the same SorosPound metrics as RuleLLM while ensuring that
retrieved currency-crisis context is recorded and auditable.

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

Review peg stress, attack and defense attribution, parser fallback rate,
retrieval success rate, retrieved-context coverage by agent, and whether RAG
changes quantity decisions without violating the schema.

## §4 Phase Analysis

Use `analysis-bases.md §4`. Retrieved ERM and currency-crisis context is most
relevant during pressure buildup, defense, and attack/break phases.

## §5 Cross-Variant Comparison

Compare Rag against RuleLLM to isolate retrieval effects and against Rule/LLM
for attack timing, defense effectiveness, and quality metrics.

## §6 Expected Results and Validation Criteria

A full Rag sample should complete 200 rounds, record valid quantity orders,
include `rag_context`, write `rag_stats.json`, and keep retrieval failures and
parser fallbacks within documented quality gates.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_sorospound_dynamics.png`, `02_sorospound_analysis.png`,
`03_summary.png`, and Rag-specific `rag_stats.json`.
