# DotComBubble Rule Variant — analysis.md

## §1 Analysis Objectives

Quantify bubble formation, peak amplitude, crash severity, and agent-wealth divergence produced by the Rule variant's deterministic threshold rules. All metrics are defined in `analysis-bases.md §2`.

## §2 Metric → Function Mapping

| Metric                              | Function                                                                   | analysis-bases.md ref |
|-------------------------------------|----------------------------------------------------------------------------|-----------------------|
| BAI (Bubble Amplitude Index)        | `bubble_amplitude_index(price_history, fundamental)`                       | §2.1                  |
| BD (Bubble Duration)                | `bubble_duration(price_history, fundamental, bubble_threshold=0.10)`       | §2.2                  |
| CS (Crash Severity)                 | `crash_severity(price_history)`                                            | §2.3                  |
| MAF (Momentum Amplification Factor) | `momentum_amplification_factor(agent_volume_by_type, bubble_rounds)`       | §2.4                  |
| SSR (Short Squeeze Resistance)      | `short_squeeze_resistance(short_seller_orders, momentum_sign_history)`     | §2.5                  |
| RT (Recovery Time)                  | `recovery_time(price_history, fundamental, recovery_threshold=0.10)`       | §2.6                  |
| WDI (Wealth Divergence Index)       | `wealth_divergence_index(agent_final_states, final_price, initial_wealth)` | §2.7                  |

## §3 Rule-Variant-Specific Notes

- **NewEconomyEvangelist (§4.1)**: Extreme hold rule (sell only at δ < −0.30) inflates BAI and BD — maximum destabilising effect with pure rules.
- **IPOFlipper (§4.2)**: Asymmetric buy-low/flip-high pattern contributes a secondary MAF spike; volume visible in `agent_volume_by_type`.
- **MomentumFollower (§4.3)**: 1-period momentum threshold 0.02 is sensitive to noise — SSR can be low if momentum reverses frequently.
- **SkepticalValueInvestor (§4.4) + ShortSeller (§4.5)**: Together supply corrective selling; their final WDI contribution should be positive (wealth gain relative to index).

## §4 Expected Ranges

| Metric | Rule-Variant Expected Range | Interpretation                                               |
|--------|-----------------------------|--------------------------------------------------------------|
| BAI    | 0.5 – 1.5                   | 50–150% above fundamental at peak                            |
| BD     | 20 – 50 rounds              | Multi-phase bubble; weak γ = 0.005 sustains                  |
| CS     | 0.40 – 0.70                 | 40–70% crash from peak                                       |
| MAF    | 0.35 – 0.60                 | Momentum volume fraction during bubble                       |
| SSR    | 0.30 – 0.60                 | Short sellers persist through moderate momentum              |
| RT     | 10 – 30 rounds              | Post-crash re-convergence                                    |
| WDI    | −0.3 – +0.3                 | Negative during bubble; positive post-crash for value/shorts |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.
