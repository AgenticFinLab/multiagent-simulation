# Trend Follower

## Summary

| Field                 | Content                                                                                                        |
|-----------------------|----------------------------------------------------------------------------------------------------------------|
| Archetype             | Trend Follower (CTA/Managed-Futures)                                                                           |
| Theory Family         | Time-Series Momentum — Chartist Trend Extrapolation                                                            |
| Behavioral Tendency   | **Diverging** — amplifies existing price movements by trading procyclically in the direction of detected trend  |
| Time Horizon          | Short-Medium (lookback window of 2–5 rounds)                                                                   |
| Risk Tolerance        | Medium-High (large position sizes scaled by volatility; willing to chase trends aggressively)                  |
| Information Asymmetry | Partial (observes price history and volatility only; no access to fundamental value or order book)             |
| Determinism           | Deterministic (given identical price history, volatility, and parameters, always produces the same order)       |

## Definition and Goals

The trend follower models systematic trend-following strategies commonly deployed by CTAs and managed-futures funds that extrapolate recent price trajectories into the future and trade in the direction of the detected trend. In the real world, these correspond to managed-futures programmes, momentum-driven commodity trading advisors, and systematic macro strategies — any participant whose buy/sell decision derives from detecting and riding price trends with volatility-adjusted sizing.

The agent's decision goal is to detect a trend signal from the deviation of the current price relative to its moving average over a lookback window, then trade in the direction of that deviation with position size scaled by signal strength and a volatility multiplier. The quantity is computed as `direction × base_position_size × strength × vol_multiplier`, where strength is normalised to [0, 1] and vol_multiplier is clamped to [0.5, 2.0]. The agent activates only when the absolute trend deviation exceeds a configurable `trend_threshold`.

The agent's behavioural role inside the simulation is to amplify existing price trends and contribute to momentum clustering and volatility persistence: during a sustained move, it adds procyclical demand that extends the trend; during high-volatility regimes, the volatility multiplier further increases position sizes, creating endogenous feedback that extends volatility clusters. Non-goals: (1) the trend follower MUST NOT trade on fundamental value or mean-revert — it is purely trend-following; (2) it MUST NOT provide structural liquidity — `provides_liquidity` is always `False`; (3) it MUST NOT scale down in high-volatility regimes — the procyclical vol multiplier scales UP with rising volatility.

## Theoretical Foundation

**Time-Series Momentum (Moskowitz, Ooi & Pedersen 2012)**:
- Theory / Study: Time Series Momentum
- Citation: Moskowitz, T. J., Ooi, Y. H. & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228–250. https://doi.org/10.1016/j.jfineco.2011.11.003
- Core Insight: A security's own past return over 1–12 months is a positive predictor of its future return. CTA practitioners exploit this autocorrelation by going long after price rises and short after price falls, typically scaling exposure by inverse volatility to normalise risk. The resulting positive-feedback trading amplifies trends and creates momentum persistence.
- Mathematical Formulation: `trend = (price - MA_lookback) / MA_lookback; strength = min(|trend| / 0.05, 1.0); vol_multiplier = 1.0 + volatility_sensitivity × (vol_ratio - 1.0), clamped [0.5, 2.0]; quantity = sign(trend) × base_position_size × strength × vol_multiplier`.
- Empirical Evidence: Moskowitz et al. (2012) document significant time-series momentum profits across 58 liquid instruments (equities, bonds, commodities, currencies) over 1965–2009, with average annualised return of 14.0% after controlling for exposure (Table 2, p. 237). The Sharpe ratio of a diversified TSMOM portfolio is 1.0, driven by trend persistence at horizons of 1–12 months.
- Relevance to This Agent: The agent implements the core time-series momentum signal with volatility-proportional sizing, consistent with CTA practice. Its procyclical vol multiplier matches the empirical finding that CTA strategies increase exposure during trending high-vol periods.
- Calibration Source: `lookback_window` in [2, 5] from the shortest horizon in Moskowitz et al. Table 2 (1-month, mapped to simulation rounds); `trend_threshold` = 0.005 from de minimis return threshold below which trading costs dominate signal; `volatility_sensitivity` = 0.8 from practitioner vol-targeting conventions.
- Falsification Conditions: If this agent's net order flow over any 10-round window is negatively correlated (ρ < -0.3) with the signed trend over the same window, the trend-following mechanism is falsified. If the agent's position size decreases when volatility increases (holding trend constant), the procyclical vol-amplification hypothesis is falsified.
- Alternative Theories: Cross-sectional momentum (Jegadeesh & Titman 1993), behavioural under-reaction (Barberis, Shleifer & Vishny 1998), rational attention-driven momentum (Hong & Stein 1999).

## Design Purpose and Activation Triggers

Purpose: Inject positive-feedback trading that generates momentum persistence, trend amplification, and volatility clustering through procyclical sizing.

Call Frequency: Every tick (every simulation round), once lookback window is filled.

Prerequisite Signals (must be available for the agent to evaluate):
- Price history of length >= lookback_window available (for computing moving average)
- Current volatility estimate available (for vol multiplier)
- Current market price available

Missing-Signal Policy: If price history has fewer observations than lookback_window, the agent holds (quantity = 0). If volatility estimate is unavailable, the agent uses `baseline_volatility` as fallback (vol_multiplier = 1.0). If current price is unavailable (NaN), the agent abstains entirely.

Activation Triggers:
- Trend detected (|trend| > trend_threshold): Trade in trend direction with vol-scaled quantity
- No trend (|trend| <= trend_threshold): Hold (quantity = 0)

Deactivation Conditions:
- Insufficient price history (first lookback_window - 1 ticks): Agent holds
- Cash exhaustion: Cannot buy further (constrained by _apply_constraints)
- Market closure / simulation end: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                                  | Mechanism                                         |
|------------------------------|---------------------------------------------------------------------|--------------------------------------------------|
| High volatility regime       | Larger position sizes (vol_multiplier > 1.0)                        | Procyclical: `1.0 + sensitivity × (vol_ratio-1)` |
| Low volatility regime        | Smaller position sizes (vol_multiplier < 1.0, floor 0.5)           | Vol_multiplier shrinks toward 0.5                |
| Strong sustained trend       | Maximum-strength trades every round                                  | strength saturates at 1.0 when |trend|/0.05 >= 1 |
| Trend reversal               | Reverses direction within 1 round of signal flip                    | Mechanistic: follows sign(trend) without delay    |

Environmental Dependencies: Requires per-round market data broadcast containing `price` field and a volatility estimate (computed from rolling std of returns or provided by coordinator). Maintains internal `price_history` buffer. No peer-action summaries, fundamental value, or order-book data needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                    | Source                     | Type / Shape  | Required? | Notes                                             |
|--------------------------|----------------------------|---------------|-----------|---------------------------------------------------|
| `price`                  | Market coordinator payload | `float`       | yes       | Current asset price                               |
| `price_history`          | Agent persisted state      | `list[float]` | yes       | Full price history for computing moving average   |
| `volatility`             | Market coordinator / self  | `float`       | yes       | Current rolling volatility estimate               |
| `round`                  | Scheduler / round header   | `int`         | yes       | Current simulation round number                   |
| `lookback_window`        | Config extras              | `int`         | yes       | Moving average window length (§Parameters)        |
| `trend_threshold`        | Config extras              | `float`       | yes       | Minimum |trend| to activate (§Parameters)        |
| `base_position_size`     | Config extras              | `float`       | yes       | Base order magnitude (§Parameters)                |
| `volatility_sensitivity` | Config extras              | `float`       | yes       | Vol-scaling coefficient (§Parameters)             |
| `baseline_volatility`    | Config extras              | `float`       | yes       | Reference vol level (§Parameters)                 |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                                 |
|-------------|--------|---------------------------|--------|-----------|------------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction derived from sign(trend)       |
| `bid_price` | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold    |
| `quantity`  | float  | [-60, 60]                 | shares | yes       | Signed order size (+ buy, - sell)       |
| `reasoning` | string | 1–2 sentences             | —      | yes       | Trend %, vol_multiplier, and quantity    |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` is signed: positive = buy, negative = sell, zero = hold.
- `bid_price` MUST equal the current market price when trading; 0.0 when holding.
- `provides_liquidity` in the outbound message envelope is always `False`.
- The agent is deterministic given the same price history, volatility, and parameters.
- strength is normalised to [0, 1]; vol_multiplier is clamped to [0.5, 2.0].

##### Serialization Format

```
<analysis>Trend = {trend:.4f} (MA deviation over {lookback_window} ticks); strength = {strength:.2f}; vol_multiplier = {vol_multiplier:.2f}; quantity = {quantity:.2f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <float>, "reasoning": "Trend-follower: {trend:.2%} deviation, vol_mult={vol_multiplier:.2f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim into the `<analysis>` block when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the MA-deviation formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the LLM may adjust quantity by ±20% but MUST preserve the sign dictated by the trend direction. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. The `provides_liquidity` field in the outbound message envelope is always `False`.

#### Decision Information Set

| Signal          | Type       | Memory Window         | Rationale                                           |
|-----------------|------------|-----------------------|-----------------------------------------------------|
| `price`         | Continuous | Current tick          | Required for computing MA deviation and bid_price   |
| `price_history` | Continuous | Last lookback_window  | Used to compute moving average for trend signal     |
| `volatility`    | Continuous | Rolling estimate      | Scales position size procyclically                  |

Does NOT use: fundamental value, order book depth, peer positions, net demand, liquidity levels — the agent reacts only to the trend signal and volatility.

#### Core Behavioral Mechanism

Step 1 — Read price history and compute moving average:
  Read: `price_history`, `lookback_window`
  `MA = mean(price_history[-lookback_window:])`

Step 2 — Compute trend deviation:
  Read: `price` (current)
  `trend = (price - MA) / MA`

Step 3 — Evaluate activation threshold:
  Read: `trend_threshold`
  IF `|trend| <= trend_threshold`: set quantity = 0, bid_price = 0.0, action = "hold" → RETURN

Step 4 — Determine direction:
  `direction = +1 if trend > 0 else -1`

Step 5 — Compute normalised strength:
  `strength = min(|trend| / 0.05, 1.0)` — saturates at 1.0 for deviations ≥ 5%

Step 6 — Compute volatility multiplier:
  Read: `volatility`, `baseline_volatility`, `volatility_sensitivity`
  `vol_ratio = volatility / baseline_volatility`
  `vol_multiplier = 1.0 + volatility_sensitivity × (vol_ratio - 1.0)`
  `vol_multiplier = clamp(vol_multiplier, 0.5, 2.0)`

Step 7 — Compute raw quantity:
  Read: `base_position_size`
  `quantity = direction × base_position_size × strength × vol_multiplier`

Step 8 — Clamp quantity:
  `quantity = clamp(quantity, -60, 60)`

Step 9 — Apply resource constraints:
  Write: `quantity = _apply_constraints(price, quantity)`

Step 10 — Determine action and execute:
  IF quantity > 0: action = "buy"; Write: cash -= quantity × price; position += quantity
  ELIF quantity < 0: action = "sell"; Write: cash += |quantity| × price; position += quantity
  ELSE: action = "hold"

Each step traces to Time-Series Momentum (Moskowitz et al. 2012): Steps 1–5 implement the trend-detection component; Steps 6–7 implement the volatility-proportional sizing that CTA practitioners use to normalise risk across varying vol regimes.

#### Action Space

| Aspect                | Specification                                                                              |
|-----------------------|--------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                      |
| Action parameter rule | `bid_price` = current market price (no limit orders; agent is a price-taker)               |
| Sizing rule           | `quantity = direction × base_position_size × strength × vol_multiplier`, clamped [-60, 60] |
| Action lifetime       | Immediate execution; no persistent resting orders                                          |
| Revision policy       | No revision — each round's order is independent; previous orders are not amended           |
| State constraint      | No self-imposed cumulative position limit at agent level                                   |
| Resource cap          | Cash constraint applied via `_apply_constraints` (cannot buy more than cash allows)        |
| Exit rule             | None — agent trades every round as long as |trend| > threshold and resources permit        |

#### Mathematical Model

**Decision output:** Signed quantity (float in [-60, 60]) representing the directional order to submit this round.

**Decision logic formalization:**

```
Step 1 — Compute moving average:
  IF len(price_history) >= lookback_window:
    MA = mean(price_history[-lookback_window:])
  ELSE:
    → HOLD (insufficient history)

Step 2 — Compute trend:
  trend = (price - MA) / MA

Step 3 — Activation gate:
  IF abs(trend) <= trend_threshold:
    quantity = 0.0
    bid_price = 0.0
    action = "hold"
    → RETURN

Step 4 — Direction and strength:
  direction = +1 if trend > 0 else -1
  strength = min(abs(trend) / 0.05, 1.0)

Step 5 — Volatility multiplier:
  vol_ratio = volatility / baseline_volatility
  vol_multiplier = 1.0 + volatility_sensitivity * (vol_ratio - 1.0)
  vol_multiplier = clamp(vol_multiplier, 0.5, 2.0)

Step 6 — Quantity:
  raw_quantity = direction * base_position_size * strength * vol_multiplier
  quantity = clamp(raw_quantity, -60, 60)
  bid_price = price

Step 7 — Apply constraints:
  quantity = _apply_constraints(bid_price, quantity)

Step 8 — Execute:
  IF quantity > 0: cash -= quantity * bid_price; position += quantity
  ELIF quantity < 0: cash += abs(quantity) * bid_price; position += quantity
```

**State variables:**
- `price_history`: Append-only list of observed prices, updated each round during `perceive`.
- `position`: Running tally of net shares held (updated by `_execute_trade` post-decision).
- `cash`: Running cash balance (updated by `_execute_trade` post-decision).

**State evolution:**
- `price_history`: Updated pre-decide (during `perceive`, appends new price).
- `position` and `cash`: Updated post-decide (during `_execute_trade`, after quantity finalised).

**Determinism contract:** Fully deterministic given identical price history, volatility estimate, and parameter values.

**Parameter symbol table:**

| Symbol                  | Meaning                                     | Default Value | Source                       |
|-------------------------|---------------------------------------------|---------------|------------------------------|
| `lookback_window`       | Moving average window length                | 3             | Moskowitz et al. (2012)      |
| `trend_threshold`       | Minimum |trend| to activate                 | 0.005         | Moskowitz et al. (2012)      |
| `base_position_size`    | Base order magnitude                        | 30.0          | simulation-bases.md §4.2.6   |
| `volatility_sensitivity`| Vol-scaling coefficient                     | 0.8           | Moskowitz et al. (2012)      |
| `baseline_volatility`   | Reference volatility level                  | 1.0           | Calibration reference        |

#### Behavioral Properties

- **Time horizon:** Short-Medium (lookback window of 2–5 rounds; reacts within 1 round of signal change)
- **Risk tolerance:** Medium-High (large position sizes amplified by vol multiplier up to 2.0×; willing to chase trends through volatile regimes)
- **Information asymmetry:** Partial (observes only price history and volatility; no fundamental value, peer positions, or order book access)
- **Psychological profile:** Chartist / trend extrapolator — believes recent price trajectories will persist; exhibits procyclical behaviour that amplifies trends and volatility clustering; no fear of mean-reversion or overextension

## Parameters

| Parameter              | Type  | Default | Valid Range     | Sensitivity | Description                                         | Impact                                           | Source                       |
|------------------------|-------|---------|-----------------|-------------|-----------------------------------------------------|--------------------------------------------------|------------------------------|
| `lookback_window`      | int   | 3       | [2, 5]          | Medium      | Moving average window for trend signal              | Shorter → noisier/faster; longer → smoother/delayed | Moskowitz et al. (2012)      |
| `trend_threshold`      | float | 0.005   | [0.0, 0.02]     | Medium      | Minimum |trend deviation| to trigger a trade         | Higher → fewer trades, less amplification         | Moskowitz et al. (2012)      |
| `base_position_size`   | float | 30.0    | [10.0, 50.0]    | High        | Base order magnitude before strength/vol scaling    | Linear multiplier on all order sizes              | simulation-bases.md §4.2.6   |
| `volatility_sensitivity` | float | 0.8   | [0.0, 2.0]      | High        | Coefficient for vol-proportional sizing             | Higher → more procyclical amplification           | Moskowitz et al. (2012)      |
| `baseline_volatility`  | float | 1.0     | [0.5, 3.0]      | Low         | Reference volatility level for vol_ratio            | Shifts the vol_multiplier baseline                | Calibration reference        |
| `initial_cash`         | float | 10000.0 | [5000, 50000]   | Low         | Starting cash endowment                             | Determines how long agent can trade               | Normalization                |
| `initial_position`     | int   | 0       | [0, 50]         | Low         | Starting inventory                                  | Non-zero start creates initial directional bias   | Normalization                |

## Worked Numerical Examples

### Case 1 — Uptrend detected (moderate)

System state: `price_history[-3:]` = [100.0, 101.0, 102.0], current `price` = 103.0, `lookback_window` = 3, `trend_threshold` = 0.005, `base_position_size` = 30.0, `volatility_sensitivity` = 0.8, `baseline_volatility` = 1.0, `volatility` = 1.0

Calculation:
- `MA` = mean([100.0, 101.0, 102.0]) = 101.0
- `trend` = (103.0 - 101.0) / 101.0 = 0.0198
- Threshold check: |0.0198| > 0.005? YES → active
- `direction` = +1 (trend > 0)
- `strength` = min(0.0198 / 0.05, 1.0) = min(0.396, 1.0) = 0.396
- `vol_ratio` = 1.0 / 1.0 = 1.0
- `vol_multiplier` = 1.0 + 0.8 × (1.0 - 1.0) = 1.0, clamp [0.5, 2.0] → 1.0
- `quantity` = +1 × 30.0 × 0.396 × 1.0 = 11.88

Decision: buy 11.88 shares at bid_price = 103.0
State update: `cash`: 10000.0 → 10000.0 - 11.88 × 103.0 = 8776.4; `position`: 0 → 11.88

### Case 2 — Downtrend with high volatility (procyclical amplification)

System state: `price_history[-3:]` = [100.0, 98.0, 95.0], current `price` = 92.0, `lookback_window` = 3, `trend_threshold` = 0.005, `base_position_size` = 30.0, `volatility_sensitivity` = 0.8, `baseline_volatility` = 1.0, `volatility` = 2.0

Calculation:
- `MA` = mean([100.0, 98.0, 95.0]) = 97.67
- `trend` = (92.0 - 97.67) / 97.67 = -0.0580
- Threshold check: |-0.0580| > 0.005? YES → active
- `direction` = -1 (trend < 0)
- `strength` = min(0.0580 / 0.05, 1.0) = min(1.16, 1.0) = 1.0 (saturated)
- `vol_ratio` = 2.0 / 1.0 = 2.0
- `vol_multiplier` = 1.0 + 0.8 × (2.0 - 1.0) = 1.8, clamp [0.5, 2.0] → 1.8
- `quantity` = -1 × 30.0 × 1.0 × 1.8 = -54.0

Decision: sell 54.0 shares at bid_price = 92.0
State update: `cash` += 54.0 × 92.0 = +4968.0; `position`: 0 → -54.0

### Case 3 — No trend (within threshold)

System state: `price_history[-3:]` = [100.0, 100.1, 99.9], current `price` = 100.05, `lookback_window` = 3, `trend_threshold` = 0.005

Calculation:
- `MA` = mean([100.0, 100.1, 99.9]) = 100.0
- `trend` = (100.05 - 100.0) / 100.0 = 0.0005
- Threshold check: |0.0005| > 0.005? NO → hold

Decision: hold
State update: No change

### Edge Case — Insufficient history

System state: tick = 1, `lookback_window` = 3. Only 1 price available, need at least 3 for MA.

Decision: hold (insufficient history)
State update: No change

### Edge Case — Vol multiplier clamped at maximum

System state: `price_history[-3:]` = [100, 97, 94], current `price` = 90, `volatility` = 3.5, `baseline_volatility` = 1.0, `volatility_sensitivity` = 0.8

Calculation:
- `MA` = mean([100, 97, 94]) = 97.0
- `trend` = (90 - 97) / 97 = -0.0722; strength = 1.0 (saturated)
- `vol_ratio` = 3.5 / 1.0 = 3.5
- `vol_multiplier` = 1.0 + 0.8 × (3.5 - 1.0) = 3.0, clamp [0.5, 2.0] → **2.0** (clamped)
- `quantity` = -1 × 30.0 × 1.0 × 2.0 = -60.0

Decision: sell 60.0 shares (at maximum capacity)

## Behavioral Verification and Calibration

**Verification criteria:**
1. Over any 10-round window where the market exhibits a sustained trend (cumulative return > 3%), the agent's net order flow MUST have the same sign as the trend in at least 80% of active rounds.
2. The agent MUST emit |quantity| that increases (weakly) when volatility increases, holding trend constant — verifying procyclical vol-amplification.
3. The agent MUST never emit a trade when |trend| <= trend_threshold (dead-zone compliance).
4. Given identical price history and parameter sequences, the agent MUST produce byte-identical outputs (determinism test).
5. The agent's `provides_liquidity` flag MUST always be `False`.

**Calibration procedure:**
- Deploy 3 instances with `lookback_window` in {2, 3, 5}.
- Run 200-round simulation with injected trend regime (50 rounds up, 50 down, 100 flat).
- Verify: (a) procyclical order flow during trending phases; (b) near-zero activity during flat phase; (c) agent reverses within 1–2 rounds of trend flip.
- Sensitivity sweep: vary `volatility_sensitivity` in {0, 0.4, 0.8, 1.5} and confirm monotone relationship between vol_sensitivity and position-size variance.

**Ablation Hooks:**

| Ablation name      | Setting                    | Hypothesis tested                                       |
|--------------------|----------------------------|---------------------------------------------------------|
| `no_trend`         | population = 0             | Removing trend-followers reduces autocorrelation        |
| `no_vol_scaling`   | `volatility_sensitivity=0` | Without vol scaling, volatility clusters are shorter    |
| `short_lookback`   | `lookback_window=2`        | Shorter lookback amplifies noise and increases turnover |

## Academic References

- Moskowitz, T. J., Ooi, Y. H. & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228–250. https://doi.org/10.1016/j.jfineco.2011.11.003
- Jegadeesh, N. & Titman, S. (1993). Returns to buying winners and selling losers: implications for stock market efficiency. *The Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Barberis, N., Shleifer, A. & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307–343. https://doi.org/10.1016/S0304-405X(98)00027-0
- De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *The Journal of Finance*, 45(2), 379–395. https://doi.org/10.2307/2328662

## Design Provenance

| Field       | Content                                                       |
|-------------|---------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                    |
| Created     | 2026-07-14                                                    |
| Version     | 2.0.0                                                         |
| Status      | canonical                                                     |
| Icon        | ![](../agent_images/icons/finance-trend-follower.png)         |
