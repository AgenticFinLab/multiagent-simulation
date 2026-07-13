# Slow Adapter

## 1 Summary

| Field                 | Content |
|-----------------------|---------|
| agent_type            | slow-adapter |
| Class name            | SlowAdapterAgent |
| Domain role           | Pension/insurance mandate with delayed information processing |
| Theory family         | Heterogeneous Agent Models (HAM) / Bounded Rationality |
| Primary signals       | fundamental_value, price_history |
| Population default    | 1 |
| Variant coverage      | Exponential-smoothing belief update with sluggish adaptation |

## 2 Definition and Goals

This agent models a slow-moving institutional investor (pension fund, insurance company) that updates beliefs about fair value with a significant lag. It blends the current fundamental signal with a long moving average, weighting new information lightly.

The decision goal is to trade toward a perceived value that updates sluggishly, creating delayed demand responses to information shocks. This reflects real-world mandate constraints, committee-based decision-making, and regulatory reporting lags.

In simulation this agent contributes to price stickiness, delayed overshooting, and predictable flows that faster agents can front-run. Non-goals: it must not react instantly to new information or trade at high frequency.

## 3 Theoretical Foundation

**Heterogeneous Agent Models**:
- Citation: Brock, W. A. & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8-9), 1235-1274. https://doi.org/10.1016/S0165-1889(98)00011-6
- Core Insight: Agents using different belief-updating speeds create endogenous market dynamics. Slow adapters stabilise in the long run but create exploitable predictability in the short run.

**Adaptive Beliefs**:
- Citation: Hommes, C. H. (2006). Heterogeneous agent models in economics and finance. In L. Tesfatsion & K. L. Judd (Eds.), *Handbook of Computational Economics*, Vol. 2, 1109-1186. Elsevier.
- Core Insight: Bounded rationality and adaptive expectations lead to systematic lags in belief formation. Agents who update slowly create persistent forecast errors under regime shifts.

- Relevance to This Agent: The agent implements a slow-updating belief rule that blends fundamental information with historical price averages using a low update weight.
- Falsification Conditions: If the agent's perceived value tracks the fundamental instantly (update_weight near 1), it is misspecified.

## 4 Design Purpose and Activation Triggers

Purpose: Introduce institutional inertia and delayed response to fundamental shifts, creating predictable flow patterns and price stickiness.

Call Frequency: every tick.

Prerequisite Signals:
- `fundamental_value` (F) available
- `price_history` of length >= `lookback_window`

Missing-Signal Policy: hold if fundamental or sufficient history is unavailable.

Activation Triggers:
- Sufficient history available: compute perceived_value and trade.
- Perceived value differs from price: submit order.

Deactivation Conditions:
- Insufficient price history (first `lookback_window - 1` ticks).
- Cash or position constraints binding.

## 5 Behavioral Framework

### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `fundamental_value` | Continuous | 1 tick | Current fundamental estimate |
| `price_history` | Array | lookback_window ticks | Compute moving average |

Does NOT use: momentum signal, volatility, peer positions.

### Core Behavioral Mechanism

1. Compute moving average: `MA = mean(price_history[-lookback_window:])`.
2. Compute perceived value: `perceived_value = update_weight * F + (1 - update_weight) * MA`.
3. Compute deviation: `deviation = (perceived_value - price) / price`.
4. Compute quantity: `quantity = base_position_size * deviation`.
5. Clamp quantity to [-10, +10].
6. Submit order if quantity is non-zero after rounding.

### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current price |
| Order quantity rule | `Q = clamp(base_position_size * deviation, -10, 10)` |
| Inventory constraint | bounded by clamp and cash |
| Wealth / leverage cap | cash >= 0; no margin |

### Mathematical Model

```
MA_t = (1/L) * sum(P_{t-L+1}, ..., P_t)
perceived_value_t = w * F_t + (1 - w) * MA_t
deviation = (perceived_value_t - P_t) / P_t
quantity = clamp(base_position_size * deviation, -10, +10)
```

Where `w = update_weight`, `L = lookback_window`.

## 6 Parameters

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| `lookback_window` | int | 10 | >= 2 | Window for moving average calculation |
| `update_weight` | float | 0.1 | (0, 1) | Weight on current fundamental (low = slow) |
| `base_position_size` | float | 10.0 | > 0 | Base scaling factor for order size |
| `initial_cash` | float | 10000.0 | > 0 | Starting cash endowment |
| `initial_position` | int | 0 | >= 0 | Starting inventory |

## 7 Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | 1 |
| Parameter heterogeneity policy | single canonical instance |
| Heterogeneity per parameter | N/A at population = 1 |
| Cross-agent correlation | N/A |
| Identity persistence | fixed for episode duration |

## 8 Worked Numerical Examples

### Case 1 - Sluggish buy after fundamental jump
```text
State: price=100, F=110, MA(10)=99, update_weight=0.1.
perceived_value = 0.1*110 + 0.9*99 = 11 + 89.1 = 100.1.
deviation = (100.1 - 100)/100 = 0.001.
quantity = 10 * 0.001 = 0.01 -> round to 0.
Decision: hold (signal too weak this tick).
```

### Case 2 - Accumulated signal produces trade
```text
State: price=95, F=110, MA(10)=102, update_weight=0.1.
perceived_value = 0.1*110 + 0.9*102 = 11 + 91.8 = 102.8.
deviation = (102.8 - 95)/95 = 0.082.
quantity = 10 * 0.082 = 0.82 -> round to 1.
Decision: buy 1 unit.
```

### Case 3 - Sell when price overshoots
```text
State: price=115, F=100, MA(10)=105, update_weight=0.1.
perceived_value = 0.1*100 + 0.9*105 = 10 + 94.5 = 104.5.
deviation = (104.5 - 115)/115 = -0.091.
quantity = 10 * (-0.091) = -0.91 -> round to -1.
Decision: sell 1 unit.
```

### Edge Case - Insufficient history
```text
State: tick=5, lookback_window=10.
Only 5 prices available.
Decision: hold.
```

## 9 Validation and Calibration

**Expected stylized facts** when this agent is present:
- Delayed price adjustment to fundamental shifts.
- Predictable order flow that lags information by several ticks.
- Reduced short-term volatility but longer adjustment to new equilibria.

**Sanity bounds (red flags)**:
- Agent tracks fundamental instantly (behaves like fundamentalist).
- Position sizes exceed clamp bounds.
- Trades before lookback window is filled.

### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_slow_adapter` | population = 0 | Removing slow adapter speeds price discovery |
| `fast_adapter` | `update_weight = 0.9` | Higher weight makes agent behave like fundamentalist |

## 10 Academic References

| # | Citation | DOI |
|---|----------|-----|
| 1 | Brock, W. A. & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *JEDC*, 22(8-9), 1235-1274. | 10.1016/S0165-1889(98)00011-6 |
| 2 | Hommes, C. H. (2006). Heterogeneous agent models in economics and finance. *Handbook of Computational Economics*, Vol. 2, 1109-1186. | N/A (book chapter) |
| 3 | Greenwood, R. & Hanson, S. G. (2015). Waves in ship prices and investment. *QJE*, 130(1), 55-109. | 10.1093/qje/qju035 |

## 11 Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AgenticFinLab |
| Created | 2025-07-14 |
| Version | 1.0.0 |
| Status | draft |
| Icon        | ![](../agent_images/icons/finance-slow-adapter.png) |
