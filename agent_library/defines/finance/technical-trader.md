# Moving-average crossover trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Moving-average crossover trader |
| Theory Family         | Technical Analysis / Market Microstructure |
| Behavioral Tendency   | **Diverging — reinforces existing price trends by generating continuation signals from moving-average crossovers; amplifies momentum away from fundamental value** |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a systematic technical trader who uses dual moving-average crossover signals to identify and ride price trends. The real-world counterpart is a trend-following CTA, systematic macro fund, or retail swing trader who relies exclusively on price-based indicators rather than fundamental valuation. Such participants are well-documented in futures, equity, and FX markets.

The decision goal is to output a buy, sell, or hold market order with a quantity scaled by the strength of the moving-average crossover signal. The agent optimises for trend-capture profit by entering positions aligned with the direction of the short-term MA relative to the long-term MA.

In simulation this agent reinforces continuation patterns and amplifies directional moves once a trend establishes. It contributes to momentum clustering and can accelerate bubble formation or crash propagation. Non-goals: (1) the agent MUST NOT use fundamental value or any anchor-based signal; (2) the agent MUST NOT provide two-sided liquidity or act as a market maker.

## Theoretical Foundation

**Time-Series Momentum**:
- Theory / Study: Time-series momentum across asset classes.
- Citation: Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228-250. https://doi.org/10.1016/j.jfineco.2011.11.003
- Core Insight: Past returns over horizons of 1-12 months positively predict future returns in equity indices, currencies, commodities, and bonds. Time-series momentum is pervasive across asset classes and generates significant abnormal returns.
- Mathematical Formulation: `signal = (short_ma - long_ma) / long_ma`; position direction aligns with sign of signal.
- Empirical Evidence: Moskowitz et al. document Sharpe ratios of 0.4-1.0 for time-series momentum strategies across 58 futures contracts (1965-2009), with t-statistics exceeding 4.0 for the pooled portfolio.
- Relevance to This Agent: The agent operationalises the time-series momentum insight by using short vs. long moving averages as a proxy for recent vs. historical performance, generating trend-following trades.
- Calibration Source: Moskowitz et al. (2012), Table 2: optimal lookback windows of 1-12 months; translated to tick-scale with short_window=3, long_window=10.
- Falsification Conditions: If the agent does not generate a buy signal within 2 ticks of the short MA crossing above the long MA by more than 1%, the mechanism is falsified.
- Alternative Theories: Mean-reversion (contrarian); random walk (no predictability); adaptive markets hypothesis.

**Technical Trading Rules and Market Efficiency**:
- Theory / Study: Simple technical trading rules and the stochastic properties of stock returns.
- Citation: Brock, W., Lakonishok, J., & LeBaron, B. (1992). Simple technical trading rules and the stochastic properties of stock returns. *Journal of Finance*, 47(5), 1731-1764. https://doi.org/10.1111/j.1540-6261.1992.tb04681.x
- Core Insight: Moving-average crossover rules generate statistically significant excess returns in the DJIA over 1897-1986; buy signals yield higher returns than sell signals, and conditional volatility differs across signal states.
- Mathematical Formulation: `buy_signal = 1 if MA_short > MA_long else 0`; returns conditional on signal state significantly differ from unconditional returns.
- Empirical Evidence: Brock et al. report buy-signal mean returns of 12% annualised vs. sell-signal mean returns of -7% annualised in DJIA data (1897-1986); bootstrap p-values < 0.01 against random walk null.
- Relevance to This Agent: Validates the MA-crossover signal as a profitable and persistent trading rule that real market participants employ, justifying the agent's exclusive reliance on this signal.
- Calibration Source: Brock et al. (1992), Table II: short windows of 1-5 days, long windows of 50-200 days; tick-rescaled to short=3, long=10.
- Falsification Conditions: If the agent's buy signals do not, on average, precede positive short-run returns more than 55% of the time (given sufficient sample), the MA mechanism adds no value beyond noise.
- Alternative Theories: Efficient market hypothesis (no predictability); data snooping bias (Lo & MacKinlay, 1990).

## Design Purpose and Activation Triggers

Purpose: Generate trend-following trades based on dual moving-average crossover signals, reinforcing momentum in directional markets.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `price_history` available (at least `short_window` observations for minimal signal)

Missing-Signal Policy: If fewer than `short_window` prices are available, hold and accumulate history. If `short_window` prices exist but fewer than `long_window`, compute short_ma against available history as long_ma.

Activation Triggers:
- `signal > 0.01`: submit buy order scaled by signal strength.
- `signal < -0.01`: submit sell order scaled by signal strength.
- `<Default>`: hold (signal within dead-zone [-0.01, +0.01]).

Deactivation Conditions:
- Position at `max_position` cap: hibernate buy side; only sell signals processed.
- Position at `-max_position` cap: hibernate sell side; only buy signals processed.
- Insufficient price history (< `short_window` observations): hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Strong trend (abs(signal) > 0.05) | Increased order size proportional to signal magnitude | Sizing formula scales linearly with signal strength |
| Low volatility / range-bound (abs(signal) < 0.01) | No trading; agent is dormant in dead-zone | Signal threshold filters out noise |

Environmental Dependencies: Requires a per-tick `price` feed and access to a rolling price history buffer of at least `long_window` observations. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price; maps to §3.6.1. |
| `price_history` | environment | `list[float]` | yes | Rolling window of past prices; maps to §3.6.1. |
| `position` | agent's own persisted state | `int` | yes | Current net position; from §3.6.4 state. |
| `round` | scheduler / round header | `int` | yes | Current simulation round. |
| `identity` | scheduler / round header | `str` | yes | Agent identity string. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action selected this call. |
| `quantity` | int | `[0, max_position]` | shares | yes | Order magnitude; 0 when action=hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, max_position]`; out-of-range values MUST be clamped before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action` (buy=positive exposure, sell=negative exposure).
- Determinism markers: decision is deterministic given identical price history and position state; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|sell|hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel: `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution. On conflict with prose elsewhere in this specification, this section wins.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current price for MA calculation [Ref 1, 2] |
| `price_history` | Continuous | `long_window` ticks | Historical prices for computing both short and long MAs [Ref 2] |
| `position` | Discrete | current | Required for capacity constraint and sizing [Ref 1] |

Does NOT use: `fundamental`, `anchor`, `bid_ask_spread`, peer signals, news feeds, volume data.

#### Core Behavioral Mechanism

1. **Read** `price_history` (last `long_window` prices) and current `position`. *(implementation convenience)*
2. **Compute** `short_ma` = mean of last `short_window` prices from `price_history`. *(Traces to Brock et al. 1992 — short MA captures recent trend.)*
3. **Compute** `long_ma` = mean of all available prices in `price_history` (up to `long_window`). *(Traces to Brock et al. 1992 — long MA captures baseline.)*
4. **Compute** `signal` = (`short_ma` - `long_ma`) / `long_ma`. *(Traces to Moskowitz et al. 2012 — normalised trend indicator.)*
5. **Evaluate** activation: if `signal > 0.01`, set direction = buy; if `signal < -0.01`, set direction = sell; otherwise set direction = hold. *(Traces to Brock et al. 1992 — threshold filter.)*
6. **Compute** raw quantity: if direction = buy, `raw_qty` = `scale` × `signal` × min(`buy_capacity`, `max_position` - `position`); if direction = sell, `raw_qty` = `scale` × abs(`signal`) × min(`sell_capacity`, `max_position` + `position`); if hold, `raw_qty` = 0. *(Traces to Moskowitz et al. 2012 — signal-proportional sizing.)*
7. **Clamp** quantity: `quantity` = max(0, int(`raw_qty`)). **Write** decision output. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price; no limit price. |
| Sizing rule | `quantity = int(scale × abs(signal) × available_capacity)` where `available_capacity = min(buy/sell_capacity, max_position ∓ position)` |
| Action lifetime | 1 tick (immediate execution or expiry) |
| Revision policy | No revision; each tick produces a fresh independent decision |
| State constraint | Position bounded by `[-max_position, +max_position]` (self-imposed) |
| Resource cap | Cash >= 0; no leverage permitted |
| Exit rule | None (agent trades indefinitely while signal exists) |

#### Mathematical Model

**Decision output:** Signed trade quantity `Q(t)` ∈ integers, and discrete action ∈ {buy, sell, hold}.

**Decision logic formalization:**

```
short_ma(t) = (1/short_window) × Σ price(t-i) for i=0..short_window-1
long_ma(t)  = (1/long_window)  × Σ price(t-j) for j=0..long_window-1
signal(t)   = (short_ma(t) - long_ma(t)) / long_ma(t)

IF signal(t) > θ_dead:
    action = buy
    Q(t) = int(scale × signal(t) × min(C_buy, Q_max - pos(t)))
ELIF signal(t) < -θ_dead:
    action = sell
    Q(t) = int(scale × |signal(t)| × min(C_sell, Q_max + pos(t)))
ELSE:
    action = hold
    Q(t) = 0
```

**State variables:**

| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | 0 |
| `cash` | float | initial_cash (scenario-defined) |
| `price_history` | list[float] | [] |

**State evolution:**
- Pre-decide: append current `price` to `price_history`; trim to `long_window`.
- Post-execution: `position += Q(t)` if buy; `position -= Q(t)` if sell. `cash -= Q(t) × price` if buy; `cash += Q(t) × price` if sell.

**Determinism contract:** Deterministic given identical price path and initial state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `short_window` | Short MA lookback period | 3 | Brock et al. (1992) |
| `long_window` | Long MA lookback period | 10 | Brock et al. (1992) |
| `scale` | Signal-to-quantity multiplier | 2.0 | Moskowitz et al. (2012) |
| `Q_max` | Maximum absolute position | 60 | Standardised |
| `θ_dead` | Dead-zone threshold | 0.01 | Brock et al. (1992) |

#### Behavioral Properties

- Time horizon: short, because the agent reacts to short-window vs. long-window MA crossovers on a tick-by-tick basis.
- Risk tolerance: high, because the agent takes concentrated directional bets without hedging or fundamental grounding.
- Information asymmetry: none; uses only publicly observable price history.
- Psychological profile: trend extrapolation bias, recency bias, and anchoring to recent price patterns rather than intrinsic value.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `short_window` | int | 3 | [1, long_window-1] | high | Lookback period for short-term moving average. | Higher -> slower signal, fewer trades, less trend amplification. | Brock et al. (1992), Table II |
| `long_window` | int | 10 | [short_window+1, 50] | high | Lookback period for long-term moving average. | Higher -> smoother baseline, delayed crossover signals. | Brock et al. (1992), Table II |
| `scale` | float | 2.0 | [0.1, 10.0] | high | Multiplier converting normalised signal to quantity. | Higher -> larger positions per unit of signal strength. | Moskowitz et al. (2012) |
| `max_position` | int | 60 | [10, 200] | medium | Maximum absolute position (long or short). | Higher -> greater trend exposure before cap binds. | Standardised |
| `dead_zone` | float | 0.01 | [0.001, 0.05] | medium | Signal magnitude below which no trade is generated. | Higher -> fewer trades, less noise but missed small trends. | Brock et al. (1992) |

## Worked Numerical Examples

### Case 1 — Buy signal (short MA above long MA)
```text
System state: price_history=[100,101,102,103,104,105,106,107,108,110]; position=0; max_position=60; scale=2.0; short_window=3; long_window=10.
Calculation:
  short_ma = mean(price_history[-3:]) = mean([107, 108, 110]) = 108.33
  long_ma = mean(price_history) = mean([100,101,102,103,104,105,106,107,108,110]) = 104.6
  signal = (108.33 - 104.6) / 104.6 = 3.73 / 104.6 = 0.0357
  signal > 0.01: action = buy
  available_capacity = min(buy_capacity, 60 - 0) = 60
  raw_qty = 2.0 × 0.0357 × 60 = 4.28
  quantity = int(4.28) = 4
Decision: buy, quantity=4.
State update: position: 0 -> 4; cash reduced by 4 × 110.
```

### Case 2 — Sell signal (short MA below long MA)
```text
System state: price_history=[110,109,108,107,106,105,104,103,102,100]; position=10; max_position=60; scale=2.0; short_window=3; long_window=10.
Calculation:
  short_ma = mean(price_history[-3:]) = mean([103, 102, 100]) = 101.67
  long_ma = mean(price_history) = mean([110,109,108,107,106,105,104,103,102,100]) = 105.4
  signal = (101.67 - 105.4) / 105.4 = -3.73 / 105.4 = -0.0354
  signal < -0.01: action = sell
  available_capacity = min(sell_capacity, 60 + 10) = 70
  raw_qty = 2.0 × 0.0354 × 70 = 4.96
  quantity = int(4.96) = 4
Decision: sell, quantity=4.
State update: position: 10 -> 6; cash increased by 4 × 100.
```

### Case 3 — Hold (signal in dead-zone)
```text
System state: price_history=[100,100,101,100,101,100,100,101,100,100]; position=5; scale=2.0; short_window=3; long_window=10.
Calculation:
  short_ma = mean([101, 100, 100]) = 100.33
  long_ma = mean(all 10) = 100.3
  signal = (100.33 - 100.3) / 100.3 = 0.03 / 100.3 = 0.0003
  |signal| < 0.01: action = hold
  quantity = 0
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Insufficient history (cold start)
```text
System state: price_history=[105, 106]; position=0; short_window=3; long_window=10.
Calculation:
  len(price_history) = 2 < short_window = 3.
  Missing-Signal Policy: hold.
  quantity = 0
Decision: hold, quantity=0.
State update: price_history grows to [105, 106, next_price] on next tick.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `short_window` <- Brock et al. (1992), Table II: 1-5 day short windows rescaled to tick granularity.
- `long_window` <- Brock et al. (1992), Table II: 50-200 day long windows rescaled.
- `scale` <- Moskowitz et al. (2012): position sizing proportional to signal magnitude.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given a rising price series where short_ma > long_ma by more than 1%, agent MUST generate a buy order within the same tick.
- Given a falling price series where short_ma < long_ma by more than 1%, agent MUST generate a sell order within the same tick.
- Given a flat price series where |signal| < 1%, agent MUST hold with zero quantity.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys when short_ma < long_ma (signal negative), THEN implementation is broken because signal-direction mapping is inverted.
- IF the agent trades when |signal| < dead_zone threshold, THEN implementation is broken because dead-zone filter is not applied.
- IF the agent's position exceeds max_position in absolute value, THEN implementation is broken because position cap is not enforced.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_momentum` | `dead_zone = 1.0` | Disabling MA signals eliminates trend amplification. | Decrease in autocorrelation of returns. | Agent trade count and directional accuracy. |
| `aggressive_scale` | `scale = 5.0` | Higher scaling amplifies momentum contribution. | Increase in position size and trend reinforcement. | Mean absolute position and signal-aligned trade volume. |
| `slow_signal` | `short_window = 8` | Slower short MA reduces signal frequency. | Decrease in trade frequency, increase in signal quality. | Trades per 100 ticks. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228-250. https://doi.org/10.1016/j.jfineco.2011.11.003 | Primary theory: time-series momentum across asset classes. |
| 2 | Brock, W., Lakonishok, J., & LeBaron, B. (1992). Simple technical trading rules and the stochastic properties of stock returns. *Journal of Finance*, 47(5), 1731-1764. https://doi.org/10.1111/j.1540-6261.1992.tb04681.x | MA crossover rule profitability and calibration. |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-technical-trader.png)         |
