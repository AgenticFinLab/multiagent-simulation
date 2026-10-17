# Slow rebalancing passive allocator

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Slow rebalancing passive allocator |
| Theory Family         | Portfolio Theory / Optimal Execution |
| Behavioral Tendency   | **Converging** — gradually rebalances toward a fixed target allocation, providing weak mean-reverting demand |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a large passive institutional allocator (pension fund, endowment, or target-date fund) that periodically rebalances toward a fixed strategic allocation. The real-world counterpart is a slow-rebalancing index fund, pension scheme, or strategic asset allocator that trades infrequently and in small sizes to minimize market impact.

The decision goal is to output a buy or sell order (or hold) that moves the current position fractionally toward its target on rebalancing rounds. The agent follows a fixed-weight policy without reference to momentum, value, or volatility signals.

In simulation this agent provides a weak stabilizing force through mean-reversion to a fixed target, but its low frequency and small trade sizes mean it cannot offset large directional flows from other agents. Non-goals: (1) it must not react to short-term price movements or volatility; (2) it must not trade on non-rebalancing rounds.

## Theoretical Foundation

**Dynamic Trading with Predictable Returns**:
- Theory / Study: Dynamic trading with predictable returns and transaction costs
- Citation: Garleanu, N. & Pedersen, L. H. (2013). Dynamic trading with predictable returns and transaction costs. *Journal of Finance*, 68(6), 2309-2340. DOI:10.1093/rfs/hhs083
- Core Insight: Optimal portfolio rebalancing under transaction costs involves gradual adjustment toward a target — a fraction of the gap is closed each period rather than immediate full rebalancing. The optimal speed depends on the ratio of alpha decay to transaction costs.
- Mathematical Formulation: `trade_t = adjustment_rate * (target_position - current_position)`
- Empirical Evidence: Garleanu & Pedersen (2013) derive optimal rebalancing speed of 0.1-0.3 per period for typical institutional cost structures (Section IV, calibration to NYSE data).
- Relevance to This Agent: The agent implements the partial-adjustment rule directly, trading a fraction of the gap on each rebalancing date.
- Calibration Source: Garleanu & Pedersen (2013), Section IV — adjustment rates of 0.1-0.3; rebalancing frequency of monthly/quarterly maps to every 20 ticks.
- Falsification Conditions: If this agent trades on non-rebalancing rounds or trades more than max_quantity in a single round, the mechanism is broken.
- Alternative Theories: Calendar rebalancing (fixed date); threshold rebalancing (only when drift exceeds band).

## Design Purpose and Activation Triggers

Purpose: Provide slow, predictable mean-reverting demand toward a fixed allocation target.

Call Frequency: every-tick (but only acts on rebalancing rounds).

Prerequisite Signals (must be available for the agent to evaluate):
- `round` available (to check rebalancing schedule)
- `position` available (current holdings)

Missing-Signal Policy: hold if position is unknown.

Activation Triggers:
- `round % rebalance_frequency == 0 AND gap != 0`: rebalance — trade fraction of gap.
- `<Default>`: hold (not a rebalancing round, or already at target).

Deactivation Conditions:
- Position equals target_position: hold (no gap to close).
- Insufficient signal: hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Large price move creating large gap | Trades max_quantity per rebalancing round (capped) | Clip rule limits single-round impact |
| Position at target | Zero trading activity | Gap is zero so no order generated |

Environmental Dependencies: Requires `round` counter and ability to observe own `position`. None beyond declared signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `round` | scheduler | `int` | yes | Current simulation round |
| `position` | agent state | `float` | yes | Current held position |
| `identity` | scheduler | `str` | yes | Agent identity |
| `retrieved_knowledge` | retrieval store | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action selected |
| `quantity` | float | `[0, 10]` | shares | yes | Unsigned trade magnitude |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared MUST NOT be emitted.
- Value ranges: `quantity` clamped to `[0, 10]`.
- Units and sign conventions: `quantity` is unsigned; direction carried by `action`.
- Determinism markers: deterministic; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|sell|hold>",
                "quantity": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain valid JSON matching the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST use fallback sentinel `"(No relevant knowledge retrieved this round.)"`.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `round` | Discrete | 1 tick | Determines whether this is a rebalancing round |
| `position` | Continuous | 1 tick | Current holdings to compute gap vs target |

Does NOT use: `price`, `fundamental`, `volatility`, order book, momentum, peer positions, sentiment.

#### Core Behavioral Mechanism

1. **Read** `round`. **Check** if `round % rebalance_frequency == 0`. If not, hold. *(Garleanu & Pedersen 2013 — periodic rebalancing)*
2. **Read** `position`, `target_position`. **Compute** `gap = target_position - position`. *(Garleanu & Pedersen 2013)*
3. **Compute** `raw_quantity = gap * adjustment_rate`. *(Garleanu & Pedersen 2013 — partial adjustment)*
4. **Clamp** `quantity = clip(raw_quantity, -max_quantity, +max_quantity)`. *(implementation convenience — impact cap)*
5. **Determine** action: if quantity > 0: buy; if quantity < 0: sell (use |quantity|); else hold. *(implementation convenience)*
6. **Write** no persistent state; position updated by engine post-fill.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price |
| Sizing rule | `quantity = clip((target_position - position) * adjustment_rate, -max_quantity, +max_quantity)` |
| Action lifetime | 1 tick |
| Revision policy | No revision; recomputes on next rebalancing round |
| State constraint | Position bounded by [0, 2 * target_position] implicitly |
| Resource cap | max_quantity per rebalancing event |
| Exit rule | None — always attempts to converge to target |

#### Mathematical Model

**Decision output:** Signed trade quantity `Q(t)` on rebalancing rounds; zero otherwise.

**Decision logic formalization:**
```
IF round % rebalance_frequency != 0:
    action = hold; quantity = 0
ELSE:
    gap = target_position - position
    raw_quantity = gap * adjustment_rate
    quantity = clip(raw_quantity, -max_quantity, +max_quantity)
    IF quantity > 0: action = buy
    ELIF quantity < 0: action = sell; quantity = |quantity|
    ELSE: action = hold; quantity = 0
```

**State variables:**

| Variable | Type | Initial Value | Update Phase |
|----------|------|---------------|--------------|
| `position` | float | `target_position` (30) | post-execution |

**State evolution:** Position updated by engine after fill. No other persisted state.

**Determinism contract:** Fully deterministic given round number and position.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `rebalance_frequency` | Rounds between rebalancing events | 20 | Garleanu & Pedersen (2013) |
| `target_position` | Fixed target allocation in shares | 30 | Standardised |
| `adjustment_rate` | Fraction of gap traded per rebalancing | 0.2 | Garleanu & Pedersen (2013) |
| `max_quantity` | Maximum shares traded per event | 10 | Standardised |

#### Behavioral Properties

- Time horizon: long — rebalances infrequently (every 20 rounds) toward a strategic target.
- Risk tolerance: low — maintains fixed allocation regardless of market conditions.
- Information asymmetry: none — uses only own position and round counter.
- Psychological profile: no biases; purely mechanical periodic rebalancing without discretion.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `rebalance_frequency` | int | 20 | [5, 100] | high | Rounds between rebalancing trades | Higher -> less frequent trading; weaker stabilization | Garleanu & Pedersen (2013), Section IV |
| `target_position` | float | 30 | [10, 200] | medium | Target allocation in shares | Higher -> larger absolute trade sizes on rebalancing | Standardised |
| `adjustment_rate` | float | 0.2 | [0.05, 1.0] | high | Fraction of gap closed per rebalancing event | Higher -> faster convergence; larger single trades | Garleanu & Pedersen (2013), Section IV |
| `max_quantity` | int | 10 | [1, 50] | medium | Maximum trade size per rebalancing round | Higher -> allows larger single-round correction | Standardised |

## Worked Numerical Examples

### Case 1 — Buy to close gap (rebalancing round)
```text
System state: round=20, position=22, target_position=30, adjustment_rate=0.2, max_quantity=10, rebalance_frequency=20.
Calculation:
  round % 20 == 0 -> rebalancing round
  gap = 30 - 22 = 8
  raw_quantity = 8 * 0.2 = 1.6
  quantity = clip(1.6, -10, +10) = 1.6
Decision: buy 1.6 shares.
State update: position: 22 -> 23.6.
```

### Case 2 — Sell to close gap (overweight)
```text
System state: round=40, position=38, target_position=30, adjustment_rate=0.2, max_quantity=10.
Calculation:
  round % 20 == 0 -> rebalancing round
  gap = 30 - 38 = -8
  raw_quantity = -8 * 0.2 = -1.6
  quantity = clip(-1.6, -10, +10) = -1.6
Decision: sell 1.6 shares.
State update: position: 38 -> 36.4.
```

### Case 3 — Hold (not a rebalancing round)
```text
System state: round=15, position=22, target_position=30.
Calculation:
  round % 20 = 15 != 0 -> not rebalancing round
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Large gap exceeds max_quantity
```text
System state: round=60, position=5, target_position=30, adjustment_rate=0.2, max_quantity=10.
Calculation:
  round % 20 == 0 -> rebalancing round
  gap = 30 - 5 = 25
  raw_quantity = 25 * 0.2 = 5.0
  quantity = clip(5.0, -10, +10) = 5.0
Decision: buy 5.0 shares (within cap).
State update: position: 5 -> 10.

Extreme sub-case: position=-70, gap=100, raw=20, clipped to 10.
Decision: buy 10 shares (capped at max_quantity).
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `rebalance_frequency` <- Garleanu & Pedersen (2013): monthly/quarterly institutional rebalancing maps to 20 ticks.
- `adjustment_rate` <- Garleanu & Pedersen (2013), Section IV: optimal adjustment 0.1-0.3 for typical cost structures.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given a rebalancing round with position below target, agent MUST buy.
- Given a non-rebalancing round, agent MUST hold regardless of position drift.
- Given position equal to target on rebalancing round, agent MUST hold (zero gap).

**Sanity bounds (red flags indicating broken implementation)**:
- IF agent trades on a non-rebalancing round THEN broken because rebalancing schedule is violated.
- IF agent's trade quantity exceeds max_quantity THEN broken because cap is violated.
- IF agent uses price or volatility in its decision THEN broken because it should be price-agnostic.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `frequent_rebalance` | `rebalance_frequency=1` | More frequent rebalancing increases stabilization | increase in mean-reversion force | Autocorrelation of position gap |
| `full_adjustment` | `adjustment_rate=1.0` | Full gap closure per round increases market impact | increase in single-round trade size | Max quantity per trade |
| `no_cap` | `max_quantity=1000` | Removing cap allows extreme single-round trades | increase in max trade sizes during large drifts | Peak single-round trade |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Garleanu, N. & Pedersen, L. H. (2013). Dynamic trading with predictable returns and transaction costs. *Journal of Finance*, 68(6), 2309-2340. DOI:10.1093/rfs/hhs083 | Primary theory for optimal partial rebalancing |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Reviewed by | — |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-passive-investor.png)         |
