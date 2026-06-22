# DispositionEffect / Index Holder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Index Holder |
| Canonical class | `IndexHolder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

`IndexHolder` is the passive buy-and-hold baseline. It does not actively trade, so it has no realized-gain or realized-loss timing bias.

## Financial Theory / Theoretical Basis

### Rule / `IndexHolder`
- Theory: simulation-bases.md Section 4.4 -- IndexHolder
- Theoretical basis: Sharpe (1991) passive investing; zero disposition effect by design.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `50.0` | Rule |
| initial_purchase_price | Rule: `100.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | index_holder | Index Holder | `IndexHolder` | 1 | `examples/DispositionEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 IndexHolder

#### Section 4.4.1 Summary

`IndexHolder` is the passive buy-and-hold baseline. It does not actively trade, so it has no realized-gain or realized-loss timing bias.

#### Section 4.4.2 Theoretical and Empirical Foundation

The design follows Sharpe's passive-investing benchmark logic: a passive holder captures market return without behavioral trading mistakes.

#### Section 4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| any market state | hold | no active order-flow contribution | Passive benchmark |

#### Section 4.4.4 Behavioral Framework

```python
quantity = 0
```

#### Section 4.4.5 Decision Process Walkthrough

The investor receives market prices but never buys or sells. It provides a clean comparison for active behavioral and rational strategies.

#### Section 4.4.6 Worked Numerical Example

At `price = 110` and `position = 50`, the order remains `quantity = 0`; portfolio value changes only through mark-to-market price movement.

#### Section 4.4.7 Academic References

Sharpe (1991); passive index-investing benchmark literature.

---

## Source Docstring Excerpts

### Rule / `IndexHolder`

```text
Passive buy-and-hold investor (no active trading).

Theory: simulation-bases.md Section 4.4 -- IndexHolder
Theoretical basis: Sharpe (1991) passive investing; zero disposition effect by design.
See simulation-bases.md Section 4.4 for mathematical model.
```
