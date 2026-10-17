# Short-term momentum trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Short-term momentum trader |
| Theory Family         | Behavioral Finance |
| Behavioral Tendency   | **Diverging — chases recent price trends and amplifies short-run moves; diverges from fundamental value during trending episodes** |
| Market Role           | **Context-dependent** - amplifies prevailing short-term trends |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |
## Definition and Goals

This agent models a trend follower or momentum trader who extrapolates recent price movement. The real-world counterpart is a momentum trader, technical trader, or short-horizon trend follower.

The decision goal is to output a buy, sell, or hold order based on recent return. It buys after sufficiently positive return and sells after sufficiently negative return.

In simulation this agent helps produce momentum and short-run trend persistence, and can amplify bubbles or accelerate corrections. Non-goals: it must not use fundamental value, cost basis, or liquidity-provision logic.

## Theoretical Foundation

**Short-Term Momentum**:
- Theory / Study: Returns to buying winners and selling losers.
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Recent winners tend to continue outperforming over short to intermediate horizons. Trend-following demand creates positive feedback in price dynamics.
- Mathematical Formulation: `return = (P_t - P_{t-1}) / P_{t-1}`.
- Empirical Evidence: Jegadeesh & Titman document profitable winner-minus-loser strategies in US equities.
- Relevance to This Agent: The agent operationalises the momentum signal as a thresholded buy/sell rule.
- Calibration Source: Jegadeesh & Titman (1993).
- Falsification Conditions: If the agent trades against the sign of recent return, the mechanism is not momentum.
- Alternative Theories: Short-horizon reversal; conservatism and later correction.

**Investor Sentiment and Momentum Extension**:
- Theory / Study: Underreaction followed by momentum and reversal.
- Citation: Barberis, N., Shleifer, A., & Vishny, R. W. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0
- Core Insight: Conservatism can create initial underreaction and later trend continuation. Momentum traders amplify the trend phase before eventual correction.
- Mathematical Formulation: `return_signal = (P_t - P_{t-1}) / P_{t-1}`.
- Empirical Evidence: The source scenario cites Barberis et al. as grounding the anchoring-momentum interaction.
- Relevance to This Agent: MomentumTrader extends the slow drift caused by anchoring agents.
- Calibration Source: Barberis, Shleifer & Vishny (1998).
- Falsification Conditions: If adding this agent does not increase short-run autocorrelation, the momentum channel is absent.
- Alternative Theories: overreaction reversal.

## Design Purpose and Activation Triggers

Purpose: Amplify local price trends without reference to fundamentals.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `prev_price` available

Missing-Signal Policy: hold until at least two valid prices exist.

Activation Triggers:
- `return > threshold`: submit buy order.
- `return < -threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached: hibernate constrained side.
- Missing prior price: hold.


Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|---|---|---|
| Trend reversal | Continues to trade in the prior trend direction until the signal explicitly flips | `momentum` is a backward-looking rolling mean; sign change lags the reversal |
| Low-volatility regime | Reduces order size as `abs(momentum)` falls below `threshold` | Sizing is proportional to signal magnitude |

Environmental Dependencies: Requires a per-tick `price` feed and a `price_history` series of at least `lookback` observations for a fully warm signal. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Mixed | Ignores small moves inside the threshold. |
| Stress | Destabilising | Reinforces large directional price moves. |

Interaction with other agents: Amplifies AnchoredTrader when price drifts upward and directly opposes ContrarianTrader.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|---|---|---|---|---|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. |
| `prev_price` | environment | `float` | yes | Maps to §3.6.1 `prev_price`. |
| `identity`, `round` | round header | `str`, `int` | yes | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|---|---|---|---|---|---|
| `action` | enum | {"market", "hold-no-op"} | — | yes | Discrete action selected this call. |
| `quantity` | float | `[0, base_position_size]` | shares | conditional | Order magnitude; 0 when `action = hold`. |
| `price_level` | float | `= price` (market order) | currency | conditional | Execution reference; equals observed `price` for market orders. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: every row marked `Required? = yes` in the Outputs table MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, base_position_size]`; out-of-range values MUST be clamped by the implementer before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. `price_level` uses the same currency unit as `fundamental` and `price`.
- Determinism markers: the decision determinism class is declared in §3.2 Summary; no seed is emitted unless the decision is `stochastic-given-seed`.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
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

Implementers of this agent MUST re-open this §3.6.0 I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current price |
| `prev_price` | Continuous | 1 tick | Previous price for return calculation |

Does NOT use: `fundamental`, `anchor`, `cost_basis`, bid-ask depth.

#### Core Behavioral Mechanism

1. Observe current and previous price.
2. Compute one-period return.
3. If return is above threshold, buy.
4. If return is below negative threshold, sell.
5. Hold for small returns.
6. Size order with return magnitude.
7. Clip by inventory and cash constraints.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current price |
| Order quantity rule | `Q = min(base_position_size, abs(return) * sizing_scale)` |
| Order lifetime | 1 tick |
| Cancellation policy | unfilled orders expire at end of tick |
| Inventory constraint | inventory bounded by `inventory_max` |
| Wealth / leverage cap | cash >= 0; no margin |
| Stop-loss / kill rule | none |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Trigger function:
  ```
  r = (P_t - P_{t-1}) / P_{t-1}
  buy if r > theta_m
  sell if r < -theta_m
  otherwise hold
  ```
- Sizing function:
  ```
  Q = sign(r) * min(base_position_size, abs(r) * sizing_scale)
  ```
- State variables: `prev_price`; `position`; `cash`.
- State-update rule: update `prev_price` after decision; update position and cash post-fill.
- Determinism contract: deterministic given price path and parameters.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_m` | momentum threshold | 0.02 | Jegadeesh & Titman (1993) |

#### Behavioral Properties

- Time horizon: short, because it uses recent price change.
- Risk tolerance: high, because it ignores fundamentals.
- Information asymmetry: none.
- Psychological profile: trend extrapolation and recency bias.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `threshold` | float | 0.02 | [0, 1] | high | Return threshold for action. | Higher -> fewer momentum trades. | Jegadeesh & Titman (1993) |
| `base_position_size` | float | 20.0 | > 0 | high | Maximum order size. | Higher -> stronger trend amplification. | Standardised |
| `sizing_scale` | float | 1000.0 | > 0 | medium | Converts return into quantity. | Higher -> more aggressive trend chasing. | Standardised |
| `inventory_max` | float | 200.0 | > 0 | low | Inventory cap. | Higher -> longer trend exposure. | Standardised |

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | iid narrow draw |
| Heterogeneity per parameter | `threshold -> Uniform(0.015, 0.03)` |
| Cross-agent correlation | none |
| Identity persistence | identical across episodes unless redrawn |

## Worked Numerical Examples

### Case 1 - Buy positive momentum
```text
Market state: P_t=103, P_{t-1}=100, threshold=0.02.
Calculation: r=0.03.
Decision: buy 20.
State update: prev_price becomes 103; position +20.
```

### Case 2 - Sell negative momentum
```text
Market state: P_t=97, P_{t-1}=100.
Calculation: r=-0.03.
Decision: sell 20.
State update: prev_price becomes 97; position -20.
```

### Case 3 - Hold small move
```text
Market state: P_t=101, P_{t-1}=100.
Calculation: r=0.01.
Decision: hold.
State update: prev_price becomes 101.
```

### Edge Case - No previous price
```text
Market state: P_t=100, prev_price missing.
Calculation: return unavailable.
Decision: hold.
State update: set prev_price=100 for next tick.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `threshold` <- Jegadeesh & Titman (1993) momentum evidence translated to scenario scale.

**Expected stylized facts** when this agent dominates the population:
- Momentum and short-run trend persistence.
- Higher volume during directional moves.
- Bubble or crash amplification in one-sided regimes.

**Sanity bounds (red flags during simulation)**:
- IF the agent exhibits the behaviour described (Agent buys after negative returns) THEN the implementation is broken because agent buys after negative returns.
- IF the agent exhibits the behaviour described (Agent uses `fundamental` in the trigger) THEN the implementation is broken because agent uses `fundamental` in the trigger.
- IF the agent exhibits the behaviour described (Agent trades without a previous price) THEN the implementation is broken because agent trades without a previous price.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_momentum` | `threshold = 1.0` | Removing momentum reduces trend persistence. |
| `aggressive_momentum` | `base_position_size = 100` | Higher capacity amplifies price runs. |

## Behavioral Verification and Calibration

- Given a one-period return above `threshold` (e.g., r = 0.03 > 0.02), agent must emit a buy order with positive quantity.
- Given a one-period return below negative `threshold` (e.g., r = -0.03 < -0.02), agent must emit a sell order with positive quantity.
- Given a one-period return inside the threshold band (e.g., |r| = 0.01 < 0.02), agent must hold with zero quantity.
- Given `prev_price` is missing or unavailable, agent must hold and not compute a return signal.
- Given inventory at `inventory_max`, agent must not increase position further on the constrained side.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_momentum` | `threshold = 1.0` | Removing momentum trading reduces short-run return autocorrelation | decrease | lag-1 return autocorrelation |
| `aggressive_momentum` | `base_position_size = 100` | Higher capacity amplifies trend persistence and bubble magnitude | increase | peak-to-trough price swing |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Momentum foundation |
| 2 | Barberis, N., Shleifer, A., & Vishny, R. W. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Anchoring-momentum interaction |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AGenticFinLab |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-06-27 |
| Version | 1.0.3 |
| Status | conformant |
| Icon        | ![](../agent_images/icons/finance-momentum-trader.png) |
