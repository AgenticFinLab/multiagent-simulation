# LiquidityDryup / Momentum Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LiquidityDryup |
| Agent type | Momentum Trader |
| Canonical class | `MomentumTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Trend follower that amplifies price moves -- a critical accelerant in the liquidity spiral. By buying into rising prices and selling into falling prices, `MomentumTrader` intensifies the market maker's stress trigger, causing more withdrawal and less liquidity.

## Financial Theory / Theoretical Basis

### Rule / `MomentumTrader`
- Theory: simulation-bases.md Section 4.4
- Foundation: De Long et al. (1990) doi:10.1111/j.1540-6261.1990.tb03695.x
- Formula: quantity = return x momentum_multiplier; max(-35, min(35, qty))

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `0.0` | Rule |
| momentum_multiplier | Rule: `200` | Rule |
| momentum_threshold | Rule: `0.01` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentum_trader | Momentum Trader | `MomentumTrader` | 2 | `examples/LiquidityDryup/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 MomentumTrader

**Summary**: Trend follower that amplifies price moves -- a critical accelerant in the liquidity spiral. By buying into rising prices and selling into falling prices, `MomentumTrader` intensifies the market maker's stress trigger, causing more withdrawal and less liquidity.

**Foundation**: De Long, J. B., et al. (1990). doi:10.1111/j.1540-6261.1990.tb03695.x; Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:10.1093/rfs/hhn098

**Design Purpose**: Model the positive-feedback traders who transform an initial liquidity shock into a self-reinforcing cascade. Momentum trading in the simulation acts as the coupling mechanism between price impact and market maker withdrawal: large returns trigger momentum buys/sells -> amplified price impact -> higher `|return|` -> market maker withdrawal -> further amplification.

**Behavioral Framework**:

| Decision Variable | Logic                 | Formula                       |
|-------------------|-----------------------|-------------------------------|
| `ret`             | Single-period return  | `market_data["return"]`       |
| Activation        | Significant trend     | `abs(ret) > momentum_threshold` |
| Quantity          | Proportional to trend | `ret x momentum_multiplier`   |
| Quantity cap      | Position risk limit   | `max(-35, min(35, quantity))` |

**Decision Walkthrough**:
1. Receive `return` from market.
2. If `|return| <= momentum_threshold`: hold.
3. Else: `quantity = return x momentum_multiplier` (positive return -> buy; negative -> sell).
4. Cap at ±35 (larger than other agents to reflect momentum trader aggression).

**Worked Example**: `return = -0.04`, `momentum_threshold = 0.01`, `momentum_multiplier = 200`. `quantity = -0.04 x 200 = -8`. Sell 8 shares, amplifying the decline, further stressing market makers.

**References**: simulation-bases.md Section 2 Theory 5 (Momentum Cascades); doi:10.1111/j.1540-6261.1990.tb03695.x

---

## Source Docstring Excerpts

### Rule / `MomentumTrader`

```text
Momentum trader - can trigger liquidity crises.

Theory: simulation-bases.md Section 4.4
Foundation: De Long et al. (1990) doi:10.1111/j.1540-6261.1990.tb03695.x
Activation: |return| > momentum_threshold
Formula: quantity = return x momentum_multiplier; max(-35, min(35, qty))

Parameters from config extras:
    - momentum_threshold, momentum_multiplier
```
