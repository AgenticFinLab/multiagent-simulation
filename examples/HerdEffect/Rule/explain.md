# HerdEffect Rule — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                                         |
|--------------------|--------------------------------------------------------------------------------|
| Variant            | Rule (deterministic baseline)                                                  |
| Simulation         | HerdEffect                                                                     |
| Decision Mechanism | Deterministic order-book formulas — all parameters from config                 |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                |
| Market Broadcast   | `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, `round` |
| Price Model        | Order-book: `P(t+1) = P(t) + α × NetDemand + γ × (F − P) + ε`                  |

The Rule variant is the deterministic baseline for HerdEffect. All five investors apply fixed `calculate_bid()` formulas to the order-book price signal, with no stochastic LLM component. This provides the cleanest signal for measuring emergent herding: any momentum episode is attributable purely to the rule-encoded positive feedback dynamics.

## §2 Theory → Implementation Mapping

### §2.1 MomentumInvestor (simulation-bases.md §4.1)

| Theory Component                          | Implementation                                               |
|-------------------------------------------|--------------------------------------------------------------|
| Shiller (1984) positive feedback          | `bid_price = price × (1 + lambda_price × ret)`               |
| Capital allocation proportional to return | `quantity = beta × ret × cash / bid_price`                   |
| Position cap                              | Bounded [−50, +50]                                           |
| Positive feedback loop                    | Buys when ret > 0; sells when ret < 0 — amplifies all trends |

### §2.2 ContrarianInvestor (simulation-bases.md §4.2)

| Theory Component                        | Implementation                                                       |
|-----------------------------------------|----------------------------------------------------------------------|
| De Bondt & Thaler (1985) mean reversion | `bid_price = fundamental + N(0, noise_std)`                          |
| Contrarian quantity                     | `quantity = beta × (fundamental − price) / price × cash / bid_price` |
| Fundamental source                      | Reads `fundamental` from own `extras` — NOT from market broadcast    |
| Stabilizing role                        | Buys when price < fundamental; sells when price > fundamental        |
| Position cap                            | Bounded [−50, +50]                                                   |

### §2.3 RiskAverseInvestor (simulation-bases.md §4.3)

| Theory Component                            | Implementation                                 |
|---------------------------------------------|------------------------------------------------|
| Markowitz (1952) mean-variance              | `variance = np.var(price_history[-lookback:])` |
| Position inversely proportional to variance | `target_qty = k / variance × cash / P`         |
| Gradual adjustment (30 %/round)             | `quantity = (target_qty − position) × 0.30`    |
| Smallest position cap                       | Bounded [−20, +20] — conservative constraint   |

### §2.4 NoiseTrader (simulation-bases.md §4.4)

| Theory Component                        | Implementation                                                        |
|-----------------------------------------|-----------------------------------------------------------------------|
| De Long et al. (1990) noise trader risk | `bid_price = price + N(0, price_noise_std)`                           |
| Random mean-reverting quantity          | `quantity = N(0, qty_noise_std) − position × position_mean_reversion` |
| Herd trigger                            | Random buy → r > 0 → MomentumInvestor activates → cascade begins      |

### §2.5 AggressiveInvestor (simulation-bases.md §4.5)

| Theory Component                          | Implementation                                                        |
|-------------------------------------------|-----------------------------------------------------------------------|
| Leveraged momentum (kappa > lambda_price) | `bid_price = price × (1 + kappa × ret)`                               |
| Acceleration bonus                        | `quantity += accel_bonus × [(P[−1]−P[−2]) − (P[−2]−P[−3])]`           |
| Largest position cap                      | Bounded [−80, +80] — extreme amplifier                                |
| History requirement                       | Uses last 3 prices for acceleration; falls back to return-only if < 3 |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3*

```
P(t+1) = P(t) + α × NetDemand(t) + γ × (F − P(t)) + ε(t)

where:
  α = supply_elasticity   [default: 0.001]
  γ = mean_reversion      [default: 0.05]
  ε ~ N(0, noise_std)     [default: 0.5]
  NetDemand = Σ signed_quantities across all agents
```

Buy orders sorted by bid_price descending (highest bidder executes first). Market collects all `{bid_price, quantity, strategy, cash, position}` orders. **Critical**: ContrarianInvestor's `fundamental` value is NOT in market broadcast — it reads from its own `extras`.

## §4 Variant Architecture

| Component       | Detail                                                                     |
|-----------------|----------------------------------------------------------------------------|
| Base class      | `BaseInvestor`                                                             |
| Abstract method | `calculate_bid()` returns `(bid_price, signed_quantity)`                   |
| Inference       | None (deterministic formulas)                                              |
| Context         | `market_data` from broadcast: `{price, return, volume, net_demand, round}` |
| Output          | `{bid_price, quantity, strategy, cash, position}` order dict               |
| Cash update     | Done in `decide()` — not in `act()`                                        |

## §5 Config Reference

Config file: `configs/HerdEffect/Rule/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors; default: 100,000 / 0)
- `lambda_price`, `beta` (MomentumInvestor)
- `fundamental`, `beta`, `noise_std` (ContrarianInvestor — fundamental in extras, not broadcast)
- `k`, `lookback` (RiskAverseInvestor)
- `price_noise_std`, `qty_noise_std`, `position_mean_reversion` (NoiseTrader)
- `kappa`, `beta`, `accel_bonus` (AggressiveInvestor)
- Market: `supply_elasticity`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`

## §6 Running Instructions

```bash
python -m examples.HerdEffect.Rule.run_herd_effect \
    -c configs/HerdEffect/Rule/simulation.yml
```

Or via Streamlit UI: select "HerdEffect" → "Rule" variant.

## §7 Expected Behavior

- **Momentum episodes**: Price shows sustained positive-return runs (EMI ≥ 0.08) triggered by NoiseTrader noise and amplified by MomentumInvestor + AggressiveInvestor
- **Acceleration signature**: AggressiveInvestor fires strongest when 3+ consecutive positive returns → sharp price spike before reversal
- **Risk-averse early exit**: RiskAverseInvestor position declines before price peak in ≥ 40 % of episodes (REI ≥ 0.40)
- **Mean reversion**: ContrarianInvestor + γ mean-reversion parameter eventually terminate each herd episode
- **No explicit imitator**: Emergent herding is purely from positive feedback on shared return signal — no agent copies any other
- **HVR target**: 1.5–4.0 (momentum phases are 1.5–4× more volatile than quiet periods)

## §8 References

See `simulation-bases.md §2` for full DOI citations for all theoretical foundations.

Key references:
- Shiller (1984) `doi:10.2307/2534436` — positive feedback trading (MomentumInvestor)
- Jegadeesh & Titman (1993) `doi:10.1111/j.1540-6261.1993.tb04702.x` — momentum evidence (MomentumInvestor calibration)
- De Bondt & Thaler (1985) `doi:10.1111/j.1540-6261.1985.tb05004.x` — mean reversion (ContrarianInvestor)
- Markowitz (1952) `doi:10.1111/j.1540-6261.1952.tb01525.x` — mean-variance optimization (RiskAverseInvestor)
- De Long et al. (1990) `doi:10.1111/j.1540-6261.1990.tb03695.x` — noise trader risk (NoiseTrader)

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
