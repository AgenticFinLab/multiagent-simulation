# LiquidityDryup — LLM Variant Analysis Guide

## §1 Analysis Objectives

The LLM variant tests whether language model agents can reproduce the liquidity spiral through narrative reasoning about stress signals. Analysis goals:

1. Determine whether LLM MarketMakers withdraw in response to stress signals — does the spiral occur?
2. Measure whether LLM coordination produces a faster or slower cascade than the Rule baseline.
3. Assess variance across runs — LLM stochasticity should produce wider metric distributions than Rule.
4. Compare LPD (dry-up duration) — LLM ValueTrader may provide liquidity sooner if the prompt is opportunistic.
5. Identify whether LLM MMs show partial withdrawal (non-binary `provides_liquidity`) that differs from rule binary.

---

## §2 Metric → Function Mapping

| Metric | Full Name                        | analysis-bases.md Ref | Python Function                      | Key Inputs                                         |
|--------|----------------------------------|-----------------------|--------------------------------------|----------------------------------------------------|
| LRI    | Liquidity Ratio Index            | §2.1                  | `liquidity_ratio_index()`            | liquidity_history, base_liquidity, n_market_makers |
| MWF    | Market Maker Withdrawal Fraction | §2.2                  | `market_maker_withdrawal_fraction()` | agent_states, round_num                            |
| MPI    | Market Price Impact              | §2.3                  | `market_price_impact()`              | price_history, trade_history                       |
| PAD    | Price-Amplitude Dislocation      | §2.4                  | `price_amplitude_dislocation()`      | price_history, fundamental, lri_history            |
| LPD    | Liquidity Persistence Duration   | §2.5                  | `liquidity_persistence_duration()`   | lri_history                                        |
| WDI    | Wealth Distribution Index        | §2.6                  | `wealth_distribution_index()`        | agent_states, final_price                          |
| LPI    | Liquidity Provider Index         | §2.7                  | `liquidity_provider_index()`         | trade_history                                      |

---

## §3 Variant-Specific Notes

- **Run ≥ 5 simulations**: LLM temperature introduces significant run-to-run variance. Report mean ± std for LRI, LPD, PAD.
- **Qualitative cascade check**: If LRI never falls below 0.5 in any run, the LLM is not reproducing the spiral — strengthen withdrawal prompts.
- **Partial withdrawal**: Unlike Rule (binary), LLM MMs may output `provides_liquidity` values between 0 and `base_liquidity`. Track the distribution of partial values.
- **ValueTrader LLM opportunity**: Monitor whether LLM ValueTrader recognises "crisis opportunity" — this may accelerate recovery vs. Rule.
- **LPI diagnostic**: In LLM variant, LPI_MarketMaker may have higher variance than Rule. A bi-modal distribution (0 or `base_liquidity`) suggests LLM binary-style withdrawal; unimodal near `base_liquidity/2` suggests partial.

---

## §4 Expected Ranges

| Metric      | Expected Range | Red Flag                      |
|-------------|----------------|-------------------------------|
| LRI minimum | 0.05–0.30      | > 0.70 (no dry-up in any run) |
| MWF maximum | 0.5–1.0        | < 0.3 (weak withdrawal)       |
| PAD         | 0.08–0.20      | < 0.03                        |
| LPD         | 8–20 rounds    | 0 (no dry-up)                 |
| WDI         | 0.20–0.40      | < 0.05                        |

LLM variant should show wider confidence intervals than Rule for all metrics.

---

## §5 References

- analysis-bases.md §2.1 (LRI); §2.2 (MWF); §2.3 (MPI); §2.4 (PAD); §2.5 (LPD); §2.6 (WDI); §2.7 (LPI)
- Brunnermeier & Pedersen (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)
- Grossman & Miller (1988). doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x)
- Kyle (1985). doi:[10.2307/1913210](https://doi.org/10.2307/1913210)
