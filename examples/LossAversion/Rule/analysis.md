# LossAversion — Rule Variant Analysis Guide

## §1 Analysis Objectives

The Rule variant provides the maximum-strength expression of loss aversion — all thresholds are deterministic and directly encode `loss_aversion_lambda = 2.25`. Analysis goals:

1. Confirm LAI converges to the theoretical λ ≈ 2.25.
2. Measure disposition effect magnitude (DEI) against Odean (1998) benchmark PGR/PLR ≈ 1.5.
3. Quantify break-even escalation (BER) and its contribution to volatility (VAF).
4. Establish the Rule-variant baseline for cross-variant NCE computation.
5. Measure wealth penalty (WPI) for biased vs. rational agents over 100 rounds.

---

## §2 Metric → Function Mapping

| Metric | Full Name                       | analysis-bases.md Ref | Python Function                     | Key Inputs                                                    |
|--------|---------------------------------|-----------------------|-------------------------------------|---------------------------------------------------------------|
| LAI    | Loss Aversion Index             | §2.1                  | `loss_aversion_index()`             | trade_history, agent_type='LossAverseInvestor'                |
| DEI    | Disposition Effect Index        | §2.2                  | `disposition_effect_index()`        | trade_history, price_history, agent_states                    |
| BER    | Break-Even Escalation Ratio     | §2.3                  | `break_even_escalation_ratio()`     | trade_history, agent_type='BreakEvenTrader'                   |
| VAF    | Volatility Amplification Factor | §2.5                  | `volatility_amplification_factor()` | price_history, fundamental, rational_benchmark_std            |
| WPI    | Wealth Penalty Index            | §2.6                  | `wealth_penalty_index()`            | agent_states, final_price, biased_types, rational_type        |
| SRR    | Sell Rate Ratio                 | §2.7                  | `sell_rate_ratio()`                 | trade_history, price_history, agent_type='LossAverseInvestor' |

---

## §3 Variant-Specific Notes

- **Maximum bias expression**: Rule is the deterministic upper bound for LAI, DEI, and BER. All other variants should show lower values.
- **No LLM variance**: All results are reproducible given the same random seed (noise only from `random.gauss`). Re-run 5 times for stable mean estimates.
- **Break-even timing**: `BreakEvenTrader` activates only when `pnl_pct < –0.05`. Ensure `noise_std` is high enough to generate sufficient loss events — recommend `noise_std ≥ 0.3`.
- **RationalTrader benchmark**: Normalized terminal wealth of `RationalTrader` is the denominator of WPI. Verify `risk_aversion = 0.7` and deviation threshold 0.03 in config.
- **LAI vs. config lambda**: A well-calibrated Rule run should produce LAI ≈ 2.0–2.5. If LAI ≠ `loss_aversion_lambda`, investigate entry-price update logic and sell-fraction settings.

---

## §4 Expected Ranges

| Metric | Expected Range | Red Flag        |
|--------|----------------|-----------------|
| LAI    | 2.0–2.8        | < 1.5 or > 3.5  |
| DEI    | 1.5–2.5        | < 1.0 or > 3.5  |
| BER    | 1.5–3.5        | < 1.0 or > 6.0  |
| VAF    | 0.1–2.5        | ≤ 0.1 or ≥ 4.0  |
| WPI    | 0.75–0.90      | > 1.0 or < 0.60 |
| SRR    | 1.5–2.5        | < 1.0 or > 4.0  |

The Rule variant should consistently yield the highest LAI, DEI, BER, and lowest WPI across all 4 variants.

---

## §5 References

- analysis-bases.md §2.1 (LAI); §2.2 (DEI); §2.3 (BER); §2.5 (VAF); §2.6 (WPI); §2.7 (SRR)
- Kahneman, D., & Tversky, A. (1979). doi:[10.2307/1914185](https://doi.org/10.2307/1914185)
- Odean, T. (1998). doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)
- Barberis, N., & Xiong, W. (2009). doi:[10.1111/j.1540-6261.2009.01448.x](https://doi.org/10.1111/j.1540-6261.2009.01448.x)
- Barber, B. M., & Odean, T. (2000). doi:[10.1111/0022-1082.00226](https://doi.org/10.1111/0022-1082.00226)

## §6 Expected Results and Validation

Valid Rule outputs should complete 200 rounds with valid market records, non-empty price history, and deterministic loss-aversion behavior. They are the baseline for LAI, DEI, BER, VAF, WPI, and SRR comparisons.

## §7 Visualization Catalogue

`Rule/analysis.py → create_visualizations(data, output_path)` produces `summary.json`, `00_investor_bids.png`, `01_lossaversion_dynamics.png`, `02_lossaversion_analysis.png`, and `03_summary.png`. Scenario reports may add LAI/DEI/BER/WPI summary tables when trade-level records are available.
