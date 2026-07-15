# Mean-Reversion Contrarian Investor

## Summary

| Field                 | Content                                                                                                           |
|-----------------------|-------------------------------------------------------------------------------------------------------------------|
| Archetype             | Mean-Reversion Contrarian Investor                                                                                |
| Theory Family         | Behavioral Finance — Overreaction and Mean Reversion                                                              |
| Behavioral Tendency   | **Converging** — buys when price is below fundamental, sells when above, pushing price toward equilibrium         |
| Time Horizon          | Medium (trades based on deviation from fundamental value)                                                         |
| Risk Tolerance        | Medium (takes positions against the crowd but sizes conservatively)                                               |
| Information Asymmetry | Full (knows fundamental value; partial noise in bid execution)                                                    |
| Determinism           | Stochastic-given-seed (Gaussian noise added to bid price)                                                         |

## Definition and Goals

The contrarian investor models value-oriented fund managers and institutional investors who trade against prevailing market sentiment by buying undervalued assets (price below fundamental) and selling overvalued assets (price above fundamental). In the real world, these correspond to value investors, contrarian mutual fund managers, and institutional rebalancers who exploit mean-reversion patterns documented by De Bondt & Thaler (1985) — past losers outperform past winners over subsequent 3-5 year periods.

The agent's decision goal is to produce a limit order with `bid_price` and `quantity` each round. The bid price is set near the fundamental value plus Gaussian noise (modelling execution uncertainty), and quantity is proportional to the percentage mispricing (fundamental - price) / price. The agent acts as a stabiliser, providing a gravitational pull toward fundamental value.

The agent's behavioural role inside the simulation is to act as the primary stabiliser and counterweight to momentum traders. By buying when price has fallen below fundamental and selling when it has risen above, the contrarian investor dampens herding-induced price deviations and accelerates mean reversion. Non-goals: (1) the contrarian investor MUST NOT chase momentum — it never buys into rising prices or sells into falling prices based on return signals; (2) the contrarian investor MUST NOT ignore fundamental value — every decision is anchored to the declared fundamental.

## Theoretical Foundation

**Overreaction and Mean Reversion (De Bondt & Thaler 1985)**:
- Theory / Study: Does the Stock Market Overreact?
- Citation: De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- Core Insight: Stocks that have experienced extreme past returns (winners or losers over 3-5 years) subsequently reverse: past losers outperform past winners by an average of 24.6% over the subsequent 36 months, consistent with investor overreaction to news.
- Mathematical Formulation: `quantity = beta * (fundamental - P) / P * cash / bid_price` — position size scales with percentage mispricing.
- Empirical Evidence: De Bondt & Thaler (1985, Table 1) report cumulative average residual returns of +19.6% for loser portfolios vs. -5.0% for winner portfolios over 36 months (t = 2.20, N = NYSE 1926-1982, p < 0.05).
- Relevance to This Agent: The agent buys assets whose price is below fundamental (analogous to past losers) and sells those above (past winners), directly exploiting the mean-reversion anomaly.
- Calibration Source: `beta` in [0.1, 0.5] derived from De Bondt & Thaler (1985): reversal magnitude of ~25% over 36 months implies contrarian position scaling of 0.1-0.5 per unit mispricing for monthly rebalancing (Section IV, p. 800).
- Falsification Conditions: If this agent buys when P > fundamental (or sells when P < fundamental), the contrarian mechanism is falsified.
- Alternative Theories: Momentum persistence (Jegadeesh & Titman 1993), rational learning (Brav & Heaton 2002).

**Long-Term Reversals Persistence (Jegadeesh & Titman 2001)**:
- Theory / Study: Profitability of Momentum Strategies
- Citation: Jegadeesh, N., & Titman, S. (2001). Profitability of momentum strategies: An evaluation of alternative explanations. *Journal of Finance*, 56(2), 699-720. https://doi.org/10.1111/0022-1082.00342
- Core Insight: While momentum profits exist at 3-12 month horizons, these profits partially reverse over longer horizons (13-60 months), confirming that contrarian strategies are profitable for patient investors with longer holding periods.
- Mathematical Formulation: `bid_price = fundamental + N(0, noise_std)` — fundamental-anchored pricing with execution noise.
- Empirical Evidence: Jegadeesh & Titman (2001, Table III) show that momentum portfolio returns reverse by approximately 50% over months 13-60 post-formation (t-stat = -2.41, N = NYSE/AMEX/NASDAQ 1965-1998).
- Relevance to This Agent: The noise component models the execution uncertainty that real contrarian investors face — they know approximate fundamental value but cannot time entries perfectly.
- Calibration Source: `noise_std` in [0.1, 5.0] calibrated from Jegadeesh & Titman (2001): tracking error of contrarian portfolios relative to fundamental benchmarks ranges from 0.1-5.0 price units depending on volatility regime (Table IV, p. 712).
- Falsification Conditions: If this agent's bid_price deviates from fundamental by more than 4 * noise_std in expectation, the fundamental-anchoring mechanism is falsified.
- Alternative Theories: Fama-French three-factor model (1993), behavioural underreaction (Hong & Stein 1999).

## Design Purpose and Activation Triggers

Purpose: Execute mean-reversion trading that buys undervalued assets and sells overvalued assets relative to fundamental value, stabilising price toward equilibrium.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available
- Fundamental value parameter configured

Missing-Signal Policy: If current price is NaN, the agent abstains (quantity = 0). Fundamental value is a parameter and always available.

Activation Triggers:
- P < fundamental (undervalued): Buy — positive quantity, bid near fundamental
- P > fundamental (overvalued): Sell — negative quantity, bid near fundamental
- P = fundamental (fair value): Hold — quantity = 0
- Default: Hold

Deactivation Conditions:
- Cash depleted to zero: Agent cannot buy (can still sell if holding position)
- Price equals fundamental: No trading motivation

Behavioral Adaptation by Condition:
| Condition                          | Behavioral change                               | Mechanism                                          |
|------------------------------------|--------------------------------------------------|---------------------------------------------------|
| Large mispricing (|F-P|/P > 0.10) | Larger position sizes, stronger mean reversion   | Quantity proportional to mispricing magnitude      |
| Small mispricing (|F-P|/P < 0.02) | Near-zero positions, minimal activity            | Quantity approaches zero as mispricing vanishes    |
| High noise environment             | More dispersed bid prices around fundamental     | noise_std parameter amplifies execution variation  |

Environmental Dependencies: Requires a per-round price broadcast from the market coordinator. Fundamental value is an intrinsic parameter. No peer-action summaries, order-book data, or momentum signals are required.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                     | Type / Shape | Required? | Notes                                              |
|----------------------|----------------------------|--------------|-----------|----------------------------------------------------|
| `price`              | Market coordinator payload | `float`      | yes       | Current asset price; maps to Decision Info Set     |
| `fundamental`        | Config parameter           | `float`      | yes       | Known equilibrium value (§3.7 parameter)           |
| `cash`               | Agent persisted state      | `float`      | yes       | Available cash balance; from state init            |
| `position`           | Agent persisted state      | `int`        | yes       | Current share holding; from state init             |
| `round`              | Scheduler / round header   | `int`        | yes       | Current simulation round number                    |
| `retrieved_knowledge`| Retrieval store (RAG only) | `list[str]`  | RAG only  | Historical mean-reversion episodes; fallback: "(No relevant knowledge retrieved this round.)" |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum              | Unit   | Required? | Meaning                                      |
|-------------|--------|---------------------------------|--------|-----------|----------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`       | —      | yes       | Direction of trade                           |
| `bid_price` | float  | > 0                             | price  | yes       | Limit price for the order                    |
| `quantity`  | int    | [-50, +50]                      | shares | yes       | Signed order size (+buy, -sell)              |
| `reasoning` | string | 1-3 sentences                   | —      | yes       | Mispricing rationale and order explanation    |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clipped to [-50, +50]; positive = buy, negative = sell.
- `bid_price` MUST be > 0; computed as fundamental + N(0, noise_std).
- `action` MUST be "buy" when quantity > 0, "sell" when quantity < 0, "hold" when quantity = 0.
- The agent is stochastic-given-seed: the Gaussian noise in bid_price varies across runs unless seeded.
- Sign convention: positive quantity = buy order, negative quantity = sell order.
- Determinism markers: if seeded, the implementation MUST log the seed per round.

##### Serialization Format

```
<analysis>Mispricing = (F - P) / P = {mispricing:.4f}; fundamental = {fundamental}; bid = F + noise = {bid_price:.2f}; qty = beta * mispricing * cash / bid = {quantity}. Action: {action}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <int>, "reasoning": "<1-3 sentences>"}</decision>
```

Retrieval-augmented variants MUST inject the fallback sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth for the following six activities.** Do NOT rely on prose elsewhere; when this section and any other section disagree, this section wins.

1. **Signal wiring** — `price` MUST be read from the market coordinator broadcast; `fundamental` from config; `cash` and `position` from agent state.
2. **Decision emission** — the code path MUST populate all four required fields and MUST clip quantity to [-50, +50].
3. **Prompt drafting (model-driven variants)** — MUST spell out the tag pattern and JSON schema with a verbatim example showing `</decision>`.
4. **Parser tests** — MUST verify tag presence, parse JSON, assert all four fields present, quantity in [-50, +50], bid_price > 0.
5. **Variant parity** — Rule, LLM, RuleLLM, and Rag variants MUST all produce the same four-field output object.
6. **Contract-versus-prose conflict** — this contract wins on any disagreement with mechanism or action-space prose.

#### Decision Information Set

| Signal       | Type       | Memory Window | Rationale                                               |
|--------------|------------|---------------|---------------------------------------------------------|
| `price`      | Continuous | Current       | Needed to compute mispricing relative to fundamental    |
| `fundamental`| Continuous | Static        | Anchor value for mean-reversion trades                  |
| `cash`       | Continuous | Current       | Determines order size capacity                          |
| `position`   | Discrete   | Current       | Tracks holdings for sell-side constraint                |

Does NOT use: price history (no momentum signal), order-book depth, peer positions, volatility estimates, volume data, return series.

#### Core Behavioral Mechanism

1. **Read market price.** Read: `price` from market broadcast, `fundamental` from config. Write: nothing. (Implementation convenience — input acquisition.)

2. **Compute mispricing.** Read: `fundamental`, `price`. Compute: `mispricing = (fundamental - price) / price`. Write: nothing (intermediate). (Traces to De Bondt & Thaler 1985 — mispricing as contrarian signal.)

3. **Compute bid price with noise.** Read: `fundamental`, `noise_std`. Compute: `bid_price = fundamental + N(0, noise_std)`. Clamp bid_price to > 0.01. Write: nothing (intermediate). (Traces to Jegadeesh & Titman 2001 — execution uncertainty around fundamental.)

4. **Compute raw quantity.** Read: `beta`, `mispricing`, `cash`, `bid_price`. Compute: `raw_qty = beta * mispricing * cash / bid_price`. Write: nothing (intermediate). (Traces to De Bondt & Thaler 1985 — position proportional to mispricing.)

5. **Clip quantity.** Read: `raw_qty`. Compute: `quantity = clip(round(raw_qty), -50, +50)`. Write: nothing (intermediate). (Implementation convenience — self-imposed cap.)

6. **Determine action.** Read: `quantity`. Compute: if quantity > 0: action = "buy"; elif quantity < 0: action = "sell"; else: action = "hold". Write: nothing. (Implementation convenience.)

7. **Emit decision object.** Read: all computed fields. Write: emit the four-field decision object per I/O Contract serialization format. (Implementation convenience — output assembly.)

#### Action Space

| Aspect                | Specification                                                                                    |
|-----------------------|--------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                            |
| Action parameter rule | `bid_price = fundamental + N(0, noise_std)`; anchored to fundamental, not market price           |
| Sizing rule           | `quantity = clip(round(beta * (fundamental - price) / price * cash / bid_price), -50, +50)`      |
| Action lifetime       | One round; re-evaluated each tick                                                                |
| Revision policy       | Implicitly revised every round; no carry-over from previous decisions                            |
| State constraint      | Position cap: quantity clipped to [-50, +50] per round                                           |
| Resource cap          | Cannot buy more than cash permits; sell limited by position (enforced by environment)            |
| Exit rule             | None — agent participates every round regardless of cumulative history                           |

#### Mathematical Model

**Decision output:** The agent computes `bid_price` (float > 0) and `quantity` (int in [-50, +50]) each round, determining a contrarian mean-reversion trade.

**Decision logic formalization:**

```
Given: price = P, fundamental = F, cash, noise_std, beta

Step 1: Mispricing
  mispricing = (F - P) / P

Step 2: Bid price (stochastic)
  bid_price = max(0.01, F + N(0, noise_std))

Step 3: Quantity
  raw_qty = beta * mispricing * cash / bid_price

Step 4: Clipping
  quantity = clip(round(raw_qty), -50, +50)

Step 5: Action classification
  if quantity > 0: action = "buy"
  elif quantity < 0: action = "sell"
  else: action = "hold"

Step 6: Edge case — price = fundamental
  if P = F: mispricing = 0, quantity = 0, action = "hold"
```

**State variables:**

| Variable   | Type    | Initial Value | Update Phase                         |
|------------|---------|---------------|--------------------------------------|
| `cash`     | `float` | 10000         | Post-execution (updated by environment) |
| `position` | `int`   | 0             | Post-execution (updated by environment) |

**State evolution:** `cash` and `position` are updated by the environment after order execution. The agent itself maintains no rolling state — each decision is computed fresh from current price and parameters.

**Determinism contract:** The decision is stochastic-given-seed due to the Gaussian noise term N(0, noise_std) in bid_price computation. Given an identical seed, the output is deterministic.

**Parameter symbol table:**

| Symbol       | Meaning                              | Default Value | Source                       |
|--------------|--------------------------------------|---------------|------------------------------|
| `fundamental`| Known equilibrium/fair value         | 100.0         | Scenario configuration       |
| `beta`       | Position sizing sensitivity          | 0.5           | De Bondt & Thaler (1985)     |
| `noise_std`  | Bid price execution noise (std dev)  | 0.5           | Jegadeesh & Titman (2001)    |
| `P`          | Current market price                 | —             | Environment signal           |
| `F`          | Alias for fundamental                | —             | Parameter                    |

#### Behavioral Properties

- Time horizon: Medium — trades based on deviation from long-term fundamental value rather than short-term returns. Rationale: contrarian profits in De Bondt & Thaler (1985) manifest over 3-5 year horizons.
- Risk tolerance: Medium — takes positions against the crowd but sizes conservatively with beta <= 0.5. Rationale: contrarian strategies face short-term tracking risk before mean reversion materialises.
- Information asymmetry: Full — the agent knows the fundamental value; real contrarian investors approximate this through valuation models.
- Psychological profile: Embodies rational value assessment with bounded execution precision; resists herding bias and anchors to fundamentals rather than price trends.

## Parameters

| Parameter          | Type    | Default | Valid Range      | Sensitivity | Description                                        | Impact                                        | Source                       |
|--------------------|---------|---------|------------------|-------------|----------------------------------------------------|-----------------------------------------------|------------------------------|
| `fundamental`      | `float` | 100.0  | [1.0, 10000.0]   | high        | Known equilibrium value the agent targets          | Higher -> agent bids higher on average         | Scenario configuration       |
| `beta`             | `float` | 0.5    | [0.1, 0.5]       | high        | Fraction of cash committed per unit mispricing     | Higher -> larger contrarian order sizes         | De Bondt & Thaler (1985)     |
| `noise_std`        | `float` | 0.5    | [0.1, 5.0]       | medium      | Standard deviation of Gaussian noise on bid price  | Higher -> more dispersed bids around fundamental | Jegadeesh & Titman (2001)  |
| `initial_cash`     | `float` | 10000  | [1000, 1000000]   | low         | Starting cash balance                              | Higher -> larger absolute order sizes          | Standardised                 |
| `initial_position` | `int`   | 0      | [0, 1000]         | low         | Starting share position                            | Higher -> more sell capacity                   | Standardised                 |

## Worked Numerical Examples

### Case 1 — Price below fundamental, buy order

System state: `price` = 90.0, `fundamental` = 100.0, `cash` = 10000, `beta` = 0.5, `noise_std` = 0.5 (noise draw = +0.3).

Calculation:
- `mispricing` = (100.0 - 90.0) / 90.0 = 0.1111
- `bid_price` = 100.0 + 0.3 = 100.3
- `raw_qty` = 0.5 * 0.1111 * 10000 / 100.3 = 555.5 / 100.3 = 5.54
- `quantity` = clip(round(5.54), -50, +50) = 6

Decision: `action = "buy"`, `bid_price = 100.3`, `quantity = 6`.

State update: `cash` and `position` updated by environment post-execution.

### Case 2 — Price above fundamental, sell order

System state: `price` = 110.0, `fundamental` = 100.0, `cash` = 10000, `beta` = 0.5, `noise_std` = 0.5 (noise draw = -0.2), `position` = 20.

Calculation:
- `mispricing` = (100.0 - 110.0) / 110.0 = -0.0909
- `bid_price` = 100.0 + (-0.2) = 99.8
- `raw_qty` = 0.5 * (-0.0909) * 10000 / 99.8 = -454.5 / 99.8 = -4.55
- `quantity` = clip(round(-4.55), -50, +50) = -5

Decision: `action = "sell"`, `bid_price = 99.8`, `quantity = -5`.

State update: `cash` and `position` updated by environment post-execution.

### Case 3 — Large mispricing, quantity approaches cap

System state: `price` = 50.0, `fundamental` = 100.0, `cash` = 10000, `beta` = 0.5, `noise_std` = 0.5 (noise draw = 0.0).

Calculation:
- `mispricing` = (100.0 - 50.0) / 50.0 = 1.0
- `bid_price` = 100.0 + 0.0 = 100.0
- `raw_qty` = 0.5 * 1.0 * 10000 / 100.0 = 5000 / 100.0 = 50.0
- `quantity` = clip(round(50.0), -50, +50) = 50

Decision: `action = "buy"`, `bid_price = 100.0`, `quantity = 50`.

State update: `cash` and `position` updated by environment post-execution.

### Edge Case — Price equals fundamental (no mispricing)

System state: `price` = 100.0, `fundamental` = 100.0, `cash` = 10000, `beta` = 0.5.

Calculation:
- `mispricing` = (100.0 - 100.0) / 100.0 = 0.0
- `raw_qty` = 0.5 * 0.0 * 10000 / bid_price = 0.0
- `quantity` = 0

Decision: `action = "hold"`, `bid_price = 100.0 + noise`, `quantity = 0`.

State update: No state change.

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `beta` <- De Bondt & Thaler (1985), Section IV: reversal magnitude of 24.6% over 36 months implies contrarian commitment of 0.1-0.5 per unit mispricing.
- `noise_std` <- Jegadeesh & Titman (2001), Table IV: tracking error of 0.1-5.0 price units for contrarian portfolios.
- `fundamental` <- Scenario-specific; represents intrinsic value anchor.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given P < fundamental, agent MUST produce quantity > 0 (buy).
- Given P > fundamental, agent MUST produce quantity < 0 (sell).
- Given P = fundamental, agent MUST produce quantity = 0 (hold).
- Quantity magnitude MUST increase monotonically with |mispricing| (holding cash constant).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys (quantity > 0) when P > fundamental THEN the contrarian mechanism is broken.
- IF the agent's quantity exceeds [-50, +50] THEN the clipping constraint is violated.
- IF the agent's bid_price is consistently far from fundamental (> 4 * noise_std) THEN noise generation is broken.
- IF the agent exhibits momentum-following behaviour THEN the mean-reversion design is violated.

#### Ablation Hooks

| Ablation name       | Setting            | Hypothesis tested                              | Expected direction                 | Metric                               |
|---------------------|--------------------|------------------------------------------------|------------------------------------|--------------------------------------|
| `no_noise`          | `noise_std = 0`    | Noise creates execution uncertainty            | Perfect convergence to fundamental | Bid price variance around fundamental|
| `high_beta`         | `beta = 0.5`       | Stronger contrarian force speeds convergence   | Faster mean reversion              | Rounds to reach fundamental +/- 1%  |
| `low_beta`          | `beta = 0.1`       | Weaker contrarian allows more drift            | Slower mean reversion              | Rounds to reach fundamental +/- 1%  |

## Academic References

| # | Citation                                                                                                                                                                           | Notes                                   |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| 1 | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x               | Primary theory: overreaction reversal   |
| 2 | Jegadeesh, N., & Titman, S. (2001). Profitability of momentum strategies. *Journal of Finance*, 56(2), 699-720. https://doi.org/10.1111/0022-1082.00342                          | Long-term reversal evidence             |
| 3 | Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3-56. https://doi.org/10.1016/0304-405X(93)90023-5 | Value factor as rational explanation |
| 4 | Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum, and overreaction. *Journal of Finance*, 54(6), 2143-2184. https://doi.org/10.1111/0022-1082.00184  | Alternative: gradual information diffusion |

## Design Provenance

| Field       | Content                    |
|-------------|----------------------------|
| Author      | polish-simulation-pipeline |
| Created     | 2026-07-14                 |
| Version     | 1.0.0                      |
| Status      | canonical                  |
