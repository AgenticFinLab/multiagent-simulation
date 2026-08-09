# Outcome Learner

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Outcome Learner                                                                                                      |
| Theory Family         | Behavioral Finance — Outcome Bias and Asymmetric Attribution                                                         |
| Behavioral Tendency   | **Diverging** — amplifies momentum asymmetrically by attributing gains to skill and losses to luck                   |
| Time Horizon          | Short (reacts within a single tick to deviations; no multi-round holding logic)                                      |
| Risk Tolerance        | High (trades with magnified conviction on positive deviations due to self-attribution)                               |
| Information Asymmetry | Partial (observes price and fundamental value; no access to order flow or private information)                       |
| Determinism           | Deterministic (given identical inputs and parameters, always produces the same order)                                |

## Definition and Goals

The outcome learner models investors who exhibit outcome bias — judging the quality of past decisions by their results rather than by the decision process. When the market is above fundamental (positive deviation), the agent attributes the situation to skill and amplifies future trades via `success_attribution`. When the market is below fundamental (negative deviation), the agent discounts the loss as bad luck via `failure_discount`, maintaining baseline trading size rather than learning to reduce exposure. In the real world, these correspond to overconfident retail traders, momentum investors with survivorship-biased track records, hedge fund managers exhibiting self-attribution bias, and social-media traders who publicise wins and hide losses.

The agent's decision goal is to produce an order (action + quantity) when the absolute deviation between current price and fundamental value exceeds `activation_threshold`. The asymmetric formula uses `attribution_scale = success_attribution if deviation > 0 else failure_discount`, yielding `qty = min(max_order, int(|deviation| * quantity_scale * attribution_scale))`. Direction follows the sign of the deviation — the agent chases momentum but with asymmetric intensity.

The agent's behavioural role inside the simulation is to serve as an asymmetric diverging force: it amplifies upside momentum more aggressively than downside, creating a characteristic bullish bias in trending markets. Non-goals: (1) the agent MUST NOT trade contrarian to the observed deviation — its outcome bias prevents learning from mispricing; (2) the agent MUST NOT apply symmetric scaling — the entire mechanism depends on the asymmetry between gain and loss attribution.

## Theoretical Foundation

**Outcome Bias (Fischhoff & Beyth 1975)**:
- Theory / Study: "I Knew It Would Happen": Remembered Probabilities of Once-Future Things
- Citation: Fischhoff, B., & Beyth, R. (1975). "I knew it would happen": Remembered probabilities of once-future things. *Organizational Behavior and Human Performance*, 13(1), 1–16. https://doi.org/10.1016/0030-5073(75)90002-1
- Core Insight: People retrospectively distort their recalled predictions toward the actual outcome, convincing themselves they predicted it correctly. In financial contexts, this creates asymmetric learning: profitable outcomes are remembered as skilled predictions, while losses are reframed as external bad luck — preventing corrective learning and perpetuating overtrading.
- Mathematical Formulation: `attribution_scale = success_attribution (1.3) if deviation > 0 else failure_discount (1.0); qty = min(max_order, int(|deviation| * quantity_scale * attribution_scale))`
- Empirical Evidence: Fischhoff & Beyth (1975, Study 1) found subjects shifted recalled predictions toward actual outcomes by 0.5–1.5 scale points on average (N=150, paired t-test p<0.001). Baron & Hershey (1988) confirmed outcome bias in investment decisions: positive-outcome decisions rated 1.2 SD higher than identical-process negative-outcome decisions.
- Relevance to This Agent: The agent operationalises outcome bias through asymmetric attribution: gains inflate confidence (success_attribution > 1.0) while losses maintain baseline (failure_discount = 1.0), producing systematically larger buy orders than sell orders for equal-magnitude deviations.
- Calibration Source: `success_attribution` = 1.3 from Fischhoff & Beyth (1975): recalled probability shifts of 30–50% toward outcomes; conservative midpoint 1.3. `failure_discount` = 1.0 from Odean (1998): losers held at baseline rates.
- Falsification Conditions: If this agent produces identical order sizes for +X% and -X% deviations (symmetry), the outcome bias mechanism is falsified. If the agent reduces size on negative deviations below failure_discount * baseline, the mechanism is incorrectly implemented.
- Alternative Theories: Hindsight bias (Fischhoff 1975), disposition effect (Shefrin & Statman 1985), overconfidence (Daniel et al. 1998).

**Overconfident Trading (Odean 1998; Barber & Odean 2000)**:
- Theory / Study: Volume, Volatility, Price, and Profit When All Traders Are Above Average; Trading Is Hazardous to Your Wealth
- Citation: Odean, T. (1998). Volume, volatility, price, and profit when all traders are above average. *Journal of Finance*, 53(6), 1887–1934. https://doi.org/10.1111/0022-1082.00259; Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. *Journal of Finance*, 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226
- Core Insight: Overconfident traders trade too much and hold losers too long because they attribute gains to ability (reinforcing future trading) and losses to bad luck (failing to reduce exposure). This produces asymmetric momentum: stronger buying into rising markets than selling into falling ones.
- Mathematical Formulation: `trade_frequency ∝ confidence_level; confidence_level = base + gain_count * attribution_boost`
- Empirical Evidence: Barber & Odean (2000, Table IV) document that the most active quintile of traders (turnover > 250% annually) underperform the least active by 7.1 percentage points annually (t=5.2, N=66,465 households, 1991–1996), consistent with overconfidence-driven excessive trading.
- Relevance to This Agent: The asymmetric attribution mechanism directly implements the Odean (1998) finding: gains reinforce trading (success_attribution > 1.0) while losses fail to reduce it (failure_discount = 1.0), producing the characteristic overtrade pattern.
- Calibration Source: Odean (1998, Section IV): overconfident traders increase trade size by 20–60% following gains; `success_attribution` range [1.0, 2.5] brackets this. Barber & Odean (2000): baseline trade maintained despite losses; `failure_discount` = 1.0.
- Falsification Conditions: If the agent's average buy quantity does not exceed its average sell quantity (in magnitude) over a symmetric deviation distribution, the asymmetric attribution is not implemented.
- Alternative Theories: Rational learning (Berk & Green 2004), prospect theory (Kahneman & Tversky 1979), representativeness (Kahneman & Tversky 1972).

## Design Purpose and Activation Triggers

Purpose: Amplify price trends asymmetrically by attributing gains to skill (inflating buys) and losses to luck (maintaining sell baseline), producing a bullish-biased momentum pattern.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation detected (deviation > activation_threshold): BUY with success_attribution scaling — agent attributes prior gains to skill
- Negative deviation detected (deviation < -activation_threshold): SELL with failure_discount scaling — agent attributes losses to luck, maintains baseline
- Default (|deviation| <= activation_threshold): Hold — no outcome to attribute

Deactivation Conditions:
- Price returns within threshold band of fundamental: Agent naturally deactivates (hold)
- Cash exhaustion: Cannot buy further (buy quantity clamped to affordable amount)
- Position exhaustion: Cannot sell below zero position (sell quantity clamped)

Behavioral Adaptation by Condition:
| Condition                         | Behavioral change                                                   | Mechanism                                                           |
|-----------------------------------|---------------------------------------------------------------------|---------------------------------------------------------------------|
| Strong positive deviation (>5%)   | Aggressively buys with success attribution amplification            | success_attribution multiplier inflates buy size above rational     |
| Strong negative deviation (<-5%)  | Sells at baseline rate without attribution inflation                | failure_discount = 1.0 maintains baseline; no panic amplification   |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `fundamental` fields. No peer-action summaries, order-book data, or historical price sequences needed.

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

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                         |
|-------------|--------|---------------------------|--------|-----------|------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction derived from sign(deviation)           |
| `quantity`  | int    | [0, max_order]            | shares | yes       | Unsigned order size (asymmetrically scaled)      |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Attribution logic and trade rationale            |

##### Content Constraints

- All three output fields MUST be present on every call.
- `quantity` MUST be clamped to [0, max_order].
- Buy quantity MUST NOT exceed affordable shares (cash / price).
- Sell quantity MUST NOT exceed current position.
- Positive deviation triggers `action = "buy"` with success_attribution; negative triggers `action = "sell"` with failure_discount.
- The agent is deterministic given the same price, fundamental, cash, position, and parameters.
- Sign convention: positive quantity with action "buy" = purchase; positive quantity with action "sell" = disposal.

##### Serialization Format

```
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; threshold = {activation_threshold}. |deviation| {'>' if active else '<='} threshold → {action}. Attribution: {'success → skill (×' + str(success_attribution) + ')' if deviation > 0 else 'failure → luck (×' + str(failure_discount) + ')'}. qty = min({max_order}, int({abs_deviation} × {quantity_scale} × {attribution_scale})) = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula with asymmetric attribution and emit the tagged output deterministically. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                     |
|---------------|------------|---------------|-------------------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation from fundamental                             |
| `fundamental` | Continuous | Current tick  | Anchor value against which outcome attribution is assessed                    |

Does NOT use: price history, trade outcomes log, technical indicators, volume data, peer positions, order book depth — the agent uses only instantaneous deviation sign to determine attribution frame (positive = success; negative = failure).

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: Fischhoff & Beyth 1975 — deviation direction determines attribution frame)

Step 3 — Evaluate activation threshold:
  Read: activation_threshold from parameters
  IF |deviation| > activation_threshold: → Active branch (Step 4)
  ELSE: → Hold branch (Step 8)
  (Traces to: Odean 1998 — minimum trading threshold for overconfident traders)

Step 4 — Determine attribution scale (asymmetric):
  Read: success_attribution, failure_discount from parameters
  IF deviation > 0: attribution_scale = success_attribution   (gain → skill)
  IF deviation < 0: attribution_scale = failure_discount      (loss → luck)
  (Traces to: Fischhoff & Beyth 1975 — asymmetric recalled certainty)

Step 5 — Compute raw quantity with attribution:
  Read: quantity_scale, max_order from parameters
  Compute: abs_deviation = |deviation|
  Compute: raw_qty = int(abs_deviation * quantity_scale * attribution_scale)
  Compute: qty = min(max_order, raw_qty)
  (Traces to: Odean 1998 — overconfident traders scale with attribution)

Step 6 — Determine direction (pro-cyclical):
  IF deviation > 0: action = "buy"   (price above fundamental → skill-confirmed trend)
  IF deviation < 0: action = "sell"  (price below fundamental → unlucky but trade anyway)
  (Traces to: Barber & Odean 2000 — overconfident traders trade in signal direction)

Step 7 — Apply resource constraints:
  Read: cash, position from agent state
  IF action == "buy": qty = min(qty, int(cash / price))
  IF action == "sell": qty = min(qty, position)
  Write: IF qty == 0 THEN action = "hold"
  (implementation convenience — budget enforcement)

Step 8 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: Odean 1998 — insufficient deviation to trigger trade)

Step 9 — Execute trade and update state (post-decision):
  IF action == "buy": Write: cash -= qty * price; Write: position += qty
  IF action == "sell": Write: cash += qty * price; Write: position -= qty
  (implementation convenience — state bookkeeping)
```

#### Action Space

| Aspect                | Specification                                                                                        |
|-----------------------|------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                |
| Action parameter rule | Trades at current market price (no limit orders; agent is a price-taker)                             |
| Sizing rule           | `qty = min(max_order, int(|deviation| * quantity_scale * attribution_scale))`, clamped by cash/position |
| Action lifetime       | Immediate execution; no persistent resting orders                                                    |
| Revision policy       | No revision — each round's order is independent; previous orders are not amended                     |
| State constraint      | Position >= 0 (no short selling); cash >= 0 (no borrowing)                                           |
| Resource cap          | `initial_cash` = 1,000,000; cannot buy more than cash allows                                         |
| Exit rule             | None — agent continues every round as long as deviation exceeds threshold                            |

#### Mathematical Model

**Decision output:** Action enum (`buy`, `sell`, `hold`) and unsigned integer quantity in [0, max_order].

**Decision logic formalization:**

```
deviation = (price - fundamental) / fundamental

IF |deviation| <= activation_threshold:
    action = "hold"; qty = 0

ELIF deviation > activation_threshold:
    attribution_scale = success_attribution
    qty = min(max_order, int(|deviation| * quantity_scale * attribution_scale))
    qty = min(qty, int(cash / price))
    action = "buy" IF qty > 0 ELSE "hold"

ELIF deviation < -activation_threshold:
    attribution_scale = failure_discount
    qty = min(max_order, int(|deviation| * quantity_scale * attribution_scale))
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

| Symbol                 | Meaning                                        | Default Value | Source                      |
|------------------------|------------------------------------------------|---------------|-----------------------------|
| `activation_threshold` | Minimum |deviation| to trigger trade           | 0.02          | Odean (1998)                |
| `quantity_scale`       | Base linear scaling of qty with deviation       | 5000          | Barber & Odean (2000)       |
| `max_order`            | Maximum order size per round                    | 800           | Barber & Odean (2000)       |
| `success_attribution`  | Gain → skill multiplier (inflates buy size)     | 1.3           | Fischhoff & Beyth (1975)    |
| `failure_discount`     | Loss → luck multiplier (maintains sell baseline)| 1.0           | Odean (1998)                |
| `initial_cash`         | Starting cash endowment                         | 1,000,000     | Standardised                |
| `initial_position`     | Starting share position                         | 0             | Standardised                |

#### Behavioral Properties

- Time horizon: Short — reacts within a single tick to any deviation above threshold; no multi-round holding logic or look-back window.
- Risk tolerance: High — trades with inflated conviction on positive deviations (success_attribution > 1.0); maintains baseline on negative deviations rather than reducing risk.
- Information asymmetry: Partial — observes current price and fundamental value but has no access to order flow, peer positions, or actual trade outcome history.
- Psychological profile: Outcome bias (Fischhoff & Beyth 1975) and overconfident self-attribution (Odean 1998; Barber & Odean 2000) — credits gains to own skill while externalising losses as luck, preventing calibration learning.

## Parameters

| Parameter              | Type  | Default   | Valid Range      | Sensitivity | Description                                                 | Impact                                                | Source                     |
|------------------------|-------|-----------|-----------------|-------------|-------------------------------------------------------------|-------------------------------------------------------|----------------------------|
| `activation_threshold` | float | 0.02      | [0.01, 0.05]    | High        | Minimum |deviation| to trigger trading                     | Higher → fewer trades, wider dead zone                | Odean (1998)               |
| `quantity_scale`       | int   | 5000      | [3000, 8000]    | High        | Base linear scaling factor from deviation to qty            | Higher → larger orders for same deviation             | Barber & Odean (2000)      |
| `max_order`            | int   | 800       | [500, 1000]     | Medium      | Maximum shares per single order                             | Higher → allows larger single-round impact            | Barber & Odean (2000)      |
| `success_attribution`  | float | 1.3       | [1.0, 2.5]      | High        | Multiplicative inflation on buys (gain = skill)             | Higher → stronger bullish asymmetry                   | Fischhoff & Beyth (1975)   |
| `failure_discount`     | float | 1.0       | [0.2, 1.0]      | Medium      | Multiplicative factor on sells (loss = luck)                | Lower → smaller sell orders, stronger bullish bias    | Odean (1998)               |
| `initial_cash`         | float | 1000000   | [500000, 2000000]| Low        | Starting cash endowment                                     | Higher → longer runway before cash exhaustion         | Standardised               |
| `initial_position`     | int   | 0         | [0, 1000]       | Low         | Starting share position                                     | Higher → enables selling from round 1                 | Standardised               |

## Worked Numerical Examples

### Case 1 — Positive deviation triggers buy with success attribution

System state: `price` = 105.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 0, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800, `success_attribution` = 1.3, `failure_discount` = 1.0

Calculation:
- `deviation` = (105.0 - 100.0) / 100.0 = 0.05
- Threshold check: |0.05| > 0.02? YES → active branch
- Attribution: deviation > 0 → attribution_scale = success_attribution = 1.3
- `raw_qty` = int(0.05 * 5000 * 1.3) = int(325) = 325
- `qty` = min(800, 325) = 325
- Direction: deviation > 0 → action = "buy" (skill-confirmed uptrend)
- Cash check: min(325, int(1,000,000 / 105.0)) = min(325, 9523) = 325

Decision: buy 325 shares at price 105.0
State update: `cash`: 1,000,000 → 965,875; `position`: 0 → 325

### Case 2 — Negative deviation triggers sell with failure discount (baseline)

System state: `price` = 95.0, `fundamental` = 100.0, `cash` = 500,000, `position` = 400, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800, `success_attribution` = 1.3, `failure_discount` = 1.0

Calculation:
- `deviation` = (95.0 - 100.0) / 100.0 = -0.05
- Threshold check: |-0.05| > 0.02? YES → active branch
- Attribution: deviation < 0 → attribution_scale = failure_discount = 1.0
- `raw_qty` = int(0.05 * 5000 * 1.0) = int(250) = 250
- `qty` = min(800, 250) = 250
- Direction: deviation < 0 → action = "sell" (bad luck, trade anyway)
- Position check: min(250, 400) = 250

Decision: sell 250 shares at price 95.0
State update: `cash`: 500,000 → 523,750; `position`: 400 → 150

### Case 3 — Large positive deviation hits max_order cap

System state: `price` = 120.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 100, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800, `success_attribution` = 1.3, `failure_discount` = 1.0

Calculation:
- `deviation` = (120.0 - 100.0) / 100.0 = 0.20
- Threshold check: |0.20| > 0.02? YES → active branch
- Attribution: deviation > 0 → attribution_scale = 1.3
- `raw_qty` = int(0.20 * 5000 * 1.3) = int(1300) = 1300
- `qty` = min(800, 1300) = 800 (clamped to max_order)
- Direction: deviation > 0 → action = "buy"
- Cash check: min(800, int(1,000,000 / 120.0)) = min(800, 8333) = 800

Decision: buy 800 shares at price 120.0
State update: `cash`: 1,000,000 → 904,000; `position`: 100 → 900

### Edge Case — Zero position prevents sell

System state: `price` = 92.0, `fundamental` = 100.0, `cash` = 300,000, `position` = 0, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800, `success_attribution` = 1.3, `failure_discount` = 1.0

Calculation:
- `deviation` = (92.0 - 100.0) / 100.0 = -0.08
- Threshold check: |-0.08| > 0.02? YES → active branch
- Attribution: deviation < 0 → attribution_scale = failure_discount = 1.0
- `raw_qty` = int(0.08 * 5000 * 1.0) = int(400) = 400
- `qty` = min(800, 400) = 400
- Direction: deviation < 0 → action = "sell"
- Position check: min(400, 0) = 0 → qty = 0 → action = "hold"

Decision: hold (no position to sell)
State update: no change

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` <- Odean (1998): active traders respond to deviations of 2%+ from perceived fair value
- `quantity_scale` <- Barber & Odean (2000): active trader turnover implies scaling at 3000–8000 per unit deviation
- `success_attribution` <- Fischhoff & Beyth (1975): recalled probability inflated by 30–50%; default 1.3
- `failure_discount` <- Odean (1998): losers held at baseline rates; no size reduction observed

**Expected individual behaviour:**
- Given price = 106, fundamental = 100 (deviation = +6%), agent MUST emit action = "buy" with qty = min(800, int(0.06 * 5000 * 1.3)) = min(800, 390) = 390
- Given price = 94, fundamental = 100 (deviation = -6%), agent MUST emit action = "sell" with qty = min(800, int(0.06 * 5000 * 1.0)) = min(800, 300) = 300
- Given price = 101, fundamental = 100 (deviation = +1%), agent MUST emit action = "hold" with qty = 0
- Asymmetry check: buy qty (390) > sell qty (300) for symmetric 6% deviation — confirms outcome bias

**Sanity bounds (red flags indicating broken implementation):**
- IF agent produces equal quantities for +X% and -X% deviations THEN broken — asymmetric attribution not applied
- IF agent's buy quantity for positive deviation is less than the sell quantity for equal-magnitude negative deviation THEN broken — attribution direction inverted
- IF agent trades when |deviation| <= activation_threshold THEN broken — dead zone violated
- IF agent emits quantity > max_order THEN broken — cap constraint violated

#### Ablation Hooks

| Ablation name             | Setting                      | Hypothesis tested                                              | Expected direction                    | Metric                   |
|---------------------------|------------------------------|----------------------------------------------------------------|---------------------------------------|--------------------------|
| `symmetric_attribution`   | `success_attribution = 1.0`  | Asymmetric attribution drives bullish bias                     | Equal buy/sell magnitudes             | `buy_sell_ratio`         |
| `strong_success_bias`     | `success_attribution = 2.0`  | Stronger success attribution amplifies upside momentum         | Larger buys, faster upward divergence | `max_positive_deviation` |
| `punish_failure`          | `failure_discount = 0.5`     | Discounting failure reduces downside selling                   | Smaller sells, higher position        | `mean_sell_quantity`     |

## Academic References

| # | Citation                                                                                                                                                                                                             | Notes                                     |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| 1 | Fischhoff, B., & Beyth, R. (1975). "I knew it would happen": Remembered probabilities of once-future things. *Organizational Behavior and Human Performance*, 13(1), 1–16. https://doi.org/10.1016/0030-5073(75)90002-1 | Primary theory; outcome bias mechanism    |
| 2 | Odean, T. (1998). Volume, volatility, price, and profit when all traders are above average. *Journal of Finance*, 53(6), 1887–1934. https://doi.org/10.1111/0022-1082.00259                                           | Overconfident trading model               |
| 3 | Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. *Journal of Finance*, 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226                                                               | Empirical calibration; active traders     |

## Design Provenance and Versioning

| Field   | Content                                                    |
|---------|------------------------------------------------------------|
| Author  | Codex                                                      |
| Created | 2026-07-16                                                 |
| Version | 1.0.0                                                      |
| Icon    | ![](../agent_images/icons/finance-outcome-learner.png)     |
| Status  | draft                                                      |
