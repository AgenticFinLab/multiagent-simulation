# Algorithmic Trend-Following Trader

## Summary

| Field                 | Content                                                                                              |
|-----------------------|------------------------------------------------------------------------------------------------------|
| Archetype             | Algorithmic Trend-Following Trader                                                                   |
| Theory Family         | Behavioral Finance — Positive-Feedback Trading                                                       |
| Behavioral Tendency   | **Diverging** — amplifies existing price trends by trading in the direction of recent momentum        |
| Time Horizon          | Short-Medium (lookback window of 3–10 rounds)                                                        |
| Risk Tolerance        | Medium (position-size capped, but willing to follow momentum into volatile regimes)                  |
| Information Asymmetry | Partial (observes price history only, no access to fundamental value or order book depth)             |
| Determinism           | Deterministic (given identical price history and parameters, always produces the same order)          |

## Definition and Goals

The algorithmic trend-following trader models medium-speed systematic trading algorithms that detect short-term momentum in asset prices and trade in the direction of the detected trend. In the real world, these correspond to quantitative momentum strategies deployed by hedge funds, proprietary trading desks, and commodity trading advisors (CTAs) — any participant whose buy/sell decision is entirely derived from recent price trajectories without reference to fundamental value.

The agent's decision goal is to produce a signed order quantity proportional to the estimated price trend over a configurable lookback window. The quantity is computed as `trend × trend_sensitivity × base_position_size × trend_multiplier`, clamped to a maximum absolute value of 40 units. The agent does not optimise an explicit utility function; instead it mechanically follows the positive-feedback rule, buying into rising prices and selling into falling prices.

The agent's behavioural role inside the simulation is to bridge the ultra-fast high-frequency traders and the slower stop-loss or fundamental agents: it detects a move that HFTs initiate and reinforces it at medium timescale, sustaining selling (or buying) pressure long enough for cascading mechanisms to trigger. Non-goals: (1) the algorithmic trader MUST NOT provide liquidity — it is always a liquidity taker; (2) it MUST NOT incorporate fundamental value signals or mean-reversion logic — it is purely trend-following.

## Theoretical Foundation

**Positive-Feedback Trading (De Long et al. 1990)**:
- Theory / Study: Noise Trader Risk in Financial Markets
- Citation: De Long, J.B., Shleifer, A., Summers, L.H., & Waldmann, R.J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *The Journal of Finance*, 45(2), 379–395. https://doi.org/10.2307/2328662
- Core Insight: Positive-feedback traders buy after price rises and sell after price falls, creating self-reinforcing momentum that pushes prices away from fundamentals. Rational speculators may amplify rather than correct this behaviour because they anticipate the feedback traders' future demand.
- Mathematical Formulation: `quantity = trend_sensitivity × (P_t / P_{t-w} - 1) × base_position_size × trend_multiplier`, where `w` is the lookback window length.
- Empirical Evidence: De Long et al. (1990) show theoretically that positive-feedback demand destabilises prices; Jegadeesh & Titman (1993, DOI: 10.1111/j.1540-6261.1993.tb04702.x) document 3-12 month momentum profits of ~1% per month across US equities 1965-1989 (t-stat > 3.0), confirming that trend-following strategies find exploitable patterns.
- Relevance to This Agent: The agent directly operationalises the positive-feedback mechanism — it mechanically buys on positive trends and sells on negative trends, with magnitude proportional to the signal strength.
- Calibration Source: `trend_sensitivity` ∈ [0.5, 2.0] calibrated from De Long et al.'s numerical examples; `trend_window` ∈ [3, 10] rounds corresponds to intraday lookback of a few minutes to a few hours in the flash-crash literature (Kirilenko et al. 2017, Table 3).
- Falsification Conditions: If this agent's net position over any 10-round sliding window is uncorrelated with the signed trend over the same window (|ρ| < 0.3), the positive-feedback mechanism is falsified.
- Alternative Theories: Rational expectations momentum (Cespa & Vives 2012), information-based momentum (Hong & Stein 1999).

## Design Purpose and Activation Triggers

Purpose: Amplify existing price movements at medium timescale by following detected trends, bridging high-frequency initiators and slower cascade agents.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Price history of length >= lookback window available
- Current market price available

Missing-Signal Policy: If price history has fewer observations than the lookback window, the agent emits quantity = 0 (no trade). If current price is unavailable (NaN), the agent abstains entirely.

Activation Triggers:
- Positive trend detected (P_t / P_{t-w} - 1 > 0): Buy order proportional to trend magnitude
- Negative trend detected (P_t / P_{t-w} - 1 < 0): Sell order proportional to trend magnitude
- Trend ≈ 0 (below floating-point noise): Hold (quantity rounds to 0)

Deactivation Conditions:
- Position clamp reached (|quantity| hits 40): Agent is at maximum capacity, cannot amplify further
- Market closure / simulation end: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                  | Behavioral change                                           | Mechanism                          |
|----------------------------|-------------------------------------------------------------|------------------------------------|
| High volatility regime     | Larger absolute orders (trend magnitude increases)           | Proportional response to trend     |
| Low liquidity (wide spread)| Same algorithmic output; does not adapt to liquidity conditions | No liquidity-awareness built in  |
| Trend reversal             | Reverses order direction within one round of signal flip     | Mechanistic: follows signal        |

Environmental Dependencies: Requires a per-round price history vector (maintained by the market coordinator) and the current tick price. No peer-action summaries needed; no external data feeds beyond the market state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                | Source                      | Type / Shape   | Required? | Notes                                |
|----------------------|-----------------------------|----------------|-----------|--------------------------------------|
| `price`              | Market coordinator payload  | `float`        | yes       | Current asset price                  |
| `price_history`      | Agent persisted state       | `list[float]`  | yes       | Full price history up to current round |
| `round`              | Scheduler / round header    | `int`          | yes       | Current simulation round number      |
| `lookback`           | Config extras               | `int`          | yes       | Trend window length (§3.7 parameter) |
| `trend_sensitivity`  | Config extras               | `float`        | yes       | Scaling factor (§3.7 parameter)      |
| `base_position_size` | Config extras               | `float`        | yes       | Base size (§3.7 parameter)           |
| `trend_multiplier`   | Config extras               | `float`        | yes       | Final multiplier (§3.7 parameter)    |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum          | Unit   | Required? | Meaning                              |
|-------------|--------|-----------------------------|--------|-----------|--------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}`   | —      | yes       | Direction derived from sign(quantity) |
| `bid_price` | float  | > 0                         | price  | yes       | Current market price (taker)         |
| `quantity`  | float  | [-40, 40]                   | shares | yes       | Signed order size (+ buy, - sell)    |
| `reasoning` | string | 1–2 sentences               | —      | yes       | Trend % and resulting quantity        |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clamped to [-40, 40] before emission.
- `bid_price` MUST equal the current market price (the agent is a price-taker).
- Positive quantity = buy; negative quantity = sell; zero = hold.
- The agent is deterministic given the same price history and parameters.

##### Serialization Format

```
<analysis>Trend over {lookback} rounds = {trend:.2%}; resulting quantity = {quantity:.2f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <float>, "reasoning": "Trend-following: {trend:.2%} over {lookback} rounds."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. The `provides_liquidity` field in the outbound message envelope is always `False`.

#### Decision Information Set

| Signal           | Source              | Frequency | Lag | Quality    |
|------------------|---------------------|-----------|-----|------------|
| `price`          | Market coordinator  | Per-round | 0   | Exact      |
| `price_history`  | Agent memory buffer | Per-round | 0   | Exact      |

The agent uses no peer signals, no fundamental value, and no order-book data.

#### Core Behavioral Mechanism

```
Step 1 — Check history sufficiency:
  Read: price_history, lookback
  IF len(price_history) < lookback:
    quantity = 0; action = "hold"
    → RETURN

Step 2 — Compute trend signal:
  Read: price_history[-lookback] (oldest), price_history[-1] (newest)
  trend = (price_history[-1] - price_history[-lookback]) / price_history[-lookback]
  (Traces to: Positive-Feedback Trading, De Long et al. 1990)

Step 3 — Scale trend into raw quantity:
  Read: trend_sensitivity, base_position_size, trend_multiplier
  raw_quantity = trend × trend_sensitivity × base_position_size × trend_multiplier

Step 4 — Clamp to position limits:
  quantity = clamp(raw_quantity, -max_quantity, max_quantity)

Step 5 — Determine action label:
  IF quantity > 0: action = "buy"; bid_price = price
  ELIF quantity < 0: action = "sell"; bid_price = price
  ELSE: action = "hold"; bid_price = 0.0

Step 6 — Apply resource constraints:
  quantity = _apply_constraints(bid_price, quantity)

Step 7 — Execute trade (post-decision):
  Write: position += quantity
  Write: cash -= quantity × bid_price
```

#### Action Space

Action types allowed: `buy`, `sell`, `hold`.

Action parameter rule: `bid_price` = current market price (no limit orders). Sizing rule: `quantity = clamp(trend × trend_sensitivity × base_position_size × trend_multiplier, -40, 40)`.

Position constraints: Maximum absolute order per round = 40 units. No cumulative position limit enforced at the agent level (this is an environment constraint if desired).

#### Mathematical Model

Core decision equation:
```
trend = (price_history[-1] - price_history[-lookback]) / price_history[-lookback]
quantity = trend × trend_sensitivity × base_position_size × trend_multiplier
quantity = clamp(quantity, -40, 40)
```

State variables:
- `price_history`: Append-only list of observed prices, updated each round.
- `position`: Running tally of net shares held (updated by `_execute_trade`).
- `cash`: Running cash balance (updated by `_execute_trade`).

#### Behavioral Properties

- Time horizon: Short-Medium — lookback window of 3–10 rounds; reacts within one round of signal change; bridges HFT and slower agents temporally.
- Risk tolerance: Medium — willing to trade into volatile regimes following momentum, but hard-clamped at ±40 units per round to prevent unbounded exposure.
- Information asymmetry: Partial — observes only price history (no fundamental value, order book depth, or peer positions).
- Psychological profile: Exhibits positive-feedback bias (De Long et al. 1990) — mechanically reinforces existing trends regardless of underlying fundamentals; no anchoring, no mean-reversion instinct; susceptible to amplifying noise as if it were signal.

## Parameters

| Parameter           | Type  | Default | Valid Range | Sensitivity | Description                             | Impact                                         | Source                                     |
|---------------------|-------|---------|-------------|-------------|-----------------------------------------|------------------------------------------------|--------------------------------------------|
| `lookback`          | int   | 5       | [3, 10]     | Medium      | Trend lookback window length            | Higher → smoother trend signal, smaller magnitude in volatile regimes | Kirilenko et al. (2017), Table 3           |
| `trend_sensitivity` | float | 1.0     | [0.5, 2.0]  | High        | Responsiveness to detected trend signal | Higher → proportionally larger order quantities | De Long et al. (1990), numerical examples  |
| `base_position_size`| float | 10.0    | [5.0, 20.0] | High        | Base order magnitude before trend scaling | Higher → proportionally larger order quantities | Flash-crash simulation calibration         |
| `trend_multiplier`  | float | 10.0    | [5.0, 15.0] | High        | Final amplification factor              | Higher → proportionally larger order quantities | Flash-crash simulation calibration         |
| `max_quantity`      | int   | 40      | [20, 80]    | Low         | Hard clamp on absolute order size per round | Higher → allows larger individual orders      | Position-limit convention across scenarios |

## Worked Numerical Examples

**Case 1 — Moderate uptrend:**
- `price_history[-5:]` = [100.0, 101.0, 102.0, 103.0, 104.0], `lookback` = 5
- `trend` = (104 - 100) / 100 = 0.04
- `quantity` = 0.04 × 1.0 × 10.0 × 10.0 = 4.0 → emit buy 4 shares
- Reasoning: "Trend-following: +4.00% over 5 rounds."

**Case 2 — Sharp downtrend (crash in progress):**
- `price_history[-5:]` = [100.0, 95.0, 88.0, 82.0, 75.0], `lookback` = 5
- `trend` = (75 - 100) / 100 = -0.25
- `quantity` = -0.25 × 1.0 × 10.0 × 10.0 = -25.0 → emit sell 25 shares
- Reasoning: "Trend-following: -25.00% over 5 rounds."

**Case 3 — Flat market:**
- `price_history[-5:]` = [100.0, 100.1, 99.9, 100.0, 100.05], `lookback` = 5
- `trend` = (100.05 - 100.0) / 100.0 = 0.0005
- `quantity` = 0.0005 × 1.0 × 10.0 × 10.0 = 0.05 → rounds to ~0, effective hold
- Reasoning: "Trend-following: +0.05% over 5 rounds."

**Edge Case — Extreme crash hitting clamp:**
- `price_history[-3:]` = [100.0, 60.0, 30.0], `lookback` = 3
- `trend` = (30 - 100) / 100 = -0.70
- Raw `quantity` = -0.70 × 1.0 × 10.0 × 10.0 = -70.0 → clamped to -40
- Reasoning: "Trend-following: -70.00% over 3 rounds. Clamped to -40."

## Behavioral Verification and Calibration

**Verification criteria:**
1. Over any 20-round window where the market exhibits a sustained unidirectional trend (cumulative return > 5%), the agent's net order flow MUST have the same sign as the trend in at least 80% of rounds.
2. The agent MUST never emit |quantity| > 40.
3. The agent MUST emit quantity = 0 when price_history length < lookback.
4. Given identical price history sequences across two runs with the same seed, the agent MUST produce byte-identical outputs (determinism test).

**Calibration procedure:**
- Set `trend_sensitivity` = 1.0, `trend_multiplier` = 10, `base_position_size` = 10, `lookback` = 5.
- Run 200-round flash-crash simulation. Verify agent contributes to crash amplification (non-zero sell flow during decline phase).
- Sensitivity sweep: vary `trend_sensitivity` in {0.5, 1.0, 1.5, 2.0} and confirm monotone relationship with crash depth.

**Ablation Hooks:**
- Disable by setting `trend_sensitivity` = 0 (agent becomes inert, always holds).
- Disable by setting `lookback` > `total_rounds` (agent never has enough history to compute trend).

## Academic References

- De Long, J.B., Shleifer, A., Summers, L.H., & Waldmann, R.J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *The Journal of Finance*, 45(2), 379–395. https://doi.org/10.2307/2328662
- Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: implications for stock market efficiency. *The Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Kirilenko, A., Kyle, A.S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: high-frequency trading in an electronic market. *The Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498
- Brunnermeier, M.K., & Pedersen, L.H. (2005). Predatory trading. *The Journal of Finance*, 60(4), 1825–1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x

## Design Provenance

| Field       | Content                                                       |
|-------------|---------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                    |
| Created     | 2026-07-11                                                    |
| Version     | 1.0.0                                                         |
| Status      | canonical                                                     |
| Icon        | ![](../agent_images/icons/finance-algorithmic-trader.png)     |
