# MarketCrash / Passive Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MarketCrash |
| Agent type | Passive Investor |
| Canonical class | `PassiveInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: A slow stabilizing allocator that rebalances occasionally. **Theoretical and Empirical Basis**: Long-horizon rebalancing creates delayed demand after price dislocations. **Design Purpose**: Provide weak mean-reverting demand in the Rule baseline. **Behavioral Framework**: Uses rebalance frequency and target position. **Decision Process**: Remain inactive most rounds; on rebalance rounds, trade toward target exposure. **Worked Numerical Example**: If target position is 30 and current position is 20 on a rebalance round, the investor buys part of the 10-share gap. **Academic References**: Gârleanu and Pedersen (2013, DOI: 10.1093/rfs/hhs083); rebalancing literature.

## Financial Theory / Theoretical Basis

### Rule / `PassiveInvestor`
- Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `30.0` | Rule |
| rebalance_frequency | Rule: `20` | Rule |
| target_position | Rule: `30.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | passive_investor | Passive Investor | `PassiveInvestor` | 1 | `examples/MarketCrash/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 PassiveInvestor

**Summary**: A slow stabilizing allocator that rebalances occasionally.
**Theoretical and Empirical Basis**: Long-horizon rebalancing creates delayed
demand after price dislocations.
**Design Purpose**: Provide weak mean-reverting demand in the Rule baseline.
**Behavioral Framework**: Uses rebalance frequency and target position.
**Decision Process**: Remain inactive most rounds; on rebalance rounds, trade
toward target exposure.
**Worked Numerical Example**: If target position is 30 and current position is
20 on a rebalance round, the investor buys part of the 10-share gap.
**Academic References**: Gârleanu and Pedersen (2013, DOI:
10.1093/rfs/hhs083); rebalancing literature.

## Source Docstring Excerpts

### Rule / `PassiveInvestor`

```text
Passive buy-and-hold investor.

Theory: simulation-bases.md Section 4.4.

Parameters from config extras:
    - rebalance_frequency, target_position
```
