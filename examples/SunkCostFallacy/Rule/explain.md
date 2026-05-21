# SunkCostFallacy Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Implements | `../simulation-bases.md` |
| Decision Logic | Config-driven deterministic sunk-cost, escalation, rational, opportunity-cost, and noise rules |
| Key Difference from Other Variants | Investor behavior is implemented directly in Python without LLM calls. |
| Primary Research Contribution | Establishes the deterministic baseline for sunk-cost holding and commitment escalation. |
| Files | `players.py`, `run_sunkcostfallacy.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

### SunkCostHolder

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.1`; class docstring cites `simulation-bases.md §4.1`. |
| Behavioral mechanism | `SunkCostHolder._make_decision()` holds losing positions and buys only after positive reinforcement. |
| Mathematical model | `deviation > hold_threshold` triggers a buy sized by `base_size`; negative deviation holds. |
| Parameters | `hold_threshold` and `base_size` from `configs/SunkCostFallacy/Rule/players.yml`. |

### CommitmentEscalator

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.2`; class docstring cites `simulation-bases.md §4.2`. |
| Behavioral mechanism | `CommitmentEscalator._make_decision()` buys after losses to average down. |
| Mathematical model | `deviation < -escalation_threshold` triggers `escalation_size * abs(deviation) / escalation_threshold`. |
| Parameters | `escalation_threshold` and `escalation_size` from config. |

### RationalCutter

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.3`; class docstring cites `simulation-bases.md §4.3`. |
| Behavioral mechanism | `RationalCutter._make_decision()` acts on valuation rather than prior cost. |
| Mathematical model | `abs(deviation) > cut_threshold` triggers valuation-based buy or sell. |
| Parameters | `cut_threshold` and `position_size` from config. |

### OpportunityCostTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.4`; class docstring cites `simulation-bases.md §4.4`. |
| Behavioral mechanism | `OpportunityCostTrader._make_decision()` reallocates when deviation exceeds `realloc_threshold`. |
| Mathematical model | Quantity scales with `position_size * abs(deviation) / realloc_threshold`. |
| Parameters | `realloc_threshold` and `position_size` from config. |

### NoiseTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.5`; class docstring cites `simulation-bases.md §4.5`. |
| Behavioral mechanism | `NoiseTrader._make_decision()` emits random low-information orders. |
| Mathematical model | `trade_probability` activates random direction and `1..noise_size` quantity. |
| Parameters | `trade_probability` and `noise_size` from config. |

## §3 Market Mechanism Implementation

Formula source: `simulation-bases.md §3.1`.

```text
P(t+1) = max(0.01, P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t))
```

`Market.perceive()` aggregates investor orders, updates price, and records price
and volume histories. `Market.decide()` broadcasts `price`, `fundamental`,
`deviation`, and `round`.

## §4 Rule Variant-Specific Features

The Rule variant emits canonical order fields: `action`, `bid_price`,
`quantity`, `agent_type`, and `reasoning`. It is deterministic except for
market noise and `NoiseTrader`.

## §5 Architecture Diagram

```text
Market.perceive(orders) -> price update
        |
        v
Market.decide() -> market_update
        |
        v
Rule investor perceive() -> _make_decision() -> canonical order
        |
        v
Market aggregates next-round demand
```

## §6 Configuration Reference

| Parameter | Config Path | Purpose |
|---|---|---|
| `price_impact` | `market.extras.price_impact` | Demand impact. |
| `mean_reversion` | `market.extras.mean_reversion` | Fundamental pull. |
| `hold_threshold` | `sunkcostholder.extras.hold_threshold` | Positive reinforcement threshold. |
| `escalation_threshold` | `commitmentescalator.extras.escalation_threshold` | Loss threshold for averaging down. |
| `cut_threshold` | `rationalcutter.extras.cut_threshold` | Rational valuation band. |
| `realloc_threshold` | `opportunitycosttrader.extras.realloc_threshold` | Opportunity-cost band. |
| `trade_probability` | `noisetrader.extras.trade_probability` | Noise activation probability. |

## §7 Running Instructions

```bash
python examples/SunkCostFallacy/Rule/run_sunkcostfallacy.py \
  -c configs/SunkCostFallacy/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

`SunkCostHolder` should avoid selling losers, `CommitmentEscalator` should add
buy pressure after losses, and rational/opportunity agents should trade on
forward-looking valuation.

## §9 References

Implementation traces to `../simulation-bases.md §3`, `../simulation-bases.md §4`,
and `../simulation-bases.md §6`. Analysis traces to `../analysis-bases.md §2`.
