# MomentumEffect / Index Fund

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | MomentumEffect |
| Agent type | Index Fund |
| Canonical class | `IndexFund` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Summary**: Maintains a target equity allocation. **Theoretical and Empirical Basis**: Passive portfolio rebalancing. **Design Purpose**: Add slow baseline flow that is not trend-seeking. **Behavioral Framework**: Rule uses `target_allocation=0.6` and `rebalance_threshold=0.05`. **Decision Process**: Rebalance gradually when portfolio allocation drifts too far from target. **Worked Numerical Example**: If equity allocation falls below target by more than 5%, the fund buys part of the gap. **Academic References**: Portfolio rebalancing and constant-mix allocation literature; Perold and Sharpe (1988).

## Financial Theory / Theoretical Basis

### Rule / `IndexFund`
- Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `_hold_order`, `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `0.0` | Rule |
| rebalance_threshold | Rule: `0.05` | Rule |
| target_allocation | Rule: `0.6` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | index_fund | Index Fund | `IndexFund` | 1 | `examples/MomentumEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 IndexFund

**Summary**: Maintains a target equity allocation.  
**Theoretical and Empirical Basis**: Passive portfolio rebalancing.  
**Design Purpose**: Add slow baseline flow that is not trend-seeking.  
**Behavioral Framework**: Rule uses `target_allocation=0.6` and
`rebalance_threshold=0.05`.  
**Decision Process**: Rebalance gradually when portfolio allocation drifts too
far from target.  
**Worked Numerical Example**: If equity allocation falls below target by more
than 5%, the fund buys part of the gap.  
**Academic References**: Portfolio rebalancing and constant-mix allocation
literature; Perold and Sharpe (1988).

## Source Docstring Excerpts

### Rule / `IndexFund`

```text
Passive Index Fund:
    Maintains fixed allocation regardless of momentum
    Serves as baseline for performance comparison

Theory: simulation-bases.md Section 4.3.

Parameters from config extras:
    - target_allocation, rebalance_threshold
```
