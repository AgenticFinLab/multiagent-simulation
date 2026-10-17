# Commitment Escalator

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Commitment Escalator                                                                                                 |
| Theory Family         | Sunk Cost Fallacy — Escalation of Commitment — Loss Aversion                                                         |
| Behavioral Tendency   | **Diverging** — doubles down on losing positions, amplifying losses by throwing good money after bad                  |
| Time Horizon          | Medium-Long (escalates commitment over multiple rounds; reluctant to exit)                                           |
| Risk Tolerance        | High (increases exposure precisely when risk is highest — during losses)                                             |
| Information Asymmetry | None (observes same signals as others but misweights sunk costs)                                                     |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The commitment escalator models investors who increase their investment in a losing position because they have already committed substantial resources and feel psychologically compelled to "justify" their prior decisions. This is the classic sunk cost fallacy applied to financial markets — the investor who averages down repeatedly, the venture capitalist who provides follow-on funding to a failing startup to protect earlier rounds, or the trader who doubles position size after a loss. In real-world markets, these correspond to retail investors averaging down on losing stock picks, venture capitalists escalating commitment to failing portfolio companies, corporate managers continuing failed projects to justify prior budgets, day traders doubling position sizes after losses (martingale behaviour), pension fund trustees maintaining allocation to underperforming managers, and governments continuing cost-overrun infrastructure projects.

The agent's decision goal is to BUY ONLY — it escalates commitment when prices fall below fundamental (treating the loss as a reason to invest more) and adds modestly when prices rise (interpreting gains as validation). The quantity formula differs by direction: on losses (dev < -threshold), `Q = escalation_size * |deviation| / escalation_threshold`; on gains (dev > threshold), `Q = escalation_size * 0.5 * deviation / escalation_threshold`. The agent never sells.

The agent's behavioural role inside the simulation is to destabilise by concentrating capital in losing positions — it withdraws liquidity from the sell side and adds demand precisely when fundamental signals suggest reducing exposure. Non-goals: (1) the commitment escalator MUST NOT sell — it never cuts losses; (2) the commitment escalator MUST NOT respond rationally to negative signals by reducing exposure.

## Theoretical Foundation

**Escalation of Commitment (Staw 1976; Staw & Hoang 1995)**:
- Theory / Study: Knee-Deep in the Big Muddy: A Study of Escalating Commitment to a Chosen Course of Action
- Citation: Staw, B. M. (1976). Knee-deep in the big muddy: A study of escalating commitment to a chosen course of action. *Organizational Behavior and Human Performance*, 16(1), 27–44. https://doi.org/10.1016/0030-5073(76)90005-2; Staw, B. M. & Hoang, H. (1995). Sunk costs in the NBA: Why draft order affects playing time and survival in professional basketball. *Administrative Science Quarterly*, 40(3), 474–494. https://doi.org/10.2307/2393794
- Core Insight: Decision makers who have invested heavily in a course of action escalate their commitment when receiving negative feedback, rather than rationally cutting losses. This occurs because: (a) admitting failure threatens self-image; (b) sunk costs are irrationally included in forward-looking decisions; (c) the decision maker believes additional investment will "turn things around." In financial markets, this manifests as averaging down on losing positions, providing follow-on capital to failing ventures, and refusing to sell at a loss.
- Mathematical Formulation: `if deviation < -escalation_threshold: quantity = escalation_size * |deviation| / escalation_threshold [BUY MORE into loss]; if deviation > escalation_threshold: quantity = escalation_size * 0.5 * deviation / escalation_threshold [modest addition on gain]`
- Empirical Evidence: Staw (1976) shows that participants who made initial investment decisions allocated 25% more additional funding to failing projects compared to those who inherited the decision (Table 2, p. 35, F(1,238) = 4.82, p < 0.05). Staw & Hoang (1995) show that NBA teams gave 23% more playing time to high draft picks regardless of performance, demonstrating sunk cost effects in professional contexts (Table 3, p. 483).
- Relevance to This Agent: The agent operationalises escalation through BUY-ONLY behaviour with asymmetric sizing: full-strength buying on losses (escalation) vs. half-strength buying on gains (modest validation). The inability to sell represents the psychological impossibility of admitting the loss was a mistake.
- Calibration Source: `escalation_threshold` = 0.05 from Staw (1976) — escalation behaviour is triggered by losses exceeding ~5% of initial commitment; `escalation_size` = 400 from simulation scaling to produce meaningful position growth during escalation episodes.
- Falsification Conditions: If this agent sells at any point, the escalation mechanism is falsified (it must NEVER cut losses). If the agent's buy quantity during losses is less than during gains, the asymmetric escalation pattern is broken.
- Alternative Theories: Rational averaging down (value investors buying more at lower prices); prospect theory (Kahneman & Tversky 1979) provides a complementary explanation through loss aversion making realised losses psychologically painful.

## Design Purpose and Activation Triggers

Purpose: Demonstrate sunk cost escalation by increasing position size during losses and modestly adding during gains, never selling, thereby concentrating capital in potentially failing positions.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Negative deviation exceeds threshold (deviation < -0.05): BUY MORE — escalate commitment into loss
- Positive deviation exceeds threshold (deviation > 0.05): BUY modestly — validate prior commitment
- Default (|deviation| <= 0.05): HOLD — insufficient signal to trigger further commitment

Deactivation Conditions:
- Cash exhaustion: Cannot buy further (the only practical limit on escalation)
- Deviation remains within threshold for extended period: Agent holds

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                         | Mechanism                                                |
|------------------------------|-----------------------------------------------------------|----------------------------------------------------------|
| Price falling (loss regime)  | Aggressive buying — full escalation_size scaling          | Loss triggers escalation: Q = escalation_size * |dev|/thresh |
| Price rising (gain regime)   | Modest buying — half escalation_size scaling              | Gain validates but doesn't trigger full escalation       |
| Extreme loss (dev < -0.20)   | Very large buy orders — deepening commitment             | Linear scaling continues with larger deviation            |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental_value` fields. No peer-action summaries, order-book data, or social signals needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source                     | Type / Shape | Required? | Notes                                              |
|------------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`                | Market coordinator payload | `float`      | yes       | Current asset market price                         |
| `fundamental_value`    | Environment / scenario     | `float`      | yes       | True or estimated fundamental value of the asset   |
| `position`             | Agent persisted state      | `float`      | yes       | Current holdings (shares)                          |
| `cash`                 | Agent persisted state      | `float`      | yes       | Current cash balance                               |
| `round`                | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `agent_id`             | Scheduler / round header   | `str`        | yes       | Agent identity string                              |
| `retrieved_knowledge`  | Retrieval store            | `list[str]`  | RAG only  | Falls back to sentinel if empty                    |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                            |
|-------------|--------|---------------------------|--------|-----------|----------------------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`         | —      | yes       | BUY or HOLD only — never sells                     |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if buying, 0.0 if hold                |
| `quantity`  | float  | [0, 1600]                 | shares | yes       | Unsigned order size (escalation-driven)             |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Escalation rationale, loss/gain context            |

##### Content Constraints

- All four output fields MUST be present on every call.
- `action` MUST be either "buy" or "hold" — "sell" is NEVER emitted.
- `price` MUST equal the current market price when buying; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- Loss-regime quantity is 2x gain-regime quantity for the same |deviation|.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); escalation_threshold = {escalation_threshold}; regime = {'loss-escalation' if deviation < 0 else 'gain-validation'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|hold>", "price": <float>, "quantity": <float>, "reasoning": "Commitment-escalator: deviation {deviation:.2%}, {'escalating into loss' if deviation < 0 else 'validating gain'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the escalation formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST NEVER output "sell" — only "buy" or "hold". Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and BUY-ONLY constraint. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                       |
|---------------------|------------|---------------|-----------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation from fundamental               |
| `fundamental_value` | Continuous | Current tick  | Reference value for determining loss vs gain regime             |
| `cash`              | Continuous | Persisted     | Determines whether additional buying is feasible                |

Does NOT use: position history (does not track total sunk cost explicitly), peer positions, order book depth, sell signals, momentum indicators — the escalator ignores exit signals by design.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Escalation of Commitment — Staw 1976)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: deviation determines loss vs gain regime for escalation behaviour)

Step 3 — Evaluate activation threshold:
  Read: `escalation_threshold`
  IF `|deviation| <= escalation_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: implementation convenience — minimum deviation to trigger commitment response)

Step 4 — Determine escalation regime and compute quantity:
  Read: `escalation_size`
  IF `deviation < -escalation_threshold` (LOSS regime):
    action = "buy"
    `quantity = escalation_size * |deviation| / escalation_threshold`
    (Theory trace: Staw 1976 — negative feedback triggers INCREASED commitment)
  ELIF `deviation > escalation_threshold` (GAIN regime):
    action = "buy"
    `quantity = escalation_size * 0.5 * deviation / escalation_threshold`
    (Theory trace: gain validates prior commitment but at half intensity)

Step 5 — Apply resource constraints:
  Read: `cash`
  IF quantity * price > cash: `quantity = floor(cash / price)`
  Write: final `quantity`
  (Implementation convenience — no theoretical claim)

Step 6 — Execute trade and update state:
  IF action == "buy": Write: `cash -= quantity * price`; `position += quantity`
  (Implementation convenience — state bookkeeping; note: NO sell path exists)

#### Action Space

| Aspect                | Specification                                                                                          |
|-----------------------|--------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold` (NEVER `sell` — the agent cannot cut losses)                                             |
| Action parameter rule | `price` = current market price (price-taker; no limit orders)                                          |
| Sizing rule           | Loss: `Q = escalation_size * |dev| / threshold`; Gain: `Q = escalation_size * 0.5 * dev / threshold`  |
| Action lifetime       | Immediate execution; no persistent resting orders                                                      |
| Revision policy       | No revision — each round's order is independent                                                        |
| State constraint      | Position grows monotonically (never decreases; buy-only behaviour)                                     |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                                              |
| Exit rule             | None — agent accumulates position until cash is exhausted                                              |

#### Mathematical Model

**Decision output:** Unsigned quantity (float, no hard cap beyond resource limits) plus action (buy/hold enum only).

**Decision logic formalization:**

```
Given: price, fundamental_value, escalation_threshold, escalation_size

Step 1 — Compute deviation:
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate:
  IF abs(deviation) <= escalation_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Escalation regime:
  IF deviation < -escalation_threshold:
    action = "buy"
    quantity = escalation_size * abs(deviation) / escalation_threshold
  ELIF deviation > escalation_threshold:
    action = "buy"
    quantity = escalation_size * 0.5 * deviation / escalation_threshold

Step 4 — Resource constraint:
  quantity = min(quantity, floor(cash / price))

Step 5 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
```

**State variables:**
- `position`: float, initial value = 0. Net shares held (monotonically increasing).
- `cash`: float, initial value = 10000.0. Available capital (monotonically decreasing when active).

**State evolution:**
- `position`: Updated post-decide (increases on every buy, never decreases).
- `cash`: Updated post-decide (decreases on every buy, never increases).

**Determinism contract:** Fully deterministic given identical price, fundamental_value, cash, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol                 | Meaning                                     | Default Value | Source                     |
|------------------------|---------------------------------------------|---------------|----------------------------|
| `escalation_threshold` | Minimum |deviation| to trigger commitment  | 0.05          | Staw (1976)                |
| `escalation_size`      | Base multiplier for quantity                | 400           | Simulation design          |

#### Behavioral Properties

- **Time horizon:** Medium-Long (escalates commitment over multiple rounds; position grows until cash exhausted)
- **Risk tolerance:** High (increases exposure during losses — precisely when risk is highest; classic anti-rational behaviour)
- **Information asymmetry:** None (observes same fundamental value signal; misuses it by treating losses as reasons to buy more)
- **Psychological profile:** Sunk cost biased — exhibits escalation of commitment (Staw 1976), self-justification motivation, loss aversion that prevents selling, and cognitive dissonance reduction through doubling down

## Parameters

| Parameter              | Type  | Default | Valid Range   | Sensitivity | Description                                                  | Impact                                                   | Source                     |
|------------------------|-------|---------|---------------|-------------|--------------------------------------------------------------|----------------------------------------------------------|----------------------------|
| `escalation_threshold` | float | 0.05    | [0.02, 0.15]  | High        | Minimum absolute deviation to trigger escalation response    | Higher → fewer escalation events, slower capital depletion | Staw (1976)               |
| `escalation_size`      | float | 400     | [100, 1000]   | High        | Base multiplier for escalation quantity                       | Higher → faster capital concentration in losing positions | Simulation design          |
| `initial_cash`         | float | 10000.0 | [5000, 50000] | Medium      | Starting cash endowment (limits total escalation capacity)   | Higher → more rounds of escalation before exhaustion     | Normalisation              |
| `initial_position`     | float | 0.0     | [0, 100]      | Low         | Starting inventory of shares                                  | Non-zero → agent already has sunk cost at start          | Normalisation              |

## Worked Numerical Examples

### Case 1 — Loss regime (escalate — buy more into falling price)

System state: `price` = 135.0, `fundamental_value` = 150.0, `escalation_threshold` = 0.05, `escalation_size` = 400, `cash` = 10000.0, `position` = 20.0

Calculation:
- `deviation` = (135.0 - 150.0) / 150.0 = -0.10
- Threshold check: |-0.10| > 0.05? YES → active
- Regime: deviation < -0.05 → LOSS escalation
- `quantity` = 400 * 0.10 / 0.05 = 800
- Resource check: 800 * 135.0 = 108000 > 10000 → `quantity` = floor(10000 / 135.0) = 74

Decision: buy 74 shares at price = 135.0
State update: `cash`: 10000.0 → 10.0; `position`: 20.0 → 94.0

### Case 2 — Gain regime (validate — modest additional buy)

System state: `price` = 165.0, `fundamental_value` = 150.0, `escalation_threshold` = 0.05, `escalation_size` = 400, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (165.0 - 150.0) / 150.0 = 0.10
- Threshold check: |0.10| > 0.05? YES → active
- Regime: deviation > 0.05 → GAIN validation
- `quantity` = 400 * 0.5 * 0.10 / 0.05 = 400
- Resource check: 400 * 165.0 = 66000 > 10000 → `quantity` = floor(10000 / 165.0) = 60

Decision: buy 60 shares at price = 165.0
State update: `cash`: 10000.0 → 100.0; `position`: 50.0 → 110.0

### Case 3 — Small deviation (hold — no escalation trigger)

System state: `price` = 152.0, `fundamental_value` = 150.0, `escalation_threshold` = 0.05

Calculation:
- `deviation` = (152.0 - 150.0) / 150.0 = 0.0133
- Threshold check: |0.0133| > 0.05? NO → hold

Decision: hold
State update: No change

### Edge Case — Cash exhausted (cannot escalate further)

System state: `price` = 120.0, `fundamental_value` = 150.0, `escalation_threshold` = 0.05, `escalation_size` = 400, `cash` = 50.0, `position` = 200.0

Calculation:
- `deviation` = (120.0 - 150.0) / 150.0 = -0.20
- Threshold check: |-0.20| > 0.05? YES → active
- Regime: LOSS escalation
- `quantity` = 400 * 0.20 / 0.05 = 1600
- Resource check: 1600 * 120.0 = 192000 > 50 → `quantity` = floor(50 / 120.0) = 0

Decision: hold (effectively deactivated — cash exhausted, cannot escalate further)
State update: No change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `escalation_threshold` = 0.05 <- Staw (1976) Table 2, escalation behaviour triggered by 5%+ losses relative to initial investment
- `escalation_size` = 400 <- Scaled to produce meaningful escalation (400–1600 units) that depletes capital over 5–15 rounds in typical loss scenarios

**Expected individual behaviour:**
- Given deviation = -0.10 (loss), agent MUST buy with Q = 400 * 0.10 / 0.05 = 800 (subject to cash)
- Given deviation = +0.10 (gain), agent MUST buy with Q = 400 * 0.5 * 0.10 / 0.05 = 400 (subject to cash)
- Agent MUST NEVER emit action = "sell" under any circumstances
- Loss-regime quantity MUST be exactly 2x gain-regime quantity for same |deviation|

**Sanity bounds (red flags indicating broken implementation):**
- IF agent emits action = "sell" THEN broken (BUY-ONLY constraint violated)
- IF agent trades when |deviation| <= 0.05 THEN broken (threshold gate failed)
- IF agent's loss-regime quantity < gain-regime quantity for same |deviation| THEN broken (escalation asymmetry inverted)
- IF agent's position ever decreases THEN broken (monotonically increasing position required)

### Ablation Hooks

| Ablation name         | Setting                        | Hypothesis tested                                         | Expected direction          | Metric                             |
|-----------------------|--------------------------------|-----------------------------------------------------------|-----------------------------|-------------------------------------|
| `no_escalator`        | population = 0                 | Removing escalators reduces capital trapped in losers     | Faster price correction     | Rounds to correct 20% mispricing   |
| `low_escalation`      | `escalation_size=100`          | Smaller escalation reduces destabilising effect           | Less capital concentration  | Final position after 30 rounds     |
| `high_threshold`      | `escalation_threshold=0.15`    | Higher threshold reduces escalation frequency             | More cash preserved         | Cash remaining after 30 rounds     |
| `symmetric`           | Gain multiplier = 1.0 (not 0.5)| Removing asymmetry tests whether loss-specific escalation matters | Different capital profile | Loss-regime vs gain-regime volume  |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Staw, B. M. (1976). Knee-deep in the big muddy: A study of escalating commitment to a chosen course of action. *Organizational Behavior and Human Performance*, 16(1), 27–44. https://doi.org/10.1016/0030-5073(76)90005-2 | Primary theory source; escalation mechanism |
| 2 | Staw, B. M. & Hoang, H. (1995). Sunk costs in the NBA: Why draft order affects playing time and survival in professional basketball. *Administrative Science Quarterly*, 40(3), 474–494. https://doi.org/10.2307/2393794 | Empirical evidence of sunk cost effects |
| 3 | Kahneman, D. & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185 | Complementary theory — loss aversion |
| 4 | Thaler, R. H. (1980). Toward a positive theory of consumer choice. *Journal of Economic Behavior & Organization*, 1(1), 39–60. https://doi.org/10.1016/0167-2681(80)90051-7 | Sunk cost and mental accounting |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-commitment-escalator.png) |
