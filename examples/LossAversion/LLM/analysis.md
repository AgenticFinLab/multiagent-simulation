# LossAversion — LLM Variant Analysis Guide

## §1 Analysis Objectives

The LLM variant tests whether language model agents can reproduce the disposition effect through narrative prompting alone, without hard-coded thresholds. Analysis goals:

1. Measure whether LAI from LLM agents falls below Rule-variant baseline (expected: yes, due to contextual moderation).
2. Quantify NCE — the degree to which LLM reduces observed loss aversion vs. the Rule variant.
3. Assess variability of LAI, DEI, and BER across multiple runs (LLM stochasticity).
4. Determine whether LLM agents produce qualitatively correct disposition-effect direction (LAI > 1.0, DEI > 1.0).
5. Compare WPI — LLM variant should produce slightly higher WPI (lower wealth penalty) than Rule.

---

## §2 Metric → Function Mapping

| Metric | Full Name                       | analysis-bases.md Ref | Python Function                     | Key Inputs                                             |
|--------|---------------------------------|-----------------------|-------------------------------------|--------------------------------------------------------|
| LAI    | Loss Aversion Index             | §2.1                  | `loss_aversion_index()`             | trade_history, agent_type='LLMLossAverseInvestor'      |
| DEI    | Disposition Effect Index        | §2.2                  | `disposition_effect_index()`        | trade_history, price_history, agent_states             |
| BER    | Break-Even Escalation Ratio     | §2.3                  | `break_even_escalation_ratio()`     | trade_history, agent_type='LLMBreakEvenTrader'         |
| NCE    | Narrative Correction Efficiency | §2.4                  | `narrative_correction_efficiency()` | lai_variant, lai_rule_baseline                         |
| VAF    | Volatility Amplification Factor | §2.5                  | `volatility_amplification_factor()` | price_history, fundamental, rational_benchmark_std     |
| WPI    | Wealth Penalty Index            | §2.6                  | `wealth_penalty_index()`            | agent_states, final_price, biased_types, rational_type |

---

## §3 Variant-Specific Notes

- **Run ≥ 5 simulations**: LLM temperature introduces significant run-to-run variance. Report mean ± std for all metrics.
- **NCE requires Rule baseline**: Run Rule variant first with identical simulation parameters; store LAI as `lai_rule_baseline`.
- **Qualitative check**: Even if LAI < 2.0, verify the direction is correct (LAI > 1.0, DEI > 1.0). If DEI < 1.0, check system prompt framing.
- **Parse failure rate**: Log how often LLM parse fails (3 retries exhausted → default "hold"). High parse-failure rate distorts all metrics toward passivity.
- **LLMRationalTrader check**: Verify `LLMRationalTrader` produces near-zero LAI and near-1.0 DEI — a sanity check that the rational prompt is functioning.

---

## §4 Expected Ranges

| Metric | Expected Range | Red Flag                                |
|--------|----------------|-----------------------------------------|
| LAI    | 1.6–2.4        | < 1.0 (no bias) or > 3.0 (exceeds Rule) |
| DEI    | 1.2–2.0        | < 1.0 (reverse disposition)             |
| BER    | 1.2–2.5        | < 1.0                                   |
| NCE    | 0.15–0.40      | < 0 (LLM amplifies bias) or > 0.9       |
| VAF    | 1.2–2.0        | < 1.0 or > 3.0                          |
| WPI    | 0.80–0.93      | < 0.70                                  |

LLM variant should show all metrics between Rule and Rag in magnitude (Rule most biased, Rag least).

---

## §5 References

- analysis-bases.md §2.1 (LAI); §2.2 (DEI); §2.3 (BER); §2.4 (NCE); §2.5 (VAF); §2.6 (WPI)
- Kahneman, D., & Tversky, A. (1979). doi:[10.2307/1914185](https://doi.org/10.2307/1914185)
- Odean, T. (1998). doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)
- Barberis, N., & Xiong, W. (2009). doi:[10.1111/j.1540-6261.2009.01448.x](https://doi.org/10.1111/j.1540-6261.2009.01448.x)

## §6 Expected Results and Validation

The accepted LLM sample should complete 200 rounds with clean parse quality and no fallback holds. Metrics should generally show weaker bias than Rule but preserve correct directionality: LAI > 1.0 and DEI > 1.0. Existing accepted LLM output can be inherited because this pass only updates analysis documentation.

## §7 Visualization Catalogue

`LLM/analysis.py` reuses the Rule analysis pipeline and writes `lossaversion_analysis.png`. LLM reports may add action-distribution, parse-quality, and narrative-correction summaries.
