# FlashCrash Rule — Explain

## §1 Overview

| Item             | Description                                                                                                                |
|------------------|----------------------------------------------------------------------------------------------------------------------------|
| **Variant**      | Rule                                                                                                                       |
| **Scenario**     | Flash Crash                                                                                                                |
| **Phenomenon**   | Rapid intraday price collapse and recovery driven by liquidity withdrawal and stop-loss cascades                           |
| **Agent count**  | 6 types: HighFrequencyTrader, MarketMaker, AlgorithmicTrader, StopLossTrader, FundamentalTrader, RetailTrader              |
| **Market model** | Liquidity-sensitive price impact: `P(t+1) = P(t) + base_price_impact × net_demand × liquidity_factor + mean_reversion + ε` |
| **Key feature**  | `provides_liquidity` flag from MarketMaker drives `liquidity_factor`; withdrawal amplifies all subsequent orders           |
| **Determinism**  | High — all thresholds and formulae are fixed                                                                               |

## §2 Theory → Implementation Mapping

| Theory construct           | simulation-bases.md reference | Rule implementation                                                                                                             |
|----------------------------|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Momentum detection         | §4.1 HighFrequencyTrader      | `signal = short_momentum × momentum_sensitivity; quantity = signal × base_position_size × speed_advantage` clamped ±60          |
| Liquidity withdrawal       | §4.2 MarketMaker              | `if price_return > volatility_threshold: provides_liquidity=False; quantity = -position × 0.3`                                  |
| Trend amplification        | §4.3 AlgorithmicTrader        | `quantity = trend × trend_sensitivity × base_position_size × trend_multiplier` clamped ±40                                      |
| Stop-loss cascade          | §4.4 StopLossTrader           | `if price < stop_price and position > 0: quantity = -position; stop_triggered = True`                                           |
| Value stabilisation        | §4.5 FundamentalTrader        | `deviation = (fundamental-price)/fundamental; quantity = deviation × base_position_size × value_sensitivity × value_multiplier` |
| Noise background           | §4.6 RetailTrader             | `quantity = gauss(0, noise_std) + (-position_mean_reversion × position)` clamped ±15; every `trade_frequency` rounds            |
| Liquidity-sensitive market | §3 Market Design              | `liquidity_factor = high_impact_multiplier if total_liquidity < low_liquidity_threshold else 1.0 + ...`                         |

## §3 Agent Interaction Flow

```
Round t:
  Market ──broadcast(price, prev_price, return, liquidity, fundamental)──► All Investors
  All Investors ──submit(quantity, provides_liquidity)──► Market

  total_liquidity = Σ provides_liquidity flags
  liquidity_factor ↑ when total_liquidity < low_liquidity_threshold
  MarketMaker toggles provides_liquidity based on price_return vs volatility_threshold
```

## §4 Crash Mechanism (Rule Logic)

```
Phase 1 (Normal):
  HFT.short_momentum ≈ 0 → small quantity
  MarketMaker.price_return < volatility_threshold → provides_liquidity=True → liquidity_factor ≈ 1

Phase 2 (Trigger):
  HFT.short_momentum > 0 threshold → sell burst (quantity up to −60)
  price_return > volatility_threshold → MarketMaker.provides_liquidity = False

Phase 3 (Cascade):
  total_liquidity < low_liquidity_threshold → liquidity_factor = high_impact_multiplier
  AlgorithmicTrader.trend → adds sell pressure
  StopLossTrader: price < stop_price → sell all (−position)

Phase 4 (Recovery):
  price << fundamental → FundamentalTrader.deviation > value_threshold → buy
  price_return settles → MarketMaker restores liquidity
```

## §5 Key Parameters

| Parameter                 | Location                   | Effect on crash                                   |
|---------------------------|----------------------------|---------------------------------------------------|
| `volatility_threshold`    | MarketMaker extras         | Lower → earlier withdrawal → deeper crash         |
| `low_liquidity_threshold` | Market extras              | Higher → longer amplified period                  |
| `high_impact_multiplier`  | Market extras              | Higher → more severe crash                        |
| `stop_loss_percent`       | StopLossTrader extras      | Lower → triggers earlier; higher → cascades later |
| `momentum_sensitivity`    | HighFrequencyTrader extras | Higher → stronger initial signal                  |
| `value_threshold`         | FundamentalTrader extras   | Lower → earlier recovery entry                    |

## §6 Files

| File                                     | Purpose                                |
|------------------------------------------|----------------------------------------|
| `players.py`                             | Market + 6 rule-based investor classes |
| `run_flash_crash.py`                     | Entry point                            |
| `configs/FlashCrash/Rule/simulation.yml` | Main simulation config                 |
| `configs/FlashCrash/Rule/players.yml`    | Agent parameter definitions            |
| `configs/FlashCrash/Rule/topology.yml`   | Star topology                          |
| `simulation-bases.md`                    | Full theoretical foundations           |
| `analysis-bases.md`                      | Metrics and analysis guide             |

## §7 Running

```bash
python examples/FlashCrash/Rule/run_flash_crash.py -c configs/FlashCrash/Rule/simulation.yml
```

## §8 Expected Behaviour

| Phase    | Rounds | Key observable                                           |
|----------|--------|----------------------------------------------------------|
| Normal   | 1–10   | Price ≈ fundamental; liquidity = full                    |
| Trigger  | 11–15  | HFT begins selling; MarketMaker first stress             |
| Cascade  | 16–25  | liquidity_factor jumps; stop-losses fire in waves        |
| Trough   | 26–30  | Min price; max price deviation from fundamental          |
| Recovery | 31–50  | FundamentalTrader buying; MarketMaker restores liquidity |

## §9 References

1. Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). *Journal of Finance*, 72(3), 967-998. doi:10.1111/jofi.12498
2. Grossman, S. J., & Miller, M. H. (1988). *Journal of Finance*, 43(3), 617-633. doi:10.1111/j.1540-6261.1988.tb02607.x
3. De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). *Journal of Finance*, 45(2), 379-395.
4. Brunnermeier, M. K., & Pedersen, L. H. (2005). *Journal of Finance*, 60(4), 1825-1863.
5. Shiller, R. J. (1981). *American Economic Review*, 71(3), 421-436.
6. Black, F. (1986). *Journal of Finance*, 41(3), 529-543.
