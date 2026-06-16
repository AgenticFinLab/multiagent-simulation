# MomentumEffect / Market Maker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MomentumEffect |
| Agent type | Market Maker |
| Canonical class | `MarketMaker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Supplies liquidity by reverting inventory toward a target. **Theoretical and Empirical Basis**: Inventory-control market making. **Design Purpose**: Dampen order imbalance without becoming a directional investor. **Behavioral Framework**: Rule uses `inventory_target=0.0` and `reversion_speed=0.2`. **Decision Process**: Buy or sell toward target inventory subject to cash and position constraints. **Worked Numerical Example**: Positive inventory above target generates a sell order. **Academic References**: Ho and Stoll (1981), DOI: 10.1016/0304-405X(81)90020-5.

## Financial Theory / Theoretical Basis

### Rule / `MarketMaker`
- Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `_hold_order`, `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `0.0` | Rule |
| inventory_target | Rule: `0.0` | Rule |
| reversion_speed | Rule: `0.2` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | market_maker | Market Maker | `MarketMaker` | 1 | `examples/MomentumEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 MarketMaker

**Summary**: Supplies liquidity by reverting inventory toward a target.  
**Theoretical and Empirical Basis**: Inventory-control market making.  
**Design Purpose**: Dampen order imbalance without becoming a directional
investor.  
**Behavioral Framework**: Rule uses `inventory_target=0.0` and
`reversion_speed=0.2`.  
**Decision Process**: Buy or sell toward target inventory subject to cash and
position constraints.  
**Worked Numerical Example**: Positive inventory above target generates a sell
order.  
**Academic References**: Ho and Stoll (1981), DOI: 10.1016/0304-405X(81)90020-5.

## Source Docstring Excerpts

### Rule / `MarketMaker`

```text
Market Maker providing liquidity.
Mean-reverts inventory to zero.

Theory: simulation-bases.md Section 4.4.

Parameters from config extras:
    - inventory_target, reversion_speed
```
