# LiquidityDryup — Rule Variant Analysis Guide

## §1 Analysis Objectives

The Rule variant provides the most mechanically deterministic dry-up cascade — withdrawal is triggered precisely at `|return| > volatility_threshold`. Analysis goals:

1. Confirm the spiral mechanics: verify that MWF drives LRI down, which drives MPI up.
2. Measure PAD — how far prices deviate from fundamental during dry-up.
3. Establish baseline LPD (dry-up duration) for cross-variant comparison.
4. Quantify wealth redistribution (WDI): ValueTrader and early MarketMaker exits gain; LiquiditySeeker loses.
5. Validate the liquidity amplification formula: MPI should be proportional to `1/LRI`.

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

- **Deterministic cascade**: Given the same random seed and noise, the Rule spiral is fully reproducible. Run 5 times with different seeds for distribution estimates.
- **Spiral validation**: Plot MWF, LRI, and MPI on the same time axis. MWF should lead LRI by 1 round; LRI should lead MPI by 0 rounds (same round).
- **ValueTrader recovery**: Identify the round when ValueTrader first provides liquidity (`|deviation| > trade_threshold`). This is the recovery trigger. Measure LPD from onset to this round.
- **MPI amplification check**: Verify `MPI_dryup / MPI_normal ≈ liquidity_factor_max / 1.0 ≈ (100 / min_liquidity)`.
- **LiquiditySeeker execution**: Track how `liquidity_adjustment` shrinks LiquiditySeeker orders during dry-up. This is the "missing demand" that prevents price recovery.

---

## §4 Expected Ranges

| Metric         | Expected Range | Red Flag                                        |
|----------------|----------------|-------------------------------------------------|
| LRI minimum    | 0.05–0.20      | > 0.60 (no dry-up — check volatility_threshold) |
| MWF maximum    | 0.7–1.0        | < 0.3 (weak withdrawal)                         |
| PAD            | 0.10–0.25      | < 0.03 (no dislocation)                         |
| LPD            | 10–25 rounds   | 0 (no dry-up) or > 60 (permanent)               |
| WDI            | 0.25–0.45      | < 0.05 (no redistribution)                      |
| MPI multiplier | 3–8×           | < 1.5× (weak amplification)                     |

Rule variant provides the baseline. All other variants should show higher LRI, shorter LPD, smaller PAD.

---

## §5 References

- analysis-bases.md §2.1 (LRI); §2.2 (MWF); §2.3 (MPI); §2.4 (PAD); §2.5 (LPD); §2.6 (WDI); §2.7 (LPI)
- Grossman & Miller (1988). doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x)
- Brunnermeier & Pedersen (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)
- Kyle (1985). doi:[10.2307/1913210](https://doi.org/10.2307/1913210)
- Amihud (2002). doi:[10.1016/S1386-4181(01)00024-6](https://doi.org/10.1016/S1386-4181(01)00024-6)
