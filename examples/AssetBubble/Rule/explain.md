# Asset Bubble Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | Asset Bubble |
| Decision Mechanism | deterministic rule-based trading orders |
| Theory Reference | `examples/AssetBubble/simulation-bases.md` |
| Market Broadcast | `configs/AssetBubble/Rule/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

This variant is the executable baseline for `simulation-bases.md §4`: every
investor class directly computes a deterministic order from market state and
`configs/AssetBubble/Rule/players.yml`.

| Investor | Theory reference | Code implementation | Config path | Decision mechanism |
|---|---|---|---|---|
| `MomentumSpeculator` | `simulation-bases.md §4.1` | `players.py::MomentumSpeculator.decide()` computes `momentum = (price - MA_k) / MA_k`, buys above `0.01`, sells below `-0.02`, and caps orders after cash/short constraints. | `momentum_speculator.config.extras.{lookback_short,aggressiveness,base_position_size,leverage_multiplier}` | Greater-fool positive feedback demand. |
| `RationalArbitrageur` | `simulation-bases.md §4.2` | `players.py::RationalArbitrageur.decide()` computes `(price - fundamental) / fundamental`, shorts above threshold with a short-cost penalty, and respects `max_short_position`. | `rational_arbitrageur.config.extras.{deviation_threshold,base_position_size,max_short_position,short_cost_sensitivity}` | Limited corrective arbitrage. |
| `NoiseTrader` | `simulation-bases.md §4.3` | `players.py::NoiseTrader.decide()` combines Gaussian sentiment and `herding_weight * return * 10`, then trades only when the signal exceeds `+/-0.1`. | `noise_trader.config.extras.{sentiment_volatility,herding_weight,base_position_size}` | Stochastic herding and noise-trader risk. |
| `FundamentalInvestor` | `simulation-bases.md §4.4` | `players.py::FundamentalInvestor.decide()` trades every `trade_frequency` rounds using `(fundamental - price) / price`, capped at `+/-15`. | `fundamental_investor.config.extras.{trade_frequency,value_sensitivity,base_position_size}` | Slow value anchor. |
| `LeveragedBuyer` | `simulation-bases.md §4.5` | `players.py::LeveragedBuyer.decide()` checks `portfolio_value / initial_equity`; below threshold it sells half the long position, otherwise it scales momentum exposure by `leverage_ratio`. | `leveraged_buyer.config.extras.{leverage_ratio,margin_call_threshold,base_position_size,initial_equity}` | Procyclical leverage and forced deleveraging. |
| `ConservativeHolder` | `simulation-bases.md §4.6` | `players.py::ConservativeHolder.decide()` rebalances every `rebalance_frequency` rounds toward `target_position` with `gap * rebalance_rate`, capped at `+/-10`. | `conservative_holder.config.extras.{target_position,rebalance_frequency,rebalance_rate}` | Stabilizing strategic allocation. |

## §3 Market Mechanism

The coordinator is `players.py::Market`. It implements `simulation-bases.md §3.1`:

```text
P(t+1) = P(t) + price_impact * net_demand
               + mean_reversion * (fundamental(t+1) - P(t))
               + noise
```

`Market.perceive()` consumes orders with `bid_price`, `quantity`, and `strategy`.
`Market.decide()` broadcasts `price`, `prev_price`, `return`, `return_pct`,
`fundamental`, `bubble_ratio`, `volume`, `net_demand`, `round`, and
`short_cost_rate`. The same broadcast contract is retained by the API variants.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/AssetBubble/Rule/players.py` |
| Prompt module | Not applicable for Rule baseline |
| Inference | No remote model call is used in the Rule baseline. |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/AssetBubble/Rule/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/AssetBubble/Rule/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/AssetBubble/Rule/topology.yml` | Message routing between coordinator and agents. |
| `configs/AssetBubble/Rule/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/AssetBubble/Rule/run_bubble.py -c configs/AssetBubble/Rule/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/AssetBubble/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/AssetBubble/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
