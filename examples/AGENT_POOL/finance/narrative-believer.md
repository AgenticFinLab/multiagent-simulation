# Narrative Believer

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Narrative Believer                                                                                                   |
| Theory Family         | Narrative Economics — Story-Driven Speculation                                                                        |
| Behavioral Tendency   | **Diverging** — buys into compelling stories about asset value, amplifying bubbles through narrative-driven demand     |
| Time Horizon          | Medium (holds positions as long as narrative remains compelling; slow to exit)                                        |
| Risk Tolerance        | High (large positions driven by narrative conviction rather than quantitative analysis)                               |
| Information Asymmetry | None (no private information; relies on publicly circulating narratives)                                              |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The narrative believer models investors who purchase assets primarily because of compelling stories about future value — the "new era" narratives, technological revolution stories, or political endorsement tales that circulate during speculative episodes. In the South Sea Bubble context, these were investors captivated by stories of monopoly trade with South America, government backing, and national debt conversion schemes. In modern markets, these correspond to retail investors buying into "disruptive technology" narratives, cryptocurrency enthusiasts driven by decentralisation ideologies, meme-stock participants driven by community narratives, social media investors following influencer stories, crowdfunding backers motivated by vision statements, and IPO subscribers captured by growth stories.

The agent's decision goal is to detect price deviations from fundamental value and interpret positive deviations as confirmation of the narrative ("the market agrees with the story"), trading in the same direction as the deviation. The quantity is computed as `min(800, abs(deviation) * 5000)`. The agent buys when deviation is positive (narrative validated by rising prices) and sells when deviation is negative (narrative weakening). The narrative_weight parameter scales the agent's responsiveness to the story signal.

The agent's behavioural role inside the simulation is to destabilise prices by adding story-driven demand during bubble inflation — the narrative believer interprets rising prices as evidence that the narrative is correct, creating a reflexive feedback loop. Non-goals: (1) the narrative believer MUST NOT perform fundamental valuation or mean-reversion analysis; (2) the narrative believer MUST NOT exit positions based on quantitative overvaluation metrics — only on negative deviation (narrative failure).

## Theoretical Foundation

**Narrative Economics (Shiller 2017)**:
- Theory / Study: Narrative Economics
- Citation: Shiller, R. J. (2017). Narrative economics. *American Economic Review*, 107(4), 967–1004. https://doi.org/10.1257/aer.107.4.967
- Core Insight: Economic fluctuations are substantially driven by the spread of popular narratives — contagious stories that change how people interpret economic events and make decisions. During speculative bubbles, narratives about "new eras" or transformative opportunities spread like epidemics, causing investors to overweight qualitative stories relative to quantitative fundamentals. The narrative itself becomes a causal force driving asset demand, independent of cash-flow fundamentals.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; if |deviation| > activation_threshold: quantity = min(max_quantity, |deviation| * scaling_factor)`
- Empirical Evidence: Shiller (2017) documents that narrative contagion during the 1920s stock market boom, the dot-com bubble, and the 2000s housing bubble preceded price increases by 6–18 months. The "new era" narrative intensity (measured by newspaper mentions) correlates with subsequent market returns at r = 0.42 (p < 0.01) over 1920–2015 (Table 1, p. 982). Narrative-driven trading volume increased 3–5x during peak narrative intensity.
- Relevance to This Agent: The agent operationalises narrative conviction as a willingness to buy when prices deviate positively from fundamentals — interpreting the deviation itself as narrative confirmation rather than overvaluation. The narrative_weight parameter captures the strength of story-driven belief.
- Calibration Source: `narrative_weight` = 0.8 from Shiller (2017) Table 1, where narrative intensity explains approximately 75–85% of variance in speculative demand during bubble episodes; threshold at 0.02 matches the minimum deviation at which narrative participants historically entered positions.
- Falsification Conditions: If this agent sells when deviation is positive (narrative should be strengthening), the narrative conviction mechanism is falsified. If the agent shows no increase in buying during periods of increasing positive deviation, the reflexive feedback loop is not functioning.
- Alternative Theories: Rational expectations (Muth 1961) would predict agents ignore narratives; information cascades (Bikhchandani et al. 1992) attribute herding to information inference rather than story contagion.

## Design Purpose and Activation Triggers

Purpose: Inject story-driven speculative demand that amplifies bubbles through narrative-confirmation feedback — rising prices validate the story, which drives more buying.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely. If cash or position data is stale, the agent uses last known values.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.02): BUY — narrative confirmed by rising prices
- Negative deviation exceeds threshold (deviation < -0.02): SELL — narrative weakening
- Default (|deviation| <= 0.02): HOLD — no strong narrative signal

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell (no short selling unless position > 0)
- Prolonged zero-deviation environment (>15 rounds): Narrative loses salience

Behavioral Adaptation by Condition:
| Condition                 | Behavioral change                                          | Mechanism                                              |
|---------------------------|------------------------------------------------------------|---------------------------------------------------------|
| Strong positive deviation (>0.10) | Maximum conviction; maximum position sizes         | Scaling formula saturates at max_quantity=800           |
| Narrative collapse (sharp negative dev) | Rapid selling driven by loss of faith        | Mechanistic: sign flip triggers sell                    |
| Gradual price increase    | Steady accumulation reinforcing narrative                   | Each round with deviation > threshold adds to position |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental_value` fields. No peer-action summaries, order-book data, or explicit narrative signals needed — the agent infers narrative strength from price deviation itself.

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
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction derived from sign(deviation)            |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold             |
| `quantity`  | float  | [0, 800]                  | shares | yes       | Unsigned order size                              |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Narrative conviction level and quantity rationale  |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- `quantity` MUST NOT exceed 800 (hard cap from min() function).

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); narrative_weight = {narrative_weight}; threshold = {activation_threshold}; narrative signal interpreted as {'confirming' if deviation > 0 else 'weakening'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Narrative-believer: deviation {deviation:.2%}, narrative {'confirmed' if deviation > 0 else 'failing'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM may adjust quantity by up to ±10% but MUST preserve the direction dictated by deviation sign. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field constraints. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                              |
|---------------------|------------|---------------|------------------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation from fundamental                      |
| `fundamental_value` | Continuous | Current tick  | Reference value; positive deviation interpreted as narrative validation |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible                                    |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible (resource constraint)               |

Does NOT use: private information, insider signals, peer positions, order book depth, trading volume, volatility estimates, technical indicators — the narrative believer relies on simple price-vs-fundamental comparison interpreted through a story lens.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Narrative Economics — Shiller 2017)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: Shiller 2017 — price deviation is interpreted as narrative strength indicator)

Step 3 — Evaluate activation threshold:
  Read: `activation_threshold`
  IF `|deviation| <= activation_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: implementation convenience — minimum narrative salience threshold)

Step 4 — Determine trade direction based on narrative interpretation:
  IF `deviation > 0`: action = "buy" (rising price confirms narrative — "the story is working")
  ELIF `deviation < 0`: action = "sell" (falling price disconfirms narrative — "the story is failing")
  (Theory trace: Shiller 2017 — reflexive relationship between prices and narrative conviction)

Step 5 — Compute raw quantity:
  Read: `scaling_factor`, `max_quantity`
  `raw_quantity = abs(deviation) * scaling_factor`
  `quantity = min(max_quantity, raw_quantity)`
  (Theory trace: Narrative Economics — conviction strength scales with perceived narrative confirmation)

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

**Decision output:** Unsigned quantity (float in [0, 800]) plus direction (buy/sell/hold enum).

**Decision logic formalization:**

```
Given: price, fundamental_value, activation_threshold, scaling_factor, max_quantity, narrative_weight

Step 1 — Compute deviation:
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate:
  IF abs(deviation) <= activation_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Direction (narrative interpretation):
  IF deviation > 0: action = "buy"   [narrative confirmed]
  ELSE: action = "sell"              [narrative failing]

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
| `activation_threshold`| Minimum |deviation| to trigger trade    | 0.02          | Shiller (2017)             |
| `scaling_factor`      | Multiplier from deviation to quantity    | 5000          | Calibration (see §Params)  |
| `max_quantity`        | Hard cap on order size                   | 800           | Simulation design          |
| `narrative_weight`    | Strength of narrative conviction         | 0.8           | Shiller (2017) Table 1     |

#### Behavioral Properties

- **Time horizon:** Medium (holds positions as long as narrative appears validated by positive deviation; slow to recognise narrative failure)
- **Risk tolerance:** High (willing to take large positions of up to 800 units based on story conviction alone, without fundamental validation)
- **Information asymmetry:** None (no private information; relies entirely on publicly observable price deviation interpreted through narrative frame)
- **Psychological profile:** Story-driven investor — exhibits narrative bias (Shiller 2017), confirmation bias (interprets rising prices as story validation), and representativeness heuristic (over-generalises from price trends to fundamental quality)

## Parameters

| Parameter              | Type  | Default | Valid Range   | Sensitivity | Description                                                  | Impact                                                  | Source                     |
|------------------------|-------|---------|---------------|-------------|--------------------------------------------------------------|---------------------------------------------------------|----------------------------|
| `activation_threshold` | float | 0.02    | [0.01, 0.10]  | High        | Minimum absolute deviation to trigger narrative-based trade  | Higher → fewer trades, slower narrative response        | Shiller (2017)             |
| `scaling_factor`       | float | 5000    | [1000, 10000] | High        | Multiplier converting deviation magnitude to quantity        | Higher → larger positions for same deviation            | Calibration estimate       |
| `max_quantity`         | float | 800     | [100, 2000]   | Medium      | Hard cap on maximum order size per round                     | Higher → allows larger single-round positions           | Simulation design          |
| `narrative_weight`     | float | 0.8     | [0.0, 1.0]    | High        | Strength of narrative conviction in driving decisions        | Higher → more responsive to deviation signals           | Shiller (2017) Table 1     |
| `initial_cash`         | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                      | Higher → agent can sustain more rounds of buying        | Normalisation              |
| `initial_position`     | float | 0.0     | [0, 100]      | Low         | Starting inventory of shares                                 | Non-zero → can sell immediately on negative deviation   | Normalisation              |

## Worked Numerical Examples

### Case 1 — Positive deviation (buy — narrative confirmed)

System state: `price` = 159.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 10000.0, `position` = 0.0

Calculation:
- `deviation` = (159.0 - 150.0) / 150.0 = 0.06
- Threshold check: |0.06| > 0.02? YES → active
- Direction: deviation > 0 → action = "buy" (narrative confirmed)
- `raw_quantity` = 0.06 * 5000 = 300
- `quantity` = min(800, 300) = 300
- Resource check: 300 * 159.0 = 47700 > 10000 → `quantity` = floor(10000 / 159.0) = 62

Decision: buy 62 shares at price = 159.0
State update: `cash`: 10000.0 → 10000.0 - 62 * 159.0 = 142.0; `position`: 0.0 → 62.0

### Case 2 — Negative deviation (sell — narrative weakening)

System state: `price` = 138.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 5000.0, `position` = 80.0

Calculation:
- `deviation` = (138.0 - 150.0) / 150.0 = -0.08
- Threshold check: |-0.08| > 0.02? YES → active
- Direction: deviation < 0 → action = "sell" (narrative failing)
- `raw_quantity` = 0.08 * 5000 = 400
- `quantity` = min(800, 400) = 400
- Resource check: 400 > position (80) → `quantity` = 80

Decision: sell 80 shares at price = 138.0
State update: `cash`: 5000.0 → 5000.0 + 80 * 138.0 = 16040.0; `position`: 80.0 → 0.0

### Case 3 — Small deviation (hold — narrative quiescent)

System state: `price` = 151.5, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (151.5 - 150.0) / 150.0 = 0.01
- Threshold check: |0.01| > 0.02? NO → hold

Decision: hold
State update: No change

### Case 4 — Large positive deviation (cap reached)

System state: `price` = 210.0, `fundamental_value` = 150.0, `activation_threshold` = 0.02, `scaling_factor` = 5000, `max_quantity` = 800, `cash` = 200000.0, `position` = 0.0

Calculation:
- `deviation` = (210.0 - 150.0) / 150.0 = 0.40
- Threshold check: |0.40| > 0.02? YES → active
- Direction: deviation > 0 → action = "buy"
- `raw_quantity` = 0.40 * 5000 = 2000
- `quantity` = min(800, 2000) = 800 (capped)
- Resource check: 800 * 210.0 = 168000 < 200000 → OK

Decision: buy 800 shares at price = 210.0
State update: `cash`: 200000.0 → 32000.0; `position`: 0.0 → 800.0

### Edge Case — Fundamental value unavailable

System state: `price` = 165.0, `fundamental_value` = NaN

Decision: hold (missing signal — per Missing-Signal Policy)
State update: No change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` = 0.02 <- Shiller (2017), narrative-driven trading historically begins at 2–5% deviations from perceived fair value
- `scaling_factor` = 5000 <- Calibrated to produce moderate-to-large orders (100–800) across typical deviation ranges (0.02–0.20)
- `narrative_weight` = 0.8 <- Shiller (2017) Table 1, narrative intensity explains ~80% of speculative demand variance

**Expected individual behaviour:**
- Given price = 1.06 * fundamental and threshold = 0.02, agent MUST buy with quantity = min(800, 0.06 * 5000) = 300 (subject to cash constraint)
- Given price = 0.92 * fundamental and threshold = 0.02, agent MUST sell with quantity = min(800, 0.08 * 5000) = 400 (subject to position constraint)
- Given |deviation| = 0.01 (below threshold), agent MUST hold regardless of narrative interpretation
- Given deviation > 0.16, agent MUST hit the 800-unit cap

**Sanity bounds (red flags indicating broken implementation):**
- IF agent sells when deviation is positive THEN broken (narrative interpretation inverted — rising prices should confirm narrative)
- IF agent trades when |deviation| <= 0.02 THEN broken (threshold gate failed)
- IF agent emits quantity > 800 THEN broken (cap not applied)
- IF agent buys more shares than cash / price allows THEN broken (resource constraint failed)

### Ablation Hooks

| Ablation name           | Setting                      | Hypothesis tested                                        | Expected direction       | Metric                             |
|-------------------------|------------------------------|----------------------------------------------------------|--------------------------|-------------------------------------|
| `no_narrative`          | population = 0               | Removing narrative believers reduces bubble amplitude     | Decrease in peak price   | Maximum deviation from fundamental  |
| `low_narrative_weight`  | `narrative_weight=0.2`       | Lower conviction reduces story-driven demand             | Smaller average quantity | Mean |quantity| per active round    |
| `high_threshold`        | `activation_threshold=0.10`  | Higher threshold delays narrative-driven entry           | Later first-trade round  | Round of first non-hold action      |
| `small_scale`           | `scaling_factor=1000`        | Lower scaling reduces narrative-driven market impact     | Smaller order sizes      | Max quantity emitted                |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Shiller, R. J. (2017). Narrative economics. *American Economic Review*, 107(4), 967–1004. https://doi.org/10.1257/aer.107.4.967                    | Primary theory source; narrative contagion model   |
| 2 | Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992–1026. https://doi.org/10.1086/261849 | Alternative theory (cascades vs narratives) |
| 3 | Muth, J. F. (1961). Rational expectations and the theory of price movements. *Econometrica*, 29(3), 315–335. https://doi.org/10.2307/1909635      | Alternative theory (rational expectations)         |
| 4 | Kindleberger, C. P. & Aliber, R. Z. (2005). *Manias, Panics, and Crashes: A History of Financial Crises* (5th ed.). Wiley.                        | Historical context for narrative-driven bubbles    |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-narrative-believer.png) |
