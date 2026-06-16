# LiquidityDryup / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LiquidityDryup |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Submits random Gaussian order flow that provides baseline liquidity and masks informed trading signals. During a dry-up, noise trading is the only source of trading volume when market makers withdraw, but its random direction provides no stabilising force.

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5
- Foundation: Black (1986) doi:10.1111/j.1540-6261.1986.tb04513.x
- Formula: quantity = N(0, noise_volatility); max(-15, min(15, qty))

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
| noise_volatility | Rule: `10.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noise_trader | Noise Trader | `NoiseTrader` | 2 | `examples/LiquidityDryup/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

**Summary**: Submits random Gaussian order flow that provides baseline liquidity and masks informed trading signals. During a dry-up, noise trading is the only source of trading volume when market makers withdraw, but its random direction provides no stabilising force.

**Foundation**: Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. doi:[10.1111/j.1540-6261.1986.tb04513.x](https://doi.org/10.1111/j.1540-6261.1986.tb04513.x); De Long, J. B., et al. (1990). doi:10.1111/j.1540-6261.1990.tb03695.x

**Design Purpose**: Represent uninformed trading that provides market depth in normal conditions but cannot substitute for market makers during a stress event. High noise volatility relative to market maker liquidity can trigger dry-up even without a fundamental shock.

**Behavioral Framework**:

| Decision Variable  | Logic           | Formula                       |
|--------------------|-----------------|-------------------------------|
| Quantity           | Random Gaussian | `N(0, noise_volatility)`      |
| Quantity cap       | Risk management | `max(-15, min(15, quantity))` |
| Provides liquidity | Never           | Always 0                      |

**Decision Walkthrough**:
1. Sample `quantity ~ N(0, noise_volatility)`.
2. Cap at ±15.
3. Submit order; `provides_liquidity = 0` always.

**Worked Example**: `noise_volatility = 5`. Sample `quantity = 8.3`. Buy 8 shares at current price. No contribution to `total_liquidity` -- market maker withdrawal is not offset.

**References**: simulation-bases.md Section 2 Theory 5; doi:10.1111/j.1540-6261.1986.tb04513.x

---

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Noise trader providing random trades.

Theory: simulation-bases.md Section 4.5
Foundation: Black (1986) doi:10.1111/j.1540-6261.1986.tb04513.x
Formula: quantity = N(0, noise_volatility); max(-15, min(15, qty))

Parameters from config extras:
    - noise_volatility
```
