# LiquidityDryup — RuleLLM Variant Analysis Guide

## §1 Analysis Objectives

The RuleLLM variant tests whether rule-anchored LLM agents produce a more consistent liquidity spiral than pure LLM while adding contextual modulation. Analysis goals:

1. Confirm that LRI falls below 0.5 in most runs (rule anchor ensures withdrawal triggers).
2. Compare LPD with Rule — rule-anchoring should maintain similar cascade onset but LLM may speed recovery.
3. Measure whether LLM quantity modulation changes PAD relative to Rule.
4. Assess variance reduction vs. LLM variant — RuleLLM should show narrower metric distributions.
5. Compare LPI_MarketMaker: RuleLLM may show more binary withdrawal (rule-triggered) vs. LLM (partial).

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

- **Rule anchor effect**: LRI should fall below 0.5 in the majority of runs (unlike pure LLM where some runs may show no dry-up).
- **LPD comparison**: If LPD(RuleLLM) < LPD(Rule), the LLM is accelerating recovery (LLM ValueTrader more aggressive). If LPD(RuleLLM) > LPD(Rule), the LLM is slowing recovery.
- **MWF pattern**: Expect more binary MWF (0 or 1 per agent) than LLM variant due to rule threshold.
- **LPI stability**: LPI_MarketMaker variance should be smaller than LLM variant.
- **Cross-validate with Rule**: If PAD(RuleLLM) ≈ PAD(Rule), LLM modulation has negligible effect. If significantly lower, LLM ValueTrader is providing more crisis liquidity.

---

## §4 Expected Ranges

| Metric      | Expected Range | Red Flag                               |
|-------------|----------------|----------------------------------------|
| LRI minimum | 0.05–0.25      | > 0.60 in most runs (rule not working) |
| MWF maximum | 0.6–1.0        | < 0.3                                  |
| PAD         | 0.09–0.22      | < 0.03                                 |
| LPD         | 9–22 rounds    | 0 (rule should ensure dry-up)          |
| WDI         | 0.22–0.42      | < 0.05                                 |

RuleLLM should show narrower confidence intervals than LLM but slightly wider than Rule.

---

## §5 References

- analysis-bases.md §2.1 (LRI); §2.2 (MWF); §2.3 (MPI); §2.4 (PAD); §2.5 (LPD); §2.6 (WDI); §2.7 (LPI)
- Brunnermeier & Pedersen (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)
- Grossman & Miller (1988). doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x)
