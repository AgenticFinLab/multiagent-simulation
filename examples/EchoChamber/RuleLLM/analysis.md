# EchoChamber RuleLLM Variant — analysis.md

## §1 Analysis Objectives

1. Assess whether embedded formula prompts constrain LLM behavior to be closer to Rule variant than pure LLM.
2. Measure consistency of intensity outputs: RuleLLM should have narrower variance than LLM variant.
3. Evaluate whether formula-constrained reasoning improves depolarizer effectiveness (BridgeBuilder, CriticalThinker).
4. Compare RuleLLM polarization dynamics to Rule baseline to quantify LLM deviation from deterministic formula.

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

- RuleLLM reasoning text is more formula-explicit than LLM — enables audit of whether agent applied the correct threshold rule.
- Embedded formula prompts tend to constrain intensity outputs closer to Rule values; variance is lower than pure LLM.
- RuleLLMBridgeBuilder tends to apply cluster-separation-based depolarization more consistently than LLMBridgeBuilder.
- RuleLLMPassiveFollower rarely deviates from neutral/low-intensity actions due to explicit engagement-probability instruction.
- Occasional prompt overflow (long system + user prompt) may cause truncation in low-context-window models.

## §4 Expected Ranges

| Metric | Expected Range | Interpretation                                                           |
|--------|----------------|--------------------------------------------------------------------------|
| PI     | 0.2 – 0.75     | Closer to Rule baseline than LLM variant; less overshoot                 |
| CS     | 0.4 – 1.8      | Closer to Rule; lower ceiling than pure LLM                              |
| MOD    | 0.0 – 0.3      | Similar to Rule baseline                                                 |
| CCE    | 0.1 – 0.5      | Closely tracks Rule; formula constraints limit deviation                 |
| PV     | 0.005 – 0.06   | Slightly higher than Rule but lower than LLM                             |
| DE     | 0.25 – 0.55    | Higher DE than LLM variant due to formula-driven depolarizer consistency |
| OV     | 0.1 – 0.35     | Close to Rule; narrower than LLM variant                                 |

## §5 References

See `analysis-bases.md §2` for full metric derivations and simulation-bases.md §4 for agent parameter sources.
