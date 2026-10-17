# Issuer-Pays Rating Agency with Overrating Bias

## Summary

| Field                 | Content                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Archetype             | Issuer-Pays Rating Agency with Overrating Bias                                                                   |
| Theory Family         | Credit Rating Agencies — Issuer-Pays Conflicts and Rating Inflation                                              |
| Behavioral Tendency   | **Diverging** — inflates demand based on distorted fundamental perception (overrating bias)                      |
| Time Horizon          | Short (single-round buy decision based on current perceived value gap)                                           |
| Risk Tolerance        | Medium (buys only with 5% discount cushion below perceived fundamental, but perception itself is inflated)       |
| Information Asymmetry | Distorted (observes true fundamental but applies systematic upward bias before decision-making)                  |
| Determinism           | Deterministic (given identical fundamental, price, and parameters, always produces the same buy decision)         |

## Definition and Goals

The rating agency agent models the demand-side distortion created by credit rating agencies operating under issuer-pays conflicts of interest. In the real world, these correspond to agencies (Moody's, S&P, Fitch) whose revenue model — being paid by the securities issuers they rate — created systematic incentives to inflate ratings on structured products, particularly mortgage-backed securities. The inflated ratings induced institutional investors bound by rating mandates to purchase securities that were riskier than their ratings indicated.

The agent's decision goal is to buy securities when the market price is below its perceived fundamental value (which is inflated by the overrating bias), thereby modelling the excess demand created when rating-dependent investors treat overrated securities as bargains. The perceived fundamental is computed as `perceived_fundamental = fundamental * (1 + overrating_bias)`, and the agent buys when `price < perceived_fundamental * 0.95`, capped at `max_buy` shares per round.

The agent's behavioural role inside the simulation is to create artificial demand that supports prices above their true fundamental value during the pre-crisis accumulation phase, delaying the price correction and allowing other agents (such as the MBS originator) to distribute securities at inflated prices. When the inevitable correction occurs, the rating agency's demand evaporates (prices fall below even the inflated threshold), contributing to demand collapse. Non-goals: (1) the rating agency MUST NOT sell securities — it models demand creation only; (2) the rating agency MUST NOT update its overrating bias during the simulation — the bias is structural and persistent.

## Theoretical Foundation

**Rating Inflation under Issuer-Pays (Bolton, Freixas & Shapiro 2012)**:
- Theory / Study: The Credit Ratings Game
- Citation: Bolton, P., Freixas, X., & Shapiro, J. (2012). The credit ratings game. *Journal of Finance*, 67(1), 85–111. https://doi.org/10.1111/j.1540-6261.2012.01730.x
- Core Insight: In a model with issuer-pays compensation, competition among rating agencies leads to rating inflation in equilibrium. Agencies inflate ratings to attract issuance business, particularly during booms when reputational costs of inflation are low because defaults are rare. This creates systematic overvaluation of structured securities.
- Mathematical Formulation: `perceived_fundamental = fundamental × (1 + overrating_bias)` — the bias represents the systematic gap between the true credit quality and the assigned rating, translated into a fundamental value premium.
- Empirical Evidence: Bolton et al. (2012, Proposition 2, p. 95) show that in the trusting equilibrium, agencies inflate with probability 1 when reputational concerns are sufficiently low. Empirically, Benmelech & Dlugosz (2009) document that 70% of AAA-rated CDO tranches originated in 2006–2007 were subsequently downgraded to junk status, implying an effective overrating of 3–5 notch levels.
- Relevance to This Agent: The agent implements the demand-side consequence of rating inflation — investors purchasing based on inflated perceived value rather than true fundamental quality.
- Calibration Source: `overrating_bias` in [0.10, 0.40] derived from Bolton et al. (2012, Section 4): a 20% overrating bias represents approximately 2–3 notch inflation in structured product ratings, consistent with observed pre-crisis AAA inflation.
- Falsification Conditions: If this agent buys at prices above its perceived_fundamental (i.e. without any discount cushion), the value-investor behaviour underlying the model is falsified.
- Alternative Theories: Reputation-based cycling (Bar-Isaac & Shapiro 2013), investor credulity models (Skreta & Veldkamp 2009).

**MBS Rating Adjustments and Conflicts (Griffin & Tang 2012)**:
- Theory / Study: Did Subjectivity Play a Role in CDO Credit Ratings?
- Citation: Griffin, J. M., & Tang, D. Y. (2012). Did subjectivity play a role in CDO credit ratings? *Review of Financial Studies*, 25(7), 2185–2224. https://doi.org/10.1093/rfs/hhs072
- Core Insight: Rating agencies made systematic positive adjustments to their quantitative models when rating CDOs, with larger adjustments for more complex and opaque structures. These subjective upward adjustments averaged 3–4 notches above what the quantitative models alone would have produced.
- Mathematical Formulation: The 0.95 discount factor in the buy condition (`price < perceived_fundamental * 0.95`) models a minimal due-diligence buffer that rating-trusting investors maintained even while relying on inflated ratings.
- Empirical Evidence: Griffin & Tang (2012, Table 5, p. 2206) document that 83% of CDO tranches received positive adjustments averaging 3.5 notches; the average adjustment was larger for deals from issuers who generated more repeat business (Table 7, p. 2212).
- Relevance to This Agent: The systematic positive adjustment mechanism maps directly to the `overrating_bias` parameter — the agent's perception of value is inflated above true fundamental by a fixed percentage.
- Calibration Source: `max_buy` = 300 represents position limits of rating-dependent institutional investors; `initial_cash` = 1500000 represents typical structured-credit allocation.
- Falsification Conditions: If the agent's perceived_fundamental equals or is below the true fundamental, the overrating mechanism is not operative.
- Alternative Theories: Pure model error (non-strategic), complexity-driven opacity (Coval et al. 2009).

## Design Purpose and Activation Triggers

Purpose: Create artificial demand based on inflated fundamental perception, supporting overvalued prices during the accumulation phase and modelling the demand distortion caused by conflicted credit ratings.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Current fundamental value available

Missing-Signal Policy: If price is unavailable (NaN), the agent holds (cannot evaluate buy condition). If fundamental value is unavailable (NaN), the agent holds (cannot compute perceived fundamental).

Activation Triggers:
- `price < perceived_fundamental * 0.95`: Buy up to `max_buy` shares (value gap detected under inflated perception)
- `price >= perceived_fundamental * 0.95`: Hold (no perceived discount)
- Default (missing signals): Hold

Deactivation Conditions:
- Cash exhausted: Agent can no longer buy
- Price rises above perceived_fundamental * 0.95: No value gap perceived
- Simulation end / market closure: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                              | Behavioral change                            | Mechanism                                   |
|----------------------------------------|----------------------------------------------|---------------------------------------------|
| Price well below perceived fundamental | Buys max_buy shares                          | Inflated perception creates perceived value |
| Price near perceived fundamental       | Holds (5% cushion not met)                   | Minimal due-diligence buffer                |
| Price collapse beyond even inflated value | Holds (eventually price falls too far)    | Cash exhaustion or buy condition not met     |

Environmental Dependencies: Requires per-round market broadcast containing `price` and `fundamental` fields. No peer actions, volatility signals, or order-book data are used.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                 | Source                      | Type / Shape | Required? | Notes                                           |
|-----------------------|-----------------------------|--------------|-----------|-------------------------------------------------|
| `price`               | Market coordinator payload  | `float`      | yes       | Current market price of MBS                     |
| `fundamental`         | Market coordinator payload  | `float`      | yes       | True fundamental value of asset                 |
| `cash`                | Agent persisted state       | `float`      | yes       | Available cash for purchases                    |
| `position`            | Agent persisted state       | `int`        | yes       | Current holdings count                          |
| `round`               | Scheduler / round header    | `int`        | yes       | Current simulation round number                 |
| `overrating_bias`     | Config extras               | `float`      | yes       | Rating inflation factor (§3.7 parameter)        |
| `max_buy`             | Config extras               | `int`        | yes       | Maximum purchase per round (§3.7 parameter)     |
| `retrieved_knowledge` | Retrieval store (RAG only)  | `list[str]`  | RAG only  | Historical rating inflation patterns; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum  | Unit   | Required? | Meaning                                        |
|-------------|--------|---------------------|--------|-----------|------------------------------------------------|
| `action`    | enum   | `{"buy", "hold"}`   | —      | yes       | Purchase decision                              |
| `quantity`  | int    | [0, max_buy]        | shares | yes       | Number of shares to buy this round             |
| `bid_price` | float  | > 0                 | price  | yes       | Price at which to submit buy order             |
| `reasoning` | string | 1–3 sentences       | —      | yes       | Perceived fundamental, gap, and decision logic |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be min(max_buy, int(cash / price)) when buy condition is met; MUST be 0 when holding.
- `action` MUST be `"buy"` when quantity > 0 and `"hold"` when quantity == 0.
- `bid_price` MUST equal the current market price.
- The agent is deterministic: identical inputs yield identical outputs.
- Sign convention: quantity is always non-negative; direction is always buy.

##### Serialization Format

```
<analysis>Fundamental = {fundamental}; perceived_fundamental = {fundamental} × (1 + {overrating_bias}) = {perceived_fundamental:.2f}; threshold = {perceived_fundamental:.2f} × 0.95 = {threshold:.2f}; price = {price}; buy = {buy_condition}.</analysis>
<decision>{"action": "<buy|hold>", "quantity": <int>, "bid_price": <float>, "reasoning": "Perceived value {perceived_fundamental:.2f} vs price {price}; {'buying' if buy else 'holding'}."}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` and `fundamental` MUST be read from the market coordinator broadcast; `cash` and `position` from agent state; config extras supply `overrating_bias` and `max_buy`.
2. **Decision emission** — the code path MUST populate all four required fields and MUST enforce the perceived_fundamental formula.
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all four fields present, quantity <= max_buy.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same four-field output object.
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal         | Type       | Memory Window | Rationale                                               |
|----------------|------------|---------------|---------------------------------------------------------|
| `price`        | Continuous | Current only  | Compared against perceived fundamental threshold        |
| `fundamental`  | Continuous | Current only  | Base for inflated perceived value computation           |
| `cash`         | Continuous | Current only  | Constrains maximum purchase quantity                    |

Does NOT use: price history, volatility, peer actions, order-book depth, position (for decision, only for reporting), deviation metric, spread, or any momentum signal.

#### Core Behavioral Mechanism

1. **Read fundamental value.** Read: `fundamental` from market broadcast. Write: nothing. (Implementation convenience — signal access.)

2. **Compute perceived fundamental.** Read: `fundamental`, `overrating_bias`. Compute: `perceived_fundamental = fundamental * (1 + overrating_bias)`. Write: nothing (intermediate variable). (Traces to Bolton et al. 2012 — rating inflation creates inflated value perception.)

3. **Compute buy threshold.** Read: `perceived_fundamental`. Compute: `threshold = perceived_fundamental * 0.95`. Write: nothing (intermediate variable). (Traces to Griffin & Tang 2012 — minimal due-diligence buffer.)

4. **Read market price.** Read: `price` from market broadcast. Write: nothing. (Implementation convenience — signal access.)

5. **Evaluate buy condition.** Read: `price`, `threshold`. Compute: `buy_condition = (price < threshold)`. Write: nothing (intermediate variable). (Core decision gate.)

6. **Compute buy quantity.** Read: `buy_condition`, `cash`, `price`, `max_buy`. If `buy_condition` is True: `quantity = min(max_buy, int(cash / price))`. Else: `quantity = 0`. Write: nothing (intermediate variable). (Size determination with position and cash limits.)

7. **Emit decision object.** Read: all computed fields. Write: emit the four-field decision object per I/O Contract serialization format. (Implementation convenience — output assembly.)

#### Action Space

| Aspect                | Specification                                                                                              |
|-----------------------|------------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `hold`                                                                                              |
| Action parameter rule | `bid_price` = current market price; `quantity` = min(max_buy, affordable shares)                           |
| Sizing rule           | Capped at `max_buy` per round and constrained by available cash.                                           |
| Action lifetime       | One round; re-evaluated each tick.                                                                         |
| Revision policy       | Implicitly revised every round — buy condition reassessed with current price and fundamental.               |
| State constraint      | Cash monotonically decreases when buying; position monotonically increases. Agent never sells.              |
| Resource cap          | Bounded by initial_cash; once depleted, agent becomes inactive.                                            |
| Exit rule             | Agent holds indefinitely once cash is exhausted or buy condition is never met; no terminal condition.       |

#### Mathematical Model

**Decision output:** The agent computes a buy decision based on perceived (inflated) fundamental vs. market price.

**Decision logic formalization:**

```
Given: fundamental_t, price_t, overrating_bias, max_buy, cash_t

Step 1: Inflate fundamental
  perceived_fundamental = fundamental_t × (1 + overrating_bias)

Step 2: Compute threshold
  threshold = perceived_fundamental × 0.95

Step 3: Evaluate buy condition
  buy_condition = (price_t < threshold)

Step 4: Size the order
  if buy_condition:
    quantity = min(max_buy, floor(cash_t / price_t))
  else:
    quantity = 0

Step 5: Action determination
  if quantity > 0:
    action = "buy"
  else:
    action = "hold"

Step 6: State evolution (post-trade)
  cash_{t+1} = cash_t - quantity × price_t
  position_{t+1} = position_t + quantity
```

**State variables:**

| Variable   | Type    | Initial Value      | Update Phase           |
|------------|---------|--------------------|------------------------|
| `cash`     | `float` | `initial_cash`     | Post-trade (decremented by quantity × price) |
| `position` | `int`   | `initial_position` | Post-trade (incremented by quantity) |

**State evolution:** Cash decreases as securities are purchased; position accumulates. Both are monotonic during active trading.

**Determinism contract:** The decision is fully deterministic given identical fundamental, price, cash, and parameters. No random number generation is used.

**Parameter symbol table:**

| Symbol                  | Meaning                                  | Default Value | Source                    |
|-------------------------|------------------------------------------|---------------|---------------------------|
| `overrating_bias`       | Rating inflation factor                  | 0.20          | Bolton et al. (2012)      |
| `max_buy`               | Maximum shares per round                 | 300           | Institutional constraints |
| `initial_cash`          | Starting cash allocation                 | 1500000       | Simulation design         |
| `initial_position`      | Starting MBS holdings                    | 500           | Simulation design         |
| `perceived_fundamental` | Inflated fundamental value               | —             | Derived                   |
| `threshold`             | Buy trigger price level                  | —             | Derived                   |

#### Behavioral Properties

- Time horizon: Single-round — the agent evaluates the buy condition fresh each round using current fundamental and price; no multi-period planning or inventory management. Rationale: rating-dependent investors re-evaluate based on current ratings each period.
- Risk tolerance: Medium — requires a 5% discount below perceived fundamental before buying, providing a small buffer, but the perception itself is inflated by 20%. Rationale: institutional investors maintain nominal due-diligence procedures even when relying on inflated ratings.
- Information asymmetry: Distorted — the agent observes the true fundamental but systematically misperceives it upward due to the overrating bias, modelling how investors trusted inflated ratings rather than conducting independent analysis.
- Psychological profile: Represents institutional overconfidence in third-party assessments; the agent delegates credit analysis to the (conflicted) rating process and acts on the inflated output.

## Parameters

| Parameter          | Type    | Default  | Valid Range       | Sensitivity | Description                                     | Impact                                              | Source                    |
|--------------------|---------|----------|-------------------|-------------|-------------------------------------------------|-----------------------------------------------------|---------------------------|
| `overrating_bias`  | `float` | 0.20    | [0.10, 0.40]     | high        | Fractional inflation of true fundamental value  | Higher -> more demand, longer price support         | Bolton et al. (2012)      |
| `max_buy`          | `int`   | 300     | [100, 1000]      | medium      | Maximum shares purchased per round              | Higher -> more demand per round, faster cash drain  | Institutional constraints |
| `initial_cash`     | `float` | 1500000 | [500000, 5000000] | medium     | Starting cash available for purchases           | Higher -> more total buying capacity                | Simulation design         |
| `initial_position` | `int`   | 500     | [0, 2000]        | low         | Starting MBS inventory                          | No effect on buy decision; affects portfolio metrics| Simulation design         |

## Worked Numerical Examples

### Case 1 — Pre-crisis, price below inflated fundamental

System state: `fundamental` = 50.00; `price` = 52.00; `overrating_bias` = 0.20; `max_buy` = 300; `cash` = 1500000.

Calculation:
- `perceived_fundamental` = 50.00 × (1 + 0.20) = 60.00
- `threshold` = 60.00 × 0.95 = 57.00
- `buy_condition` = (52.00 < 57.00) = True
- `quantity` = min(300, int(1500000 / 52.00)) = min(300, 28846) = 300

Decision: `action = "buy"`, `quantity = 300`, `bid_price = 52.00`, `reasoning = "Perceived value 60.00 vs price 52.00; buying 300 shares."`.

State update: `cash` = 1500000 - 300 × 52.00 = 1484400; `position` = 500 + 300 = 800.

### Case 2 — Fundamental declining, still buying due to inflated perception

System state: `fundamental` = 40.00; `price` = 43.00; `overrating_bias` = 0.20; `max_buy` = 300; `cash` = 900000.

Calculation:
- `perceived_fundamental` = 40.00 × (1 + 0.20) = 48.00
- `threshold` = 48.00 × 0.95 = 45.60
- `buy_condition` = (43.00 < 45.60) = True
- `quantity` = min(300, int(900000 / 43.00)) = min(300, 20930) = 300

Decision: `action = "buy"`, `quantity = 300`, `bid_price = 43.00`, `reasoning = "Perceived value 48.00 vs price 43.00; buying 300 shares."`.

State update: `cash` = 900000 - 300 × 43.00 = 887100; `position` += 300.

### Case 3 — Price above inflated threshold, holds

System state: `fundamental` = 45.00; `price` = 52.00; `overrating_bias` = 0.20; `max_buy` = 300; `cash` = 1000000.

Calculation:
- `perceived_fundamental` = 45.00 × (1 + 0.20) = 54.00
- `threshold` = 54.00 × 0.95 = 51.30
- `buy_condition` = (52.00 < 51.30) = False
- `quantity` = 0

Decision: `action = "hold"`, `quantity = 0`, `bid_price = 52.00`, `reasoning = "Perceived value 54.00 vs price 52.00; price above threshold 51.30, holding."`.

State update: No change.

### Edge Case — Cash nearly exhausted

System state: `fundamental` = 50.00; `price` = 48.00; `overrating_bias` = 0.20; `max_buy` = 300; `cash` = 5000.

Calculation:
- `perceived_fundamental` = 50.00 × (1 + 0.20) = 60.00
- `threshold` = 60.00 × 0.95 = 57.00
- `buy_condition` = (48.00 < 57.00) = True
- `quantity` = min(300, int(5000 / 48.00)) = min(300, 104) = 104

Decision: `action = "buy"`, `quantity = 104`, `bid_price = 48.00`, `reasoning = "Perceived value 60.00 vs price 48.00; buying 104 shares (cash-constrained)."`.

State update: `cash` = 5000 - 104 × 48.00 = 8.00; `position` += 104.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `overrating_bias` <- Bolton et al. (2012, Proposition 2): equilibrium inflation of 2–3 notches translates to ~15–25% fundamental value gap for investment-grade structured products. Central estimate 20%.
- `max_buy` <- Griffin & Tang (2012): institutional position limits for structured-credit allocations typically 1–5% of portfolio per issue; 300 shares represents moderate allocation capacity.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given fundamental = 50, price = 52, overrating_bias = 0.20, agent MUST buy (perceived = 60, threshold = 57, price 52 < 57).
- Given fundamental = 50, price = 58, overrating_bias = 0.20, agent MUST hold (perceived = 60, threshold = 57, price 58 > 57).
- Given fundamental = 50, price = 52, overrating_bias = 0.20, cash = 0, agent MUST hold (no cash available).
- `perceived_fundamental` MUST always exceed `fundamental` (overrating_bias > 0).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells securities THEN the buy-only constraint is violated.
- IF the agent buys when price >= perceived_fundamental * 0.95 THEN the threshold check is broken.
- IF perceived_fundamental <= fundamental THEN the overrating bias is not being applied.
- IF the agent buys more than max_buy in a single round THEN the position limit is violated.

#### Ablation Hooks

| Ablation name          | Setting                      | Hypothesis tested                                     | Expected direction                             | Metric                    |
|------------------------|------------------------------|-------------------------------------------------------|------------------------------------------------|---------------------------|
| `no_overrating`        | `overrating_bias = 0.0`     | Rating inflation creates artificial demand support     | Prices decline faster without inflated demand  | Rounds before first >5% drop |
| `extreme_inflation`    | `overrating_bias = 0.40`    | Higher inflation extends artificial price support      | Prices remain elevated longer                  | Duration of overvaluation |
| `unlimited_buying`     | `max_buy = 1000`            | Position limits moderate demand impact                 | More buying delays correction further          | Total shares accumulated  |

## Academic References

| # | Citation                                                                                                                                                              | Notes                                    |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| 1 | Bolton, P., Freixas, X., & Shapiro, J. (2012). The credit ratings game. *Journal of Finance*, 67(1), 85–111. https://doi.org/10.1111/j.1540-6261.2012.01730.x | Primary theory: issuer-pays rating inflation |
| 2 | Griffin, J. M., & Tang, D. Y. (2012). Did subjectivity play a role in CDO credit ratings? *Review of Financial Studies*, 25(7), 2185–2224. https://doi.org/10.1093/rfs/hhs072 | Empirical evidence of systematic positive adjustments |
| 3 | Benmelech, E., & Dlugosz, J. (2009). The alchemy of CDO credit ratings. *Journal of Monetary Economics*, 56(5), 617–634. https://doi.org/10.1016/j.jmoneco.2009.04.007 | AAA inflation documentation |
| 4 | Coval, J. D., Jurek, J. W., & Stafford, E. (2009). The economics of structured finance. *Journal of Economic Perspectives*, 23(1), 3–25. https://doi.org/10.1257/jep.23.1.3 | Structured finance complexity and mispricing |
| 5 | Skreta, V., & Veldkamp, L. (2009). Ratings shopping and asset complexity: A theory of ratings inflation. *Journal of Monetary Economics*, 56(5), 678–695. https://doi.org/10.1016/j.jmoneco.2009.04.006 | Ratings shopping mechanism |

## Design Provenance and Versioning

| Field   | Content                                                    |
|---------|------------------------------------------------------------|
| Author  | Codex                                                      |
| Created | 2026-07-16                                                 |
| Version | 1.0.0                                                      |
| Icon    | ![](../agent_images/icons/finance-rating-agency.png)       |
| Status  | draft                                                      |
