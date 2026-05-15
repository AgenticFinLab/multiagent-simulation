# DotComBubble LLM Variant — analysis.md

## §1 Analysis Objectives

Measure how LLM persona-driven decision-making shapes bubble amplitude, duration, crash severity, and momentum amplification relative to the Rule baseline. All metrics defined in `analysis-bases.md §2`.

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

## §3 LLM-Variant-Specific Notes

- **Higher BAI variance**: Language-model reasoning introduces stochastic decisions; BAI may exceed Rule range in high-temperature runs.
- **LLMNewEconomyEvangelist**: Narrative persona sustains buying into late-stage bubble — BD may extend beyond Rule if LLM over-weights positive price signals.
- **LLMMomentumFollower**: SSR is typically lower than Rule — LLM may narrate a "correction incoming" and exit shorts earlier, reducing squeeze resistance.
- **LLMSkepticalValueInvestor**: Fundamental anchoring in language can be robust; WDI contribution similar to Rule but varies by prompt temperature.
- **Cross-run replication**: Re-run 3× and report mean ± std for BAI and BD due to LLM non-determinism.

## §4 Expected Ranges

| Metric | LLM-Variant Expected Range | vs. Rule Baseline                       |
|--------|----------------------------|-----------------------------------------|
| BAI    | 0.4 – 1.8                  | Wider range; higher upper bound         |
| BD     | 18 – 55 rounds             | Slight extension possible               |
| CS     | 0.35 – 0.75                | Slightly wider crash range              |
| MAF    | 0.30 – 0.65                | Similar; persona amplification varies   |
| SSR    | 0.20 – 0.55                | Lower — LLM ShortSeller less persistent |
| RT     | 10 – 35 rounds             | Broader recovery distribution           |
| WDI    | −0.4 – +0.4                | Wider wealth divergence due to variance |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.
