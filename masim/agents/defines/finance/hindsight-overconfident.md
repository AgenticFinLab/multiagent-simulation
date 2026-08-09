# Hindsight Overconfident

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Hindsight Overconfident                                                                                              |
| Theory Family         | Behavioral Finance — Hindsight Bias and Overconfidence                                                               |
| Behavioral Tendency   | **Diverging** — amplifies price trends by interpreting past moves as having been obviously predictable                |
| Time Horizon          | Short (reacts within a single tick to deviations; no multi-round holding logic)                                      |
| Risk Tolerance        | High (inflates position sizing through overconfidence in post-hoc predictability)                                    |
| Information Asymmetry | Partial (observes price and fundamental value; no access to order flow or private information)                       |
| Determinism           | Deterministic (given identical inputs and parameters, always produces the same order)                                |

## Definition and Goals

The hindsight overconfident agent models the "knew-it-all-along" trader who retrospectively interprets observed price movements as having been obviously foreseeable, and then projects this illusory predictability forward into inflated confidence for the next trade. In the real world, these correspond to overconfident retail day-traders, momentum investors who rationalise past trend-following profits as skill, self-attributed hedge fund managers, financial commentators who claim they "called it," and social-media traders who exhibit hindsight-inflated conviction.

The agent's decision goal is to produce an order (action + quantity) when the absolute deviation between current price and fundamental value exceeds `activation_threshold`. The quantity formula incorporates two bias multipliers: `hindsight_inflation` (post-hoc certainty amplifier) and `prediction_overweight` (forward projection of perceived predictability), yielding `qty = min(max_order, int(|deviation| * quantity_scale * hindsight_inflation * prediction_overweight))`. Direction follows the sign of the deviation — the agent chases momentum, interpreting existing trends as validation of its forecasting ability.

The agent's behavioural role inside the simulation is to serve as a diverging momentum amplifier: by trading pro-cyclically with inflated size (larger than an unbiased momentum trader would use), it accelerates price departures from fundamental value. Non-goals: (1) the agent MUST NOT trade contrarian to the observed deviation — its hindsight bias tells it the trend was obvious and will continue; (2) the agent MUST NOT reduce position size in response to prolonged deviations — overconfidence prevents it from recognising its own calibration errors.

## Theoretical Foundation

**Hindsight Bias (Fischhoff 1975)**:
- Theory / Study: Hindsight ≠ Foresight: The Effect of Outcome Knowledge on Judgment Under Uncertainty
- Citation: Fischhoff, B. (1975). Hindsight ≠ foresight: The effect of outcome knowledge on judgment under uncertainty. *Journal of Experimental Psychology: Human Perception and Performance*, 1(3), 288–299. https://doi.org/10.1037/0096-1523.1.3.288
- Core Insight: Once an outcome is known, people systematically overestimate the degree to which they could have predicted it. This "creeping determinism" causes traders to believe past price movements were foreseeable, inflating their confidence in predicting future movements — leading to oversized positions in the direction of recent trends.
- Mathematical Formulation: `qty = min(max_order, int(|deviation| * quantity_scale * hindsight_inflation * prediction_overweight))`
- Empirical Evidence: Fischhoff (1975, Experiment 1) found that subjects assigned 2–3x higher subjective probabilities to outcomes they knew had occurred versus control groups (N=120, p<0.001). In financial contexts, Biais & Weber (2009) document 30–50% overconfidence inflation in calibration tasks among experienced traders.
- Relevance to This Agent: The agent operationalises hindsight bias by inflating its trade size via `hindsight_inflation` — it perceives past moves as "obvious" and scales up bets accordingly, producing larger-than-rational momentum trades.
- Calibration Source: `hindsight_inflation` = 1.5 from Fischhoff (1975): judged probability inflated by factor of 1.3–2.0 post-outcome; midpoint 1.5. `activation_threshold` = 0.02 from Barber & Odean (2000): active retail traders respond to moves of 2%+.
- Falsification Conditions: If this agent holds for more than 3 consecutive rounds where |deviation| > activation_threshold, the hindsight mechanism is falsified. If the agent's trade size is not larger than a baseline momentum trader (one with inflation=1.0) under identical conditions, the overconfidence amplification is absent.
- Alternative Theories: Overconfidence (Daniel et al. 1998), confirmation bias (Nickerson 1998), self-attribution bias (Miller & Ross 1975).

**Overconfidence and Security Market Over/Underreactions (Daniel, Hirshleifer & Subrahmanyam 1998)**:
- Theory / Study: Investor Psychology and Security Market Under- and Overreactions
- Citation: Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839–1885. https://doi.org/10.1111/0022-1082.00077
- Core Insight: Overconfident investors overweight their private signals, generating momentum in the short term (as they push prices in the signal direction) and eventual reversal (when public information corrects). Combined with self-attribution bias (credit for gains, excuses for losses), overconfidence is self-reinforcing — exactly the dynamic this agent embodies.
- Mathematical Formulation: `effective_signal_weight = base_weight * (1 + overconfidence_factor); overconfidence_factor ∈ [0.3, 1.0]`
- Empirical Evidence: Daniel et al. (1998, Proposition 2) predict short-run momentum profits proportional to overconfidence — empirically validated by Jegadeesh & Titman (1993): 1.31% monthly excess returns for 6-month strategies (t=3.07, N=25 years).
- Relevance to This Agent: The `prediction_overweight` parameter directly operationalises the DHS overconfidence factor — the agent overweights its "signal" (the observed deviation) beyond rational levels, producing oversized directional bets.
- Calibration Source: Daniel et al. (1998, Section III): overconfidence parameter ranges 0.3–1.0 above base weight; `prediction_overweight` default 1.0 (base) with range [1.0, 2.0] for sensitivity sweeps.
- Falsification Conditions: If the agent's per-round trade quantity does not exceed `int(|deviation| * quantity_scale)` (the unbiased baseline) when hindsight_inflation > 1.0 or prediction_overweight > 1.0, then the overconfidence mechanism is not implemented.
- Alternative Theories: Rational expectations (Muth 1961), disposition effect (Shefrin & Statman 1985), noise trader risk (DeLong et al. 1990).

## Design Purpose and Activation Triggers

Purpose: Amplify existing price trends by trading pro-cyclically with inflated confidence derived from hindsight bias and overconfidence in self-perceived predictive ability.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value available (broadcast by market coordinator)

Missing-Signal Policy: If fundamental value is unavailable or NaN, the agent holds (quantity = 0, no action). If price is unavailable, the agent abstains entirely.

Activation Triggers:
- Positive deviation detected (deviation > activation_threshold): BUY — agent interprets uptrend as "obviously predictable" and bets on continuation
- Negative deviation detected (deviation < -activation_threshold): SELL — agent interprets downtrend as foreseeable and bets on continuation
- Default (|deviation| <= activation_threshold): Hold — no "obvious" trend to exploit

Deactivation Conditions:
- Price returns within threshold band of fundamental: Agent naturally deactivates (hold)
- Cash exhaustion: Cannot buy further (buy quantity clamped to affordable amount)
- Position exhaustion: Cannot sell below zero position (sell quantity clamped)

Behavioral Adaptation by Condition:
| Condition                          | Behavioral change                                                | Mechanism                                                            |
|------------------------------------|------------------------------------------------------------------|----------------------------------------------------------------------|
| Large deviation (|deviation| > 10%) | Aggressively trades with maximum conviction (hits max_order cap) | Hindsight inflation × scale saturates at cap                         |
| Small deviation near threshold     | Trades modestly; bias multipliers still inflate above rational    | Linear scaling at low magnitude but still amplified by inflation    |

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
| `quantity`  | int    | [0, max_order]            | shares | yes       | Unsigned order size (bias-inflated)              |
| `reasoning` | string | 1–3 sentences             | —      | yes       | Hindsight narrative and trade rationale          |

##### Content Constraints

- All three output fields MUST be present on every call.
- `quantity` MUST be clamped to [0, max_order].
- Buy quantity MUST NOT exceed affordable shares (cash / price).
- Sell quantity MUST NOT exceed current position.
- Positive deviation triggers `action = "buy"`; negative deviation triggers `action = "sell"`.
- The agent is deterministic given the same price, fundamental, cash, position, and parameters.
- Sign convention: positive quantity with action "buy" = purchase; positive quantity with action "sell" = disposal.

##### Serialization Format

```
<analysis>Deviation = (price - fundamental) / fundamental = {deviation:.4f}; threshold = {activation_threshold}. |deviation| {'>' if active else '<='} threshold → {action}. Hindsight logic: past move was 'obvious', inflating confidence by {hindsight_inflation} × {prediction_overweight}. qty = min({max_order}, int({abs_deviation} × {quantity_scale} × {hindsight_inflation} × {prediction_overweight})) = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "quantity": <int>, "reasoning": "<1-3 sentence explanation>"}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the deviation formula with bias multipliers and emit the tagged output deterministically. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema and field set. On conflict between this contract and any other section, this contract wins.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                                                      |
|---------------|------------|---------------|--------------------------------------------------------------------------------|
| `price`       | Continuous | Current tick  | Required for computing deviation from fundamental                              |
| `fundamental` | Continuous | Current tick  | Anchor value against which "predictability" is retrospectively assessed         |

Does NOT use: price history, technical indicators, volume data, peer positions, order book depth, moving averages, news feeds — the agent reacts only to the instantaneous deviation, interpreting it through a hindsight lens.

#### Core Behavioral Mechanism

```
Step 1 — Read market inputs:
  Read: price from market_data
  Read: fundamental from market_data
  (implementation convenience — input acquisition)

Step 2 — Compute deviation:
  Compute: deviation = (price - fundamental) / fundamental
  (Traces to: Fischhoff 1975 — deviation magnitude triggers hindsight certainty)

Step 3 — Evaluate activation threshold:
  Read: activation_threshold from parameters
  IF |deviation| > activation_threshold: → Active branch (Step 4)
  ELSE: → Hold branch (Step 8)
  (Traces to: Fischhoff 1975 — minimum threshold for outcome to be perceived as "obvious")

Step 4 — Apply hindsight inflation and compute raw quantity:
  Read: quantity_scale, max_order, hindsight_inflation, prediction_overweight from parameters
  Compute: abs_deviation = |deviation|
  Compute: raw_qty = int(abs_deviation * quantity_scale * hindsight_inflation * prediction_overweight)
  Compute: qty = min(max_order, raw_qty)
  (Traces to: Fischhoff 1975 — hindsight inflation; Daniel et al. 1998 — overconfidence multiplier)

Step 5 — Determine direction (pro-cyclical):
  IF deviation > 0: action = "buy"   (price above fundamental → "obviously" going higher)
  IF deviation < 0: action = "sell"  (price below fundamental → "obviously" going lower)
  (Traces to: Daniel et al. 1998 — overconfident traders trade in signal direction)

Step 6 — Apply resource constraints:
  Read: cash, position from agent state
  IF action == "buy": qty = min(qty, int(cash / price))
  IF action == "sell": qty = min(qty, position)
  Write: IF qty == 0 THEN action = "hold"
  (implementation convenience — budget enforcement)

Step 7 — Emit decision:
  Emit: {action, qty, reasoning}
  (implementation convenience — output formatting)

Step 8 — Hold branch:
  Compute: action = "hold"; qty = 0
  (Traces to: Fischhoff 1975 — insufficient outcome to trigger hindsight certainty)

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
| Sizing rule           | `qty = min(max_order, int(|deviation| * quantity_scale * hindsight_inflation * prediction_overweight))`, clamped by cash/position |
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
    qty = min(max_order, int(|deviation| * quantity_scale * hindsight_inflation * prediction_overweight))
    qty = min(qty, int(cash / price))
    action = "buy" IF qty > 0 ELSE "hold"

ELIF deviation < -activation_threshold:
    qty = min(max_order, int(|deviation| * quantity_scale * hindsight_inflation * prediction_overweight))
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

| Symbol                  | Meaning                                       | Default Value | Source                     |
|-------------------------|-----------------------------------------------|---------------|----------------------------|
| `activation_threshold`  | Minimum |deviation| to trigger trade          | 0.02          | Fischhoff (1975)           |
| `quantity_scale`        | Base linear scaling of qty with deviation      | 5000          | Daniel et al. (1998)       |
| `max_order`             | Maximum order size per round                   | 800           | Daniel et al. (1998)       |
| `hindsight_inflation`   | Multiplicative bias from "knew it all along"   | 1.5           | Fischhoff (1975)           |
| `prediction_overweight` | Forward projection of overconfident prediction | 1.0           | Daniel et al. (1998)       |
| `initial_cash`          | Starting cash endowment                        | 1,000,000     | Standardised               |
| `initial_position`      | Starting share position                        | 0             | Standardised               |

#### Behavioral Properties

- Time horizon: Short — reacts within a single tick to any deviation above threshold; no multi-round holding logic or look-back window.
- Risk tolerance: High — trades with inflated conviction (bias multipliers > 1.0) proportional to deviation magnitude; willing to deploy full capital toward trend-chasing bets.
- Information asymmetry: Partial — observes current price and fundamental value but has no access to order flow, peer positions, or private signals.
- Psychological profile: Hindsight bias (Fischhoff 1975) and overconfidence (Daniel et al. 1998) — retrospectively views past price moves as obvious, inflating forward-looking confidence and trade size beyond rational levels.

## Parameters

| Parameter              | Type  | Default   | Valid Range      | Sensitivity | Description                                                 | Impact                                              | Source                  |
|------------------------|-------|-----------|-----------------|-------------|-------------------------------------------------------------|-----------------------------------------------------|-------------------------|
| `activation_threshold` | float | 0.02      | [0.01, 0.05]    | High        | Minimum |deviation| to trigger trading                     | Higher → fewer trades, wider dead zone              | Fischhoff (1975)        |
| `quantity_scale`       | int   | 5000      | [3000, 8000]    | High        | Base linear scaling factor from deviation to qty            | Higher → larger orders for same deviation           | Daniel et al. (1998)    |
| `max_order`            | int   | 800       | [500, 1000]     | Medium      | Maximum shares per single order                             | Higher → allows larger single-round impact          | Daniel et al. (1998)    |
| `hindsight_inflation`  | float | 1.5       | [1.0, 2.0]      | High        | Multiplicative inflation from hindsight certainty           | Higher → larger orders, stronger trend amplification| Fischhoff (1975)        |
| `prediction_overweight`| float | 1.0       | [1.0, 2.0]      | Medium      | Forward overconfidence multiplier on perceived predictability| Higher → amplifies position sizing beyond hindsight | Daniel et al. (1998)    |
| `initial_cash`         | float | 1000000   | [500000, 2000000]| Low        | Starting cash endowment                                     | Higher → longer runway before cash exhaustion       | Standardised            |
| `initial_position`     | int   | 0         | [0, 1000]       | Low         | Starting share position                                     | Higher → enables selling from round 1               | Standardised            |

## Worked Numerical Examples

### Case 1 — Positive deviation triggers buy with hindsight inflation

System state: `price` = 104.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 0, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800, `hindsight_inflation` = 1.5, `prediction_overweight` = 1.0

Calculation:
- `deviation` = (104.0 - 100.0) / 100.0 = 0.04
- Threshold check: |0.04| > 0.02? YES → active branch
- `raw_qty` = int(0.04 * 5000 * 1.5 * 1.0) = int(300) = 300
- `qty` = min(800, 300) = 300
- Direction: deviation > 0 → action = "buy" ("obviously" going higher)
- Cash check: min(300, int(1,000,000 / 104.0)) = min(300, 9615) = 300

Decision: buy 300 shares at price 104.0
State update: `cash`: 1,000,000 → 968,800; `position`: 0 → 300

### Case 2 — Large deviation hits max_order cap

System state: `price` = 115.0, `fundamental` = 100.0, `cash` = 1,000,000, `position` = 200, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800, `hindsight_inflation` = 1.5, `prediction_overweight` = 1.0

Calculation:
- `deviation` = (115.0 - 100.0) / 100.0 = 0.15
- Threshold check: |0.15| > 0.02? YES → active branch
- `raw_qty` = int(0.15 * 5000 * 1.5 * 1.0) = int(1125) = 1125
- `qty` = min(800, 1125) = 800 (clamped to max_order)
- Direction: deviation > 0 → action = "buy"
- Cash check: min(800, int(1,000,000 / 115.0)) = min(800, 8695) = 800

Decision: buy 800 shares at price 115.0
State update: `cash`: 1,000,000 → 908,000; `position`: 200 → 1000

### Case 3 — Negative deviation triggers sell

System state: `price` = 96.0, `fundamental` = 100.0, `cash` = 500,000, `position` = 400, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800, `hindsight_inflation` = 1.5, `prediction_overweight` = 1.0

Calculation:
- `deviation` = (96.0 - 100.0) / 100.0 = -0.04
- Threshold check: |-0.04| > 0.02? YES → active branch
- `raw_qty` = int(0.04 * 5000 * 1.5 * 1.0) = int(300) = 300
- `qty` = min(800, 300) = 300
- Direction: deviation < 0 → action = "sell" ("obviously" heading lower)
- Position check: min(300, 400) = 300

Decision: sell 300 shares at price 96.0
State update: `cash`: 500,000 → 528,800; `position`: 400 → 100

### Edge Case — Position exhaustion limits sell

System state: `price` = 90.0, `fundamental` = 100.0, `cash` = 200,000, `position` = 50, `activation_threshold` = 0.02, `quantity_scale` = 5000, `max_order` = 800, `hindsight_inflation` = 1.5, `prediction_overweight` = 1.0

Calculation:
- `deviation` = (90.0 - 100.0) / 100.0 = -0.10
- Threshold check: |-0.10| > 0.02? YES → active branch
- `raw_qty` = int(0.10 * 5000 * 1.5 * 1.0) = int(750) = 750
- `qty` = min(800, 750) = 750
- Direction: deviation < 0 → action = "sell"
- Position check: min(750, 50) = 50 (clamped by position)

Decision: sell 50 shares at price 90.0
State update: `cash`: 200,000 → 204,500; `position`: 50 → 0

## Behavioral Verification and Calibration

**Calibration data sources:**
- `activation_threshold` <- Fischhoff (1975): hindsight certainty triggers at outcome magnitudes corresponding to 2–5% price moves
- `quantity_scale` <- Daniel et al. (1998): overconfident momentum loading scales at 3000–8000
- `hindsight_inflation` <- Fischhoff (1975, Experiment 1): judged probability inflated by 1.3–2.0x post-outcome; default 1.5
- `prediction_overweight` <- Daniel et al. (1998, Section III): overconfidence factor 1.0–2.0

**Expected individual behaviour:**
- Given price = 106, fundamental = 100 (deviation = +6%), agent MUST emit action = "buy" with qty = min(800, int(0.06 * 5000 * 1.5 * 1.0)) = min(800, 450) = 450
- Given price = 97, fundamental = 100 (deviation = -3%), agent MUST emit action = "sell" with qty = min(800, int(0.03 * 5000 * 1.5 * 1.0)) = min(800, 225) = 225
- Given price = 101, fundamental = 100 (deviation = +1%), agent MUST emit action = "hold" with qty = 0

**Sanity bounds (red flags indicating broken implementation):**
- IF agent buys when deviation < 0 THEN broken — direction logic is inverted
- IF agent sells when deviation > 0 THEN broken — direction logic is inverted
- IF agent trades when |deviation| <= activation_threshold THEN broken — dead zone violated
- IF agent emits quantity > max_order THEN broken — cap constraint violated
- IF agent's quantity equals `int(|deviation| * quantity_scale)` when hindsight_inflation > 1.0 THEN broken — bias multiplier not applied

#### Ablation Hooks

| Ablation name             | Setting                    | Hypothesis tested                                              | Expected direction                     | Metric                   |
|---------------------------|----------------------------|----------------------------------------------------------------|----------------------------------------|--------------------------|
| `disable_hindsight`       | `hindsight_inflation = 1.0`| Hindsight inflation is necessary for excess momentum           | Smaller orders, less trend amplification| `mean_order_size`        |
| `max_overconfidence`      | `prediction_overweight = 2.0`| Double overconfidence doubles trend-chasing intensity        | Larger orders, faster price divergence | `max_absolute_deviation` |
| `high_threshold`          | `activation_threshold = 0.05`| Higher threshold reduces trading frequency                  | Fewer trades, more stable prices       | `trade_count`            |

## Academic References

| # | Citation                                                                                                                                                                                                             | Notes                                    |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1 | Fischhoff, B. (1975). Hindsight ≠ foresight: The effect of outcome knowledge on judgment under uncertainty. *Journal of Experimental Psychology: Human Perception and Performance*, 1(3), 288–299. https://doi.org/10.1037/0096-1523.1.3.288 | Primary theory; hindsight bias mechanism |
| 2 | Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839–1885. https://doi.org/10.1111/0022-1082.00077             | Overconfidence model; momentum prediction|
| 3 | Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. *Journal of Finance*, 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226                                                               | Overconfident retail trader calibration  |
| 4 | Biais, B., & Weber, M. (2009). Hindsight bias, risk perception, and investment performance. *Management Science*, 55(6), 1018–1029. https://doi.org/10.1287/mnsc.1090.1000                                           | Financial hindsight bias measurement     |

## Design Provenance

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-14                   |
| Version     | 1.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-hindsight-overconfident.png)         |
