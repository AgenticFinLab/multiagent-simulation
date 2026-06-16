# MomentumEffect / Fundamental Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MomentumEffect |
| Agent type | Fundamental Trader |
| Canonical class | `FundamentalTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Trades against mispricing relative to fundamental value. **Theoretical and Empirical Basis**: Fundamental-value anchoring and limits of arbitrage. **Design Purpose**: Provide long-run gravity against trend overshoot. **Behavioral Framework**: Rule uses `value_threshold=0.05`, `scale=1.5`, `max_position=50.0`. **Decision Process**: Buy undervaluation and sell overvaluation once mispricing exceeds threshold. **Worked Numerical Example**: Price 8% below fundamental triggers a buy. **Academic References**: Shleifer and Vishny (1997), DOI: 10.1111/j.1540-6261.1997.tb03807.x.

## Financial Theory / Theoretical Basis

### Rule / `FundamentalTrader`
- Theory: simulation-bases.md Section 4.6.

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
| max_position | Rule: `50.0` | Rule |
| scale | Rule: `1.5` | Rule |
| value_threshold | Rule: `0.05` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | fundamental_trader | Fundamental Trader | `FundamentalTrader` | 2 | `examples/MomentumEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.6 FundamentalTrader / FundamentalAnchor

**Summary**: Trades against mispricing relative to fundamental value.  
**Theoretical and Empirical Basis**: Fundamental-value anchoring and limits of
arbitrage.  
**Design Purpose**: Provide long-run gravity against trend overshoot.  
**Behavioral Framework**: Rule uses `value_threshold=0.05`, `scale=1.5`,
`max_position=50.0`.  
**Decision Process**: Buy undervaluation and sell overvaluation once mispricing
exceeds threshold.  
**Worked Numerical Example**: Price 8% below fundamental triggers a buy.  
**Academic References**: Shleifer and Vishny (1997), DOI:
10.1111/j.1540-6261.1997.tb03807.x.

## Source Docstring Excerpts

### Rule / `FundamentalTrader`

```text
Fundamental Analysis: Trade toward intrinsic value.
Provides weak stabilizing force against momentum.

Theory: simulation-bases.md Section 4.6.

Parameters from config extras:
    - value_threshold, scale, max_position
```
