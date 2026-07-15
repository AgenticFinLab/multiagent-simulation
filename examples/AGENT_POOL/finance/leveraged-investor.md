# Leveraged Investor with Margin-Call Fire-Sale Mechanism

## Summary

| Field                 | Content                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Archetype             | Leveraged Investor with Margin-Call Fire-Sale Mechanism                                                           |
| Theory Family         | Funding Liquidity — Margin Spirals and Fire-Sale Amplification                                                   |
| Behavioral Tendency   | **Diverging** — amplifies crashes via forced fire sales on margin breach                                         |
| Time Horizon          | Short (single-round conditional sell triggered by deviation threshold)                                           |
| Risk Tolerance        | Low in crisis (forced to liquidate regardless of expected recovery; zero discretion under margin breach)          |
| Information Asymmetry | Partial (observes price and fundamental; deviation computation requires both signals)                            |
| Determinism           | Deterministic (given identical deviation and parameters, always produces the same fire-sale decision)             |

## Definition and Goals

The leveraged investor models highly leveraged financial institutions (hedge funds, broker-dealers, structured investment vehicles) whose balance sheets are funded against structured-credit collateral. In the real world, these correspond to entities such as Bear Stearns' Enhanced Leverage Fund, Carlyle Capital Corporation, and Lehman Brothers' proprietary positions, which faced margin calls and forced liquidations as MBS collateral values declined during 2007–2008.

The agent's decision goal is to monitor the deviation of market price from fundamental value and execute forced sales when the deviation breaches a margin-call threshold. The fire-sale rule is: if `deviation < -margin_call_trigger`, sell `int(position * fire_sale_fraction)`. This creates geometric position decay during stress, with each round's liquidation reducing the position by half (at default parameters), producing successive waves of selling that progressively depress prices further.

The agent's behavioural role inside the simulation is to serve as the central fire-sale amplification mechanism: when prices decline sufficiently from fundamental value, margin calls force involuntary selling that further depresses prices, which triggers additional margin calls on other leveraged entities — the classic Brunnermeier-Pedersen funding liquidity spiral. Non-goals: (1) the leveraged investor MUST NOT buy during a fire sale — margin calls mandate liquidation only; (2) the leveraged investor MUST NOT exercise discretion over fire-sale timing — the threshold breach is mechanical and immediate.

## Theoretical Foundation

**Funding Liquidity Spirals (Brunnermeier & Pedersen 2009)**:
- Theory / Study: Market Liquidity and Funding Liquidity
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098
- Core Insight: A negative feedback loop exists between market liquidity and funding liquidity: declining asset prices reduce collateral values, triggering margin calls that force fire sales, which further reduce prices. This spiral is self-reinforcing and can produce price dislocations far exceeding what fundamentals alone would warrant.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental`; `if deviation < -margin_call_trigger: sell_qty = int(position × fire_sale_fraction)`. The geometric decay models successive margin call rounds.
- Empirical Evidence: Brunnermeier & Pedersen (2009, Proposition 2, p. 2210) prove that margin spirals are self-reinforcing in equilibrium. Empirically, Adrian & Shin (2010) document that broker-dealer leverage contracted by 50% during the crisis, with forced asset sales of $1–2 trillion in aggregate during 2007–2008.
- Relevance to This Agent: The agent directly implements the forced-liquidation leg of the margin spiral — it sells a large fraction of its position when collateral value declines below the margin threshold, mechanically without discretion.
- Calibration Source: `margin_call_trigger` in [0.05, 0.20] derived from Brunnermeier & Pedersen (2009, Section 3): typical haircuts on structured credit rose from 5% to 40% during the crisis; a 10% decline threshold models the initial margin call point before haircuts escalated.
- Falsification Conditions: If this agent holds position during a period where deviation < -margin_call_trigger (i.e. does not fire-sell), the forced-liquidation mechanism is falsified.
- Alternative Theories: Voluntary deleveraging (Shleifer & Vishny 1992), bank-run models (Diamond & Dybvig 1983).

**Procyclical Leverage and Asset Pricing (Adrian & Shin 2010)**:
- Theory / Study: Liquidity and Leverage
- Citation: Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002
- Core Insight: Financial intermediaries manage balance sheets procyclically — they expand leverage in booms and contract in busts. During contractions, the leverage constraint binds and forces asset sales at a rate proportional to the required balance-sheet adjustment, creating fire-sale externalities that depress market prices below fundamental values.
- Mathematical Formulation: `fire_sale_fraction = 0.50` models the empirical observation that institutions under margin pressure liquidated roughly half their positions in each forced-selling episode, producing geometric decay: `position_t = position_0 × (1 - fire_sale_fraction)^n` where n = number of margin-call rounds triggered.
- Empirical Evidence: Adrian & Shin (2010, Figure 3, p. 425) show that broker-dealer assets contracted by $500B in Q4 2008 alone; Carlyle Capital Corporation liquidated ~$16B in MBS (its entire portfolio) over 3 margin-call episodes in March 2008, losing approximately 50% per episode.
- Relevance to This Agent: The 50% fire-sale fraction and geometric decay model are calibrated directly from the empirical leverage-cycle dynamics documented by Adrian & Shin.
- Calibration Source: `fire_sale_fraction` = 0.50 based on Adrian & Shin (2010): typical forced-selling episodes liquidated 40–60% of the stressed portfolio; `initial_position` = 1500 and `initial_cash` = 2000000 model a moderately leveraged structured-credit portfolio.
- Falsification Conditions: If the agent's position does not decrease by approximately fire_sale_fraction when deviation < -margin_call_trigger, the forced-liquidation model is broken.
- Alternative Theories: Optimal liquidation under uncertainty (Almgren & Chriss 2001), strategic delay of fire sales (Diamond & Rajan 2011).

## Design Purpose and Activation Triggers

Purpose: Serve as the central fire-sale amplification mechanism — forced selling on margin breach depresses prices, triggering further margin calls in a self-reinforcing spiral.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Current fundamental value available
- Current agent position > 0

Missing-Signal Policy: If price or fundamental is unavailable (NaN), the agent holds (cannot compute deviation). If position is zero, the agent holds (nothing to liquidate).

Activation Triggers:
- `deviation < -margin_call_trigger` AND `position > 0`: Fire-sell `int(position * fire_sale_fraction)` shares
- `deviation >= -margin_call_trigger`: Hold (no margin breach)
- Default (missing signals): Hold

Deactivation Conditions:
- Deviation recovers above -margin_call_trigger: Margin pressure relieved
- Position reaches zero: Fully liquidated
- Simulation end / market closure: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                                | Behavioral change                             | Mechanism                              |
|------------------------------------------|-----------------------------------------------|----------------------------------------|
| Small price decline (above threshold)    | Holds — no margin breach                      | Leverage still within limits           |
| Large price decline (below threshold)    | Fire-sells 50% of position                    | Margin call forces liquidation         |
| Sustained crisis (multiple rounds below) | Geometric position decay (successive 50% cuts)| Repeated margin calls each round       |

Environmental Dependencies: Requires per-round market broadcast containing `price` and `fundamental` fields. Access to agent's own `position` state. No peer actions, order-book depth, or volatility signals are used.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source                      | Type / Shape | Required? | Notes                                           |
|------------------------|-----------------------------|--------------|-----------|-------------------------------------------------|
| `price`                | Market coordinator payload  | `float`      | yes       | Current market price of asset                   |
| `fundamental`          | Market coordinator payload  | `float`      | yes       | True fundamental value of asset                 |
| `position`             | Agent persisted state       | `int`        | yes       | Current holdings subject to margin              |
| `cash`                 | Agent persisted state       | `float`      | yes       | Available cash balance                          |
| `round`                | Scheduler / round header    | `int`        | yes       | Current simulation round number                 |
| `margin_call_trigger`  | Config extras               | `float`      | yes       | Deviation threshold for forced liquidation (§3.7)|
| `fire_sale_fraction`   | Config extras               | `float`      | yes       | Fraction of position sold per margin call (§3.7)|
| `retrieved_knowledge`  | Retrieval store (RAG only)  | `list[str]`  | RAG only  | Historical margin-call episodes; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum   | Unit   | Required? | Meaning                                     |
|-------------|--------|----------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"sell", "hold"}`   | —      | yes       | Fire-sale or hold decision                  |
| `quantity`  | int    | [0, position]        | shares | yes       | Number of shares to liquidate               |
| `bid_price` | float  | > 0                  | price  | yes       | Market price for order submission           |
| `reasoning` | string | 1–3 sentences        | —      | yes       | Deviation, threshold, and margin-call logic |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST equal `int(position * fire_sale_fraction)` when margin is breached; MUST be 0 otherwise.
- `action` MUST be `"sell"` when quantity > 0 and `"hold"` when quantity == 0.
- `bid_price` MUST equal the current market price.
- The agent is deterministic: identical inputs yield identical outputs.
- Sign convention: quantity is always non-negative; direction is always sell.

##### Serialization Format

```
<analysis>Price = {price}; fundamental = {fundamental}; deviation = ({price} - {fundamental}) / {fundamental} = {deviation:.4f}; margin_call_trigger = -{margin_call_trigger}; breach = {breach}.</analysis>
<decision>{"action": "<sell|hold>", "quantity": <int>, "bid_price": <float>, "reasoning": "Deviation {deviation:.4f} {'breaches' if breach else 'within'} margin threshold -{margin_call_trigger}; {'fire-selling' if breach else 'holding'}."}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` and `fundamental` MUST be read from the market coordinator broadcast; `position` and `cash` from agent state; config extras supply `margin_call_trigger` and `fire_sale_fraction`.
2. **Decision emission** — the code path MUST populate all four required fields and MUST enforce the margin-breach formula.
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all four fields present, quantity = int(position × fraction) when breach.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same four-field output object.
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                           |
|---------------|------------|---------------|-----------------------------------------------------|
| `price`       | Continuous | Current only  | Needed for deviation computation                    |
| `fundamental` | Continuous | Current only  | Denominator and reference for deviation computation |
| `position`    | Discrete   | Current only  | Determines fire-sale quantity                       |

Does NOT use: price history, volatility, peer actions, order-book depth, momentum indicators, spread, cash (for the decision — only position matters), or any forward-looking signals.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast. Write: nothing. (Implementation convenience — signal access.)

2. **Read fundamental value.** Read: `fundamental` from market broadcast. Write: nothing. (Implementation convenience — signal access.)

3. **Compute deviation.** Read: `price`, `fundamental`. Compute: `deviation = (price - fundamental) / fundamental`. Write: nothing (intermediate variable). (Core metric — measures collateral value shortfall.)

4. **Evaluate margin-call condition.** Read: `deviation`, `margin_call_trigger`. Compute: `breach = (deviation < -margin_call_trigger)`. Write: nothing (intermediate variable). (Traces to Brunnermeier & Pedersen 2009 — threshold-based margin call.)

5. **Read current position.** Read: `position` from agent state. Write: nothing. (Implementation convenience — state access.)

6. **Compute fire-sale quantity.** Read: `breach`, `position`, `fire_sale_fraction`. If `breach` is True AND `position > 0`: `sell_qty = int(position * fire_sale_fraction)`. If `sell_qty == 0` and `position > 0`: `sell_qty = 1`. Else: `sell_qty = 0`. Write: nothing (intermediate variable). (Traces to Adrian & Shin 2010 — geometric liquidation.)

7. **Emit decision object.** Read: all computed fields. Write: emit the four-field decision object per I/O Contract serialization format. (Implementation convenience — output assembly.)

#### Action Space

| Aspect                | Specification                                                                                              |
|-----------------------|------------------------------------------------------------------------------------------------------------|
| Action types allowed  | `sell`, `hold`                                                                                             |
| Action parameter rule | `bid_price` = current market price; `quantity` = int(position × fire_sale_fraction) on breach              |
| Sizing rule           | Fixed fraction (50%) of current position per margin-call event; geometric decay over multiple rounds.      |
| Action lifetime       | One round; re-evaluated each tick.                                                                         |
| Revision policy       | Each round independently evaluates margin condition — previous fire sales reduce position but not threshold.|
| State constraint      | Position monotonically decreases during crisis. Agent never buys.                                          |
| Resource cap          | Bounded by initial_position; once fully liquidated, agent becomes inactive.                                 |
| Exit rule             | Agent holds indefinitely once position is zero or margin condition is no longer breached.                   |

#### Mathematical Model

**Decision output:** The agent computes a binary fire-sale trigger based on price deviation from fundamental.

**Decision logic formalization:**

```
Given: price_t, fundamental_t, position_t, margin_call_trigger, fire_sale_fraction

Step 1: Compute deviation
  deviation = (price_t - fundamental_t) / fundamental_t

Step 2: Evaluate margin breach
  breach = (deviation < -margin_call_trigger)

Step 3: Size the fire sale
  if breach AND position_t > 0:
    sell_qty = max(1, floor(position_t × fire_sale_fraction))
  else:
    sell_qty = 0

Step 4: Action determination
  if sell_qty > 0:
    action = "sell"
  else:
    action = "hold"

Step 5: Position evolution (post-trade)
  position_{t+1} = position_t - sell_qty
  cash_{t+1} = cash_t + sell_qty × price_t
```

**State variables:**

| Variable   | Type    | Initial Value      | Update Phase           |
|------------|---------|--------------------|------------------------|
| `position` | `int`   | `initial_position` | Post-trade (decremented by sell_qty) |
| `cash`     | `float` | `initial_cash`     | Post-trade (incremented by sell_qty × price) |

**State evolution:** During sustained crisis (deviation remains below trigger), position decays geometrically: `position_t = initial_position × (1 - fire_sale_fraction)^n` where n is the number of consecutive breach rounds.

**Determinism contract:** The decision is fully deterministic given identical price, fundamental, position, and parameters. No random number generation is used.

**Parameter symbol table:**

| Symbol               | Meaning                                      | Default Value | Source                        |
|----------------------|----------------------------------------------|---------------|-------------------------------|
| `margin_call_trigger`| Negative deviation threshold for fire sale   | 0.10          | Brunnermeier & Pedersen (2009)|
| `fire_sale_fraction` | Fraction of position liquidated per call     | 0.50          | Adrian & Shin (2010)          |
| `initial_position`   | Starting leveraged holdings                  | 1500          | Simulation design             |
| `initial_cash`       | Starting cash buffer                         | 2000000       | Simulation design             |
| `deviation`          | Price-to-fundamental gap (signed)            | —             | Derived                       |
| `breach`             | Boolean margin-call flag                     | —             | Derived                       |

#### Behavioral Properties

- Time horizon: Single-round — the agent evaluates the margin condition independently each round; no anticipation of future price paths or strategic timing of liquidation. Rationale: margin calls are immediate and non-discretionary; the leveraged institution has no choice but to sell when the call arrives.
- Risk tolerance: Zero discretion under stress — when the margin threshold is breached, the agent must sell regardless of expected recovery or perceived overshooting. Rationale: margin calls are contractual obligations enforced by prime brokers; the institution cannot negotiate timing.
- Information asymmetry: Partial — the agent observes both price and fundamental but uses them only to compute deviation; it does not forecast future prices or estimate recovery probabilities.
- Psychological profile: Mechanistic institutional constraint rather than behavioural bias; models the structural vulnerability of leveraged balance sheets to collateral-value declines.

## Parameters

| Parameter            | Type    | Default  | Valid Range      | Sensitivity | Description                                       | Impact                                                  | Source                        |
|----------------------|---------|----------|------------------|-------------|---------------------------------------------------|---------------------------------------------------------|-------------------------------|
| `margin_call_trigger`| `float` | 0.10    | [0.05, 0.20]    | high        | Magnitude of negative deviation triggering sell   | Lower -> earlier fire sales, deeper spiral              | Brunnermeier & Pedersen (2009)|
| `fire_sale_fraction` | `float` | 0.50    | [0.20, 0.80]    | high        | Fraction of position sold per margin event        | Higher -> more selling per round, faster depletion      | Adrian & Shin (2010)          |
| `initial_position`   | `int`   | 1500    | [500, 5000]     | medium      | Starting leveraged MBS holdings                   | Higher -> more total fire-sale supply                   | Simulation design             |
| `initial_cash`       | `float` | 2000000 | [500000, 10000000]| low        | Starting cash buffer                              | No effect on sell decision; affects portfolio metrics    | Simulation design             |

## Worked Numerical Examples

### Case 1 — Moderate decline, no margin breach

System state: `price` = 46.00; `fundamental` = 50.00; `position` = 1500; `margin_call_trigger` = 0.10; `fire_sale_fraction` = 0.50.

Calculation:
- `deviation` = (46.00 - 50.00) / 50.00 = -0.08
- `breach` = (-0.08 < -0.10) = False
- `sell_qty` = 0

Decision: `action = "hold"`, `quantity = 0`, `bid_price = 46.00`, `reasoning = "Deviation -0.0800 within margin threshold -0.10; holding."`.

State update: No change.

### Case 2 — First margin-call trigger, fire sale begins

System state: `price` = 44.00; `fundamental` = 50.00; `position` = 1500; `margin_call_trigger` = 0.10; `fire_sale_fraction` = 0.50.

Calculation:
- `deviation` = (44.00 - 50.00) / 50.00 = -0.12
- `breach` = (-0.12 < -0.10) = True
- `sell_qty` = int(1500 × 0.50) = 750

Decision: `action = "sell"`, `quantity = 750`, `bid_price = 44.00`, `reasoning = "Deviation -0.1200 breaches margin threshold -0.10; fire-selling 750 shares."`.

State update: `position` = 1500 - 750 = 750; `cash` += 750 × 44.00 = +33000.

### Case 3 — Second margin call (sustained crisis), geometric decay

System state: `price` = 42.00; `fundamental` = 50.00; `position` = 750; `margin_call_trigger` = 0.10; `fire_sale_fraction` = 0.50.

Calculation:
- `deviation` = (42.00 - 50.00) / 50.00 = -0.16
- `breach` = (-0.16 < -0.10) = True
- `sell_qty` = int(750 × 0.50) = 375

Decision: `action = "sell"`, `quantity = 375`, `bid_price = 42.00`, `reasoning = "Deviation -0.1600 breaches margin threshold -0.10; fire-selling 375 shares."`.

State update: `position` = 750 - 375 = 375; `cash` += 375 × 42.00 = +15750.

### Edge Case — Very small position, floor guard

System state: `price` = 40.00; `fundamental` = 50.00; `position` = 1; `margin_call_trigger` = 0.10; `fire_sale_fraction` = 0.50.

Calculation:
- `deviation` = (40.00 - 50.00) / 50.00 = -0.20
- `breach` = (-0.20 < -0.10) = True
- `sell_qty_raw` = int(1 × 0.50) = 0
- Floor guard: `sell_qty = 0` but `position > 0` → `sell_qty = 1`

Decision: `action = "sell"`, `quantity = 1`, `bid_price = 40.00`, `reasoning = "Deviation -0.2000 breaches margin threshold -0.10; fire-selling 1 share (floor guard)."`.

State update: `position` = 1 - 1 = 0; `cash` += 1 × 40.00 = +40.00.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `margin_call_trigger` <- Brunnermeier & Pedersen (2009, Section 3): initial margin requirements on structured credit were 5–10%; a 10% decline triggers the first margin call.
- `fire_sale_fraction` <- Adrian & Shin (2010, Figure 3): empirical leverage contraction episodes show 40–60% position reduction per forced-selling round; 50% is the central estimate.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.08 and margin_call_trigger = 0.10, agent MUST hold (no breach).
- Given deviation = -0.12 and margin_call_trigger = 0.10, agent MUST sell int(position × 0.50) shares.
- Given deviation = -0.10 exactly and margin_call_trigger = 0.10, agent MUST hold (strict inequality: -0.10 is NOT < -0.10).
- Given position = 0 and breach = True, agent MUST hold (nothing to liquidate).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent holds when deviation < -margin_call_trigger AND position > 0 THEN the fire-sale mechanism is broken.
- IF the agent sells when deviation >= -margin_call_trigger THEN the threshold check is inverted or broken.
- IF the agent buys securities at any point THEN the sell-only constraint is violated.
- IF the agent's position increases between rounds THEN the monotonic-depletion-during-crisis property is violated.

#### Ablation Hooks

| Ablation name          | Setting                          | Hypothesis tested                                    | Expected direction                         | Metric                       |
|------------------------|----------------------------------|------------------------------------------------------|--------------------------------------------|------------------------------|
| `no_fire_sales`        | `margin_call_trigger = 1.0`     | Fire sales are necessary for crash amplification      | Crash depth decreases significantly        | Maximum drawdown             |
| `early_margin_call`    | `margin_call_trigger = 0.05`    | Lower thresholds produce earlier and deeper spirals   | Crisis begins sooner                       | Round of first fire sale     |
| `smaller_liquidation`  | `fire_sale_fraction = 0.20`     | Larger liquidation fractions accelerate price decline  | Slower price decline per round             | Price decline per round      |

## Academic References

| # | Citation                                                                                                                                                              | Notes                                    |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201–2238. https://doi.org/10.1093/rfs/hhn098 | Primary theory: funding-liquidity spiral mechanism |
| 2 | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002 | Procyclical leverage and empirical fire-sale dynamics |
| 3 | Shleifer, A., & Vishny, R. W. (2011). Fire sales in finance and macroeconomics. *Journal of Economic Perspectives*, 25(1), 29–48. https://doi.org/10.1257/jep.25.1.29 | Fire-sale externalities and price impact |
| 4 | Gorton, G. B., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425–451. https://doi.org/10.1016/j.jfineco.2011.03.016 | Repo market haircut spirals |
| 5 | Greenwood, R., Landier, A., & Thesmar, D. (2015). Vulnerable banks. *Journal of Financial Economics*, 115(3), 471–485. https://doi.org/10.1016/j.jfineco.2014.11.006 | Fire-sale contagion across institutions |

## Design Provenance

| Field       | Content                                                       |
|-------------|---------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                    |
| Created     | 2026-07-14                                                    |
| Version     | 1.0.0                                                         |
| Status      | canonical                                                     |
| Icon        | ![](../agent_images/icons/finance-leveraged-investor.png)     |
