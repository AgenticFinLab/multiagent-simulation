# ShortSqueeze / Retail Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ShortSqueeze |
| Agent type | Retail Trader |
| Canonical class | `RetailTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Submits noisy demand with a bullish tilt. **Theoretical and Empirical Basis**: Attention-driven buying, social trading, and retail herding from Section 2.3. **Design Purpose**: Add stochastic retail demand that can start or reinforce the squeeze. **Behavioral Framework**: Uses `bullish_bias`, `noise_std`, `min_quantity`, and `max_quantity`. **Decision Process**: Draw a noisy order, add bullish bias, then clamp the quantity to configured bounds. **Worked Numerical Example**: A random draw of +8 combined with `bullish_bias=5` produces a +13 buy order if it remains within quantity caps. **Academic References**: Barber and Odean (2008), DOI: 10.1093/rfs/hhm079.

## Financial Theory / Theoretical Basis

### Rule / `RetailTrader`
- Theory: simulation-bases.md Section 4.3

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| bullish_bias | Rule: `5.0` | Rule |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `0.0` | Rule |
| max_quantity | Rule: `25.0` | Rule |
| min_quantity | Rule: `-15.0` | Rule |
| noise_std | Rule: `12.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | retail | Retail Trader | `RetailTrader` | 3 | `examples/ShortSqueeze/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 RetailTrader

**Summary**: Submits noisy demand with a bullish tilt.
**Theoretical and Empirical Basis**: Attention-driven buying, social trading,
and retail herding from Section 2.3.
**Design Purpose**: Add stochastic retail demand that can start or reinforce the
squeeze.
**Behavioral Framework**: Uses `bullish_bias`, `noise_std`, `min_quantity`, and
`max_quantity`.
**Decision Process**: Draw a noisy order, add bullish bias, then clamp the
quantity to configured bounds.
**Worked Numerical Example**: A random draw of +8 combined with
`bullish_bias=5` produces a +13 buy order if it remains within quantity caps.
**Academic References**: Barber and Odean (2008), DOI: 10.1093/rfs/hhm079.

## Source Docstring Excerpts

### Rule / `RetailTrader`

```text
Retail trader who can trigger squeeze.
Theory: simulation-bases.md Section 4.3

Parameters from config extras:
    - noise_std, bullish_bias, min_quantity, max_quantity
```
