# High-Frequency Momentum Trader

## Summary

| Field                 | Content                                                                                                      |
|-----------------------|--------------------------------------------------------------------------------------------------------------|
| Archetype             | High-Frequency Momentum Trader                                                                               |
| Theory Family         | Market Microstructure — HFT Momentum Amplification                                                           |
| Behavioral Tendency   | **Diverging** — amplifies existing price movements by trading rapidly in the direction of short-term momentum |
| Time Horizon          | Ultra-short (lookback window of 2–5 rounds)                                                                  |
| Risk Tolerance        | Medium-high (large position sizes, but hard-clamped at ±60)                                                  |
| Information Asymmetry | Partial (observes price history only, no access to fundamental value or order book depth)                     |
| Determinism           | Deterministic (given identical price history and parameters, always produces the same order)                  |

## Definition and Goals

The high-frequency momentum trader models ultra-fast algorithmic trading systems that detect very short-term momentum signals and trade aggressively in the direction of detected price velocity. In the real world, these correspond to proprietary high-frequency trading firms (e.g. Virtu, Citadel Securities, Jump Trading) and co-located algorithmic strategies that execute within milliseconds of detecting directional signals — any participant whose buy/sell decision derives from ultra-short price trajectories with a speed advantage over other market participants.

The agent's decision goal is to produce a signed order quantity proportional to the estimated short-term momentum over a very short lookback window. The quantity is computed as `short_momentum × momentum_sensitivity × base_position_size × speed_advantage`, clamped to a maximum absolute value of 60 units. The agent does not optimise an explicit utility function; it mechanically amplifies detected momentum at the fastest timescale in the simulation.

The agent's behavioural role inside the simulation is to serve as the primary crash trigger: it detects the initial directional move earliest (due to its speed advantage and short lookback) and amplifies it with large position sizes before slower agents can react, seeding the cascade that algorithmic traders and stop-loss traders subsequently reinforce. Non-goals: (1) the high-frequency trader MUST NOT provide liquidity — it is always a liquidity taker with `provides_liquidity = False`; (2) it MUST NOT incorporate fundamental value signals or mean-reversion logic — it is purely momentum-driven; (3) it MUST NOT exhibit market-making behaviour such as quoting two-sided spreads.

## Theoretical Foundation

**HFT Flash Crash Dynamics (Kirilenko et al. 2017)**:
- Theory / Study: The Flash Crash: High-Frequency Trading in an Electronic Market
- Citation: Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498
- Core Insight: High-frequency traders act as rapid momentum amplifiers during flash crashes. They detect short-term price velocity faster than other participants and trade aggressively in the direction of the move, creating a "hot potato" effect where inventory is rapidly passed between HFTs, amplifying net directional pressure and depleting standing liquidity.
- Mathematical Formulation: `quantity = (P_t - P_{t-k}) / P_{t-k} × momentum_sensitivity × base_position_size × speed_advantage`, where `k` is the short lookback window (2–5 rounds).
- Empirical Evidence: Kirilenko et al. (2017) analyse E-mini S&P 500 futures on May 6, 2010: HFTs' net position swung from +3,000 to -3,000 contracts within minutes; their aggregate trading volume was 29% of total volume during the crash window (Table 3, p. 985). The paper documents that HFTs' net selling was concentrated in a 13-minute window and preceded the worst of the price collapse.
- Relevance to This Agent: The agent directly operationalises the HFT momentum-amplification mechanism — it detects short-term momentum faster (shorter lookback) and trades larger (speed_advantage multiplier) than other trend-following agents, seeding the crash cascade.
- Calibration Source: `momentum_sensitivity` in [0.5, 3.0] from Kirilenko et al. (2017) Table 3 HFT participation rates; `speed_advantage` in [1.2, 2.0] calibrated from the documented 2–5x volume advantage of HFTs over other aggressive traders; `lookback` in [2, 5] rounds represents sub-minute detection horizons.
- Falsification Conditions: If this agent's net order flow over any 5-round window is uncorrelated with the signed short-term momentum over the same window (|r| < 0.3), the HFT momentum-amplification mechanism is falsified.
- Alternative Theories: Informed trading (Kyle 1985), inventory-based market-making (Avellaneda & Stoikov 2008), rational expectations momentum (Cespa & Vives 2012).

## Design Purpose and Activation Triggers

Purpose: Amplify initial price movements at ultra-short timescale through rapid momentum detection and aggressive directional trading, acting as the primary crash trigger.

Call Frequency: Every tick (every simulation round).

Prerequisite Signals (must be available for the agent to evaluate):
- Price history of length >= lookback window available
- Current market price available

Missing-Signal Policy: If price history has fewer observations than the lookback window, the agent uses the single-round return from `market_data["return"]` as a fallback momentum estimate. If current price is unavailable (NaN), the agent abstains entirely (quantity = 0).

Activation Triggers:
- Positive short-momentum detected (short_momentum > 0): Buy order proportional to momentum magnitude × speed_advantage
- Negative short-momentum detected (short_momentum < 0): Sell order proportional to momentum magnitude × speed_advantage
- Momentum near zero (signal rounds to ~0): Hold (quantity negligible)

Deactivation Conditions:
- Position clamp reached (|quantity| hits 60): Agent is at maximum capacity per round
- Cash exhaustion: Cannot buy further (constrained by _apply_constraints)
- Market closure / simulation end: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                       | Behavioral change                                                | Mechanism                                      |
|---------------------------------|------------------------------------------------------------------|------------------------------------------------|
| High volatility regime          | Larger absolute orders (momentum magnitude increases)            | Proportional response amplified by speed_advantage |
| Rapid trend reversal            | Reverses direction within 1–2 rounds of signal flip              | Ultra-short lookback ensures fast re-detection |
| Low-liquidity environment       | Same algorithmic output; does not self-limit based on liquidity  | No liquidity-awareness built into decision     |

Environmental Dependencies: Requires per-round market data broadcast containing `price` and `return` fields. Maintains an internal `price_history` buffer. No peer-action summaries or fundamental value signals needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source                     | Type / Shape  | Required? | Notes                                             |
|------------------------|----------------------------|---------------|-----------|---------------------------------------------------|
| `price`                | Market coordinator payload | `float`       | yes       | Current asset price                               |
| `return`               | Market coordinator payload | `float`       | yes       | Single-round return (fallback momentum)           |
| `price_history`        | Agent persisted state      | `list[float]` | yes       | Full price history up to current round            |
| `round`                | Scheduler / round header   | `int`         | yes       | Current simulation round number                   |
| `lookback`             | Config extras              | `int`         | yes       | Short momentum window length (§Parameters)        |
| `momentum_sensitivity` | Config extras              | `float`       | yes       | Scaling factor for momentum signal (§Parameters)  |
| `base_position_size`   | Config extras              | `float`       | yes       | Base order magnitude (§Parameters)                |
| `speed_advantage`      | Config extras              | `float`       | yes       | HFT speed multiplier (§Parameters)               |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                               |
|-------------|--------|---------------------------|--------|-----------|---------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction derived from sign(quantity)  |
| `bid_price` | float  | > 0                       | price  | yes       | Current market price (taker)          |
| `quantity`  | float  | [-60, 60]                 | shares | yes       | Signed order size (+ buy, - sell)     |
| `reasoning` | string | 1–2 sentences             | —      | yes       | Momentum % and resulting quantity     |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clamped to [-60, 60] before emission.
- `bid_price` MUST equal the current market price (the agent is a price-taker).
- Positive quantity = buy; negative quantity = sell; zero = hold.
- `provides_liquidity` in the outbound message envelope is always `False`.
- The agent is deterministic given the same price history and parameters.

##### Serialization Format

```
<analysis>Short momentum over {lookback} rounds = {short_momentum:.2%}; signal = {signal:.4f}; quantity = {quantity:.2f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <float>, "reasoning": "HFT momentum: {short_momentum:.2%} over {lookback} rounds, speed_advantage={speed_advantage}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity directly from the formula. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. The `provides_liquidity` field in the outbound message envelope is always `False`.

#### Decision Information Set

| Signal          | Type       | Memory Window    | Rationale                                                  |
|-----------------|------------|------------------|------------------------------------------------------------|
| `price`         | Continuous | Current tick     | Required for computing momentum and setting bid_price      |
| `price_history` | Continuous | Last 2–5 ticks   | Core input for short-momentum calculation                  |
| `return`        | Continuous | Current tick     | Fallback momentum estimate when history < lookback         |

Does NOT use: fundamental value, order book depth, peer positions, liquidity levels, volume data, net demand — the agent reacts only to short-term price trajectory.

#### Core Behavioral Mechanism

```
Step 1 — Compute short momentum:
  Read: price_history, lookback, market_data["return"]
  IF len(price_history) >= lookback:
    recent = price_history[-lookback:]
    short_momentum = (recent[-1] - recent[0]) / recent[0]
  ELSE:
    short_momentum = market_data["return"]
  (Traces to: HFT Flash Crash Dynamics, Kirilenko et al. 2017)

Step 2 — Compute signal strength:
  Read: momentum_sensitivity
  signal = short_momentum × momentum_sensitivity

Step 3 — Compute raw quantity:
  Read: base_position_size, speed_advantage
  raw_quantity = signal × base_position_size × speed_advantage

Step 4 — Clamp to position limits:
  Read: max_quantity
  quantity = clamp(raw_quantity, -max_quantity, max_quantity)

Step 5 — Apply resource constraints:
  Read: price, cash, position
  quantity = _apply_constraints(price, quantity)

Step 6 — Determine action label:
  IF quantity > 0: action = "buy"; bid_price = price
  ELIF quantity < 0: action = "sell"; bid_price = price
  ELSE: action = "hold"; bid_price = 0.0

Step 7 — Execute trade (post-decision):
  Write: position += quantity
  Write: cash -= quantity × bid_price
```

#### Action Space

| Aspect                | Specification                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                                 |
| Action parameter rule | `bid_price` = current market price (no limit orders; agent is always a price-taker)                   |
| Sizing rule           | `quantity = clamp(short_momentum × momentum_sensitivity × base_position_size × speed_advantage, -60, 60)` |
| Action lifetime       | Immediate execution; no persistent resting orders                                                     |
| Revision policy       | No revision — each round's order is independent; previous orders are not amended                      |
| State constraint      | No self-imposed cumulative position limit at agent level                                              |
| Resource cap          | Cash constraint applied via `_apply_constraints` (cannot buy more than cash allows)                   |
| Exit rule             | None — agent trades every round as long as conditions permit                                          |

#### Mathematical Model

**Decision output:** Signed quantity (float in [-60, 60]) representing the directional order to submit this round.

**Decision logic formalization:**

```
Step 1 — Compute short momentum:
  IF len(price_history) >= lookback:
    recent = price_history[-lookback:]
    short_momentum = (recent[-1] - recent[0]) / recent[0]
  ELSE:
    short_momentum = market_data["return"]

Step 2 — Compute signal:
  signal = short_momentum * momentum_sensitivity

Step 3 — Compute raw quantity:
  raw_quantity = signal * base_position_size * speed_advantage

Step 4 — Clamp:
  quantity = clamp(raw_quantity, -60, 60)

Step 5 — Apply resource constraints:
  quantity = _apply_constraints(price, quantity)

Step 6 — Determine action:
  IF quantity > 0: action = "buy"
  ELIF quantity < 0: action = "sell"
  ELSE: action = "hold"
```

**State variables:**
- `price_history`: Append-only list of observed prices, updated each round during `perceive`.
- `position`: Running tally of net shares held (updated by `_execute_trade` post-decision).
- `cash`: Running cash balance (updated by `_execute_trade` post-decision).

**State evolution:**
- `price_history`: Updated pre-decide (during `perceive`, appends new price).
- `position` and `cash`: Updated post-decide (during `_execute_trade`, after quantity finalised).

**Determinism contract:** Fully deterministic given identical price history and parameter values.

**Parameter symbol table:**

| Symbol                 | Meaning                            | Default Value | Source                       |
|------------------------|------------------------------------|---------------|------------------------------|
| `lookback`             | Short momentum window length       | 2             | Kirilenko et al. (2017)      |
| `momentum_sensitivity` | Scaling factor for momentum signal | 3.0           | Kirilenko et al. (2017)      |
| `base_position_size`   | Base order magnitude               | 40.0          | simulation-bases.md §4.1     |
| `speed_advantage`      | HFT speed multiplier               | 1.5           | simulation-bases.md §4.1     |
| `max_quantity`         | Hard clamp on absolute order size  | 60            | simulation-bases.md §4.1     |

#### Behavioral Properties

- Time horizon: Ultra-short — lookback window of 2–5 rounds; detects and reacts to momentum within 1–2 ticks; fastest agent in the ecosystem.
- Risk tolerance: Medium-high — trades large position sizes (base 40 shares × 1.5 speed advantage) but hard-clamped at ±60 units per round.
- Information asymmetry: Partial — observes only price history and single-round returns; no access to fundamental value, order book depth, or peer positions.
- Psychological profile: Pure momentum amplifier (Kirilenko et al. 2017) — no fundamental anchoring, no mean-reversion, no risk-aversion modulation; mechanically trades in the direction of detected short-term velocity regardless of magnitude or context.

## Parameters

| Parameter              | Type  | Default | Valid Range | Sensitivity | Description                                    | Impact                                              | Source                               |
|------------------------|-------|---------|-------------|-------------|------------------------------------------------|-----------------------------------------------------|--------------------------------------|
| `lookback`             | int   | 2       | [2, 5]      | Medium      | Short momentum lookback window length          | Higher → smoother but slower signal detection        | Kirilenko et al. (2017), Table 3     |
| `momentum_sensitivity` | float | 3.0     | [0.5, 3.0]  | High        | Responsiveness to detected momentum signal     | Higher → proportionally larger order quantities     | Kirilenko et al. (2017), Table 3     |
| `base_position_size`   | float | 40.0    | [20.0, 60.0]| High        | Base order magnitude before speed scaling      | Higher → proportionally larger order quantities     | simulation-bases.md §4.1             |
| `speed_advantage`      | float | 1.5     | [1.2, 2.0]  | High        | Multiplier reflecting HFT execution speed edge | Higher → proportionally larger order quantities     | simulation-bases.md §4.1             |
| `max_quantity`         | int   | 60      | [30, 100]   | Low         | Hard clamp on absolute order size per round    | Higher → allows larger individual orders            | Position-limit convention            |

## Worked Numerical Examples

### Case 1 — Moderate positive momentum

System state: `price_history[-2:]` = [100.0, 102.0], `lookback` = 2, `momentum_sensitivity` = 3.0, `base_position_size` = 40.0, `speed_advantage` = 1.5

Calculation:
- `short_momentum` = (102.0 - 100.0) / 100.0 = 0.02
- `signal` = 0.02 × 3.0 = 0.06
- `raw_quantity` = 0.06 × 40.0 × 1.5 = 3.6
- `quantity` = clamp(3.6, -60, 60) = 3.6

Decision: buy 3.6 shares at bid_price = 102.0
State update: `cash`: 10000.0 → 10000.0 - 3.6 × 102.0 = 9632.8; `position`: 0 → 3.6

### Case 2 — Sharp negative momentum (crash in progress)

System state: `price_history[-2:]` = [100.0, 90.0], `lookback` = 2, `momentum_sensitivity` = 3.0, `base_position_size` = 40.0, `speed_advantage` = 1.5

Calculation:
- `short_momentum` = (90.0 - 100.0) / 100.0 = -0.10
- `signal` = -0.10 × 3.0 = -0.30
- `raw_quantity` = -0.30 × 40.0 × 1.5 = -18.0
- `quantity` = clamp(-18.0, -60, 60) = -18.0

Decision: sell 18.0 shares at bid_price = 90.0
State update: `cash`: 10000.0 → 10000.0 + 18.0 × 90.0 = 11620.0; `position`: 0 → -18.0 (constrained by _apply_constraints if position = 0, resulting in quantity = 0 if no position to sell)

### Case 3 — Flat market (near-zero momentum)

System state: `price_history[-2:]` = [100.0, 100.05], `lookback` = 2, `momentum_sensitivity` = 3.0, `base_position_size` = 40.0, `speed_advantage` = 1.5

Calculation:
- `short_momentum` = (100.05 - 100.0) / 100.0 = 0.0005
- `signal` = 0.0005 × 3.0 = 0.0015
- `raw_quantity` = 0.0015 × 40.0 × 1.5 = 0.09
- `quantity` = clamp(0.09, -60, 60) = 0.09 (effectively negligible)

Decision: buy 0.09 shares (effectively hold)
State update: minimal change

### Edge Case — Extreme crash hitting clamp

System state: `price_history[-2:]` = [100.0, 60.0], `lookback` = 2, `momentum_sensitivity` = 3.0, `base_position_size` = 40.0, `speed_advantage` = 1.5

Calculation:
- `short_momentum` = (60.0 - 100.0) / 100.0 = -0.40
- `signal` = -0.40 × 3.0 = -1.20
- `raw_quantity` = -1.20 × 40.0 × 1.5 = -72.0
- `quantity` = clamp(-72.0, -60, 60) = -60.0 (clamped)

Decision: sell 60.0 shares at bid_price = 60.0 (subject to position constraint)
State update: If position = 50, constrained to sell 50; `position`: 50 → 0; `cash` += 50 × 60.0

## Behavioral Verification and Calibration

**Verification criteria:**
1. Over any 5-round window where the market exhibits a sustained unidirectional move (cumulative return > 3%), the agent's net order flow MUST have the same sign as the momentum in at least 90% of rounds.
2. The agent MUST never emit |quantity| > 60.
3. When price_history length < lookback, the agent MUST fall back to using the single-round return as its momentum signal.
4. Given identical price history sequences across two runs with the same parameters, the agent MUST produce byte-identical outputs (determinism test).
5. The agent's `provides_liquidity` flag MUST always be `False`.

**Calibration procedure:**
- Set `momentum_sensitivity` = 3.0, `base_position_size` = 40.0, `speed_advantage` = 1.5, `lookback` = 2.
- Run 200-round flash-crash simulation. Verify agent produces the largest absolute order volumes in the first 5–10 rounds of the crash phase.
- Sensitivity sweep: vary `momentum_sensitivity` in {0.5, 1.0, 2.0, 3.0} and confirm monotone relationship with crash initiation speed.

**Ablation Hooks:**

| Ablation name         | Setting                   | Hypothesis tested                              | Expected direction                    | Metric                        |
|-----------------------|---------------------------|------------------------------------------------|---------------------------------------|-------------------------------|
| `disable_hft`         | `momentum_sensitivity = 0`| HFT is necessary for crash initiation          | Crash depth decreases or disappears   | `crash_depth`                 |
| `slow_hft`            | `lookback = 5`            | Shorter lookback amplifies crashes more         | Crash develops more slowly            | `time_to_trough`              |
| `reduce_speed`        | `speed_advantage = 1.0`   | Speed advantage amplifies crash magnitude       | Smaller order sizes in early crash    | `hft_volume_first_10_rounds`  |

## Academic References

| # | Citation                                                                                                                                                                        | Notes                                       |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| 1 | Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498 | Primary theory; HFT momentum amplification  |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379–395. https://doi.org/10.2307/2328395 | Positive-feedback trading mechanism         |
| 3 | Brunnermeier, M. K., & Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825–1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x                    | Predatory exploitation of momentum traders  |

## Design Provenance

| Field       | Content                                                          |
|-------------|------------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                       |
| Created     | 2026-07-11                                                       |
| Version     | 1.0.0                                                            |
| Status      | canonical                                                        |
| Icon        | ![](../agent_images/icons/finance-high-frequency-trader.png)     |
