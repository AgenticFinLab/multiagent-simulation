# EchoChamber RuleLLM Analysis Plan

## §1 Objectives

The RuleLLM analysis checks whether explicit social-dynamics rules constrain
LLM behavior while preserving the special schema.

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

Analyze formula adherence, action validity, polarization path, role-specific
activity, and parse retry/failure rates.

## §4 Phase Analysis

Compare phase timing with Rule to see whether explicit rules preserve
deterministic dynamics.

## §5 Cross-Variant Comparison

RuleLLM is expected to sit between Rule and LLM: formula-guided but still
language-model mediated.

## §6 Expected Results and Validation Criteria

A full RuleLLM sample should complete 200 rounds and keep every social action
within the special schema.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`,
`01_echochamber_dynamics.png`, `02_echochamber_analysis.png`, and
`03_summary.png`.
