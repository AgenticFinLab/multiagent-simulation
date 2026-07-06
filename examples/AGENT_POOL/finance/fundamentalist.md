# Fundamentalist

## 1 Summary

| Field                 | Content |
|-----------------------|---------|
| agent_type            | fundamentalist |
| Class name            | FundamentalistAgent |
| Domain role           | Value/contrarian fund that trades toward perceived fundamental value at low frequency |
| Theory family         | Heterogeneous Agent Models (HAM) |
| Primary signals       | fundamental_value, price |
| Population default    | 2 |
| Variant coverage      | Noisy value estimation with clamped position sizing |

## 2 Definition and Goals

This agent models a fundamentalist investor who believes prices revert to an intrinsic value. The real-world counterpart is a value fund, contrarian allocator, or long-horizon institutional investor.

The decision goal is to buy when price is below estimated fundamental value and sell when above, with order size proportional to the perceived mispricing. It trades infrequently (every 3 ticks) and carries estimation noise, reflecting imperfect information about true value.

In simulation this agent provides a stabilising mean-reversion force that counteracts momentum traders and noise traders. Non-goals: it must not chase trends or trade every tick.

## 3 Theoretical Foundation

**Heterogeneous Agent Models**:
- Citation: Brock, W. A. & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8-9), 1235-1274. https://doi.org/10.1016/S0165-1889(98)00011-6
- Core Insight: Markets contain fundamentalists who push price toward value and chartists who amplify deviations. The interaction generates complex price dynamics including bubbles and crashes.
- Mathematical Formulation: Fundamentalist demand is proportional to `(V - P)/P` where V is perceived value.
- Empirical Evidence: Heterogeneous-agent models reproduce excess volatility, fat tails, and volatility clustering observed in real markets.
- Relevance to This Agent: The agent implements the fundamentalist belief type from Brock-Hommes, providing the stabilising anchor in a heterogeneous population.
- Calibration Source: Brock & Hommes (1998), Table 1 parameter sets.
- Falsification Conditions: If the agent's orders correlate with momentum rather than value deviation, it is misspecified.

## 4 Design Purpose and Activation Triggers

Purpose: Supply mean-reverting demand that anchors prices near fundamental value and dampens speculative bubbles.

Call Frequency: every 3 ticks (low frequency).

Prerequisite Signals:
- `price` available
- `fundamental_value` available (possibly with noise)

Missing-Signal Policy: hold if price or fundamental estimate is unavailable.

Activation Triggers:
- `tick % trade_frequency == 0`: compute deviation and submit order.
- Otherwise: hold.

Deactivation Conditions:
- Cash insufficient for buy: skip buy orders.
- Position at clamp boundary: no further orders in that direction.

## 5 Behavioral Framework

### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current market price |
| `fundamental_value` | Continuous | 1 tick | Estimated intrinsic value (noisy) |

Does NOT use: momentum, trend, peer flow, volatility.

### Core Behavioral Mechanism

1. Check if current tick is a trading tick (`tick % trade_frequency == 0`).
2. If not, hold.
3. Estimate value: `estimated_value = fundamental_value + N(0, value_noise_std)`.
4. Compute deviation: `deviation = (estimated_value - price) / price`.
5. Compute raw quantity: `quantity = value_sensitivity * deviation * base_position_size`.
6. Clamp quantity to [-20, +20].
7. Submit order if quantity is non-zero.

### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current price |
| Order quantity rule | `Q = clamp(value_sensitivity * deviation * base_position_size, -20, 20)` |
| Inventory constraint | bounded by clamp and cash |
| Wealth / leverage cap | cash >= 0; no margin |

### Mathematical Model

```
estimated_value = fundamental_value + epsilon,  epsilon ~ N(0, value_noise_std)
deviation = (estimated_value - price) / price
quantity = clamp(value_sensitivity * deviation * base_position_size, -20, +20)
```

## 6 Parameters

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| `trade_frequency` | int | 3 | >= 1 | Trade every N ticks |
| `value_sensitivity` | float | 0.5 | (0, 5] | Responsiveness to value deviation |
| `base_position_size` | float | 20.0 | > 0 | Base scaling factor for order size |
| `value_noise_std` | float | 2.0 | >= 0 | Std dev of noise added to fundamental estimate |
| `initial_cash` | float | 10000.0 | > 0 | Starting cash endowment |
| `initial_position` | int | 0 | >= 0 | Starting inventory |

## 7 Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | 2 |
| Parameter heterogeneity policy | value_noise_std drawn per instance |
| Heterogeneity per parameter | `value_noise_std ~ Uniform(1.0, 3.0)` |
| Cross-agent correlation | independent noise draws |
| Identity persistence | fixed for episode duration |

## 8 Worked Numerical Examples

### Case 1 - Buy on undervaluation
```text
State: tick=3, price=100, fundamental_value=105, noise_draw=+1.0.
estimated_value = 105 + 1.0 = 106.
deviation = (106 - 100)/100 = 0.06.
quantity = 0.5 * 0.06 * 20 = 0.6 -> round to 1.
Decision: buy 1 unit at price 100.
```

### Case 2 - Sell on overvaluation
```text
State: tick=6, price=110, fundamental_value=100, noise_draw=-0.5.
estimated_value = 100 - 0.5 = 99.5.
deviation = (99.5 - 110)/110 = -0.0955.
quantity = 0.5 * (-0.0955) * 20 = -0.955 -> round to -1.
Decision: sell 1 unit at price 110.
```

### Case 3 - Large deviation with clamping
```text
State: tick=9, price=50, fundamental_value=100, noise_draw=+3.0.
estimated_value = 103.
deviation = (103 - 50)/50 = 1.06.
quantity = 0.5 * 1.06 * 20 = 10.6 -> round to 11, within clamp.
Decision: buy 11 units at price 50.
```

### Edge Case - Non-trading tick
```text
State: tick=4, trade_frequency=3.
4 % 3 != 0.
Decision: hold.
```

## 9 Validation and Calibration

**Expected stylized facts** when this agent is present:
- Price mean-reverts toward fundamental over medium horizon.
- Reduces excess volatility relative to noise-only populations.
- Order flow negatively correlated with recent price deviation from value.

**Sanity bounds (red flags)**:
- Orders correlate positively with momentum.
- Average position size exceeds clamp bounds.
- Agent trades on non-trading ticks.

### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_fundamentalist` | population = 0 | Removing value traders leads to persistent mispricing |
| `perfect_info` | `value_noise_std = 0` | Perfect information speeds convergence to fundamental |

## 10 Academic References

| # | Citation | DOI |
|---|----------|-----|
| 1 | Brock, W. A. & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *JEDC*, 22(8-9), 1235-1274. | 10.1016/S0165-1889(98)00011-6 |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H. & Waldmann, R. J. (1990). Noise trader risk in financial markets. *JPE*, 98(4), 703-738. | 10.1086/261703 |

## 11 Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AgenticFinLab |
| Created | 2025-07-14 |
| Version | 1.0.0 |
| Change log | 1.0.0 - Initial creation based on Brock-Hommes fundamentalist archetype |
| Status | draft |
| Icon        | ![](../agent_images/icons/finance-fundamentalist.png) |
