# EchoChamber LLM Analysis Plan

## §1 Objectives

The LLM analysis checks whether persona-driven social actions produce coherent
opinion dynamics and valid special-schema decisions.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Polarization amplification | `def compute_polarization_amplification(polarization) -> float` | `analysis-bases.md §2.1` |
| Polarization persistence | `def compute_polarization_persistence(polarization) -> float` | `analysis-bases.md §2.2` |
| Cluster separation | `def compute_cluster_separation(cluster_series) -> dict` | `analysis-bases.md §2.3` |
| Polarize activity | `def compute_polarize_activity(polarize_counts) -> float` | `analysis-bases.md §2.4` |
| Depolarize activity | `def compute_depolarize_activity(depolarize_counts) -> float` | `analysis-bases.md §2.5` |
| Opinion dispersion | `def compute_opinion_dispersion(agent_opinions) -> float` | `analysis-bases.md §2.6` |
| API quality | `def compute_api_quality(actions, rag_contexts) -> dict` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Analyze action validity, polarization path, opinion trajectories, parse retries,
and final cluster separation.

## §4 Phase Analysis

Use the same phase framework as Rule and compare whether LLM social reasoning
amplifies or moderates polarization phases.

## §5 Cross-Variant Comparison

LLM is compared against Rule for stochastic deviations while preserving schema
validity.

## §6 Expected Results and Validation Criteria

A full LLM sample should complete 200 rounds with valid `action_type`,
`intensity`, `opinion`, and reasoning fields.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_echochamber_dynamics.png`, `02_echochamber_analysis.png`, and
`03_summary.png`.
