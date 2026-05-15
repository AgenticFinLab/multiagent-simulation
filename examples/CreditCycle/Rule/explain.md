# CreditCycle Rule Variant — explain.md

## §1 Overview

The Rule variant implements the CreditCycle simulation using deterministic threshold-based logic. All investor decisions are computed from the current price deviation δ(t) and internal state counters (MinskyBorrower's `stable_rounds`) without LLM inference. This provides the baseline deterministic credit-cycle dynamics for comparison.

| Aspect             | Detail                                       |
|--------------------|----------------------------------------------|
| Variant            | Rule                                         |
| Simulation         | CreditCycle                                  |
| Decision Mechanism | Threshold rules on δ(t) and `stable_rounds`  |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`              |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 ProCyclicalLender (simulation-bases.md §4.1)

| Theory Component                            | Implementation                                                    |
|---------------------------------------------|-------------------------------------------------------------------|
| Pro-cyclical leverage (Adrian & Shin, 2010) | `if deviation > expansion_threshold: buy qty × credit_multiplier` |
| Credit contraction during bust              | `if deviation < −expansion_threshold: sell order_size`            |
| Boom expansion threshold                    | `expansion_threshold = 0.03`                                      |
| Credit multiplier                           | `credit_multiplier = 2.0` (order_size × 2.0 during boom)          |

### §2.2 MinskyBorrower (simulation-bases.md §4.2)

| Theory Component                          | Implementation                                         |
|-------------------------------------------|--------------------------------------------------------|
| Stability breeds fragility (Minsky, 1986) | `stable_rounds` counter increments when `              |
| Hedge→Ponzi progression                   | Buy triggered when `stable_rounds > 3`                 |
| Minsky moment forced deleveraging         | `if deviation < crisis_threshold: sell order_size × 2` |
| Crisis threshold                          | `crisis_threshold = −0.05`                             |

### §2.3 CounterCyclicalLender (simulation-bases.md §4.3)

| Theory Component                            | Implementation                         |
|---------------------------------------------|----------------------------------------|
| Counter-cyclical capital buffer (Basel III) | `if deviation < −0.05: buy order_size` |
| Reserve build during boom                   | `if deviation > 0.05: sell order_size` |
| Boom sell threshold                         | `boom_sell_threshold = 0.05`           |
| Crisis inject threshold                     | `crisis_buy_threshold = −0.05`         |

### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component                | Implementation                                       |
|---------------------------------|------------------------------------------------------|
| Margin of safety (Graham, 1949) | `if deviation < −0.10: buy` (10% discount threshold) |
| Overvaluation exit              | `if deviation > 0.10: sell`                          |
| Value discount                  | `value_discount = 0.10`                              |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                        | Implementation                                        |
|-----------------------------------------|-------------------------------------------------------|
| Random uninformed trading (Black, 1986) | `if random.random() < trade_probability: buy or sell` |
| Trade probability                       | `trade_probability = 0.3`                             |
| Order size                              | `Uniform(100, 500)`                                   |

## §3 Market Mechanism

```
P(t+1) = P(t) + λ·D(t) + γ·[F(t)−P(t)] + ε(t)
```

- `λ = 0.01` (price_impact), `γ = 0.03` (mean_reversion), `σ = 0.5` (noise_std)
- `δ(t) = [P(t) − F(t)] / F(t)` drives all investor decisions

## §4 Variant-Specific Features

- **Minsky counter**: `stable_rounds` is the unique feature — tracks consecutive rounds with `|δ| < 0.02`, enabling endogenous leverage build-up.
- **Double-size crisis sell**: MinskyBorrower sells `order_size × 2` during crisis, modeling forced deleveraging at scale.
- **Credit multiplier**: ProCyclicalLender buys `order_size × credit_multiplier` during boom — only this variant has volume scaling.
- **Asymmetric thresholds**: CounterCyclicalLender and ValueInvestor use different crisis/boom thresholds (−0.05 vs. ±0.10) to model institutional layering.

## §5 Config Reference

Config file: `CreditCycle/Rule/config.yaml`

Key `extras` fields: `initial_price`, `fundamental_value`, `price_impact`, `mean_reversion`, `noise_std`, `expansion_threshold`, `credit_multiplier`, `max_leverage`, `crisis_threshold`, `crisis_buy_threshold`, `boom_sell_threshold`, `value_discount`, `trade_probability`.

## §6 Running Instructions

```bash
cd multiagent-simulation
python -m examples.CreditCycle.Rule.run
```

## §7 Expected Behavior

- 2–3 boom-bust cycles per 100-round run
- Peak price ≈ 108–115 during boom; trough ≈ 80–90 during bust
- MinskyBorrower stable_rounds reaches 4–8 before crisis onset
- CounterCyclicalLender and ValueInvestor buying limits trough depth

## §8 References

See `simulation-bases.md §2` for full DOI citations.
