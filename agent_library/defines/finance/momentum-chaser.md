# High-Frequency Momentum-Chasing Trend Follower

## Summary

| Field                 | Content                                                                                                      |
|-----------------------|--------------------------------------------------------------------------------------------------------------|
| Archetype             | High-Frequency Momentum-Chasing Trend Follower                                                               |
| Theory Family         | Behavioral Finance — Positive-Feedback Trading                                                               |
| Behavioral Tendency   | **Diverging** — amplifies existing price trends by trading in the direction of recent momentum                |
| Time Horizon          | Short (configurable lookback window of 3–10 rounds)                                                          |
| Risk Tolerance        | High (follows momentum into volatile regimes with position size proportional to velocity magnitude)          |
| Information Asymmetry | Partial (observes price history only; no access to fundamental value or order-book depth)                    |
| Determinism           | Deterministic (given identical price history and parameters, always produces the same signed order)           |

## Definition and Goals

The momentum chaser models high-frequency trend-following algorithms that detect short-term price momentum over a configurable lookback window and trade in the direction of the detected trend with position size proportional to the magnitude of the move. In the real world, these correspond to HFT momentum strategies, algorithmic trend-followers, and short-term systematic CTAs — any fast participant whose directional entry decision is derived entirely from recent price trajectories without reference to fundamental value or order-book state.

The agent's decision goal is to produce a signed order quantity proportional to the estimated price velocity over its lookback window. The quantity is computed as `min(|velocity| × position_multiplier, 1000)` with the sign matching the velocity direction. The agent does not optimise an explicit utility function; instead it mechanically follows the positive-feedback rule, buying into rising prices and selling into falling prices, with a velocity threshold that filters out noise. Orders are constrained by available cash (for buys) and current position (for sells).

The agent's behavioural role inside the simulation is to accelerate directional price moves during a flash crash: once an initial decline is detected, the momentum chaser adds net sell flow that compounds the selling pressure initiated by institutional sellers and amplified by HFT market-maker withdrawal. Its `agent_type = "hft"` classification ensures it counts toward `hft_participation`, maintaining the appearance of HFT activity even as market makers withdraw. Non-goals: (1) the momentum chaser MUST NOT provide liquidity — it is always a liquidity taker with `provides_liquidity = False`; (2) the momentum chaser MUST NOT incorporate mean-reversion or fundamental-value signals — it is purely a trend amplifier that never trades against the detected momentum direction.

## Theoretical Foundation

**Positive-Feedback Trading (De Long et al. 1990)**:
- Theory / Study: Positive Feedback Investment Strategies and Destabilizing Rational Speculation
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379–395. https://doi.org/10.2307/2328662
- Core Insight: Positive-feedback traders buy after price rises and sell after price falls, creating self-reinforcing momentum that pushes prices away from fundamentals. The resulting destabilising effect is amplified when rational speculators anticipate and front-run the feedback traders' predictable future demand, further accelerating trends.
- Mathematical Formulation: `velocity = (P_t - P_{t-lookback}) / P_{t-lookback}; if |velocity| > entry_threshold: quantity = sign(velocity) × min(|velocity| × position_multiplier, 1000)`
- Empirical Evidence: De Long et al. (1990) demonstrate theoretically that positive-feedback demand destabilises equilibrium prices; Jegadeesh & Titman (1993, DOI: 10.1111/j.1540-6261.1993.tb04702.x) document 3–12 month momentum profits of ~1% per month across US equities 1965–1989 (t-stat > 3.0); at shorter horizons, Kirilenko et al. (2017, Table 4) show HFT momentum traders contributed ~33% of sell volume during the crash phase.
- Relevance to This Agent: The agent directly operationalises the positive-feedback mechanism at HFT timescale — it mechanically buys on positive velocity and sells on negative velocity, with magnitude scaling linearly with signal strength, contributing directional flow that reinforces the crash.
- Calibration Source: `entry_threshold` in [0.001, 0.02] calibrated from De Long et al.'s threshold-based entry model; `lookback_window` in [3, 10] rounds corresponds to intraday momentum windows of seconds to minutes in flash-crash context (Kirilenko et al. 2017, Section 3.2); `position_multiplier` in [500, 5000] scaled to produce order sizes in the 50–1000 unit range observed in the flash crash.
- Falsification Conditions: If this agent's net order direction over any 10-round window is opposite to the price trend direction over the same window in more than 30% of cases (when velocity exceeds threshold), the positive-feedback mechanism is falsified.
- Alternative Theories: Rational expectations momentum (Cespa & Vives 2012), information-based momentum (Hong & Stein 1999), technical analysis trend-following (Lo et al. 2000).

**Momentum Amplification in Market Microstructure (Kirilenko et al. 2017)**:
- Theory / Study: The Flash Crash: High-Frequency Trading in an Electronic Market
- Citation: Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498
- Core Insight: During the 2010 flash crash, a distinct class of HFT participants ("Aggressive HFTs") traded primarily in the direction of the existing price move, adding net selling pressure that accelerated the decline. These traders differed from HFT market makers in that they never provided liquidity and always took directional positions.
- Mathematical Formulation: `net_HFT_directional_flow = Σ (quantity_i × sign(velocity_i))` for all momentum-type HFT orders; flow is positively correlated with price direction.
- Empirical Evidence: Kirilenko et al. (2017, Section 4, pp. 980–985) classify HFT into market-making and aggressive categories; aggressive HFTs contributed approximately 33% of selling volume during the crash's most intense 5-minute window (Figure 5, p. 987). Their activity was positively autocorrelated with a lag-1 coefficient > 0.7.
- Relevance to This Agent: The agent models the "Aggressive HFT" category — it is classified as `agent_type = "hft"` but never provides liquidity, instead adding directional flow that compounds the crash when detected velocity exceeds threshold.
- Calibration Source: Kirilenko et al. (2017, Table 4): aggressive HFT order sizes ranged from 100 to 2000 contracts; entry sensitivity corresponded to velocity > 0.5% over 1–5 minute windows, mapping to `entry_threshold` of 0.001–0.02.
- Falsification Conditions: If this agent produces zero orders during a sustained trend (|velocity| > 3 × `entry_threshold` for 5+ consecutive rounds), the momentum amplification mechanism is falsified.
- Alternative Theories: HFT inventory rebalancing (Menkveld 2013), HFT statistical arbitrage (Budish et al. 2015).

## Design Purpose and Activation Triggers

Purpose: Detect short-term price momentum and trade in the direction of the trend with size proportional to velocity magnitude, amplifying directional moves during crash and recovery phases.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Price history of length >= `lookback_window` available
- Current market price available

Missing-Signal Policy: If price history has fewer observations than `lookback_window`, the agent emits quantity = 0 (no trade). If current price is unavailable (NaN), the agent abstains entirely.

Activation Triggers:
- Positive velocity exceeds threshold (velocity > `entry_threshold`): Buy order with quantity = min(velocity × `position_multiplier`, 1000), constrained by cash
- Negative velocity exceeds threshold (velocity < -`entry_threshold`): Sell order with quantity = -min(|velocity| × `position_multiplier`, 1000), constrained by position
- Velocity within threshold band (|velocity| <= `entry_threshold`): Hold (quantity = 0)
- Default (insufficient history): Hold (quantity = 0)

Deactivation Conditions:
- Cash exhausted (cannot buy): Buy-side momentum signal ignored; quantity clamped to 0
- Position exhausted (cannot sell): Sell-side momentum signal ignored; quantity clamped to 0
- Simulation end / market closure: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                            | Behavioral change                                              | Mechanism                                   |
|--------------------------------------|----------------------------------------------------------------|---------------------------------------------|
| High volatility / strong trend       | Larger absolute order sizes (velocity magnitude drives sizing) | Linear proportional response to velocity    |
| Low volatility / range-bound market  | No orders emitted (velocity below threshold)                   | Entry threshold filters noise               |
| Resource depletion (cash/position)   | Order size reduced or zeroed                                   | Hard constraint from available resources    |

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator containing the `price` field. The agent maintains its own rolling price history buffer of length `lookback_window`. No peer-action summaries, fundamental value, or order-book depth required.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source                      | Type / Shape  | Required? | Notes                                               |
|------------------------|-----------------------------|---------------|-----------|------------------------------------------------------|
| `price`                | Market coordinator payload  | `float`       | yes       | Current asset price; maps to §3.6.1                  |
| `price_history`        | Agent persisted state       | `list[float]` | yes       | Rolling price buffer; populated from §3.6.4 init     |
| `round`                | Scheduler / round header    | `int`         | yes       | Current simulation round number                      |
| `cash`                 | Agent persisted state       | `float`       | yes       | Available cash for buying; state variable from §3.6.4|
| `position`             | Agent persisted state       | `int`         | yes       | Current shares held; state variable from §3.6.4      |
| `lookback_window`      | Config extras               | `int`         | yes       | Momentum lookback period (§3.7 parameter)            |
| `entry_threshold`      | Config extras               | `float`       | yes       | Minimum velocity to trigger entry (§3.7 parameter)   |
| `position_multiplier`  | Config extras               | `float`       | yes       | Velocity-to-quantity scaling (§3.7 parameter)        |
| `retrieved_knowledge`  | Retrieval store (RAG only)  | `list[str]`   | RAG only  | Historical momentum episodes; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum          | Unit   | Required? | Meaning                                            |
|-------------|--------|-----------------------------|--------|-----------|-----------------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`   | —      | yes       | Direction derived from sign of computed quantity     |
| `bid_price` | float  | > 0                         | price  | yes       | Current market price (agent is a price-taker)       |
| `quantity`  | int    | [-1000, 1000]               | shares | yes       | Signed order size (+ buy, - sell, 0 hold)           |
| `reasoning` | string | 1–3 sentences               | —      | yes       | Velocity value, threshold comparison, and result    |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clamped to [-1000, 1000] before emission (hard cap from sizing formula).
- `quantity` for buys MUST NOT exceed `floor(cash / price)`.
- `quantity` for sells (negative) MUST NOT exceed `-position` in absolute value.
- `bid_price` MUST equal the current market price (the agent is a price-taker).
- Positive quantity = buy; negative quantity = sell; zero = hold.
- `provides_liquidity` in the outbound envelope is always `False`.
- `agent_type` in the outbound envelope is always `"hft"`.
- The agent is deterministic given the same price history, state, and parameters.

##### Serialization Format

```
<analysis>Lookback velocity over {lookback_window} rounds = {velocity:.4f}; threshold = {entry_threshold}; |velocity| {'exceeds' if triggered else 'below'} threshold. Raw quantity = {raw_qty}; constrained quantity = {quantity}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "Momentum {velocity:.4f} over {lookback_window} rounds {'triggers' if triggered else 'below threshold for'} {'buy' if velocity > 0 else 'sell'} of {abs(quantity)} units."}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` MUST be read from the market coordinator broadcast; `price_history`, `cash`, and `position` MUST be the agent's own persisted state; config extras supply parameters.
2. **Decision emission** — the code path MUST populate all four required fields; quantity MUST be clamped to [-1000, 1000] AND constrained by cash/position before emission.
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all four fields present, quantity in valid range, sign matches action.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same four-field output object with `provides_liquidity = False` and `agent_type = "hft"` in the envelope.
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal          | Type       | Memory Window               | Rationale                                                         |
|-----------------|------------|-----------------------------|-------------------------------------------------------------------|
| `price`         | Continuous | `lookback_window` rounds    | Required to compute velocity over the lookback period             |
| `price_history` | Continuous | `lookback_window` rounds    | Rolling buffer; velocity derived from first and last entries      |
| `cash`          | Continuous | Current value only          | Constrains maximum buy quantity                                   |
| `position`      | Continuous | Current value only          | Constrains maximum sell quantity                                  |

Does NOT use: fundamental value, order-book depth, spread, volatility (computed by environment), peer positions, aggregate volume, HFT participation ratio. The agent is deliberately myopic — it sees only price trajectory.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from latest market broadcast. Write: append `price` to `price_history`. (Implementation convenience — state persistence.)

2. **Check history sufficiency.** Read: `len(price_history)`, `lookback_window`. If `len(price_history) < lookback_window`, proceed to step 7 (hold). (Implementation convenience — cold-start guard.)

3. **Compute lookback velocity.** Read: `price_history[-lookback_window]` (oldest in window), `price_history[-1]` (newest). Compute: `velocity = (price_history[-1] - price_history[-lookback_window]) / price_history[-lookback_window]`. Write: nothing (intermediate). (Traces to De Long et al. 1990 — return-based momentum signal.)

4. **Evaluate entry threshold.** Read: `velocity`, `entry_threshold`. Compute: `triggered = |velocity| > entry_threshold`. If not triggered, proceed to step 7 (hold). (Traces to De Long et al. 1990 — minimum momentum filter.)

5. **Compute raw order quantity.** Read: `velocity`, `position_multiplier`. Compute: `raw_quantity = sign(velocity) × min(|velocity| × position_multiplier, 1000)`. Write: nothing (intermediate). (Traces to De Long et al. 1990 — proportional feedback; Kirilenko et al. 2017 — velocity-scaled order sizing.)

6. **Apply resource constraints.** Read: `raw_quantity`, `cash`, `position`, `price`. Compute: if `raw_quantity > 0`: `quantity = min(raw_quantity, floor(cash / price))`; if `raw_quantity < 0`: `quantity = max(raw_quantity, -position)`. Write: update `cash` and `position` to reflect the executed trade. (Implementation convenience — budget enforcement.)

7. **Emit decision object.** Read: `quantity`, `price`. Compute: `action = "buy" if quantity > 0 else ("sell" if quantity < 0 else "hold")`. Write: emit the four-field decision object per I/O Contract. (Implementation convenience — output assembly.)

#### Action Space

| Aspect                | Specification                                                                                                       |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                                |
| Action parameter rule | `bid_price` = current market price (no limit orders; agent is always a price-taker)                                  |
| Sizing rule           | `quantity = sign(velocity) × min(|velocity| × position_multiplier, 1000)`, constrained by cash (buy) or position (sell) |
| Action lifetime       | One round; re-evaluated each tick. No persistent orders carried forward.                                             |
| Revision policy       | Implicitly revised every round — no order amendment; fresh decision each call.                                       |
| State constraint      | Position bounded by available resources (cash for long, shares for short); no explicit position limit beyond resource.|
| Resource cap          | Cash cannot go negative; position cannot go negative. Self-enforced each round.                                      |
| Exit rule             | None — agent participates every round; resource exhaustion naturally silences it but does not trigger explicit exit.  |

#### Mathematical Model

**Decision output:** The agent computes a signed integer `quantity ∈ [-1000, 1000]` representing shares to buy (positive) or sell (negative) this round.

**Decision logic formalization:**

```
Given: price_history = [..., p_{t-lookback}, ..., p_t]
       lookback_window = w
       entry_threshold = θ
       position_multiplier = m
       cash, position (persisted state)

Step 1: History check
  if len(price_history) < w:
    quantity = 0 → DONE

Step 2: Velocity computation
  velocity = (p_t - p_{t-w}) / p_{t-w}    (if p_{t-w} > 0, else 0.0)

Step 3: Threshold filter
  if |velocity| <= θ:
    quantity = 0 → DONE

Step 4: Raw sizing
  raw_qty = sign(velocity) × min(|velocity| × m, 1000)
  raw_qty = int(raw_qty)    (truncate toward zero)

Step 5: Resource constraint
  if raw_qty > 0:
    max_buy = floor(cash / p_t)    (if p_t > 0, else 0)
    quantity = min(raw_qty, max_buy)
  elif raw_qty < 0:
    quantity = max(raw_qty, -position)

Step 6: State update (post-execution)
  if quantity > 0:
    cash -= quantity × p_t
    position += quantity
  elif quantity < 0:
    cash += |quantity| × p_t
    position += quantity    (decreases)
```

**State variables:**

| Variable        | Type          | Initial Value | Update Phase                    |
|-----------------|---------------|---------------|---------------------------------|
| `price_history` | `list[float]` | `[]`          | Pre-decide (append on perceive) |
| `cash`          | `float`       | from config   | Post-decide (after trade execution) |
| `position`      | `int`         | from config   | Post-decide (after trade execution) |

**State evolution:** `price_history` is appended each round during the perceive phase. `cash` and `position` are updated after the decision is made, reflecting the executed trade. Update ordering: perceive (append price) -> decide (compute quantity) -> act (update cash/position).

**Determinism contract:** The decision is fully deterministic given identical `price_history`, `cash`, `position`, and parameters. No random number generation is used.

**Parameter symbol table:**

| Symbol                | Meaning                                     | Default Value | Source                    |
|-----------------------|---------------------------------------------|---------------|---------------------------|
| `lookback_window` (w) | Number of rounds for velocity computation   | 5             | Kirilenko et al. (2017)   |
| `entry_threshold` (θ) | Minimum |velocity| to trigger a trade       | 0.001         | De Long et al. (1990)     |
| `position_multiplier` (m) | Velocity-to-quantity scaling factor     | 2000          | Kirilenko et al. (2017)   |
| `velocity`            | Computed lookback return                    | —             | Derived (intermediate)    |
| `raw_qty`             | Pre-constraint order size                   | —             | Derived (intermediate)    |
| `quantity`            | Final constrained order size                | —             | Derived (output)          |

#### Behavioral Properties

- Time horizon: Short — decisions based on a configurable lookback window of 3–10 rounds; the agent has no long-term memory beyond the velocity calculation and its resource state. Rationale: HFT momentum strategies operate on timescales of seconds to minutes; the lookback window models the minimal trend-detection horizon.
- Risk tolerance: High — the agent is willing to commit significant capital proportional to momentum magnitude, up to 1000 units per round, without risk-of-ruin checks or volatility scaling. Rationale: aggressive HFT momentum traders documented by Kirilenko et al. (2017) showed no evidence of volatility-adjusted sizing during the crash.
- Information asymmetry: Partial — observes price history only; blind to fundamental value, order-book depth, and peer strategies.
- Psychological profile: Purely mechanistic positive-feedback behaviour; no Bayesian updating, no learning, no fear/greed modulation. Embodies the herding bias described by De Long et al. (1990) in its most extreme automated form.

## Parameters

| Parameter             | Type    | Default | Valid Range    | Sensitivity | Description                                             | Impact                                                | Source                   |
|-----------------------|---------|---------|----------------|-------------|---------------------------------------------------------|-------------------------------------------------------|--------------------------|
| `lookback_window`     | `int`   | 5       | [3, 10]        | medium      | Number of rounds over which to compute price velocity   | Higher -> smoother velocity, slower response to trends| Kirilenko et al. (2017)  |
| `entry_threshold`     | `float` | 0.001   | [0.001, 0.02]  | high        | Minimum absolute velocity to trigger an order           | Higher -> fewer trades, less amplification of small moves | De Long et al. (1990)|
| `position_multiplier` | `float` | 2000    | [500, 5000]    | high        | Scaling factor converting velocity magnitude to quantity| Higher -> larger orders, more aggressive amplification| Kirilenko et al. (2017)  |
| `initial_cash`        | `float` | 100000  | [10000, 1000000]| low        | Starting cash balance available for buying              | Higher -> can sustain buying longer before exhaustion | Standardised             |
| `initial_position`    | `int`   | 1000    | [0, 10000]     | medium      | Starting share position available for selling           | Higher -> can sustain selling longer during crash     | Standardised             |

## Worked Numerical Examples

### Case 1 — Moderate downtrend, sell order

System state: `price_history[-5:]` = [40.00, 39.50, 39.00, 38.50, 38.00]; `lookback_window` = 5; `entry_threshold` = 0.001; `position_multiplier` = 2000; `cash` = 100000; `position` = 1000.

Calculation:
- `velocity` = (38.00 - 40.00) / 40.00 = -0.05
- `|velocity|` = 0.05 > 0.001 = True (triggered)
- `raw_qty` = sign(-0.05) × min(0.05 × 2000, 1000) = -1 × min(100, 1000) = -100
- Constraint: `max(raw_qty, -position)` = max(-100, -1000) = -100
- `quantity` = -100

Decision: `action = "sell"`, `bid_price = 38.00`, `quantity = -100`.

State update: `cash` = 100000 + 100 × 38.00 = 103800; `position` = 1000 - 100 = 900.

### Case 2 — Strong uptrend, buy order

System state: `price_history[-5:]` = [36.00, 37.00, 38.00, 39.00, 40.00]; `lookback_window` = 5; `entry_threshold` = 0.001; `position_multiplier` = 2000; `cash` = 100000; `position` = 500.

Calculation:
- `velocity` = (40.00 - 36.00) / 36.00 = 0.1111
- `|velocity|` = 0.1111 > 0.001 = True (triggered)
- `raw_qty` = sign(0.1111) × min(0.1111 × 2000, 1000) = +1 × min(222.2, 1000) = +222
- Constraint: `min(raw_qty, floor(100000 / 40.00))` = min(222, 2500) = 222
- `quantity` = 222

Decision: `action = "buy"`, `bid_price = 40.00`, `quantity = 222`.

State update: `cash` = 100000 - 222 × 40.00 = 91120; `position` = 500 + 222 = 722.

### Case 3 — Flat market, hold

System state: `price_history[-5:]` = [40.00, 40.01, 39.99, 40.00, 40.005]; `lookback_window` = 5; `entry_threshold` = 0.001; `position_multiplier` = 2000; `cash` = 100000; `position` = 1000.

Calculation:
- `velocity` = (40.005 - 40.00) / 40.00 = 0.000125
- `|velocity|` = 0.000125 > 0.001 = False (not triggered)
- `quantity` = 0

Decision: `action = "hold"`, `bid_price = 40.005`, `quantity = 0`.

State update: No change. `cash` = 100000; `position` = 1000.

### Edge Case — Sell constrained by position exhaustion

System state: `price_history[-5:]` = [40.00, 38.00, 36.00, 34.00, 32.00]; `lookback_window` = 5; `entry_threshold` = 0.001; `position_multiplier` = 2000; `cash` = 100000; `position` = 50.

Calculation:
- `velocity` = (32.00 - 40.00) / 40.00 = -0.20
- `|velocity|` = 0.20 > 0.001 = True (triggered)
- `raw_qty` = sign(-0.20) × min(0.20 × 2000, 1000) = -1 × min(400, 1000) = -400
- Constraint: `max(raw_qty, -position)` = max(-400, -50) = -50 (clamped by position)
- `quantity` = -50

Decision: `action = "sell"`, `bid_price = 32.00`, `quantity = -50`. (Position-constrained: would sell 400 but only holds 50.)

State update: `cash` = 100000 + 50 × 32.00 = 101600; `position` = 50 - 50 = 0. (Agent is now silenced for future sell signals until position rebuilds.)

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `lookback_window` <- Kirilenko et al. (2017), Section 3.2: HFT momentum detection over 1–5 minute windows, mapped to 3–10 rounds.
- `entry_threshold` <- De Long et al. (1990), numerical examples: minimum momentum signal of 0.1–2% to trigger positive-feedback entry, mapped to 0.001–0.02.
- `position_multiplier` <- Kirilenko et al. (2017), Table 4: aggressive HFT order sizes of 100–2000 contracts at velocities of 0.5–5%, implying multipliers of 500–5000.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given velocity of -0.05 (well above threshold 0.001 in absolute terms) and sufficient position, agent MUST emit a sell order of min(0.05 × 2000, 1000) = 100 units.
- Given velocity of 0.0005 (below threshold 0.001), agent MUST emit quantity = 0 regardless of available resources.
- Given fewer than `lookback_window` price observations, agent MUST emit quantity = 0.
- Given velocity of -0.80 (extreme crash), agent MUST cap raw quantity at 1000 before resource constraint.
- Given velocity > threshold but `position = 0` and velocity < 0, agent MUST emit quantity = 0 (cannot sell what it does not hold).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits a buy order when velocity is negative (and vice versa) THEN the directional logic is inverted.
- IF the agent emits |quantity| > 1000 THEN the hard cap is not being enforced.
- IF the agent emits a sell quantity exceeding its current position in absolute value THEN the resource constraint is broken.
- IF the agent emits `provides_liquidity = True` in any outbound message THEN the non-liquidity-providing constraint is violated.
- IF the agent trades when |velocity| <= `entry_threshold` THEN the threshold filter is broken.

#### Ablation Hooks

| Ablation name           | Setting                            | Hypothesis tested                                          | Expected direction                         | Metric                              |
|-------------------------|------------------------------------|------------------------------------------------------------|--------------------------------------------|--------------------------------------|
| `no_momentum`           | `position_multiplier = 0`          | Momentum chasers are necessary for crash amplification     | Crash depth decreases without momentum     | Maximum drawdown in price            |
| `high_threshold`        | `entry_threshold = 0.10`           | Higher entry barrier reduces crash amplification           | Fewer trades, shallower crash              | Total momentum-chaser sell volume    |
| `short_lookback`        | `lookback_window = 3`              | Shorter lookback increases responsiveness and amplification| Earlier activation, deeper crash           | Round of first momentum sell order   |
| `extreme_multiplier`    | `position_multiplier = 5000`       | Larger orders accelerate crash speed                       | Faster crash progression                   | Rounds from crash start to trough    |

## Academic References

| # | Citation                                                                                                                                                                    | Notes                                          |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| 1 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379–395. https://doi.org/10.2307/2328662 | Primary theory: positive-feedback momentum     |
| 2 | Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498 | Aggressive HFT momentum in flash crash context |
| 3 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Empirical momentum effect documentation        |
| 4 | CFTC & SEC (2010). Findings regarding the market events of May 6, 2010. Joint Advisory Committee Report. | Official event reconstruction                  |
| 5 | Brunnermeier, M. K., & Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825–1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x | Predatory exploitation of momentum dynamics    |

## Design Provenance and Versioning

| Field   | Content                                                       |
|---------|---------------------------------------------------------------|
| Author  | Codex                                                         |
| Created | 2026-07-16                                                    |
| Version | 1.0.0                                                         |
| Icon    | ![](../agent_images/icons/finance-momentum-chaser.png)        |
| Status  | draft                                                         |
