# MarketCrash / Leveraged Hedge Fund

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MarketCrash |
| Agent type | Leveraged Hedge Fund |
| Canonical class | `LeveragedHedgeFund` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: A leveraged investor subject to margin calls and liquidation. **Theoretical and Empirical Basis**: Margin spirals force deleveraging into drawdowns; see Brunnermeier and Pedersen (2009, DOI: 10.1093/rfs/hhn098). **Design Purpose**: Create forced selling after losses and balance-sheet stress. **Behavioral Framework**: Uses leverage, margin-call threshold, liquidation threshold, and momentum sensitivity. **Decision Process**: Mark portfolio equity to market; if equity ratio crosses margin thresholds, sell to reduce leverage; otherwise trade with momentum. **Worked Numerical Example**: If equity ratio falls from 0.6 to 0.45, below a 0.5 margin-call level, the fund sells part of its position to restore leverage. **Academic References**: Brunnermeier and Pedersen (2009); Adrian and Shin (2010, DOI: 10.1016/j.jfineco.2010.02.001).

## Financial Theory / Theoretical Basis

### Rule / `LeveragedHedgeFund`
- Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `5000.0` | Rule |
| initial_leverage | Rule: `3.0` | Rule |
| initial_position | Rule: `60.0` | Rule |
| liquidation_level | Rule: `0.3` | Rule |
| margin_call_level | Rule: `0.5` | Rule |
| momentum_sensitivity | Rule: `0.5` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | leveraged_hedge_fund | Leveraged Hedge Fund | `LeveragedHedgeFund` | 3 | `examples/MarketCrash/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 LeveragedHedgeFund

**Summary**: A leveraged investor subject to margin calls and liquidation.
**Theoretical and Empirical Basis**: Margin spirals force deleveraging into
drawdowns; see Brunnermeier and Pedersen (2009, DOI: 10.1093/rfs/hhn098).
**Design Purpose**: Create forced selling after losses and balance-sheet stress.
**Behavioral Framework**: Uses leverage, margin-call threshold, liquidation
threshold, and momentum sensitivity.
**Decision Process**: Mark portfolio equity to market; if equity ratio crosses
margin thresholds, sell to reduce leverage; otherwise trade with momentum.
**Worked Numerical Example**: If equity ratio falls from 0.6 to 0.45, below a
0.5 margin-call level, the fund sells part of its position to restore leverage.
**Academic References**: Brunnermeier and Pedersen (2009); Adrian and Shin
(2010, DOI: 10.1016/j.jfineco.2010.02.001).

## Source Docstring Excerpts

### Rule / `LeveragedHedgeFund`

```text
Leveraged hedge fund subject to margin constraints.

Theory: simulation-bases.md Section 4.2.

Parameters from config extras:
    - initial_leverage, margin_call_level, liquidation_level, momentum_sensitivity
```
