# EchoChamber Rule Variant — analysis.md

## §1 Analysis Objectives

1. Measure baseline polarization dynamics under deterministic rule-based agents.
2. Confirm Sunstein (2001) group polarization: PI increases when destabilizing agents dominate.
3. Quantify BridgeBuilder effectiveness as a function of cluster separation.
4. Establish Rule variant as the parameter-sweep baseline for comparison with LLM/RuleLLM/Rag.

## §2 Metric → Function Mapping

| Metric                         | Function                                                        | analysis-bases.md ref |
|--------------------------------|-----------------------------------------------------------------|-----------------------|
| Polarization Index (PI)        | `polarization_index(polarization_history)`                      | §2.1                  |
| Cluster Separation (CS)        | `cluster_separation(opinion_list)`                              | §2.2                  |
| Mean Opinion Drift (MOD)       | `mean_opinion_drift(mean_opinion_history)`                      | §2.3                  |
| Cross-Cutting Exposure (CCE)   | `cross_cutting_exposure(opinion_list, center_threshold=0.3)`    | §2.4                  |
| Polarization Velocity (PV)     | `polarization_velocity(polarization_history)`                   | §2.5                  |
| Depolarizer Effectiveness (DE) | `depolarizer_effectiveness(depolarize_counts, polarize_counts)` | §2.6                  |
| Opinion Variance (OV)          | `opinion_variance(opinion_list)`                                | §2.7                  |

## §3 Variant-Specific Notes

- Rule variant produces fully deterministic results given fixed random seed — ideal for parameter sweep experiments.
- Ideologue opinion converges to ±1 within ~20–30 rounds due to extremity boost; Conformist tracks cluster mean.
- BridgeBuilder depolarization intensity scales linearly with cluster separation — most effective after clusters form.
- CriticalThinker depolarization activates only when PI > 0.3 — passive in low-polarization environments.
- PassiveFollower introduces stochastic variability via `random.random() < engagement_probability` check; all other agents are deterministic.

## §4 Expected Ranges

| Metric | Expected Range | Interpretation                                               |
|--------|----------------|--------------------------------------------------------------|
| PI     | 0.2 – 0.8      | Rises from initial_polarization toward equilibrium           |
| CS     | 0.5 – 1.8      | Moderate (0.5) to strong bifurcation (>1.5) by end of run    |
| MOD    | 0.0 – 0.3      | Near 0 if symmetric composition; higher if asymmetric        |
| CCE    | 0.1 – 0.5      | Declines from initial moderate distribution                  |
| PV     | 0.005 – 0.05   | Slow stable dynamics; high only during transition phases     |
| DE     | 0.2 – 0.5      | Below 0.5 if Ideologues + Conformists outnumber stabilizers  |
| OV     | 0.1 – 0.35     | Rises as bimodal distribution forms; max near uniform spread |

## §5 References

See `analysis-bases.md §2` for full metric derivations and simulation-bases.md §4 for agent parameter sources.
