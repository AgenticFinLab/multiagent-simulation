# EndowmentEffect Rule — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                       |
|--------------------|--------------------------------------------------------------|
| Variant            | Rule (deterministic baseline)                                |
| Simulation         | EndowmentEffect                                              |
| Decision Mechanism | Fixed threshold formulas — all parameters loaded from config |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                              |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                 |

The Rule variant is the deterministic baseline for the EndowmentEffect simulation. All five investors apply fixed threshold formulas to observed market data, with no stochastic LLM component. This provides the cleanest signal for measuring the endowment effect: any volume suppression or price stickiness is attributable purely to the rule-encoded ownership bias.

## §2 Theory → Implementation Mapping

### §2.1 EndowedHolder (simulation-bases.md §4.1)

| Theory Component                          | Implementation                                                                                         |
|-------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Endowment premium (Kahneman et al., 1990) | `endowment_premium = extras["endowment_premium"]`; sell only if `deviation > endowment_premium + 0.05` |
| Ownership suppresses selling              | `action = "hold"` by default; sell threshold requires deviation >> premium                             |
| Rational buying at undervaluation         | `if deviation < -0.05: buy(min(500, affordable))`                                                      |
| Sell reluctance factor                    | `sell_q = min(int(position * sell_reluctance), max(position, 0))`                                      |

### §2.2 StatusQuoSeller (simulation-bases.md §4.2)

| Theory Component                               | Implementation                                                                                |
|------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Status quo bias (Samuelson & Zeckhauser, 1988) | `status_quo_threshold = extras["status_quo_threshold"]`; sell only if `deviation > threshold` |
| Inertia in holding decisions                   | Default hold; only acts on large deviation or deep undervaluation                             |
| Buy on significant undervaluation              | `elif deviation < -0.08: buy(300)`                                                            |

### §2.3 RationalArbitrageur (simulation-bases.md §4.3)

| Theory Component                             | Implementation                                                                            |
|----------------------------------------------|-------------------------------------------------------------------------------------------|
| Rational expectations benchmark (Muth, 1961) | Uses `market_data["deviation"]` directly — no ownership adjustment                        |
| Symmetric arbitrage                          | `if deviation < -arb_threshold: buy(600)` and `elif deviation > arb_threshold: sell(600)` |
| `arb_threshold` from config                  | `arb_threshold = extras["arb_threshold"]`                                                 |

### §2.4 NewBuyer (simulation-bases.md §4.4)

| Theory Component                                         | Implementation                                                                   |
|----------------------------------------------------------|----------------------------------------------------------------------------------|
| Rational WTP equals market value (Kahneman et al., 1990) | `buy_threshold = extras["buy_threshold"]`; buys when `deviation < buy_threshold` |
| No ownership premium                                     | No endowment adjustment; pure deviation-based decision                           |
| Sell significant overvaluation                           | `elif deviation > 0.10: sell(min(400, position))`                                |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component                       | Implementation                                                                |
|----------------------------------------|-------------------------------------------------------------------------------|
| Uninformed noise trading (Black, 1986) | `if random.random() < trade_probability:` random direction and size [50, 200] |
| Trade probability from config          | `trade_probability = extras["trade_probability"]`                             |
| Constrained by portfolio               | `qty = min(qty, affordable/position)`                                         |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Implemented in `Market.decide()`. Market collects all investor orders (action + quantity), computes net demand (sum of signed quantities), applies price impact + mean reversion + noise, and broadcasts `market_data` containing `price`, `prev_price`, `fundamental`, `deviation`, `return_pct`, `round`.

## §4 Variant Architecture

| Component      | Detail                                    |
|----------------|-------------------------------------------|
| Base class     | `GeneralPlayer`                           |
| Inference      | None (deterministic formulas)             |
| Context        | `market_data` from broadcast              |
| Output parsing | Direct `{"action": ..., "quantity": ...}` |
| Retry logic    | Not applicable                            |

## §5 Config Reference

Config file: `configs/EndowmentEffect/Rule/simulation.yml`

Key extras per investor:
- `initial_cash`, `initial_position` (all investors)
- `endowment_premium`, `sell_reluctance` (EndowedHolder)
- `status_quo_threshold` (StatusQuoSeller)
- `arb_threshold` (RationalArbitrageur)
- `buy_threshold` (NewBuyer)
- `trade_probability` (NoiseTrader)
- Market: `price_impact`, `mean_reversion`, `noise_std`, `fundamental_value`, `initial_price`

## §6 Running Instructions

```bash
python -m examples.EndowmentEffect.Rule.run_endowment_effect \
    -c configs/EndowmentEffect/Rule/simulation.yml
```

Or via Streamlit UI: select "EndowmentEffect" → "Rule" variant.

## §7 Expected Behavior

- **Price stickiness**: Price remains 5–15% above fundamental for 15–50 rounds before correction
- **Volume suppression**: EndowedHolder and StatusQuoSeller hold for majority of rounds; turnover 40–60% of rational baseline
- **MAD target**: 0.03–0.12 (see analysis-bases.md §2.2)
- **Half-life**: 15–50 rounds for deviation to decay by 50%
- **RationalArbitrageur**: Active seller throughout overvaluation phase; drives gradual correction
- **NoiseTrader**: Provides ≈10–15 units/round of random background volume

## §8 References

See `simulation-bases.md §2` for full DOI citations for all theoretical foundations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
