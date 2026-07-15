# Opportunity Cost Trader

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Opportunity Cost Trader                                                                                              |
| Theory Family         | Opportunity Cost Theory — Capital Reallocation — Rational Portfolio Choice                                           |
| Behavioral Tendency   | **Converging** — reallocates capital from overvalued to undervalued assets, pushing prices toward fundamental value    |
| Time Horizon          | Medium (acts selectively, only when opportunity cost of inaction is large)                                            |
| Risk Tolerance        | Medium (moderate position sizes; patient but decisive when threshold crossed)                                         |
| Information Asymmetry | None (uses publicly available fundamental value)                                                                     |
| Determinism           | Deterministic (given identical deviation signal and parameters, always produces the same order)                       |

## Definition and Goals

The opportunity cost trader models investors who recognise that holding a mispriced asset imposes an opportunity cost — capital tied up in an overvalued position could earn higher returns elsewhere, while cash held during undervaluation misses cheap entry points. Unlike the commitment escalator who ignores opportunity costs and doubles down, this agent explicitly computes the implicit cost of inaction and trades when that cost exceeds a threshold. In real-world markets, these correspond to portfolio managers with formal opportunity-cost budgeting, asset allocators comparing cross-sectional expected returns, endowment CIOs optimising across alternative investments, private equity GPs evaluating redeployment, institutional investors with capital-efficiency mandates, and treasury managers optimising working capital allocation.

The agent's decision goal is to detect mispricing and reallocate capital when |deviation| exceeds a relatively high realloc_threshold (0.08). The higher threshold (vs 0.05 for rational-cutter) reflects that opportunity cost calculations require larger mispricings to overcome informational and computational costs. Quantity is computed as `position_size * |deviation| / realloc_threshold`. Direction is contrarian: sell overvalued, buy undervalued.

The agent's behavioural role inside the simulation is to provide selective price correction — acting less frequently than the rational cutter but with the same directional logic, it represents the intermediate case between full rationality and complete inertia. Non-goals: (1) the opportunity cost trader MUST NOT trade at small deviations (threshold = 0.08 is intentionally higher than the rational cutter's 0.05); (2) the opportunity cost trader MUST NOT exhibit sunk cost bias or escalation of commitment.

## Theoretical Foundation

**Opportunity Cost and Capital Reallocation (Buchanan 1969; Markowitz 1952)**:
- Theory / Study: Cost and Choice / Portfolio Selection
- Citation: Buchanan, J. M. (1969). *Cost and Choice: An Inquiry in Economic Theory*. Chicago: Markham Publishing; Markowitz, H. (1952). Portfolio selection. *The Journal of Finance*, 7(1), 77–91. https://doi.org/10.2307/2975974
- Core Insight: The true cost of any action is the value of the best forgone alternative. In portfolio management, holding an overvalued asset imposes an opportunity cost equal to the expected return that capital could earn if deployed to an undervalued opportunity. Rational capital reallocation occurs when the opportunity cost of the status quo exceeds the transaction costs of switching. This creates a threshold-based reallocation mechanism where the threshold is determined by the magnitude of forgone returns.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; opportunity_cost = |deviation| * capital_at_risk; if opportunity_cost justifies action (|deviation| > realloc_threshold): quantity = position_size * |deviation| / realloc_threshold; direction = -sign(deviation)`
- Empirical Evidence: Buchanan (1969) establishes the theoretical framework for opportunity cost in decision-making. Empirical work by Chen, Hong & Stein (2002, *Journal of Financial Economics*) shows that mutual fund managers reallocate capital when expected return differentials exceed 6–10% (Table 3, p. 183), consistent with a reallocation threshold of 0.06–0.10. Portfolio turnover data from Morningstar shows that the median active fund has turnover of 60–80% per year, with rebalancing triggered by valuation gaps of 8–12%.
- Relevance to This Agent: The agent operationalises opportunity cost through a higher activation threshold (0.08 vs 0.05) that represents the computational and informational costs of opportunity-cost assessment. Once triggered, it trades at full strength contrarian to deviation.
- Calibration Source: `realloc_threshold` = 0.08 from Chen, Hong & Stein (2002) Table 3, where institutional reallocation is triggered by expected return differentials of 6–10%; `position_size` = 300 reflecting moderate capital allocation per rebalancing event.
- Falsification Conditions: If this agent trades at deviations below 0.08, the opportunity-cost threshold is not functioning. If the agent holds when deviation exceeds 0.15 (clear opportunity cost), the mechanism is broken.
- Alternative Theories: Sunk cost models (Staw 1976) predict holding regardless of opportunity cost; rational inattention (Sims 2003) provides an alternative explanation for threshold-based action through information processing costs.

## Design Purpose and Activation Triggers

Purpose: Demonstrate selective capital reallocation based on opportunity cost assessment — trades less frequently than the rational cutter but with the same contrarian logic when the cost of inaction becomes substantial.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value estimate available (from environment or scenario)
- Agent's own position and cash state available

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation exceeds threshold (deviation > 0.08): SELL — high opportunity cost of holding overvalued asset
- Negative deviation exceeds threshold (deviation < -0.08): BUY — high opportunity cost of missing undervalued entry
- Default (|deviation| <= 0.08): HOLD — opportunity cost below action threshold

Deactivation Conditions:
- Cash exhaustion: Cannot buy further
- Zero position when sell signal fires: Cannot sell
- Fundamental value signal lost: Agent holds

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                         | Mechanism                                              |
|------------------------------|-----------------------------------------------------------|--------------------------------------------------------|
| Small deviation (<=0.08)     | No action — opportunity cost below threshold              | Higher threshold than rational cutter (0.08 vs 0.05)   |
| Moderate deviation (0.08–0.20)| Contrarian trading at full strength                      | Linear: Q = position_size * |dev| / threshold          |
| Large deviation (>0.20)      | Larger contrarian positions — high opportunity cost       | Linear scaling continues                               |

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
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Contrarian direction toward fundamental          |
| `price`     | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold             |
| `quantity`  | float  | [0, 1200]                 | shares | yes       | Unsigned order size                              |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Opportunity cost rationale, deviation level      |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is unsigned; direction is encoded in `action` field.
- `price` MUST equal the current market price when trading; 0.0 when holding.
- The agent is deterministic given the same price, fundamental_value, and parameters.
- Higher threshold than rational cutter — trades less frequently.

##### Serialization Format

```
<analysis>Deviation = {deviation:.4f} ({deviation:.2%} from fundamental); realloc_threshold = {realloc_threshold}; opportunity cost {'justifies action' if |deviation| > threshold else 'below threshold'}; computed quantity = {quantity:.1f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "price": <float>, "quantity": <float>, "reasoning": "Opportunity-cost-trader: deviation {deviation:.2%}, opportunity cost {'high — reallocating' if acted else 'acceptable — holding'}, qty={quantity:.0f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the opportunity-cost formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM MUST preserve the contrarian direction and respect the higher threshold. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal              | Type       | Memory Window | Rationale                                                              |
|---------------------|------------|---------------|------------------------------------------------------------------------|
| `price`             | Continuous | Current tick  | Required for computing deviation and opportunity cost                   |
| `fundamental_value` | Continuous | Current tick  | Reference value for determining forgone-return magnitude               |
| `position`          | Continuous | Persisted     | Capital at risk in current holding                                     |
| `cash`              | Continuous | Persisted     | Available capital for reallocation                                     |

Does NOT use: sunk cost information, entry prices, peer behaviour, momentum signals, order book — focuses solely on forward-looking opportunity cost derived from deviation.

#### Core Behavioral Mechanism

Step 1 — Read fundamental value and current price:
  Read: `price`, `fundamental_value`
  (Theory trace: Buchanan 1969 — opportunity cost assessment requires comparing alternatives)

Step 2 — Compute deviation signal:
  `deviation = (price - fundamental_value) / fundamental_value`
  (Theory trace: deviation magnitude represents the opportunity cost of inaction)

Step 3 — Evaluate reallocation threshold:
  Read: `realloc_threshold`
  IF `|deviation| <= realloc_threshold`: set quantity = 0, action = "hold" → RETURN
  (Theory trace: Buchanan 1969 — action only justified when opportunity cost exceeds switching costs)

Step 4 — Determine contrarian direction:
  IF `deviation > 0`: action = "sell" (overvalued — capital better deployed elsewhere)
  ELIF `deviation < 0`: action = "buy" (undervalued — capture mispriced opportunity)
  (Theory trace: Markowitz 1952 — reallocate toward highest expected return)

Step 5 — Compute quantity:
  Read: `position_size`
  `quantity = position_size * |deviation| / realloc_threshold`
  (Theory trace: position proportional to opportunity cost magnitude)

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
| Sizing rule           | `quantity = position_size * |deviation| / realloc_threshold`                          |
| Action lifetime       | Immediate execution; no persistent resting orders                                     |
| Revision policy       | No revision — each round's order is independent                                       |
| State constraint      | Position >= 0 (no naked shorting; can only sell what is held)                         |
| Resource cap          | Cash constraint: cannot buy more than cash / price allows                             |
| Exit rule             | None — agent trades when opportunity cost exceeds threshold                           |

#### Mathematical Model

**Decision output:** Unsigned quantity (float, no hard cap beyond resources) plus direction (buy/sell/hold enum).

**Decision logic formalization:**

```
Given: price, fundamental_value, realloc_threshold, position_size

Step 1 — Compute deviation:
  deviation = (price - fundamental_value) / fundamental_value

Step 2 — Activation gate:
  IF abs(deviation) <= realloc_threshold:
    action = "hold"
    quantity = 0.0
    → RETURN

Step 3 — Contrarian direction:
  IF deviation > 0: action = "sell"
  ELSE: action = "buy"

Step 4 — Quantity:
  quantity = position_size * abs(deviation) / realloc_threshold

Step 5 — Resource constraint:
  IF action == "buy": quantity = min(quantity, floor(cash / price))
  IF action == "sell": quantity = min(quantity, position)

Step 6 — State update:
  IF action == "buy": cash -= quantity * price; position += quantity
  IF action == "sell": cash += quantity * price; position -= quantity
```

**State variables:**
- `position`: float, initial value = 50. Net shares held.
- `cash`: float, initial value = 10000.0. Available capital.

**State evolution:**
- `position`: Updated post-decide (increases on buy, decreases on sell).
- `cash`: Updated post-decide (decreases on buy, increases on sell).

**Determinism contract:** Fully deterministic given identical price, fundamental_value, position, cash, and parameter values. No stochastic components.

**Parameter symbol table:**

| Symbol              | Meaning                                     | Default Value | Source                     |
|---------------------|---------------------------------------------|---------------|----------------------------|
| `realloc_threshold` | Minimum |deviation| to justify reallocation | 0.08          | Buchanan (1969); Chen et al. (2002) |
| `position_size`     | Base multiplier for quantity                | 300           | Simulation design          |

#### Behavioral Properties

- **Time horizon:** Medium (acts selectively; waits for larger deviations than the rational cutter before committing)
- **Risk tolerance:** Medium (moderate position sizes; patient approach to capital deployment)
- **Information asymmetry:** None (uses publicly available fundamental value; opportunity cost calculation is available to all)
- **Psychological profile:** Opportunity-cost aware — explicitly weighs the cost of inaction; no sunk cost bias; acts as an intermediate between full-frequency rational rebalancing and biased inertia

## Parameters

| Parameter           | Type  | Default | Valid Range   | Sensitivity | Description                                                     | Impact                                                    | Source                          |
|---------------------|-------|---------|---------------|-------------|-----------------------------------------------------------------|-----------------------------------------------------------|---------------------------------|
| `realloc_threshold` | float | 0.08    | [0.03, 0.20]  | High        | Minimum absolute deviation to justify capital reallocation      | Higher → fewer trades, more capital locked in mispricing   | Buchanan (1969); Chen et al.    |
| `position_size`     | float | 300     | [100, 800]    | High        | Base multiplier for quantity calculation                         | Higher → larger positions for same deviation              | Simulation design               |
| `initial_cash`      | float | 10000.0 | [5000, 50000] | Low         | Starting cash endowment                                          | Higher → more reallocation capacity                       | Normalisation                   |
| `initial_position`  | float | 50.0    | [0, 200]      | Medium      | Starting inventory of shares                                     | Higher → more capacity for sell-side reallocation         | Simulation design               |

## Worked Numerical Examples

### Case 1 — Large overvaluation (sell — opportunity cost high)

System state: `price` = 168.0, `fundamental_value` = 150.0, `realloc_threshold` = 0.08, `position_size` = 300, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (168.0 - 150.0) / 150.0 = 0.12
- Threshold check: |0.12| > 0.08? YES → active
- Direction: deviation > 0 → action = "sell"
- `quantity` = 300 * 0.12 / 0.08 = 450
- Resource check: 450 > position (50) → `quantity` = 50

Decision: sell 50 shares at price = 168.0
State update: `cash`: 10000.0 → 18400.0; `position`: 50.0 → 0.0

### Case 2 — Large undervaluation (buy — opportunity cost of missing cheap entry)

System state: `price` = 132.0, `fundamental_value` = 150.0, `realloc_threshold` = 0.08, `position_size` = 300, `cash` = 10000.0, `position` = 50.0

Calculation:
- `deviation` = (132.0 - 150.0) / 150.0 = -0.12
- Threshold check: |-0.12| > 0.08? YES → active
- Direction: deviation < 0 → action = "buy"
- `quantity` = 300 * 0.12 / 0.08 = 450
- Resource check: 450 * 132.0 = 59400 > 10000 → `quantity` = floor(10000 / 132.0) = 75

Decision: buy 75 shares at price = 132.0
State update: `cash`: 10000.0 → 100.0; `position`: 50.0 → 125.0

### Case 3 — Moderate deviation (hold — opportunity cost below threshold)

System state: `price` = 159.0, `fundamental_value` = 150.0, `realloc_threshold` = 0.08

Calculation:
- `deviation` = (159.0 - 150.0) / 150.0 = 0.06
- Threshold check: |0.06| > 0.08? NO → hold

Decision: hold
State update: No change

### Edge Case — Deviation at threshold boundary

System state: `price` = 162.0, `fundamental_value` = 150.0, `realloc_threshold` = 0.08

Calculation:
- `deviation` = (162.0 - 150.0) / 150.0 = 0.08
- Threshold check: |0.08| > 0.08? NO (equal, not exceeded) → hold

Decision: hold
State update: No change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `realloc_threshold` = 0.08 <- Chen, Hong & Stein (2002) Table 3, institutional reallocation triggered at 6–10% expected return differentials
- `position_size` = 300 <- Calibrated for moderate orders (300–750) across typical deviation range

**Expected individual behaviour:**
- Given deviation = +0.12, agent MUST sell with Q = 300 * 0.12 / 0.08 = 450 (subject to position)
- Given deviation = -0.10, agent MUST buy with Q = 300 * 0.10 / 0.08 = 375 (subject to cash)
- Given |deviation| = 0.06 (below 0.08), agent MUST hold
- Agent MUST trade less frequently than rational-cutter (higher threshold) but with same direction

**Sanity bounds (red flags indicating broken implementation):**
- IF agent trades when |deviation| <= 0.08 THEN broken (threshold gate failed)
- IF agent buys overvalued or sells undervalued THEN broken (contrarian direction violated)
- IF agent trades at same frequency as rational-cutter (threshold 0.05) THEN broken (threshold distinction lost)
- IF agent exhibits sunk-cost-driven behaviour THEN broken (forward-looking only)

### Ablation Hooks

| Ablation name         | Setting                      | Hypothesis tested                                           | Expected direction         | Metric                              |
|-----------------------|------------------------------|-------------------------------------------------------------|----------------------------|--------------------------------------|
| `no_opportunity`      | population = 0               | Removing OC trader increases mispricing persistence          | Longer mispricing          | Rounds to correct 10% deviation     |
| `low_threshold`       | `realloc_threshold=0.05`     | Lower threshold makes agent identical to rational cutter    | More frequent trading      | Trade count per 50 rounds            |
| `high_threshold`      | `realloc_threshold=0.15`     | Higher threshold reduces correction frequency               | Larger peak deviations     | Max |deviation|                      |
| `vs_rational_cutter`  | Compare threshold 0.08 vs 0.05 | Opportunity cost friction vs pure rationality             | OC agent trades less often | Relative trade frequency             |

## Academic References

| # | Citation                                                                                                                                           | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Buchanan, J. M. (1969). *Cost and Choice: An Inquiry in Economic Theory*. Chicago: Markham Publishing.                                            | Primary theory — opportunity cost framework        |
| 2 | Markowitz, H. (1952). Portfolio selection. *The Journal of Finance*, 7(1), 77–91. https://doi.org/10.2307/2975974                                  | Rational portfolio choice foundation               |
| 3 | Chen, J., Hong, H. & Stein, J. C. (2002). Breadth of ownership and stock returns. *Journal of Financial Economics*, 66(2–3), 171–205. https://doi.org/10.1016/S0304-405X(02)00223-4 | Empirical reallocation thresholds |
| 4 | Sims, C. A. (2003). Implications of rational inattention. *Journal of Monetary Economics*, 50(3), 665–690. https://doi.org/10.1016/S0304-3932(03)00029-1 | Alternative theory for threshold-based action |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-opportunity-cost-trader.png) |
