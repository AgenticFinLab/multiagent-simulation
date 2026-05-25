# EchoChamber Rag Analysis Plan

## §1 Objectives

The Rag analysis checks both EchoChamber social-dynamics quality and retrieval
coverage for model decisions.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Polarization amplification | `def compute_polarization_amplification(polarization) -> float` | `analysis-bases.md §2.1` |
| Polarization persistence | `def compute_polarization_persistence(polarization) -> float` | `analysis-bases.md §2.2` |
| Cluster separation | `def compute_cluster_separation(cluster_series) -> dict` | `analysis-bases.md §2.3` |
| Polarize activity | `def compute_polarize_activity(polarize_counts) -> float` | `analysis-bases.md §2.4` |
| Depolarize activity | `def compute_depolarize_activity(depolarize_counts) -> float` | `analysis-bases.md §2.5` |
| Opinion dispersion | `def compute_opinion_dispersion(agent_opinions) -> float` | `analysis-bases.md §2.6` |
| Retrieval/API quality | `def compute_api_quality(actions, rag_contexts) -> dict` | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Analyze polarization path, action validity, role-specific activity, retrieval
success rate, and explanation quality.

## §4 Phase Analysis

Compare retrieval coverage across initialization, reinforcement, cluster
formation, depolarizing response, and terminal phases.

## §5 Cross-Variant Comparison

Rag is compared against RuleLLM to isolate the effect of retrieved context.

## §6 Expected Results and Validation Criteria

A full Rag sample should complete 200 rounds, record valid special-schema
actions, and write `rag_context` plus `rag_stats.json`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_echochamber_dynamics.png`, `02_echochamber_analysis.png`, `03_summary.png`,
and `rag_stats.json`.
