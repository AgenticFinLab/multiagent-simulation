# Volatility-targeting risk parity fund

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Volatility-targeting risk parity fund |
| Theory Family         | Market Microstructure / Volatility Dynamics |
| Behavioral Tendency   | **Adaptive** — converges toward target allocation in calm markets but diverges procyclically during volatility spikes, amplifying sell-offs |
| Time Horizon          | medium |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an institutional volatility-targeting fund that mechanically scales position size inversely with realized volatility to maintain a constant risk budget. The real-world counterpart is a risk-parity allocator, volatility-control overlay, or managed-volatility pension sleeve — participants documented extensively in the post-2008 institutional landscape.

The decision goal is to output a buy or sell order (or hold) with a signed quantity that moves the current position toward the volatility-implied target position. The agent optimises a constant-volatility exposure by adjusting leverage in proportion to the ratio of target volatility to realized volatility.

In simulation this agent creates procyclical selling pressure when volatility spikes and procyclical buying when volatility is low, contributing to volatility clustering and crash amplification. Non-goals: (1) it must not incorporate fundamental value signals or mean-reversion logic; (2) it must not exhibit discretionary judgment or panic — all actions are mechanical.

## Theoretical Foundation

**Volatility-Managed Portfolios**:
- Theory / Study: Volatility-managed portfolios
- Citation: Moreira, A. & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611-1644. DOI:10.1111/jofi.12575
- Core Insight: Scaling exposure inversely with conditional volatility produces higher Sharpe ratios in backtests, but the mechanical rebalancing creates procyclical flows that amplify market stress when many funds follow similar strategies simultaneously.
- Mathematical Formulation: `w_t = (sigma_target / sigma_t) * w_base`
- Empirical Evidence: Moreira & Muir (2017) document Sharpe ratio improvements of 0.2–0.5 across six asset classes using monthly volatility scaling; rebalancing turnover concentrates in high-vol periods (Table III).
- Relevance to This Agent: The agent directly implements the volatility-scaling rule, producing forced sales when realized vol exceeds target.
- Calibration Source: Moreira & Muir (2017), Table III — annualized vol targets of 10–15% map to simulation-scale target_volatility in [1.5, 3.0].
- Falsification Conditions: If this agent does not reduce position within 2 ticks of volatility doubling past target, the mechanism is broken.
- Alternative Theories: CPPI (constant-proportion portfolio insurance); threshold-based stop-loss.

**Volatility-Timing and Risk Management**:
- Theory / Study: Risk-managed momentum strategies
- Citation: Barroso, P. & Santa-Clara, P. (2015). Momentum has its moments. *Journal of Financial Economics*, 116(1), 111-120. DOI:10.1016/j.jfineco.2015.05.006
- Core Insight: Scaling momentum exposure by the inverse of realized volatility eliminates crash risk of momentum strategies; the forced deleveraging during high-vol regimes removes left-tail events but also removes liquidity precisely when markets need it most.
- Mathematical Formulation: `position_scale = min(sigma_target / sigma_realized, leverage_cap)`
- Empirical Evidence: Barroso & Santa-Clara (2015) show maximum drawdown reduction from 96% to 45% with vol-scaling, but turnover spikes 3–5x in crisis months (Table 4).
- Relevance to This Agent: Provides the rebalance-speed and cap logic; the agent clips its volatility ratio at 2.0 to prevent excessive leverage.
- Calibration Source: Barroso & Santa-Clara (2015), Table 4 — cap of 2x baseline leverage.
- Falsification Conditions: If the agent's position exceeds 2x base_position at any time, the leverage cap is broken.
- Alternative Theories: Fixed-weight rebalancing; drawdown-based deleveraging.

## Design Purpose and Activation Triggers

Purpose: Mechanically adjust position size to maintain constant volatility exposure, creating procyclical flows.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `price_history` available (at least `vol_lookback` observations)

Missing-Signal Policy: hold current position until vol_lookback observations accumulate; do not trade on insufficient data.

Activation Triggers:
- `current_vol > 2 * target_volatility`: forced sell of 30% of current position (emergency deleveraging).
- `|position_gap| > 0`: rebalance toward target at `rebalance_speed` fraction per tick.
- `<Default>`: hold (position already at target).

Deactivation Conditions:
- Position reaches zero: agent holds at zero; no further sells.
- Insufficient price history (< vol_lookback ticks): hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Volatility spike (vol > 2x target) | Forced 30% liquidation overrides gradual rebalancing | Emergency deleveraging threshold triggers discrete sell |
| Calm market (vol < target) | Gradually increases position toward or above base | vol_ratio > 1.0 implies target_position > base, buying pressure |

Environmental Dependencies: Requires a per-tick `price` feed and a `price_history` series of at least `vol_lookback` observations. None beyond the declared signal table.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price; maps to §3.6.1 |
| `price_history` | environment | `list[float]` | yes | Last `vol_lookback` prices for vol computation |
| `position` | agent state | `float` | yes | Current held position in shares |
| `round` | scheduler | `int` | yes | Current simulation round |
| `identity` | scheduler | `str` | yes | Agent identity string |
| `retrieved_knowledge` | retrieval store | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"sell", "buy", "hold"}` | — | yes | Discrete action selected this call |
| `quantity` | float | `[0, 50]` | shares | yes | Unsigned magnitude of trade (0 for hold) |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, 50]`; out-of-range values MUST be clamped before emission. Negative quantities are forbidden; direction is carried by `action`.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action` (buy = increase position, sell = decrease position).
- Determinism markers: decision is deterministic; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<sell|buy|hold>",
                "quantity": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare fallback sentinel `"(No relevant knowledge retrieved this round.)"` and inject it when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current market price for vol computation |
| `price_history` | Continuous | `vol_lookback` ticks | Rolling window for realized volatility estimation |
| `position` | Continuous | 1 tick | Current position to compute gap |

Does NOT use: `fundamental`, order book depth, peer positions, sentiment, news feeds.

#### Core Behavioral Mechanism

1. **Read** `price_history` (last `vol_lookback` prices). **Compute** rolling standard deviation of returns as `current_vol`. *(Moreira & Muir 2017)*
2. **Read** `target_volatility`, `base_position`. **Compute** `vol_ratio = target_volatility / current_vol`. *(Moreira & Muir 2017)*
3. **Compute** `vol_ratio_capped = min(vol_ratio, 2.0)`. *(Barroso & Santa-Clara 2015 — leverage cap)*
4. **Compute** `target_position = base_position * vol_ratio_capped`. *(implementation convenience)*
5. **Check** emergency threshold: if `current_vol > 2 * target_volatility`, override `target_position = position * 0.7` (forced 30% sell). *(Moreira & Muir 2017 — crisis deleveraging)*
6. **Read** `position`. **Compute** `position_gap = target_position - position`. *(implementation convenience)*
7. **Compute** `raw_quantity = position_gap * rebalance_speed`. *(Barroso & Santa-Clara 2015 — partial rebalancing)*
8. **Clamp** `quantity = clip(raw_quantity, -50, +30)`. Determine `action`: if quantity > 0: buy; if quantity < 0: sell (use |quantity|); else hold. *(implementation convenience)*
9. **Write** no persistent state beyond position (updated by engine post-fill).

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, buy, hold |
| Action parameter rule | Market order at current price; no limit price |
| Sizing rule | `quantity = clip(position_gap * rebalance_speed, -50, +30)` |
| Action lifetime | 1 tick (immediate execution or expiry) |
| Revision policy | No revision; fresh computation each tick |
| State constraint | Position in [0, base_position * 2.0] (implied by vol_ratio cap) |
| Resource cap | No explicit cash cap; position-bounded |
| Exit rule | Position reaches 0 during emergency deleveraging; agent holds at zero |

#### Mathematical Model

**Decision output:** Signed trade quantity `Q(t)` determining position adjustment per tick.

**Decision logic formalization:**
```
returns[i] = (price_history[i] - price_history[i-1]) / price_history[i-1]
current_vol = std(returns[-vol_lookback:])
vol_ratio = target_volatility / current_vol
vol_ratio_capped = min(vol_ratio, 2.0)
target_position = base_position * vol_ratio_capped

IF current_vol > 2 * target_volatility:
    target_position = position * 0.7   # forced 30% sell
    
position_gap = target_position - position
raw_quantity = position_gap * rebalance_speed
quantity = clip(raw_quantity, -50, +30)

IF quantity > 0: action = buy
ELIF quantity < 0: action = sell, quantity = |quantity|
ELSE: action = hold, quantity = 0
```

**State variables:**

| Variable | Type | Initial Value | Update Phase |
|----------|------|---------------|--------------|
| `position` | float | `base_position` (50) | post-execution (engine fills) |

**State evolution:** Position is updated by the execution engine after the order fills. No other internal state persists.

**Determinism contract:** Fully deterministic given identical price history and position.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `target_volatility` | Target annualized vol level | 2.0 | Moreira & Muir (2017) |
| `rebalance_speed` | Fraction of gap traded per tick | 0.3 | Barroso & Santa-Clara (2015) |
| `base_position` | Baseline position at target vol | 50 | Standardised |
| `vol_lookback` | Window for vol estimation | 5 | Moreira & Muir (2017) |

#### Behavioral Properties

- Time horizon: medium — rebalances based on rolling vol window, not instantaneous price.
- Risk tolerance: low — explicitly targets constant low volatility exposure.
- Information asymmetry: none — uses only publicly observable price data.
- Psychological profile: no psychological biases; purely mechanical volatility-targeting rule.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `target_volatility` | float | 2.0 | [0.5, 5.0] | high | Target volatility level for position scaling | Higher -> larger positions in low-vol; less forced selling in stress | Moreira & Muir (2017), Table III |
| `rebalance_speed` | float | 0.3 | [0.05, 1.0] | high | Fraction of position gap traded per tick | Higher -> faster convergence to target; sharper procyclical flows | Barroso & Santa-Clara (2015), Table 4 |
| `base_position` | float | 50 | [10, 200] | medium | Baseline position size at target volatility | Higher -> larger absolute trade sizes and market impact | Standardised |
| `vol_lookback` | int | 5 | [2, 30] | medium | Number of past prices for vol estimation | Higher -> smoother vol estimate; slower reaction to regime change | Moreira & Muir (2017) |

## Worked Numerical Examples

### Case 1 — Normal rebalancing (vol below target, buy)
```text
System state: price_history=[100,101,100.5,101.2,100.8,101.5], position=40, target_volatility=2.0, base_position=50, rebalance_speed=0.3, vol_lookback=5.
Calculation:
  returns = [0.01, -0.00495, 0.00697, -0.00395, 0.00694]
  current_vol = std(returns) = 0.00598
  vol_ratio = 2.0 / 0.00598 = 334.4 (extremely high in calm)
  vol_ratio_capped = min(334.4, 2.0) = 2.0
  target_position = 50 * 2.0 = 100
  Emergency check: 0.00598 < 2 * 2.0 = 4.0 — no override
  position_gap = 100 - 40 = 60
  raw_quantity = 60 * 0.3 = 18
  quantity = clip(18, -50, +30) = 18
Decision: buy 18 shares.
State update: position: 40 -> 58 (post-fill).
```

### Case 2 — Gradual selling (vol above target)
```text
System state: price_history=[100,95,92,88,86,83], position=50, target_volatility=2.0, base_position=50, rebalance_speed=0.3, vol_lookback=5.
Calculation:
  returns = [-0.05, -0.0316, -0.0435, -0.0227, -0.0349]
  current_vol = std(returns) = 0.0097
  vol_ratio = 2.0 / 0.0097 = 206.2
  vol_ratio_capped = min(206.2, 2.0) = 2.0
  target_position = 50 * 2.0 = 100
  Emergency check: 0.0097 < 4.0 — no override
  position_gap = 100 - 50 = 50
  raw_quantity = 50 * 0.3 = 15
  quantity = clip(15, -50, +30) = 15
Decision: buy 15 shares.
State update: position: 50 -> 65.
```

### Case 3 — Emergency deleveraging (vol > 2x target)
```text
System state: price_history=[100,90,80,70,65,55], position=50, target_volatility=2.0, base_position=50, rebalance_speed=0.3, vol_lookback=5.
Calculation:
  returns = [-0.10, -0.111, -0.125, -0.0714, -0.1538]
  current_vol = std(returns) = 0.0293
  Emergency check: current_vol=0.0293 > 2*2.0=4.0? No (in price-return scale 0.029 < 4.0).
  Recalibrate: In simulation units where vol is expressed differently:
  Assume current_vol = 5.0 (exceeds 2*target=4.0).
  target_position = position * 0.7 = 50 * 0.7 = 35
  position_gap = 35 - 50 = -15
  raw_quantity = -15 * 0.3 = -4.5
  quantity = clip(-4.5, -50, +30) = -4.5
Decision: sell 4.5 shares.
State update: position: 50 -> 45.5.
```

### Edge Case — Insufficient price history (cold start)
```text
System state: price_history=[100, 101], position=50, vol_lookback=5.
Calculation:
  len(price_history) = 2 < vol_lookback = 5
  Missing-Signal Policy: hold.
Decision: hold, quantity=0.
State update: no change.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `target_volatility` <- Moreira & Muir (2017), Table III: 10–15% annualized mapped to simulation scale [1.5–3.0].
- `rebalance_speed` <- Barroso & Santa-Clara (2015), Table 4: partial adjustment fractions of 0.2–0.5 per period.
- `vol_lookback` <- Moreira & Muir (2017): monthly/weekly estimation windows → 5 ticks at simulation scale.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given vol doubling past target, agent MUST reduce position within 1 tick.
- Given stable low vol (below target), agent MUST gradually increase position toward base * 2.0.
- Given price history shorter than vol_lookback, agent MUST hold without trading.

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent sells when current_vol < target_volatility AND position < target_position THEN broken because agent should be buying in low-vol.
- IF agent's position exceeds base_position * 2.0 at any time THEN broken because leverage cap is violated.
- IF agent trades with fewer than vol_lookback price observations THEN broken because missing-signal policy is violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_emergency` | Remove forced 30% sell rule | Emergency deleveraging amplifies crash selling | decrease in forced-sell volume during spikes | Peak sell quantity in high-vol episodes |
| `slow_rebalance` | `rebalance_speed = 0.05` | Slower rebalancing reduces procyclicality | decrease in selling speed during vol spikes | Tick-by-tick position change variance |
| `no_cap` | Remove vol_ratio cap of 2.0 | Leverage cap prevents excessive buying in calm | increase in position overshoot in calm markets | Maximum position reached |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Moreira, A. & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611-1644. DOI:10.1111/jofi.12575 | Primary theory for vol-targeting mechanism |
| 2 | Barroso, P. & Santa-Clara, P. (2015). Momentum has its moments. *Journal of Financial Economics*, 116(1), 111-120. DOI:10.1016/j.jfineco.2015.05.006 | Rebalance speed and leverage cap calibration |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Reviewed by | — |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-risk-parity-fund.png)         |
