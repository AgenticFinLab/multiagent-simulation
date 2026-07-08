# EchoChamber Rule Analysis Plan

## §1 Objectives

The Rule analysis verifies formula-driven polarization dynamics and provides the
baseline for comparing API variants.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Polarization amplification | `def compute_polarization_amplification(polarization) -> float` | `analysis-bases.md §2.1` |
| Polarization persistence | `def compute_polarization_persistence(polarization) -> float` | `analysis-bases.md §2.2` |
| Cluster separation | `def compute_cluster_separation(cluster_series) -> dict` | `analysis-bases.md §2.3` |
| Polarize activity | `def compute_polarize_activity(polarize_counts) -> float` | `analysis-bases.md §2.4` |
| Depolarize activity | `def compute_depolarize_activity(depolarize_counts) -> float` | `analysis-bases.md §2.5` |
| Opinion dispersion | `def compute_opinion_dispersion(agent_opinions) -> float` | `analysis-bases.md §2.6` |
| Quality checks | `compute_api_quality(actions, rag_contexts)` validates the shared special schema; RAG coverage is optional for Rule | `analysis-bases.md §2.7` |

## §3 Analysis Dimensions

Analyze polarization, mean opinion, cluster separation, polarize/depolarize
activity, and per-agent opinion trajectories.

## §4 Phase Analysis

Use initialization, reinforcement, cluster formation, depolarizing response, and
terminal state phases from `analysis-bases.md §4`.

## §5 Cross-Variant Comparison

Rule is compared with LLM, RuleLLM, and Rag on polarization path, activity
composition, and final opinion dispersion.

## §6 Expected Results and Validation Criteria

A full Rule sample should complete 200 rounds and produce finite polarization,
cluster, activity, and opinion series. Missing metric directories, empty series,
invalid JSON, mismatched series lengths, and out-of-range state fail explicitly.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_echochamber_dynamics.png`, `02_echochamber_analysis.png`, and
`03_summary.png`.
