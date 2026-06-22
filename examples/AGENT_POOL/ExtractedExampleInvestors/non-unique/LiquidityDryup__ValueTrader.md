# LiquidityDryup / Value Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LiquidityDryup |
| Agent type | Value Trader |
| Canonical class | `ValueTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Fundamental-anchored investor who buys when price is below fundamental and sells when above, providing stabilising liquidity when market prices deviate significantly. During a dry-up, `ValueTrader` acts as the last line of defence against extreme price dislocation.

## Financial Theory / Theoretical Basis

### Rule / `ValueTrader`
- Theory: simulation-bases.md Section 4.3
- Foundation: Shleifer & Vishny (1997) doi:10.1111/j.1540-6261.1997.tb03807.x
- Formula: quantity = deviation x value_multiplier; provides base_liquidity_provision

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_liquidity_provision | Rule: `20` | Rule |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `0.0` | Rule |
| liquidity_threshold | Rule: `0.05` | Rule |
| trade_threshold | Rule: `0.03` | Rule |
| value_multiplier | Rule: `30` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | value_trader | Value Trader | `ValueTrader` | 2 | `examples/LiquidityDryup/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 ValueTrader

**Summary**: Fundamental-anchored investor who buys when price is below fundamental and sells when above, providing stabilising liquidity when market prices deviate significantly. During a dry-up, `ValueTrader` acts as the last line of defence against extreme price dislocation.

**Foundation**: Shleifer, A., & Vishny, R. W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35-55. doi:[10.1111/j.1540-6261.1997.tb03807.x](https://doi.org/10.1111/j.1540-6261.1997.tb03807.x); Amihud, Y., & Mendelson, H. (1986). doi:10.1016/0304-405X(86)90065-6

**Design Purpose**: Model the patient capital that eventually halts a liquidity dry-up. When `|deviation| > trade_threshold`, `ValueTrader` provides both liquidity (`base_liquidity_provision`) and a corrective price signal. Their limited size (cap ±25) reflects limits-to-arbitrage constraints.

**Behavioral Framework**:

| Decision Variable   | Logic                            | Formula                               |
|---------------------|----------------------------------|---------------------------------------|
| `deviation`         | Price deviation from fundamental | `(fundamental - price) / fundamental` |
| Liquidity provision | Active when large deviation      | `base_liquidity_provision if abs(deviation) > liquidity_threshold else 0` |
| Quantity            | Value-corrective trade           | `deviation x value_multiplier if abs(deviation) > trade_threshold else 0` |
| Quantity cap        | Limits to arbitrage              | `max(-25, min(25, quantity))`         |

**Decision Walkthrough**:
1. Compute `deviation = (fundamental - price) / fundamental`.
2. If `|deviation| > liquidity_threshold`: provide `base_liquidity_provision` to market.
3. If `|deviation| > trade_threshold`: trade `deviation x value_multiplier` (buy if underpriced, sell if overpriced).
4. Cap at ±25.

**Worked Example**: `fundamental = 100`, `price = 85`, `deviation = 0.15 > trade_threshold = 0.03`. `quantity = 0.15 x 30 = 4.5`. Buy about 4.5 shares + provide `base_liquidity_provision = 20` liquidity units.

**References**: simulation-bases.md Section 2 Theory 3 (Kyle Impact); doi:10.1111/j.1540-6261.1997.tb03807.x

---

## Source Docstring Excerpts

### Rule / `ValueTrader`

```text
Value trader who provides liquidity to the market.

Theory: simulation-bases.md Section 4.3
Foundation: Shleifer & Vishny (1997) doi:10.1111/j.1540-6261.1997.tb03807.x
Activation: |deviation| > trade_threshold
Formula: quantity = deviation x value_multiplier; provides base_liquidity_provision

Parameters from config extras:
    - liquidity_threshold, trade_threshold, base_liquidity_provision, value_multiplier
```
