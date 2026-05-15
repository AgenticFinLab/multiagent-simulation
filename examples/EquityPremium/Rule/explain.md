# EquityPremium Rule — Implementation Explanation

## §1 Overview

The Rule variant is the deterministic baseline for the EquityPremium simulation. All five investors apply fixed allocation formulas to observed market data. Loss aversion and horizon effects are encoded directly as mathematical parameters, providing a clean, reproducible signal for measuring the equity premium puzzle.

| Aspect             | Detail                                                                    |
|--------------------|---------------------------------------------------------------------------|
| Variant            | Rule (deterministic baseline)                                             |
| Simulation         | EquityPremium                                                             |
| Decision Mechanism | Target allocation formulas — all parameters loaded from config            |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                           |
| Market Broadcast   | `stock_price`, `prev_stock_price`, `stock_return`, `bond_return`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 MyopicLossAverseInvestor (simulation-bases.md §4.1)

| Theory Component                               | Implementation                                                                                      |
|------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Myopic loss aversion (Benartzi & Thaler, 1995) | `evaluation_window = extras["evaluation_window"]`; rolling window risk computation                  |
| Loss aversion coefficient λ                    | `loss_aversion = extras["loss_aversion"]`; `perceived_risk = vol × (1 + loss_aversion × loss_prob)` |
| Risk-adjusted target allocation                | `target_stock_pct = max(0.1, 0.5 - risk_aversion × perceived_risk)`                                 |
| Gradual rebalancing                            | `stock_qty = gap × 0.3`, clamped to [−10, +10]                                                      |

### §2.2 LongHorizonInvestor (simulation-bases.md §4.2)

| Theory Component                          | Implementation                                                   |
|-------------------------------------------|------------------------------------------------------------------|
| Long evaluation horizon (Samuelson, 1969) | No rolling window; purely target-based rebalancing               |
| Target stock allocation                   | `target_stock_pct = extras["target_stock_pct"]` (typically 0.60) |
| Slow rebalancing                          | `stock_qty = gap × 0.2`, clamped to [−15, +15]                   |

### §2.3 RiskNeutralInvestor (simulation-bases.md §4.3)

| Theory Component                            | Implementation                                                                |
|---------------------------------------------|-------------------------------------------------------------------------------|
| Rational benchmark (Mehra & Prescott, 1985) | `excess_return = stock_return - bond_return`; no loss adjustment              |
| Proportional allocation                     | `stock_qty = excess_return × excess_return_multiplier`, clamped to [−20, +20] |
| No loss aversion                            | No loss_aversion or risk_aversion parameters used                             |

### §2.4 ConservativeInvestor (simulation-bases.md §4.4)

| Theory Component                                           | Implementation                                                        |
|------------------------------------------------------------|-----------------------------------------------------------------------|
| Prospect theory bond preference (Kahneman & Tversky, 1979) | `target_stock_pct = extras["target_stock_pct"]` (typically 0.25)      |
| Very slow rebalancing                                      | `stock_qty = gap × 0.1`, clamped to [−5, +5]                          |
| Persistent under-allocation                                | Low target + slow adjustment → persistent under-weighting of equities |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                       | Implementation                                                  |
|----------------------------------------|-----------------------------------------------------------------|
| Uninformed noise trading (Black, 1986) | `stock_qty = random.gauss(0, noise_std)`, clamped to [−10, +10] |
| Noise parameter                        | `noise_std = extras["noise_std"]`                               |
| Random direction                       | No signal; uncorrelated with fundamental or momentum            |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) × (1 + μ_stock + demand_impact + ε(t))
demand_impact = 0.001 × sum(stock_qty_i)
```

Market collects all investor `stock_qty` orders, computes net demand impact, adds random return, and broadcasts `market_data` containing `stock_price`, `prev_stock_price`, `stock_return`, `bond_return`, `round`.

## §4 Variant Architecture

| Component      | Detail                                                |
|----------------|-------------------------------------------------------|
| Base class     | `BaseInvestor` → `GeneralPlayer`                      |
| Inference      | None (deterministic formulas)                         |
| Context        | `market_data` from broadcast + `stock_history` buffer |
| Output parsing | Direct `{"stock_qty": ..., "strategy": ...}`          |
| Retry logic    | Not applicable                                        |

## §5 Config Reference

Config file: `configs/EquityPremium/Rule/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_stock` (all investors)
- `loss_aversion`, `evaluation_window`, `risk_aversion` (MyopicLossAverseInvestor)
- `target_stock_pct` (LongHorizonInvestor, ConservativeInvestor)
- `excess_return_multiplier` (RiskNeutralInvestor)
- `noise_std` (NoiseTrader)
- Market: `stock_expected_return`, `bond_return`, `stock_volatility`, `initial_stock_price`

## §6 Running Instructions

```bash
python -m examples.EquityPremium.Rule.run_equity_premium \
    -c configs/EquityPremium/Rule/simulation.yml
```

## §7 Expected Behavior

- **Equity premium**: 4–7% annualized; driven by MyopicLossAverseInvestor and ConservativeInvestor
- **Equity allocation**: MyopicLA holds 20–40%; LongHorizon holds 55–65%; Conservative holds 20–30%
- **LPI**: 0.40–0.55 for MyopicLossAverseInvestor with 5-round window
- **PWE (MyopicLA)**: 0.85–0.95 (wealth loss vs. buy-and-hold)

## §8 References

See `simulation-bases.md §2` for full DOI citations for all theoretical foundations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
