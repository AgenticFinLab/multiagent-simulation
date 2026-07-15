# Fundamentalist

## Summary

| Field                 | Content                                                                                                                              |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Value-contrarian fundamentalist investor                                                                                             |
| Theory Family         | Heterogeneous Agent Models (HAM)                                                                                                     |
| Behavioral Tendency   | **Converging — trades toward perceived fundamental value, providing stabilising mean-reversion pressure against speculative excess** |
| Market Role           | **Stabilising** - anchors price near fundamental value and dampens trend-following bubbles                                           |
| Time Horizon          | medium                                                                                                                               |
| Risk Tolerance        | moderate                                                                                                                             |
| Information Asymmetry | partial (noisy fundamental estimate)                                                                                                 |
| Determinism           | stochastic-given-seed                                                                                                                |

## Definition and Goals

This agent models a fundamentalist investor who believes prices revert to an intrinsic value. The real-world counterpart is a value fund, contrarian allocator, or long-horizon institutional investor who enters positions when price deviates materially from estimated worth.

The decision goal is to buy when price is below estimated fundamental value and sell when above, with order size proportional to the perceived mispricing. It trades infrequently (every `trade_frequency` ticks) and carries estimation noise, reflecting imperfect information about true value.

In simulation this agent provides a stabilising mean-reversion force that counteracts momentum traders and noise traders, preventing unbounded drift and anchoring prices near the rational-expectations equilibrium. Non-goals: it must not chase trends, trade every tick, or respond to volatility regimes.

## Theoretical Foundation

**Heterogeneous Agent Models (HAM)**:
- Theory / Study: Fundamentalist-chartist interaction and complex price dynamics.
- Citation: Brock, W. A. & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8-9), 1235-1274. https://doi.org/10.1016/S0165-1889(98)00011-6
- Core Insight: Markets contain fundamentalists who push price toward value and chartists who amplify deviations. The interaction generates complex price dynamics including bubbles and crashes.
- Mathematical Formulation: Fundamentalist demand is proportional to `(V - P)/P` where V is perceived value and P is market price.
- Empirical Evidence: Heterogeneous-agent models reproduce excess volatility, fat tails, and volatility clustering observed in real markets.
- Relevance to This Agent: The agent implements the fundamentalist belief type from Brock-Hommes, providing the stabilising anchor in a heterogeneous population.
- Calibration Source: Brock & Hommes (1998), Table 1 parameter sets.
- Falsification Conditions: If the agent's orders correlate positively with momentum rather than negatively with value deviation, it is misspecified.
- Alternative Theories: Rational expectations with homogeneous agents; adaptive market hypothesis.

**Noise Trader Risk**:
- Theory / Study: Limits to arbitrage in the presence of uninformed traders.
- Citation: De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703-738. https://doi.org/10.1086/261703
- Core Insight: Fundamentalists face noise-trader risk when exploiting mispricings, justifying conservative position sizing and imperfect information about true value.
- Mathematical Formulation: Arbitrageur demand is bounded by noise-trader variance.
- Empirical Evidence: Value strategies exhibit long drawdowns consistent with noise-trader risk.
- Relevance to This Agent: The value_noise_std parameter and position clamping reflect the limits on fundamentalist aggression under noise-trader uncertainty.
- Calibration Source: De Long et al. (1990), equilibrium model.
- Falsification Conditions: If the agent sizes positions without any uncertainty or constraint, it ignores noise-trader risk.
- Alternative Theories: Efficient markets with no arbitrage limits.

## Design Purpose and Activation Triggers

Purpose: Supply mean-reverting demand that anchors prices near fundamental value and dampens speculative bubbles, preventing unbounded momentum-driven price drift.

Call Frequency: every `trade_frequency` ticks (default 3; low frequency).

Prerequisite Signals:
- `price` available from market broadcast
- `fundamental` available from market broadcast
- Round number available for frequency gating

Missing-Signal Policy: hold if price or fundamental estimate is unavailable in the market_data payload.

Activation Triggers:
- `round_num % trade_frequency == 0`: compute deviation and submit order.
- `round_num % trade_frequency != 0`: hold with zero quantity and zero bid_price.
- `<Default>`: hold.

Deactivation Conditions:
- Cash insufficient for buy: quantity constrained to `cash / bid_price`.
- Position insufficient for sell: quantity constrained to `-position`.
- Quantity rounds to zero after clamping: effective hold.

Behavioral Adaptation by Condition:
| Condition               | Behavioral change                                        | Mechanism                                                           |
|-------------------------|----------------------------------------------------------|---------------------------------------------------------------------|
| High volatility regime  | No adaptation; agent ignores volatility state            | Decision uses only fundamental deviation, not volatility            |
| Large positive deviation| Larger buy orders, capped at +20                         | Sizing is proportional to deviation, clamped at boundary            |
| Cash depletion          | Buy orders scaled down to affordable quantity            | `min(quantity, cash / bid_price)` constraint in `_apply_constraints`|

Environmental Dependencies: Requires `market_data` broadcast containing `price` and `fundamental` fields. Uses `HistoryBuffer` for price and volatility tracking via `BaseInvestor.perceive()`.

Market Contribution by Regime:
| Regime | Contribution  | Mechanism                                                   |
|--------|---------------|-------------------------------------------------------------|
| Calm   | Stabilising   | Supplies mean-reverting demand when small deviations exist. |
| Stress | Stabilising   | Buys into crashes, sells into bubbles (contrarian).         |

Interaction with other agents: Opposes TrendFollower and NoiseTrader; complements SlowAdapter in providing value-convergent demand. Peak single-round demand is bounded at 20 units, insufficient to single-handedly reverse momentum but sufficient to slow it.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source          | Type / Shape   | Required? | Notes                                                                                       |
|------------------------|-----------------|----------------|-----------|---------------------------------------------------------------------------------------------|
| `price`                | market_data     | `float`        | yes       | Current market price from market broadcast.                                                 |
| `fundamental`          | market_data     | `float`        | yes       | Fundamental value from market coordinator.                                                  |
| `round_num`            | observation     | `int`          | yes       | Current simulation round for frequency gating.                                              |
| `identity`, `round`    | round header    | `str`, `int`   | yes       | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum              | Unit     | Required?   | Meaning                                                                   |
|---------------|--------|---------------------------------|----------|-------------|---------------------------------------------------------------------------|
| `action`      | enum   | {"buy", "sell", "hold"}         | —        | yes         | Discrete action selected this call.                                       |
| `quantity`    | float  | `[0, 20]`                       | shares   | conditional | Order magnitude; 0 when `action = hold`.                                  |
| `price_level` | float  | `= price` (market order)        | currency | conditional | Execution reference; equals observed `price` for market orders.           |
| `reasoning`   | string | 1-3 sentences                   | —        | yes         | Audit trail explaining WHY the action was chosen.                         |

##### Content Constraints

- Required fields: every row marked `Required? = yes` in the Outputs table MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, 20]`; out-of-range values MUST be clamped by the implementer before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. `price_level` uses the same currency unit as `price`.
- Determinism markers: the decision determinism class is declared in Summary as `stochastic-given-seed`; the stochastic element is the Gaussian noise draw on fundamental estimate.

##### Serialization Format

    <analysis>...free-form reasoning, 1-3 sentences...</analysis>
    <decision>{"action": "<one of the declared enum values>",
                "quantity": <float>,
                "price_level": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel for `retrieved_knowledge` (e.g. `"(No relevant knowledge retrieved this round.)"`) and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal         | Type       | Memory Window | Rationale                                          |
|----------------|------------|---------------|----------------------------------------------------|
| `price`        | Continuous | 1 tick        | Current market price for deviation computation     |
| `fundamental`  | Continuous | 1 tick        | True fundamental value broadcast by market         |
| `round_num`    | Discrete   | 1 tick        | Frequency gating via modulo operation              |

Does NOT use: `momentum`, `trend`, `volatility`, peer positions, cost basis, bid-ask depth.

#### Core Behavioral Mechanism

1. Check if current round is a trading round: `round_num % trade_frequency == 0`.
2. If not a trading round, hold with zero quantity.
3. Estimate value with noise: `estimated_value = fundamental + N(0, value_noise_std)`.
4. Compute normalised deviation: `deviation = (estimated_value - price) / price`.
5. Compute raw quantity: `quantity = value_sensitivity * deviation * base_position_size`.
6. Clamp quantity to `[-20, +20]`.
7. Set `bid_price = price` (market order approximation).
8. Apply cash constraint: `quantity = min(quantity, cash / bid_price)` for buys.
9. Apply position constraint: `quantity = max(quantity, -position)` for sells.
10. Execute trade: update `cash` and `position` in state.
11. Emit order payload with `bid_price`, `quantity`, and `strategy` fields.

#### Action Space

| Aspect                | Specification                                                             |
|-----------------------|---------------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                        |
| Price level rule      | market order at current price                                             |
| Order quantity rule   | `Q = clamp(value_sensitivity * deviation * base_position_size, -20, +20)` |
| Order lifetime        | 1 tick (consumed by market coordinator in same round)                     |
| Cancellation policy   | unfilled orders expire at end of round                                    |
| Inventory constraint  | cannot sell below position = 0; cannot buy beyond cash / price            |
| Wealth / leverage cap | cash >= 0; no margin; no short selling                                    |
| Stop-loss / kill rule | none                                                                      |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Trigger function:
  ```
  if round_num % trade_frequency != 0:
      Q*(t) = 0  (hold)
  ```
- Value estimation:
  ```
  estimated_value = F + epsilon,  epsilon ~ N(0, sigma_val)
  ```
- Deviation signal:
  ```
  deviation = (estimated_value - P) / P
  ```
- Sizing function:
  ```
  Q_raw = s_val * deviation * Q_base
  Q*(t) = clamp(Q_raw, -20, +20)
  ```
- State variables: `cash`; `position`; `price_history`; `volatility_history`.
- State-update rule: update position and cash post-fill via `_execute_trade`.
- Determinism contract: stochastic-given-seed due to `random.gauss(0, value_noise_std)`.

| Symbol      | Meaning                    | Default Value | Source                         |
|-------------|----------------------------|---------------|--------------------------------|
| `F`         | fundamental value          | market-given  | Market coordinator broadcast   |
| `P`         | current price              | market-given  | Market coordinator broadcast   |
| `sigma_val` | value estimation noise std | 2.0           | Brock & Hommes (1998)          |
| `s_val`     | value sensitivity          | 0.5           | Brock & Hommes (1998)          |
| `Q_base`    | base position size         | 20.0          | Calibration                    |
| `f_trade`   | trade frequency            | 3             | Brock & Hommes (1998)          |

#### Behavioral Properties

- Time horizon: medium, because it trades infrequently and holds positions through multi-tick deviations.
- Risk tolerance: moderate, because it uses conservative position sizing with strict clamp bounds.
- Information asymmetry: partial, because it observes the true fundamental but adds estimation noise.
- Psychological profile: patient value investor with contrarian conviction; tolerates short-term losses while waiting for mean reversion.

## Parameters

| Parameter            | Type  | Default  | Valid Range | Sensitivity | Description                                            | Impact                                                          | Source                                           |
|----------------------|-------|----------|-------------|-------------|--------------------------------------------------------|-----------------------------------------------------------------|--------------------------------------------------|
| `trade_frequency`    | int   | 3        | >= 1        | medium      | Trade every N rounds; controls participation rate.     | Higher -> fewer trades, weaker stabilisation per unit time.     | Brock & Hommes (1998), 10.1016/S0165-1889(98)00011-6 |
| `value_sensitivity`  | float | 0.5      | (0, 5]      | high        | Responsiveness to value deviation signal.              | Higher -> larger orders per unit deviation.                     | Brock & Hommes (1998), 10.1016/S0165-1889(98)00011-6 |
| `base_position_size` | float | 20.0     | > 0         | high        | Base scaling factor for order size computation.        | Higher -> stronger market impact per active round.              | Calibrated for meaningful net demand             |
| `value_noise_std`    | float | 2.0      | >= 0        | medium      | Std dev of Gaussian noise added to fundamental estimate.| Higher -> noisier estimates, weaker convergence to true value. | Estimation uncertainty literature                |
| `initial_cash`       | float | 10000.0  | > 0         | low         | Starting cash endowment for the agent.                 | Higher -> can sustain larger cumulative positions.              | Normalization (scenario default)                 |
| `initial_position`   | int   | 0        | >= 0        | low         | Starting inventory of the risky asset.                 | Non-zero -> agent begins with exposure.                        | Normalization (scenario default)                 |

## Population and Heterogeneity

| Aspect                         | Specification                                                     |
|--------------------------------|-------------------------------------------------------------------|
| Default population size        | 2                                                                 |
| Parameter heterogeneity policy | Stochastic value noise creates per-instance divergence            |
| Heterogeneity per parameter    | `value_noise_std` draws create unique estimated values per round  |
| Cross-agent correlation        | Independent noise draws; no shared random state                   |
| Identity persistence           | Fixed parameters for episode duration; noise redrawn each round   |

Population rationale: Two instances provide double the stabilising demand without overwhelming destabilising agents. The stochastic noise (`value_noise_std`) ensures that even identically parameterised instances compute different estimated values each active round, preventing perfectly correlated orders.

## Worked Numerical Examples

### Case 1 - Buy on undervaluation
```text
State: round=3, price=100.0, fundamental=105.0, noise_draw=+1.0.
Frequency gate: 3 % 3 == 0 -> active.
estimated_value = 105.0 + 1.0 = 106.0.
deviation = (106.0 - 100.0) / 100.0 = 0.06.
quantity = 0.5 * 0.06 * 20.0 = 0.60.
Clamp check: 0.60 in [-20, 20] -> passes.
bid_price = 100.0.
Cash constraint: cash=10000, max_affordable=100.0 -> 0.60 <= 100.0, passes.
Decision: buy 0.60 units at price 100.0.
State update: cash -= 60.0, position += 0.60.
```

### Case 2 - Sell on overvaluation
```text
State: round=6, price=110.0, fundamental=100.0, noise_draw=-0.5.
Frequency gate: 6 % 3 == 0 -> active.
estimated_value = 100.0 + (-0.5) = 99.5.
deviation = (99.5 - 110.0) / 110.0 = -0.0955.
quantity = 0.5 * (-0.0955) * 20.0 = -0.955.
Clamp check: -0.955 in [-20, 20] -> passes.
bid_price = 110.0.
Position constraint: position=5, max_sellable=5 -> abs(-0.955) <= 5, passes.
Decision: sell 0.955 units at price 110.0.
State update: cash += 105.0, position -= 0.955.
```

### Case 3 - Large deviation with clamping
```text
State: round=9, price=50.0, fundamental=100.0, noise_draw=+3.0.
Frequency gate: 9 % 3 == 0 -> active.
estimated_value = 100.0 + 3.0 = 103.0.
deviation = (103.0 - 50.0) / 50.0 = 1.06.
quantity = 0.5 * 1.06 * 20.0 = 10.6.
Clamp check: 10.6 in [-20, 20] -> passes (no clamp needed).
bid_price = 50.0.
Cash constraint: cash=10000, max_affordable=200.0 -> 10.6 <= 200.0, passes.
Decision: buy 10.6 units at price 50.0.
State update: cash -= 530.0, position += 10.6.
```

### Edge Case - Non-trading round (hold)
```text
State: round=4, trade_frequency=3.
Frequency gate: 4 % 3 = 1 != 0 -> inactive.
Decision: hold (quantity=0.0, bid_price=0.0).
State update: no change to cash or position.
```

### Edge Case - Cash constraint binds
```text
State: round=12, price=100.0, fundamental=120.0, noise_draw=0.0, cash=5.0.
estimated_value = 120.0.
deviation = (120.0 - 100.0) / 100.0 = 0.20.
quantity_raw = 0.5 * 0.20 * 20.0 = 2.0.
bid_price = 100.0.
Cash constraint: max_affordable = 5.0 / 100.0 = 0.05.
quantity = min(2.0, 0.05) = 0.05.
Decision: buy 0.05 units at price 100.0.
State update: cash -= 5.0, position += 0.05.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `trade_frequency` <- Brock & Hommes (1998) heterogeneous-agent calibration; low-frequency trading in value strategies.
- `value_sensitivity` <- Brock & Hommes (1998) Table 1 parameter ranges for fundamentalist responsiveness.
- `base_position_size` <- scenario-level calibration ensuring meaningful net demand without dominance.
- `value_noise_std` <- estimation uncertainty consistent with information asymmetry literature.

**Expected stylized facts** when this agent is present:
- Price mean-reverts toward fundamental over medium horizon.
- Reduces excess volatility relative to noise-only or momentum-only populations.
- Order flow negatively correlated with recent price deviation from fundamental value.
- Peak single-round demand bounded at 20 units; sufficient to slow momentum but not reverse it alone.

**Sanity bounds (red flags during simulation)**:
- IF orders correlate positively with momentum THEN the value-deviation signal is inverted because fundamentalists must be contrarian.
- IF average position size exceeds 20 THEN the clamp logic is broken because all quantities must be bounded by [-20, +20].
- IF the agent trades on non-trading rounds (round_num % trade_frequency != 0) THEN the frequency gate is bypassed because the modulo check must suppress action.
- IF estimated_value equals fundamental exactly every round THEN the noise injection is absent because Gaussian noise must be applied.

#### Ablation Hooks

| Ablation name        | Setting                    | Hypothesis tested                                          |
|----------------------|----------------------------|------------------------------------------------------------|
| `no_fundamentalist`  | population = 0             | Removing value traders leads to persistent mispricing      |
| `perfect_info`       | `value_noise_std = 0`      | Perfect information speeds convergence to fundamental      |
| `high_frequency`     | `trade_frequency = 1`      | Frequent fundamentalist trading eliminates momentum profit |
| `aggressive_sizing`  | `value_sensitivity = 2.0`  | Stronger value demand dampens volatility clustering        |

## Academic References

| # | Citation                                                                                                                                                                                            | Notes                                                                        |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| 1 | Brock, W. A. & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8-9), 1235-1274. https://doi.org/10.1016/S0165-1889(98)00011-6 | Primary HAM framework; fundamentalist demand specification                   |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703-738. https://doi.org/10.1086/261703     | Limits to arbitrage justifying conservative sizing and noise in estimation    |
| 3 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                                                                                                                                   | Foundational value-investing philosophy motivating contrarian behavior        |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 2.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-fundamentalist.png) |
