# EquityPremium / Conservative Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EquityPremium |
| Agent type | Conservative Investor |
| Canonical class | `ConservativeInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Information set**: `stock_price`

## Financial Theory / Theoretical Basis

### Rule / `ConservativeInvestor`
- Theory: simulation-bases.md Section 4.4 -- ConservativeInvestor
- Theoretical basis: Kahneman & Tversky (1979) prospect theory; heightened loss

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_stock | Rule: `0.0` | Rule |
| target_stock_pct | Rule: `0.2` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | conservative | Conservative Investor | `ConservativeInvestor` | 3 | `examples/EquityPremium/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ConservativeInvestor

#### Summary
Prefers bond allocation; adjusts toward a low equity target very slowly. Embodies the prospect-theory-driven bond preference that amplifies the equity premium puzzle.

#### Theoretical and Empirical Foundation
- **Kahneman & Tversky (1979)**: Prospect theory; loss aversion drives persistent bond preference. DOI: `https://doi.org/10.2307/1914185`
- **Benartzi & Thaler (1995)**: Conservative investors demand high premium before entering equities. DOI: `https://doi.org/10.2307/2118511`

#### Design Purpose and Activation Scenarios
- **Activates when**: Always active; allocates minimally to stocks
- **Role in phenomenon**: Represents the majority of retail investors who demand the high premium; key source of the puzzle
- **Interaction effects**: Persistent sell/hold pressure on equities; reinforces MyopicLossAverseInvestor's direction

#### Behavioral Framework

**Information set**: `stock_price`

**Mechanism narrative**: Targets a low stock allocation (e.g., 20-30%), adjusts slowly (10% of gap per round). Conservative rebalancing means stock allocation rarely reaches target.

**Mathematical model**:
```
target_value = target_stock_pct x portfolio_value
stock_qty = (target_value - current_stock_value) / price x 0.1
stock_qty clamped to [-5, +5]
```

**Behavioral properties**: Loss aversion; strong status quo bias; slow adjustment

#### Decision Process Walkthrough

1. Observe `stock_price`
2. Compute target vs. current stock value
3. Adjust 10% of gap per round (clamped ±5)

#### Worked Numerical Example

Given: price = 100, cash = 15000, stock = 20, target_stock_pct = 0.25
- portfolio_value = 15000 + 20 x 100 = 17000
- target_value = 0.25 x 17000 = 4250; current_value = 2000
- stock_qty = (4250 - 2000) / 100 x 0.1 = 2.25 -> buy 2.25 units

#### Academic References
- Kahneman, D., & Tversky, A. (1979). *Prospect theory*. Econometrica. DOI: https://doi.org/10.2307/1914185

---

## Source Docstring Excerpts

### Rule / `ConservativeInvestor`

```text
Conservative investor -- prefers bonds, demands high equity premium before switching.

Theory: simulation-bases.md Section 4.4 -- ConservativeInvestor
Theoretical basis: Kahneman & Tversky (1979) prospect theory; heightened loss
sensitivity drives persistent bond preference even at attractive equity returns.
See simulation-bases.md Section 4.4 for mathematical model.
```
