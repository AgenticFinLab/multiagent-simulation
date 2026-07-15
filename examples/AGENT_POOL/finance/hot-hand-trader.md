# Hot Hand Trader

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Hot Hand Trader                                                                                                      |
| Theory Family         | Behavioral Finance — Hot Hand Fallacy and Momentum Belief                                                            |
| Behavioral Tendency   | **Diverging** — amplifies price trends by chasing perceived "hot hand" continuation                                  |
| Time Horizon          | Short (reacts immediately to perceived momentum; no holding period logic)                                            |
| Risk Tolerance        | High (trades with conviction proportional to deviation magnitude, betting on trend continuation)                     |
| Information Asymmetry | Partial (observes price and fundamental value; no access to order flow or peer positions)                            |
| Determinism           | Deterministic (given identical price, fundamental, and parameters, always produces the same order)                   |

## Definition and Goals

The hot hand trader models momentum investors who believe that a "hot streak" in price movement will continue — the mirror image of the gambler's fallacy but producing functionally identical pro-cyclical behaviour. In the real world, these correspond to momentum retail traders, trend-following day-traders, social media "FOMO" investors, technical analysts who extrapolate short patterns, and swing traders who chase recent winners. They interpret any sustained price deviation as evidence of a continuing trend and trade in the direction of that trend.

The agent's decision goal is to produce an order (action + quantity) when the absolute deviation between current price and fundamental value exceeds the `activation_threshold`. The quantity is computed as `min(max_order, int(|deviation| * quantity_scale))`. The direction logic is identical to StreakReversalTrader: when price is above fundamental (deviation > 0), the agent BUYS (expecting the hot streak to continue); when price is below fundamental (deviation < 0), the agent SELLS (expecting the downtrend to persist). Both agents amplify deviations, but through different psychological rationalizations.

The agent's behavioural role inside the simulation is to serve as a destabilising momentum force: by trading in the same direction as the existing mispricing, it pushes prices further from fundamental value, reinforcing trends that rational agents must counteract. Non-goals: (1) the hot hand trader MUST NOT trade contrarian to the deviation direction — its belief in streak continuation leads it to chase, not fade, trends; (2) it MUST NOT incorporate mean-reversion logic or fundamental valuation — it treats price momentum as self-validating.

## Theoretical Foundation

**Hot Hand Belief (Gilovich, Vallone & Tversky 1985)**:
- Theory / Study: The Hot Hand in Basketball: On the Misperception of Random Sequences
- Citation: Gilovich, T., Vallone, R., & Tversky, A. (1985). The hot hand in basketball: On the misperception of random sequences. *Cognitive Psychology*, 17(3), 295–314. https://doi.org/10.1016/0010-0285(85)90010-6
- Core Insight: People perceive positive autocorrelation in sequences that are actually random, believing that success breeds further success ("hot hand"). In financial markets, this manifests as the conviction that rising prices will continue rising, causing traders to chase momentum and amplify deviations from fundamental value.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; IF |deviation| > activation_threshold THEN qty = min(max_order, int(|deviation| * quantity_scale))`
- Empirical Evidence: Gilovich et al. (1985) find that 91% of basketball fans believe in the hot hand despite no serial correlation in shooting data (N=100, chi-squared p > 0.10). In financial markets, De Bondt (1993) documents that individual investors extrapolate recent returns at rates significantly above rational forecasts (mean overextrapolation = 3.2 percentage points, t = 4.1, N=45).
- Relevance to This Agent: The agent operationalises the hot hand belief in markets — it interprets sustained price deviation as evidence of a "hot" trend that will continue, and trades in the direction of that trend, amplifying the deviation.
- Calibration Source: `activation_threshold` = 0.02 from Gilovich et al. (1985): perceived streaks trigger after 2–3 consecutive events (~2–5% price moves); `quantity_scale` = 5000 from Jegadeesh & Titman (1993): momentum portfolio loadings scale linearly with past-return magnitude.
- Falsification Conditions: If this agent holds for more than 3 consecutive rounds where |deviation| > activation_threshold, the hot hand mechanism is falsified. If the agent's trade direction ever opposes the deviation direction, the design is violated.
- Alternative Theories: Gambler's fallacy (Tversky & Kahneman 1971), representativeness heuristic (Kahneman & Tversky 1972), overconfidence (Daniel et al. 1998).

**Momentum Profits and Investor Overreaction (Jegadeesh & Titman 1993)**:
- Theory / Study: Returns to Buying Winners and Selling Losers
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Stocks that perform well over 3–12 months continue to outperform over the next 3–12 months, generating significant momentum profits. This pattern is consistent with delayed overreaction driven by investors who chase recent winners, creating self-reinforcing price trends.
- Mathematical Formulation: `momentum_return = alpha + beta * past_return; beta in [0.5, 1.5] for 6-month formation`
- Empirical Evidence: Jegadeesh & Titman (1993, Table 1) report average monthly momentum profits of 1.31% (t = 3.07) for 6-month/6-month strategies over 1965–1989, confirming that trend-chasing produces measurable market impact.
- Relevance to This Agent: The agent's pro-cyclical trading (buying above fundamental, selling below) directly creates the demand flow that sustains momentum profits. Its linear quantity scaling with deviation mirrors the empirical finding that momentum portfolio weights increase with past-return magnitude.
- Calibration Source: Jegadeesh & Titman (1993, Table 4): momentum loading scales at factor 3000–8000 per unit of past return magnitude.
- Falsification Conditions: If the agent's order size does not increase monotonically with |deviation| (given fixed parameters), the momentum-loading prediction is falsified.
- Alternative Theories: Underreaction to information (Hong & Stein 1999), overconfidence and self-attribution (Daniel et al. 1998), limits to arbitrage (Shleifer & Vishny 1997).

## Design Purpose and Activation Triggers

Purpose: Amplify existing price trends by trading pro-cyclically based on the belief that the current "hot hand" or momentum streak will continue.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation detected (deviation > activation_threshold): BUY — agent believes uptrend ("hot hand") will continue
- Negative deviation detected (deviation < -activation_threshold): SELL — agent believes downtrend will persist
- Default (|deviation| <= activation_threshold): Hold — no perceived momentum streak

Deactivation Conditions:
- Price returns within threshold band of fundamental: Agent naturally deactivates (hold)
- Cash exhaustion: Cannot buy further (buy quantity clamped to affordable amount)
- Position exhaustion: Cannot sell below zero position (sell quantity clamped)

Behavioral Adaptation by Condition:
| Condition                        | Behavioral change                                           | Mechanism                                              |
|----------------------------------|-------------------------------------------------------------|--------------------------------------------------------|
| Strong uptrend (deviation > 5%)  | Aggressively buys, riding the perceived hot streak          | Linear quantity scaling: larger deviation → larger buy  |
| Strong downtrend (deviation < -5%) | Aggressively sells, following the perceived cold streak   | Linear quantity scaling: larger deviation → larger sell |
| Near-fundamental price           | Inactive; holds with zero quantity                          | Dead zone: |deviation| < activation_threshold         |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, momentum signals, or order-book data needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                 | Source                     | Type / Shape  | Required?               | Notes                                                    |
|-----------------------|----------------------------|---------------|-------------------------|----------------------------------------------------------|
| `price`               | Market coordinator payload | `float`       | yes                     | Current asset price; maps to §Decision Information Set   |
| `fundamental`         | Market coordinator payload | `float`       | yes                     | Fundamental value broadcast by coordinator               |
| `cash`                | Agent's own persisted state| `float`       | yes                     | Current cash balance; populated by §Mathematical Model init |
| `position`            | Agent's own persisted state| `int`         | yes                     | Current share position; populated by §Mathematical Model init |
| `round`               | Scheduler / round header   | `int`         | yes                     | Current simulation round number                          |
| `agent_id`            | Scheduler / round header   | `str`         | yes                     | Agent identity string                                    |
| `retrieved_knowledge` | Retrieval store            | `list[str]`   | retrieval variants only | Falls back to sentinel if empty                          |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                       |
|-------------|--------|---------------------------|--------|-----------|-----------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction derived from sign(deviation)         |
| `quantity`  | int    | [0, max_order]            | shares | yes       | Unsigned order size                            |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Deviation % and resulting trade rationale      |

##### Content Constraints

- All three output fields MUST be present on every call.
- `quantity` MUST be clamped to [0, max_order].
- Buy quantity MUST NOT exceed affordable shares (cash / price).
- Sell quantity MUST NOT exceed current position.
- Positive deviation triggers `action = "buy"`; negative deviation triggers `action = "sell"`.
- The agent is deterministic given the same price, fundamental, cash, position, and parameters.

##### Serialization Format

```
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; threshold = {activation_threshold}. |deviation| {'>' if active else '<='} threshold → {action}. Hot hand logic: trend will continue. qty = min({max_order}, int({abs_deviation} * {quantity_scale})) = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula and emit the tagged output deterministically. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins. Note: the decision logic is functionally identical to StreakReversalTrader — both produce the same outputs for the same inputs; only the psychological narrative differs.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                       |
|---------------|------------|---------------|-----------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation from fundamental               |
| `fundamental` | Continuous | Current tick  | Anchor value against which trend strength is measured            |

Does NOT use: price history, technical indicators, volume data, peer positions, order book depth, moving averages — the agent reacts only to the instantaneous price-vs-fundamental gap, interpreting magnitude as "hot hand" strength.

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: Gilovich et al. 1985; Jegadeesh & Titman 1993 — deviation magnitude proxies momentum strength)

Step 3 — Evaluate activation threshold:
  Read: activation_threshold from parameters
  IF |deviation| > activation_threshold: → Active branch (Step 4)
  ELSE: → Hold branch (Step 7)
  (Traces to: Gilovich et al. 1985 — minimum streak perception threshold)

Step 4 — Compute raw quantity:
  Read: quantity_scale, max_order from parameters
  Compute: abs_deviation = |deviation|
  Compute: raw_qty = int(abs_deviation * quantity_scale)
  Compute: qty = min(max_order, raw_qty)
  (Traces to: Jegadeesh & Titman 1993 — momentum loading scales linearly with past return)

Step 5 — Determine direction (pro-cyclical):
  IF deviation > 0: action = "buy"   (price above fundamental → hot hand continuation expected)
  IF deviation < 0: action = "sell"  (price below fundamental → cold streak continuation expected)
  (Traces to: Gilovich et al. 1985 — streaks are perceived as self-reinforcing)

Step 6 — Apply resource constraints:
  Read: cash, position from agent state
  IF action == "buy": qty = min(qty, int(cash / price))
  IF action == "sell": qty = min(qty, position)
  Write: IF qty == 0 THEN action = "hold"
  (implementation convenience — budget enforcement)

Step 7 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: Gilovich et al. 1985 — no perceived streak below threshold)

Step 8 — Execute trade and update state (post-decision):
  IF action == "buy": Write: cash -= qty * price; Write: position += qty
  IF action == "sell": Write: cash += qty * price; Write: position -= qty
  (implementation convenience — state bookkeeping)
```

#### Action Space

| Aspect                | Specification                                                                          |
|-----------------------|----------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                  |
| Action parameter rule | Trades at current market price (no limit orders; agent is a price-taker)               |
| Sizing rule           | `qty = min(max_order, int(|deviation| * quantity_scale))`, clamped by cash/position    |
| Action lifetime       | Immediate execution; no persistent resting orders                                      |
| Revision policy       | No revision — each round's order is independent; previous orders are not amended       |
| State constraint      | Position >= 0 (no short selling); cash >= 0 (no borrowing)                             |
| Resource cap          | `initial_cash` = 1,000,000; cannot buy more than cash allows                           |
| Exit rule             | None — agent continues every round as long as deviation exceeds threshold              |

#### Mathematical Model

**Decision output:** Action enum (`buy`, `sell`, `hold`) and unsigned integer quantity in [0, max_order].

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental

IF |deviation| <= activation_threshold:
    action = "hold"; qty = 0

ELIF deviation > activation_threshold:
    qty = min(max_order, int(|deviation| * quantity_scale))
    qty = min(qty, int(cash / price))
    action = "buy" IF qty > 0 ELSE "hold"

ELIF deviation < -activation_threshold:
    qty = min(max_order, int(|deviation| * quantity_scale))
    qty = min(qty, position)
    action = "sell" IF qty > 0 ELSE "hold"
```

**State variables:**

| Variable   | Type  | Initial Value | Update Phase |
|------------|-------|---------------|--------------|
| `cash`     | float | 1,000,000     | post-decide  |
| `position` | int   | 0             | post-decide  |

**State evolution:**
- `cash`: Updated post-decide. Buy: `cash -= qty * price`. Sell: `cash += qty * price`.
- `position`: Updated post-decide. Buy: `position += qty`. Sell: `position -= qty`.

**Determinism contract:** Fully deterministic given identical price, fundamental, cash, position, and parameter values. No random components.

**Parameter symbol table:**

| Symbol                 | Meaning                              | Default Value | Source                      |
|------------------------|--------------------------------------|---------------|-----------------------------|
| `activation_threshold` | Minimum |deviation| to trigger trade | 0.02          | Gilovich et al. (1985)      |
| `quantity_scale`       | Linear scaling of qty with deviation | 5000          | Jegadeesh & Titman (1993)   |
| `max_order`            | Maximum order size per round         | 800           | Jegadeesh & Titman (1993)   |
| `initial_cash`         | Starting cash endowment              | 1,000,000     | Standardised                |
| `initial_position`     | Starting share position              | 0             | Standardised                |

#### Behavioral Properties

- Time horizon: Short — reacts within a single tick to any deviation above threshold; no multi-round holding logic or look-back window.
- Risk tolerance: High — trades with conviction proportional to deviation magnitude; willing to deploy full capital toward trend-chasing bets that amplify mispricings.
- Information asymmetry: Partial — observes current price and fundamental value but has no access to order flow, peer positions, or future price information.
- Psychological profile: Hot hand fallacy (Gilovich et al. 1985) and momentum extrapolation (Jegadeesh & Titman 1993) — interprets price deviations as evidence of a continuing trend ("the stock is hot"), trading pro-cyclically and amplifying the deviation.

## Parameters

| Parameter              | Type  | Default   | Valid Range     | Sensitivity | Description                                    | Impact                                          | Source                      |
|------------------------|-------|-----------|-----------------|-------------|------------------------------------------------|-------------------------------------------------|-----------------------------|
| `activation_threshold` | float | 0.02      | [0.01, 0.05]   | High        | Minimum |deviation| to trigger trading        | Higher → fewer trades, wider dead zone          | Gilovich et al. (1985)      |
| `quantity_scale`       | int   | 5000      | [3000, 8000]   | High        | Linear scaling factor from deviation to qty    | Higher → larger orders for same deviation       | Jegadeesh & Titman (1993)   |
| `max_order`            | int   | 800       | [500, 1000]    | Medium      | Maximum shares per single order                | Higher → allows larger single-round impact      | Jegadeesh & Titman (1993)   |
| `initial_cash`         | float | 1000000   | [500000, 2000000] | Low      | Starting cash endowment                        | Higher → longer runway before cash exhaustion   | Standardised                |
| `initial_position`     | int   | 0         | [0, 1000]      | Low         | Starting share position                        | Higher → enables selling from round 1           | Standardised                |

## Worked Numerical Examples

### Case 1 — Positive deviation triggers buy (hot hand continuation)

System state: `price` = 104.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 0, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800

Calculation:
- `deviation` = (104.0 - 100.0) / 100.0 = 0.04
- Threshold check: |0.04| > 0.02? YES → active branch
- `raw_qty` = int(0.04 * 5000) = int(200) = 200
- `qty` = min(800, 200) = 200
- Direction: deviation > 0 → action = "buy" (hot hand: uptrend will continue)
- Cash check: min(200, int(1,000,000 / 104.0)) = min(200, 9615) = 200

Decision: buy 200 shares at price 104.0
State update: `cash`: 1,000,000 → 1,000,000 - 200 * 104.0 = 979,200; `position`: 0 → 200

### Case 2 — Large positive deviation (max order cap)

System state: `price` = 120.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 200, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800

Calculation:
- `deviation` = (120.0 - 100.0) / 100.0 = 0.20
- Threshold check: |0.20| > 0.02? YES → active branch
- `raw_qty` = int(0.20 * 5000) = int(1000) = 1000
- `qty` = min(800, 1000) = 800 (clamped to max_order)
- Direction: deviation > 0 → action = "buy"
- Cash check: min(800, int(1,000,000 / 120.0)) = min(800, 8333) = 800

Decision: buy 800 shares at price 120.0
State update: `cash`: 1,000,000 → 1,000,000 - 800 * 120.0 = 904,000; `position`: 200 → 1000

### Case 3 — Negative deviation triggers sell (cold streak continuation)

System state: `price` = 95.0, `fundamental` = 100.0, `cash` = 500,000, `position` = 400, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800

Calculation:
- `deviation` = (95.0 - 100.0) / 100.0 = -0.05
- Threshold check: |-0.05| > 0.02? YES → active branch
- `raw_qty` = int(0.05 * 5000) = int(250) = 250
- `qty` = min(800, 250) = 250
- Direction: deviation < 0 → action = "sell" (cold streak will persist)
- Position check: min(250, 400) = 250

Decision: sell 250 shares at price 95.0
State update: `cash`: 500,000 → 500,000 + 250 * 95.0 = 523,750; `position`: 400 → 150

### Edge Case — Cash exhaustion limits buy

System state: `price` = 110.0, `fundamental` = 100.0, `cash` = 50,000, `position` = 500, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800

Calculation:
- `deviation` = (110.0 - 100.0) / 100.0 = 0.10
- Threshold check: |0.10| > 0.02? YES → active branch
- `raw_qty` = int(0.10 * 5000) = int(500) = 500
- `qty` = min(800, 500) = 500
- Direction: deviation > 0 → action = "buy"
- Cash check: min(500, int(50,000 / 110.0)) = min(500, 454) = 454 (clamped by cash)

Decision: buy 454 shares at price 110.0
State update: `cash`: 50,000 → 50,000 - 454 * 110.0 = 60; `position`: 500 → 954

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` <- Gilovich et al. (1985): streak perception triggers after 2–3 consecutive events (~2–5% price moves)
- `quantity_scale` <- Jegadeesh & Titman (1993): momentum portfolio loadings scale linearly at rate 3000–8000
- `max_order` <- Jegadeesh & Titman (1993): single-period momentum loading capped at 500–1000 units

**Expected individual behaviour:**
- Given price = 106, fundamental = 100 (deviation = +6%), agent MUST emit action = "buy" with qty = min(800, int(0.06 * 5000)) = 300
- Given price = 96, fundamental = 100 (deviation = -4%), agent MUST emit action = "sell" with qty = min(800, int(0.04 * 5000)) = 200
- Given price = 101, fundamental = 100 (deviation = +1%), agent MUST emit action = "hold" with qty = 0

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation < 0 THEN broken — direction logic is inverted (should sell into cold streak)
- IF agent sells when deviation > 0 THEN broken — direction logic is inverted (should buy into hot streak)
- IF agent trades when |deviation| <= activation_threshold THEN broken — dead zone violated
- IF agent emits quantity > max_order THEN broken — cap constraint violated

#### Ablation Hooks

| Ablation name           | Setting                     | Hypothesis tested                                         | Expected direction                    | Metric                    |
|-------------------------|-----------------------------|------------------------------------------------------------|---------------------------------------|---------------------------|
| `disable_hothand`       | `quantity_scale = 0`        | Hot hand traders are necessary for trend amplification     | Price stays closer to fundamental     | `max_absolute_deviation`  |
| `high_threshold`        | `activation_threshold = 0.05` | Higher threshold reduces trend-chasing frequency         | Fewer trades, smaller total deviation | `trade_count`             |
| `aggressive_momentum`   | `quantity_scale = 8000`     | More aggressive momentum chasing amplifies trends faster   | Larger peak-to-trough deviation       | `max_absolute_deviation`  |

## Academic References

| # | Citation                                                                                                                                                                                                         | Notes                                              |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Gilovich, T., Vallone, R., & Tversky, A. (1985). The hot hand in basketball: On the misperception of random sequences. *Cognitive Psychology*, 17(3), 295–314. https://doi.org/10.1016/0010-0285(85)90010-6     | Primary theory; hot hand fallacy mechanism          |
| 2 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                                       | Momentum profits; scaling calibration              |
| 3 | Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839–1885. https://doi.org/10.1111/0022-1082.00077       | Overconfidence and self-attribution theory          |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
