# Fundamental Value Trader

## Summary

| Field                 | Content                                                                                                             |
|-----------------------|---------------------------------------------------------------------------------------------------------------------|
| Archetype             | Fundamental Value Trader                                                                                            |
| Theory Family         | Value Investing — Excess Volatility and Fundamental Anchoring                                                        |
| Behavioral Tendency   | **Converging** — pushes price toward fundamental value by buying undervalued assets and selling overvalued ones       |
| Time Horizon          | Medium-Long (waits for significant deviation before acting; holds through volatility)                                |
| Risk Tolerance        | Medium (willing to buy during crashes but size-constrained)                                                          |
| Information Asymmetry | Partial (observes both current price and fundamental value; no access to order flow or peer positions)               |
| Determinism           | Deterministic (given identical price, fundamental, and parameters, always produces the same order)                   |

## Definition and Goals

The fundamental value trader models informed participants who estimate the intrinsic value of an asset and trade contrarily when the market price deviates sufficiently from that estimate. In the real world, these correspond to value-oriented hedge funds, long-only fundamental managers, contrarian institutional investors, and corporate buyback programmes — any participant whose buy/sell decision is derived from comparing market price to a fundamental valuation anchor rather than from momentum or technical signals.

The agent's decision goal is to produce a signed order quantity proportional to the deviation between fundamental value and current price, activated only when the absolute deviation exceeds a configurable `value_threshold`. The quantity is computed as `deviation × base_position_size × value_sensitivity × value_multiplier`, clamped to [0, 50] for buys and [-30, 0] for sells. The agent always provides liquidity to the market.

The agent's behavioural role inside the simulation is to supply the stabilising recovery force: during a flash crash, as the price falls well below fundamental value, this agent begins buying aggressively, absorbing excess sell pressure and providing the demand that eventually arrests the decline and drives recovery. Non-goals: (1) the fundamental trader MUST NOT follow momentum or trends — it is purely mean-reverting relative to fundamental value; (2) it MUST NOT withdraw from the market under stress — unlike market makers, it always provides liquidity regardless of volatility conditions.

## Theoretical Foundation

**Excess Volatility and Fundamental Value Anchoring (Shiller 1981)**:
- Theory / Study: Do Stock Prices Move Too Much to Be Justified by Subsequent Changes in Dividends?
- Citation: Shiller, R. J. (1981). Do stock prices move too much to be justified by subsequent changes in dividends? *American Economic Review*, 71(3), 421–436. https://doi.org/10.1257/aer.71.3.421
- Core Insight: Stock prices exhibit excess volatility relative to the present value of future dividends, meaning that prices frequently deviate from fundamental value. Value-motivated traders who buy at deep discounts to fundamental value provide a gravitational anchoring force that limits the extent and duration of mispricings and drives eventual price recovery toward intrinsic value.
- Mathematical Formulation: `deviation = (fundamental - price) / fundamental; IF |deviation| > value_threshold THEN quantity = deviation × base_position_size × value_sensitivity × value_multiplier`.
- Empirical Evidence: Shiller (1981) documents that the variance of actual stock prices is 5–13 times the variance of the ex-post rational price (the discounted stream of subsequent dividends) for S&P 500 data 1871–1979, implying persistent mispricings (p. 427, Table 1). De Bondt & Thaler (1985, DOI: 10.1111/j.1540-6261.1985.tb05004.x) demonstrate mean-reversion of -25% for prior "losers" over 3–5 year horizons (t = 2.2), confirming value strategies exploit these deviations.
- Relevance to This Agent: The agent directly operationalises the fundamental-anchoring mechanism — it buys when price is significantly below fundamental and sells when above, with magnitude proportional to the deviation, providing the mean-reverting force that resolves flash-crash mispricings.
- Calibration Source: `value_threshold` in [0.03, 0.10] from Shiller's excess-volatility bounds (mispricings of 3–10% are typical before value traders act); `value_sensitivity` in [0.5, 2.0] from the range of value-strategy aggressiveness documented in practitioner literature.
- Falsification Conditions: If this agent holds (quantity = 0) for more than 5 consecutive rounds where |deviation| > value_threshold, the fundamental-anchoring mechanism is falsified. If the agent's order direction ever agrees with (rather than opposes) the direction of price movement away from fundamental, the design is violated.
- Alternative Theories: Rational expectations equilibrium (Grossman & Stiglitz 1980), adaptive markets hypothesis (Lo 2004), information-based trading (Kyle 1985).

## Design Purpose and Activation Triggers

Purpose: Provide stabilising mean-reverting demand by buying assets priced below fundamental value and selling those priced above, acting as the primary recovery force during flash crashes.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Undervaluation detected (deviation > value_threshold): Buy order proportional to deviation magnitude
- Overvaluation detected (deviation < -value_threshold): Sell order proportional to deviation magnitude
- Within dead zone (|deviation| <= value_threshold): Hold (quantity = 0)

Deactivation Conditions:
- Price returns within threshold band of fundamental: Agent naturally deactivates (hold)
- Cash exhaustion: Cannot buy further (constrained by _apply_constraints)
- Market closure / simulation end: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                       | Behavioral change                                              | Mechanism                                     |
|---------------------------------|----------------------------------------------------------------|-----------------------------------------------|
| Deep crash (large deviation)    | Much larger buy orders (deviation multiplies quantity linearly) | Proportional response: bigger gap → bigger buy |
| Normal market (small deviation) | Inactive; holds with zero quantity                             | Dead zone: |deviation| < threshold            |
| Overshoot recovery              | Begins selling if price overshoots above fundamental           | Symmetric: deviation < -threshold triggers sell |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, momentum signals, or order-book data needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source                     | Type / Shape | Required? | Notes                                           |
|---------------------|----------------------------|--------------|-----------|-------------------------------------------------|
| `price`             | Market coordinator payload | `float`      | yes       | Current asset price                             |
| `fundamental`       | Market coordinator payload | `float`      | yes       | Fundamental value broadcast by coordinator      |
| `round`             | Scheduler / round header   | `int`        | yes       | Current simulation round number                 |
| `value_threshold`   | Config extras              | `float`      | yes       | Minimum deviation to activate (§Parameters)     |
| `base_position_size`| Config extras              | `float`      | yes       | Base order magnitude (§Parameters)              |
| `value_sensitivity` | Config extras              | `float`      | yes       | Scaling factor for deviation signal (§Parameters) |
| `value_multiplier`  | Config extras              | `float`      | yes       | Final amplification factor (§Parameters)        |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                |
|-------------|--------|---------------------------|--------|-----------|----------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction derived from sign(deviation) |
| `bid_price` | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold   |
| `quantity`  | float  | [-30, 50]                 | shares | yes       | Signed order size (+ buy, - sell)      |
| `reasoning` | string | 1–2 sentences             | —      | yes       | Deviation % and resulting quantity      |

##### Content Constraints

- All four output fields MUST be present on every call.
- Buy quantity MUST be clamped to [0, 50]; sell quantity MUST be clamped to [-30, 0].
- `bid_price` MUST equal the current market price when trading; 0.0 when holding.
- Positive quantity = buy (price below fundamental); negative quantity = sell (price above fundamental).
- `provides_liquidity` in the outbound message envelope is always `True`.
- The agent is deterministic given the same price, fundamental, and parameters.

##### Serialization Format

```
<analysis>Deviation = (fundamental - price) / fundamental = {deviation:.2%}; threshold = {value_threshold}. {action_rationale}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <float>, "reasoning": "Fundamental: {deviation:.2%} deviation from value."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. The `provides_liquidity` field in the outbound message envelope is always `True`.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                           |
|---------------|------------|---------------|-----------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation from fundamental   |
| `fundamental` | Continuous | Current tick  | Anchor value against which mispricing is measured   |

Does NOT use: price history, momentum signals, peer positions, volume data, net demand, liquidity levels — the agent reacts only to the current price-vs-fundamental gap.

#### Core Behavioral Mechanism

```
Step 1 — Read inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  deviation = (fundamental - price) / fundamental
  (Traces to: Excess Volatility, Shiller 1981)

Step 3 — Evaluate activation threshold:
  Read: value_threshold
  IF deviation > value_threshold: → Buy branch (Step 4a)
  ELIF deviation < -value_threshold: → Sell branch (Step 4b)
  ELSE: → Hold branch (Step 4c)

Step 4a — Buy branch:
  Read: base_position_size, value_sensitivity, value_multiplier
  raw_quantity = deviation × base_position_size × value_sensitivity × value_multiplier
  quantity = clamp(raw_quantity, 0, 50)
  bid_price = price; action = "buy"

Step 4b — Sell branch:
  raw_quantity = deviation × base_position_size × value_sensitivity × value_multiplier
  quantity = clamp(raw_quantity, -30, 0)
  bid_price = price; action = "sell"

Step 4c — Hold branch:
  quantity = 0.0; bid_price = 0.0; action = "hold"

Step 5 — Apply resource constraints:
  quantity = _apply_constraints(bid_price, quantity)

Step 6 — Execute trade (post-decision):
  IF quantity > 0: Write: cash -= quantity × bid_price; Write: position += quantity
  ELIF quantity < 0: Write: cash += abs(quantity) × bid_price; Write: position += quantity
```

#### Action Space

| Aspect                | Specification                                                                                   |
|-----------------------|-------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                           |
| Action parameter rule | `bid_price` = current market price (no limit orders; agent is a price-taker)                    |
| Sizing rule           | `quantity = clamp(deviation × base_position_size × value_sensitivity × value_multiplier, -30, 50)` |
| Action lifetime       | Immediate execution; no persistent resting orders                                               |
| Revision policy       | No revision — each round's order is independent; previous orders are not amended                |
| State constraint      | No self-imposed cumulative position limit at agent level                                        |
| Resource cap          | Cash constraint applied via `_apply_constraints` (cannot buy more than cash allows)             |
| Exit rule             | None — agent continues to trade every round as long as deviation exceeds threshold              |

#### Mathematical Model

**Decision output:** Signed quantity (float in [-30, 50]) representing the directional order to submit this round.

**Decision logic formalization:**

```
Step 1 — Read inputs:
  Read: price from market_data
  Read: fundamental from market_data

Step 2 — Compute deviation:
  deviation = (fundamental - price) / fundamental

Step 3 — Evaluate activation threshold:
  IF deviation > value_threshold:
    → Buy branch (Step 4a)
  ELIF deviation < -value_threshold:
    → Sell branch (Step 4b)
  ELSE:
    → Hold branch (Step 4c)

Step 4a — Buy branch:
  raw_quantity = deviation * base_position_size * value_sensitivity * value_multiplier
  quantity = clamp(raw_quantity, 0, 50)
  bid_price = price
  action = "buy"

Step 4b — Sell branch:
  raw_quantity = deviation * base_position_size * value_sensitivity * value_multiplier
  quantity = clamp(raw_quantity, -30, 0)
  bid_price = price
  action = "sell"

Step 4c — Hold branch:
  quantity = 0.0
  bid_price = 0.0
  action = "hold"

Step 5 — Apply resource constraints:
  quantity = _apply_constraints(bid_price, quantity)

Step 6 — Execute trade:
  IF quantity > 0: cash -= quantity * bid_price; position += quantity
  ELIF quantity < 0: cash += abs(quantity) * bid_price; position += quantity
```

**State variables:**
- `position`: Running tally of net shares held (updated by `_execute_trade` post-decision).
- `cash`: Running cash balance (updated by `_execute_trade` post-decision).
- `price_history`: Append-only list of observed prices (maintained by base class, not consumed by this agent's decision logic).

**State evolution:**
- `price_history`: Updated pre-decide (during `perceive`).
- `position` and `cash`: Updated post-decide (during `_execute_trade`).

**Determinism contract:** Fully deterministic given identical price, fundamental, and parameter values.

**Parameter symbol table:**

| Symbol              | Meaning                                    | Default Value | Source                      |
|---------------------|--------------------------------------------|---------------|-----------------------------|
| `value_threshold`   | Minimum deviation to activate trading      | 0.10          | Shiller (1981)              |
| `base_position_size`| Base order magnitude                       | 30.0          | simulation-bases.md §4.5    |
| `value_sensitivity` | Scaling factor for deviation signal        | 1.0           | simulation-bases.md §4.5    |
| `value_multiplier`  | Final amplification factor                 | 10            | simulation-bases.md §4.5    |

#### Behavioral Properties

- Time horizon: Medium-Long — waits for significant deviation (>10% default) before acting; holds through short-term volatility; recovery horizon measured in tens of rounds.
- Risk tolerance: Medium — willing to buy aggressively during crashes (up to 50 shares/round) but size-constrained by clamp and cash; does not lever.
- Information asymmetry: Partial — observes both current price and fundamental value (broadcast by coordinator); no access to order flow, peer positions, or momentum signals.
- Psychological profile: Rational value anchor (Shiller 1981) — no trend-following bias, no disposition effect, no panic response; acts purely on mispricing magnitude relative to a known reference value.

## Parameters

| Parameter           | Type  | Default | Valid Range  | Sensitivity | Description                                       | Impact                                              | Source                          |
|---------------------|-------|---------|--------------|-------------|---------------------------------------------------|-----------------------------------------------------|---------------------------------|
| `value_threshold`   | float | 0.10    | [0.03, 0.10] | High        | Minimum deviation from fundamental to trigger     | Higher → fewer trades, later intervention           | Shiller (1981)                  |
| `base_position_size`| float | 30.0    | [15.0, 50.0] | High        | Base order magnitude before deviation scaling     | Higher → proportionally larger order quantities     | simulation-bases.md §4.5        |
| `value_sensitivity` | float | 1.0     | [0.5, 2.0]   | Medium      | Responsiveness to deviation signal                | Higher → proportionally larger order quantities     | simulation-bases.md §4.5        |
| `value_multiplier`  | float | 10.0    | [5.0, 15.0]  | High        | Final amplification factor for quantity           | Higher → proportionally larger order quantities     | simulation-bases.md §4.5        |

## Worked Numerical Examples

### Case 1 — Moderate undervaluation (buy signal)

System state: `price` = 88.0, `fundamental` = 100.0, `value_threshold` = 0.10, `base_position_size` = 30.0, `value_sensitivity` = 1.0, `value_multiplier` = 10

Calculation:
- `deviation` = (100.0 - 88.0) / 100.0 = 0.12
- Threshold check: 0.12 > 0.10? YES → buy branch
- `raw_quantity` = 0.12 × 30.0 × 1.0 × 10 = 36.0
- `quantity` = clamp(36.0, 0, 50) = 36.0

Decision: buy 36.0 shares at bid_price = 88.0
State update: `cash`: 10000.0 → 10000.0 - 36.0 × 88.0 = 6832.0; `position`: 0 → 36.0

### Case 2 — Deep crash (large undervaluation)

System state: `price` = 70.0, `fundamental` = 100.0, `value_threshold` = 0.10, `base_position_size` = 30.0, `value_sensitivity` = 1.0, `value_multiplier` = 10

Calculation:
- `deviation` = (100.0 - 70.0) / 100.0 = 0.30
- Threshold check: 0.30 > 0.10? YES → buy branch
- `raw_quantity` = 0.30 × 30.0 × 1.0 × 10 = 90.0
- `quantity` = clamp(90.0, 0, 50) = 50.0 (clamped)

Decision: buy 50.0 shares at bid_price = 70.0
State update: `cash`: 10000.0 → 10000.0 - 50.0 × 70.0 = 6500.0; `position`: 0 → 50.0

### Case 3 — Overvaluation (sell signal)

System state: `price` = 115.0, `fundamental` = 100.0, `value_threshold` = 0.10, `base_position_size` = 30.0, `value_sensitivity` = 1.0, `value_multiplier` = 10, `position` = 30.0

Calculation:
- `deviation` = (100.0 - 115.0) / 100.0 = -0.15
- Threshold check: -0.15 < -0.10? YES → sell branch
- `raw_quantity` = -0.15 × 30.0 × 1.0 × 10 = -45.0
- `quantity` = clamp(-45.0, -30, 0) = -30.0 (clamped)

Decision: sell 30.0 shares at bid_price = 115.0
State update: `cash`: 10000.0 → 10000.0 + 30.0 × 115.0 = 13450.0; `position`: 30.0 → 0.0

### Edge Case — Within dead zone (no trade)

System state: `price` = 95.0, `fundamental` = 100.0, `value_threshold` = 0.10, `base_position_size` = 30.0, `value_sensitivity` = 1.0, `value_multiplier` = 10

Calculation:
- `deviation` = (100.0 - 95.0) / 100.0 = 0.05
- Threshold check: 0.05 > 0.10? NO; -0.05 < -0.10? NO → hold branch
- `quantity` = 0.0, `bid_price` = 0.0

Decision: hold
State update: No change

## Behavioral Verification and Calibration

**Verification criteria:**
1. When deviation > value_threshold, the agent MUST emit a positive (buy) quantity proportional to the deviation magnitude.
2. When deviation < -value_threshold, the agent MUST emit a negative (sell) quantity proportional to the deviation magnitude.
3. When |deviation| <= value_threshold, the agent MUST emit quantity = 0 (hold).
4. The agent MUST never emit buy quantity > 50 or sell quantity < -30.
5. The agent's `provides_liquidity` flag MUST always be `True`.
6. Given identical inputs across two runs, the agent MUST produce byte-identical outputs (determinism test).

**Calibration procedure:**
- Set `value_threshold` = 0.10, `base_position_size` = 30.0, `value_sensitivity` = 1.0, `value_multiplier` = 10.
- Run 200-round flash-crash simulation. Verify agent begins buying only after price drops >10% below fundamental.
- Verify agent's net buying volume during crash trough exceeds its selling volume during normal periods by at least 5:1.
- Sensitivity sweep: vary `value_threshold` in {0.03, 0.05, 0.08, 0.10} and confirm that lower thresholds produce earlier intervention and shallower crash troughs.

**Ablation Hooks:**

| Ablation name          | Setting                  | Hypothesis tested                                       | Expected direction                      | Metric              |
|------------------------|--------------------------|---------------------------------------------------------|-----------------------------------------|---------------------|
| `disable_fundamental`  | `value_sensitivity = 0`  | Fundamental traders are necessary for price recovery    | No recovery; price stays depressed      | `recovery_speed`    |
| `aggressive_value`     | `value_threshold = 0.03` | Earlier intervention limits crash depth                 | Shallower crash trough                  | `crash_depth`       |
| `passive_value`        | `value_threshold = 0.10` | Late intervention allows deeper crash before recovery   | Deeper trough but still recovers        | `max_drawdown`      |

## Academic References

| # | Citation                                                                                                                                                                    | Notes                                         |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 1 | Shiller, R. J. (1981). Do stock prices move too much to be justified by subsequent changes in dividends? *American Economic Review*, 71(3), 421–436. https://doi.org/10.1257/aer.71.3.421 | Primary theory; excess volatility and fundamental anchoring |
| 2 | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x        | Empirical evidence for mean-reversion profits |
| 3 | Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498 | Flash crash context; fundamental traders drive recovery |

## Design Provenance

| Field       | Content                                                          |
|-------------|------------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                       |
| Created     | 2026-07-11                                                       |
| Version     | 1.0.0                                                            |
| Status      | canonical                                                        |
| Icon        | ![](../agent_images/icons/finance-fundamental-trader.png)        |
