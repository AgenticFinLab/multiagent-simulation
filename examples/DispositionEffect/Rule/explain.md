# DispositionEffect Rule Variant — explain.md

## §1 Overview

The Rule variant implements DispositionEffect with deterministic threshold rules grounded in Prospect Theory. DispositionInvestor tracks reference points (purchase price) and applies fixed gain/loss thresholds to trigger sell decisions. This provides the mechanically exact Prospect Theory baseline.

| Aspect             | Detail                                                                |
|--------------------|-----------------------------------------------------------------------|
| Variant            | Rule                                                                  |
| Simulation         | DispositionEffect                                                     |
| Decision Mechanism | Threshold rules on `gain_loss = (P − P_ref) / P_ref`                  |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                       |
| Market Broadcast   | `price`, `prev_price`, `return`, `volume`, `net_demand`, `news_shock` |

## §2 Theory → Implementation Mapping

### §2.1 DispositionInvestor (simulation-bases.md §4.1)

| Theory Component                                       | Implementation                                           |
|--------------------------------------------------------|----------------------------------------------------------|
| Prospect Theory gain domain (Kahneman & Tversky, 1979) | Above `gain_threshold`, sell `position × sell_fraction_gain` |
| Prospect Theory loss domain                            | Below `loss_threshold`, sell `position × sell_fraction_loss` |
| Reference point anchoring                              | `purchase_price` tracked per investor; updated on trades |
| Buy at reference point                                 | Buy inside `reference_buy_band`, subject to configured caps |
| Loss aversion λ                                        | `loss_aversion` validates the sell-fraction asymmetry |

### §2.2 RationalInvestor (simulation-bases.md §4.2)

| Theory Component                                          | Implementation                                                                                |
|-----------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Expected Utility Theory (von Neumann & Morgenstern, 1944) | `current_alloc = equity_value / total_value`                                                  |
| Target allocation rebalancing                             | Move by `rebalance_speed` when allocation leaves the target band |
| No reference point                                        | Ignores `purchase_price`; acts on portfolio weight deviation only                             |

### §2.3 TaxAwareInvestor (simulation-bases.md §4.3)

| Theory Component                           | Implementation                                        |
|--------------------------------------------|-------------------------------------------------------|
| Tax-loss harvesting (Constantinides, 1983) | Sell by `tax_harvest_fraction` below `tax_loss_threshold` |
| Capital gains deferral                     | Hold above `capital_gains_hold` |

### §2.4 IndexHolder (simulation-bases.md §4.4)

| Theory Component                    | Implementation        |
|-------------------------------------|-----------------------|
| Passive buy-and-hold (Sharpe, 1991) | `quantity = 0` always |

### §2.5 InstitutionalInvestor (simulation-bases.md §4.5)

| Theory Component                                  | Implementation                                    |
|---------------------------------------------------|---------------------------------------------------|
| Professional discipline (Shapira & Venezia, 2001) | Same configured `sell_fraction` for gains and losses |
| Threshold discipline                              | Separate configured gain/loss thresholds with symmetric sizing |

## §3 Market Mechanism

```
P(t+1) = P(t) + λ·NetDemand(t) + γ·[F(t)−P(t)] + ε(t) + NewsShock(t)
λ = 0.08, γ = 0.05
NewsShock: probability 0.15, magnitude ~ Uniform(−4, +4)
```

## §4 Variant-Specific Features

- **Reference point tracking**: Each investor maintains `purchase_price`; `update_reference_point()` called on every trade.
- **Asymmetric sell fractions**: DispositionInvestor sells 50% of position on gain trigger but only 15% on loss trigger — core Prospect Theory asymmetry.
- **News shocks**: Random shocks create gain/loss states that trigger investor decisions; essential for observing disposition behavior.
- **move_reference=False**: DispositionInvestor preserves original purchase price on buys — maintains psychological anchor.

## §5 Architecture Diagram

```
Market(coordinator)
  ├─ broadcasts price, return, volume, net_demand, news_shock
  ├─ receives order payloads with action, bid_price, quantity, strategy
  └─ clears price using price impact, mean reversion, noise, and news shocks

Investors
  ├─ perceive market broadcast
  ├─ update reference-point and portfolio state
  ├─ decide with deterministic disposition, rational, tax, passive, or
  │  institutional rules
  └─ act by sending one order payload to the market
```

## §6 Config Reference

Config files: `configs/DispositionEffect/Rule/simulation.yml`, `players.yml`, and `topology.yml`

Key extras include all market dynamics, initial portfolio state, decision
thresholds, sizing fractions, `reference_buy_band`, `minimum_trade_quantity`,
and `rebalance_speed`. Every behavioral number is loaded from `players.yml`.

## §7 Running Instructions

```bash
python -m examples.DispositionEffect.Rule.run_disposition -c configs/DispositionEffect/Rule/simulation.yml
```

For a five-round isolated smoke run, set `DISPOSITION_RULE_OUTPUT_DIR` and add
`--steps 5`. Omitting `--steps` executes the configured 200 rounds.

## §8 Expected Behavior

- PGR ≈ 0.10–0.20 (calibrated to Odean 1998 benchmark of 14.8%)
- PLR ≈ 0.06–0.12 (calibrated to Odean benchmark of 9.8%)
- PGR/PLR ≈ 1.4–1.7
- DispositionInvestor wealth < RationalInvestor wealth (3–5% annual drag)
- TaxAwareInvestor PLR > DispositionInvestor PLR (anti-disposition via tax incentive)

## §9 References

See `simulation-bases.md §2` for full DOI citations.
