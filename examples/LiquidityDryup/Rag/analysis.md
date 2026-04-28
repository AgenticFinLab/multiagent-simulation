# LiquidityDryup — Rag Variant Analysis Guide

## §1 Analysis Objectives

The Rag variant tests whether historical crisis knowledge moderates the liquidity spiral. It should produce the highest minimum LRI, shortest LPD, and smallest PAD across all variants. Analysis goals:

1. Confirm LRI minimum is higher than all other variants (KB moderates MarketMaker withdrawal).
2. Measure LPD — expected shortest due to KB-informed ValueTrader early entry.
3. Assess KB retrieval quality: are the right historical episodes retrieved for current conditions?
4. Check whether MarketMaker partial withdrawal (non-zero `provides_liquidity` during stress) is observed.
5. Measure WDI — expected lowest redistribution due to shorter, shallower spiral.

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

- **KB composition is critical**: The knowledge base must include episodes with documented recovery timelines. Without post-crisis recovery data, the Rag variant cannot demonstrate faster LPD than Rule.
- **ValueTrader KB effect**: Manually inspect reasoning traces — does ValueTrader cite historical recovery evidence when entering? If yes, KB is functioning as designed.
- **Partial MarketMaker withdrawal**: Inspect `provides_liquidity` values for MarketMaker during stress rounds. Rag variant should show more cases of partial provision (e.g., `provides_liquidity = 10` instead of 0) when KB shows rapid reversal precedents.
- **LPD comparison**: If LPD(Rag) ≈ LPD(Rule), the KB is not enabling faster recovery. Check that historical episodes with LPD < 10 are in the KB.
- **LRI minimum check**: If LRI(Rag) minimum ≈ LRI(Rule), KB is not moderating withdrawal. Check MarketMaker prompt KB injection.

---

## §4 Expected Ranges

| Metric      | Expected Range | Red Flag                                                    |
|-------------|----------------|-------------------------------------------------------------|
| LRI minimum | 0.10–0.30      | < 0.05 (KB not moderating withdrawal) or > 0.70 (no dry-up) |
| MWF maximum | 0.4–0.8        | = 1.0 in all runs (KB not partially moderating)             |
| PAD         | 0.07–0.18      | > 0.25 (Rag not improving on Rule)                          |
| LPD         | 6–15 rounds    | > 20 (KB not accelerating recovery)                         |
| WDI         | 0.18–0.35      | > 0.45 (Rag not reducing redistribution)                    |

Rag variant should be the best performer across all metrics — highest LRI, shortest LPD, lowest PAD, lowest WDI.

---

## §5 References

- analysis-bases.md §2.1 (LRI); §2.2 (MWF); §2.3 (MPI); §2.4 (PAD); §2.5 (LPD); §2.6 (WDI); §2.7 (LPI)
- Brunnermeier & Pedersen (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)
- Grossman & Miller (1988). doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x)
- Amihud (2002). doi:[10.1016/S1386-4181(01)00024-6](https://doi.org/10.1016/S1386-4181(01)00024-6)
- simulation-bases.md §8 (Historical Case Studies — source material for KB)
