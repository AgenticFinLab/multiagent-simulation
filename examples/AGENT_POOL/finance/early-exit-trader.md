# Early Exit Trader

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Early Exit Trader                                                                                                    |
| Theory Family         | Rational Bubble Riding — Strategic Liquidation — Optimal Stopping                                                    |
| Behavioral Tendency   | **Converging** — sells overvalued assets to exit ahead of a crash, providing peak-adjacent selling pressure            |
| Time Horizon          | Medium (rides bubbles partially, then exits before collapse; timing-sensitive)                                        |
| Risk Tolerance        | Medium (participates in bubbles but with exit discipline; not reckless)                                              |
| Information Asymmetry | Partial (possesses valuation discipline but not perfect timing knowledge)                                            |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The early exit trader models sophisticated participants who recognise that bubbles can be partially rational to ride — but who possess the discipline to exit before the peak, locking in gains while less disciplined participants are still accumulating. This is the "smart money" that buys during early bubble phases but sells as overvaluation becomes extreme. In the Tulip Mania context, these were the experienced florists and merchants in Haarlem who sold their bulb inventory in late January 1637, weeks before the crash on February 3rd. In modern markets, these correspond to hedge funds that ride momentum but have stop-profit triggers, venture capitalists who liquidate at IPO, corporate insiders selling after lock-up expiry near peaks, quant funds with mean-reversion overlays, event-driven funds timing catalyst-based exits, and experienced traders with trailing stop-profit discipline.

The agent's decision goal is to detect overvaluation through deviation of price from fundamental value and SELL (contrarian) when |deviation| exceeds 0.05. The agent also buys when undervalued (deviation < -0.05). Quantity is `min(500, abs(deviation) * 3000)`. The agent's sell behaviour near bubble peaks provides the critical "early exit" characteristic — its selling pressure can serve as a trigger for cascade reversals.

The agent's behavioural role inside the simulation is peak-adjacent selling — it provides the first contrarian sell pressure as bubbles mature, potentially catalysing the reversal that crashes the market. Unlike pure fundamentalists who sell throughout the bubble, this agent's theoretical motivation is strategic exit timing rather than permanent value-based contrarianism. Non-goals: (1) the early exit trader MUST NOT hold positions through extreme overvaluations waiting for exact peak timing; (2) the early exit trader MUST NOT refuse to buy undervalued assets — it participates in both directions.

## Theoretical Foundation

**Rational Bubble Riding and Strategic Liquidation (Thompson 2007; Brunnermeier & Nagel 2004)**:
- Theory / Study: The tulipmania: Fact or artifact? / Hedge Funds and the Technology Bubble
- Citation: Thompson, E. A. (2007). The tulipmania: Fact or artifact? *Public Choice*, 130(1), 99–114. https://doi.org/10.1007/s11127-006-9074-4; Brunnermeier, M. K. & Nagel, S. (2004). Hedge funds and the technology bubble. *The Journal of Finance*, 59(5), 2013–2040. https://doi.org/10.1111/j.1540-6261.2004.00690.x
- Core Insight: Some participants in bubble markets are not irrational — they rationally ride the bubble for profits while planning a strategic exit before the crash. Brunnermeier & Nagel (2004) show that hedge funds actually INCREASED positions during the tech bubble but reduced them before the peak, earning positive returns from bubble participation with timely exit. Thompson (2007) argues that some Tulip Mania participants were essentially trading options with limited downside, making their participation rational given the payoff structure. The key is exit discipline: the agent acts contrarian (sells) once deviation reaches levels where the probability of correction exceeds the probability of further appreciation.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; if |deviation| > threshold: quantity = min(max_quantity, |deviation| * scaling_factor); if deviation > 0: sell (exit the overvalued position); if deviation < 0: buy (enter undervalued)`
- Empirical Evidence: Brunnermeier & Nagel (2004) show that hedge funds reduced NASDAQ holdings by 20–40% in Q4 1999 to Q1 2000, before the March 2000 crash (Table III, p. 2029). Their selling preceded the peak by 1–3 months, earning cumulative returns of 30–40% from bubble participation plus timely exit. Thompson (2007) estimates that experienced Dutch florists exited tulip futures 2–4 weeks before the February 1637 crash.
- Relevance to This Agent: The agent's contrarian sell threshold of 0.05 means it begins exiting once overvaluation exceeds 5% — early enough to avoid the worst of a crash but not so early as to miss all bubble gains. The agent's existence creates peak-adjacent selling pressure that can catalyse reversals.
- Calibration Source: `activation_threshold` = 0.05 from Brunnermeier & Nagel (2004) — hedge funds began reducing positions when tech stocks exceeded fundamental estimates by 5–15%; `max_quantity` = 500 reflecting graduated exit rather than panic selling.
- Falsification Conditions: If this agent continues to accumulate (buy) when deviation exceeds +0.10, the exit discipline is falsified. If the agent's selling pattern is not concentrated in the period of peak overvaluation, the strategic timing mechanism is not functioning.
- Alternative Theories: Greater fool theory (agents ride without exit plan); pure fundamentalism (agents sell immediately on any overvaluation); rational expectations (bubble is impossible).

## Design Purpose and Activation Triggers

Purpose: Provide peak-adjacent selling pressure through strategic exit behaviour — the agent sells as overvaluation matures, potentially catalysing cascade reversals.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.05): SELL — exit overvalued position
- Negative deviation exceeds threshold (deviation < -0.05): BUY — enter undervalued position
- Default (|deviation| <= 0.05): HOLD — insufficient signal for strategic action

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell
- Fundamental value signal lost: Agent holds

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                         | Mechanism                                            |
|------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| Moderate overvaluation (0.05–0.10) | Begin selling — graduated exit                     | Linear scaling: deviation * 3000                     |
| Extreme overvaluation (>0.15)| Maximum selling — urgent exit                             | Scaling saturates at max_quantity=500                 |
| Undervaluation (dev < -0.05) | Buy — enter for future exit opportunity                  | Contrarian buying to build position                  |

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

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                          |
|-------------|--------|---------------------------|--------|-----------|--------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Contrarian direction for strategic exit/entry    |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold             |
| `quantity`  | float  | [0, 500]                  | shares | yes       | Unsigned order size                              |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Strategic exit/entry rationale                    |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- `quantity` MUST NOT exceed 500.
- Direction MUST be contrarian: sell overvalued (exit), buy undervalued (enter).

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); threshold = {activation_threshold}; strategic assessment: {'overvalued — strategic exit' if deviation > 0 else 'undervalued — strategic entry'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Early-exit-trader: deviation {deviation:.2%}, strategic {'exit' if deviation > 0 else 'entry'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the strategic exit formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST preserve contrarian direction. Retrieval-augmented variants inject domain knowledge but MUST honour the same schema. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                       |
|---------------------|------------|---------------|-----------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation and exit timing                |
| `fundamental_value` | Continuous | Current tick  | Reference for determining overvaluation level                   |
| `position`          | Continuous | Persisted     | Determines whether sell (exit) is feasible                      |
| `cash`              | Continuous | Persisted     | Determines whether buy (entry) is feasible                      |

Does NOT use: exact peak timing prediction, peer exit signals, volume data, momentum — uses only current deviation as exit trigger.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Strategic Liquidation — Brunnermeier & Nagel 2004)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: deviation level signals when exit probability exceeds continuation value)

Step 3 — Evaluate activation threshold:
  Read: `activation_threshold`
  IF `|deviation| <= activation_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: Thompson 2007 — strategic exit requires sufficient overvaluation to justify timing risk)

Step 4 — Determine contrarian direction:
  IF `deviation > 0`: action = "sell" (overvalued — strategic exit)
  ELIF `deviation < 0`: action = "buy" (undervalued — strategic entry)
  (Theory trace: Brunnermeier & Nagel 2004 — smart money sells into bubble peaks)

Step 5 — Compute quantity:
  Read: `scaling_factor`, `max_quantity`
  `raw_quantity = abs(deviation) * scaling_factor`
  `quantity = min(max_quantity, raw_quantity)`
  (Theory trace: graduated exit — larger sales as overvaluation increases)

Step 6 — Apply resource constraints:
  Read: `cash`, `position`
  IF action == "buy" AND quantity * price > cash: `quantity = floor(cash / price)`
  IF action == "sell" AND quantity > position: `quantity = position`
  Write: final `quantity`
  (Implementation convenience — no theoretical claim)

Step 7 — Execute trade and update state:
  IF action == "buy": Write: `cash -= quantity * price`; `position += quantity`
  IF action == "sell": Write: `cash += quantity * price`; `position -= quantity`
  (Implementation convenience — state bookkeeping)

#### Action Space

| Aspect                | Specification                                                                         |
|-----------------------|---------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                 |
| Action parameter rule | `price` = current market price (price-taker; no limit orders)                         |
| Sizing rule           | `quantity = min(500, abs(deviation) * 3000)`                                          |
| Action lifetime       | Immediate execution; no persistent resting orders                                     |
| Revision policy       | No revision — each round's order is independent                                       |
| State constraint      | Position >= 0 (no naked shorting)                                                     |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                             |
| Exit rule             | None — agent exits (sells) at any round when deviation > threshold and position > 0   |

#### Mathematical Model

**Decision output:** Unsigned quantity (float in [0, 500]) plus contrarian direction (buy/sell/hold enum).

**Decision logic formalization:**

```
Given: price, fundamental_value, activation_threshold, scaling_factor, max_quantity

Step 1 — Compute deviation:
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate:
  IF abs(deviation) <= activation_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Contrarian direction:
  IF deviation > 0: action = "sell"   [strategic exit]
  ELSE: action = "buy"               [strategic entry]

Step 4 — Quantity:
  raw_quantity = abs(deviation) * scaling_factor
  quantity = min(max_quantity, raw_quantity)

Step 5 — Resource constraint:
  IF action == "buy": quantity = min(quantity, floor(cash / price))
  IF action == "sell": quantity = min(quantity, position)

Step 6 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
  IF action == "sell": cash += quantity * price; position -= quantity
```

**State variables:**
- `position`: float, initial value = 50. Net shares held (starts with holding to enable exit).
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide.
- `cash`: Updated post-decide.

**Determinism contract:** Fully deterministic. No stochastic components.

**Parameter symbol table:**

| Symbol                | Meaning                                  | Default Value | Source                          |
|-----------------------|------------------------------------------|---------------|----------------------------------|
| `activation_threshold`| Minimum |deviation| to trigger action   | 0.05          | Brunnermeier & Nagel (2004)      |
| `scaling_factor`      | Multiplier from deviation to quantity    | 3000          | Calibration (see §Params)        |
| `max_quantity`        | Hard cap on order size                   | 500           | Strategic graduated exit design  |

#### Behavioral Properties

- **Time horizon:** Medium (participates in both directions; exits as overvaluation matures rather than waiting for exact peak)
- **Risk tolerance:** Medium (disciplined exit prevents catastrophic loss; but still participates in speculative markets)
- **Information asymmetry:** Partial (possesses valuation discipline; lacks perfect peak-timing knowledge)
- **Psychological profile:** Disciplined strategic trader — combines partial bubble participation with exit discipline; no sunk cost bias; willing to sell into strength; represents "smart money" behaviour documented by Brunnermeier & Nagel (2004)

## Parameters

| Parameter              | Type  | Default | Valid Range   | Sensitivity | Description                                                  | Impact                                                    | Source                          |
|------------------------|-------|---------|---------------|-------------|--------------------------------------------------------------|-----------------------------------------------------------|---------------------------------|
| `activation_threshold` | float | 0.05    | [0.02, 0.15]  | High        | Minimum deviation to trigger strategic exit/entry            | Higher → later exit, more bubble participation            | Brunnermeier & Nagel (2004)     |
| `scaling_factor`       | float | 3000    | [1000, 8000]  | High        | Multiplier converting deviation to quantity                  | Higher → larger exit orders, faster liquidation           | Calibration estimate            |
| `max_quantity`         | float | 500     | [100, 1000]   | Medium      | Hard cap on order size per round                             | Higher → can exit position faster                         | Strategic exit design           |
| `initial_cash`         | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                      | Higher → more entry capacity                              | Normalisation                   |
| `initial_position`     | float | 50.0    | [0, 200]      | Medium      | Starting position (enables immediate exit on overvaluation)  | Higher → more shares available for early exit selling     | Simulation design               |

## Worked Numerical Examples

### Case 1 — Overvalued (sell — strategic exit)

System state: `price` = 165.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (165.0 - 150.0) / 150.0 = 0.10
- Threshold check: |0.10| > 0.05? YES → active
- Direction: deviation > 0 → action = "sell" (strategic exit)
- `raw_quantity` = 0.10 * 3000 = 300
- `quantity` = min(500, 300) = 300
- Resource check: 300 > position (50) → `quantity` = 50

Decision: sell 50 shares at price = 165.0
State update: `cash`: 10000.0 → 18250.0; `position`: 50.0 → 0.0

### Case 2 — Undervalued (buy — strategic entry)

System state: `price` = 135.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500, `cash` = 10000.0, `position` = 0.0

Calculation:
- `deviation` = (135.0 - 150.0) / 150.0 = -0.10
- Threshold check: |-0.10| > 0.05? YES → active
- Direction: deviation < 0 → action = "buy" (strategic entry)
- `raw_quantity` = 0.10 * 3000 = 300
- `quantity` = min(500, 300) = 300
- Resource check: 300 * 135.0 = 40500 > 10000 → `quantity` = floor(10000 / 135.0) = 74

Decision: buy 74 shares at price = 135.0
State update: `cash`: 10000.0 → 10.0; `position`: 0.0 → 74.0

### Case 3 — Within band (hold)

System state: `price` = 153.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05

Calculation:
- `deviation` = (153.0 - 150.0) / 150.0 = 0.02
- Threshold check: |0.02| > 0.05? NO → hold

Decision: hold
State update: No change

### Edge Case — Extreme overvaluation (cap reached, position already partially exited)

System state: `price` = 225.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500, `position` = 200.0

Calculation:
- `deviation` = (225.0 - 150.0) / 150.0 = 0.50
- `raw_quantity` = 0.50 * 3000 = 1500
- `quantity` = min(500, 1500) = 500 (capped)
- Resource check: 500 <= position (200) → NO, `quantity` = 200

Decision: sell 200 shares at price = 225.0 (exit all remaining)
State update: `position`: 200.0 → 0.0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` = 0.05 <- Brunnermeier & Nagel (2004), hedge funds began selling at 5–15% overvaluation
- `scaling_factor` = 3000 <- Graduated exit producing 150–500 shares across typical overvaluation range
- `max_quantity` = 500 <- Reflects graduated rather than panic selling behaviour

**Expected individual behaviour:**
- Given deviation = +0.10 and position = 50, agent MUST sell all 50 shares (strategic exit)
- Given deviation = -0.08, agent MUST buy with Q = min(500, 0.08 * 3000) = 240 (strategic entry)
- Given |deviation| = 0.03, agent MUST hold
- Agent's selling MUST be concentrated during overvaluation episodes (peak-adjacent)

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation is positive THEN broken (should be exiting, not accumulating)
- IF agent trades when |deviation| <= 0.05 THEN broken (threshold gate failed)
- IF agent emits quantity > 500 THEN broken (cap not applied)
- IF agent holds through extreme overvaluation (>0.20) without selling THEN broken (exit discipline absent)

### Ablation Hooks

| Ablation name         | Setting                      | Hypothesis tested                                        | Expected direction        | Metric                              |
|-----------------------|------------------------------|----------------------------------------------------------|---------------------------|--------------------------------------|
| `no_early_exit`       | population = 0               | Removing early-exiters delays bubble peak reversal       | Later crash timing        | Round of first major decline         |
| `low_threshold`       | `activation_threshold=0.02`  | Earlier exit triggers faster bubble deflation            | Earlier correction        | Round of peak price                  |
| `high_threshold`      | `activation_threshold=0.15`  | Later exit allows bubble to grow further                 | Higher peak               | Max deviation from fundamental       |
| `large_scale`         | `scaling_factor=6000`        | Larger exit orders create more selling pressure          | Sharper correction        | Rate of price decline at peak        |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Thompson, E. A. (2007). The tulipmania: Fact or artifact? *Public Choice*, 130(1), 99–114. https://doi.org/10.1007/s11127-006-9074-4              | Rational bubble participation in Tulip Mania       |
| 2 | Brunnermeier, M. K. & Nagel, S. (2004). Hedge funds and the technology bubble. *The Journal of Finance*, 59(5), 2013–2040. https://doi.org/10.1111/j.1540-6261.2004.00690.x | Empirical evidence of smart-money exit timing |
| 3 | Shleifer, A. & Vishny, R. W. (1997). The limits of arbitrage. *The Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Capital constraints on exit capacity |
| 4 | Tirole, J. (1985). Asset bubbles and overlapping generations. *Econometrica*, 53(6), 1499–1528. https://doi.org/10.2307/1913232                   | Rational bubble theory                             |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-early-exit-trader.png) |
