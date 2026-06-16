# EquityPremium / Long Horizon Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EquityPremium |
| Agent type | Long Horizon Investor |
| Canonical class | `LongHorizonInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Information set**: `stock_price` only (no rolling evaluation)

## Financial Theory / Theoretical Basis

### Rule / `LongHorizonInvestor`
- Theory: simulation-bases.md Section 4.2 -- LongHorizonInvestor
- Theoretical basis: Samuelson (1969) horizon effect; longer evaluation intervals

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| evaluation_window | Rule: `50` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_stock | Rule: `0.0` | Rule |
| target_stock_pct | Rule: `0.6` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | long_horizon | Long Horizon Investor | `LongHorizonInvestor` | 2 | `examples/EquityPremium/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 LongHorizonInvestor

#### Summary
Maintains a target stock allocation based on a long-horizon strategy, adjusting slowly toward the target. Long evaluation windows reduce perceived volatility, enabling higher equity allocation.

#### Theoretical and Empirical Foundation
- **Samuelson (1969)**: Intertemporal portfolio choice. Constant equity allocation is optimal for i.i.d. returns and power utility. DOI: `https://doi.org/10.2307/1926559`
- **Benartzi & Thaler (1995)**: Long evaluation horizon reduces perceived risk, lowering demanded premium. DOI: `https://doi.org/10.2307/2118511`

#### Design Purpose and Activation Scenarios
- **Activates when**: Always active; gradually rebalances toward `target_stock_pct`
- **Role in phenomenon**: Provides stabilizing equity demand; counteracts MyopicLossAverseInvestor's sell pressure
- **Interaction effects**: Supports stock price; reduces equity premium in aggregate

#### Behavioral Framework

**Information set**: `stock_price` only (no rolling evaluation)

**Mechanism narrative**: Computes the gap between current and target stock allocation, adjusts by 20% of the gap per round. Insensitive to short-term losses -- embodies the long-horizon rational benchmark.

**Mathematical model**:
```
target_value = target_stock_pct x portfolio_value
stock_qty = (target_value - current_stock_value) / price x 0.2
stock_qty clamped to [-15, +15]
```

**Behavioral properties**: Rational target allocation; slow rebalancing; horizon insensitivity

#### Decision Process Walkthrough

1. Observe `stock_price` from market broadcast
2. Compute portfolio_value = cash + stock x price
3. Compute gap between target and current stock value
4. Submit 20% of gap as stock_qty order

#### Worked Numerical Example

Given: price = 102, cash = 10000, stock = 50, target_stock_pct = 0.60
- portfolio_value = 10000 + 50 x 102 = 15100
- target_value = 0.60 x 15100 = 9060
- current_value = 50 x 102 = 5100
- stock_qty = (9060 - 5100) / 102 x 0.2 ≈ 7.8 -> buy 7.8 units

#### Academic References
- Samuelson, P. A. (1969). *Lifetime portfolio selection by dynamic stochastic programming*. ReStat. DOI: https://doi.org/10.2307/1926559

---

## Source Docstring Excerpts

### Rule / `LongHorizonInvestor`

```text
Long-horizon investor -- less myopic, accepts more risk over extended evaluation windows.

Theory: simulation-bases.md Section 4.2 -- LongHorizonInvestor
Theoretical basis: Samuelson (1969) horizon effect; longer evaluation intervals
reduce perceived volatility and allow higher equity allocation.
See simulation-bases.md Section 4.2 for mathematical model.
```
