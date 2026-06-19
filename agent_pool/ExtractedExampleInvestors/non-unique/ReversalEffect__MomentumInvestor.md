# ReversalEffect / Momentum Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ReversalEffect |
| Agent type | Momentum Investor |
| Canonical class | `MomentumInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Trades with the recent trend. **Theoretical and Empirical Basis**: Short-horizon continuation and positive-feedback trading. **Design Purpose**: Delay correction and create competition with contrarian pressure. **Behavioral Framework**: Uses recent return, `momentum_threshold`, `momentum_multiplier`, and `base_position_size`. **Decision Process**: Buy into positive momentum and sell into negative momentum when the signal exceeds threshold. **Worked Numerical Example**: A recent +6% move above a 3% threshold creates a buy order proportional to the excess trend. **Academic References**: Jegadeesh and Titman (1993), DOI: 10.1111/j.1540-6261.1993.tb04702.x; Shleifer and Summers (1990).

## Financial Theory / Theoretical Basis

### Rule / `MomentumInvestor`
- Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `20.0` | Rule |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `0.0` | Rule |
| lookback_window | Rule: `5` | Rule |
| momentum_multiplier | Rule: `10` | Rule |
| momentum_threshold | Rule: `0.02` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentum | Momentum Investor | `MomentumInvestor` | 3 | `examples/ReversalEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 MomentumInvestor

**Summary**: Trades with the recent trend.
**Theoretical and Empirical Basis**: Short-horizon continuation and
positive-feedback trading.
**Design Purpose**: Delay correction and create competition with contrarian
pressure.
**Behavioral Framework**: Uses recent return, `momentum_threshold`,
`momentum_multiplier`, and `base_position_size`.
**Decision Process**: Buy into positive momentum and sell into negative
momentum when the signal exceeds threshold.
**Worked Numerical Example**: A recent +6% move above a 3% threshold creates a
buy order proportional to the excess trend.
**Academic References**: Jegadeesh and Titman (1993), DOI:
10.1111/j.1540-6261.1993.tb04702.x; Shleifer and Summers (1990).

## Source Docstring Excerpts

### Rule / `MomentumInvestor`

```text
Short-term momentum investor.

Theory: simulation-bases.md Section 4.2.

Parameters from config extras:
    - lookback_window, momentum_threshold, base_position_size, momentum_multiplier
```
