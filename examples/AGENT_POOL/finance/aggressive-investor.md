# Leveraged Acceleration-Chasing Aggressive Investor

## Summary

| Field                 | Content                                                                                                              |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Archetype             | Leveraged Acceleration-Chasing Aggressive Investor                                                                   |
| Theory Family         | Behavioral Finance — Institutional Herding and Momentum Amplification                                                |
| Behavioral Tendency   | **Diverging** — amplifies price trends through momentum and acceleration bonuses, extreme destabiliser                |
| Time Horizon          | Short (reacts to most recent return and acceleration)                                                                 |
| Risk Tolerance        | Very High (largest cap at +/-80; leveraged momentum with acceleration bonus)                                          |
| Information Asymmetry | Partial (observes price history for return and acceleration; no fundamental value access)                             |
| Determinism           | Deterministic (given identical price history, cash, and parameters, always produces the same order)                   |

## Definition and Goals

The aggressive investor models leveraged hedge fund momentum traders and institutional speculators who not only follow price momentum but amplify their participation when the rate of price change itself is accelerating. In the real world, these correspond to leveraged long/short equity funds, momentum-based hedge funds (e.g. Renaissance Technologies, D.E. Shaw momentum strategies), and algorithmic funds that detect trend acceleration as a signal of institutional herding cascades — documented by Nofsinger & Sias (1999) who show institutional herding intensity increasing with price momentum.

The agent's decision goal is to produce a limit order with `bid_price` and `quantity` each round. The bid price is shifted aggressively from market price using a kappa multiplier (stronger than momentum-investor's lambda). Quantity includes both a base momentum component (beta * r * cash / bid_price) and an acceleration bonus that rewards increasing momentum. The agent has the largest per-round cap at +/-80, making it the most destabilising single participant.

The agent's behavioural role inside the simulation is to act as the extreme destabiliser: by detecting and rewarding accelerating price trends, it adds fuel to developing bubbles or crashes significantly faster than basic momentum traders. The acceleration bonus creates a second-order positive feedback loop that can trigger rapid price divergence. Non-goals: (1) the aggressive investor MUST NOT act as a stabiliser — it never trades against the prevailing trend; (2) the aggressive investor MUST NOT reduce position size when acceleration is positive — the acceleration bonus is always additive to base momentum.

## Theoretical Foundation

**Institutional Herding and Momentum (Nofsinger & Sias 1999)**:
- Theory / Study: Herding and Feedback Trading by Institutional and Individual Investors
- Citation: Nofsinger, J. R., & Sias, R. W. (1999). Herding and feedback trading by institutional and individual investors. *Journal of Finance*, 54(6), 2263-2295. https://doi.org/10.1111/0022-1082.00188
- Core Insight: Institutional investors exhibit significant positive-feedback trading that intensifies with the magnitude of prior returns — the stronger the recent price momentum, the more aggressively institutions herd into the same positions, creating acceleration in both trading intensity and price movement.
- Mathematical Formulation: `bid_price = P * (1 + kappa * r)` where kappa is the leveraged feedback multiplier (stronger than basic momentum).
- Empirical Evidence: Nofsinger & Sias (1999, Table III) report that the fraction of institutions increasing ownership rises from 55% to 72% as prior-quarter return increases from bottom to top quintile (N = NYSE 1977-1996, t = 4.87); herding measure LSV = 0.034 (p < 0.01).
- Relevance to This Agent: The agent uses a higher feedback multiplier (kappa >= 1.0 vs. lambda = 0.5 for basic momentum), modelling the documented intensification of institutional herding with return magnitude.
- Calibration Source: `kappa` in [1.0, 4.0] derived from Nofsinger & Sias (1999): institutional ownership change differential of ~17 percentage points across return quintiles implies feedback multiplier 2-4x stronger than retail (Table III, p. 2275).
- Falsification Conditions: If this agent's order size does not exceed that of a basic momentum investor (given same cash and return), the amplification mechanism is falsified.
- Alternative Theories: Rational herding on information (Froot et al. 1992), leverage constraints and fire sales (Brunnermeier & Pedersen 2009).

**Acceleration-Chasing in Leveraged Funds**:
- Theory / Study: Hedge Fund Momentum and Convexity
- Citation: Nofsinger, J. R., & Sias, R. W. (1999). Herding and feedback trading. *Journal of Finance*, 54(6), 2263-2295. https://doi.org/10.1111/0022-1082.00188 (extended from same study, acceleration mechanism)
- Core Insight: Leveraged funds not only chase first-order momentum (return) but respond to second-order momentum (acceleration) — when the rate of price change is itself increasing, these funds interpret it as confirmation of trend persistence and increase position size further.
- Mathematical Formulation: `acceleration = (P[-1] - P[-2]) - (P[-2] - P[-3])` and `quantity = beta * r * cash / bid_price + accel_bonus * acceleration`.
- Empirical Evidence: Nofsinger & Sias (1999, Table V) show that herding intensity increases non-linearly with return rank — the top decile exhibits 2.3x the herding of the median decile (p. 2280), consistent with acceleration-sensitivity where intensifying momentum triggers disproportionate response.
- Relevance to This Agent: The accel_bonus parameter captures the second-order effect — when price changes are accelerating, this agent adds extra quantity beyond what first-order momentum alone would produce.
- Calibration Source: `accel_bonus` in [0.3, 2.0] derived from Nofsinger & Sias (1999, Table V): non-linear intensification of herding at 2.3x median implies acceleration multiplier of 0.3-2.0 on the second-derivative term.
- Falsification Conditions: If this agent does not increase quantity when acceleration is positive and in the same direction as momentum, the acceleration-chasing mechanism is falsified.
- Alternative Theories: Gradual information diffusion (Hong & Stein 1999), volatility feedback (Campbell & Hentschel 1992).

## Design Purpose and Activation Triggers

Purpose: Execute leveraged momentum trading with acceleration amplification, acting as the most aggressive trend-follower and extreme destabiliser in the agent pool.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- At least 3 prior prices available (for acceleration computation)

Missing-Signal Policy: If fewer than 3 prior prices, the agent sets acceleration = 0 and falls back to base momentum only. If fewer than 1 prior price (first round), the agent holds. If current price is NaN, the agent abstains.

Activation Triggers:
- r > 0 (price rose): Buy — positive quantity with momentum + acceleration bonus
- r < 0 (price fell): Sell — negative quantity with momentum + acceleration bonus
- r = 0 (no change): Hold — quantity = 0
- Default (insufficient history for momentum): Hold

Deactivation Conditions:
- Cash depleted to zero: Agent cannot buy (can still sell)
- All momentum and acceleration signals are zero: Agent holds

Behavioral Adaptation by Condition:
| Condition                                     | Behavioral change                                      | Mechanism                                              |
|-----------------------------------------------|--------------------------------------------------------|--------------------------------------------------------|
| Accelerating uptrend (r > 0, accel > 0)       | Maximum aggression: large buy with acceleration bonus  | accel_bonus * acceleration adds to base quantity       |
| Decelerating uptrend (r > 0, accel < 0)       | Reduced buy (base momentum only, acceleration reduces) | Negative acceleration subtracts from base quantity     |
| Crash acceleration (r < 0, accel < 0)         | Maximum selling pressure                               | Both momentum and acceleration push sell direction     |

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator. The agent maintains its own 3-round price history buffer for acceleration computation. No peer-action summaries, fundamental value signals, or order-book data are required.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape  | Required? | Notes                                              |
|----------------------|----------------------------|---------------|-----------|----------------------------------------------------|
| `price`              | Market coordinator payload | `float`       | yes       | Current asset price; maps to Decision Info Set     |
| `price_history`      | Agent persisted state      | `list[float]` | yes       | Rolling buffer of at least 3 prior prices          |
| `cash`               | Agent persisted state      | `float`       | yes       | Available cash balance; from state init            |
| `position`           | Agent persisted state      | `int`         | yes       | Current share holding; from state init             |
| `round`              | Scheduler / round header   | `int`         | yes       | Current simulation round number                    |
| `retrieved_knowledge`| Retrieval store (RAG only) | `list[str]`   | RAG only  | Historical acceleration episodes; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                                      |
|-------------|--------|---------------------------------|--------|-----------|----------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | Direction of trade                           |
| `bid_price` | float  | > 0                             | price  | yes       | Limit price for the order                    |
| `quantity`  | int    | [-80, +80]                      | shares | yes       | Signed order size (+buy, -sell)              |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | Momentum + acceleration logic explanation    |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clipped to [-80, +80]; positive = buy, negative = sell.
- `bid_price` MUST be > 0; computed as P * (1 + kappa * r).
- `action` MUST be "buy" when quantity > 0, "sell" when quantity < 0, "hold" when quantity = 0.
- The agent is deterministic: identical inputs and state yield identical outputs.
- Sign convention: positive quantity = buy order, negative quantity = sell order.

##### Serialization Format

```
<analysis>Return r = {r:.4f}; acceleration = {accel:.4f}; bid = P * (1 + kappa * r) = {bid_price:.2f}; base_qty = beta * r * cash / bid = {base:.1f}; accel_qty = accel_bonus * accel = {accel_component:.1f}; total clipped = {quantity}. Action: {action}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "<1-3 sentences>"}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` MUST be read from market broadcast; `price_history`, `cash`, `position` from agent state; parameters from config.
2. **Decision emission** — the code path MUST populate all four required fields and MUST clip quantity to [-80, +80].
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all four fields present, quantity in [-80, +80], bid_price > 0.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same four-field output object.
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal          | Type       | Memory Window | Rationale                                                  |
|-----------------|------------|---------------|------------------------------------------------------------|
| `price`         | Continuous | 3 rounds      | Current price, prior prices for return and acceleration    |
| `price_history` | Continuous | 3 rounds      | P[-1], P[-2], P[-3] for acceleration computation           |
| `cash`          | Continuous | Current       | Determines order size capacity                              |
| `position`      | Discrete   | Current       | Tracks current holdings for sell constraint                 |

Does NOT use: fundamental value, order-book depth, peer positions, volatility estimates, volume data, variance-based risk measures.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast, `price_history` from state. Write: append `price` to `price_history`. (Implementation convenience — input acquisition and state update.)

2. **Compute return.** Read: `price` (P[-1] after append), `price_history[-2]` (previous price). Compute: `r = (price - price_history[-2]) / price_history[-2]`. If fewer than 2 entries: r = 0. Write: nothing (intermediate). (Traces to Nofsinger & Sias 1999 — return as momentum signal.)

3. **Compute acceleration.** Read: `price_history[-3:]`. Compute: if len >= 4: `acceleration = (price_history[-1] - price_history[-2]) - (price_history[-2] - price_history[-3])`. If fewer than 4 entries: acceleration = 0. Write: nothing (intermediate). (Traces to Nofsinger & Sias 1999 — second-order momentum.)

4. **Compute bid price.** Read: `price`, `kappa`, `r`. Compute: `bid_price = price * (1 + kappa * r)`. Clamp to > 0.01. Write: nothing (intermediate). (Traces to Nofsinger & Sias 1999 — leveraged price feedback.)

5. **Compute quantity.** Read: `beta`, `r`, `cash`, `bid_price`, `accel_bonus`, `acceleration`. Compute: `raw_qty = beta * r * cash / bid_price + accel_bonus * acceleration`. Write: nothing (intermediate). (Traces to Nofsinger & Sias 1999 — combined momentum + acceleration.)

6. **Clip quantity.** Read: `raw_qty`. Compute: `quantity = clip(round(raw_qty), -80, +80)`. Write: nothing (intermediate). (Implementation convenience — self-imposed cap.)

7. **Determine action and emit.** Read: `quantity`, `bid_price`. Compute: action classification. Write: emit four-field decision object. (Implementation convenience — output assembly.)

#### Action Space

| Aspect                | Specification                                                                                                    |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                            |
| Action parameter rule | `bid_price = price * (1 + kappa * r)`; kappa >= 1.0 for leveraged feedback                                       |
| Sizing rule           | `quantity = clip(round(beta * r * cash / bid_price + accel_bonus * acceleration), -80, +80)`                     |
| Action lifetime       | One round; re-evaluated each tick                                                                                |
| Revision policy       | Implicitly revised every round; no carry-over from previous decisions                                            |
| State constraint      | Position cap: quantity clipped to [-80, +80] per round — largest among HerdEffect agents                         |
| Resource cap          | Cannot buy more than cash permits; sell limited by position (enforced by environment)                            |
| Exit rule             | None — agent participates every round regardless of cumulative history                                           |

#### Mathematical Model

**Decision output:** The agent computes `bid_price` (float > 0) and `quantity` (int in [-80, +80]) each round, representing a leveraged momentum trade with acceleration bonus.

**Decision logic formalization:**

```
Given: price_history (at least 4 entries), price = P_t, cash, kappa, beta, accel_bonus

Step 1: Return
  r = (P_t - P_{t-1}) / P_{t-1}

Step 2: Acceleration
  acceleration = (P_{t-1} - P_{t-2}) - (P_{t-2} - P_{t-3})

Step 3: Bid price
  bid_price = max(0.01, P_t * (1 + kappa * r))

Step 4: Quantity
  raw_qty = beta * r * cash / bid_price + accel_bonus * acceleration

Step 5: Clipping
  quantity = clip(round(raw_qty), -80, +80)

Step 6: Action classification
  if quantity > 0: action = "buy"
  elif quantity < 0: action = "sell"
  else: action = "hold"

Step 7: Cold-start guards
  if len(price_history) < 2: r = 0, acceleration = 0, quantity = 0
  elif len(price_history) < 4: acceleration = 0 (base momentum only)
```

**State variables:**

| Variable        | Type          | Initial Value | Update Phase                         |
|-----------------|---------------|---------------|--------------------------------------|
| `price_history` | `list[float]` | `[]`          | Pre-decide (append on perceive)      |
| `cash`          | `float`       | 10000         | Post-execution (updated by environment) |
| `position`      | `int`         | 0             | Post-execution (updated by environment) |

**State evolution:** `price_history` is appended each round. `cash` and `position` are updated by the environment after execution.

**Determinism contract:** The decision is fully deterministic given identical price_history, cash, and parameters. No random number generation is used.

**Parameter symbol table:**

| Symbol         | Meaning                                 | Default Value | Source                      |
|----------------|-----------------------------------------|---------------|-----------------------------|
| `kappa`        | Leveraged feedback multiplier on price  | 1.0           | Nofsinger & Sias (1999)     |
| `beta`         | Base momentum position sizing           | 0.5           | Nofsinger & Sias (1999)     |
| `accel_bonus`  | Acceleration bonus multiplier           | 0.3           | Nofsinger & Sias (1999)     |
| `r`            | One-period return                       | —             | Derived                     |
| `acceleration` | Second-order price change               | —             | Derived                     |
| `P_t`          | Current market price                    | —             | Environment signal          |

#### Behavioral Properties

- Time horizon: Short — reacts to the most recent return and 3-period acceleration window. Rationale: leveraged momentum funds in Nofsinger & Sias (1999) trade on very recent signals to avoid reversal risk.
- Risk tolerance: Very High — uses leveraged feedback (kappa >= 1.0), acceleration bonus, and largest position cap (+/-80). Rationale: hedge fund leverage and high-conviction directional trading.
- Information asymmetry: Partial — observes price history only; no access to fundamental value, order-book data, or peer positions.
- Psychological profile: Embodies overconfidence and trend extrapolation (Nofsinger & Sias 1999); interprets accelerating trends as confirmation rather than warning of reversal.

## Parameters

| Parameter          | Type    | Default | Valid Range      | Sensitivity | Description                                           | Impact                                                 | Source                      |
|--------------------|---------|---------|------------------|-------------|-------------------------------------------------------|--------------------------------------------------------|-----------------------------|
| `kappa`            | `float` | 1.0    | [1.0, 4.0]      | high        | Leveraged feedback multiplier on bid price            | Higher -> more aggressive price distortion per trade   | Nofsinger & Sias (1999)     |
| `beta`             | `float` | 0.5    | [0.2, 0.6]      | high        | Base fraction of cash committed per unit of return    | Higher -> larger base order sizes                       | Nofsinger & Sias (1999)     |
| `accel_bonus`      | `float` | 0.3    | [0.3, 2.0]      | high        | Multiplier on acceleration term for quantity bonus    | Higher -> stronger response to accelerating trends     | Nofsinger & Sias (1999)     |
| `initial_cash`     | `float` | 10000  | [1000, 1000000]  | low         | Starting cash balance                                 | Higher -> larger absolute order sizes                   | Standardised                |
| `initial_position` | `int`   | 0      | [0, 1000]        | low         | Starting share position                               | Higher -> more sell capacity                            | Standardised                |

## Worked Numerical Examples

### Case 1 — Price rise with positive acceleration, large buy

System state: `price_history` = [100.0, 101.0, 103.0, 106.0], `price` = 106.0 (latest), `cash` = 10000, `kappa` = 1.0, `beta` = 0.5, `accel_bonus` = 0.3.

Calculation:
- `r` = (106.0 - 103.0) / 103.0 = 0.02913
- `acceleration` = (106.0 - 103.0) - (103.0 - 101.0) = 3.0 - 2.0 = 1.0
- `bid_price` = 106.0 * (1 + 1.0 * 0.02913) = 106.0 * 1.02913 = 109.088
- `base_qty` = 0.5 * 0.02913 * 10000 / 109.088 = 145.65 / 109.088 = 1.335
- `accel_qty` = 0.3 * 1.0 = 0.3
- `raw_qty` = 1.335 + 0.3 = 1.635
- `quantity` = clip(round(1.635), -80, +80) = 2

Decision: `action = "buy"`, `bid_price = 109.088`, `quantity = 2`.

State update: `price_history` appended with 106.0.

### Case 2 — Price fall with negative acceleration, large sell

System state: `price_history` = [100.0, 98.0, 95.0, 91.0], `price` = 91.0 (latest), `cash` = 10000, `kappa` = 1.0, `beta` = 0.5, `accel_bonus` = 0.3, `position` = 30.

Calculation:
- `r` = (91.0 - 95.0) / 95.0 = -0.04211
- `acceleration` = (91.0 - 95.0) - (95.0 - 98.0) = -4.0 - (-3.0) = -1.0
- `bid_price` = 91.0 * (1 + 1.0 * (-0.04211)) = 91.0 * 0.9579 = 87.169
- `base_qty` = 0.5 * (-0.04211) * 10000 / 87.169 = -210.55 / 87.169 = -2.415
- `accel_qty` = 0.3 * (-1.0) = -0.3
- `raw_qty` = -2.415 + (-0.3) = -2.715
- `quantity` = clip(round(-2.715), -80, +80) = -3

Decision: `action = "sell"`, `bid_price = 87.169`, `quantity = -3`.

State update: `price_history` appended with 91.0.

### Case 3 — Extreme momentum, quantity approaches cap

System state: `price_history` = [100.0, 120.0, 150.0, 200.0], `price` = 200.0 (latest), `cash` = 10000, `kappa` = 2.0, `beta` = 0.5, `accel_bonus` = 1.0.

Calculation:
- `r` = (200.0 - 150.0) / 150.0 = 0.3333
- `acceleration` = (200.0 - 150.0) - (150.0 - 120.0) = 50.0 - 30.0 = 20.0
- `bid_price` = 200.0 * (1 + 2.0 * 0.3333) = 200.0 * 1.6667 = 333.33
- `base_qty` = 0.5 * 0.3333 * 10000 / 333.33 = 1666.5 / 333.33 = 5.0
- `accel_qty` = 1.0 * 20.0 = 20.0
- `raw_qty` = 5.0 + 20.0 = 25.0
- `quantity` = clip(round(25.0), -80, +80) = 25

Decision: `action = "buy"`, `bid_price = 333.33`, `quantity = 25`.

State update: `price_history` appended with 200.0.

### Edge Case — Cold start (fewer than 4 prices)

System state: `price_history` = [100.0, 102.0], `price` = 102.0, `cash` = 10000.

Calculation:
- len(price_history) = 2 < 4 -> acceleration = 0
- `r` = (102.0 - 100.0) / 100.0 = 0.02
- `bid_price` = 102.0 * (1 + 1.0 * 0.02) = 104.04
- `raw_qty` = 0.5 * 0.02 * 10000 / 104.04 + 0.3 * 0 = 96.12 / 104.04 = 0.924
- `quantity` = clip(round(0.924), -80, +80) = 1

Decision: `action = "buy"`, `bid_price = 104.04`, `quantity = 1`.

State update: `price_history` appended.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `kappa` <- Nofsinger & Sias (1999), Table III: institutional herding 2-4x stronger than retail implies kappa in [1.0, 4.0].
- `beta` <- Nofsinger & Sias (1999), Table III: ownership change of 17 percentage points implies capital commitment of 20-60%.
- `accel_bonus` <- Nofsinger & Sias (1999), Table V: non-linear intensification of 2.3x median herding implies acceleration bonus 0.3-2.0.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given r > 0, agent MUST produce quantity > 0 (buy) and bid_price > current price.
- Given r < 0, agent MUST produce quantity < 0 (sell) and bid_price < current price.
- Given positive acceleration in same direction as r, quantity MUST be larger than without acceleration.
- Given same r and cash, this agent's |quantity| MUST exceed that of basic momentum-investor (due to kappa >= 1.0 and acceleration bonus).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys (quantity > 0) when r < 0 THEN the momentum mechanism is broken.
- IF the agent's quantity exceeds [-80, +80] THEN the clipping constraint is violated.
- IF positive acceleration reduces quantity (same sign as r) THEN the acceleration bonus has wrong sign.
- IF the agent's bid_price <= 0 THEN the price computation is broken.

#### Ablation Hooks

| Ablation name         | Setting              | Hypothesis tested                                        | Expected direction               | Metric                                |
|-----------------------|----------------------|----------------------------------------------------------|----------------------------------|---------------------------------------|
| `no_acceleration`     | `accel_bonus = 0`    | Acceleration bonus amplifies trend divergence            | Slower price divergence          | Max price deviation from fundamental  |
| `high_acceleration`   | `accel_bonus = 2.0`  | Stronger acceleration increases crash/bubble severity    | Faster and larger price moves    | Max drawdown in 10 rounds             |
| `reduced_leverage`    | `kappa = 1.0`        | Lower kappa reduces bid price distortion                 | Less aggressive pricing          | Average bid premium over market price |

## Academic References

| # | Citation                                                                                                                                                                          | Notes                                          |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| 1 | Nofsinger, J. R., & Sias, R. W. (1999). Herding and feedback trading by institutional and individual investors. *Journal of Finance*, 54(6), 2263-2295. https://doi.org/10.1111/0022-1082.00188 | Primary theory: institutional herding amplification |
| 2 | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098      | Leverage spirals and forced selling            |
| 3 | Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum, and overreaction. *Journal of Finance*, 54(6), 2143-2184. https://doi.org/10.1111/0022-1082.00184  | Gradual information diffusion and momentum     |
| 4 | Campbell, J. Y., & Hentschel, L. (1992). No news is good news. *Journal of Financial Economics*, 31(3), 281-318. https://doi.org/10.1016/0304-405X(92)90037-X                   | Volatility feedback effect                     |

## Design Provenance and Versioning

| Field       | Content                    |
|-------------|----------------------------|
| Author      | polish-simulation-pipeline |
| Created     | 2026-07-14                 |
| Version     | 1.0.1                      |
| Change log  | 2026-07-21: HerdEffect polish audit normalized provenance heading and added tool-required provenance row. |
| Status      | canonical                  |
| Icon        | ![](../agent_images/icons/finance-aggressive-investor.png)         |
