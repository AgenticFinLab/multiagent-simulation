# EquityPremium / Risk Neutral Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EquityPremium |
| Agent type | Risk Neutral Investor |
| Canonical class | `RiskNeutralInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Information set**: `stock_return`, `bond_return`

## Financial Theory / Theoretical Basis

### Rule / `RiskNeutralInvestor`
- Theory: simulation-bases.md Section 4.3 -- RiskNeutralInvestor
- Theoretical basis: Mehra & Prescott (1985) equity premium puzzle baseline; standard

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| excess_return_multiplier | Rule: `500` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_stock | Rule: `0.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | risk_neutral | Risk Neutral Investor | `RiskNeutralInvestor` | 1 | `examples/EquityPremium/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 RiskNeutralInvestor

#### Summary
Trades on the excess return signal between stocks and bonds. Represents the standard expected-utility benchmark that the equity premium puzzle challenges.

#### Theoretical and Empirical Foundation
- **Mehra & Prescott (1985)**: Risk-neutral benchmark where excess return fully explains allocation. DOI: `https://doi.org/10.1016/0304-3932(85)90061-3`
- **Lucas (1978)**: Asset pricing under rational expectations. DOI: `https://doi.org/10.2307/1913837`

#### Design Purpose and Activation Scenarios
- **Activates when**: `excess_return = stock_return - bond_return` ≠ 0
- **Role in phenomenon**: Provides rational benchmark; its modest allocation reveals why the puzzle exists
- **Interaction effects**: Partial counterforce to myopic loss-averse selling

#### Behavioral Framework

**Information set**: `stock_return`, `bond_return`

**Mechanism narrative**: Computes excess return and scales it by a multiplier. Trades proportionally to the signal without loss aversion adjustment.

**Mathematical model**:
```
excess_return = stock_return - bond_return
stock_qty = excess_return x excess_return_multiplier
stock_qty clamped to [-20, +20]
```

**Behavioral properties**: Fully rational; no loss aversion; ignores short-term volatility

#### Decision Process Walkthrough

1. Observe `stock_return` and `bond_return`
2. Compute excess_return
3. Submit stock_qty = excess_return x multiplier

#### Worked Numerical Example

Given: stock_return = 0.008, bond_return = 0.002, multiplier = 500
- excess_return = 0.006
- stock_qty = 0.006 x 500 = 3.0 -> buy 3 units

#### Academic References
- Mehra, R., & Prescott, E. C. (1985). *The equity premium: A puzzle*. JME. DOI: https://doi.org/10.1016/0304-3932(85)90061-3

---

## Source Docstring Excerpts

### Rule / `RiskNeutralInvestor`

```text
Risk-neutral investor -- theoretically optimal allocation based on expected excess return.

Theory: simulation-bases.md Section 4.3 -- RiskNeutralInvestor
Theoretical basis: Mehra & Prescott (1985) equity premium puzzle baseline; standard
expected-utility maximizer cannot explain the observed equity premium.
See simulation-bases.md Section 4.3 for mathematical model.
```
