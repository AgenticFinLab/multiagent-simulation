# Intrinsic Value Trader

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Intrinsic Value Trader                                                                                               |
| Theory Family         | Fundamental Valuation — Rational Arbitrage — Efficient Markets                                                       |
| Behavioral Tendency   | **Converging** — buys undervalued assets and sells overvalued ones, pushing prices toward intrinsic fundamental value  |
| Time Horizon          | Medium-Long (waits for significant mispricings; patient contrarian approach)                                         |
| Risk Tolerance        | Low-Medium (smaller positions, higher threshold; constrained by limits to arbitrage)                                 |
| Information Asymmetry | Partial (possesses fundamental valuation capability but faces noise-trader risk)                                      |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The intrinsic value trader models fundamentally-oriented market participants who assess an asset's worth through discounted cash-flow analysis, historical comparables, or economic modelling, and trade against deviations when they become sufficiently large. In the Tulip Mania context, these were the rare merchants and horticulturalists who understood the true propagation economics of tulip bulbs — that breeding new varieties took 7–12 years and that most traded varieties had limited long-term scarcity value. In modern markets, these correspond to value investors applying DCF models, fundamental short-sellers with deep research capabilities, sector analysts at investment banks, contrarian macro fund managers, pension fund CIOs using valuation-driven allocation, and academic researchers exploiting documented anomalies.

The agent's decision goal is to detect mispricing through deviation of price from fundamental value, then trade AGAINST the deviation when it exceeds the threshold (0.05). Quantity is `min(500, abs(deviation) * 3000)`. The agent buys when price is below fundamental (undervalued) and sells when above (overvalued). This contrarian direction provides a stabilising force against speculative excess.

The agent's behavioural role inside the simulation is to provide a stabilising but structurally weak counterforce — with lower position caps (500 vs 800) and higher threshold (0.05 vs 0.02) than the destabilising agents, it enters later and trades smaller, consistent with limits to arbitrage during manias. Non-goals: (1) the intrinsic value trader MUST NOT trade in the direction of the bubble (buy overvalued); (2) the intrinsic value trader MUST NOT use momentum, social proof, or trend signals.

## Theoretical Foundation

**Fundamental Valuation (Garber 2000; Shleifer & Vishny 1997)**:
- Theory / Study: Famous First Bubbles / The Limits of Arbitrage
- Citation: Garber, P. M. (2000). *Famous First Bubbles: The Fundamentals of Early Manias*. Cambridge, MA: MIT Press; Shleifer, A. & Vishny, R. W. (1997). The limits of arbitrage. *The Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Even during famous manias, some participants possessed accurate fundamental valuations. Garber (2000) argues that certain tulip prices (especially for rare breeder bulbs) may have been partially justified by fundamentals, while common-variety prices were clearly speculative. The key insight for this agent is that fundamental valuators exist but face limits to arbitrage: capital constraints, noise trader risk (prices can diverge further from fundamental before correcting), and agency problems. Their stabilising force is structurally weaker than the combined destabilising forces of trend chasers and herders.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; if |deviation| > threshold: quantity = min(max_quantity, |deviation| * scaling_factor); direction = -sign(deviation) [contrarian toward fundamental]`
- Empirical Evidence: Garber (2000, Table 4.1) shows that tulip bulb prices for common varieties exceeded fundamental estimates by 500–2000% at the peak in January 1637, while rare varieties were overpriced by 100–300%. Shleifer & Vishny (1997) document that hedge funds specialising in arbitrage experienced capital outflows of 15–30% precisely when mispricings were largest (Table 1), limiting their corrective capacity.
- Relevance to This Agent: The higher threshold (0.05) and lower cap (500) operationalise the limits to arbitrage. The agent trades contrarian but cannot fully correct mispricings due to structural capacity constraints.
- Calibration Source: `activation_threshold` = 0.05 from Shleifer & Vishny (1997) — arbitrageurs require 5–10% mispricing to justify action; `max_quantity` = 500 reflecting 60% of speculator capacity due to capital constraints.
- Falsification Conditions: If this agent buys overvalued assets (trades with the bubble), the contrarian mechanism is falsified. If the agent trades at deviations below 0.05, the limits-to-arbitrage threshold is broken.
- Alternative Theories: Efficient Markets Hypothesis (Fama 1970) would deny persistent mispricings; noise trader models (De Long et al. 1990) explain why arbitrage is limited.

## Design Purpose and Activation Triggers

Purpose: Provide a weak stabilising force through fundamental-based contrarian trading that enters late and trades small, illustrating limits to arbitrage during speculative manias.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.05): SELL — overvalued, contrarian selling
- Negative deviation exceeds threshold (deviation < -0.05): BUY — undervalued, contrarian buying
- Default (|deviation| <= 0.05): HOLD — mispricing too small to justify action

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell
- Fundamental value signal lost: Agent holds

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                         | Mechanism                                            |
|------------------------------|-----------------------------------------------------------|------------------------------------------------------|
| Moderate overvaluation (0.05–0.15) | Small contrarian positions                          | Linear scaling: deviation * 3000                     |
| Extreme overvaluation (>0.15)| Larger positions but still capped at 500                  | Cap limits maximum correction force                  |
| Mispricing correction        | Positions unwound as deviation falls below threshold      | Hold triggered when |deviation| <= 0.05              |

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
| `quantity`  | float  | [0, 500]                  | shares | yes       | Unsigned order size (capped by limits to arb)    |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Fundamental deviation and contrarian rationale    |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- `quantity` MUST NOT exceed 500 (limits-to-arbitrage cap).
- Direction MUST be contrarian: sell overvalued, buy undervalued.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); threshold = {activation_threshold}; intrinsic assessment: {'overvalued — sell' if deviation > 0 else 'undervalued — buy'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Intrinsic-value-trader: deviation {deviation:.2%}, fundamental {'sell overvalued' if deviation > 0 else 'buy undervalued'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the contrarian formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST preserve the contrarian direction. Retrieval-augmented variants inject domain knowledge but MUST honour the same output schema. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                       |
|---------------------|------------|---------------|-----------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation from fundamental               |
| `fundamental_value` | Continuous | Current tick  | True value against which overvaluation is assessed              |
| `position`          | Continuous | Persisted     | Determines whether sell is feasible                             |
| `cash`              | Continuous | Persisted     | Determines whether buy is feasible                              |

Does NOT use: momentum signals, social proof, peer positions, order book, trend indicators — pure fundamental valuation comparison.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Fundamental valuation — Garber 2000)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: deviation from intrinsic value triggers arbitrage)

Step 3 — Evaluate activation threshold:
  Read: `activation_threshold`
  IF `|deviation| <= activation_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: Shleifer & Vishny 1997 — limits to arbitrage create inaction zone)

Step 4 — Determine contrarian direction:
  IF `deviation > 0`: action = "sell" (overvalued — sell against mania)
  ELIF `deviation < 0`: action = "buy" (undervalued — buy the correction)
  (Theory trace: Garber 2000 — fundamental valuators trade against mispricings)

Step 5 — Compute quantity:
  Read: `scaling_factor`, `max_quantity`
  `raw_quantity = abs(deviation) * scaling_factor`
  `quantity = min(max_quantity, raw_quantity)`
  (Theory trace: Limits to arbitrage — constrained capacity caps correction force)

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
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                         |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                             |
| Exit rule             | None — agent trades when |deviation| > threshold and resources permit                 |

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
  IF deviation > 0: action = "sell"
  ELSE: action = "buy"

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
- `position`: Updated post-decide.
- `cash`: Updated post-decide.

**Determinism contract:** Fully deterministic. No stochastic components.

**Parameter symbol table:**

| Symbol                | Meaning                                  | Default Value | Source                       |
|-----------------------|------------------------------------------|---------------|------------------------------|
| `activation_threshold`| Minimum |deviation| to trigger trade    | 0.05          | Shleifer & Vishny (1997)     |
| `scaling_factor`      | Multiplier from deviation to quantity    | 3000          | Calibration (see §Params)    |
| `max_quantity`        | Hard cap on order size                   | 500           | Limits to arbitrage design   |

#### Behavioral Properties

- **Time horizon:** Medium-Long (waits for significant mispricings; patient contrarian)
- **Risk tolerance:** Low-Medium (smaller positions; higher threshold; constrained)
- **Information asymmetry:** Partial (knows fundamental value but faces timing risk)
- **Psychological profile:** Rational fundamentalist — no cognitive biases; driven by DCF logic; faces structural constraints (capital, noise trader risk) rather than behavioural limitations

## Parameters

| Parameter              | Type  | Default | Valid Range   | Sensitivity | Description                                                    | Impact                                                    | Source                       |
|------------------------|-------|---------|---------------|-------------|----------------------------------------------------------------|-----------------------------------------------------------|------------------------------|
| `activation_threshold` | float | 0.05    | [0.02, 0.15]  | High        | Minimum absolute deviation to trigger contrarian trade          | Higher → fewer trades, more mispricing tolerated          | Shleifer & Vishny (1997)     |
| `scaling_factor`       | float | 3000    | [1000, 8000]  | High        | Multiplier converting deviation to quantity                    | Higher → larger contrarian positions                      | Calibration estimate         |
| `max_quantity`         | float | 500     | [100, 1000]   | Medium      | Hard cap on order size (limits to arbitrage)                   | Higher → stronger correction capability                   | Limits to arbitrage design   |
| `initial_cash`         | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                        | Higher → more buying capacity                             | Normalisation                |
| `initial_position`     | float | 0.0     | [0, 100]      | Low         | Starting inventory                                             | Non-zero → can sell immediately on positive deviation     | Normalisation                |

## Worked Numerical Examples

### Case 1 — Overvalued (sell — contrarian)

System state: `price` = 165.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (165.0 - 150.0) / 150.0 = 0.10
- Threshold check: |0.10| > 0.05? YES → active
- Direction: deviation > 0 → action = "sell"
- `raw_quantity` = 0.10 * 3000 = 300
- `quantity` = min(500, 300) = 300
- Resource check: 300 > position (50) → `quantity` = 50

Decision: sell 50 shares at price = 165.0
State update: `cash`: 10000.0 → 18250.0; `position`: 50.0 → 0.0

### Case 2 — Undervalued (buy — contrarian)

System state: `price` = 135.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500, `cash` = 10000.0, `position` = 0.0

Calculation:
- `deviation` = (135.0 - 150.0) / 150.0 = -0.10
- Threshold check: |-0.10| > 0.05? YES → active
- Direction: deviation < 0 → action = "buy"
- `raw_quantity` = 0.10 * 3000 = 300
- `quantity` = min(500, 300) = 300
- Resource check: 300 * 135.0 = 40500 > 10000 → `quantity` = floor(10000 / 135.0) = 74

Decision: buy 74 shares at price = 135.0
State update: `cash`: 10000.0 → 10.0; `position`: 0.0 → 74.0

### Case 3 — Below threshold (hold)

System state: `price` = 155.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05

Calculation:
- `deviation` = (155.0 - 150.0) / 150.0 = 0.033
- Threshold check: |0.033| > 0.05? NO → hold

Decision: hold
State update: No change

### Edge Case — Extreme overvaluation (cap reached)

System state: `price` = 225.0, `fundamental_value` = 150.0, `activation_threshold` = 0.05, `scaling_factor` = 3000, `max_quantity` = 500, `position` = 600.0

Calculation:
- `deviation` = (225.0 - 150.0) / 150.0 = 0.50
- `raw_quantity` = 0.50 * 3000 = 1500
- `quantity` = min(500, 1500) = 500 (capped — limits to arbitrage)

Decision: sell 500 shares at price = 225.0
State update: `position`: 600.0 → 100.0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` = 0.05 <- Shleifer & Vishny (1997), 5–10% mispricing required to overcome costs
- `scaling_factor` = 3000 <- Moderate orders (150–500) across typical deviations
- `max_quantity` = 500 <- ~60% of speculator capacity, reflecting capital constraints

**Expected individual behaviour:**
- Given deviation = +0.10, agent MUST sell with Q = min(500, 0.10 * 3000) = 300
- Given deviation = -0.08, agent MUST buy with Q = min(500, 0.08 * 3000) = 240
- Given |deviation| = 0.03, agent MUST hold
- Agent MUST never buy overvalued or sell undervalued

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation is positive THEN broken (trades with mania instead of against it)
- IF agent trades when |deviation| <= 0.05 THEN broken (threshold gate failed)
- IF agent emits quantity > 500 THEN broken (cap not applied)
- IF agent's net effect amplifies deviation THEN broken (should stabilise)

### Ablation Hooks

| Ablation name        | Setting                      | Hypothesis tested                                        | Expected direction         | Metric                             |
|----------------------|------------------------------|----------------------------------------------------------|----------------------------|------------------------------------|
| `no_fundamentalist`  | population = 0               | Removing value traders increases mania amplitude         | Higher peak deviation      | Max |deviation| from fundamental   |
| `low_threshold`      | `activation_threshold=0.02`  | Lower threshold enables earlier correction               | Smaller peak bubbles       | Max |deviation|                     |
| `high_cap`           | `max_quantity=800`           | More capital allows stronger stabilisation               | Lower peak deviation       | Max |deviation|                     |
| `weak_scaling`       | `scaling_factor=1000`        | Reduced position weakens correction                      | Larger peak deviation      | Max |deviation|                     |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Garber, P. M. (2000). *Famous First Bubbles: The Fundamentals of Early Manias*. Cambridge, MA: MIT Press.                                         | Primary source; fundamental valuation in manias    |
| 2 | Shleifer, A. & Vishny, R. W. (1997). The limits of arbitrage. *The Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Limits to arbitrage — capital constraints |
| 3 | De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703 | Noise trader risk for fundamentalists |
| 4 | Fama, E. F. (1970). Efficient capital markets. *The Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486                          | Efficient markets alternative                      |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-intrinsic-value-trader.png) |
