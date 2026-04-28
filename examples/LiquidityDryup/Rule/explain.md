# LiquidityDryup — Rule Variant Explanation

## §1 Overview

| Item               | Description                                                                                                                           |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Liquidity dry-up — market makers withdraw under volatility stress, triggering a self-reinforcing price-impact spiral                  |
| **Variant**        | Rule-based: all agents use deterministic formulas; market maker withdrawal triggered by volatility threshold                          |
| **Investor Count** | 5 classes: MarketMaker, LiquiditySeeker, ValueTrader, MomentumTrader, NoiseTrader                                                     |
| **Key Feature**    | Endogenous liquidity amplification: `liquidity_factor = 100 / max(total_liquidity, 10)` raises price impact as market makers withdraw |
| **Academic Value** | Replicates Brunnermeier–Pedersen (2009) liquidity spiral through agent-based interactions                                             |

---

## §2 Theory → Implementation Mapping

### §2.1 MarketMaker (simulation-bases.md §4.1)

Implements Grossman–Miller (1988) immediacy provider with endogenous withdrawal.

| Theory Element           | Rule Implementation                                                            |
|--------------------------|--------------------------------------------------------------------------------|
| Inventory risk threshold | `if                                                                            |
| Withdrawal               | `provides_liquidity = 0; quantity = −position × withdraw_rebalance`            |
| Normal provision         | `provides_liquidity = base_liquidity; quantity = −position × normal_rebalance` |
| Quantity cap             | `max(−25, min(25, quantity))`                                                  |

Activation: `|return| > volatility_threshold` for withdrawal.

### §2.2 LiquiditySeeker (simulation-bases.md §4.2)

Brunnermeier–Pedersen demand-side liquidity constraint.

| Theory Element    | Rule Implementation                                        |
|-------------------|------------------------------------------------------------|
| Random trade need | `target = N(0, target_volatility)`                         |
| Liquidity scaling | `quantity = target × min(1.0, liquidity / liquidity_base)` |
| Quantity cap      | `max(−20, min(20, quantity))`                              |

### §2.3 ValueTrader (simulation-bases.md §4.3)

Fundamental-anchored crisis liquidity provider.

| Theory Element      | Rule Implementation            |
|---------------------|--------------------------------|
| Deviation trigger   | `                              |
| Quantity            | `deviation × value_multiplier` |
| Liquidity provision | `base_liquidity_provision if   |
| Cap                 | `max(−25, min(25, quantity))`  |

### §2.4 MomentumTrader (simulation-bases.md §4.4)

Positive-feedback cascade amplifier.

| Theory Element   | Rule Implementation            |
|------------------|--------------------------------|
| Trend activation | `                              |
| Quantity         | `return × momentum_multiplier` |
| Cap              | `max(−35, min(35, quantity))`  |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

Random Gaussian order flow.

| Theory Element     | Rule Implementation           |
|--------------------|-------------------------------|
| Trade size         | `N(0, noise_volatility)`      |
| Cap                | `max(−15, min(15, quantity))` |
| Liquidity provided | Always 0                      |

---

## §3 Market Mechanism

Price formation with endogenous liquidity amplification:

```
P(t+1) = P(t) + (λ × NetDemand × liquidity_factor) + γ × (F − P(t)) + ε(t)

liquidity_factor = 100 / max(total_liquidity, 10)
total_liquidity = base_liquidity + Σ provides_liquidity_i
```

The spiral mechanism:
1. High volatility → MarketMaker withdraws (`provides_liquidity = 0`).
2. `total_liquidity` drops → `liquidity_factor` rises.
3. Next round's price impact is amplified → larger price moves.
4. Larger moves → more MarketMaker withdrawals → further amplification.
5. ValueTrader eventually provides corrective liquidity when `|deviation| > trade_threshold`.

---

## §4 Variant Architecture

```
Rule Variant Architecture
─────────────────────────
Market (liquidity-dependent pricing)
  │  broadcast {price, return, liquidity, fundamental}
  ├─ MarketMaker        │ volatility threshold → withdraw / provide
  ├─ LiquiditySeeker    │ random need × liquidity adjustment
  ├─ ValueTrader        │ deviation trigger → value + liquidity
  ├─ MomentumTrader     │ return × multiplier (cascade amplifier)
  └─ NoiseTrader        │ N(0, noise_volatility)
```

All agents are purely deterministic rule-based.

---

## §5 Config Reference

| Parameter                  | Agent           | Default | Description                              |
|----------------------------|-----------------|---------|------------------------------------------|
| `volatility_threshold`     | MarketMaker     | 0.03    |                                          |
| `base_liquidity`           | MarketMaker     | 30      | Liquidity units in normal conditions     |
| `withdraw_rebalance`       | MarketMaker     | 0.5     | Inventory offload fraction during stress |
| `normal_rebalance`         | MarketMaker     | 0.1     | Normal inventory rebalancing             |
| `target_volatility`        | LiquiditySeeker | 10      | σ of trade size distribution             |
| `liquidity_base`           | LiquiditySeeker | 100     | Liquidity normalisation                  |
| `liquidity_threshold`      | ValueTrader     | 0.03    | Deviation for liquidity provision        |
| `trade_threshold`          | ValueTrader     | 0.05    | Deviation for value trading              |
| `base_liquidity_provision` | ValueTrader     | 20      | Crisis liquidity units                   |
| `value_multiplier`         | ValueTrader     | 100     | Trade size scaling                       |
| `momentum_threshold`       | MomentumTrader  | 0.02    | Minimum return to follow                 |
| `momentum_multiplier`      | MomentumTrader  | 500     | Trend intensity                          |
| `noise_volatility`         | NoiseTrader     | 5       | σ of noise order                         |
| `fundamental_value`        | Market          | 100     | Fundamental anchor                       |
| `price_impact`             | Market          | 0.001   | Base λ                                   |
| `mean_reversion`           | Market          | 0.05    | γ                                        |
| `noise_std`                | Market          | 0.01    | Market noise                             |

---

## §6 Running Instructions

```bash
# Run Rule variant
python examples/LiquidityDryup/Rule/run_liquidity.py \
    -c configs/LiquidityDryup/Rule/simulation.yml

# Run with more aggressive withdrawal
python examples/LiquidityDryup/Rule/run_liquidity.py \
    -c configs/LiquidityDryup/Rule/simulation.yml \
    --extras volatility_threshold=0.02
```

Output written to `records/LiquidityDryup/Rule/`.

---

## §7 Expected Behavior

| Metric         | Expected Range | Rationale                                     |
|----------------|----------------|-----------------------------------------------|
| LRI minimum    | 0.05–0.20      | Strong spiral — all MMs withdraw at threshold |
| MWF maximum    | 0.7–1.0        | Most MMs withdraw during dry-up               |
| PAD            | 0.10–0.25      | Significant dislocation from fundamental      |
| LPD            | 10–25 rounds   | Moderate-to-sustained dry-up                  |
| WDI            | 0.25–0.45      | Significant wealth redistribution             |
| MPI multiplier | 3–8×           | Price impact amplification during dry-up      |

Rule variant produces the most mechanically consistent dry-up cascade. It is the baseline against which LLM, RuleLLM, and Rag variants are compared.

---

## §8 References

- Grossman, S. J., & Miller, M. H. (1988). doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x)
- Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)
- Kyle, A. S. (1985). doi:[10.2307/1913210](https://doi.org/10.2307/1913210)
- De Long, J. B., et al. (1990). doi:[10.1111/j.1540-6261.1990.tb03695.x](https://doi.org/10.1111/j.1540-6261.1990.tb03695.x)
- simulation-bases.md §4.1–§4.5 (Investor Taxonomy)

---

## §9 Variant Comparison

| Dimension             | Rule                         | LLM                       | RuleLLM                     | Rag                        |
|-----------------------|------------------------------|---------------------------|-----------------------------|----------------------------|
| MM withdrawal trigger | Volatility threshold formula | LLM observes stress       | Rule threshold + LLM timing | Rule + KB crisis precedent |
| Spiral mechanism      | Automatic liquidity_factor   | Emergent LLM coordination | Rule-anchored spiral        | RAG moderates recovery     |
| Expected LRI min      | 0.05–0.20                    | 0.05–0.30                 | 0.05–0.25                   | 0.10–0.30                  |
| Expected LPD          | 10–25 rounds                 | 8–20 rounds               | 9–22 rounds                 | 6–15 rounds                |
| Stochasticity         | Minimal                      | High                      | Moderate                    | Moderate                   |
