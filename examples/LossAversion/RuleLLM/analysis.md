# LossAversion — RuleLLM Variant Analysis Guide

## §1 Analysis Objectives

The RuleLLM variant tests whether rule-anchored LLM agents maintain the strong bias expression of the Rule variant while allowing LLM narrative modulation. Analysis goals:

1. Confirm LAI remains closer to Rule than to pure LLM (rule anchoring dominates).
2. Measure NCE — expected to be smaller than LLM variant (rule prevents full narrative correction).
3. Assess whether LLM quantity modulation in `BreakEvenTrader` significantly changes BER.
4. Compare WPI — expected between Rule and LLM variants.
5. Evaluate run-to-run variance — expected lower than LLM due to rule anchoring.

---

## §2 Metric → Function Mapping

| Metric | Full Name                       | analysis-bases.md Ref | Python Function                     | Key Inputs                                             |
|--------|---------------------------------|-----------------------|-------------------------------------|--------------------------------------------------------|
| LAI    | Loss Aversion Index             | §2.1                  | `loss_aversion_index()`             | trade_history, agent_type='RuleLLMLossAverseInvestor'  |
| DEI    | Disposition Effect Index        | §2.2                  | `disposition_effect_index()`        | trade_history, price_history, agent_states             |
| BER    | Break-Even Escalation Ratio     | §2.3                  | `break_even_escalation_ratio()`     | trade_history, agent_type='RuleLLMBreakEvenTrader'     |
| NCE    | Narrative Correction Efficiency | §2.4                  | `narrative_correction_efficiency()` | lai_variant, lai_rule_baseline                         |
| VAF    | Volatility Amplification Factor | §2.5                  | `volatility_amplification_factor()` | price_history, fundamental, rational_benchmark_std     |
| WPI    | Wealth Penalty Index            | §2.6                  | `wealth_penalty_index()`            | agent_states, final_price, biased_types, rational_type |

---

## §3 Variant-Specific Notes

- **Rule-anchored LAI**: Because the direction of sell decisions is rule-enforced, LAI should be close to the Rule variant's value. LLM impact is mainly on quantity, not direction.
- **NCE < LLM variant**: Rule gates prevent LLM from ignoring bias triggers. NCE should be 0.10–0.30, not 0.15–0.40 as in pure LLM.
- **BER may be higher**: LLM may choose to escalate more aggressively than the rule formula if the prompt frames recovery as urgent. Monitor for BER > 3.5.
- **Stability**: Fewer parse failures expected — rule provides a default action if LLM fails, reducing passive "hold" distortion.
- **Cross-validate with Rule**: The RuleLLM → Rule comparison isolates pure LLM contribution. If LAI(RuleLLM) ≈ LAI(Rule), LLM has negligible effect.

---

## §4 Expected Ranges

| Metric | Expected Range | Red Flag                          |
|--------|----------------|-----------------------------------|
| LAI    | 1.8–2.5        | < 1.5 (rule not working) or > 3.0 |
| DEI    | 1.3–2.2        | < 1.0                             |
| BER    | 1.3–3.0        | < 1.0 or > 6.0                    |
| NCE    | 0.10–0.30      | > 0.40 (LLM overriding rule)      |
| VAF    | 1.3–2.2        | < 1.0 or > 4.0                    |
| WPI    | 0.78–0.92      | < 0.65                            |

RuleLLM should fall between Rule and LLM for all bias metrics, closer to Rule.

---

## §5 References

- analysis-bases.md §2.1 (LAI); §2.2 (DEI); §2.3 (BER); §2.4 (NCE); §2.5 (VAF); §2.6 (WPI)
- Kahneman, D., & Tversky, A. (1979). doi:[10.2307/1914185](https://doi.org/10.2307/1914185)
- Odean, T. (1998). doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)
- Barberis, N., & Xiong, W. (2009). doi:[10.1111/j.1540-6261.2009.01448.x](https://doi.org/10.1111/j.1540-6261.2009.01448.x)

## §6 Expected Results and Validation

Valid RuleLLM outputs should complete 200 rounds with clean parse quality and metrics closer to Rule than pure LLM. Validation should inspect whether embedded rule guidance keeps LAI and DEI above rational levels while allowing some LLM quantity modulation.

## §7 Visualization Catalogue

`RuleLLM/analysis.py` reuses the Rule analysis pipeline and writes `summary.json`, `00_investor_bids.png`, `01_lossaversion_dynamics.png`, `02_lossaversion_analysis.png`, and `03_summary.png`. Reports may add rule-adherence and quantity-modulation summaries.
