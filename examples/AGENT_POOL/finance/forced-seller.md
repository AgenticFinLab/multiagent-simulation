# Forced seller

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Margin-constrained forced liquidator |
| Theory Family         | Fire Sales / Forced Liquidation Spirals |
| Behavioral Tendency   | **Destabilising** - sells into falling markets due to binding constraints, amplifying price declines |
| Time Horizon          | short |
| Risk Tolerance        | none (involuntary) |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an institutional investor forced to liquidate holdings due to margin calls, regulatory capital requirements, or fund redemptions, regardless of fundamental value. The real-world counterpart is the leveraged fund or bank facing fire-sale pressure documented by Shleifer and Vishny (2011) and Brunnermeier and Pedersen (2009). The agent emits sell or hold orders with quantity determined by the gap between required and actual margin levels.

The decision goal is to sell enough assets to restore the margin ratio above the maintenance requirement. The agent has no choice in timing or price - it must sell when margin is breached, creating pro-cyclical selling that amplifies downturns. Non-goals: it must not buy under any circumstances while margin is breached, and it must not delay liquidation beyond the next tick when the margin call is active.

The agent is designed for scenarios exploring liquidity spirals, fire-sale externalities, and systemic risk where forced selling by one agent depresses prices and triggers margin calls on others.

## Theoretical Foundation

**Fire sales and financial stability**:
- Theory / Study: Fire sales in finance and macroeconomics.
- Citation: Shleifer, A. & Vishny, R. W. (2011). Fire sales in finance and macroeconomics. *Journal of Economic Perspectives*, 25(1), 29-48. https://doi.org/10.1257/jep.25.1.29
- Core Insight: When leveraged institutions face binding constraints, they sell assets at prices below fundamental value. These fire sales depress prices further, potentially triggering margin calls on other institutions and creating a destabilising spiral.
- Mathematical Formulation: `Q_sell = position * (maintenance_margin - current_margin) / maintenance_margin` when `current_margin < maintenance_margin`.
- Empirical Evidence: Shleifer & Vishny document fire-sale discounts of 20-40% during the 2008 financial crisis across multiple asset classes.
- Relevance to This Agent: The agent operationalises the mechanical forced-selling that creates fire-sale externalities.
- Calibration Source: `maintenance_margin` 0.25-0.40, `liquidation_fraction` 0.2-0.5, margin call levels from broker regulations.
- Falsification Conditions: If the agent fails to sell when margin is breached, or buys during a margin call, the design is falsified.
- Alternative Theories: Voluntary deleveraging; margin call with grace period.

**Margin spirals and liquidity**:
- Theory / Study: Market liquidity and funding liquidity.
- Citation: Brunnermeier, M. K. & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098
- Core Insight: Market liquidity and funding liquidity are mutually reinforcing: declining prices reduce collateral values, triggering margin calls that force further selling, which reduces prices further. This creates liquidity spirals.
- Mathematical Formulation: Margin spiral: price drop -> collateral loss -> forced sale -> further price drop.
- Empirical Evidence: Brunnermeier & Pedersen provide theoretical foundations validated by 2007-2009 crisis dynamics.
- Relevance to This Agent: The agent is a single node in the spiral mechanism; multiple instances create cascading liquidation.
- Calibration Source: Leverage ratios 3-10x; initial margin 50%, maintenance 25-40%.
- Falsification Conditions: If the agent's selling does not increase with the severity of the margin breach, design is falsified.
- Alternative Theories: Optimal liquidation (Almgren & Chriss 2001); gradual unwinding.

## Design Purpose and Activation Triggers

Purpose: Mechanically sell assets to restore margin compliance, representing the forced-liquidation node in fire-sale spiral dynamics.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `current_margin` available (equity / position_value)
- own `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `current_margin < maintenance_margin`: sell sized by `liquidation_fraction * position * (maintenance_margin - current_margin) / maintenance_margin`.
- `<Default>`: hold (no margin breach).

Deactivation Conditions:
- margin restored above maintenance level.
- position fully liquidated (no more to sell).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| margin slightly below maintenance | sells moderate fraction | proportional liquidation |
| margin deeply below maintenance | sells large fraction aggressively | emergency liquidation |
| margin above maintenance | holds, no action | constraint not binding |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `current_margin` | derived | float | yes | equity / (position * price) |
| `position` | own state | float | yes | current holdings subject to liquidation |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"sell", "hold"}` | none | yes | order direction (never buys during margin call) |
| `quantity` | float | `>= 0` | units | yes | liquidation size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. The forced seller never buys during a margin breach. Quantity must be clamped to available position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `current_margin` | Continuous | 1 tick | margin call trigger |
| `position` | State | persistent | sell constraint |

Does NOT use: fundamental value, sentiment, peer positions, forecasts.

#### Core Behavioral Mechanism

1. Read `price`, `current_margin`, and `position`.
2. If `current_margin < maintenance_margin` and `position > 0`, compute sell quantity as `liquidation_fraction * position * (maintenance_margin - current_margin) / maintenance_margin`.
3. Clamp sell quantity to available position.
4. If margin is above maintenance or position is zero, hold.
5. Emit the decision object and update position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, hold (never buys during margin breach) |
| Action parameter rule | market order at current price (fire-sale, price-insensitive) |
| Sizing rule | `liquidation_fraction * position * margin_deficit / maintenance_margin` |
| Action lifetime | one decision call |
| Revision policy | recalculate each tick until margin restored |
| State constraint | position cannot fall below zero |
| Resource cap | sell cannot exceed current position |
| Exit rule | stop selling when margin >= maintenance_margin |

#### Mathematical Model

`q_sell = min(position, liquidation_fraction * position * (M - m) / M)` if `m < M`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `M` | maintenance margin requirement | 0.30 | broker/regulatory standard |
| `liquidation_fraction` | aggressiveness of liquidation | 0.35 | Shleifer & Vishny (2011) |
| `min_sell` | minimum liquidation per tick | 100.0 | operational floor |
| `position_floor` | minimum position below which full liquidation occurs | 50.0 | operational constraint |

#### Behavioral Properties

- Time horizon: short, because forced liquidation is immediate and non-discretionary.
- Risk tolerance: none (involuntary), because the agent has no choice in selling.
- Information asymmetry: none, because the agent acts solely on its own margin state.
- Psychological profile: constrained institution with no agency over timing or price.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `maintenance_margin` | float | 0.30 | [0.25, 0.40] | high | margin level below which forced selling begins | Lower -> later trigger, bigger eventual sell | broker regulations |
| `liquidation_fraction` | float | 0.35 | [0.2, 0.5] | high | fraction of deficit to liquidate per tick | Higher -> faster liquidation, more market impact | Shleifer & Vishny (2011) |
| `min_sell` | float | 100.0 | [50, 300] | low | minimum units sold per liquidation tick | Ensures progress toward margin restoration | operational |
| `position_floor` | float | 50.0 | [10, 100] | low | below this position, sell all remaining | Prevents dust positions | operational |

## Worked Numerical Examples

### Case 1 - Moderate Margin Breach
System state: price 80.0, current_margin 0.22, maintenance_margin 0.30, position 5000.
Calculation: margin deficit = (0.30 - 0.22) / 0.30 = 0.267. `q = 0.35 * 5000 * 0.267 = 467`.
Decision: sell 467.
State update: position decreases to 4533.

### Case 2 - Severe Margin Breach
System state: price 60.0, current_margin 0.10, maintenance_margin 0.30, position 5000.
Calculation: margin deficit = (0.30 - 0.10) / 0.30 = 0.667. `q = 0.35 * 5000 * 0.667 = 1167`.
Decision: sell 1167.
State update: position decreases to 3833.

### Case 3 - No Margin Breach
System state: price 100.0, current_margin 0.45, maintenance_margin 0.30, position 5000.
Calculation: current_margin (0.45) > maintenance (0.30). No breach.
Decision: hold.
State update: unchanged.

### Edge Case - Near-Zero Position
System state: price 50.0, current_margin 0.15, maintenance_margin 0.30, position 30 (below position_floor 50).
Calculation: position (30) < position_floor (50). Sell all remaining.
Decision: sell 30.
State update: position reaches zero; agent fully liquidated.

## Behavioral Verification and Calibration

- Given `current_margin < maintenance_margin` and positive position, agent must sell.
- Given `current_margin >= maintenance_margin`, agent must hold.
- Agent must never buy while margin is below maintenance.
- Sell quantity must increase with the severity of the margin breach.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-forced-selling | `maintenance_margin = 0` | forced sales amplify downturns | decrease | max drawdown |
| aggressive-liquidation | `liquidation_fraction = 0.5` | faster liquidation increases crash depth | increase | price impact per tick |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Shleifer, A. & Vishny, R. W. (2011). Fire sales in finance and macroeconomics. https://doi.org/10.1257/jep.25.1.29 | Fire-sale theory and externalities |
| 2 | Brunnermeier, M. K. & Pedersen, L. H. (2009). Market liquidity and funding liquidity. https://doi.org/10.1093/rfs/hhn098 | Liquidity spiral mechanism |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-forced-seller.png) |
| Status | draft |
