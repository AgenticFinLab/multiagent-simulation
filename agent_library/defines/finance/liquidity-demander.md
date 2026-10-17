# Liquidity Demander

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Urgent liquidity-seeking agent who accepts price impact to transact immediately |
| Theory Family         | Liquidity Premium / Market Microstructure |
| Behavioral Tendency   | **Demanding** - consumes liquidity by placing large market orders that move prices |
| Time Horizon          | very short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a market participant who must transact immediately regardless of price impact — an institutional investor facing redemptions, a portfolio manager executing a block trade, or a corporate treasurer meeting a cash obligation. The real-world counterpart is documented by Amihud (2002) and Kyle (1985): agents whose urgency means they pay the bid-ask spread and move prices against themselves, creating the liquidity premium that compensates patient market makers.

The decision goal is to execute a required transaction (buy or sell) as quickly as possible, accepting market impact. The agent trades when a liquidity need arises (modeled as a stochastic or threshold-driven event) and accepts whatever price is available. Non-goals: the agent does not minimize market impact, does not split orders, and does not wait for better prices.

## Theoretical Foundation

**Illiquidity premium and price impact**:
- Theory / Study: Illiquidity and stock returns.
- Citation: Amihud, Y. (2002). Illiquidity and stock returns: Cross-section and time-series effects. *Journal of Financial Markets*, 5(1), 31-56. https://doi.org/10.1016/S1386-4181(01)00024-6
- Core Insight: Assets with higher price impact (illiquidity) earn a premium because liquidity demanders must compensate patient suppliers for absorbing their order flow.
- Mathematical Formulation: Amihud's ILLIQ = `|r_t| / Volume_t`. The agent generates the numerator by demanding liquidity.
- Empirical Evidence: Amihud documents a strong positive relationship between illiquidity ratios and expected stock returns.
- Relevance to This Agent: The agent represents the demand side of the liquidity premium, generating price impact that creates the illiquidity measure.
- Calibration Source: `urgency_threshold` 0.3-0.8, `order_size_fraction` 0.05-0.30, `need_probability` 0.05-0.20.
- Falsification Conditions: If the agent splits orders or waits for better prices, the design is falsified.
- Alternative Theories: Optimal execution (Almgren & Chriss 2001) which minimizes impact; patient block trading.

**Kyle lambda and permanent price impact**:
- Citation: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210
- Core Insight: Kyle's lambda measures permanent price impact per unit of order flow; the liquidity demander's trades directly contribute to this impact.

## Design Purpose and Activation Triggers

Purpose: Generate liquidity demand shocks by executing large immediate orders that move prices, creating the price impact that drives the illiquidity premium.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `liquidity_need` available (urgency signal, float 0-1)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `liquidity_need > urgency_threshold` AND `need_direction == "sell"`: sell immediately at market.
- `liquidity_need > urgency_threshold` AND `need_direction == "buy"`: buy immediately at market.
- `<Default>`: hold (no urgency).

Deactivation Conditions:
- liquidity need fully satisfied (required quantity executed).
- no cash for buy or no position for sell.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| High urgency | large immediate order | full size executed without splitting |
| Low urgency | no action | below threshold, no liquidity demand |
| Partial fill available | takes whatever is available | does not wait for full fill |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | execution reference |
| `liquidity_need` | environment | float [0,1] | yes | urgency intensity |
| `need_direction` | environment | enum {buy, sell} | yes | which side needs liquidity |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity is the full demanded amount, clamped only by resource availability.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `liquidity_need` | Continuous | 1 tick | urgency trigger |
| `need_direction` | Categorical | 1 tick | buy vs sell side |
| `cash` | State | persistent | buy constraint |
| `position` | State | persistent | sell constraint |

Does NOT use: order book depth, future price forecasts, fundamental value.

#### Core Behavioral Mechanism

1. Read `liquidity_need` and `need_direction`.
2. If `liquidity_need <= urgency_threshold`, hold.
3. If `need_direction == "buy"`: compute `q = min(cash / price, order_size_fraction * base_demand)`.
4. If `need_direction == "sell"`: compute `q = min(position, order_size_fraction * base_demand)`.
5. Execute immediately as market order (no limit price, no splitting).
6. Emit decision.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order, immediate execution |
| Sizing rule | `order_size_fraction * base_demand`, capped by resources |
| Action lifetime | one decision call |
| Revision policy | new need each tick |
| State constraint | position >= 0, cash >= 0 |
| Resource cap | buy limited by cash/price, sell limited by position |
| Exit rule | none — one-shot execution per need event |

#### Mathematical Model

`q = order_size_fraction * base_demand` when `liquidity_need > urgency_threshold`

Clamped: `q_buy = min(cash / price, q)`, `q_sell = min(position, q)`

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `urgency_threshold` | minimum need to trigger trade | 0.50 | calibration |
| `order_size_fraction` | fraction of base demand per order | 0.15 | Amihud (2002) |
| `base_demand` | base demand in units | 2000.0 | scenario normalization |
| `need_probability` | probability of liquidity need per tick | 0.10 | calibration |

#### Behavioral Properties

- Time horizon: very short, because execution is immediate.
- Risk tolerance: medium, because the agent accepts cost but does not seek risk.
- Information asymmetry: partial, has knowledge of own need but not market depth.
- Psychological profile: urgent, cost-insensitive transactor focused on completion.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `urgency_threshold` | float | 0.50 | [0.30, 0.80] | medium | minimum liquidity_need to trigger execution | Lower -> more frequent demand shocks | calibration |
| `order_size_fraction` | float | 0.15 | [0.05, 0.30] | high | fraction of base_demand executed per event | Higher -> larger price impact | Amihud (2002) |
| `base_demand` | float | 2000.0 | [500, 5000] | high | base demand quantity | Higher -> larger orders | scenario normalization |
| `need_probability` | float | 0.10 | [0.05, 0.20] | medium | probability of liquidity need arising each tick | Higher -> more demand events | calibration |

## Worked Numerical Examples

### Case 1 - Urgent Sell
System state: price 100, liquidity_need 0.75 (> 0.50), need_direction sell, position 5000.
Calculation: `q = 0.15 * 2000 = 300`. Capped: `min(5000, 300) = 300`.
Decision: sell 300.
State update: position decreases by 300.

### Case 2 - Urgent Buy
System state: price 50, liquidity_need 0.90, need_direction buy, cash 100000.
Calculation: `q = 0.15 * 2000 = 300`. Capped: `min(100000/50, 300) = min(2000, 300) = 300`.
Decision: buy 300.
State update: position increases by 300, cash decreases by 15000.

### Case 3 - Hold (Below Threshold)
System state: price 100, liquidity_need 0.30 (< 0.50).
Calculation: urgency below threshold.
Decision: hold.
State update: unchanged.

### Edge Case - Insufficient Inventory
System state: price 100, liquidity_need 0.80, need_direction sell, position 50.
Calculation: `q = min(50, 300) = 50`.
Decision: sell 50 (partial fill, constrained by position).
State update: position goes to zero.

## Behavioral Verification and Calibration

- Given liquidity_need above urgency_threshold, agent must execute immediately in the need_direction.
- Given liquidity_need below threshold, agent must hold.
- Given insufficient resources, agent must execute maximum available (no waiting).
- Agent must never split orders across multiple ticks or use limit prices.
- Given missing liquidity_need signal, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| large-demand | `order_size_fraction = 0.30` | larger orders create more price impact | increase | Amihud ILLIQ ratio |
| rare-needs | `need_probability = 0.02` | fewer demand shocks reduce volatility | decrease | price volatility |
| low-threshold | `urgency_threshold = 0.30` | more frequent demands increase illiquidity | increase | spread, impact |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Amihud, Y. (2002). Illiquidity and stock returns: Cross-section and time-series effects. *Journal of Financial Markets*, 5(1), 31-56. https://doi.org/10.1016/S1386-4181(01)00024-6 | Core illiquidity premium theory |
| 2 | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210 | Price impact (Kyle lambda) |
| 3 | Almgren, R., & Chriss, N. (2001). Optimal execution of portfolio transactions. *Journal of Risk*, 3(2), 5-39. | Alternative: optimal execution (contrast) |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-liquidity-demander.png) |
| Status | draft |
