# EquityPremium / Myopic Loss Averse Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EquityPremium |
| Agent type | Myopic Loss Averse Investor |
| Canonical class | `MyopicLossAverseInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Information set**: `stock_price`, `stock_history` (rolling `evaluation_window` entries), `stock_return`

## Financial Theory / Theoretical Basis

### Rule / `MyopicLossAverseInvestor`
- Theory: simulation-bases.md Section 4.1 -- MyopicLossAverseInvestor
- Theoretical basis: Benartzi & Thaler (1995) myopic loss aversion; frequent

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| evaluation_window | Rule: `5` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_stock | Rule: `0.0` | Rule |
| loss_aversion | Rule: `2.25` | Rule |
| risk_aversion | Rule: `2.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | mla | Myopic Loss Averse | `MyopicLossAverseInvestor` | 5 | `examples/EquityPremium/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 MyopicLossAverseInvestor

#### Summary
Evaluates portfolio over a short rolling window, overweighting recent losses. Frequent negative realizations drive extreme equity risk aversion, demanding high premiums before holding stocks.

#### Theoretical and Empirical Foundation
- **Benartzi & Thaler (1995)**: Myopic loss aversion. Investors who evaluate over 1-year horizons and have lambda ≈ 2.25 demand ~6% equity premium. DOI: `https://doi.org/10.2307/2118511`
- **Kahneman & Tversky (1979)**: Prospect theory. Loss aversion coefficient lambda ≈ 2-2.5 drives asymmetric evaluation. DOI: `https://doi.org/10.2307/1914185`

#### Design Purpose and Activation Scenarios
- **Activates when**: Rolling window loss probability is high (recent negative returns)
- **Role in phenomenon**: Amplifies equity risk premium; primary driver of the puzzle in simulation
- **Interaction effects**: Reduces net stock demand, driving price below fundamental; counterbalanced by LongHorizonInvestor

#### Behavioral Framework

**Information set**: `stock_price`, `stock_history` (rolling `evaluation_window` entries), `stock_return`

**Mechanism narrative**: Computes recent return volatility and loss probability over a short window. Multiplies volatility by a loss-aversion-weighted factor. Sets target stock allocation inversely proportional to perceived risk. Adjusts toward target gradually (30% of gap per round).

**Mathematical model**:
```
returns = [r_t-1, r_t-2, ..., r_t-evaluation_window]
vol = std(returns)
loss_prob = count(r < 0) / evaluation_window
perceived_risk = vol x (1 + loss_aversion x loss_prob)
target_stock_pct = max(0.1, 0.5 - risk_aversion x perceived_risk)
stock_qty = (target_value - current_value) / price x 0.3
```

**Behavioral properties**: Bounded rationality; myopic evaluation horizon; loss aversion (lambda > 1)

#### Decision Process Walkthrough

1. Observe `stock_price` and retrieve `stock_history` for last `evaluation_window` rounds
2. Compute `vol` and `loss_prob` from return series
3. Compute `perceived_risk = vol x (1 + loss_aversion x loss_prob)`
4. Compute `target_stock_pct = max(0.1, 0.5 - risk_aversion x perceived_risk)`
5. Submit stock_qty adjustment (clamped to [-10, +10])

#### Worked Numerical Example

Given: price = 105, evaluation_window = 5, recent returns = [-0.02, -0.01, 0.01, -0.02, 0.00]
- vol = 0.013, loss_prob = 0.6
- loss_aversion = 2.25, risk_aversion = 3
- perceived_risk = 0.013 x (1 + 2.25 x 0.6) = 0.031
- target_stock_pct = max(0.1, 0.5 - 3 x 0.031) = 0.407
- stock_qty = (0.407 x portfolio_value - current_stock_value) / 105 x 0.3 -> sell signal

#### Academic References
- Benartzi, S., & Thaler, R. H. (1995). *Myopic loss aversion and the equity premium puzzle*. QJE. DOI: https://doi.org/10.2307/2118511

---

## Source Docstring Excerpts

### Rule / `MyopicLossAverseInvestor`

```text
Myopic Loss Averse Investor -- evaluates frequently, overweights recent losses.

Theory: simulation-bases.md Section 4.1 -- MyopicLossAverseInvestor
Theoretical basis: Benartzi & Thaler (1995) myopic loss aversion; frequent
evaluation amplifies loss sensitivity, driving excessive equity risk premium.
See simulation-bases.md Section 4.1 for mathematical model.
```
