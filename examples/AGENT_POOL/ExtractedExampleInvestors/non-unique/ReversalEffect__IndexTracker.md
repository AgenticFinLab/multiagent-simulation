# ReversalEffect / Index Tracker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ReversalEffect |
| Agent type | Index Tracker |
| Canonical class | `IndexTracker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Rebalances toward target exposure. **Theoretical and Empirical Basis**: Passive allocation and benchmark rebalancing. **Design Purpose**: Add slow stabilizing demand in the Rule baseline. **Behavioral Framework**: Uses `target_position` and `rebalance_threshold`. **Decision Process**: Buy or sell when inventory drifts beyond the rebalance band. **Worked Numerical Example**: If current position is materially below target, the agent buys the gap subject to threshold rules. **Academic References**: Index rebalancing and passive-investment literature; Perold and Sharpe (1988).

## Financial Theory / Theoretical Basis

### Rule / `IndexTracker`
- Theory: simulation-bases.md Section 4.6.

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
| rebalance_threshold | Rule: `0.1` | Rule |
| target_position | Rule: `50.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | index_tracker | Index Tracker | `IndexTracker` | 1 | `examples/ReversalEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.6 IndexTracker

**Summary**: Rebalances toward target exposure.
**Theoretical and Empirical Basis**: Passive allocation and benchmark
rebalancing.
**Design Purpose**: Add slow stabilizing demand in the Rule baseline.
**Behavioral Framework**: Uses `target_position` and `rebalance_threshold`.
**Decision Process**: Buy or sell when inventory drifts beyond the rebalance
band.
**Worked Numerical Example**: If current position is materially below target,
the agent buys the gap subject to threshold rules.
**Academic References**: Index rebalancing and passive-investment literature;
Perold and Sharpe (1988).

## Source Docstring Excerpts

### Rule / `IndexTracker`

```text
Passive index tracker for benchmarking.

Theory: simulation-bases.md Section 4.6.

Parameters from config extras:
    - target_position, rebalance_threshold
```
