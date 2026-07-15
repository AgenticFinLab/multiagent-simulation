# Leverage Trader

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Leverage Trader                                                                                                      |
| Theory Family         | Market Microstructure — Leverage Cycles and Balance-Sheet Constraints                                                |
| Behavioral Tendency   | **Adaptive** — buys convergence normally but forced-sells under equity erosion (margin call channel)                  |
| Time Horizon          | Medium (holds leveraged positions; forced to liquidate under stress)                                                  |
| Risk Tolerance        | High (operates at 25x leverage; willing to accept extreme concentration until margin forces action)                  |
| Information Asymmetry | Partial (observes own equity/leverage state and market price; no peer positions or systemic stress indicators)        |
| Determinism           | Deterministic (given identical inputs and parameters, always produces the same order)                                |

## Definition and Goals

The leverage trader models balance-sheet-constrained institutional investors who normally buy undervalued assets with leverage but are forced to deleverage when equity erodes past margin thresholds. This captures the leverage-cycle channel documented by Geanakoplos (2010): during calm periods, leverage expands and funds buy aggressively; during stress, equity losses trigger margin calls that force pro-cyclical selling, amplifying downturns. In the real world, these correspond to leveraged hedge funds, proprietary trading desks with capital constraints, prime-brokered accounts facing margin requirements, collateralised lending vehicles, and leveraged ETFs with rebalancing mandates.

The agent's decision goal is adaptive: (1) under normal equity conditions and negative deviation > 3%, it buys with leveraged capital to exploit the discount; (2) when equity drops below the margin_call_threshold relative to position exposure, it is forced to sell 30% of its position regardless of price — modelling the involuntary deleveraging that converts rational convergence traders into procyclical sellers during crises.

The agent's behavioural role inside the simulation is to demonstrate the leverage-cycle dynamic: individually rational convergence trading that transforms into destabilising forced selling under stress. Non-goals: (1) the agent MUST NOT ignore margin pressure — forced selling is the central mechanism, not optional; (2) the agent MUST NOT sell voluntarily when equity is healthy and deviation is negative — it believes in convergence during normal times.

## Theoretical Foundation

**Leverage Cycles (Geanakoplos 2010)**:
- Theory / Study: The Leverage Cycle
- Citation: Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1–65. https://doi.org/10.1086/648285
- Core Insight: Leverage is procyclical: it increases during booms (as collateral values rise) and contracts violently during busts (as collateral values fall and margin calls cascade). This creates a positive feedback loop — falling prices erode equity, triggering forced sales that further depress prices, which triggers more margin calls.
- Mathematical Formulation: `equity = cash + position * price; leverage_exposure = |position * price| / leverage_ratio; IF equity < leverage_exposure * margin_call_threshold: forced_sell = int(position * 0.30)`
- Empirical Evidence: Geanakoplos (2010, Section 4) documents that leverage in the US mortgage market expanded from 10:1 to 20:1 during 2003–2006, then contracted to 5:1 during 2007–2009, with the contraction phase causing 30–50% forced asset sales across the financial system.
- Relevance to This Agent: The agent directly models the leverage cycle's deleveraging phase — when equity falls below margin thresholds, it is forced to sell 30% of position irrespective of its convergence view, creating procyclical selling pressure during crises.
- Calibration Source: `leverage_ratio` = 25 from Geanakoplos (2010, Table 3): peak leverage ratios 20–30x in mortgage-backed securities. `margin_call_threshold` = 0.04 from Adrian & Shin (2010, Table 1): margin calls triggered at 3–5% equity deterioration.
- Falsification Conditions: If this agent continues buying when its equity ratio is below the margin_call_threshold, the forced-selling mechanism is falsified. If the agent force-sells when equity is healthy (above threshold), the margin logic is broken.
- Alternative Theories: Rational deleveraging (Miller 1977), fire-sale externalities (Shleifer & Vishny 1992), bank run dynamics (Diamond & Dybvig 1983).

**Margin Spirals (Brunnermeier & Pedersen 2009)**:
- Theory / Study: Market Liquidity and Funding Liquidity
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
- Core Insight: There is a reinforcing loop between market liquidity and funding liquidity: when asset prices fall, margins increase, forcing leveraged traders to reduce positions, which further depresses prices and triggers additional margin calls. This "liquidity spiral" explains why small shocks can cascade into large market dislocations.
- Mathematical Formulation: `margin_spiral_condition: IF price_decline > threshold THEN margin_increase → forced_liquidation → further_price_decline`
- Empirical Evidence: Brunnermeier & Pedersen (2009, Figure 2) document that the bid-ask spread for S&P 500 futures widened by 400% during LTCM crisis (August–October 1998), consistent with forced liquidation by leveraged traders consuming market liquidity.
- Relevance to This Agent: The 30% forced-sell rule under margin stress directly creates the selling pressure that drives the liquidity spiral — when this agent (and others like it) sell simultaneously, they depress prices further, potentially triggering more margin calls across the system.
- Calibration Source: Brunnermeier & Pedersen (2009, Section 4): forced liquidation fractions of 20–50% of position; default 30%. Adrian & Shin (2010, DOI:10.1016/j.jfi.2008.12.002): leverage targeting by financial intermediaries adjusts at 25–50% of position per quarter.
- Falsification Conditions: If the agent never force-sells during a period where its equity has breached the margin threshold, the margin spiral channel is non-functional. If forced selling stops after one round despite continued equity breach, the persistence of deleveraging is absent.
- Alternative Theories: Voluntary risk reduction (VaR targeting), panic selling (behavioural), rational portfolio insurance (Leland 1980).

## Design Purpose and Activation Triggers

Purpose: Demonstrate the leverage-cycle channel by buying with leverage during normal conditions and force-selling under equity stress, capturing the procyclical deleveraging dynamic.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action) unless margin call is triggered (which depends only on price and position). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Margin call triggered (equity < exposure * margin_call_threshold): FORCED SELL 30% of position — involuntary deleveraging
- Normal condition AND negative deviation > 3% (deviation < -0.03): BUY — leveraged convergence trade
- Default (no margin call AND |deviation| <= 0.03 OR deviation > 0): Hold — no trading opportunity or overvaluation

Deactivation Conditions:
- Position reduced to zero: No further forced selling possible
- Cash depleted: Cannot buy further
- Price returns to fundamental: Normal convergence buying ceases

Behavioral Adaptation by Condition:
| Condition                         | Behavioral change                                                   | Mechanism                                                         |
|-----------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------|
| Equity stress (margin breached)   | Involuntary selling of 30% of position; overrides convergence logic  | Margin call → forced liquidation regardless of view               |
| Normal equity, price below fund.  | Buys with leveraged capital; standard convergence trading             | Leveraged buying when spread exceeds 3%                           |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No external margin-call signals needed — the agent self-computes its equity constraint.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                 | Source                      | Type / Shape | Required?               | Notes                                                    |
|-----------------------|-----------------------------|--------------|-------------------------|----------------------------------------------------------|
| `price`               | Market coordinator payload  | `float`      | yes                     | Current asset price; maps to §Decision Information Set   |
| `fundamental`         | Market coordinator payload  | `float`      | yes                     | Fundamental value broadcast by coordinator               |
| `cash`                | Agent's own persisted state | `float`      | yes                     | Current cash balance; populated by §Mathematical Model   |
| `position`            | Agent's own persisted state | `int`        | yes                     | Current share position; populated by §Mathematical Model |
| `round`               | Scheduler / round header    | `int`        | yes                     | Current simulation round number                          |
| `agent_id`            | Scheduler / round header    | `str`        | yes                     | Agent identity string                                    |
| `retrieved_knowledge` | Retrieval store             | `list[str]`  | retrieval variants only | Falls back to sentinel if empty                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                           |
|-------------|--------|---------------------------|--------|-----------|---------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction: buy (convergence) or sell (forced)       |
| `quantity`  | int    | [0, max_position]         | shares | yes       | Unsigned order size                                |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Margin status and trade rationale                  |

##### Content Constraints

- All three output fields MUST be present on every call.
- `quantity` MUST be non-negative.
- Forced-sell quantity is exactly int(position * 0.30), not more.
- Buy quantity MUST NOT exceed leveraged capacity.
- The agent is deterministic given the same price, fundamental, cash, position, and parameters.
- Margin call logic takes priority over convergence logic (checked first).

##### Serialization Format

```
<analysis>Price = {price}, Fundamental = {fundamental}. Equity = cash + position × price = {equity}. Leverage exposure = |position × price| / leverage_ratio = {exposure}. Margin threshold = exposure × {margin_call_threshold} = {threshold_value}. {'MARGIN CALL: equity < threshold → forced sell 30%' if margin_triggered else 'Equity healthy.'}. Deviation = {deviation:.4f}. Action: {action}, qty = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute equity, check margin condition, then either force-sell or evaluate convergence buying, emitting the tagged output deterministically. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                    |
|---------------|------------|---------------|------------------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for equity computation and convergence deviation                      |
| `fundamental` | Continuous | Current tick  | Benchmark for convergence trading under normal conditions                      |

Does NOT use: peer positions, order book depth, VaR signals from external risk systems, systemic stress indicators — the agent manages its own balance sheet autonomously using only price and its internal state.

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute equity and leverage exposure:
  Read: cash, position from agent state
  Read: leverage_ratio, margin_call_threshold from parameters
  Compute: equity = cash + position * price
  Compute: leverage_exposure = abs(position * price) / leverage_ratio
  (Traces to: Geanakoplos 2010 — equity computation for leverage constraint)

Step 3 — Check margin call condition:
  Compute: margin_threshold = leverage_exposure * margin_call_threshold
  IF equity < margin_threshold AND position > 0: → Forced-sell branch (Step 4)
  ELSE: → Normal evaluation (Step 5)
  (Traces to: Brunnermeier & Pedersen 2009 — margin call triggers forced liquidation)

Step 4 — Forced deleveraging:
  Compute: forced_qty = int(position * 0.30)
  Compute: qty = max(1, forced_qty)
  Write: action = "sell"
  → Skip to Step 8
  (Traces to: Geanakoplos 2010 — involuntary position reduction under margin pressure)

Step 5 — Compute deviation for convergence evaluation:
  Compute: deviation = (price - fundamental) / fundamental
  IF deviation < -0.03: → Convergence buy branch (Step 6)
  ELSE: → Hold branch (Step 7)
  (Traces to: Shleifer & Vishny 1997 — convergence requires material discount)

Step 6 — Leveraged convergence buy:
  Compute: leveraged_cash = cash * leverage_ratio
  Compute: raw_qty = int(leveraged_cash * abs(deviation) / price)
  Compute: qty = min(raw_qty, int(leveraged_cash / price))
  Write: action = "buy"
  (Traces to: Geanakoplos 2010 — leverage expansion during calm conditions)

Step 7 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: Geanakoplos 2010 — no opportunity or already overleveraged)

Step 8 — Execute trade and update state (post-decision):
  IF action == "buy": Write: cash -= qty * price; Write: position += qty
  IF action == "sell": Write: cash += qty * price; Write: position -= qty
  (implementation convenience — state bookkeeping)
```

#### Action Space

| Aspect                | Specification                                                                                          |
|-----------------------|--------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                  |
| Action parameter rule | Trades at current market price (no limit orders; agent is a price-taker)                               |
| Sizing rule           | Forced sell: `int(position * 0.30)`. Normal buy: `int(cash * leverage_ratio * |deviation| / price)`     |
| Action lifetime       | Immediate execution; no persistent resting orders                                                      |
| Revision policy       | No revision — each round's order is independent; forced sells cannot be revoked                        |
| State constraint      | Position >= 0 (no short selling); cash >= 0 after trade                                                 |
| Resource cap          | `initial_cash` from config; effective capital = cash * leverage_ratio                                   |
| Exit rule             | Forced selling continues each round while margin condition persists                                    |

#### Mathematical Model

**Decision output:** Action enum (`buy`, `sell`, `hold`) and unsigned integer quantity.

**Decision logic formalization:**

```
equity = cash + position * price
leverage_exposure = abs(position * price) / leverage_ratio
margin_threshold = leverage_exposure * margin_call_threshold

IF equity < margin_threshold AND position > 0:
    qty = max(1, int(position * 0.30))
    action = "sell"   (forced deleveraging)

ELIF (price - fundamental) / fundamental < -0.03:
    deviation = (price - fundamental) / fundamental
    leveraged_cash = cash * leverage_ratio
    qty = min(int(leveraged_cash * |deviation| / price), int(leveraged_cash / price))
    action = "buy" IF qty > 0 ELSE "hold"

ELSE:
    action = "hold"; qty = 0
```

**State variables:**

| Variable   | Type  | Initial Value     | Update Phase |
|------------|-------|-------------------|--------------|
| `cash`     | float | config-determined | post-decide  |
| `position` | int   | 0                 | post-decide  |

**State evolution:**
- `cash`: Updated post-decide. Buy: `cash -= qty * price`. Sell: `cash += qty * price`.
- `position`: Updated post-decide. Buy: `position += qty`. Sell: `position -= qty`.

**Determinism contract:** Fully deterministic given identical price, fundamental, cash, position, and parameter values. No random components.

**Parameter symbol table:**

| Symbol                   | Meaning                                              | Default Value     | Source                        |
|--------------------------|------------------------------------------------------|-------------------|-------------------------------|
| `leverage_ratio`         | Capital multiplier for position sizing                | 25                | Geanakoplos (2010)            |
| `margin_call_threshold`  | Equity/exposure ratio that triggers forced selling    | 0.04              | Adrian & Shin (2010)          |
| `initial_cash`           | Starting cash endowment                               | config-determined | Standardised                  |

#### Behavioral Properties

- Time horizon: Medium — holds leveraged convergence positions across rounds; forced selling is involuntary and event-driven.
- Risk tolerance: High — operates at 25x leverage; accepts extreme concentration until margin forces liquidation.
- Information asymmetry: Partial — observes own equity and market price but has no visibility into systemic leverage or peer positions.
- Psychological profile: Rational under normal conditions (convergence trading) but subject to involuntary procyclical behavior under stress (Geanakoplos 2010; Brunnermeier & Pedersen 2009). The forced-selling mechanism is structural, not psychological.

## Parameters

| Parameter               | Type  | Default           | Valid Range      | Sensitivity | Description                                               | Impact                                                | Source                      |
|-------------------------|-------|-------------------|-----------------|-------------|-----------------------------------------------------------|-------------------------------------------------------|-----------------------------|
| `leverage_ratio`        | int   | 25                | [5, 50]         | High        | Capital multiplier for effective position sizing           | Higher → larger positions, earlier margin calls        | Geanakoplos (2010)          |
| `margin_call_threshold` | float | 0.04              | [0.02, 0.10]    | High        | Equity/exposure ratio triggering forced sell               | Lower → more sensitive to equity erosion              | Adrian & Shin (2010)        |
| `initial_cash`          | float | config-determined | [100000, 5000000]| Low        | Starting cash endowment                                    | Higher → longer runway before margin breach           | Standardised                |

## Worked Numerical Examples

### Case 1 — Normal condition: leveraged convergence buy

System state: `price` = 94.0, `fundamental` = 100.0, `cash` = 500,000, `position` = 0, `leverage_ratio` = 25, `margin_call_threshold` = 0.04

Calculation:
- `equity` = 500,000 + 0 * 94.0 = 500,000
- `leverage_exposure` = |0 * 94.0| / 25 = 0
- `margin_threshold` = 0 * 0.04 = 0
- Margin check: 500,000 < 0? NO → normal evaluation
- `deviation` = (94.0 - 100.0) / 100.0 = -0.064
- Deviation check: -0.064 < -0.03? YES → convergence buy
- `leveraged_cash` = 500,000 * 25 = 12,500,000
- `raw_qty` = int(12,500,000 * 0.064 / 94.0) = int(8510.6) = 8510
- Capacity: min(8510, int(12,500,000 / 94.0)) = min(8510, 132978) = 8510

Decision: buy 8510 shares at price 94.0
State update: `cash`: 500,000 → 500,000 - 8510 * 94.0 = -299,940 (leveraged, tracked as debt); `position`: 0 → 8510

### Case 2 — Margin call triggers forced sell

System state: `price` = 80.0, `fundamental` = 100.0, `cash` = 50,000, `position` = 5000, `leverage_ratio` = 25, `margin_call_threshold` = 0.04

Calculation:
- `equity` = 50,000 + 5000 * 80.0 = 450,000
- `leverage_exposure` = |5000 * 80.0| / 25 = 16,000
- `margin_threshold` = 16,000 * 0.04 = 640
- Margin check: 450,000 < 640? NO (equity still healthy in this case)

Adjusted example — more leveraged state: `cash` = -350,000 (debt from leveraged buying), `position` = 5000
- `equity` = -350,000 + 5000 * 80.0 = 50,000
- `leverage_exposure` = |5000 * 80.0| / 25 = 16,000
- `margin_threshold` = 16,000 * 0.04 = 640
- Margin check: 50,000 < 640? NO (still healthy with these parameters)

Revised to trigger: `cash` = -390,000, `position` = 5000, `price` = 78.0
- `equity` = -390,000 + 5000 * 78.0 = 0
- `leverage_exposure` = |5000 * 78.0| / 25 = 15,600
- `margin_threshold` = 15,600 * 0.04 = 624
- Margin check: 0 < 624? YES → FORCED SELL
- `forced_qty` = int(5000 * 0.30) = 1500

Decision: sell 1500 shares (forced deleveraging)
State update: `cash`: -390,000 → -390,000 + 1500 * 78.0 = -273,000; `position`: 5000 → 3500

### Case 3 — Normal hold (no discount, no margin call)

System state: `price` = 101.0, `fundamental` = 100.0, `cash` = 500,000, `position` = 1000, `leverage_ratio` = 25, `margin_call_threshold` = 0.04

Calculation:
- `equity` = 500,000 + 1000 * 101.0 = 601,000
- `leverage_exposure` = |1000 * 101.0| / 25 = 4,040
- `margin_threshold` = 4,040 * 0.04 = 161.6
- Margin check: 601,000 < 161.6? NO → normal evaluation
- `deviation` = (101.0 - 100.0) / 100.0 = +0.01
- Deviation check: 0.01 < -0.03? NO → hold

Decision: hold
State update: no change

### Edge Case — Position already zero, margin irrelevant

System state: `price` = 70.0, `fundamental` = 100.0, `cash` = 5,000, `position` = 0, `leverage_ratio` = 25, `margin_call_threshold` = 0.04

Calculation:
- `equity` = 5,000 + 0 = 5,000
- `leverage_exposure` = 0
- Margin check: position = 0 → margin call condition requires position > 0 → NO
- `deviation` = (70.0 - 100.0) / 100.0 = -0.30
- Deviation check: -0.30 < -0.03? YES → convergence buy
- `leveraged_cash` = 5,000 * 25 = 125,000
- `raw_qty` = int(125,000 * 0.30 / 70.0) = int(535.7) = 535

Decision: buy 535 shares (small leveraged buy with minimal remaining capital)
State update: `cash`: 5,000 → 5,000 - 535 * 70.0 = -32,450; `position`: 0 → 535

## Behavioral Verification and Calibration

**Calibration data sources:**
- `leverage_ratio` <- Geanakoplos (2010, Table 3): peak leverage 20–30x for mortgage-backed securities; default 25
- `margin_call_threshold` <- Adrian & Shin (2010, Table 1): margin calls at 3–5% equity deterioration; default 0.04

**Expected individual behaviour:**
- Given healthy equity and price 6% below fundamental, agent MUST emit action = "buy" with leveraged quantity
- Given equity below margin threshold with position > 0, agent MUST emit action = "sell" with qty = int(position * 0.30)
- Given no position and price at fundamental, agent MUST emit action = "hold" with qty = 0

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when equity < margin_threshold and position > 0 THEN broken — margin call logic not prioritised
- IF agent holds (qty = 0) when margin is breached and position > 0 THEN broken — forced selling not triggered
- IF forced sell quantity != int(position * 0.30) THEN broken — deleveraging fraction incorrect
- IF agent sells when equity is healthy and deviation < 0 THEN broken — should be buying convergence

#### Ablation Hooks

| Ablation name           | Setting                       | Hypothesis tested                                              | Expected direction                      | Metric                   |
|-------------------------|-------------------------------|----------------------------------------------------------------|-----------------------------------------|--------------------------|
| `no_margin_call`        | `margin_call_threshold = 0.0` | Forced selling is necessary for procyclical amplification       | No forced sales, position maintained    | `forced_sell_count`      |
| `aggressive_margin`     | `margin_call_threshold = 0.10`| Higher threshold triggers earlier deleveraging                  | More frequent forced sells              | `forced_sell_count`      |
| `low_leverage`          | `leverage_ratio = 5`          | Lower leverage reduces both buy size and margin sensitivity     | Smaller positions, fewer margin events  | `max_position_size`      |

## Academic References

| # | Citation                                                                                                                                                                                                             | Notes                                      |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1–65. https://doi.org/10.1086/648285                                                                                                | Primary theory; leverage cycles            |
| 2 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098                                           | Margin spirals; liquidity dynamics         |
| 3 | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002                                                          | Leverage targeting; margin calibration     |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
