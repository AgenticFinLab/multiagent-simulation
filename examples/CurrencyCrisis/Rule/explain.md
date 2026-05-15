# CurrencyCrisis Rule Variant — explain.md

## §1 Overview

The Rule variant implements CurrencyCrisis with deterministic threshold rules. Attack behavior scales with current deviation; self-fulfilling momentum is tracked via 3-period price history; central bank defense is activated by fixed thresholds. This provides the baseline FX crisis dynamics.

| Aspect             | Detail                                        |
|--------------------|-----------------------------------------------|
| Variant            | Rule                                          |
| Simulation         | CurrencyCrisis                                |
| Decision Mechanism | Threshold rules on δ(t) and 3-period momentum |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`               |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`  |

## §2 Theory → Implementation Mapping

### §2.1 SpeculativeAttacker (simulation-bases.md §4.1)

| Theory Component                         | Implementation                               |
|------------------------------------------|----------------------------------------------|
| Reserve depletion attack (Krugman, 1979) | `if deviation < −0.03: sell qty × (1 +       |
| Short-cover on recovery                  | `if deviation > 0.05: buy cover_size`        |
| Attack scaling                           | `attack_size = 500`; scales dynamically with |

### §2.2 SelfFulfillingTrader (simulation-bases.md §4.2)

| Theory Component                            | Implementation                                     |
|---------------------------------------------|----------------------------------------------------|
| Expectation-based momentum (Obstfeld, 1996) | Sell when 3-period momentum < −0.5                 |
| Coordination signal                         | `momentum = mean(price[-3:]) - mean(price[-6:-3])` |
| Momentum threshold                          | `momentum_threshold = 0.5`                         |

### §2.3 CentralBankDefender (simulation-bases.md §4.3)

| Theory Component     | Implementation                                  |
|----------------------|-------------------------------------------------|
| Reserve intervention | `if deviation < −0.03: buy defense_size (600)`  |
| Emergency defense    | `if deviation < −0.10: buy reserve_size (1000)` |
| Reserve constraint   | Limited by `initial_cash`                       |

### §2.4 FundamentalHedger (simulation-bases.md §4.4)

| Theory Component                         | Implementation                               |
|------------------------------------------|----------------------------------------------|
| Fundamental anchor (Morris & Shin, 1998) | `if deviation < −0.08: buy order_size (400)` |
| Overvaluation sell                       | `if deviation > 0.08: sell order_size`       |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                | Implementation                                       |
|---------------------------------|------------------------------------------------------|
| Random FX trading (Black, 1986) | `trade_probability = 0.3`, `qty ~ Uniform(100, 500)` |

## §3 Market Mechanism

```
P(t+1) = P(t) + λ·D(t) + γ·[F(t)−P(t)] + ε(t)
λ = 0.01, γ = 0.02 (weaker mean-reversion than equity — persistent crisis)
```

## §4 Variant-Specific Features

- **Scaled attack**: SpeculativeAttacker's sell volume scales with `|δ| × 10` — unique to this simulation's attack model.
- **3-period momentum**: SelfFulfillingTrader uses a 3/6-period moving average difference for the momentum signal.
- **Two-tier defense**: Normal (600 units at δ < −0.03) and emergency (1,000 units at δ < −0.10).
- **Wider FundamentalHedger threshold**: 8% vs. 5% in other simulations — reflects FX market broader tolerance.

## §5 Config Reference

Config file: `CurrencyCrisis/Rule/config.yaml`

Key extras: `initial_price`, `fundamental_value`, `price_impact`, `mean_reversion`, `noise_std`, `attack_threshold`, `attack_size`, `momentum_threshold`, `defense_threshold`, `defense_size`, `crisis_threshold`, `reserve_size`, `fundamental_threshold`, `trade_probability`.

## §6 Running Instructions

```bash
python -m examples.CurrencyCrisis.Rule.run
```

## §7 Expected Behavior

- Attack may deepen to −15% to −25% below peg before defense stabilizes
- SFAF ≈ 0.6–0.9 (self-fulfilling amplification present but not dominant)
- FAS ≈ 0.5–0.8
- WTI near-zero if defense is effective; positive if peg collapses

## §8 References

See `simulation-bases.md §2` for full DOI citations.
