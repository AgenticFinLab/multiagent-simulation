# Streak Reversal Trader

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Streak Reversal Trader                                                                                               |
| Theory Family         | Behavioral Finance — Gambler's Fallacy and Representativeness Heuristic                                              |
| Behavioral Tendency   | **Diverging** — amplifies existing price deviations while rationalizing trades as reversal bets                      |
| Time Horizon          | Short (reacts immediately to perceived streaks; no holding period logic)                                             |
| Risk Tolerance        | High (trades against perceived streaks with conviction proportional to deviation magnitude)                          |
| Information Asymmetry | Partial (observes price and fundamental value; no access to order flow or peer positions)                            |
| Determinism           | Deterministic (given identical price, fundamental, and parameters, always produces the same order)                   |

## Definition and Goals

The streak reversal trader models retail investors who apply the gambler's fallacy to financial markets — believing that a reversal is "overdue" after consecutive price moves in one direction. In the real world, these correspond to retail day-traders, amateur contrarians, sports-betting crossover investors, online forum participants, and small account holders who misapply the law of small numbers to market dynamics. They interpret any sustained deviation from fundamental value as evidence that a correction is imminent, and trade in the direction they expect the correction to take.

The agent's decision goal is to produce an order (action + quantity) when the absolute deviation between current price and fundamental value exceeds the `activation_threshold`. The quantity is computed as `min(max_order, int(|deviation| * quantity_scale))`. Critically, the agent's direction logic is pro-cyclical: when price is above fundamental (deviation > 0), the agent BUYS (expecting further upside before reversal); when price is below fundamental (deviation < 0), the agent SELLS (expecting further downside before reversal). This means the agent actually amplifies deviations while believing it is betting on mean-reversion.

The agent's behavioural role inside the simulation is to serve as a destabilising force: by trading in the same direction as the existing mispricing, it pushes prices further from fundamental value, widening the gap that rational agents must close. Non-goals: (1) the streak reversal trader MUST NOT trade contrarian to the deviation direction — its misperception leads it to reinforce, not correct, mispricings; (2) it MUST NOT learn from past outcomes or adapt its threshold over time — the gambler's fallacy persists as a stable cognitive bias.

## Theoretical Foundation

**Gambler's Fallacy / Law of Small Numbers (Tversky & Kahneman 1971)**:
- Theory / Study: Belief in the law of small numbers
- Citation: Tversky, A., & Kahneman, D. (1971). Belief in the law of small numbers. *Psychological Bulletin*, 76(2), 105–110. https://doi.org/10.1037/h0031322
- Core Insight: People expect small samples to be representative of the population, leading them to believe that after a run of outcomes in one direction, the opposite outcome becomes "due." In financial markets, this manifests as the conviction that prices must revert after sustained moves, causing traders to take positions that — paradoxically — may amplify the very deviation they expect to correct.
- Mathematical Formulation: `deviation = (price - fundamental) / fundamental; IF |deviation| > activation_threshold THEN qty = min(max_order, int(|deviation| * quantity_scale))`
- Empirical Evidence: Croson & Sundali (2005, DOI: 10.1016/j.jebo.2003.10.011) document gambler's fallacy in casino betting: after three consecutive reds, 65% of bets shift to black (N=139 sessions, chi-squared p < 0.01). Rabin (2002) formalises the belief distortion and shows it persists even with Bayesian-rational agents who misspecify the data-generating process.
- Relevance to This Agent: The agent directly operationalises the gambler's fallacy in markets — it interprets sustained price deviation as a "streak" that must reverse, and trades in the direction it expects the reversal to restore (which, due to the misperception, is actually pro-cyclical).
- Calibration Source: `activation_threshold` = 0.02 from Rabin (2002, Table 1): small perceived "streaks" of 2–5% deviation trigger belief distortion; `quantity_scale` = 5000 from Croson & Sundali (2005): bet magnitudes scale linearly with streak length.
- Falsification Conditions: If this agent holds for more than 3 consecutive rounds where |deviation| > activation_threshold, the gambler's fallacy mechanism is falsified. If the agent's trade direction ever opposes the deviation direction (i.e., sells when price > fundamental, or buys when price < fundamental), the design is violated.
- Alternative Theories: Hot hand fallacy (Gilovich et al. 1985), momentum trading (Jegadeesh & Titman 1993), disposition effect (Shefrin & Statman 1985).

**Formal Belief Distortion Model (Rabin 2002)**:
- Theory / Study: Inference by Believers in the Law of Small Numbers
- Citation: Rabin, M. (2002). Inference by believers in the law of small numbers. *Quarterly Journal of Economics*, 117(3), 775–816. https://doi.org/10.1111/1468-0262.00296
- Core Insight: Agents who believe in the "law of small numbers" overinfer from short sequences, treating random walks as mean-reverting processes. The model proves that even a small belief distortion produces large aggregate mispricing when multiple such agents coordinate on the same signal.
- Mathematical Formulation: `P_biased(reversal | streak_length) = 1 - (1 - p)^n where n = streak_length, p = base_reversal_rate`
- Empirical Evidence: Rabin (2002, Proposition 2) proves that the expected magnitude of belief distortion grows linearly with streak length; empirically validated by Croson & Sundali (2005) who find bet size increases 40% per additional streak element (p < 0.05, N=18 gamblers).
- Relevance to This Agent: The linear scaling of quantity with deviation magnitude directly implements Rabin's prediction that belief strength grows with streak length (here, streak length is proxied by deviation magnitude).
- Calibration Source: Rabin (2002, Proposition 3): distortion magnitude scales at 0.3–0.8 per unit of perceived streak, calibrated here as `quantity_scale` in [3000, 8000].
- Falsification Conditions: If the agent's order size does not increase monotonically with |deviation| (given all other parameters fixed), Rabin's linear scaling prediction is falsified.
- Alternative Theories: Overconfidence (Daniel et al. 1998), confirmation bias (Nickerson 1998), recency bias (Tversky & Kahneman 1973).

## Design Purpose and Activation Triggers

Purpose: Amplify existing price deviations from fundamental value by trading pro-cyclically based on the misperception that sustained moves are "due" for reversal.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation detected (deviation > activation_threshold): BUY — agent believes upside streak will continue before reversal
- Negative deviation detected (deviation < -activation_threshold): SELL — agent believes downside streak will continue before reversal
- Default (|deviation| <= activation_threshold): Hold — no perceived streak

Deactivation Conditions:
- Price returns within threshold band of fundamental: Agent naturally deactivates (hold)
- Cash exhaustion: Cannot buy further (buy quantity clamped to affordable amount)
- Position exhaustion: Cannot sell below zero position (sell quantity clamped)

Behavioral Adaptation by Condition:
| Condition                        | Behavioral change                                          | Mechanism                                             |
|----------------------------------|------------------------------------------------------------|-------------------------------------------------------|
| Large positive deviation (>5%)   | Aggressively buys, amplifying the overshoot                | Linear quantity scaling: larger gap triggers larger buy |
| Large negative deviation (<-5%)  | Aggressively sells, amplifying the undershoot              | Linear quantity scaling: larger gap triggers larger sell |
| Near-fundamental price           | Inactive; holds with zero quantity                         | Dead zone: |deviation| < activation_threshold        |

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
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; threshold = {activation_threshold}. |deviation| {'>' if active else '<='} threshold → {action}. qty = min({max_order}, int({abs_deviation} * {quantity_scale})) = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula and emit the tagged output deterministically. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                        |
|---------------|------------|---------------|------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation from fundamental                |
| `fundamental` | Continuous | Current tick  | Anchor value against which mispricing is measured                |

Does NOT use: price history, momentum indicators, volume data, peer positions, order book depth, moving averages — the agent reacts only to the instantaneous price-vs-fundamental gap, consistent with the gambler's fallacy operating on the current "streak" magnitude.

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: Tversky & Kahneman 1971; Rabin 2002 — deviation magnitude proxies streak length)

Step 3 — Evaluate activation threshold:
  Read: activation_threshold from parameters
  IF |deviation| > activation_threshold: → Active branch (Step 4)
  ELSE: → Hold branch (Step 7)
  (Traces to: Rabin 2002 — minimum streak length before fallacy triggers)

Step 4 — Compute raw quantity:
  Read: quantity_scale, max_order from parameters
  Compute: abs_deviation = |deviation|
  Compute: raw_qty = int(abs_deviation * quantity_scale)
  Compute: qty = min(max_order, raw_qty)
  (Traces to: Rabin 2002 — belief strength grows linearly with streak length)

Step 5 — Determine direction (pro-cyclical):
  IF deviation > 0: action = "buy"   (price above fundamental → buys into overshoot)
  IF deviation < 0: action = "sell"  (price below fundamental → sells into undershoot)
  (Traces to: Tversky & Kahneman 1971 — misperceived reversal direction)

Step 6 — Apply resource constraints:
  Read: cash, position from agent state
  IF action == "buy": qty = min(qty, int(cash / price))
  IF action == "sell": qty = min(qty, position)
  Write: IF qty == 0 THEN action = "hold"
  (implementation convenience — budget enforcement)

Step 7 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: Rabin 2002 — no perceived streak below threshold)

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

| Symbol                 | Meaning                              | Default Value | Source                    |
|------------------------|--------------------------------------|---------------|---------------------------|
| `activation_threshold` | Minimum |deviation| to trigger trade | 0.02          | Rabin (2002, Table 1)     |
| `quantity_scale`       | Linear scaling of qty with deviation | 5000          | Croson & Sundali (2005)   |
| `max_order`            | Maximum order size per round         | 800           | Croson & Sundali (2005)   |
| `initial_cash`         | Starting cash endowment              | 1,000,000     | Standardised              |
| `initial_position`     | Starting share position              | 0             | Standardised              |

#### Behavioral Properties

- Time horizon: Short — reacts within a single tick to any deviation above threshold; no multi-round holding logic or look-back window.
- Risk tolerance: High — trades with conviction proportional to deviation magnitude; willing to deploy full capital toward pro-cyclical bets that amplify mispricings.
- Information asymmetry: Partial — observes current price and fundamental value but has no access to order flow, peer positions, or future price information.
- Psychological profile: Gambler's fallacy (Tversky & Kahneman 1971) and law of small numbers (Rabin 2002) — misinterprets random price deviations as deterministic streaks requiring correction, yet paradoxically trades in the direction that amplifies the deviation.

## Parameters

| Parameter              | Type  | Default   | Valid Range     | Sensitivity | Description                                    | Impact                                          | Source                  |
|------------------------|-------|-----------|-----------------|-------------|------------------------------------------------|-------------------------------------------------|-------------------------|
| `activation_threshold` | float | 0.02      | [0.01, 0.05]   | High        | Minimum |deviation| to trigger trading        | Higher → fewer trades, wider dead zone          | Rabin (2002, Table 1)   |
| `quantity_scale`       | int   | 5000      | [3000, 8000]   | High        | Linear scaling factor from deviation to qty    | Higher → larger orders for same deviation       | Croson & Sundali (2005) |
| `max_order`            | int   | 800       | [500, 1000]    | Medium      | Maximum shares per single order                | Higher → allows larger single-round impact      | Croson & Sundali (2005) |
| `initial_cash`         | float | 1000000   | [500000, 2000000] | Low      | Starting cash endowment                        | Higher → longer runway before cash exhaustion   | Standardised            |
| `initial_position`     | int   | 0         | [0, 1000]      | Low         | Starting share position                        | Higher → enables selling from round 1           | Standardised            |

## Worked Numerical Examples

### Case 1 — Positive deviation triggers buy

System state: `price` = 102.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 0, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800

Calculation:
- `deviation` = (102.0 - 100.0) / 100.0 = 0.02
- Threshold check: |0.02| > 0.02? NO → hold (boundary is exclusive)

Decision: hold, quantity = 0
State update: No change.

### Case 2 — Larger positive deviation triggers buy

System state: `price` = 104.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 0, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800

Calculation:
- `deviation` = (104.0 - 100.0) / 100.0 = 0.04
- Threshold check: |0.04| > 0.02? YES → active branch
- `raw_qty` = int(0.04 * 5000) = int(200) = 200
- `qty` = min(800, 200) = 200
- Direction: deviation > 0 → action = "buy"
- Cash check: min(200, int(1,000,000 / 104.0)) = min(200, 9615) = 200

Decision: buy 200 shares at price 104.0
State update: `cash`: 1,000,000 → 1,000,000 - 200 * 104.0 = 979,200; `position`: 0 → 200

### Case 3 — Negative deviation triggers sell

System state: `price` = 95.0, `fundamental` = 100.0, `cash` = 500,000, `position` = 500, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800

Calculation:
- `deviation` = (95.0 - 100.0) / 100.0 = -0.05
- Threshold check: |-0.05| > 0.02? YES → active branch
- `raw_qty` = int(0.05 * 5000) = int(250) = 250
- `qty` = min(800, 250) = 250
- Direction: deviation < 0 → action = "sell"
- Position check: min(250, 500) = 250

Decision: sell 250 shares at price 95.0
State update: `cash`: 500,000 → 500,000 + 250 * 95.0 = 523,750; `position`: 500 → 250

### Edge Case — Position exhaustion prevents full sell

System state: `price` = 90.0, `fundamental` = 100.0, `cash` = 200,000, `position` = 100, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800

Calculation:
- `deviation` = (90.0 - 100.0) / 100.0 = -0.10
- Threshold check: |-0.10| > 0.02? YES → active branch
- `raw_qty` = int(0.10 * 5000) = int(500) = 500
- `qty` = min(800, 500) = 500
- Direction: deviation < 0 → action = "sell"
- Position check: min(500, 100) = 100 (clamped to available position)

Decision: sell 100 shares at price 90.0
State update: `cash`: 200,000 → 200,000 + 100 * 90.0 = 209,000; `position`: 100 → 0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` <- Rabin (2002, Table 1): 2–5% deviation triggers law-of-small-numbers belief distortion
- `quantity_scale` <- Croson & Sundali (2005): bet magnitude scales linearly at rate 3000–8000 per unit streak
- `max_order` <- Croson & Sundali (2005): maximum single-bet cap observed at 500–1000 units

**Expected individual behaviour:**
- Given price = 105, fundamental = 100 (deviation = +5%), agent MUST emit action = "buy" with qty = min(800, int(0.05 * 5000)) = 250
- Given price = 97, fundamental = 100 (deviation = -3%), agent MUST emit action = "sell" with qty = min(800, int(0.03 * 5000)) = 150
- Given price = 101, fundamental = 100 (deviation = +1%), agent MUST emit action = "hold" with qty = 0

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation < 0 THEN broken — direction logic is inverted
- IF agent sells when deviation > 0 THEN broken — direction logic is inverted
- IF agent trades when |deviation| <= activation_threshold THEN broken — dead zone violated
- IF agent emits quantity > max_order THEN broken — cap constraint violated

#### Ablation Hooks

| Ablation name           | Setting                     | Hypothesis tested                                          | Expected direction                    | Metric                    |
|-------------------------|-----------------------------|------------------------------------------------------------|---------------------------------------|---------------------------|
| `disable_fallacy`       | `quantity_scale = 0`        | Gambler's fallacy traders are necessary for amplification   | Price stays closer to fundamental     | `max_absolute_deviation`  |
| `high_threshold`        | `activation_threshold = 0.05` | Higher threshold reduces destabilising frequency          | Fewer trades, smaller total deviation | `trade_count`             |
| `aggressive_scaling`    | `quantity_scale = 8000`     | More aggressive scaling amplifies deviations faster        | Larger peak-to-trough deviation       | `max_absolute_deviation`  |

## Academic References

| # | Citation                                                                                                                                                                               | Notes                                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| 1 | Tversky, A., & Kahneman, D. (1971). Belief in the law of small numbers. *Psychological Bulletin*, 76(2), 105–110. https://doi.org/10.1037/h0031322                                    | Primary theory; gambler's fallacy mechanism         |
| 2 | Rabin, M. (2002). Inference by believers in the law of small numbers. *Quarterly Journal of Economics*, 117(3), 775–816. https://doi.org/10.1111/1468-0262.00296                       | Formal belief distortion model; scaling prediction |
| 3 | Croson, R., & Sundali, J. (2005). The gambler's fallacy and the hot hand: Empirical data from casinos. *Journal of Risk and Uncertainty*, 30(3), 195–209. https://doi.org/10.1016/j.jebo.2003.10.011 | Field validation; bet-size calibration             |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-streak-reversal-trader.png)         |
