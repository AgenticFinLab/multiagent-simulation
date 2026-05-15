# HerdingInformation Rule — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                               |
|--------------------|------------------------------------------------------|
| Variant            | Rule (deterministic baseline)                        |
| Simulation         | HerdingInformation                                   |
| Decision Mechanism | Deterministic rule-based cascade threshold formulas  |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                      |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`         |
| Price Model        | `P(t+1) = P(t) + λ × NetDemand + γ × (F − P(t)) + ε` |

The Rule variant is the deterministic baseline for HerdingInformation. All five investors apply fixed threshold formulas to the broadcast `deviation` signal. This provides the cleanest signal for measuring information cascade dynamics: cascade formation, reputation herding, and the limits of independent correction.

## §2 Theory → Implementation Mapping

### §2.1 CascadeFollower (simulation-bases.md §4.1)

| Theory Component                             | Implementation                                           |
|----------------------------------------------|----------------------------------------------------------|
| Bikhchandani et al. (1992) cascade formation | Counts rounds with `                                     |
| Social signal weighting                      | `qty = min(800, int(                                     |
| Cascade direction                            | Follows deviation: buys when dev > 0; sells when dev < 0 |
| Pre-cascade                                  | Holds until cascade_count threshold reached              |

### §2.2 ReputationHerder (simulation-bases.md §4.2)

| Theory Component                              | Implementation                                      |
|-----------------------------------------------|-----------------------------------------------------|
| Scharfstein & Stein (1990) reputation herding | `qty = min(600, int(                                |
| Lower activation threshold                    | Activates at `                                      |
| Career concern amplification                  | `reputation_concern` ∈ [1.0, 3.0] scales trade size |

### §2.3 IndependentThinker (simulation-bases.md §4.3)

| Theory Component        | Implementation                                                   |
|-------------------------|------------------------------------------------------------------|
| Rational Bayesian agent | `qty = min(500, int(                                             |
| Contrarian signal       | Buys when dev < 0 (undervalued); sells when dev > 0 (overvalued) |
| Activation threshold    | `                                                                |

### §2.4 Contrarian (simulation-bases.md §4.4)

| Theory Component                               | Implementation                                                     |
|------------------------------------------------|--------------------------------------------------------------------|
| De Bondt & Thaler (1985) deliberate contrarian | `qty = min(400, int(                                               |
| Higher threshold than IndependentThinker       | Activates at `                                                     |
| Cascade resistance                             | Sells when dev > 0; buys when dev < 0 — mirrors IndependentThinker |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                | Implementation                                                    |
|---------------------------------|-------------------------------------------------------------------|
| Black (1986) uninformed trading | `if random() < trade_probability: qty = random.randint(100, 500)` |
| Random direction                | Coin flip for buy/sell — cascade trigger and baseline liquidity   |
| Accidental cascade initiator    | Random deviations increment CascadeFollower's cascade_count       |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)

where:
  λ = price_impact      [default: 0.001]
  γ = mean_reversion    [default: 0.05]
  ε ~ N(0, noise_std)   [default: 0.5]
  NetDemand = Σ signed_quantities
```

Market broadcasts `{price, fundamental, deviation, round}`. The `deviation = (P − F) / F` signal is what CascadeFollower counts — rounds where `|deviation| > 0.03` increment cascade_count.

## §4 Variant Architecture

| Component     | Detail                                             |
|---------------|----------------------------------------------------|
| Base class    | `GeneralPlayer`                                    |
| Inference     | None (deterministic formulas)                      |
| Context       | `market_data` from broadcast                       |
| Output        | `{"action": "buy"/"sell"/"hold", "quantity": int}` |
| Cascade state | `cascade_count` maintained in `custom_state`       |

## §5 Config Reference

Config file: `configs/HerdingInformation/Rule/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `social_weight`, `cascade_trigger` (CascadeFollower)
- `reputation_concern` (ReputationHerder)
- `signal_precision` (IndependentThinker)
- `contrarian_threshold` (Contrarian)
- `trade_probability` (NoiseTrader)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`

## §6 Running Instructions

```bash
python -m examples.HerdingInformation.Rule.run_herding_information \
    -c configs/HerdingInformation/Rule/simulation.yml
```

Or via Streamlit UI: select "HerdingInformation" → "Rule" variant.

## §7 Expected Behavior

- **Cascade formation**: CascadeFollower activates after `cascade_trigger` rounds of |deviation| > 0.03 — deterministic cascade lock-in
- **Pre-cascade reputation herding**: ReputationHerder fires at any |deviation| > 0.02 — earlier than CascadeFollower
- **Capacity asymmetry**: Combined herding capacity (1,400) > correction capacity (900) — cascades cannot be immediately broken
- **CCI target**: 0.40–0.70 (cascade agents' share of total volume during cascade rounds)
- **Rule provides tightest MAD band**: Deterministic cascade_trigger → consistent cascade formation timing
- **No LLM variability**: Cascade onset round is deterministic given same random seed

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Bikhchandani, Hirshleifer & Welch (1992) `doi:10.1086/261849` — CascadeFollower
- Scharfstein & Stein (1990) — ReputationHerder
- Shleifer & Vishny (1997) `doi:10.1111/j.1540-6261.1997.tb03807.x` — capacity asymmetry

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
