# Short-term momentum trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Short-term momentum trader |
| Theory Family         | Behavioral Finance |
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
- `return > entry_threshold`: submit buy order.
- `return < -entry_threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached: hibernate constrained side.
- Missing prior price: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Mixed | Ignores small moves inside the threshold. |
| Stress | Destabilising | Reinforces large directional price moves. |

Interaction with other agents: Amplifies AnchoredTrader when price drifts upward and directly opposes ContrarianTrader.

## Behavioral Framework

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
| `entry_threshold` | float | 0.02 | [0, 1] | high | Return threshold for action. | Higher -> fewer momentum trades. | Jegadeesh & Titman (1993) |
| `base_position_size` | float | 20.0 | > 0 | high | Maximum order size. | Higher -> stronger trend amplification. | Standardised |
| `sizing_scale` | float | 1000.0 | > 0 | medium | Converts return into quantity. | Higher -> more aggressive trend chasing. | Standardised |
| `inventory_max` | float | 200.0 | > 0 | low | Inventory cap. | Higher -> longer trend exposure. | Standardised |

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | iid narrow draw |
| Heterogeneity per parameter | `entry_threshold -> Uniform(0.015, 0.03)` |
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
- `entry_threshold` <- Jegadeesh & Titman (1993) momentum evidence translated to scenario scale.

**Expected stylized facts** when this agent dominates the population:
- Momentum and short-run trend persistence.
- Higher volume during directional moves.
- Bubble or crash amplification in one-sided regimes.

**Sanity bounds (red flags during simulation)**:
- Agent buys after negative returns.
- Agent uses `fundamental` in the trigger.
- Agent trades without a previous price.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_momentum` | `entry_threshold = 1.0` | Removing momentum reduces trend persistence. |
| `aggressive_momentum` | `base_position_size = 100` | Higher capacity amplifies price runs. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Momentum foundation |
| 2 | Barberis, N., Shleifer, A., & Vishny, R. W. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Anchoring-momentum interaction |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author |  |
| Reviewed by |  |
| Created | 2026-06-27 |
| Version | 1.0.0 |
| Change log | 1.0.0 - Created from AnchoringEffect Agent Design Summary row 4.4 |
| Status | draft |
