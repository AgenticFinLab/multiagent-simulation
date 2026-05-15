# EchoChamber LLM Variant — analysis.md

## §1 Analysis Objectives

1. Assess whether LLM persona reasoning produces higher or lower polarization than the Rule baseline.
2. Evaluate cross-agent heterogeneity in LLM variant: do agents deviate from their assigned persona over rounds?
3. Compare LLM-generated `reasoning` text across agent types to detect persona consistency.
4. Measure whether LLM Ideologue overshoots Rule Ideologue in polarization contribution.

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

- LLM action decisions are stochastic across runs even with identical initial conditions; multiple runs needed for statistical comparison with Rule variant.
- LLMPassiveBystander tends to produce more "neutral" actions than Rule PassiveFollower, reducing stochastic polarization noise.
- LLMCriticalThinker may produce more nuanced depolarization reasoning, but the quantitative intensity output may not differ significantly from Rule.
- LLMBridgeBuilder effectiveness is limited by the fact that opinion update formulas are hardcoded — LLM only controls `action_type` and `intensity`.
- Failed LLM parses (all 3 retries) default to neutral action, introducing a floor on stochastic depolarization.

## §4 Expected Ranges

| Metric | Expected Range | Interpretation                                                           |
|--------|----------------|--------------------------------------------------------------------------|
| PI     | 0.2 – 0.9      | Wider than Rule due to LLM stochasticity; may overshoot in some runs     |
| CS     | 0.4 – 2.0      | Can exceed Rule CS if Ideologue persona produces stronger extremity      |
| MOD    | 0.0 – 0.4      | Wider range than Rule; persona asymmetries may produce directional drift |
| CCE    | 0.05 – 0.5     | May decline faster than Rule if LLM Conformist follows majority strongly |
| PV     | 0.005 – 0.08   | Higher than Rule in some runs due to LLM reasoning variability           |
| DE     | 0.15 – 0.55    | Slightly lower DE if LLM Bystander defaults to neutral more often        |
| OV     | 0.1 – 0.40     | Higher upper bound than Rule due to persona-induced extremity            |

## §5 References

See `analysis-bases.md §2` for full metric derivations and simulation-bases.md §4 for agent parameter sources.
