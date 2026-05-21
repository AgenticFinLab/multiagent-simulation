# DotComBubble Rule Variant — explain.md

## §1 Overview

The Rule variant implements DotComBubble with deterministic threshold rules. Bubble dynamics emerge from the interaction of narrative-driven buyers, momentum amplifiers, and value-anchored sellers, all governed by fixed deviation thresholds.

| Aspect             | Detail                                                             |
|--------------------|--------------------------------------------------------------------|
| Variant            | Rule                                                               |
| Simulation         | DotComBubble                                                       |
| Decision Mechanism | Threshold rules on `deviation = (P − F) / F` and 1-period momentum |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                    |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                       |

## §2 Theory → Implementation Mapping

### §2.1 NewEconomyEvangelist (simulation-bases.md §4.1)

| Theory Component                    | Implementation                                                             |
|-------------------------------------|----------------------------------------------------------------------------|
| Narrative economics (Shiller, 2000) | `if deviation > -0.20: buy order_size (600)` — buys even when overvalued   |
| Crash capitulation                  | `if deviation < -0.30: sell order_size // 2` — only sells at extreme crash |

### §2.2 IPOFlipper (simulation-bases.md §4.2)

| Theory Component                                | Implementation                                                                 |
|-------------------------------------------------|--------------------------------------------------------------------------------|
| IPO underpricing flip (Ofek & Richardson, 2003) | `if deviation > flip_threshold (0.05) and position > 0: sell order_size (700)` |
| Accumulate for flip                             | `if deviation < 0: buy order_size`                                             |

### §2.3 MomentumFollower (simulation-bases.md §4.3)

| Theory Component                             | Implementation                                           |
|----------------------------------------------|----------------------------------------------------------|
| 1-period momentum (Jegadeesh & Titman, 1993) | `m = (P[-1] − P[-2]) / P[-2]`                            |
| Buy on uptrend                               | `if m > momentum_threshold (0.02): buy order_size (500)` |
| Sell on downtrend                            | `if m < -momentum_threshold: sell order_size`            |

### §2.4 SkepticalValueInvestor (simulation-bases.md §4.4)

| Theory Component                 | Implementation                               |
|----------------------------------|----------------------------------------------|
| Post-crash buying (Graham, 1949) | `if deviation < -0.10: buy order_size (400)` |
| Exit overvaluation               | `if deviation > 0.20: sell order_size`       |

### §2.5 ShortSeller (simulation-bases.md §4.5)

| Theory Component                                 | Implementation                                                 |
|--------------------------------------------------|----------------------------------------------------------------|
| Short overvaluation (Abreu & Brunnermeier, 2003) | `if deviation > short_threshold (0.15): sell order_size (400)` |
| Cover on crash                                   | `if deviation < cover_threshold (-0.05): buy order_size`       |

## §3 Market Mechanism

```
P(t+1) = P(t) + λ·NetDemand(t) + γ·[F(t)−P(t)] + ε(t)
λ = 0.01, γ = 0.005 (weak mean-reversion — bubble persistence design)
```

## §4 Variant-Specific Features

- **Weak mean reversion**: γ = 0.005 allows bubble to persist far beyond fundamental — calibrated to dot-com's multi-year duration.
- **1-period momentum**: MomentumFollower uses single-period return, not multi-period lookback — simple but effective in trending markets.
- **NewEconomyEvangelist extreme hold**: Only sells at δ < −0.30 — models behavioral commitment to internet narrative.
- **IPOFlipper asymmetry**: Buys at any dip but only flips above δ = 0.05 — creates asymmetric buy/sell pressure.

## §5 Config Reference

Config files: `configs/DotComBubble/Rule/{simulation.yml,players.yml,topology.yml,persona.yml}`

Key extras: `initial_price`, `fundamental_value`, `price_impact`, `mean_reversion`, `noise_std`, `order_size`, `flip_threshold`, `momentum_threshold`, `value_buy_threshold`, `value_sell_threshold`, `short_threshold`, `cover_threshold`.

## §6 Running Instructions

```bash
python -m examples.DotComBubble.Rule.run_dotcombubble
```

## §7 Expected Behavior

- BAI ≈ 0.5–1.5 (50–150% above fundamental)
- BD ≈ 20–50 rounds
- CS ≈ 0.4–0.7 (40–70% crash)
- SkepticalValueInvestor and ShortSeller outperform during and after crash
- WDI negative at end (stabilizing agents vindicated by crash)

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Cross-Variant Role

Rule output is the deterministic baseline for:

| Comparison | Purpose |
|---|---|
| Rule vs LLM | Test whether persona-only LLM agents reproduce narrative-driven bubble dynamics. |
| Rule vs RuleLLM | Test whether explicit rule guidance preserves the deterministic bubble mechanism under LLM reasoning. |
| RuleLLM vs Rag | Test whether retrieved bubble-history knowledge changes valuation discipline, momentum following, or short-seller behavior. |
