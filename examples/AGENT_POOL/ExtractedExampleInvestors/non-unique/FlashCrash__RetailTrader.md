# FlashCrash / Retail Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash |
| Agent type | Retail Trader |
| Canonical class | `RetailTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Role:** Uninformed background participant.

## Financial Theory / Theoretical Basis

### Rule / `RetailTrader`
- Theory: simulation-bases.md Section 4.6 -- RetailTrader
- Theoretical basis: Uninformed noise trading; slow reaction and infrequent

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `0.0` | Rule |
| noise_std | Rule: `8.0` | Rule |
| position_mean_reversion | Rule: `0.1` | Rule |
| trade_frequency | Rule: `5` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | retail_trader | Retail Trader | `RetailTrader` | 2 | `examples/FlashCrash/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.6 RetailTrader

**Role:** Uninformed background participant.

**Behavioural model:**
```python
if round_num % trade_frequency != 0:
    quantity = 0.0          # only trades every trade_frequency rounds
else:
    quantity = gauss(0, noise_std) + (-position_mean_reversion * position)
    quantity = clamp(quantity, -15, 15)
```

**Parameters:** `trade_frequency`, `noise_std`, `position_mean_reversion`

**Decision rule:** Mostly silent; trades at fixed intervals with random direction and a position mean-reversion drag.

**Market effect:** Provides steady low-volume background; prevents market from being trivially one-sided.

**Theory:** Black (1986) -- noise traders.

**Diversity:** Varied `trade_frequency` (1-5 rounds) and `noise_std` (1.0-5.0).

**Distinguishing feature:** Infrequent; adds stochastic volume without directional bias.

## Source Docstring Excerpts

### Rule / `RetailTrader`

```text
Retail trader with slow reaction time.

Theory: simulation-bases.md Section 4.6 -- RetailTrader
Theoretical basis: Uninformed noise trading; slow reaction and infrequent
trading provides background volume without directional crash contribution.
See simulation-bases.md Section 4.6 for mathematical model.

Parameters from config extras:
    - trade_frequency, noise_std, position_mean_reversion
```
