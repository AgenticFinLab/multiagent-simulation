# LTCMCollapse Rule — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Implements | `../simulation-bases.md` |
| Decision Logic | deterministic formulas in `players.py`; no LLM calls |
| Key Difference | establishes the fixed-rule baseline for convergence-arbitrage stress |
| Files | `players.py`, `run_ltcmcollapse.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

### ConvergenceArbitrageur

| Design Element | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.1` |
| Class | `ConvergenceArbitrageur` in `players.py` |
| Trigger | `abs(deviation) > extras["entry_spread"]` |
| Sizing | `cash * leverage * abs(deviation) / price`, capped by `extras["max_position"]` |
| State | `cash`, `position`, `price`, `fundamental`, `deviation` |
| Config | `configs/LTCMCollapse/Rule/players.yml` key `convergencearbitrageur` |

### LeverageTrader

| Design Element | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.2` |
| Class | `LeverageTrader` |
| Margin Trigger | `equity < abs(position * price) * extras["margin_call_threshold"]` |
| Deleveraging | sells or buys `int(abs(position) * 0.3)` |
| Opportunity Branch | buys when `deviation < -0.03` and no margin breach |

### RiskManager

| Design Element | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.3` |
| Class | `RiskManager` |
| Trigger | `abs(deviation) > extras["var_limit"] * 3` |
| Sizing | cuts 50% of absolute position |

### LiquidityProvider

| Design Element | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.4` |
| Class | `LiquidityProvider` |
| Stress Withdrawal | holds when `abs(deviation) > 0.05` |
| Normal Liquidity | buys or sells up to 500 shares inside `inventory_limit` |

### CentralBank

| Design Element | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.5` |
| Class | `CentralBank` |
| Trigger | `deviation < -extras["intervention_threshold"]` and probability draw succeeds |
| Sizing | fixed buy quantity of 2,000 shares |

## §3 Market Mechanism Implementation

Formula source: `simulation-bases.md §3.1`.

```
P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 0.01)
```

Implemented in `Market.perceive()`.

| Symbol | Python Variable | Config Path | Value |
|---|---|---|---:|
| `lambda` | `price_impact` | `market.extras.price_impact` | 0.03 |
| `gamma` | `mean_reversion` | `market.extras.mean_reversion` | 0.01 |
| `F` | `fundamental` | `market.extras.fundamental_value` | 100.0 |
| `epsilon` | `noise` | `market.extras.noise_std` | 0.015 |
| `D(t)` | `net_demand` | computed from inbound orders | - |

## §4 Variant-Specific Features

Rule mode is the deterministic reference. It contains no provider latency, prompt variance, or malformed-output risk. The only stochastic components are market noise and the probabilistic `CentralBank` rescue draw.

All investor thresholds are read from `config.extras`. The implemented order schema is standard: `{"type": "order", "action": ..., "quantity": ...}`.

## §5 Architecture Diagram

```text
Market.perceive()
  -> clear prior orders and update price
Market.decide()/act()
  -> broadcast {price, fundamental, deviation, round}
Investors.perceive()
  -> read market_update
Investors.decide()
  -> compute deterministic order
Investors.act()
  -> emit order for next market round
```

## §6 Configuration Reference

| Area | File | Notes |
|---|---|---|
| simulation | `configs/LTCMCollapse/Rule/simulation.yml` | 200 rounds, Ray and record settings |
| players | `configs/LTCMCollapse/Rule/players.yml` | market and investor classes/parameters |
| topology | `configs/LTCMCollapse/Rule/topology.yml` | market broadcasts to investors; investors route orders to market |
| persona | `configs/LTCMCollapse/Rule/persona.yml` | framework persona schema |

## §7 Expected Behavior Patterns

| Phase | Expected Rule Behavior |
|---|---|
| Normal | liquidity provider trades around fundamental; other agents hold or lightly trade |
| Stress | convergence and leverage agents react to widened deviation |
| Crisis | risk manager cuts positions; liquidity provider withdraws |
| Recovery | central-bank support and mean reversion stabilize price |

## §8 Validation Checklist

- `scripts/run_example_matrix.py --dry-run --scenario LTCMCollapse --mechanism Rule` discovers one row.
- `preflight_rows.py --row LTCMCollapse__Rule` reports zero failures.
- Full-run sample can be inherited from `fix-scenarios` if no runtime files change.

## §9 References

- `../simulation-bases.md`
- `../analysis-bases.md`
- `players.py`
- `configs/LTCMCollapse/Rule/players.yml`
