# EuropeanDebtCrisis Rule — Implementation Explanation

## §1 Overview

The Rule variant is the deterministic baseline for the EuropeanDebtCrisis simulation. All five investors apply fixed threshold comparisons to observed deviation from fundamental. No stochastic LLM component — crisis dynamics are driven purely by rule-encoded panic thresholds and intervention triggers.

| Aspect             | Detail                                                        |
|--------------------|---------------------------------------------------------------|
| Variant            | Rule (deterministic baseline)                                 |
| Simulation         | EuropeanDebtCrisis                                            |
| Decision Mechanism | Deviation-threshold rules — all parameters loaded from config |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                               |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                  |

## §2 Theory → Implementation Mapping

### §2.1 PeripheryBondSeller (simulation-bases.md §4.1)

| Theory Component                              | Implementation                                                                      |
|-----------------------------------------------|-------------------------------------------------------------------------------------|
| Self-fulfilling speculation (De Grauwe, 2011) | `sell_threshold = extras["sell_threshold"]`; sell when `deviation < sell_threshold` |
| Amplifying sell pressure                      | `qty = min(600, position)`; maximum sell volume per round                           |
| Recovery buying                               | `elif deviation > 0.08: buy(min(400, affordable))`                                  |

### §2.2 CreditorPanicker (simulation-bases.md §4.2)

| Theory Component                            | Implementation                                                                              |
|---------------------------------------------|---------------------------------------------------------------------------------------------|
| Sovereign-bank nexus (Acharya et al., 2014) | `panic_threshold = extras["panic_threshold"]`; activates when `deviation < panic_threshold` |
| Amplification of initial shock              | `qty = min(700, position)` — larger than PeripheryBondSeller at 600                         |
| Slow re-entry                               | `elif deviation > 0.06: buy(min(300, affordable))` — lower recovery threshold than PBS      |

### §2.3 CoreBondBuyer (simulation-bases.md §4.3)

| Theory Component                                          | Implementation                                                                           |
|-----------------------------------------------------------|------------------------------------------------------------------------------------------|
| Flight-to-quality capital rotation (De Grauwe & Ji, 2012) | `flight_threshold = extras["flight_threshold"]`; buy when `deviation < flight_threshold` |
| Partial stabilization at crisis depths                    | `qty = min(400, affordable)` — provides partial floor                                    |
| Sell on recovery                                          | `elif deviation > 0.10: sell(min(400, position))`                                        |

### §2.4 ECBIntervenor (simulation-bases.md §4.4)

| Theory Component                     | Implementation                                                                                             |
|--------------------------------------|------------------------------------------------------------------------------------------------------------|
| Central bank backstop (Draghi, 2012) | `intervention_threshold = extras["intervention_threshold"]`; buy when `deviation < intervention_threshold` |
| Large order size                     | `qty = min(800, affordable)` — largest single buyer; circuit breaker role                                  |
| Gradual withdrawal on recovery       | `elif deviation > 0.05: sell(min(500, position))`                                                          |

### §2.5 HedgedFund (simulation-bases.md §4.5)

| Theory Component                              | Implementation                                                     |
|-----------------------------------------------|--------------------------------------------------------------------|
| Limits to arbitrage (Shleifer & Vishny, 1997) | `entry_threshold = extras["entry_threshold"]`; symmetric arbitrage |
| Buy on undervaluation                         | `if deviation < -entry_threshold: buy(min(500, affordable))`       |
| Sell on overvaluation                         | `elif deviation > entry_threshold: sell(min(500, position))`       |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Market collects all orders, computes net demand = sum(buy_qty) − sum(sell_qty), applies price impact + mean reversion + noise, broadcasts `market_data` with `price`, `fundamental`, `deviation`, `round`.

## §4 Variant Architecture

| Component      | Detail                                     |
|----------------|--------------------------------------------|
| Base class     | `GeneralPlayer`                            |
| Inference      | None (deterministic threshold comparisons) |
| Context        | `market_data` from broadcast               |
| Output parsing | Direct `{"action": ..., "quantity": ...}`  |
| Retry logic    | Not applicable                             |

## §5 Config Reference

Config file: `configs/EuropeanDebtCrisis/Rule/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `sell_threshold` (PeripheryBondSeller)
- `panic_threshold` (CreditorPanicker)
- `flight_threshold` (CoreBondBuyer)
- `intervention_threshold` (ECBIntervenor)
- `entry_threshold` (HedgedFund)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`

## §6 Running Instructions

```bash
python -m examples.EuropeanDebtCrisis.Rule.run_edc \
    -c configs/EuropeanDebtCrisis/Rule/simulation.yml
```

## §7 Expected Behavior

- **Crisis onset**: Occurs when `deviation < sell_threshold`; typically rounds 5–10
- **CDI**: 0.15–0.30 (15–30% below fundamental at trough)
- **CD**: 10–25 rounds (crisis duration in Rule baseline)
- **IER**: 0.75–0.95 (ECB covers most crisis rounds if threshold is well-calibrated)
- **SRT**: 5–15 rounds from trough to near-fundamental recovery

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
