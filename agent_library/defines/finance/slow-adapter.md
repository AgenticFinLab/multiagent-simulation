# Slow Adapter

## Summary

| Field                 | Content                                                                                                                                              |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Conservative institutional slow-adapter investor                                                                                                     |
| Theory Family         | Heterogeneous Agent Models (HAM) / Bounded Rationality                                                                                               |
| Behavioral Tendency   | **Converging — trades toward a sluggishly-updated perceived value, contributing delayed stabilisation and extending volatility cluster duration**    |
| Market Role           | **Stabilising (delayed)** - provides inertial mean-reversion demand that lags information shocks by multiple rounds                                  |
| Time Horizon          | long                                                                                                                                                 |
| Risk Tolerance        | low                                                                                                                                                  |
| Information Asymmetry | high (slow information processing, stale beliefs)                                                                                                    |
| Determinism           | deterministic                                                                                                                                        |

## Definition and Goals

This agent models a slow-moving institutional investor (pension fund, insurance company) that updates beliefs about fair value with a significant lag. It blends the current fundamental signal with a long moving average of prices, weighting new information lightly via an exponential-smoothing-style rule.

The decision goal is to trade toward a perceived value that updates sluggishly, creating delayed demand responses to information shocks. This reflects real-world mandate constraints, committee-based decision-making, regulatory reporting lags, and quarterly rebalancing cycles.

In simulation this agent contributes to price stickiness, delayed overshooting, and predictable flows that faster agents can front-run. It extends volatility clustering duration beyond what the GARCH mechanism alone produces. Non-goals: it must not react instantly to new information, trade at high frequency, or respond to volatility regimes.

## Theoretical Foundation

**Heterogeneous Agent Models (HAM)**:
- Theory / Study: Adaptive belief formation with heterogeneous updating speeds.
- Citation: Brock, W. A. & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8-9), 1235-1274. https://doi.org/10.1016/S0165-1889(98)00011-6
- Core Insight: Agents using different belief-updating speeds create endogenous market dynamics. Slow adapters stabilise in the long run but create exploitable predictability in the short run.
- Mathematical Formulation: Perceived value is a convex combination of fundamental and historical average: `V_perceived = w * F + (1 - w) * MA`.
- Empirical Evidence: Heterogeneous-agent models with mixed updating speeds reproduce autocorrelation in order flow and persistent price deviations.
- Relevance to This Agent: The agent implements a slow-updating belief rule that blends fundamental information with historical price averages using a low update weight.
- Calibration Source: Brock & Hommes (1998); adaptive expectations calibration.
- Falsification Conditions: If the agent's perceived value tracks the fundamental instantly (update_weight near 1), it is misspecified as a fundamentalist rather than a slow adapter.
- Alternative Theories: Rational inattention; sticky information models.

**Adaptive Expectations and Bounded Rationality**:
- Theory / Study: Heterogeneous agent models with bounded rationality.
- Citation: Hommes, C. H. (2006). Heterogeneous agent models in economics and finance. In L. Tesfatsion & K. L. Judd (Eds.), *Handbook of Computational Economics*, Vol. 2, 1109-1186. Elsevier.
- Core Insight: Bounded rationality and adaptive expectations lead to systematic lags in belief formation. Agents who update slowly create persistent forecast errors under regime shifts and extend the autocorrelation of market dynamics.
- Mathematical Formulation: `V_t = alpha * F_t + (1 - alpha) * V_{t-1}` where alpha is low.
- Empirical Evidence: Institutional investor flows show multi-quarter adjustment lags to macro shocks.
- Relevance to This Agent: The `update_weight` parameter directly controls the speed of belief adaptation; low values create the institutional inertia observed in pension and insurance mandates.
- Calibration Source: Hommes (2006); Greenwood & Hanson (2015) for institutional flow persistence.
- Falsification Conditions: If agent orders respond to shocks within 1-2 rounds, the delay mechanism is absent.
- Alternative Theories: Full Bayesian updating with costly attention.

**Institutional Flow Persistence**:
- Theory / Study: Waves in investment driven by slow-moving capital.
- Citation: Greenwood, R. & Hanson, S. G. (2015). Waves in ship prices and investment. *Quarterly Journal of Economics*, 130(1), 55-109. https://doi.org/10.1093/qje/qju035
- Core Insight: Slow-moving institutional capital creates predictable waves in asset prices that persist far beyond initial shocks, consistent with the delayed demand pattern this agent produces.
- Relevance to This Agent: Validates the multi-round persistence of orders following a single fundamental shift.
- Calibration Source: Greenwood & Hanson (2015) adjustment speed estimates.
- Falsification Conditions: If the agent fully adjusts within one round, it does not generate wave-like flow patterns.

## Design Purpose and Activation Triggers

Purpose: Introduce institutional inertia and delayed response to fundamental shifts, creating predictable flow patterns, price stickiness, and extended volatility cluster duration.

Call Frequency: every tick (but effective trading is conditional on deviation magnitude).

Prerequisite Signals:
- `price` available from market broadcast
- `fundamental` (F) available from market broadcast
- `price_history` of length >= `lookback_window` for moving average computation

Missing-Signal Policy: hold if fundamental or sufficient price history is unavailable. When `len(price_history) < lookback_window`, use current price as the moving average proxy (graceful degradation).

Activation Triggers:
- `len(price_history) >= lookback_window` AND `abs(deviation) > 0.02`: compute perceived value and submit order.
- `abs(deviation) <= 0.02`: hold (signal too weak for conservative mandate).
- `<Default>`: hold.

Deactivation Conditions:
- Insufficient price history (first ticks before lookback window fills).
- Cash or position constraints binding.
- Deviation below materiality threshold (0.02).

Behavioral Adaptation by Condition:
| Condition               | Behavioral change                                            | Mechanism                                                                |
|-------------------------|--------------------------------------------------------------|--------------------------------------------------------------------------|
| High volatility regime  | No adaptation; agent ignores volatility state                | Decision uses only blended perceived value, not volatility signal         |
| Fundamental regime shift| Slow response over many rounds as MA catches up              | Low `update_weight` keeps MA dominant in perceived value for many rounds  |
| Price mean-reverting    | Orders diminish as deviation shrinks toward zero             | Sizing is proportional to deviation; small deviation -> near-zero orders  |

Environmental Dependencies: Requires `market_data` broadcast containing `price` and `fundamental` fields. Uses `HistoryBuffer` for price tracking via `BaseInvestor.perceive()`.

Market Contribution by Regime:
| Regime | Contribution       | Mechanism                                                               |
|--------|---------------------|-------------------------------------------------------------------------|
| Calm   | Neutral to mild     | Small deviations produce near-zero orders; effectively dormant.         |
| Stress | Persistence-adding  | Delayed response extends demand in one direction for multiple rounds.   |

Interaction with other agents: Complements Fundamentalist (both mean-revert) but with much longer time constant. Provides predictable flow that TrendFollower can partially front-run. Does not directly oppose or amplify VolatilityTrader.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source          | Type / Shape     | Required? | Notes                                                                                       |
|------------------------|-----------------|------------------|-----------|---------------------------------------------------------------------------------------------|
| `price`                | market_data     | `float`          | yes       | Current market price from market broadcast.                                                 |
| `fundamental`          | market_data     | `float`          | yes       | Fundamental value from market coordinator.                                                  |
| `price_history`        | agent state     | `HistoryBuffer`  | yes       | Rolling price history for moving average computation.                                       |
| `round_num`            | observation     | `int`            | yes       | Current simulation round.                                                                   |
| `identity`, `round`    | round header    | `str`, `int`     | yes       | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum              | Unit     | Required?   | Meaning                                                                   |
|---------------|--------|---------------------------------|----------|-------------|---------------------------------------------------------------------------|
| `action`      | enum   | {"buy", "sell", "hold"}         | —        | yes         | Discrete action selected this call.                                       |
| `quantity`    | float  | `[0, 10]`                       | shares   | conditional | Order magnitude; 0 when `action = hold`.                                  |
| `price_level` | float  | `= price` (market order)        | currency | conditional | Execution reference; equals observed `price` for market orders.           |
| `reasoning`   | string | 1-3 sentences                   | —        | yes         | Audit trail explaining WHY the action was chosen.                         |

##### Content Constraints

- Required fields: every row marked `Required? = yes` in the Outputs table MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, 10]`; out-of-range values MUST be clamped by the implementer before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. `price_level` uses the same currency unit as `price`.
- Determinism markers: the decision determinism class is declared in Summary as `deterministic`; no stochastic element exists in the decision logic.

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

| Signal          | Type       | Memory Window          | Rationale                                          |
|-----------------|------------|------------------------|----------------------------------------------------|
| `price`         | Continuous | 1 tick                 | Current price for deviation computation            |
| `fundamental`   | Continuous | 1 tick                 | True fundamental value from market broadcast       |
| `price_history` | Array      | `lookback_window` ticks| Compute moving average for blended value estimate  |

Does NOT use: `momentum`, `volatility`, `trend_signal`, peer positions, cost basis.

#### Core Behavioral Mechanism

1. Retrieve price history from agent state (`HistoryBuffer`).
2. Check if sufficient history exists: `len(price_history) >= lookback_window`.
3. If insufficient history, set `long_ma = price` (graceful degradation).
4. Otherwise compute moving average: `long_ma = mean(price_history[-lookback_window:])`.
5. Compute blended perceived value: `perceived_value = update_weight * fundamental + (1 - update_weight) * long_ma`.
6. Compute normalised deviation: `deviation = (perceived_value - price) / price`.
7. Apply materiality filter: if `abs(deviation) <= 0.02`, hold with zero quantity.
8. Compute quantity: `quantity = base_position_size * deviation`.
9. Clamp quantity to `[-10, +10]` (conservative institutional mandate).
10. Set `bid_price = price` (market order approximation).
11. Apply cash constraint for buys; apply position constraint for sells.
12. Execute trade: update `cash` and `position` in state.
13. Emit order payload with `bid_price`, `quantity`, and `strategy` fields.

#### Action Space

| Aspect                | Specification                                                             |
|-----------------------|---------------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                        |
| Price level rule      | market order at current price                                             |
| Order quantity rule   | `Q = clamp(base_position_size * deviation, -10, +10)` when material      |
| Order lifetime        | 1 tick (consumed by market coordinator in same round)                     |
| Cancellation policy   | unfilled orders expire at end of round                                    |
| Inventory constraint  | cannot sell below position = 0; cannot buy beyond cash / price            |
| Wealth / leverage cap | cash >= 0; no margin; no short selling                                    |
| Stop-loss / kill rule | none                                                                      |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Moving average:
  ```
  MA_t = (1/L) * sum(P_{t-L+1}, ..., P_t)
  ```
- Perceived value (exponential-smoothing style blend):
  ```
  V_perceived_t = w * F_t + (1 - w) * MA_t
  ```
- Deviation signal:
  ```
  deviation = (V_perceived_t - P_t) / P_t
  ```
- Sizing function with materiality gate:
  ```
  if abs(deviation) > 0.02:
      Q*(t) = clamp(Q_base * deviation, -10, +10)
  else:
      Q*(t) = 0  (hold)
  ```
- State variables: `cash`; `position`; `price_history` (HistoryBuffer); `volatility_history`.
- State-update rule: update position and cash post-fill via `_execute_trade`.
- Determinism contract: deterministic given price history and parameters.

| Symbol       | Meaning                         | Default Value | Source                         |
|--------------|---------------------------------|---------------|--------------------------------|
| `F`          | fundamental value               | market-given  | Market coordinator broadcast   |
| `P`          | current price                   | market-given  | Market coordinator broadcast   |
| `w`          | update weight on fundamental    | 0.1           | Adaptive expectations lit.     |
| `L`          | lookback window for MA          | 10            | Brock & Hommes (1998)          |
| `Q_base`     | base position size              | 10.0          | Calibration                    |
| `theta_mat`  | materiality threshold           | 0.02          | Institutional trading practice |

#### Behavioral Properties

- Time horizon: long, because the low update weight causes beliefs to lag market by many rounds.
- Risk tolerance: low, because it uses conservative position sizing with tight clamp bounds and a materiality filter.
- Information asymmetry: high, because it systematically underweights new information relative to stale moving-average data.
- Psychological profile: patient institutional mandate with committee-style inertia; prefers small positions and avoids frequent trading; tolerates persistent tracking error versus true fundamental.

## Parameters

| Parameter            | Type  | Default  | Valid Range | Sensitivity | Description                                                  | Impact                                                                    | Source                                                |
|----------------------|-------|----------|-------------|-------------|--------------------------------------------------------------|---------------------------------------------------------------------------|-------------------------------------------------------|
| `lookback_window`    | int   | 10       | >= 2        | high        | Window length for moving average price computation.          | Higher -> slower perceived value adaptation, longer clustering extension. | Brock & Hommes (1998), 10.1016/S0165-1889(98)00011-6 |
| `update_weight`      | float | 0.1      | (0, 1)      | high        | Weight on current fundamental in blended value estimate.     | Lower -> more inertia, stickier beliefs, longer adjustment lag.           | Adaptive expectations literature                      |
| `base_position_size` | float | 10.0     | > 0         | medium      | Base scaling factor for order size computation.              | Higher -> larger per-round demand, stronger delayed stabilisation.        | Calibrated for weak stabilisation                     |
| `initial_cash`       | float | 10000.0  | > 0         | low         | Starting cash endowment for the agent.                       | Higher -> can sustain larger cumulative positions over time.              | Normalization (scenario default)                      |
| `initial_position`   | int   | 0        | >= 0        | low         | Starting inventory of the risky asset.                       | Non-zero -> agent begins with exposure bias.                             | Normalization (scenario default)                      |

## Population and Heterogeneity

| Aspect                         | Specification                                                  |
|--------------------------------|----------------------------------------------------------------|
| Default population size        | 1                                                              |
| Parameter heterogeneity policy | Single canonical instance                                      |
| Heterogeneity per parameter    | N/A at population = 1                                          |
| Cross-agent correlation        | N/A                                                            |
| Identity persistence           | Fixed parameters for episode duration                          |

Population rationale: One instance is sufficient to extend clustering duration without dominating the system. The slow adapter's contribution is persistent but small in magnitude per round; adding more instances would create excessive stabilisation that offsets the trend-follower amplification needed for the volatility-clustering phenomenon.

## Worked Numerical Examples

### Case 1 - Sluggish buy after fundamental jump (signal too weak)
```text
State: price=100.0, fundamental=110.0, MA(10)=99.0, update_weight=0.1.
perceived_value = 0.1 * 110.0 + 0.9 * 99.0 = 11.0 + 89.1 = 100.1.
deviation = (100.1 - 100.0) / 100.0 = 0.001.
Materiality check: abs(0.001) = 0.001 <= 0.02 -> below threshold.
Decision: hold (signal too weak this tick).
State update: no change to cash or position.
```

### Case 2 - Accumulated signal produces buy trade
```text
State: price=95.0, fundamental=110.0, MA(10)=102.0, update_weight=0.1.
perceived_value = 0.1 * 110.0 + 0.9 * 102.0 = 11.0 + 91.8 = 102.8.
deviation = (102.8 - 95.0) / 95.0 = 0.082.
Materiality check: abs(0.082) = 0.082 > 0.02 -> passes threshold.
quantity = 10.0 * 0.082 = 0.82.
Clamp check: 0.82 in [-10, 10] -> passes.
bid_price = 95.0.
Cash constraint: cash=10000, max_affordable=105.3 -> 0.82 <= 105.3, passes.
Decision: buy 0.82 units at price 95.0.
State update: cash -= 77.9, position += 0.82.
```

### Case 3 - Sell when price overshoots perceived value
```text
State: price=115.0, fundamental=100.0, MA(10)=105.0, update_weight=0.1.
perceived_value = 0.1 * 100.0 + 0.9 * 105.0 = 10.0 + 94.5 = 104.5.
deviation = (104.5 - 115.0) / 115.0 = -0.091.
Materiality check: abs(-0.091) = 0.091 > 0.02 -> passes threshold.
quantity = 10.0 * (-0.091) = -0.91.
Clamp check: -0.91 in [-10, 10] -> passes.
bid_price = 115.0.
Position constraint: position=5, max_sellable=5 -> abs(-0.91) <= 5, passes.
Decision: sell 0.91 units at price 115.0.
State update: cash += 104.65, position -= 0.91.
```

### Edge Case - Insufficient history (graceful degradation)
```text
State: tick=5, lookback_window=10, price=100.0, fundamental=110.0.
Only 5 prices available in history; condition len(price_history) < lookback_window.
Fallback: long_ma = price = 100.0.
perceived_value = 0.1 * 110.0 + 0.9 * 100.0 = 11.0 + 90.0 = 101.0.
deviation = (101.0 - 100.0) / 100.0 = 0.01.
Materiality check: abs(0.01) = 0.01 <= 0.02 -> below threshold.
Decision: hold.
State update: no change.
```

### Edge Case - Large deviation with clamping
```text
State: price=70.0, fundamental=100.0, MA(10)=95.0, update_weight=0.1.
perceived_value = 0.1 * 100.0 + 0.9 * 95.0 = 10.0 + 85.5 = 95.5.
deviation = (95.5 - 70.0) / 70.0 = 0.364.
quantity_raw = 10.0 * 0.364 = 3.64.
Clamp check: 3.64 in [-10, 10] -> passes (no clamp needed).
Decision: buy 3.64 units at price 70.0.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `lookback_window` <- Brock & Hommes (1998) belief heterogeneity calibration; institutional rebalancing cycles.
- `update_weight` <- adaptive expectations literature; pension fund quarterly review cadence implies low weight on new information.
- `base_position_size` <- calibrated for weak per-round demand that accumulates persistence without dominating.

**Expected stylized facts** when this agent is present:
- Delayed price adjustment to fundamental shifts lasting multiple rounds beyond the initial shock.
- Predictable order flow that lags information by several ticks (exploitable by trend followers).
- Extended volatility clustering duration beyond what the GARCH mechanism alone produces.
- Reduced short-term volatility but longer adjustment arcs to new equilibria.

**Sanity bounds (red flags during simulation)**:
- IF agent tracks fundamental instantly (perceived value equals fundamental within 1 round) THEN the update weight is too high because slow adaptation requires low weight.
- IF position sizes exceed 10 THEN the clamp logic is broken because all quantities must be bounded by [-10, +10].
- IF agent trades before lookback window is filled AND deviation exceeds threshold THEN the graceful degradation is not correctly using current price as MA proxy.
- IF orders show zero autocorrelation after a shock THEN the persistence mechanism is absent because slow adaptation must produce multi-round order sequences.

#### Ablation Hooks

| Ablation name       | Setting                   | Hypothesis tested                                               |
|---------------------|---------------------------|-----------------------------------------------------------------|
| `no_slow_adapter`   | population = 0            | Removing slow adapter speeds price discovery and shortens vol clusters |
| `fast_adapter`      | `update_weight = 0.9`    | Higher weight makes agent behave like fundamentalist             |
| `very_slow`         | `update_weight = 0.01`   | Extremely slow adaptation creates multi-episode persistence      |
| `wide_window`       | `lookback_window = 50`   | Wider MA window further delays response to regime shifts         |

## Behavioral Verification and Calibration

- Given a sudden fundamental jump (F from 100 to 110), agent must NOT adjust perceived value to 110 within a single round; perceived value must lag by multiple rounds due to low `update_weight`.
- Given deviation from perceived value exceeds materiality threshold (abs > 0.02), agent must emit a trade with quantity proportional to deviation magnitude.
- Given deviation from perceived value is below materiality threshold (abs <= 0.02), agent must hold with zero quantity.
- Given insufficient price history (fewer than `lookback_window` observations), agent must use current price as the moving average proxy and still apply the materiality filter.
- Given position = 0 and a sell signal, agent must hold because short selling is not permitted.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_slow_adapter` | population = 0 | Removing slow adapter shortens volatility cluster duration | decrease | autocorrelation decay half-life of squared returns |
| `fast_adapter` | `update_weight = 0.9` | High update weight eliminates institutional lag, making agent behave like fundamentalist | decrease | number of rounds for perceived value to converge post-shock |

## Academic References

| # | Citation                                                                                                                                                                                                                          | Notes                                                               |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| 1 | Brock, W. A. & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8-9), 1235-1274. https://doi.org/10.1016/S0165-1889(98)00011-6   | Primary HAM framework; heterogeneous updating speeds                |
| 2 | Hommes, C. H. (2006). Heterogeneous agent models in economics and finance. In L. Tesfatsion & K. L. Judd (Eds.), *Handbook of Computational Economics*, Vol. 2, 1109-1186. Elsevier.                                            | Bounded rationality and adaptive expectations in financial markets  |
| 3 | Greenwood, R. & Hanson, S. G. (2015). Waves in ship prices and investment. *Quarterly Journal of Economics*, 130(1), 55-109. https://doi.org/10.1093/qje/qju035                                                                 | Institutional flow persistence and slow-moving capital waves        |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 2.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-slow-adapter.png) |
