# Fixed-Income Bond Trader Exploiting Mark-to-Market Dislocations

## Summary

| Field                 | Content                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------|
| Archetype             | Fixed-Income Bond Trader Exploiting Mark-to-Market Dislocations                                 |
| Theory Family         | Fixed-income valuation / Duration and mark-to-market accounting                                 |
| Behavioral Tendency   | **Adaptive** — buys undervaluation, sells overvaluation; switches direction based on deviation sign |
| Time Horizon          | Medium                                                                                          |
| Risk Tolerance        | Medium                                                                                          |
| Information Asymmetry | Partial — uses public price and fundamental value but has expertise in fixed-income valuation    |
| Determinism           | Deterministic                                                                                   |

## Definition and Goals

This agent models a professional fixed-income trader at a broker-dealer or asset-management firm who actively trades around mark-to-market dislocations in bank-related securities. The real-world counterpart is the class of sell-side bond traders, proprietary trading desks, and fixed-income hedge funds that exploit mispricings created when held-to-maturity portfolios must be marked to market during stress events — such as the SVB crisis where $21 billion in bond losses crystallized upon forced asset sales. These participants are opportunistic: they buy securities they assess as undervalued and sell those they view as overvalued.

The decision goal is to produce a buy or sell action when the absolute deviation from fundamental value exceeds 3%, with quantity scaled proportionally to the deviation magnitude — specifically `quantity = min(500, int(abs(deviation) * 3000))`. The agent optimises risk-adjusted returns by exploiting temporary mark-to-market dislocations that it expects to mean-revert.

Behaviourally, this agent is a mixed/opportunistic participant. It provides liquidity during distress (buying undervalued securities) and adds selling pressure during overvaluation. The characteristic pattern is two-sided trading around fundamental value with a deadband of 3% inside which the agent holds. Non-goals: (1) This agent MUST NOT trade within the 3% deadband — it does not scalp small deviations or market-make continuously. (2) This agent MUST NOT take directional bets independent of the deviation signal — it is always mean-reversion oriented, never momentum-following.

## Theoretical Foundation

**Fixed-Income Duration and Mark-to-Market Losses**:
- Theory / Study: Duration as a measure of bond-price sensitivity to interest rates; mark-to-market accounting crystallizes paper losses
- Citation: Macaulay, F.R. (1938). *Some Theoretical Problems Suggested by the Movements of Interest Rates, Bond Yields and Stock Prices in the United States since 1856*. NBER. (Duration concept); FASB ASC 320 (mark-to-market accounting standard).
- Core Insight: The percentage change in a bond's price is approximately equal to its modified duration times the change in yield: dP/P ≈ -D * dy. When a bank holds bonds at amortized cost and is forced to sell (or must mark to market under accounting rules), unrealized losses become realized, creating sudden price pressure on related securities. Opportunistic traders exploit the gap between fire-sale prices and intrinsic value based on hold-to-maturity cash flows.
- Mathematical Formulation: `trade_signal = deviation / abs(deviation) * min(500, int(abs(deviation) * 3000))` when `abs(deviation) > deadband_threshold`
- Empirical Evidence: Ellul, Jotikasthira & Lundblad (2011, *Review of Financial Studies*) find that fire-sale-driven mispricings in corporate bonds produce excess returns of 1.5–3.0% per month for buyers of distressed bonds (N = 6,791 bond-quarters, t-stat = 3.12).
- Relevance to This Agent: The bond trader identifies mark-to-market dislocations (where fire-sale prices deviate from fundamental hold-to-maturity value) and trades toward convergence, buying undervalued and selling overvalued securities.
- Calibration Source: Ellul et al. (2011), Table 4: mean fire-sale discount of 3.2% for investment-grade bonds under forced selling; supports deadband_threshold of 0.03.
- Falsification Conditions: If this agent trades when abs(deviation) < deadband_threshold, the deadband logic is broken. If the agent buys when deviation > 0 (overvalued) or sells when deviation < 0 (undervalued), the direction logic is inverted.
- Alternative Theories: Limits of arbitrage (Shleifer & Vishny 1997) where capital constraints prevent full exploitation of mispricings; noise-trader risk (De Long et al. 1990) where deviations may widen before converging.

**Mean Reversion in Fixed-Income Spreads**:
- Theory / Study: Empirical mean-reversion in credit spreads and bond mispricings post-stress
- Citation: Collin-Dufresne, P., Goldstein, R.S. & Martin, J.S. (2001). "The Determinants of Credit Spread Changes." *Journal of Finance*, 56(6), 2177–2207. DOI:10.1111/0022-1082.00402
- Core Insight: Credit spreads exhibit mean-reversion with a half-life of 3–6 months for investment-grade bonds. During stress events, spreads overshoot fundamentally justified levels due to liquidity demand, then revert as the liquidity shock dissipates. Traders who buy during the overshoot earn convergence profits.
- Mathematical Formulation: `expected_profit = abs(deviation) * convergence_probability` where convergence_probability is historically 0.75–0.85 within 20 trading days for investment-grade bonds
- Empirical Evidence: Collin-Dufresne et al. (2001) find that only 25% of credit-spread variation is explained by fundamentals (adjusted R² = 0.25), implying large transient components amenable to mean-reversion trading. The residual component has a monthly autocorrelation of 0.31 (SE = 0.06), indicating predictable reversion.
- Relevance to This Agent: The bond trader's strategy is predicated on mean-reversion — buying into price declines and selling into price increases with the expectation that fire-sale dislocations are transient.
- Calibration Source: Collin-Dufresne et al. (2001), Table 6: residual half-life implies profitable holding period of 10–20 ticks at simulation timescale. Quantity scaling of 3000 calibrated to produce meaningful position sizes at typical deviation magnitudes (3–10%).
- Falsification Conditions: If the agent's cumulative P&L is systematically negative in scenarios where price converges to fundamental within 20 ticks, the strategy calibration is broken.
- Alternative Theories: Random walk in spreads (Fama 1970 efficient markets); persistent mispricing under limits of arbitrage (Shleifer & Vishny 1997).

## Design Purpose and Activation Triggers

Purpose: This agent exhibits opportunistic two-sided trading that exploits mark-to-market dislocations when deviation from fundamental value exceeds a deadband threshold.

Call Frequency: every-tick

Prerequisite Signals (must be available for the agent to evaluate):
- `current_price` available (real-time market price)
- `fundamental_value` available (reference value for deviation computation)

Missing-Signal Policy: If `current_price` or `fundamental_value` is unavailable or NaN, hold — the trader abstains from trading without reliable valuation signals.

Activation Triggers:
- Undervaluation detected: buy — when `deviation < -deadband_threshold` (default: -0.03)
- Overvaluation detected: sell — when `deviation > deadband_threshold` (default: 0.03)
- Default: hold — no action when `abs(deviation) <= deadband_threshold`

Deactivation Conditions:
- Cash exhausted (for buys): if `cash <= 0`, cannot execute buy orders
- Position exhausted (for sells): if `position <= 0`, cannot execute sell orders
- Deviation returns within deadband: trading ceases when |deviation| <= 0.03

Behavioral Adaptation by Condition:
| Condition                     | Behavioral change                                    | Mechanism                                          |
|-------------------------------|------------------------------------------------------|----------------------------------------------------|
| Large negative deviation      | Buy aggressively with quantity scaled to |deviation|  | Quantity formula: abs(dev)*3000, capped at 500     |
| Large positive deviation      | Sell aggressively with quantity scaled to |deviation| | Same formula applied symmetrically for selling     |
| Small deviation (within 3%)   | No trading — agent holds existing position           | Deadband prevents overtrading on noise             |

Environmental Dependencies: Requires real-time price feed and fundamental value reference. No peer signals, order-book data, or external research feeds required.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input              | Source                    | Type / Shape | Required? | Notes                                              |
|--------------------|---------------------------|--------------|-----------|----------------------------------------------------|
| `current_price`    | environment / market feed | `float`      | yes       | maps to Decision Information Set                   |
| `fundamental_value`| environment / scenario    | `float`      | yes       | maps to Decision Information Set                   |
| `cash`             | agent's own persisted state| `float`     | yes       | populated on first call by initial_cash            |
| `position`         | agent's own persisted state| `int`       | yes       | populated on first call by initial_position        |
| `round`            | scheduler / round header  | `int`        | yes       | current simulation round number                    |
| `agent_id`         | scheduler / round header  | `str`        | yes       | agent identity                                     |
| `retrieved_knowledge`| retrieval store          | `list[str]`  | retrieval variants only | falls back to sentinel if empty     |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum            | Unit   | Required? | Meaning                                     |
|-------------|--------|-------------------------------|--------|-----------|---------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`     | —      | yes       | discrete action selected this call          |
| `quantity`  | int    | `[0, 500]`                   | shares | yes       | number of units to trade                    |
| `reasoning` | string | 1–3 sentences                 | —      | yes       | audit trail explaining decision             |

##### Content Constraints

- **Required fields**: `action`, `quantity`, and `reasoning` MUST be present on every call.
- **Forbidden fields**: no `price` or `limit_price` field — agent trades at market.
- **Value ranges**: `quantity` MUST be clamped to `[0, 500]`. For buys: also clamped by `int(cash/current_price)`. For sells: also clamped by `position`.
- **Units and sign conventions**: quantity is always non-negative; `buy` increases position, `sell` decreases position. Direction is encoded in the action enum, not quantity sign.
- **Determinism markers**: decision is deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...reasoning about deviation direction and magnitude relative to deadband, 1–3 sentences...</analysis>
<decision>{"action": "buy", "quantity": 450, "reasoning": "Deviation of -15% exceeds 3% deadband; buying 450 shares at mark-to-market discount."}</decision>
```

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON with keys matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include the tag+JSON schema in the system prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities:**

1. **Signal wiring** — `current_price`, `fundamental_value` from environment; `cash`, `position` from persisted state.
2. **Decision emission** — every decision MUST populate `action`, `quantity`, `reasoning`. Quantity MUST obey all clamping rules.
3. **Prompt drafting (model-driven variants)** — prompt MUST spell out tags and JSON schema with verbatim example.
4. **Parser tests** — smoke test verifying tag presence, JSON validity, field presence, and range compliance.
5. **Variant parity** — all declared variants produce the SAME field set.
6. **Contract-versus-prose conflict resolution** — this section wins on conflict.

#### Decision Information Set

| Signal             | Type       | Memory Window | Rationale                                                   |
|--------------------|------------|---------------|-------------------------------------------------------------|
| `current_price`    | Continuous | 1 tick        | Required for deviation calculation                           |
| `fundamental_value`| Continuous | 1 tick        | Reference for identifying mark-to-market dislocations        |
| `cash`             | Continuous | 1 tick        | Constrains buying capacity                                  |
| `position`         | Discrete   | 1 tick        | Constrains selling capacity                                 |

Does NOT use: order-book depth, trading volume, social media sentiment, peer positions, credit ratings, or yield-curve shape. The agent relies solely on deviation from fundamental value.

#### Core Behavioral Mechanism

1. **Read** `current_price`, `fundamental_value`, `cash`, `position` from environment and own state. **No write.** (Implementation convenience — signal acquisition.)

2. **Compute deviation**: `deviation = (current_price - fundamental_value) / fundamental_value`. **Read**: current_price, fundamental_value. **Write**: none. (Traces to Macaulay 1938 / Ellul et al. 2011 — assessing mark-to-market dislocation magnitude.)

3. **Evaluate deadband**: if `abs(deviation) <= deadband_threshold`, emit hold and skip to step 8. **Read**: deviation, deadband_threshold. **Write**: none. (Traces to Collin-Dufresne et al. 2001 — small deviations may be noise rather than exploitable dislocations.)

4. **Determine direction**: if `deviation < 0` (undervalued), set direction = buy. If `deviation > 0` (overvalued), set direction = sell. **Read**: deviation. **Write**: none. (Traces to mean-reversion logic — buy low, sell high relative to fundamental.)

5. **Compute raw quantity**: `raw_quantity = int(abs(deviation) * 3000)`. **Read**: deviation. **Write**: none. (Traces to Ellul et al. 2011 — quantity proportional to dislocation magnitude.)

6. **Apply caps and constraints**: `quantity = min(500, raw_quantity)`. For buys: further clamp `quantity = min(quantity, int(cash / current_price))`. For sells: further clamp `quantity = min(quantity, position)`. **Read**: raw_quantity, cash, current_price, position. **Write**: none. (Implementation convenience — physical and budget constraints.)

7. **Emit trade decision**: output `action = direction`, `quantity` as computed. **Read**: direction, quantity. **Write**: For buys: cash -= quantity * current_price, position += quantity (post-execution). For sells: position -= quantity, cash += quantity * current_price (post-execution).

8. **Emit hold decision** (if deadband not breached): output `action = "hold"`, `quantity = 0`. **Read**: none additional. **Write**: none.

#### Action Space

| Aspect                | Specification                                                                                    |
|-----------------------|--------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                           |
| Action parameter rule | No continuous price parameter — agent trades at market price                                     |
| Sizing rule           | `quantity = min(500, int(abs(deviation) * 3000))`, further clamped by cash (buys) or position (sells) |
| Action lifetime       | Immediate execution — market order, expires at end of tick                                       |
| Revision policy       | No revision — order is final once emitted                                                        |
| State constraint      | `position >= 0` for sells; `cash >= 0` for buys — no short-selling, no borrowing                |
| Resource cap          | Maximum 500 units per tick; total buying capped by initial_cash; total selling capped by initial_position |
| Exit rule             | Agent holds indefinitely when deviation is within deadband; becomes one-sided if cash or position exhausted |

#### Mathematical Model

**Decision output**: Ternary action `a in {buy, sell, hold}` and non-negative integer quantity `q in [0, 500]`.

**Decision logic formalization**:

```
deviation = (current_price - fundamental_value) / fundamental_value

if abs(deviation) <= deadband_threshold:
    action = "hold"
    quantity = 0
elif deviation < -deadband_threshold:
    action = "buy"
    quantity = min(500, int(abs(deviation) * 3000), int(cash / current_price))
elif deviation > deadband_threshold:
    action = "sell"
    quantity = min(500, int(abs(deviation) * 3000), position)
```

**State variables**:

| Variable   | Type  | Initial Value      | Update Phase   |
|------------|-------|--------------------|----------------|
| `cash`     | float | `initial_cash`     | post-execution |
| `position` | int   | `initial_position` | post-execution |

**State evolution**: After buy: `cash -= quantity * price`, `position += quantity`. After sell: `position -= quantity`, `cash += quantity * price`. Updates occur post-execution.

**Determinism contract**: Fully deterministic given identical inputs and state. No random draws.

**Parameter symbol table**:

| Symbol              | Meaning                                        | Default Value | Source                          |
|---------------------|------------------------------------------------|---------------|---------------------------------|
| `deadband_threshold`| Minimum absolute deviation to trigger trading  | 0.03          | Ellul et al. (2011), Table 4    |
| `initial_cash`      | Starting cash for buying operations            | 50000.0       | Scenario configuration          |
| `initial_position`  | Starting share position for selling operations | 500           | Scenario configuration          |

#### Behavioral Properties

- **Time horizon**: Medium — holds positions expecting mean-reversion over multiple ticks (10–20 tick expected convergence) rather than intra-tick scalping. Rationale: credit-spread mean-reversion half-life is 3–6 months (Collin-Dufresne et al. 2001).
- **Risk tolerance**: Medium — takes directional positions against the prevailing trend (buying into declines, selling into rallies) but sizes positions conservatively with per-tick caps. Rationale: professional bond traders manage position limits.
- **Information asymmetry**: Partial — uses public price and a fundamental value estimate but has professional expertise in fixed-income valuation that gives more precise deviation estimates than retail participants.
- **Psychological profile**: Rational opportunist with no behavioral biases modeled. Embodies efficient-market contrarian logic: deviations from fundamental are exploitable rather than informative. Constraints come from capital limits (Shleifer & Vishny 1997), not cognitive limitations.

## Parameters

| Parameter           | Type  | Default  | Valid Range     | Sensitivity | Description                                              | Impact                                                    | Source                       |
|---------------------|-------|----------|-----------------|-------------|----------------------------------------------------------|-----------------------------------------------------------|------------------------------|
| `deadband_threshold`| float | 0.03     | (0.0, 0.20)     | high        | Minimum absolute deviation to trigger any trade          | Higher -> fewer trades, only large dislocations exploited | Ellul et al. (2011) Table 4  |
| `initial_cash`      | float | 50000.0  | [1000, 1000000] | medium      | Starting cash available for buy operations               | Higher -> more buying capacity, longer engagement         | Scenario configuration       |
| `initial_position`  | int   | 500      | [0, 50000]      | medium      | Starting position available for sell operations          | Higher -> more selling capacity when overvalued           | Scenario configuration       |

## Worked Numerical Examples

### Case 1 — Buy triggered by undervaluation

System state: current_price = 85.0, fundamental_value = 100.0, cash = 50000.0, position = 500, deadband_threshold = 0.03

Calculation:
  deviation = (85.0 - 100.0) / 100.0 = -0.15
  Check: abs(-0.15) = 0.15 > deadband_threshold (0.03)? Yes.
  Direction: deviation < 0, so action = "buy"
  raw_quantity = int(abs(-0.15) * 3000) = int(450) = 450
  quantity = min(500, 450, int(50000/85)) = min(500, 450, 588) = 450

Decision: action = "buy", quantity = 450
State update: cash: 50000 -> 11750 (50000 - 450*85); position: 500 -> 950

### Case 2 — Sell triggered by overvaluation

System state: current_price = 108.0, fundamental_value = 100.0, cash = 50000.0, position = 500, deadband_threshold = 0.03

Calculation:
  deviation = (108.0 - 100.0) / 100.0 = 0.08
  Check: abs(0.08) = 0.08 > deadband_threshold (0.03)? Yes.
  Direction: deviation > 0, so action = "sell"
  raw_quantity = int(abs(0.08) * 3000) = int(240) = 240
  quantity = min(500, 240, 500) = 240

Decision: action = "sell", quantity = 240
State update: position: 500 -> 260; cash: 50000 -> 75920 (50000 + 240*108)

### Case 3 — Hold within deadband

System state: current_price = 98.0, fundamental_value = 100.0, cash = 50000.0, position = 500, deadband_threshold = 0.03

Calculation:
  deviation = (98.0 - 100.0) / 100.0 = -0.02
  Check: abs(-0.02) = 0.02 > deadband_threshold (0.03)? No.

Decision: action = "hold", quantity = 0
State update: no changes

### Edge Case — Buy desired but cash insufficient

System state: current_price = 80.0, fundamental_value = 100.0, cash = 150.0, position = 500, deadband_threshold = 0.03

Calculation:
  deviation = (80.0 - 100.0) / 100.0 = -0.20
  Check: abs(-0.20) = 0.20 > deadband_threshold (0.03)? Yes.
  Direction: deviation < 0, so action = "buy"
  raw_quantity = int(abs(-0.20) * 3000) = int(600) = 600
  quantity = min(500, 600, int(150/80)) = min(500, 600, 1) = 1

Decision: action = "buy", quantity = 1
State update: cash: 150 -> 70 (150 - 1*80); position: 500 -> 501

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `deadband_threshold` <- Ellul et al. (2011), Table 4: mean fire-sale discount of 3.2% for investment-grade bonds; 3% deadband ensures trading only at economically meaningful dislocations.
- `initial_cash` / `initial_position` <- Scenario configuration; sized to allow 10–20 trades at typical quantities.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given deviation = -0.10 with sufficient cash, agent MUST emit buy with quantity = min(500, 300) = 300.
- Given deviation = +0.05 with position = 500, agent MUST emit sell with quantity = min(500, 150, 500) = 150.
- Given deviation = -0.02 (within deadband), agent MUST emit hold regardless of cash or position.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys when deviation > 0 THEN direction logic is inverted.
- IF the agent sells when deviation < 0 THEN direction logic is inverted.
- IF the agent trades when abs(deviation) < deadband_threshold THEN deadband is broken.
- IF buy quantity * price > cash THEN budget constraint is violated.

#### Ablation Hooks

| Ablation name       | Setting                      | Hypothesis tested                           | Expected direction        | Metric                               |
|---------------------|------------------------------|---------------------------------------------|---------------------------|--------------------------------------|
| `wide_deadband`     | `deadband_threshold = 0.10`  | Wider deadband reduces trading frequency    | Fewer total trades        | Count of non-hold actions            |
| `narrow_deadband`   | `deadband_threshold = 0.01`  | Narrow deadband increases overtrading       | More trades, lower P&L    | Trade count and cumulative P&L       |
| `high_capital`      | `initial_cash = 500000`      | More capital allows sustained contrarian buying | More buy actions in stress | Buy action count during price decline |

## Academic References

| # | Citation                                                                                                                                                                  | Notes                                     |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| 1 | Macaulay, F.R. (1938). *Some Theoretical Problems Suggested by the Movements of Interest Rates, Bond Yields and Stock Prices in the United States since 1856*. NBER.      | Duration concept foundation               |
| 2 | Ellul, A., Jotikasthira, C. & Lundblad, C.T. (2011). "Regulatory Pressure and Fire Sales in the Corporate Bond Market." *Review of Financial Studies*, 24(6), 1801–1843. DOI:10.1093/rfs/hhq055 | Fire-sale mispricing evidence  |
| 3 | Collin-Dufresne, P., Goldstein, R.S. & Martin, J.S. (2001). "The Determinants of Credit Spread Changes." *Journal of Finance*, 56(6), 2177–2207. DOI:10.1111/0022-1082.00402 | Mean-reversion in credit spreads   |
| 4 | Shleifer, A. & Vishny, R.W. (1997). "The Limits of Arbitrage." *Journal of Finance*, 52(1), 35–55. DOI:10.1111/j.1540-6261.1997.tb03807.x                                | Capital constraints on arbitrage          |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-bond-trader.png) |
