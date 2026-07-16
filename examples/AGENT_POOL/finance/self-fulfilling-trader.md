# Self-fulfilling trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Reflexivity-driven trader whose actions validate beliefs |
| Theory Family         | Macro-Finance / Reflexivity Theory |
| Behavioral Tendency   | **Diverging** - trades aggressively based on directional conviction, creating price pressure that confirms the initial belief |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a large speculator or coordinated trading group whose aggressive positioning creates the very market conditions that validate the original thesis. The real-world counterpart is the reflexive speculator described by Soros (1987) and the self-fulfilling prophecy mechanism formalised by Merton (1948). The agent enters large directional positions when it perceives market vulnerability, with the explicit expectation that its trading impact will move prices toward the predicted level.

The decision goal is to profit from reflexive dynamics by taking large positions early and benefiting from the price movement its own actions help create. It is not a passive price-taker and does not wait for fundamental confirmation. Non-goals: it must not trade without conviction about market vulnerability, and it must not ignore the feedback loop between its actions and price.

## Theoretical Foundation

**Reflexivity in financial markets**:
- Theory / Study: Reflexivity and market instability.
- Citation: Soros, G. (1987). *The Alchemy of Finance*. Simon & Schuster. ISBN: 978-0-471-04313-5.
- Core Insight: Market participants' biased perceptions influence market fundamentals, which in turn reinforce the biased perceptions, creating positive feedback loops. Prices do not passively reflect fundamentals; they actively shape them.
- Mathematical Formulation: `price_next = price + impact_coefficient * own_trade_size + fundamental_drift`. The agent's trade creates impact that moves price toward its predicted target.
- Empirical Evidence: Soros documents reflexive dynamics in currency markets (1992 ERM crisis), equity markets, and credit cycles.
- Relevance to This Agent: The agent explicitly models the feedback loop: large position -> price impact -> belief confirmation -> further positioning.
- Calibration Source: `conviction_threshold` 0.3-0.7, `aggression_multiplier` 2.0-5.0.
- Falsification Conditions: If the agent trades small sizes that cannot generate meaningful market impact, the design is falsified.
- Alternative Theories: Efficient market hypothesis (no feedback); rational expectations equilibrium.

**Self-fulfilling prophecy theorem**:
- Theory / Study: The self-fulfilling prophecy.
- Citation: Merton, R. K. (1948). The self-fulfilling prophecy. *Antioch Review*, 8(2), 193-210. https://doi.org/10.2307/4609267
- Core Insight: A false definition of a situation evokes new behaviour that makes the originally false conception come true. In markets, widespread belief in a price decline can cause the decline through coordinated selling.
- Mathematical Formulation: `belief_strength = initial_conviction + feedback_gain * price_change_in_predicted_direction`.
- Empirical Evidence: Merton documents self-fulfilling bank runs, racial discrimination spirals, and market panics as instances of the theorem.
- Relevance to This Agent: The agent's conviction strengthens as price moves in its predicted direction, leading to further aggressive trading.
- Calibration Source: `feedback_gain` 0.5-2.0.
- Falsification Conditions: If the agent does not increase position size when price moves in the predicted direction, the design is falsified.
- Alternative Theories: Fundamental-only price determination; noise trader models without feedback.

## Design Purpose and Activation Triggers

Purpose: Take large directional positions when market conditions appear vulnerable to reflexive dynamics, profiting from the self-reinforcing price movement the agent's own actions help initiate.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `vulnerability_index` available (composite indicator of market fragility)
- `price_change` available (recent directional movement)
- own `cash` and `position` available
- own `conviction` state (internal belief strength)

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `vulnerability_index > conviction_threshold` AND `conviction > 0` (bullish reflexive attack): buy aggressively, sized by `aggression_multiplier * base_size * conviction`.
- `vulnerability_index > conviction_threshold` AND `conviction < 0` (bearish reflexive attack): sell aggressively, sized by `aggression_multiplier * base_size * |conviction|`.
- Price moves in predicted direction: increase `|conviction|` by `feedback_gain * |price_change|`.
- Price moves against predicted direction beyond `retreat_threshold`: reduce position.
- `<Default>`: hold and monitor.

Deactivation Conditions:
- conviction decays to zero.
- cash or position exhausted.
- price moves against prediction beyond retreat_threshold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| vulnerable market + strong conviction | large aggressive trades | reflexive attack initiation |
| price confirms prediction | increases conviction and position | positive feedback loop |
| price contradicts prediction | reduces conviction and exits | reflexive retreat |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `vulnerability_index` | environment | float | yes | market fragility indicator (0-1) |
| `price_change` | environment | float | yes | recent directional price move |
| `cash` | own state | float | yes | available capital |
| `position` | own state | float | yes | current holdings |
| `conviction` | own state | float | yes | directional belief strength (-1 to +1) |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `vulnerability_index` | Continuous | 1 tick | attack condition |
| `price_change` | Continuous | 1 tick | feedback signal |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell capacity |
| `conviction` | State | persistent | belief strength and direction |

Does NOT use: fundamental valuation, peer consensus, central bank signals.

#### Core Behavioral Mechanism

1. Read `price`, `vulnerability_index`, `price_change`, `cash`, `position`, and `conviction`.
2. Update conviction via feedback: if `sign(price_change) == sign(conviction)`, then `conviction = conviction + feedback_gain * |price_change|`, clamped to [-1, 1].
3. If `sign(price_change) != sign(conviction)` and `|price_change| > retreat_threshold`, then `conviction = conviction * decay_rate`.
4. If `vulnerability_index > conviction_threshold` and `conviction > 0`:
   - `q = min(cash / price, aggression_multiplier * base_size * conviction)`. Buy.
5. If `vulnerability_index > conviction_threshold` and `conviction < 0`:
   - `q = min(position, aggression_multiplier * base_size * |conviction|)`. Sell.
6. If conviction has decayed or vulnerability is low: hold.
7. Emit decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `aggression_multiplier * base_size * |conviction|`, capped by resources |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy quantity cannot exceed `cash / price` |
| Exit rule | retreat when price moves against conviction beyond threshold |

#### Mathematical Model

`q = min(resource_cap, aggression_multiplier * base_size * |conviction|)` when `vulnerability_index > conviction_threshold`; conviction update: `conviction_new = clamp(conviction + feedback_gain * aligned_price_change, -1, 1)`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `conviction_threshold` | vulnerability level to initiate attack | 0.50 | Soros (1987) |
| `aggression_multiplier` | position size multiplier | 3.0 | Soros (1987) |
| `base_size` | base trade size | 500.0 | scenario calibration |
| `feedback_gain` | conviction reinforcement rate | 1.0 | Merton (1948) |
| `retreat_threshold` | adverse price move triggering retreat | 0.03 | risk management |
| `decay_rate` | conviction decay on adverse moves | 0.50 | calibration |

#### Behavioral Properties

- Time horizon: short, because reflexive trades depend on rapid feedback loops.
- Risk tolerance: high, because large positions are essential to generate market impact.
- Information asymmetry: partial, because the agent perceives vulnerability that others may not.
- Psychological profile: aggressive speculator who bets on creating self-reinforcing dynamics.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `conviction_threshold` | float | 0.50 | [0.30, 0.70] | high | vulnerability level needed to initiate position | Lower -> attacks more frequently | Soros (1987) |
| `aggression_multiplier` | float | 3.0 | [2.0, 5.0] | high | multiplier on base_size for position sizing | Higher -> larger market impact | Soros (1987) |
| `base_size` | float | 500.0 | [200, 1000] | medium | base order quantity | Higher -> larger absolute trades | scenario calibration |
| `feedback_gain` | float | 1.0 | [0.5, 2.0] | high | rate of conviction reinforcement from confirming moves | Higher -> faster escalation | Merton (1948) |
| `retreat_threshold` | float | 0.03 | [0.01, 0.05] | medium | adverse price change triggering conviction decay | Lower -> faster retreat | risk management |
| `decay_rate` | float | 0.50 | [0.25, 0.75] | medium | multiplicative decay of conviction on adverse moves | Lower -> faster capitulation | calibration |

## Worked Numerical Examples

### Case 1 - Reflexive Attack Initiation (Bullish)

System state: price 100.0, vulnerability_index 0.65, price_change +0.01, cash 200000, position 100, conviction +0.70.
Calculation: `vulnerability_index (0.65) > conviction_threshold (0.50)` and `conviction > 0`.
Conviction update: `conviction = clamp(0.70 + 1.0 * 0.01, -1, 1) = 0.71`.
`q = min(200000/100, 3.0 * 500 * 0.71) = min(2000, 1065) = 1065`.
Decision: buy 1065.
State update: position increases; cash decreases.

### Case 2 - Feedback Reinforcement

System state: price 103.0, vulnerability_index 0.60, price_change +0.03, cash 100000, position 1100, conviction +0.71.
Calculation: confirming move. `conviction = clamp(0.71 + 1.0 * 0.03, -1, 1) = 0.74`.
`q = min(100000/103, 3.0 * 500 * 0.74) = min(970.9, 1110) = 970`.
Decision: buy 970.
State update: position increases further.

### Case 3 - Adverse Move Retreat

System state: price 96.0, vulnerability_index 0.55, price_change -0.04, cash 50000, position 2000, conviction +0.74.
Calculation: `price_change` opposes conviction. `|price_change| = 0.04 > retreat_threshold (0.03)`.
`conviction = 0.74 * 0.50 = 0.37`. Low conviction with vulnerability still above threshold.
`q = min(2000, 3.0 * 500 * 0.37) = min(2000, 555) = 555`. But agent retreats: sell 555.
Decision: sell 555.
State update: position decreases; conviction reduced.

### Edge Case - Low Vulnerability

System state: price 100.0, vulnerability_index 0.30, price_change 0.0, cash 200000, position 500, conviction +0.80.
Calculation: `vulnerability_index (0.30) < conviction_threshold (0.50)` -> no attack.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given high vulnerability and positive conviction, agent must buy aggressively.
- Given confirming price moves, agent must increase conviction (up to cap).
- Given adverse price moves exceeding retreat threshold, agent must decay conviction and reduce position.
- Given low vulnerability, agent must hold regardless of conviction level.
- Agent must generate orders large enough to plausibly create market impact (minimum aggression_multiplier * base_size * 0.3 units).

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-feedback | `feedback_gain = 0.0` | reflexive reinforcement is essential for self-fulfilling dynamics | decrease | attack success rate |
| low-aggression | `aggression_multiplier = 1.0` | large trades are needed for market impact | decrease | price movement caused |
| no-retreat | `retreat_threshold = 1.0` | retreat prevents catastrophic losses | increase | max drawdown |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Soros, G. (1987). *The Alchemy of Finance*. Simon & Schuster. ISBN: 978-0-471-04313-5. | Reflexivity theory in financial markets |
| 2 | Merton, R. K. (1948). The self-fulfilling prophecy. *Antioch Review*, 8(2), 193-210. https://doi.org/10.2307/4609267 | Self-fulfilling prophecy theorem |
| 3 | Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. https://doi.org/10.1515/9781400865536 | Feedback loops and speculative dynamics |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-self-fulfilling-trader.png) |
| Status | draft |
