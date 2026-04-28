# FlashCrash2010 Rule — Explain

## §1 Overview

| Item             | Description                                                                                                                             |
|------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**      | Rule                                                                                                                                    |
| **Scenario**     | FlashCrash2010                                                                                                                          |
| **Phenomenon**   | May 6, 2010 Flash Crash — order-book depth collapse, HFT withdrawal, stop-loss cascade                                                  |
| **Agent count**  | 5 types: HFTMarketMaker, MomentumChaser, FundamentalTrader, StopLossTrader, NoiseTrader                                                 |
| **Market model** | Order-book depth model: `P(t+1) = P(t) + λ × NetFlow / Depth(t) + γ × (F − P) + ε`; `Depth` driven by volatility and HFT participation  |
| **Key feature**  | `HFTMarketMaker.agent_type = "hft"` drives `hft_participation`; withdrawal collapses `stress_factor` → `Depth` → amplified price impact |
| **Determinism**  | High — all thresholds and formulae are fixed                                                                                            |

## §2 Theory → Implementation Mapping

| Theory construct       | simulation-bases.md reference | Rule implementation                                                                                                                     |
|------------------------|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| HFT stress withdrawal  | §4.1 HFTMarketMaker           | `velocity = mean(                                                                                                                       |
| Momentum amplification | §4.2 MomentumChaser           | `velocity = (price[-1] - price[-lookback]) / price[-lookback]; quantity = int(min(abs(velocity) × position_multiplier, 1000))`          |
| Value stabilisation    | §4.3 FundamentalTrader        | `deviation = (price - fundamental) / fundamental; if deviation < -trigger: buy(order_size); elif deviation > trigger: sell(order_size)` |
| Stop-loss cascade      | §4.4 StopLossTrader           | `stop_level = entry_price × (1 - stop_percentage); if price <= stop_level: sell(-position); stopped=True`                               |
| Noise background       | §4.5 NoiseTrader              | `if random() > trade_probability: qty=0 else: qty = ±randint(min_order, max_order)`                                                     |
| Order-book depth       | §3 Market Design              | `stress_factor` depressed by `volatility > 0.01` and `hft_participation < 0.30`; `Depth = base_depth × max(stress_factor, 0.1)`         |
| Spread widening        | §3 Market Design              | `spread = base_spread + volatility × 0.5; if hft_participation < 0.30: spread × 3; if volatility > 0.02: spread × 5`                    |

## §3 Agent Interaction Flow

```
Round t:
  Market.perceive() — collect all orders; compute hft_participation
  Market.decide()   — compute volatility, stress_factor, Depth, spread, new_price
  Market.act()      — broadcast: price, prev_price, return_pct, fundamental, deviation,
                                  spread, depth, volume, volatility, round
  Investors.perceive() — read market_data; update price_history
  Investors.decide()   — compute quantity, agent_type, provides_liquidity
  Investors.act()      — send order to Market
```

## §4 Crash Mechanism (Rule Logic)

```
Phase 1 (Normal):
  HFTMarketMaker.velocity < withdrawal_threshold → provides_liquidity=True, quantity=500
  hft_participation ≈ 0.6–0.7 → stress_factor = 1.0 → Depth ≈ base_depth

Phase 2 (Trigger):
  MomentumChaser.velocity > entry_threshold → sell (quantity ∝ velocity)
  price drops → HFTMarketMaker.velocity rises toward withdrawal_threshold

Phase 3 (Cascade):
  velocity > withdrawal_threshold → HFTMarketMaker withdraws (quantity=0)
  hft_participation drops < 0.30 → stress_factor × 0.5 → Depth collapses
  spread × 3 or × 5 → amplified impact
  StopLossTrader: price <= stop_level → sell entire position

Phase 4 (Recovery):
  FundamentalTrader: deviation < -value_trigger → buy(order_size)
  HFTMarketMaker velocity drops → returns gradually
```

## §5 Key Parameters

| Parameter              | Location                 | Effect on crash                           |
|------------------------|--------------------------|-------------------------------------------|
| `withdrawal_threshold` | HFTMarketMaker extras    | Lower → earlier withdrawal → deeper crash |
| `base_depth`           | Market extras            | Lower → more severe price impact          |
| `price_impact` (λ)     | Market extras            | Higher → more sensitive to order flow     |
| `stop_percentage`      | StopLossTrader extras    | Lower → triggers earlier in cascade       |
| `entry_threshold`      | MomentumChaser extras    | Lower → earlier momentum entry            |
| `value_trigger`        | FundamentalTrader extras | Lower → earlier recovery entry            |

## §6 Files

| File                                         | Purpose                                |
|----------------------------------------------|----------------------------------------|
| `players.py`                                 | Market + 5 rule-based investor classes |
| `run_flashcrash2010.py`                      | Entry point                            |
| `configs/FlashCrash2010/Rule/simulation.yml` | Main simulation config                 |
| `configs/FlashCrash2010/Rule/players.yml`    | Agent parameter definitions            |
| `configs/FlashCrash2010/Rule/topology.yml`   | Star topology                          |
| `simulation-bases.md`                        | Full theoretical foundations           |
| `analysis-bases.md`                          | Metrics and analysis guide             |

## §7 Running

```bash
python examples/FlashCrash2010/Rule/run_flashcrash2010.py -c configs/FlashCrash2010/Rule/simulation.yml
```

## §8 Expected Behaviour

| Phase    | Rounds | Key observable                                       |
|----------|--------|------------------------------------------------------|
| Normal   | 1–10   | `depth` ≈ `base_depth`; HFT active; spread tight     |
| Trigger  | 11–15  | MomentumChaser selling; HFT first stress             |
| Cascade  | 16–25  | `depth` < 20 % base; spread × 5–50; stop-losses fire |
| Trough   | 26–30  | Min price; max spread; FT buying begins              |
| Recovery | 31–50  | `depth` rebuilds; price → fundamental                |

## §9 References

1. Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). *Journal of Finance*, 72(3), 967-998. doi:10.1111/jofi.12498
2. CFTC-SEC Joint Report (2010). *Findings Regarding the Market Events of May 6, 2010.*
3. Biais, B., Foucault, T., & Moinas, S. (2015). *Journal of Financial Economics*, 116(2), 292-313. doi:10.1016/j.jfineco.2015.03.004
4. De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). *Journal of Finance*, 45(2), 379-395.
5. Brunnermeier, M. K., & Pedersen, L. H. (2005). *Journal of Finance*, 60(4), 1825-1863.
6. Shiller, R. J. (1981). *American Economic Review*, 71(3), 421-436.
7. Black, F. (1986). *Journal of Finance*, 41(3), 529-543.
