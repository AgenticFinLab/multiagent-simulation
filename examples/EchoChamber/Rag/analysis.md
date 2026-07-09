# EchoChamber Rag Analysis Plan

## §1 Objectives

The Rag analysis checks both EchoChamber social-dynamics quality and retrieval
coverage for model decisions.

## §2 Core Metrics

| Metric | Implementation Trace | Source |
|---|---|---|
| Polarization amplification | `analysis.py:compute_polarization_amplification` | `analysis-bases.md §2.1` |
| Polarization persistence | `analysis.py:compute_polarization_persistence` | `analysis-bases.md §2.2` |
| Cluster separation | `analysis.py:compute_cluster_separation` | `analysis-bases.md §2.3` |
| Polarize activity | `analysis.py:compute_polarize_activity` | `analysis-bases.md §2.4` |
| Depolarize activity | `analysis.py:compute_depolarize_activity` | `analysis-bases.md §2.5` |
| Opinion dispersion | `analysis.py:compute_opinion_dispersion` | `analysis-bases.md §2.6` |
| Retrieval/API quality | `analysis.py:compute_api_quality` and `analyze_rag_knowledge_effect` | `analysis-bases.md §2.7` |

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
