# Uninformed Retail Noise Trader

## Summary

| Field                 | Content                                                                                                      |
|-----------------------|--------------------------------------------------------------------------------------------------------------|
| Archetype             | Uninformed Retail Noise Trader                                                                               |
| Theory Family         | Noise Trading — Random Background Volume                                                                     |
| Behavioral Tendency   | **Adaptive** — neither systematically diverging nor converging; random with weak position mean-reversion      |
| Time Horizon          | Low-frequency (trades only every `trade_frequency` rounds)                                                   |
| Risk Tolerance        | Low (small position sizes, hard-clamped at ±15)                                                              |
| Information Asymmetry | None (trades randomly without using any market information)                                                   |
| Determinism           | Stochastic-given-seed (output depends on Gaussian random draw seeded by simulation RNG)                      |

## Definition and Goals

The uninformed retail noise trader models individual retail investors and small market participants who trade infrequently with no informational edge, generating random background volume in the market. In the real world, these correspond to individual investors making sporadic portfolio adjustments, algorithmic rebalancing bots with randomized timing, and "noise" in the sense of Black (1986) — any participant whose trading activity is uncorrelated with either fundamental value changes or short-term price momentum.

The agent's decision goal is to emit a random signed quantity drawn from a Gaussian distribution centered at zero, with a weak mean-reversion drag pulling its position back toward zero over time. The quantity is computed as `gauss(0, noise_std) + (-position_mean_reversion × position)`, clamped to [-15, 15]. The agent only trades on rounds divisible by `trade_frequency`, remaining silent on other rounds.

The agent's behavioural role inside the simulation is to provide steady low-volume background activity that prevents the market from being trivially one-sided or liquidity-less during calm periods. Retail traders do not contribute meaningfully to crash dynamics — they are too small and infrequent to amplify cascades. Non-goals: (1) the retail trader MUST NOT exhibit momentum-following or trend-detection behaviour — its direction is random; (2) it MUST NOT provide liquidity in the structural sense — `provides_liquidity` is always `False`; (3) it MUST NOT accumulate large directional positions — the mean-reversion component ensures position drift is bounded.

## Theoretical Foundation

**Noise Trading (Black 1986)**:
- Theory / Study: Noise
- Citation: Black, F. (1986). Noise. *Journal of Finance*, 41(3), 528–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x
- Core Insight: Noise traders are participants who trade on noise as if it were information. They provide the essential "other side" of informed trades, making markets liquid enough to function, but their activity is uncorrelated with fundamental value changes. Without noise traders, informed traders would have no counterparties and markets would be informationally efficient but illiquid.
- Mathematical Formulation: `quantity = N(0, noise_std) + (-position_mean_reversion × position)`, where N(0, σ) is a Gaussian draw; the mean-reversion term prevents unbounded position drift.
- Empirical Evidence: Black (1986) argues theoretically that noise trading accounts for a substantial fraction of total market volume. Barber & Odean (2000, DOI: 10.1111/0022-1082.00226) document that individual retail investors trade excessively (average annual turnover of 75% vs. 53% for the market) with no informational edge, earning -3.7% annual excess returns after costs — consistent with uninformed noise trading (Table III, p. 789).
- Relevance to This Agent: The agent directly operationalises the noise-trading concept — it trades at random intervals with random direction and magnitude, providing background volume without directional bias or information content, ensuring the market simulation has realistic non-zero volume even in calm periods.
- Calibration Source: `noise_std` in [1.0, 8.0] calibrated from typical retail order sizes relative to institutional volume in Barber & Odean (2000); `trade_frequency` in [1, 5] rounds represents the empirical observation that retail traders do not participate every tick; `position_mean_reversion` in [0.05, 0.2] ensures positions remain bounded within a few multiples of noise_std.
- Falsification Conditions: If this agent's net order flow over any 50-round window exhibits correlation |r| > 0.3 with the price trend over the same window, the noise-trading assumption is falsified (the agent is accidentally momentum-following). If the agent's average absolute position exceeds 3 × noise_std / position_mean_reversion over a full simulation, the mean-reversion mechanism is falsified.
- Alternative Theories: Uninformed liquidity traders (Kyle 1985), disposition-effect traders (Shefrin & Statman 1985), attention-driven traders (Barber & Odean 2008).

## Design Purpose and Activation Triggers

Purpose: Provide random low-volume background trading activity, ensuring realistic non-zero market volume during calm periods without contributing directional bias.

Call Frequency: Every tick (every simulation round), but active only on rounds where `round_num % trade_frequency == 0`.

Prerequisite Signals (must be available for the agent to evaluate):
- Current market price available (for bid_price)
- Round number available (for trade_frequency gating)
- Own position available (for mean-reversion component)

Missing-Signal Policy: If price is unavailable (NaN), the agent abstains (quantity = 0). Round number and position are always available from internal state.

Activation Triggers:
- Trade round (round_num % trade_frequency == 0): Generate random quantity with mean-reversion
- Non-trade round (round_num % trade_frequency != 0): Hold (quantity = 0)

Deactivation Conditions:
- Non-trade round: Agent is silent (emits zero quantity)
- Cash exhaustion combined with zero position: Cannot trade in either direction
- Market closure / simulation end: Agent ceases activity

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                                              | Mechanism                                       |
|------------------------------|----------------------------------------------------------------|-------------------------------------------------|
| Large accumulated position   | Mean-reversion term biases quantity toward reducing position   | `-position_mean_reversion × position` grows     |
| High volatility regime       | No change in behaviour; agent is market-condition-blind        | Random draw is independent of market state      |
| Crash in progress            | No directional response; continues random trading if trade round | Noise unaffected by price movements            |

Environmental Dependencies: Requires per-round market data broadcast containing `price` field (used only for bid_price). Requires access to simulation round number. No peer-action summaries, fundamental value, momentum signals, or liquidity data needed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                     | Source                     | Type / Shape | Required? | Notes                                               |
|---------------------------|----------------------------|--------------|-----------|-----------------------------------------------------|
| `price`                   | Market coordinator payload | `float`      | yes       | Current asset price (used for bid_price)            |
| `position`                | Agent persisted state      | `float`      | yes       | Current net position (for mean-reversion)           |
| `round`                   | Scheduler / round header   | `int`        | yes       | Current simulation round number                     |
| `trade_frequency`         | Config extras              | `int`        | yes       | Trade every N rounds (§Parameters)                  |
| `noise_std`               | Config extras              | `float`      | yes       | Standard deviation of random quantity (§Parameters) |
| `position_mean_reversion` | Config extras              | `float`      | yes       | Mean-reversion coefficient (§Parameters)            |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                               |
|-------------|--------|---------------------------|--------|-----------|---------------------------------------|
| `action`    | enum   | `{"buy", "sell", "hold"}` | —      | yes       | Direction derived from sign(quantity)  |
| `bid_price` | float  | > 0 or 0.0               | price  | yes       | Market price if trading, 0.0 if hold  |
| `quantity`  | float  | [-15, 15]                 | shares | yes       | Signed order size (+ buy, - sell)     |
| `reasoning` | string | 1–2 sentences             | —      | yes       | Trade rationale (noise + reversion)   |

##### Content Constraints

- All four output fields MUST be present on every call.
- `quantity` MUST be clamped to [-15, 15] before emission.
- `bid_price` = current market price when trading; 0.0 on non-trade rounds.
- Positive quantity = buy; negative quantity = sell; zero = hold.
- `provides_liquidity` in the outbound message envelope is always `False`.
- The agent is stochastic-given-seed; the Gaussian draw depends on the simulation RNG state.

##### Serialization Format

```
<analysis>Trade round: {is_trade_round}. Random draw = {random_trade:.2f}, reversion = {reversion:.2f}, quantity = {quantity:.2f}.</analysis>
<decision>{"action": "<buy|sell|hold>", "bid_price": <float>, "quantity": <float>, "reasoning": "Noise trader: random={random_trade:.2f}, reversion={reversion:.2f}."}</decision>
```

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Rule-driven variants compute quantity from the Gaussian draw plus mean-reversion term. Model-driven variants (LLM, RuleLLM) MUST include the output schema in the prompt and parse the `<decision>` JSON; the stochastic element may be injected as a pre-computed random number in the prompt context. Retrieval-augmented variants inject domain knowledge before the decision but MUST still honour the same output schema. The `provides_liquidity` field in the outbound message envelope is always `False`.

#### Decision Information Set

| Signal     | Type       | Memory Window | Rationale                                          |
|------------|------------|---------------|----------------------------------------------------|
| `price`    | Continuous | Current tick  | Required for setting bid_price                     |
| `position` | Continuous | Current state | Required for mean-reversion component of quantity  |
| `round`    | Discrete   | Current tick  | Required for trade_frequency gating                |

Does NOT use: price history, momentum signals, fundamental value, peer positions, volume data, net demand, liquidity levels — the agent is intentionally information-free beyond its own position.

#### Core Behavioral Mechanism

```
Step 1 — Check trade frequency gate:
  Read: round_num, trade_frequency
  IF round_num % trade_frequency != 0:
    quantity = 0.0; bid_price = 0.0; action = "hold"
    → RETURN (skip remaining steps)
  (implementation convenience — frequency gating)

Step 2 — Generate random component:
  random_trade = gauss(0, noise_std)
  (Traces to: Noise Trading, Black 1986)

Step 3 — Compute mean-reversion component:
  Read: position, position_mean_reversion
  reversion = -position_mean_reversion × position

Step 4 — Compute raw quantity:
  raw_quantity = random_trade + reversion

Step 5 — Clamp:
  Read: max_quantity
  quantity = clamp(raw_quantity, -max_quantity, max_quantity)
  bid_price = price

Step 6 — Apply resource constraints:
  quantity = _apply_constraints(bid_price, quantity)

Step 7 — Determine action:
  IF quantity > 0: action = "buy"
  ELIF quantity < 0: action = "sell"
  ELSE: action = "hold"

Step 8 — Execute trade (post-decision):
  IF quantity > 0: Write: cash -= quantity × bid_price; Write: position += quantity
  ELIF quantity < 0: Write: cash += abs(quantity) × bid_price; Write: position += quantity
```

#### Action Space

| Aspect                | Specification                                                                        |
|-----------------------|--------------------------------------------------------------------------------------|
| Action types allowed  | `buy`, `sell`, `hold`                                                                |
| Action parameter rule | `bid_price` = current market price when trading; 0.0 on non-trade rounds             |
| Sizing rule           | `quantity = clamp(gauss(0, noise_std) + (-position_mean_reversion × position), -15, 15)` |
| Action lifetime       | Immediate execution; no persistent resting orders                                    |
| Revision policy       | No revision — each trade-round's order is independent                                |
| State constraint      | Mean-reversion ensures position stays bounded (long-run mean ≈ 0)                    |
| Resource cap          | Cash constraint applied via `_apply_constraints`; hard clamp at ±15 shares per round |
| Exit rule             | None — agent continues trading at fixed frequency indefinitely                       |

#### Mathematical Model

**Decision output:** Signed quantity (float in [-15, 15]) representing the random order to submit this round (or 0 on non-trade rounds).

**Decision logic formalization:**

```
Step 1 — Check trade frequency gate:
  Read: round_num, trade_frequency
  IF round_num % trade_frequency != 0:
    quantity = 0.0
    bid_price = 0.0
    action = "hold"
    → RETURN (skip remaining steps)

Step 2 — Generate random component:
  random_trade = gauss(0, noise_std)  [from simulation RNG]

Step 3 — Compute mean-reversion component:
  Read: position
  reversion = -position_mean_reversion * position

Step 4 — Compute raw quantity:
  raw_quantity = random_trade + reversion

Step 5 — Clamp:
  quantity = clamp(raw_quantity, -15, 15)
  bid_price = price

Step 6 — Apply resource constraints:
  quantity = _apply_constraints(bid_price, quantity)

Step 7 — Determine action:
  IF quantity > 0: action = "buy"
  ELIF quantity < 0: action = "sell"
  ELSE: action = "hold"

Step 8 — Execute trade:
  IF quantity > 0: cash -= quantity * bid_price; position += quantity
  ELIF quantity < 0: cash += abs(quantity) * bid_price; position += quantity
```

**State variables:**
- `position`: Running tally of net shares held (updated by `_execute_trade` post-decision).
- `cash`: Running cash balance (updated by `_execute_trade` post-decision).
- `price_history`: Append-only list of observed prices (maintained by base class, not consumed by decision logic).

**State evolution:**
- `price_history`: Updated pre-decide (during `perceive`).
- `position` and `cash`: Updated post-decide (during `_execute_trade`).

**Determinism contract:** Stochastic-given-seed. The Gaussian draw uses Python's `random.gauss()` seeded by the simulation's global RNG seed. Given identical seed and call sequence, outputs are reproducible.

**Parameter symbol table:**

| Symbol                    | Meaning                                    | Default Value | Source                      |
|---------------------------|--------------------------------------------|---------------|-----------------------------|
| `trade_frequency`         | Trade every N rounds                       | 5             | Black (1986)                |
| `noise_std`               | Standard deviation of random quantity      | 8.0           | simulation-bases.md §4.6    |
| `position_mean_reversion` | Mean-reversion coefficient toward zero     | 0.1           | simulation-bases.md §4.6    |
| `max_quantity`            | Hard clamp on absolute order size          | 15            | simulation-bases.md §4.6    |

#### Behavioral Properties

- Time horizon: Low-frequency — trades only every `trade_frequency` rounds (default: every 5th round); holds between trade rounds; no intraday or tick-level timing.
- Risk tolerance: Low — small position sizes hard-clamped at ±15 shares per round; mean-reversion ensures long-run position stays near zero.
- Information asymmetry: None — trades randomly without using any market information; completely uninformed about price, fundamental value, or peer behaviour.
- Psychological profile: Pure noise trader (Black 1986) — no biases exploited (no momentum-following, no anchoring, no disposition effect); randomness is the defining trait; weak mean-reversion represents only the mechanical desire to avoid unbounded position drift, not a strategic choice.

## Parameters

| Parameter                 | Type  | Default | Valid Range  | Sensitivity | Description                                         | Impact                                               | Source                        |
|---------------------------|-------|---------|--------------|-------------|-----------------------------------------------------|------------------------------------------------------|-------------------------------|
| `trade_frequency`         | int   | 5       | [1, 5]       | Medium      | Agent trades every N rounds; silent otherwise       | Higher → fewer active rounds, lower total volume     | Black (1986)                  |
| `noise_std`               | float | 8.0     | [1.0, 8.0]   | High        | Standard deviation of random quantity component     | Higher → wider distribution of order sizes           | simulation-bases.md §4.6      |
| `position_mean_reversion` | float | 0.1     | [0.05, 0.2]  | Medium      | Strength of position mean-reversion toward zero     | Higher → faster return to zero position, smaller drift | simulation-bases.md §4.6    |
| `max_quantity`            | int   | 15      | [5, 25]      | Low         | Hard clamp on absolute order size per round         | Higher → allows larger individual orders             | Position-limit convention     |

## Worked Numerical Examples

### Case 1 — Trade round with positive random draw

System state: `round_num` = 10, `trade_frequency` = 5, `position` = 0.0, `noise_std` = 8.0, `position_mean_reversion` = 0.1, `price` = 95.0, random draw = +6.5

Calculation:
- Trade frequency gate: 10 % 5 == 0 → active round
- `random_trade` = 6.5 (from gauss(0, 8.0))
- `reversion` = -0.1 × 0.0 = 0.0
- `raw_quantity` = 6.5 + 0.0 = 6.5
- `quantity` = clamp(6.5, -15, 15) = 6.5

Decision: buy 6.5 shares at bid_price = 95.0
State update: `cash`: 10000.0 → 10000.0 - 6.5 × 95.0 = 9382.5; `position`: 0.0 → 6.5

### Case 2 — Trade round with negative draw and position reversion

System state: `round_num` = 15, `trade_frequency` = 5, `position` = 10.0, `noise_std` = 8.0, `position_mean_reversion` = 0.1, `price` = 92.0, random draw = -3.0

Calculation:
- Trade frequency gate: 15 % 5 == 0 → active round
- `random_trade` = -3.0
- `reversion` = -0.1 × 10.0 = -1.0
- `raw_quantity` = -3.0 + (-1.0) = -4.0
- `quantity` = clamp(-4.0, -15, 15) = -4.0

Decision: sell 4.0 shares at bid_price = 92.0
State update: `cash` += 4.0 × 92.0 = +368.0; `position`: 10.0 → 6.0

### Case 3 — Non-trade round (silent)

System state: `round_num` = 12, `trade_frequency` = 5, `position` = 6.0, `price` = 93.0

Calculation:
- Trade frequency gate: 12 % 5 == 2 (not 0) → silent round
- `quantity` = 0.0, `bid_price` = 0.0

Decision: hold
State update: No change

### Edge Case — Large position triggers strong mean-reversion

System state: `round_num` = 20, `trade_frequency` = 5, `position` = 14.0, `noise_std` = 8.0, `position_mean_reversion` = 0.1, `price` = 90.0, random draw = +2.0

Calculation:
- Trade frequency gate: 20 % 5 == 0 → active round
- `random_trade` = 2.0
- `reversion` = -0.1 × 14.0 = -1.4
- `raw_quantity` = 2.0 + (-1.4) = 0.6
- `quantity` = clamp(0.6, -15, 15) = 0.6

Decision: buy 0.6 shares at bid_price = 90.0 (even with positive random draw, mean-reversion partially offsets, keeping quantity small)
State update: `position`: 14.0 → 14.6; `cash` -= 0.6 × 90.0

## Behavioral Verification and Calibration

**Verification criteria:**
1. On non-trade rounds (round_num % trade_frequency != 0), the agent MUST emit quantity = 0.
2. Over a long simulation (200+ rounds), the agent's average net position MUST be approximately zero (within ±2 × noise_std / position_mean_reversion).
3. The agent's order direction over 100+ trade rounds MUST show no statistically significant correlation with the price trend (|r| < 0.15).
4. The agent MUST never emit |quantity| > 15.
5. The agent's `provides_liquidity` flag MUST always be `False`.
6. Given identical simulation seed, the agent MUST produce identical outputs across reruns (stochastic reproducibility).

**Calibration procedure:**
- Set `trade_frequency` = 5, `noise_std` = 8.0, `position_mean_reversion` = 0.1.
- Run 200-round simulation. Verify agent's total volume is <5% of total market volume.
- Verify order direction is uncorrelated with price movements (run correlation test, expect |r| < 0.1).
- Verify position stays bounded: mean ≈ 0, std ≈ noise_std / sqrt(2 × position_mean_reversion × trade_frequency).

**Ablation Hooks:**

| Ablation name         | Setting                        | Hypothesis tested                                       | Expected direction                      | Metric                   |
|-----------------------|--------------------------------|---------------------------------------------------------|-----------------------------------------|--------------------------|
| `disable_retail`      | `noise_std = 0`                | Noise traders provide necessary background volume       | Market volume drops on non-crash rounds | `avg_volume_calm_period` |
| `frequent_retail`     | `trade_frequency = 1`          | More frequent noise increases realistic volume          | Higher background volume                | `total_volume`           |
| `no_reversion`        | `position_mean_reversion = 0`  | Mean-reversion prevents position drift                  | Position drifts randomly without bound  | `max_abs_position`       |

## Academic References

| # | Citation                                                                                                                                                        | Notes                                        |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------|
| 1 | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 528–543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                                              | Primary theory; noise traders in markets     |
| 2 | Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. *Journal of Finance*, 55(2), 773–806. https://doi.org/10.1111/0022-1082.00226           | Empirical evidence of retail noise trading   |
| 3 | Kirilenko, A. A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). The Flash Crash: High-frequency trading in an electronic market. *Journal of Finance*, 72(3), 967–998. https://doi.org/10.1111/jofi.12498 | Flash crash context; retail vs. institutional volume |

## Design Provenance

| Field       | Content                                                     |
|-------------|-------------------------------------------------------------|
| Author      | polish-simulation-pipeline                                  |
| Created     | 2026-07-11                                                  |
| Version     | 1.0.0                                                       |
| Status      | canonical                                                   |
| Icon        | ![](../agent_images/icons/finance-retail-trader.png)        |
