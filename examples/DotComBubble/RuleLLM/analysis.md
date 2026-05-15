# DotComBubble RuleLLM Variant — analysis.md

## §1 Analysis Objectives

Evaluate whether rule boundaries reduce metric variance relative to pure LLM while preserving flexibility beyond pure Rule. All metrics defined in `analysis-bases.md §2`.

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

## §3 RuleLLM-Variant-Specific Notes

- **Rule fidelity check**: Verify that `RuleLLMNewEconomyEvangelist` sells only when δ < −0.30 — LLM should not override direction boundary.
- **Quantity variation**: LLM adjusts order quantities within rule-permitted direction; `agent_volume_by_type` will show less uniform order sizes vs. Rule.
- **MAF comparison**: MAF should be similar to Rule; meaningful deviation indicates LLM overrode momentum signal via contextual reasoning.
- **SSR stability**: Higher than pure LLM — embedded short threshold prevents early cover. Compare directly with LLM/analysis.md §4.
- **BD convergence**: BD variance should be ≤ LLM variant variance; use 3-run std as convergence test.

## §4 Expected Ranges

| Metric | RuleLLM-Variant Expected Range | vs. Rule Baseline                                            |
|--------|--------------------------------|--------------------------------------------------------------|
| BAI    | 0.5 – 1.6                      | Close to Rule; slight upside from LLM quantity amplification |
| BD     | 20 – 52 rounds                 | Slightly wider than Rule; tighter than LLM                   |
| CS     | 0.40 – 0.72                    | Near Rule; LLM may delay crash onset                         |
| MAF    | 0.35 – 0.62                    | Near Rule                                                    |
| SSR    | 0.28 – 0.60                    | Between Rule and LLM                                         |
| RT     | 10 – 32 rounds                 | Near Rule                                                    |
| WDI    | −0.3 – +0.35                   | Near Rule; minor LLM deviation                               |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.
