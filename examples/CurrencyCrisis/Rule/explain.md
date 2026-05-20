# CurrencyCrisis Rule Variant — explain.md

## §1 Overview

The Rule variant implements `simulation-bases.md` with deterministic FX-market
threshold rules. It is the baseline for measuring whether speculative selling,
self-fulfilling momentum, central-bank defense, and fundamental anchoring can
produce a currency-crisis path without language-model reasoning.

| Aspect | Implementation |
|---|---|
| Variant | Rule |
| Market | `Market` clears order flow and broadcasts `price`, `fundamental`, `deviation`, `round` |
| Agents | `SpeculativeAttacker`, `SelfFulfillingTrader`, `CentralBankDefender`, `FundamentalHedger`, `NoiseTrader` |
| Runtime source | `examples/CurrencyCrisis/Rule/players.py` |
| Config source | `configs/CurrencyCrisis/Rule/players.yml` |

## §2 Theory → Implementation Mapping

| Theory Component | Implementation |
|---|---|
| Reserve-depletion attack (`simulation-bases.md §4.1`) | `SpeculativeAttacker` sells when `deviation < -attack_threshold` and buys back when deviation recovers. |
| Self-fulfilling expectation channel (`simulation-bases.md §4.2`) | `SelfFulfillingTrader` sells on negative deviation and buys cautiously on recovery. |
| Peg defense (`simulation-bases.md §4.3`) | `CentralBankDefender` buys when currency weakness exceeds `defense_threshold` and sells when overvalued. |
| Fundamental-value anchor (`simulation-bases.md §4.4`) | `FundamentalHedger` trades against large deviations from fair value. |
| Baseline FX liquidity (`simulation-bases.md §4.5`) | `NoiseTrader` adds random buy/sell/hold flow. |
| Price impact and mean reversion (`simulation-bases.md §3`) | `Market.perceive()` applies net-demand price impact, mean reversion to fundamental value, and Gaussian noise. |

## §3 Market Mechanism

The market uses the root-document price equation:

```text
P(t+1) = P(t) + price_impact * net_demand
       + mean_reversion * (fundamental - P(t)) + noise
```

`deviation = (price - fundamental) / fundamental` is the state variable consumed
by every investor class. Negative deviation means the domestic currency is weak
relative to the peg.

## §4 Variant-Specific Features

Rule decisions are deterministic conditional on the current market state and
config extras:

| Agent | Trigger | Action |
|---|---|---|
| `SpeculativeAttacker` | `deviation < -attack_threshold` | Sell up to `order_size` |
| `SpeculativeAttacker` | `deviation > attack_threshold` | Buy up to `order_size` |
| `SelfFulfillingTrader` | `deviation < -contagion_sensitivity` | Sell up to `order_size` |
| `CentralBankDefender` | `deviation < -defense_threshold` | Buy up to `order_size` |
| `FundamentalHedger` | `abs(deviation) > fundamental_threshold` | Buy below fair value, sell above fair value |
| `NoiseTrader` | random draw below `trade_probability` | Random buy or sell |

## §5 Config Reference

The variant uses `configs/CurrencyCrisis/Rule/players.yml`. Required extras are
read directly by the corresponding player classes:

| Component | Required extras |
|---|---|
| `Market` | `record_path`, `custom_state_hot_limit`, `initial_price`, `fundamental_value`, `price_impact`, `mean_reversion`, `noise_std` |
| Trading agents | `initial_cash`, `initial_position`, and each agent's threshold/order-size parameters |
| `NoiseTrader` | `trade_probability`, `min_order`, `max_order` |

## §6 Running Instructions

```bash
python examples/CurrencyCrisis/Rule/run_currencycrisis.py \
  -c configs/CurrencyCrisis/Rule/simulation.yml
```

The standard matrix runner can also discover this row as `CurrencyCrisis__Rule`.

## §7 Expected Behavior

- Speculative and self-fulfilling sellers should create negative-deviation
  pressure when the peg weakens.
- Central-bank and fundamental investors should dampen the sell-off.
- The price series should show whether attack pressure exceeds stabilizing
  demand.
- The Rule variant provides the deterministic benchmark for the LLM, RuleLLM,
  and RAG variants.

## §8 References

The theoretical references and calibration rationale are in
`simulation-bases.md §2`, `§4`, and `§6`.

## §9 Cross-Variant Role

Rule output is the baseline for:

| Comparison | Purpose |
|---|---|
| Rule vs LLM | Test whether persona-only LLM agents reproduce crisis dynamics. |
| Rule vs RuleLLM | Test how language reasoning changes outcomes when rule structure is explicit. |
| RuleLLM vs RAG | Test whether retrieved FX-crisis knowledge changes decision quality or crisis severity. |
