# Volmageddon Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | Volmageddon |
| Decision Mechanism | Deterministic current-market volatility quantity orders |
| Theory Reference | `examples/Volmageddon/simulation-bases.md` |
| Market Broadcast | `configs/Volmageddon/Rule/topology.yml` |

Volmageddon is a special trading schema scenario. It does not use limit-order
`bid_price` fields. The market consumes `action`, `quantity`, and `agent_type`,
then updates a volatility proxy from aggregate net demand at the current proxy
level.

## §2 Theory -> Implementation Mapping

### §2.1 ShortVolTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Short-vol carry and stop-loss covering | `ShortVolTrader` in `examples/Volmageddon/Rule/players.py` sells volatility when deviation is below -2% and buys to cover when `deviation > stop_loss`. |
| Required config | `stop_loss`, `initial_cash`, `initial_position`, `initial_price`, `fundamental_value` from `configs/Volmageddon/Rule/players.yml`. |
| Quantity schema | Emits `action` and non-negative `quantity`; no `bid_price` is used by the market. |

### §2.2 VolETNManager (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Inverse-volatility product rebalancing | `VolETNManager` buys volatility proxy exposure when deviation exceeds `rebalance_threshold`. |
| Required config | `rebalance_threshold` and `rebalance_size` from `configs/Volmageddon/Rule/players.yml`. |
| Quantity schema | Buy quantity is `int(deviation * rebalance_size)` subject to cash constraints. |

### §2.3 LongVolHedger (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Long-volatility insurance and profit-taking | `LongVolHedger` buys when the proxy is cheap and sells when volatility spikes. |
| Required config | `hedge_ratio` plus portfolio initialization fields. |
| Quantity schema | Orders are capped at 500 units and constrained by cash or inventory. |

### §2.4 VolArbitrageur (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Term-structure dislocation arbitrage | `VolArbitrageur` trades only when `abs(deviation) > entry_threshold`. |
| Required config | `entry_threshold` from `configs/Volmageddon/Rule/players.yml`. |
| Quantity schema | Quantity is `min(5000, int(abs(deviation) * 20000))` before cash/inventory constraints. |

### §2.5 EquityTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Volatility-linked equity de-risking | `EquityTrader` trades only when `abs(deviation) > 2 * risk_limit`. |
| Required config | `risk_limit` from `configs/Volmageddon/Rule/players.yml`. |
| Quantity schema | Quantity is `min(1000, int(abs(deviation) * 3000))` before constraints. |

## §3 Market Mechanism

`Market` is imported from `examples/Volmageddon/Rule/players.py`. It extracts
orders with `action` and `quantity`, computes net demand, applies
`price_impact`, `mean_reversion`, and `noise_std`, and broadcasts the next
round's `price`, `fundamental`, and `deviation`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/Volmageddon/Rule/players.py` |
| Prompt module | Not applicable |
| Inference | No remote model call |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic config/schema errors fail fast |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/Volmageddon/Rule/simulation.yml` | 200-round simulation entry point and record path |
| `configs/Volmageddon/Rule/players.yml` | Market parameters and five investor archetypes |
| `configs/Volmageddon/Rule/topology.yml` | Market update and investor order routing |
| `configs/Volmageddon/Rule/persona.yml` | Persona and recording metadata |

## §6 Running Instructions

```bash
python examples/Volmageddon/Rule/run_volmageddon.py -c configs/Volmageddon/Rule/simulation.yml
```

## §7 Expected Behavior

- Short-volatility covering and inverse-ETN rebalancing should create
  procyclical buy pressure during positive deviation episodes.
- Long-vol and arbitrage roles should provide partial stabilization.
- Equity traders should connect volatility stress to risk reduction.
- A full accepted sample must complete 200 rounds and pass structural quality
  review against `analysis-bases.md`.

## §8 References

See `examples/Volmageddon/simulation-bases.md §2` for theory references and
`§8` for historical anchors.

## §9 Variant Comparison

Rule is the deterministic baseline used to compare the LLM, RuleLLM, and Rag
variants on spike magnitude, timing, feedback attribution, and quality metrics.
