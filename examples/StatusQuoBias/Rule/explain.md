# StatusQuoBias Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Implements | `../simulation-bases.md` |
| Decision Logic | Config-driven deterministic formulas |
| Key Difference from Other Variants | Investor behavior is fully specified in Python thresholds and sizing rules. |
| Primary Research Contribution | Establishes the deterministic status quo and default-inertia baseline. |
| Files | `players.py`, `run_statusquobias.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

### InertialHolder

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.1`; class docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism | `InertialHolder._make_decision()` holds unless `abs(deviation) > extras["change_threshold"]`. |
| Mathematical model | Quantity scales with `base_size`, deviation intensity, and `inertia_strength`. |
| State variables | `cash`, `position`, `price`, `fundamental`, and `deviation` are maintained in `custom_state`. |
| Parameters | `change_threshold`, `base_size`, and `inertia_strength` from `configs/StatusQuoBias/Rule/players.yml`. |

### DefaultFollower

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.2`; class docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism | `DefaultFollower._make_decision()` holds inside `active_deviation`. |
| Mathematical model | Quantity scales with `base_size`, `default_weight`, and deviation magnitude. |
| State variables | Same market and portfolio state as §4.1. |
| Parameters | `active_deviation`, `default_weight`, and `base_size` from config. |

### ActiveRebalancer

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.3`; class docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism | `ActiveRebalancer._make_decision()` trades when valuation deviation crosses `rebalance_threshold`. |
| Mathematical model | Quantity is `position_size * abs(deviation) / rebalance_threshold`, bounded by cash or holdings. |
| State variables | Same market and portfolio state as §4.1. |
| Parameters | `rebalance_threshold` and `position_size` from config. |

### MomentumTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.4`; class docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism | `MomentumTrader._make_decision()` follows deviation sign after `entry_threshold` is crossed. |
| Mathematical model | Quantity is `position_size * abs(deviation) / entry_threshold`, bounded by constraints. |
| State variables | Same market and portfolio state as §4.1. |
| Parameters | `entry_threshold` and `position_size` from config. |

### NoiseTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.5`; class docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism | `NoiseTrader._make_decision()` samples a random buy or sell when `trade_probability` activates. |
| Mathematical model | Quantity is sampled from `1..noise_size`, then bounded by cash or holdings. |
| State variables | Same market and portfolio state as §4.1. |
| Parameters | `trade_probability` and `noise_size` from config. |

## §3 Market Mechanism Implementation

Formula source: `simulation-bases.md §3.1`.

```text
P(t+1) = max(0.01, P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t))
```

| Simulation Symbol | Python Variable | Config Path | Default |
|---|---|---|---:|
| lambda | `price_impact` | `market.config.extras.price_impact` | 0.02 |
| gamma | `mean_reversion` | `market.config.extras.mean_reversion` | 0.02 |
| F | `fundamental` | `market.config.extras.fundamental_value` | 100.0 |
| sigma | `noise_std` | `market.config.extras.noise_std` | 0.01 |
| D(t) | `net_demand` | computed from investor orders | round-specific |

The market consumes `action`, `quantity`, and `agent_type`; investors also emit
`bid_price` and `reasoning` so the analysis output contract can inspect bid
curves and decision rationale.

## §4 Rule Variant-Specific Features

The Rule variant is deterministic except for market noise and the
`NoiseTrader`. It uses direct config fields rather than prompt text. All
investor classes return canonical order fields: `action`, `bid_price`,
`quantity`, `agent_type`, and `reasoning`.

## §5 Architecture Diagram

```text
Market.perceive(orders)
        |
        v
Market.decide() -> price/fundamental/deviation broadcast
        |
        v
Rule investor perceive() -> _make_decision() -> canonical order
        |
        v
Market aggregates net demand and updates P(t+1)
```

## §6 Configuration Reference

| Parameter | Config Path | Used By | Purpose |
|---|---|---|---|
| `price_impact` | `market.extras.price_impact` | Market | Demand impact. |
| `mean_reversion` | `market.extras.mean_reversion` | Market | Fundamental pull. |
| `change_threshold` | `inertialholder.extras.change_threshold` | InertialHolder | Status quo switching threshold. |
| `active_deviation` | `defaultfollower.extras.active_deviation` | DefaultFollower | Default drift threshold. |
| `rebalance_threshold` | `activerebalancer.extras.rebalance_threshold` | ActiveRebalancer | Rational rebalancing threshold. |
| `entry_threshold` | `momentumtrader.extras.entry_threshold` | MomentumTrader | Momentum activation threshold. |
| `trade_probability` | `noisetrader.extras.trade_probability` | NoiseTrader | Noise activation probability. |

## §7 Running Instructions

```bash
python examples/StatusQuoBias/Rule/run_statusquobias.py \
  -c configs/StatusQuoBias/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

`InertialHolder` and `DefaultFollower` should hold more often than
`ActiveRebalancer` after moderate deviations. Momentum and noise flow should
prevent the price path from being a pure threshold system.

## §9 References

Implementation traces to `../simulation-bases.md §3`, `../simulation-bases.md §4`,
and `../simulation-bases.md §6`. Analysis traces to `../analysis-bases.md §2`.
