# Positive Feedback Momentum Trader

## Summary

| Field                 | Content                                                                                                     |
|-----------------------|-------------------------------------------------------------------------------------------------------------|
| Archetype             | Positive Feedback Momentum Trader                                                                           |
| Theory Family         | Behavioral Finance — Momentum and Positive Feedback Trading                                                 |
| Behavioral Tendency   | **Diverging** — buys when price rises and sells when price falls, amplifying deviations from fundamental    |
| Time Horizon          | Short (reacts to most recent return only)                                                                   |
| Risk Tolerance        | High (chases price moves without hedging or fundamental anchor)                                             |
| Information Asymmetry | Partial (observes price history; no access to fundamental value)                                            |
| Determinism           | Deterministic (given identical price and cash, always produces the same order)                              |

## Definition and Goals

The momentum investor models retail and institutional trend-followers who buy assets that have recently risen in price and sell assets that have recently fallen. In the real world, these correspond to retail momentum traders, trend-following CTAs, and algorithmic momentum strategies that exploit short-term serial correlation in returns. This participant type is extensively documented in Jegadeesh & Titman (1993) who find that buying past winners and selling past losers generates significant abnormal returns over 3-12 month horizons.

The agent's decision goal is to produce a limit order with `bid_price` and `quantity` each round. The bid price is shifted from the current market price in the direction of the recent return (higher bid when price rises, lower when it falls). Quantity is proportional to the magnitude of the return and the agent's available cash. The agent follows a deterministic positive-feedback rule rather than optimising an explicit utility function.

The agent's behavioural role inside the simulation is to act as the primary herding amplifier: by buying into rallies and selling into declines, it reinforces price trends and can push the market away from fundamental value. In multi-agent simulations of herd behaviour, this agent generates the core positive-feedback loop that Shiller (1984) identifies as the driver of excess volatility. Non-goals: (1) the momentum investor MUST NOT incorporate fundamental value in its decision — it reacts solely to price momentum; (2) the momentum investor MUST NOT act as a stabiliser — it never trades against the prevailing trend.

## Theoretical Foundation

**Irrational Exuberance and Positive Feedback Trading (Shiller 1984)**:
- Theory / Study: Stock Prices and Social Dynamics
- Citation: Shiller, R. J. (1984). Stock prices and social dynamics. *Brookings Papers on Economic Activity*, 1984(2), 457-510. https://doi.org/10.2307/2534436
- Core Insight: Stock price movements are amplified beyond what fundamentals warrant because investors engage in positive feedback — buying when prices rise creates further price increases, which attract further buying, generating self-reinforcing cycles of excess volatility.
- Mathematical Formulation: `bid_price = P * (1 + lambda_price * r)` where r is recent return and lambda_price controls feedback intensity.
- Empirical Evidence: Shiller (1984, Table 1) documents that actual stock price volatility exceeds the variance bound implied by subsequent dividends by a factor of 5-13x (S&P 500, 1871-1979), consistent with positive-feedback amplification (p. 466, significance at 1% level).
- Relevance to This Agent: The agent directly implements the positive feedback mechanism — its buying intensity increases with recent positive returns, creating the excess volatility Shiller identifies.
- Calibration Source: `lambda_price` in [0.5, 2.0] derived from Shiller (1984): excess volatility ratios of 5-13x imply feedback multipliers in the range 0.5-2.0 per unit return (Section III, p. 472).
- Falsification Conditions: If this agent sells when recent return r > 0 (or buys when r < 0), the positive-feedback mechanism is falsified.
- Alternative Theories: Rational expectations with information cascades (Banerjee 1992), noise trader risk (De Long et al. 1990).

**Momentum Returns (Jegadeesh & Titman 1993)**:
- Theory / Study: Returns to Buying Winners and Selling Losers
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.2307/2328882
- Core Insight: Stocks that have performed well over the past 3-12 months continue to outperform, and stocks that have performed poorly continue to underperform, generating statistically significant momentum profits averaging ~1% per month.
- Mathematical Formulation: `quantity = beta * r * cash / bid_price` where beta scales participation intensity to return magnitude.
- Empirical Evidence: Jegadeesh & Titman (1993, Table 1) report average monthly returns of 0.95-1.31% for momentum portfolios (6-month formation, 6-month holding) with t-statistics exceeding 3.0 (N = NYSE/AMEX 1965-1989).
- Relevance to This Agent: The agent's quantity scales with return magnitude, modelling the documented behaviour where momentum traders increase position size proportionally to signal strength.
- Calibration Source: `beta` in [0.1, 0.5] calibrated from Jegadeesh & Titman (1993): portfolio turnover data suggest momentum traders commit 10-50% of available capital per unit of return signal (Table 4, p. 79).
- Falsification Conditions: If this agent's quantity does not increase monotonically with |r|, the momentum-scaling mechanism is falsified.
- Alternative Theories: Overreaction hypothesis (De Bondt & Thaler 1985), underreaction to earnings (Chan et al. 1996).

## Design Purpose and Activation Triggers

Purpose: Execute positive-feedback trading that buys when price rises and sells when price falls, amplifying market trends and generating herding-driven excess volatility.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Previous market price available (to compute return)

Missing-Signal Policy: If previous price is unavailable (first round), the agent sets r = 0 and holds (quantity = 0). If current price is NaN, the agent abstains entirely.

Activation Triggers:
- r > 0 (price rose): Buy — positive quantity, bid above current price
- r < 0 (price fell): Sell — negative quantity, bid below current price
- r = 0 (no change): Hold — quantity = 0
- Default (missing signal): Hold

Deactivation Conditions:
- Cash depleted to zero: Agent cannot buy (can still sell if holding position)
- r = 0 for sustained period: Agent remains idle

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                             | Mechanism                                    |
|------------------------------|-----------------------------------------------|----------------------------------------------|
| Strong uptrend (r > 0.05)   | Larger buy orders, higher bid premium         | Linear feedback: lambda_price * r increases  |
| Strong downtrend (r < -0.05)| Larger sell orders, lower bid                 | Symmetric negative feedback on price         |
| Low volatility (r near 0)   | Minimal or no trading activity                | Quantity proportional to |r| approaches zero |

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator. The agent maintains its own record of the previous price. No peer-action summaries, fundamental value signals, or order-book data are required.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required? | Notes                                              |
|----------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes       | Current asset price; maps to Decision Info Set     |
| `previous_price`     | Agent persisted state      | `float`      | yes       | Last round's price; for return calculation         |
| `cash`               | Agent persisted state      | `float`      | yes       | Available cash balance; from state init            |
| `position`           | Agent persisted state      | `int`        | yes       | Current share holding; from state init             |
| `round`              | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `retrieved_knowledge`| Retrieval store (RAG only) | `list[str]`  | RAG only  | Historical momentum episodes; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                                      |
|-------------|--------|---------------------------------|--------|-----------|----------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | Direction of trade                           |
| `bid_price` | float  | > 0                             | price  | yes       | Limit price for the order                    |
| `quantity`  | int    | [-50, +50]                      | shares | yes       | Signed order size (+buy, -sell)              |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | Explanation of return signal and resulting order |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clipped to [-50, +50]; positive = buy, negative = sell.
- `bid_price` MUST be > 0; computed as P * (1 + lambda_price * r).
- `action` MUST be "buy" when quantity > 0, "sell" when quantity < 0, "hold" when quantity = 0.
- The agent is deterministic: identical inputs and state yield identical outputs.
- Sign convention: positive quantity = buy order, negative quantity = sell order.

##### Serialization Format

```
<analysis>Return r = {r:.4f}; lambda_price = {lambda_price}; bid = P * (1 + {lambda_price} * {r}) = {bid_price:.2f}; qty = beta * r * cash / bid = {quantity}. Action: {action}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "<1-3 sentences>"}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` MUST be read from the market coordinator broadcast; `previous_price` and `cash` from agent state; config extras supply parameters.
2. **Decision emission** — the code path MUST populate all four required fields and MUST clip quantity to [-50, +50].
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all four fields present, quantity in [-50, +50], bid_price > 0.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same four-field output object.
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal           | Type       | Memory Window | Rationale                                              |
|------------------|------------|---------------|--------------------------------------------------------|
| `price`          | Continuous | 1 round       | Current price for bid calculation and return computation |
| `previous_price` | Continuous | 1 round       | Prior price for return computation (r = (P - P_prev)/P_prev) |
| `cash`           | Continuous | Current       | Determines order size capacity                          |
| `position`       | Discrete   | Current       | Tracks current holdings for sell constraint             |

Does NOT use: fundamental value, order-book depth, peer positions, volatility estimates, volume data, any forecast of future returns.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast, `previous_price` from state. Write: nothing yet. (Implementation convenience — input acquisition.)

2. **Compute return.** Read: `price`, `previous_price`. Compute: `r = (price - previous_price) / previous_price`. Write: nothing (intermediate). (Traces to Jegadeesh & Titman 1993 — return as momentum signal.)

3. **Compute bid price.** Read: `price`, `lambda_price`, `r`. Compute: `bid_price = price * (1 + lambda_price * r)`. Write: nothing (intermediate). (Traces to Shiller 1984 — positive feedback pricing.)

4. **Compute raw quantity.** Read: `beta`, `r`, `cash`, `bid_price`. Compute: `raw_qty = beta * r * cash / bid_price`. Write: nothing (intermediate). (Traces to Jegadeesh & Titman 1993 — position sizing proportional to signal.)

5. **Clip quantity.** Read: `raw_qty`. Compute: `quantity = clip(round(raw_qty), -50, +50)`. Write: nothing (intermediate). (Implementation convenience — self-imposed position cap.)

6. **Determine action.** Read: `quantity`. Compute: if quantity > 0: action = "buy"; elif quantity < 0: action = "sell"; else: action = "hold". Write: nothing. (Implementation convenience — action classification.)

7. **Update state.** Read: `price`. Write: `previous_price = price`. (Implementation convenience — state persistence for next round.)

8. **Emit decision object.** Read: all computed fields. Write: emit the four-field decision object per I/O Contract serialization format. (Implementation convenience — output assembly.)

#### Action Space

| Aspect                | Specification                                                                                          |
|-----------------------|--------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                  |
| Action parameter rule | `bid_price = price * (1 + lambda_price * r)`; shifted in direction of return                          |
| Sizing rule           | `quantity = clip(round(beta * r * cash / bid_price), -50, +50)`                                       |
| Action lifetime       | One round; re-evaluated each tick                                                                      |
| Revision policy       | Implicitly revised every round; no carry-over from previous decisions                                  |
| State constraint      | Position cap: quantity clipped to [-50, +50] per round                                                 |
| Resource cap          | Cannot buy more than cash permits; sell limited by position (enforced by environment)                  |
| Exit rule             | None — agent participates every round regardless of cumulative history                                 |

#### Mathematical Model

**Decision output:** The agent computes `bid_price` (float > 0) and `quantity` (int in [-50, +50]) each round, determining the direction and size of a momentum trade.

**Decision logic formalization:**

```
Given: price = P_t, previous_price = P_{t-1}, cash, position

Step 1: Return computation
  r = (P_t - P_{t-1}) / P_{t-1}

Step 2: Bid price
  bid_price = P_t * (1 + lambda_price * r)

Step 3: Quantity computation
  raw_qty = beta * r * cash / bid_price

Step 4: Clipping
  quantity = clip(round(raw_qty), -50, +50)

Step 5: Action classification
  if quantity > 0: action = "buy"
  elif quantity < 0: action = "sell"
  else: action = "hold"

Step 6: Cold-start guard
  if previous_price is None:
    r = 0, quantity = 0, action = "hold"
```

**State variables:**

| Variable         | Type    | Initial Value | Update Phase                         |
|------------------|---------|---------------|--------------------------------------|
| `previous_price` | `float` | None          | Post-decide (set to current price)   |
| `cash`           | `float` | 10000         | Post-execution (updated by environment) |
| `position`       | `int`   | 0             | Post-execution (updated by environment) |

**State evolution:** `previous_price` is written at the end of each round after the decision is emitted. `cash` and `position` are updated by the environment after order execution, not by the agent's own logic.

**Determinism contract:** The decision is fully deterministic given identical price, previous_price, cash, and parameters. No random number generation is used.

**Parameter symbol table:**

| Symbol         | Meaning                         | Default Value | Source                    |
|----------------|---------------------------------|---------------|---------------------------|
| `lambda_price` | Feedback intensity on bid price | 0.5           | Shiller (1984)            |
| `beta`         | Position sizing sensitivity     | 0.3           | Jegadeesh & Titman (1993) |
| `r`            | One-period return               | —             | Derived (intermediate)    |
| `P_t`          | Current market price            | —             | Environment signal        |
| `P_{t-1}`      | Previous market price           | —             | Agent state               |

#### Behavioral Properties

- Time horizon: Short — reacts only to the most recent single-period return; no multi-period lookback. Rationale: momentum traders in Jegadeesh & Titman (1993) form portfolios based on recent performance windows.
- Risk tolerance: High — trades aggressively in the direction of price moves without hedging, stop-losses, or diversification. Rationale: pure positive-feedback traders do not manage downside risk.
- Information asymmetry: Partial — observes price history only; has no access to fundamental value or other agents' intentions.
- Psychological profile: Embodies extrapolation bias and trend-chasing behaviour (Shiller 1984); assumes recent returns predict future returns without rational justification.

## Parameters

| Parameter          | Type    | Default | Valid Range      | Sensitivity | Description                                    | Impact                                        | Source                    |
|--------------------|---------|---------|------------------|-------------|------------------------------------------------|-----------------------------------------------|---------------------------|
| `lambda_price`     | `float` | 0.5    | [0.5, 2.0]      | high        | Multiplier on return for bid price adjustment  | Higher -> larger price distortion per trade    | Shiller (1984)            |
| `beta`             | `float` | 0.3    | [0.1, 0.5]      | high        | Fraction of cash committed per unit of return  | Higher -> larger order sizes                   | Jegadeesh & Titman (1993) |
| `initial_cash`     | `float` | 10000  | [1000, 1000000]  | low         | Starting cash balance                          | Higher -> larger absolute order sizes          | Standardised              |
| `initial_position` | `int`   | 0      | [0, 1000]        | low         | Starting share position                        | Higher -> more capacity to sell                | Standardised              |

## Worked Numerical Examples

### Case 1 — Price rise, buy order

System state: `price` = 102.0, `previous_price` = 100.0, `cash` = 10000, `lambda_price` = 0.5, `beta` = 0.3.

Calculation:
- `r` = (102.0 - 100.0) / 100.0 = 0.02
- `bid_price` = 102.0 * (1 + 0.5 * 0.02) = 102.0 * 1.01 = 103.02
- `raw_qty` = 0.3 * 0.02 * 10000 / 103.02 = 60.0 / 103.02 = 0.582
- `quantity` = clip(round(0.582), -50, +50) = 1

Decision: `action = "buy"`, `bid_price = 103.02`, `quantity = 1`.

State update: `previous_price`: 100.0 -> 102.0.

### Case 2 — Price fall, sell order

System state: `price` = 95.0, `previous_price` = 100.0, `cash` = 10000, `lambda_price` = 0.5, `beta` = 0.3, `position` = 10.

Calculation:
- `r` = (95.0 - 100.0) / 100.0 = -0.05
- `bid_price` = 95.0 * (1 + 0.5 * (-0.05)) = 95.0 * 0.975 = 92.625
- `raw_qty` = 0.3 * (-0.05) * 10000 / 92.625 = -150.0 / 92.625 = -1.619
- `quantity` = clip(round(-1.619), -50, +50) = -2

Decision: `action = "sell"`, `bid_price = 92.625`, `quantity = -2`.

State update: `previous_price`: 100.0 -> 95.0.

### Case 3 — Large price rise, quantity capped

System state: `price` = 150.0, `previous_price` = 100.0, `cash` = 10000, `lambda_price` = 2.0, `beta` = 0.5.

Calculation:
- `r` = (150.0 - 100.0) / 100.0 = 0.50
- `bid_price` = 150.0 * (1 + 2.0 * 0.50) = 150.0 * 2.0 = 300.0
- `raw_qty` = 0.5 * 0.50 * 10000 / 300.0 = 2500.0 / 300.0 = 8.333
- `quantity` = clip(round(8.333), -50, +50) = 8

Decision: `action = "buy"`, `bid_price = 300.0`, `quantity = 8`.

State update: `previous_price`: 100.0 -> 150.0.

### Edge Case — Cold start (no previous price)

System state: `price` = 100.0, `previous_price` = None (first round), `cash` = 10000.

Calculation:
- `previous_price` is None -> cold-start guard triggered
- `r` = 0
- `quantity` = 0

Decision: `action = "hold"`, `bid_price = 100.0`, `quantity = 0`.

State update: `previous_price`: None -> 100.0.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `lambda_price` <- Shiller (1984), Section III: excess volatility ratios of 5-13x imply feedback multipliers of 0.5-2.0.
- `beta` <- Jegadeesh & Titman (1993), Table 4: momentum portfolio turnover implies 10-50% capital commitment per unit signal.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given r > 0, agent MUST produce quantity > 0 (buy) and bid_price > current price.
- Given r < 0, agent MUST produce quantity < 0 (sell) and bid_price < current price.
- Given r = 0, agent MUST produce quantity = 0 (hold).
- Quantity magnitude MUST increase monotonically with |r| (holding cash constant).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys (quantity > 0) when r < 0 THEN the positive-feedback mechanism is broken.
- IF the agent's quantity exceeds [-50, +50] THEN the clipping constraint is violated.
- IF the agent's bid_price <= 0 THEN the price computation is broken.
- IF the agent produces different outputs for identical inputs and state THEN determinism is violated.

#### Ablation Hooks

| Ablation name       | Setting              | Hypothesis tested                              | Expected direction              | Metric                                    |
|---------------------|----------------------|------------------------------------------------|---------------------------------|-------------------------------------------|
| `no_feedback`       | `lambda_price = 0`   | Price feedback amplifies trends                | Trend magnitude decreases       | Max price deviation from fundamental      |
| `high_feedback`     | `lambda_price = 2.0` | Stronger feedback increases herding intensity  | Trend magnitude increases       | Max price deviation from fundamental      |
| `low_participation` | `beta = 0.1`         | Lower participation reduces amplification      | Smaller order sizes, less trend | Average absolute quantity per round       |

## Academic References

| # | Citation                                                                                                                                                                       | Notes                                  |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------|
| 1 | Shiller, R. J. (1984). Stock prices and social dynamics. *Brookings Papers on Economic Activity*, 1984(2), 457-510. https://doi.org/10.2307/2534436                           | Primary theory: positive feedback      |
| 2 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.2307/2328882                        | Momentum returns documentation         |
| 3 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x | Noise trader positive feedback model |
| 4 | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x         | Alternative: overreaction hypothesis   |

## Design Provenance and Versioning

| Field   | Content                                                        |
|---------|----------------------------------------------------------------|
| Author  | Codex                                                          |
| Created | 2026-07-16                                                     |
| Version | 1.0.0                                                          |
| Icon    | ![](../agent_images/icons/finance-momentum-investor.png)       |
| Status  | draft                                                          |
