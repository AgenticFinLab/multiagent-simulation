# Trend Chaser

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Trend Chaser                                                                                                         |
| Theory Family         | Positive-Feedback Speculation — Greater Fool Theory — Momentum Trading                                               |
| Behavioral Tendency   | **Diverging** — buys into rising prices and sells into falling prices, amplifying existing trends                     |
| Time Horizon          | Short (reacts immediately to current deviation; no long-term planning)                                               |
| Risk Tolerance        | High (large position sizes chasing momentum; willing to buy at extreme valuations)                                   |
| Information Asymmetry | None (no private information; relies purely on observable price-vs-fundamental deviation)                             |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The trend chaser models speculative participants who buy assets because prices are rising and sell because prices are falling — the classic positive-feedback trader who expects to profit by selling to a "greater fool" at an even higher price. In the Tulip Mania context (1636–1637), these were the speculators in the Dutch Republic who bought tulip futures at escalating prices expecting to resell before the crash. In modern markets, these correspond to retail day-traders chasing momentum, crypto speculators buying during parabolic moves, meme-stock traders expecting "to the moon" outcomes, leveraged ETF momentum chasers, algorithmic trend-following systems without fundamental anchoring, and futures market speculators extrapolating recent price moves.

The agent's decision goal is to detect price deviation from fundamental value and trade IN THE SAME DIRECTION as the deviation — buying when price exceeds fundamental (riding the trend up) and selling when price is below fundamental (following the trend down). Quantity is computed as `min(800, abs(deviation) * 5000)`. This procyclical behaviour amplifies existing mispricings.

The agent's behavioural role inside the simulation is to destabilise prices through positive-feedback trading that accelerates both bubbles and crashes. During bubbles, it adds demand that pushes prices further above fundamental; during crashes, its selling accelerates the decline. Non-goals: (1) the trend chaser MUST NOT perform fundamental valuation or mean-reversion analysis; (2) the trend chaser MUST NOT provide contrarian stabilisation — it always trades WITH the trend.

## Theoretical Foundation

**Positive-Feedback Speculation and Greater Fool Theory (Mackay 1841; De Long et al. 1990)**:
- Theory / Study: Extraordinary Popular Delusions / Positive Feedback Investment Strategies
- Citation: Mackay, C. (1841). *Extraordinary Popular Delusions and the Madness of Crowds*. London: Richard Bentley; De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *The Journal of Finance*, 45(2), 379–395. https://doi.org/10.2307/2328662
- Core Insight: Positive-feedback trading — buying because prices have risen, selling because they have fallen — is a powerful destabilising force in financial markets. When a critical mass of traders extrapolates recent price movements, their collective buying creates a self-fulfilling prophecy that extends trends far beyond fundamental value. The "greater fool" logic assumes someone else will pay an even higher price, justifying purchases at already-inflated valuations. During the Dutch Tulip Mania, this logic pushed single bulb prices to 10x annual wage levels before the abrupt collapse in February 1637.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; if |deviation| > activation_threshold: quantity = min(max_quantity, |deviation| * scaling_factor); direction = sign(deviation) [procyclical]`
- Empirical Evidence: De Long et al. (1990) model demonstrates that positive-feedback traders create excess volatility and predictable price patterns. Empirical studies of the Dutch Tulip Mania (Garber 2000, *Famous First Bubbles*, Table 4.1) document price increases of 500–1100% over 3 months in Semper Augustus bulbs, driven primarily by speculative momentum trading in futures contracts. Thompson (2007) estimates that 90%+ of tulip futures trading in December 1636–January 1637 was speculative rather than end-user demand.
- Relevance to This Agent: The agent operationalises pure positive-feedback trading by always moving in the direction of deviation from fundamental — buying the overvalued (trend up) and selling the undervalued (trend down). The min(800, deviation * 5000) sizing produces large positions during strong trends while capping maximum exposure.
- Calibration Source: `activation_threshold` = 0.02 from De Long et al. (1990) — feedback traders respond to small price movements (2–3% deviations trigger action); `max_quantity` = 800 and `scaling_factor` = 5000 calibrated to produce orders of 100–800 across typical bubble deviations.
- Falsification Conditions: If this agent trades against the deviation direction (contrarian), the positive-feedback mechanism is falsified. If the agent fails to increase buying as positive deviation grows, the procyclical amplification is not functioning.
- Alternative Theories: Fundamental valuation (Garber 2000) explains some tulip price levels through rarity and breeding rights; rational bubble models (Tirole 1985) show bubbles can exist without irrationality under certain conditions.

## Design Purpose and Activation Triggers

Purpose: Inject positive-feedback speculative demand that amplifies both bubbles and crashes through procyclical trading — buying into strength and selling into weakness.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.02): BUY — ride the trend up
- Negative deviation exceeds threshold (deviation < -0.02): SELL — follow the trend down
- Default (|deviation| <= 0.02): HOLD — no clear trend signal

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell (no naked shorting)
- Deviation collapses to near zero for extended period: Agent holds

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                         | Mechanism                                            |
|------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| Strong positive deviation (>0.10) | Maximum position sizes (approaching 800 cap)         | Scaling: min(800, dev * 5000) saturates              |
| Trend reversal               | Rapid direction change within 1 round                    | Mechanistic: follows sign(deviation) without delay    |
| Extreme bubble (>0.16)       | Capped at max quantity 800                               | Hard cap prevents unlimited exposure                 |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental_value` fields. No peer-action summaries, order-book data, or social signals needed — the trend chaser infers trend from price-vs-fundamental deviation.

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
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Procyclical direction (same as deviation sign)   |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold             |
| `quantity`  | float  | [0, 800]                  | shares | yes       | Unsigned order size                              |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Trend direction, momentum strength, quantity     |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- `quantity` MUST NOT exceed 800 (hard cap).
- Direction MUST be procyclical: buy when overvalued, sell when undervalued.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); threshold = {activation_threshold}; trend direction = {'up — buying' if deviation > 0 else 'down — selling'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Trend-chaser: deviation {deviation:.2%}, chasing {'uptrend' if deviation > 0 else 'downtrend'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the procyclical formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST preserve the procyclical direction (buy overvalued, sell undervalued). Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                       |
|---------------------|------------|---------------|-----------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation and trend direction            |
| `fundamental_value` | Continuous | Current tick  | Reference for computing deviation magnitude                    |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible                             |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible                              |

Does NOT use: fundamental valuation analysis, mean-reversion logic, peer positions, order book, volume, moving averages — the trend chaser uses only current deviation as its signal.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Positive-Feedback — De Long et al. 1990)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: deviation direction indicates the trend to chase)

Step 3 — Evaluate activation threshold:
  Read: `activation_threshold`
  IF `|deviation| <= activation_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: implementation convenience — minimum trend strength to trigger action)

Step 4 — Determine PROCYCLICAL trade direction:
  IF `deviation > 0`: action = "buy" (price above fundamental — chase uptrend)
  ELIF `deviation < 0`: action = "sell" (price below fundamental — chase downtrend)
  (Theory trace: De Long et al. 1990 — positive feedback: buy rising, sell falling)

Step 5 — Compute raw quantity:
  Read: `scaling_factor`, `max_quantity`
  `raw_quantity = abs(deviation) * scaling_factor`
  `quantity = min(max_quantity, raw_quantity)`
  (Theory trace: Greater fool — larger trends attract larger speculative positions)

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
| Sizing rule           | `quantity = min(800, abs(deviation) * 5000)`                                          |
| Action lifetime       | Immediate execution; no persistent resting orders                                     |
| Revision policy       | No revision — each round's order is independent                                       |
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                         |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                             |
| Exit rule             | None — agent trades every round when |deviation| > threshold and resources permit     |

#### Mathematical Model

**Decision output:** Unsigned quantity (float in [0, 800]) plus procyclical direction (buy/sell/hold enum).

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

Step 3 — Procyclical direction:
  IF deviation > 0: action = "buy"   [ride uptrend]
  ELSE: action = "sell"              [follow downtrend]

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
- `position`: float, initial value = 0. Net shares held.
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide (after quantity finalised and trade executed).
- `cash`: Updated post-decide (after quantity finalised and trade executed).

**Determinism contract:** Fully deterministic given identical price, fundamental_value, position, cash, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol                | Meaning                                  | Default Value | Source                     |
|-----------------------|------------------------------------------|---------------|----------------------------|
| `activation_threshold`| Minimum |deviation| to trigger trade    | 0.02          | De Long et al. (1990)      |
| `scaling_factor`      | Multiplier from deviation to quantity    | 5000          | Calibration (see §Params)  |
| `max_quantity`        | Hard cap on order size                   | 800           | Simulation design          |

#### Behavioral Properties

- **Time horizon:** Short (reacts immediately to current deviation without forward planning or long-term view)
- **Risk tolerance:** High (large positions up to 800 units chasing trends; willing to buy at extreme overvaluations)
- **Information asymmetry:** None (no private information; purely mechanical response to observable deviation)
- **Psychological profile:** Positive-feedback speculator — exhibits extrapolation bias, greater-fool belief, herd instinct, overconfidence in trend persistence, and disregard for fundamental value

## Parameters

| Parameter              | Type  | Default | Valid Range   | Sensitivity | Description                                                  | Impact                                                  | Source                     |
|------------------------|-------|---------|---------------|-------------|--------------------------------------------------------------|---------------------------------------------------------|----------------------------|
| `activation_threshold` | float | 0.02    | [0.01, 0.10]  | High        | Minimum absolute deviation to trigger trend-chasing trade    | Higher → fewer trades, less bubble amplification        | De Long et al. (1990)      |
| `scaling_factor`       | float | 5000    | [1000, 10000] | High        | Multiplier converting deviation magnitude to quantity        | Higher → larger positions for same deviation            | Calibration estimate       |
| `max_quantity`         | float | 800     | [100, 2000]   | Medium      | Hard cap on maximum order size per round                     | Higher → allows larger single-round positions           | Simulation design          |
| `initial_cash`         | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                      | Higher → agent can chase trends longer                  | Normalisation              |
| `initial_position`     | float | 0.0     | [0, 100]      | Low         | Starting inventory of shares                                 | Non-zero → can sell immediately on negative deviation   | Normalisation              |

## Worked Numerical Examples

### Case 1 — Positive deviation (buy — chase uptrend)

System state: `price` = 159.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 10000.0, `position` = 0.0

Calculation:
- `deviation` = (159.0 - 150.0) / 150.0 = 0.06
- Threshold check: |0.06| > 0.02? YES → active
- Direction: deviation > 0 → action = "buy" (procyclical — chase uptrend)
- `raw_quantity` = 0.06 * 5000 = 300
- `quantity` = min(800, 300) = 300
- Resource check: 300 * 159.0 = 47700 > 10000 → `quantity` = floor(10000 / 159.0) = 62

Decision: buy 62 shares at price = 159.0
State update: `cash`: 10000.0 → 142.0; `position`: 0.0 → 62.0

### Case 2 — Negative deviation (sell — chase downtrend)

System state: `price` = 138.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 5000.0, `position` = 80.0

Calculation:
- `deviation` = (138.0 - 150.0) / 150.0 = -0.08
- Threshold check: |-0.08| > 0.02? YES → active
- Direction: deviation < 0 → action = "sell" (procyclical — chase downtrend)
- `raw_quantity` = 0.08 * 5000 = 400
- `quantity` = min(800, 400) = 400
- Resource check: 400 > position (80) → `quantity` = 80

Decision: sell 80 shares at price = 138.0
State update: `cash`: 5000.0 → 16040.0; `position`: 80.0 → 0.0

### Case 3 — Small deviation (hold)

System state: `price` = 151.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02

Calculation:
- `deviation` = (151.0 - 150.0) / 150.0 = 0.0067
- Threshold check: |0.0067| > 0.02? NO → hold

Decision: hold
State update: No change

### Edge Case — Extreme bubble (cap reached)

System state: `price` = 210.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 200000.0, `position` = 0.0

Calculation:
- `deviation` = (210.0 - 150.0) / 150.0 = 0.40
- `raw_quantity` = 0.40 * 5000 = 2000
- `quantity` = min(800, 2000) = 800 (capped)

Decision: buy 800 shares at price = 210.0
State update: `cash`: 200000.0 → 32000.0; `position`: 0.0 → 800.0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` = 0.02 <- De Long et al. (1990), feedback traders respond to 2–3% price movements
- `scaling_factor` = 5000 <- Calibrated to produce orders of 100–800 across typical bubble deviations (0.02–0.20)
- `max_quantity` = 800 <- Maximum per-round speculative position consistent with simulation scaling

**Expected individual behaviour:**
- Given deviation = +0.06 (above threshold), agent MUST buy with Q = min(800, 0.06 * 5000) = 300
- Given deviation = -0.04 (above threshold magnitude), agent MUST sell with Q = min(800, 0.04 * 5000) = 200
- Given |deviation| = 0.01 (below threshold), agent MUST hold
- Agent MUST ALWAYS trade in the same direction as deviation (procyclical)

**Sanity bounds (red flags indicating broken implementation):**
- IF agent sells when deviation is positive THEN broken (should buy into uptrend — procyclical)
- IF agent buys when deviation is negative THEN broken (should sell into downtrend)
- IF agent trades when |deviation| <= 0.02 THEN broken (threshold gate failed)
- IF agent emits quantity > 800 THEN broken (cap not applied)

### Ablation Hooks

| Ablation name        | Setting                      | Hypothesis tested                                        | Expected direction        | Metric                              |
|----------------------|------------------------------|----------------------------------------------------------|---------------------------|--------------------------------------|
| `no_chaser`          | population = 0               | Removing trend chasers reduces bubble amplitude          | Lower peak deviation      | Max deviation from fundamental       |
| `high_threshold`     | `activation_threshold=0.10`  | Higher threshold delays feedback entry                   | Slower bubble growth      | Rate of price change during bubble   |
| `small_scale`        | `scaling_factor=1000`        | Smaller positions reduce destabilising impact            | Lower peak deviation      | Max deviation from fundamental       |
| `low_cap`            | `max_quantity=200`           | Lower cap limits individual contribution to trend        | Slower bubble growth      | Rounds to reach 50% deviation        |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Mackay, C. (1841). *Extraordinary Popular Delusions and the Madness of Crowds*. London: Richard Bentley.                                          | Historical narrative of speculative manias         |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *The Journal of Finance*, 45(2), 379–395. https://doi.org/10.2307/2328662 | Primary theory — positive feedback model |
| 3 | Garber, P. M. (2000). *Famous First Bubbles: The Fundamentals of Early Manias*. Cambridge, MA: MIT Press.                                        | Tulip Mania price data and analysis                |
| 4 | Thompson, E. A. (2007). The tulipmania: Fact or artifact? *Public Choice*, 130(1), 99–114. https://doi.org/10.1007/s11127-006-9074-4              | Speculative volume estimates for Tulip Mania       |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-trend-chaser.png) |
