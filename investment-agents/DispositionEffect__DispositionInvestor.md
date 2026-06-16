# DispositionEffect / Disposition Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | DispositionEffect |
| Agent type | Disposition Investor |
| Canonical class | `DispositionInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

`DispositionInvestor` is the primary behavioral agent. It treats the original purchase price as a mental-accounting reference point, sells winners quickly, and realizes losers only after a larger drawdown.

## Financial Theory / Theoretical Basis

### Rule / `DispositionInvestor`
- Disposition Effect Investor (Prospect Theory).
- Behavior:
- - Sells winners quickly (gain_threshold ~10%)
- - Holds losers stubbornly (loss_threshold ~30%)
- Theory: simulation-bases.md Section 4.1 -- DispositionInvestor
- Theoretical basis: Kahneman & Tversky (1979) Prospect Theory; asymmetric gain/loss treatment with lambda = 2.25.

## Behavior and Decision Logic

- Key implementation methods: `_hold_order`, `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| buy_fraction | Rule: `0.15` | Rule |
| custom_state_hot_limit | Rule: `3` | Rule |
| gain_threshold | Rule: `0.03` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `30.0` | Rule |
| initial_purchase_price | Rule: `100.0` | Rule |
| loss_aversion | Rule: `2.25` | Rule |
| loss_threshold | Rule: `-0.1` | Rule |
| max_position | Rule: `30.0` | Rule |
| sell_fraction_gain | Rule: `0.5` | Rule |
| sell_fraction_loss | Rule: `0.15` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | disposition_investor | Disposition Investor | `DispositionInvestor` | 50 | `examples/DispositionEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 DispositionInvestor

#### Section 4.1.1 Summary

`DispositionInvestor` is the primary behavioral agent. It treats the original purchase price as a mental-accounting reference point, sells winners quickly, and realizes losers only after a larger drawdown.

#### Section 4.1.2 Theoretical and Empirical Foundation

The agent implements Prospect Theory's reference dependence and loss aversion (Kahneman & Tversky, 1979), Shefrin and Statman's (1985) disposition-effect mechanism, and Odean's (1998) PGR/PLR empirical benchmark.

#### Section 4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `gain_loss >= gain_threshold` | sell winner | realizes gains quickly and raises PGR | Prospect Theory gain-domain risk aversion |
| `gain_loss <= loss_threshold` | reluctantly sell loser | realizes fewer losses and lowers PLR | Prospect Theory loss-domain risk seeking |
| `-0.01 <= gain_loss < 0.01` | buy near reference | reinforces anchoring to purchase price | Mental accounting |

#### Section 4.1.4 Behavioral Framework

```python
gain_loss = (price - purchase_price) / purchase_price
if gain_loss >= gain_threshold:
    quantity = -position * sell_fraction_gain
elif gain_loss <= loss_threshold:
    quantity = -position * sell_fraction_loss
elif -0.01 <= gain_loss < 0.01 and position < max_position:
    quantity = min((max_position - position) * buy_fraction, cash * 0.15 / price)
else:
    quantity = 0
```

#### Section 4.1.5 Decision Process Walkthrough

At a 3% gain, the investor sells half of the position to lock in gains. At a 7% loss, the investor holds because the loss threshold has not been reached. At a 10% loss, it sells only a small fraction.

#### Section 4.1.6 Worked Numerical Example

With `position = 30`, `purchase_price = 100`, `price = 103`, and `gain_threshold = 0.03`, `gain_loss = 0.03`; the sell order is `-30 * 0.5 = -15` shares.

#### Section 4.1.7 Academic References

Kahneman & Tversky (1979); Shefrin & Statman (1985); Odean (1998).

---

## Source Docstring Excerpts

### Rule / `DispositionInvestor`

```text
Disposition Effect Investor (Prospect Theory).

Behavior:
    - Sells winners quickly (gain_threshold ~10%)
    - Holds losers stubbornly (loss_threshold ~30%)

Parameters from config extras:
    - gain_threshold, loss_threshold, loss_aversion
    - sell_fraction_gain, sell_fraction_loss

Theory: simulation-bases.md Section 4.1 -- DispositionInvestor
Theoretical basis: Kahneman & Tversky (1979) Prospect Theory; asymmetric gain/loss treatment with lambda = 2.25.
See simulation-bases.md Section 4.1 for mathematical model.
```
