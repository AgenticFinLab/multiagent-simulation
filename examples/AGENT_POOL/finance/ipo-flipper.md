# IPO flipper

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Short-term IPO allocation flipper |
| Theory Family         | IPO Underpricing / Initial Returns |
| Behavioral Tendency   | **Neutral** - buys at IPO allocation and sells quickly into opening-day demand, capturing the underpricing spread |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a short-term trader who acquires shares in initial public offerings at the offer price and sells them quickly (within ticks representing the first trading day) to capture the well-documented IPO "pop" - the average first-day return. The real-world counterpart is the institutional or retail flipper documented by Ritter (1991) and Ljungqvist (2007). The agent emits buy or sell orders with timing driven by the IPO event and exit triggered by a target return or time limit.

The decision goal is to buy at the IPO offer price and sell into initial demand, capturing the first-day underpricing premium. The agent does not hold for long-term value; it treats IPOs as a short-term spread trade. Non-goals: it must not hold IPO shares beyond the flip window, and it must not buy IPO shares after the initial allocation period (i.e., it does not chase in the secondary market).

The agent is designed for scenarios exploring IPO market dynamics, underpricing puzzles, flipping behaviour, and how institutional allocation practices affect secondary market price discovery.

## Theoretical Foundation

**IPO underpricing**:
- Theory / Study: The long-run performance of initial public offerings.
- Citation: Ritter, J. R. (1991). The long-run performance of initial public offerings. *Journal of Finance*, 46(1), 3-27. https://doi.org/10.1111/j.1540-6261.1991.tb03743.x
- Core Insight: IPOs are systematically underpriced on average by 10-20%, creating a reliable first-day return for those who receive allocations. This return compensates for winner's curse and information asymmetry between issuers and informed investors.
- Mathematical Formulation: `expected_return = (first_day_price - offer_price) / offer_price`, averaging 10-20%.
- Empirical Evidence: Ritter documents average first-day returns of 16% across thousands of US IPOs from 1975-1984, consistent across eras.
- Relevance to This Agent: The agent exploits this systematic underpricing by buying at offer price and selling into first-day demand.
- Calibration Source: `flip_target_return` 0.05-0.20, `max_hold_ticks` 1-5, `allocation_size` 200-1000.
- Falsification Conditions: If the agent holds beyond the flip window or buys in secondary market, the design is falsified.
- Alternative Theories: Signalling theories of underpricing (Allen & Faulhaber 1989); litigation avoidance.

**IPO allocation and flipping**:
- Theory / Study: IPO underpricing: A survey.
- Citation: Ljungqvist, A. (2007). IPO underpricing. In B. E. Eckbo (Ed.), *Handbook of Empirical Corporate Finance* (pp. 375-422). Elsevier. https://doi.org/10.1016/B978-0-444-53265-7.50021-4
- Core Insight: Underwriters penalise flippers by reducing future allocations, yet flipping remains profitable because the immediate return exceeds the expected value of future allocations for many investors. Flipping concentrates in hot IPOs.
- Mathematical Formulation: Flip decision: sell if `current_return >= flip_target` or `ticks_held >= max_hold_ticks`.
- Empirical Evidence: Ljungqvist surveys multiple mechanisms explaining persistence of underpricing and documents flipper behaviour.
- Relevance to This Agent: Calibrates the agent's exit timing and target return parameters.
- Calibration Source: Hot IPO flipping rates of 20-70% of allocations sold on day 1.
- Falsification Conditions: If the agent does not sell within the flip window, design is falsified.
- Alternative Theories: Sentiment-driven IPO pricing; prospect theory reference points.

## Design Purpose and Activation Triggers

Purpose: Buy IPO allocations at offer price and sell within a short window to capture underpricing returns.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available (current secondary market price)
- `offer_price` available (IPO allocation price)
- `ipo_active` flag (whether currently in IPO flip window)
- `ticks_since_ipo` available (time elapsed since allocation)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `ipo_active = true` and `position = 0` and `ticks_since_ipo = 0`: buy at offer_price sized by `allocation_size`.
- `ipo_active = true` and `position > 0` and `(price - offer_price) / offer_price >= flip_target_return`: sell all position (target met).
- `ipo_active = true` and `position > 0` and `ticks_since_ipo >= max_hold_ticks`: sell all position (time limit exit).
- `<Default>`: hold.

Deactivation Conditions:
- position fully sold (flip complete).
- IPO window expires.
- no IPO event active.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| IPO allocation available | buys at offer price | allocation acquisition |
| target return reached | sells entire position | profit-taking flip |
| time limit reached without target | sells entire position | disciplined time-based exit |

Environmental Dependencies: IPO event scheduling from simulation environment.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current secondary market price |
| `offer_price` | environment | float | yes | IPO allocation price |
| `ipo_active` | environment | bool | yes | whether IPO flip window is open |
| `ticks_since_ipo` | environment | int | yes | ticks elapsed since allocation |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | current IPO shares held |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash (for buy) or position (for sell).

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | exit decision and P&L calculation |
| `offer_price` | Continuous | persistent (set at IPO) | cost basis for return calculation |
| `ipo_active` | Discrete | 1 tick | window eligibility |
| `ticks_since_ipo` | Counter | persistent | time-limit exit |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell constraint |

Does NOT use: fundamental valuation, long-term forecasts, peer positioning, market sentiment.

#### Core Behavioral Mechanism

1. Read `price`, `offer_price`, `ipo_active`, `ticks_since_ipo`, `cash`, and `position`.
2. If `ipo_active = false`, hold.
3. If `ipo_active = true` and `position = 0` and `ticks_since_ipo = 0`, buy `min(cash / offer_price, allocation_size)`.
4. If `position > 0`, compute `current_return = (price - offer_price) / offer_price`.
5. If `current_return >= flip_target_return` or `ticks_since_ipo >= max_hold_ticks`, sell all position.
6. Otherwise, hold (waiting for target or time limit).
7. Emit the decision object and update cash/position after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | buy at offer_price; sell at market price |
| Sizing rule | buy: `allocation_size`; sell: entire position |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero; only one IPO allocation per event |
| Resource cap | buy cannot exceed cash / offer_price |
| Exit rule | sell all when target return met or time limit reached |

#### Mathematical Model

`q_buy = min(cash / P_offer, allocation_size)` at `t = 0`; `q_sell = position` if `(P - P_offer)/P_offer >= R` or `t >= T_max`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `R` | flip target return | 0.10 | Ritter (1991) |
| `T_max` | maximum hold ticks before forced exit | 3 | Ljungqvist (2007) |
| `allocation_size` | IPO shares allocated | 500.0 | scenario normalization |
| `stop_loss` | return at which to exit at a loss | -0.05 | risk management |

#### Behavioral Properties

- Time horizon: short, because the agent flips within one trading day (a few ticks).
- Risk tolerance: medium, because IPO flipping has limited downside due to underpricing but carries some first-day reversal risk.
- Information asymmetry: partial, because IPO allocations are preferentially given to informed/institutional investors.
- Psychological profile: opportunistic, disciplined, mechanical profit-taker with no attachment to holdings.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `flip_target_return` | float | 0.10 | [0.05, 0.20] | high | return threshold triggering sell | Lower -> faster flip, less per-trade profit | Ritter (1991) |
| `max_hold_ticks` | int | 3 | [1, 5] | high | maximum ticks before forced exit | Lower -> more disciplined, less exposure | Ljungqvist (2007) |
| `allocation_size` | float | 500.0 | [200, 1000] | medium | shares acquired at IPO offer price | Higher -> more first-day selling pressure | scenario normalization |
| `stop_loss` | float | -0.05 | [-0.10, -0.02] | medium | loss threshold for early exit | More negative -> more loss tolerance | risk management |

## Worked Numerical Examples

### Case 1 - IPO Allocation Buy
System state: ipo_active true, ticks_since_ipo 0, offer_price 20.0, cash 100000, position 0, allocation_size 500.
Calculation: IPO active, no position, tick 0. `q = min(100000/20, 500) = min(5000, 500) = 500`.
Decision: buy 500.
State update: position increases to 500; cash decreases by 10000.

### Case 2 - Target Return Flip
System state: ipo_active true, ticks_since_ipo 1, price 22.5, offer_price 20.0, position 500, flip_target_return 0.10.
Calculation: current_return = (22.5 - 20) / 20 = 0.125 >= 0.10. Target met. `q = 500`.
Decision: sell 500.
State update: position decreases to 0; cash increases by 11250; profit = 1250.

### Case 3 - Time Limit Exit
System state: ipo_active true, ticks_since_ipo 3, price 21.0, offer_price 20.0, position 500, max_hold_ticks 3.
Calculation: ticks (3) >= max_hold (3). Time limit reached. current_return = 0.05 (below target but positive). `q = 500`.
Decision: sell 500.
State update: position decreases to 0; cash increases by 10500; profit = 500.

### Edge Case - IPO Drops (Stop Loss)
System state: ipo_active true, ticks_since_ipo 1, price 18.5, offer_price 20.0, position 500, stop_loss -0.05.
Calculation: current_return = (18.5 - 20) / 20 = -0.075 < -0.05 (stop loss triggered). `q = 500`.
Decision: sell 500.
State update: position decreases to 0; cash increases by 9250; loss = -750.

## Behavioral Verification and Calibration

- Given IPO active and tick 0, agent must buy allocation if cash permits.
- Given target return met, agent must sell entire position immediately.
- Given max_hold_ticks reached, agent must sell regardless of return.
- Agent must never buy IPO shares after initial allocation tick.
- Agent must never hold beyond max_hold_ticks.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-flip-pressure | `allocation_size = 0` | flippers create first-day selling pressure | decrease | first-day volume |
| patient-holder | `max_hold_ticks = 20` | quick flipping reduces long-run returns | increase | holding period return |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Ritter, J. R. (1991). The long-run performance of initial public offerings. https://doi.org/10.1111/j.1540-6261.1991.tb03743.x | IPO underpricing documentation |
| 2 | Ljungqvist, A. (2007). IPO underpricing. https://doi.org/10.1016/B978-0-444-53265-7.50021-4 | Comprehensive IPO survey and flipper behaviour |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-ipo-flipper.png) |
| Status | draft |
