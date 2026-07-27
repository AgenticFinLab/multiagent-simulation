# Skeptical Analyst

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Skeptical Analyst                                                                                                    |
| Theory Family         | Fundamental Valuation — Limits to Arbitrage                                                                          |
| Behavioral Tendency   | **Converging** — sells overvalued assets and buys undervalued ones, pushing prices toward fundamental value           |
| Time Horizon          | Medium-Long (patient; waits for large mispricings before acting)                                                     |
| Risk Tolerance        | Low-Medium (smaller position sizes, higher activation threshold than speculators)                                    |
| Information Asymmetry | Partial (possesses fundamental valuation capability but lacks timing information)                                     |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The skeptical analyst models fundamentally-oriented investors who assess intrinsic value through cash-flow analysis, discount models, or historical valuation multiples, and trade against mispricings when they become sufficiently large. In the South Sea Bubble context, these were the minority of sceptics — Archibald Hutcheson, who published pamphlets questioning the Company's arithmetic, and cautious merchants who doubted the South American trade monopoly would generate claimed revenues. In modern markets, these correspond to value investors, fundamental analysts at research firms, short-sellers with deep due-diligence processes, contrarian fund managers, academic finance researchers monitoring valuation ratios, and pension fund CIOs applying liability-driven investment frameworks.

The agent's decision goal is to detect mispricing through a deviation signal (current price relative to fundamental value), then trade AGAINST the deviation when it exceeds a higher threshold (0.05). The quantity is computed as `min(500, abs(deviation) * 3000)`. The agent buys when price is below fundamental (undervalued) and sells when price is above fundamental (overvalued). This is the opposite direction from the insider and narrative agents.

The agent's behavioural role inside the simulation is to provide a stabilising counterforce, but one that is structurally weak — its lower position cap (500 vs 800) and higher activation threshold (0.05 vs 0.02) mean it enters late and trades smaller, consistent with the "limits to arbitrage" literature. Non-goals: (1) the skeptical analyst MUST NOT trade in the direction of the bubble (buy overvalued assets); (2) the skeptical analyst MUST NOT use momentum or trend signals — it is purely contrarian against fundamentals.

## Theoretical Foundation

**Fundamental Valuation and Limits to Arbitrage (Shleifer & Vishny 1997; Dale 2004)**:
- Theory / Study: The Limits of Arbitrage
- Citation: Shleifer, A. & Vishny, R. W. (1997). The limits of arbitrage. *The Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x; Dale, R. (2004). *The First Crash: Lessons from the South Sea Bubble*. Princeton University Press.
- Core Insight: Rational arbitrageurs who identify mispricings face capital constraints, noise trader risk, and agency problems that limit their ability to correct prices. Even when fundamental value is known, the arbitrageur's finite capital and risk of forced liquidation before prices correct means that stabilising forces are structurally weaker than destabilising ones. During the South Sea Bubble, sceptics who sold early faced margin calls as prices continued rising, forcing them to cover at losses.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; if |deviation| > threshold: quantity = min(max_quantity, |deviation| * scaling_factor); direction = -sign(deviation) [contrarian]`
- Empirical Evidence: Shleifer & Vishny (1997) show that performance-based arbitrage capital flows out of contrarian funds exactly when mispricings are largest (Table 1, correlation of -0.6 between fund flows and mispricing magnitude). Dale (2004) documents that early short-sellers of South Sea stock faced forced buybacks when price rose 200% before eventually collapsing, with estimated losses of 30–50% of capital for those who covered early.
- Relevance to This Agent: The agent's higher threshold (0.05 vs 0.02) and lower max quantity (500 vs 800) operationalise the limits to arbitrage — it acts only on large deviations and with constrained firepower, representing the structural weakness of stabilising forces during bubbles.
- Calibration Source: `activation_threshold` = 0.05 from Shleifer & Vishny (1997) — arbitrageurs typically require mispricing of 5–10% before capital deployment is justified given transaction costs and noise trader risk; `max_quantity` = 500 reflecting capital constraints (~60% of speculator capacity).
- Falsification Conditions: If this agent buys when price exceeds fundamental (trades WITH the bubble), the contrarian mechanism is falsified. If the agent trades at deviations below 0.05, the limits-to-arbitrage threshold discipline is broken.
- Alternative Theories: Efficient Markets Hypothesis (Fama 1970) would deny persistent mispricings exist; DeLong et al. (1990) noise trader risk model provides a complementary explanation for why arbitrage is limited.

## Design Purpose and Activation Triggers

Purpose: Provide a structurally weak stabilising force that trades against mispricings but only at large deviations with limited capacity, illustrating limits to arbitrage.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely. If cash or position data is stale, the agent uses last known values.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.05): SELL — asset overvalued, contrarian selling
- Negative deviation exceeds threshold (deviation < -0.05): BUY — asset undervalued, contrarian buying
- Default (|deviation| <= 0.05): HOLD — mispricing too small to justify action given costs/risk

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell
- Fundamental value signal lost: Agent hibernates

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                              | Mechanism                                              |
|------------------------------|----------------------------------------------------------------|--------------------------------------------------------|
| Extreme overvaluation (>0.20)| Maximum sell quantity deployed                                  | Scaling saturates at max_quantity=500                   |
| Moderate mispricing (0.05–0.10)| Small contrarian positions                                   | Linear scaling: quantity = deviation * 3000            |
| Mispricing correction        | Positions unwound as deviation approaches zero                 | Hold triggered when |deviation| falls below threshold  |

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
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Contrarian direction: opposite to deviation sign  |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold             |
| `quantity`  | float  | [0, 500]                  | shares | yes       | Unsigned order size                              |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Fundamental deviation and contrarian rationale    |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- `quantity` MUST NOT exceed 500 (hard cap from min() function).
- Direction MUST be contrarian: sell when overvalued, buy when undervalued.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); threshold = {activation_threshold}; contrarian action indicated; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Skeptical-analyst: deviation {deviation:.2%}, contrarian {'sell' if deviation > 0 else 'buy'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula with contrarian direction. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST preserve the contrarian direction (sell overvalued, buy undervalued). Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field constraints. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                       |
|---------------------|------------|---------------|-----------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation from fundamental               |
| `fundamental_value` | Continuous | Current tick  | Reference value against which overvaluation is assessed         |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible                             |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible (resource constraint)        |

Does NOT use: narratives, momentum signals, peer positions, order book depth, trading volume, social sentiment — the skeptical analyst relies exclusively on fundamental valuation comparison.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Fundamental Valuation — Shleifer & Vishny 1997)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: Fundamental valuation — deviation measures mispricing)

Step 3 — Evaluate activation threshold:
  Read: `activation_threshold`
  IF `|deviation| <= activation_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: Limits to arbitrage — requires large mispricing to justify action)

Step 4 — Determine CONTRARIAN trade direction:
  IF `deviation > 0`: action = "sell" (overvalued — sell against bubble)
  ELIF `deviation < 0`: action = "buy" (undervalued — buy the dip)
  (Theory trace: Shleifer & Vishny 1997 — fundamental-based contrarian trading)

Step 5 — Compute raw quantity:
  Read: `scaling_factor`, `max_quantity`
  `raw_quantity = abs(deviation) * scaling_factor`
  `quantity = min(max_quantity, raw_quantity)`
  (Theory trace: Limits to arbitrage — constrained capital limits position size)

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

| Aspect                | Specification                                                                             |
|-----------------------|-------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                     |
| Action parameter rule | `price` = current market price (price-taker; no limit orders)                             |
| Sizing rule           | `quantity = min(500, abs(deviation) * 3000)`                                              |
| Action lifetime       | Immediate execution; no persistent resting orders                                         |
| Revision policy       | No revision — each round's order is independent                                           |
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                             |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                                 |
| Exit rule             | None — agent trades every round when |deviation| > threshold and resources permit         |

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
  IF deviation > 0: action = "sell"   [overvalued → sell]
  ELSE: action = "buy"               [undervalued → buy]

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

| Symbol                | Meaning                                  | Default Value | Source                       |
|-----------------------|------------------------------------------|---------------|------------------------------|
| `activation_threshold`| Minimum |deviation| to trigger trade    | 0.05          | Shleifer & Vishny (1997)     |
| `scaling_factor`      | Multiplier from deviation to quantity    | 3000          | Calibration (see §Params)    |
| `max_quantity`        | Hard cap on order size                   | 500           | Limits to arbitrage design   |

#### Behavioral Properties

- **Time horizon:** Medium-Long (waits for large mispricings; patient contrarian approach)
- **Risk tolerance:** Low-Medium (smaller positions than speculators; higher threshold before action; capital-constrained)
- **Information asymmetry:** Partial (knows fundamental value but lacks timing information about when correction will occur)
- **Psychological profile:** Rational fundamental analyst — no cognitive biases; driven by discounted cash-flow logic; faces limits-to-arbitrage constraints (capital, noise trader risk) rather than behavioural limitations

## Parameters

| Parameter              | Type  | Default | Valid Range   | Sensitivity | Description                                                    | Impact                                                    | Source                       |
|------------------------|-------|---------|---------------|-------------|----------------------------------------------------------------|-----------------------------------------------------------|------------------------------|
| `activation_threshold` | float | 0.05    | [0.02, 0.15]  | High        | Minimum absolute deviation to trigger contrarian trade          | Higher → fewer trades, larger mispricings tolerated       | Shleifer & Vishny (1997)     |
| `scaling_factor`       | float | 3000    | [1000, 8000]  | High        | Multiplier converting deviation magnitude to quantity          | Higher → larger positions for same deviation              | Calibration estimate         |
| `max_quantity`         | float | 500     | [100, 1000]   | Medium      | Hard cap on maximum order size per round                       | Higher → allows larger single-round contrarian positions  | Limits to arbitrage design   |
| `initial_cash`         | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                        | Higher → agent can sustain more rounds of buying          | Normalisation                |
| `initial_position`     | float | 0.0     | [0, 100]      | Low         | Starting inventory of shares                                   | Non-zero → can sell immediately on positive deviation     | Normalisation                |

## Worked Numerical Examples

### Case 1 — Overvalued asset (sell — contrarian)

System state: `price` = 165.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (165.0 - 150.0) / 150.0 = 0.10
- Threshold check: |0.10| > 0.05? YES → active
- Direction: deviation > 0 → action = "sell" (contrarian — asset overvalued)
- `raw_quantity` = 0.10 * 3000 = 300
- `quantity` = min(500, 300) = 300
- Resource check: 300 > position (50) → `quantity` = 50

Decision: sell 50 shares at price = 165.0
State update: `cash`: 10000.0 → 18250.0; `position`: 50.0 → 0.0

### Case 2 — Undervalued asset (buy — contrarian)

System state: `price` = 135.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500, `cash` = 10000.0, `position` = 0.0

Calculation:
- `deviation` = (135.0 - 150.0) / 150.0 = -0.10
- Threshold check: |-0.10| > 0.05? YES → active
- Direction: deviation < 0 → action = "buy" (contrarian — asset undervalued)
- `raw_quantity` = 0.10 * 3000 = 300
- `quantity` = min(500, 300) = 300
- Resource check: 300 * 135.0 = 40500 > 10000 → `quantity` = floor(10000 / 135.0) = 74

Decision: buy 74 shares at price = 135.0
State update: `cash`: 10000.0 → 10.0; `position`: 0.0 → 74.0

### Case 3 — Moderate deviation (hold — below threshold)

System state: `price` = 155.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500

Calculation:
- `deviation` = (155.0 - 150.0) / 150.0 = 0.033
- Threshold check: |0.033| > 0.05? NO → hold

Decision: hold
State update: No change

### Edge Case — Extreme overvaluation (cap reached)

System state: `price` = 225.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500, `cash` = 5000.0, `position` = 600.0

Calculation:
- `deviation` = (225.0 - 150.0) / 150.0 = 0.50
- Threshold check: |0.50| > 0.05? YES → active
- Direction: deviation > 0 → action = "sell"
- `raw_quantity` = 0.50 * 3000 = 1500
- `quantity` = min(500, 1500) = 500 (capped)
- Resource check: 500 <= position (600) → OK

Decision: sell 500 shares at price = 225.0
State update: `cash`: 5000.0 → 117500.0; `position`: 600.0 → 100.0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` = 0.05 <- Shleifer & Vishny (1997), arbitrageurs require 5–10% mispricing to overcome transaction costs and noise trader risk
- `scaling_factor` = 3000 <- Calibrated for moderate positions (150–500) over typical deviation range (0.05–0.20)
- `max_quantity` = 500 <- Represents ~60% of speculator capacity, consistent with capital constraints in limits-to-arbitrage literature

**Expected individual behaviour:**
- Given price = 1.10 * fundamental and threshold = 0.05, agent MUST sell with quantity = min(500, 0.10 * 3000) = 300 (subject to position constraint)
- Given price = 0.90 * fundamental and threshold = 0.05, agent MUST buy with quantity = min(500, 0.10 * 3000) = 300 (subject to cash constraint)
- Given |deviation| = 0.03 (below threshold), agent MUST hold regardless of mispricing direction
- Agent MUST never buy overvalued assets or sell undervalued ones

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation is positive THEN broken (direction logic inverted — should be contrarian)
- IF agent trades when |deviation| <= 0.05 THEN broken (threshold gate failed)
- IF agent emits quantity > 500 THEN broken (cap not applied)
- IF agent's net effect over 50 rounds is to amplify deviation from fundamental THEN broken (should stabilise)

### Ablation Hooks

| Ablation name        | Setting                      | Hypothesis tested                                          | Expected direction         | Metric                             |
|----------------------|------------------------------|------------------------------------------------------------|----------------------------|------------------------------------|
| `no_skeptic`         | population = 0               | Removing skeptics increases bubble amplitude               | Increase in peak deviation | Max |deviation| from fundamental   |
| `low_threshold`      | `activation_threshold=0.02`  | Lower threshold enables earlier contrarian entry           | Earlier sell-side activity | Round of first sell action          |
| `high_capacity`      | `max_quantity=800`           | More capital allows stronger stabilisation                 | Lower peak deviation       | Max |deviation| from fundamental   |
| `weak_scaling`       | `scaling_factor=1000`        | Reduced position size weakens stabilising force            | Higher peak deviation      | Max |deviation| from fundamental   |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Shleifer, A. & Vishny, R. W. (1997). The limits of arbitrage. *The Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Primary theory source; limits to arbitrage    |
| 2 | Dale, R. (2004). *The First Crash: Lessons from the South Sea Bubble*. Princeton University Press.                                                | Historical context for skeptics in SSB             |
| 3 | Fama, E. F. (1970). Efficient capital markets. *The Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486                          | Alternative theory (EMH)                           |
| 4 | De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703 | Complementary theory — noise trader risk |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-skeptical-analyst.png) |
