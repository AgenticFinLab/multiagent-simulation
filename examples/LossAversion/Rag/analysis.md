# LossAversion — Rag Variant Analysis Guide

## §1 Analysis Objectives

The Rag variant is the expected optimum for bias reduction — agents retrieve Prospect Theory and Disposition Effect literature, enabling self-recognition of their own behavioural biases. Analysis goals:

1. Confirm LAI is the lowest across all 4 variants (Rag should show most debiasing).
2. Measure NCE — expected to be 0.30–0.60, the largest correction.
3. Assess whether KB composition affects DEI (retrieval of Odean 1998 → more loser-selling).
4. Check WPI — expected highest across variants (smallest wealth penalty).
5. Evaluate KB retrieval quality: are the right papers being retrieved for each agent type?

---

## §2 Metric → Function Mapping

| Metric | Full Name                       | analysis-bases.md Ref | Python Function                     | Key Inputs                                             |
|--------|---------------------------------|-----------------------|-------------------------------------|--------------------------------------------------------|
| LAI    | Loss Aversion Index             | §2.1                  | `loss_aversion_index()`             | trade_history, agent_type='RagLossAverseInvestor'      |
| DEI    | Disposition Effect Index        | §2.2                  | `disposition_effect_index()`        | trade_history, price_history, agent_states             |
| BER    | Break-Even Escalation Ratio     | §2.3                  | `break_even_escalation_ratio()`     | trade_history, agent_type='RagBreakEvenTrader'         |
| NCE    | Narrative Correction Efficiency | §2.4                  | `narrative_correction_efficiency()` | lai_variant, lai_rule_baseline                         |
| VAF    | Volatility Amplification Factor | §2.5                  | `volatility_amplification_factor()` | price_history, fundamental, rational_benchmark_std     |
| WPI    | Wealth Penalty Index            | §2.6                  | `wealth_penalty_index()`            | agent_states, final_price, biased_types, rational_type |

---

## §3 Variant-Specific Notes

- **KB composition is critical**: The knowledge base must include Odean (1998) with clear PGR/PLR data and Barberis & Xiong (2009) documenting break-even costs. Without these, NCE will not reach the 0.30–0.60 range.
- **NCE is the key diagnostic**: Rag variant's NCE measures the incremental debiasing power of retrieval-augmented reasoning over rule + LLM.
- **Self-correction check**: Manually inspect a sample of LLM reasoning traces. If `LossAverseInvestor` agents cite retrieved Odean (1998) and adjust sell fractions, the RAG mechanism is functioning.
- **BER unique behaviour**: `BreakEvenTrader` may actually *reduce* escalation when Barberis & Xiong (2009) is retrieved — the paper explicitly shows break-even gambling destroys value. Monitor BER carefully.
- **DEI direction**: Even with KB retrieval, DEI should remain > 1.0 — full debiasing is unlikely. If DEI ≈ 1.0, the KB is over-correcting.

---

## §4 Expected Ranges

| Metric | Expected Range | Red Flag                                          |
|--------|----------------|---------------------------------------------------|
| LAI    | 1.4–2.0        | > 2.3 (KB not reducing bias) or < 1.0             |
| DEI    | 1.0–1.8        | < 1.0 (over-correction) or > 2.5 (KB not working) |
| BER    | 1.0–2.0        | > 3.5 (KB not retrieved for BreakEvenTrader)      |
| NCE    | 0.30–0.60      | < 0.15 (KB quality poor) or > 0.90                |
| VAF    | 1.2–1.8        | > 3.0                                             |
| WPI    | 0.85–0.95      | < 0.80 (Rag should outperform LLM)                |

Rag variant should produce the lowest LAI, BER, VAF and highest NCE, WPI across all 4 variants.

---

## §5 References

- analysis-bases.md §2.1 (LAI); §2.2 (DEI); §2.3 (BER); §2.4 (NCE); §2.5 (VAF); §2.6 (WPI)
- Kahneman, D., & Tversky, A. (1979). doi:[10.2307/1914185](https://doi.org/10.2307/1914185)
- Odean, T. (1998). doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)
- Barberis, N., & Xiong, W. (2009). doi:[10.1111/j.1540-6261.2009.01448.x](https://doi.org/10.1111/j.1540-6261.2009.01448.x)
- Shefrin, H., & Statman, M. (1985). doi:[10.1111/j.1540-6261.1985.tb05002.x](https://doi.org/10.1111/j.1540-6261.1985.tb05002.x)

## §6 Expected Results and Validation

The accepted RAG sample should complete 200 rounds with clean parse quality and usable retrieval context. It should show the strongest narrative correction among API modes, but not erase the phenomenon entirely. Existing accepted RAG output can be inherited because this pass only updates analysis documentation.

## §7 Visualization Catalogue

`Rag/analysis.py` reuses the Rule analysis pipeline and writes `lossaversion_analysis.png`. RAG reports should add retrieval-quality notes and compare LAI/DEI/BER against RuleLLM.
