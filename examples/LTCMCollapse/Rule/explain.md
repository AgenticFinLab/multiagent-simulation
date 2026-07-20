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

### §2.1 ConvergenceArbitrageur (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.1` |
| Class | `ConvergenceArbitrageur` in `players.py` |
| Trigger | `abs(deviation) > extras["entry_spread"]` |
| Sizing | `cash * leverage * abs(deviation) / price`, capped by remaining room below `extras["max_position"]` |
| State | `cash`, `position`, `price`, `fundamental`, `deviation` |
| Config | `configs/LTCMCollapse/Rule/players.yml` key `convergencearbitrageur` |

### §2.2 LeverageTrader (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.2` |
| Class | `LeverageTrader` |
| Margin Trigger | `equity < abs(position * price) * extras["margin_call_threshold"]` |
| Equity | `abs(position * initial_price) * (1 / leverage_ratio + margin_call_threshold) + position * (price - initial_price)` |
| Deleveraging | sells or buys `int(abs(position) * extras["delever_fraction"])`; a zero-lot close becomes `hold` |
| Opportunity Branch | buys `base_size` when `deviation < -margin_call_threshold` and no margin breach |

### §2.3 RiskManager (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.3` |
| Class | `RiskManager` |
| Trigger | `abs(deviation) > max(extras["var_trigger"], extras["var_limit"] * extras["var_multiplier"])` |
| Sizing | cuts `risk_cut_fraction` of absolute position |

### §2.4 LiquidityProvider (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.4` |
| Class | `LiquidityProvider` |
| Stress Withdrawal | provision tapers as `max(0, 1 - abs(deviation) / stress_exit)` |
| Normal Liquidity | buys or sells up to `base_size * provision_fraction` inside `inventory_limit` |

### §2.5 CentralBank (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Theory | `simulation-bases.md §4.5` |
| Class | `CentralBank` |
| Trigger | `deviation < -extras["intervention_threshold"]` and probability draw succeeds |
| Sizing | `intervention_size` after a seeded rescue draw; otherwise a seeded `noise_size` background buy may occur |

## §3 Market Mechanism Implementation

Formula source: `simulation-bases.md §3.1`.

```
P(t+1) = max(P(t) + lambda * D(t) / M + gamma * [F - P(t)] + epsilon(t) + F*S(t), P_min)
```

Implemented in `Market.perceive()`.

| Symbol | Python Variable | Config Path | Value |
|---|---|---|---:|
| `lambda` | `price_impact` | `market.extras.price_impact` | 0.03 |
| `M` | `market_depth` | `market.extras.market_depth` | 100.0 |
| `gamma` | `mean_reversion` | `market.extras.mean_reversion` | 0.01 |
| `F` | `fundamental` | `market.extras.fundamental_value` | 100.0 |
| `epsilon` | `noise` | `market.extras.noise_std` | 0.015 |
| `D(t)` | `net_demand` | computed from inbound orders | - |
| `S(t)` | `shock_return` | `market.extras.shock_schedule` | rounds 20-23 |
| `P_min` | `price_floor` | `market.extras.price_floor` | 0.01 |

## §4 Variant-Specific Features

Rule mode is the reproducible deterministic-policy reference. It contains no provider latency, prompt variance, or malformed-output risk. Market noise and central-bank draws are fixed by the identity/round seed.

All investor thresholds are read from `config.extras`. The implemented order schema is standard: `{"type": "order", "action": ..., "quantity": ...}`.

## §5 Architecture Diagram

```text
Market.perceive()
  -> clear previous orders and update price
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
- Runtime logic should remain stable unless a documented mechanism or contract defect is found.

## §9 References

- `../simulation-bases.md`
- `../analysis-bases.md`
- `players.py`
- `configs/LTCMCollapse/Rule/players.yml`
