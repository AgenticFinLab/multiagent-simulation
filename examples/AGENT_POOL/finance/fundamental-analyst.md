# Conservative fundamental analyst

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Conservative fundamental analyst |
| Theory Family         | Behavioral Finance |
| Behavioral Tendency   | **Converging — trades directly on the gap between price and fundamental value; converges on fundamental value** |
| Market Role           | **Stabilising** - gradually corrects mispricing through slow belief updating |
| Time Horizon          | long |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |
## Definition and Goals

This agent models a fundamentalist or value investor who learns conservatively from fundamental information. The real-world counterpart is a fundamentalist / value investor or institutional analyst who updates valuation estimates gradually.

The decision goal is to emit buy, sell, or hold orders based on the gap between price and an internally smoothed belief about fundamental value. It differs from RationalUpdater because its belief moves slowly rather than instantly to the true fundamental.

In simulation this agent helps produce sustained but bounded mispricing, slow decay of deviations, and stabilising long-horizon correction. Non-goals: it must not use first-price anchors, pure random noise, or short-term trend following.

## Theoretical Foundation

**Conservative Belief Updating**:
- Theory / Study: Investor sentiment, conservatism, and underreaction.
- Citation: Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0
- Core Insight: Investors can underreact to fundamental information and update beliefs slowly, producing delayed correction and predictable price dynamics. Conservative learning is stabilising but not instantaneous.
- Mathematical Formulation: `belief_t = belief_{t-1} + beta * (F_t - belief_{t-1})`.
- Empirical Evidence: Behavioral-finance evidence links underreaction to momentum and later reversal.
- Relevance to This Agent: The agent trades on price deviation from smoothed belief, not directly from `F`.
- Calibration Source: Barberis, Shleifer & Vishny (1998).
- Falsification Conditions: If `belief_t` jumps instantly to `F_t` with `beta < 1`, conservative learning is absent.
- Alternative Theories: RationalUpdater's immediate update; limits to arbitrage.

**Limits to Arbitrage and Slow Convergence**:
- Theory / Study: Limits of arbitrage.
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Even correct beliefs may not immediately eliminate mispricing when capital or institutional constraints limit trading. Slow convergence can therefore coexist with fundamental analysis.
- Mathematical Formulation: `Q = min(base_position_size, abs(dev) * sizing_scale)`.
- Empirical Evidence: The source scenario uses this literature to explain why convergence is slow despite correct beliefs.
- Relevance to This Agent: The agent corrects mispricing gradually through smoothed beliefs and capped orders.
- Calibration Source: Shleifer & Vishny (1997); Barberis, Shleifer & Vishny (1998).
- Falsification Conditions: If the agent eliminates mispricing instantly despite low `learning_rate`, its constraints are not represented.
- Alternative Theories: full rational updating.

## Design Purpose and Activation Triggers

Purpose: Provide slow, stabilising fundamental correction through conservative belief updating.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `belief` initialized

Missing-Signal Policy: hold if `price` or `fundamental` is unavailable; initialize belief from first valid fundamental.

Activation Triggers:
- `(price - belief) / belief < -threshold`: submit buy order.
- `(price - belief) / belief > threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached: hibernate constrained side.
- Fundamental signal stale: hold.


Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|---|---|---|
| Large `abs(deviation)` | Aggressively trades toward `fundamental` | Sizing is proportional to deviation; capped by `base_position_size` |
| Small `abs(deviation)` | Holds inside the no-trade band | `abs(deviation) < threshold` |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Stabilising | Trades toward smoothed fundamental belief. |
| Stress | Stabilising | Corrects mispricing gradually without abrupt full-information trading. |

Interaction with other agents: Complements RationalUpdater but acts more slowly; opposes AnchoredTrader and HistoricalAnchor.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|---|---|---|---|---|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. |
| `fundamental` | environment | `float` | yes | Maps to §3.6.1 `fundamental`. |
| `belief` | environment | `float` | yes | Maps to §3.6.1 `belief`. |
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
| `price` | Continuous | 1 tick | Current market price |
| `fundamental` | Continuous | 1 tick | True value input to belief update |
| `belief` | State | persistent | Smoothed valuation estimate |

Does NOT use: `momentum`, `anchor`, `cost_basis`, peer flow.

#### Core Behavioral Mechanism

1. Initialize belief from the first valid fundamental value.
2. Update belief toward fundamental at speed `learning_rate`.
3. Compute deviation between price and belief.
4. Buy when price is below belief by more than threshold.
5. Sell when price is above belief by more than threshold.
6. Hold inside the no-trade band.
7. Keep belief as persistent state across ticks.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current price |
| Order quantity rule | `Q = min(base_position_size, abs(dev) * sizing_scale)` |
| Order lifetime | 1 tick |
| Cancellation policy | unfilled orders expire at end of tick |
| Inventory constraint | inventory bounded by `inventory_max` |
| Wealth / leverage cap | cash >= 0; no margin |
| Stop-loss / kill rule | none |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Trigger function:
  ```
  belief_t = belief_{t-1} + beta * (F_t - belief_{t-1})
  dev = (P_t - belief_t) / belief_t
  buy if dev < -theta
  sell if dev > theta
  otherwise hold
  ```
- Sizing function:
  ```
  Q = -sign(dev) * min(base_position_size, abs(dev) * sizing_scale)
  ```
- State variables: `belief`; `position`; `cash`.
- State-update rule: update belief pre-decision; update position and cash post-fill.
- Determinism contract: deterministic given signals, state, and parameters.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `beta` | belief learning rate | 0.20 | Barberis, Shleifer & Vishny (1998) |
| `theta` | belief deviation threshold | 0.02 | Standardised |

#### Behavioral Properties

- Time horizon: long, because belief changes gradually.
- Risk tolerance: medium.
- Information asymmetry: none.
- Psychological profile: conservatism and slow belief updating.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `learning_rate` | float | 0.20 | [0, 1] | high | Speed of belief movement toward fundamental. | Higher -> faster correction and less conservatism. | Barberis, Shleifer & Vishny (1998) |
| `threshold` | float | 0.02 | [0, 1] | high | Deviation from belief needed to trade. | Higher -> fewer trades and wider belief-price gap. | Standardised |
| `base_position_size` | float | 20.0 | > 0 | medium | Maximum order size. | Higher -> stronger correction. | Standardised |
| `sizing_scale` | float | 1000.0 | > 0 | medium | Converts belief deviation into quantity. | Higher -> more aggressive belief-based trading. | Standardised |
| `inventory_max` | float | 200.0 | > 0 | low | Inventory cap. | Higher -> more correction capacity. | Standardised |

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | iid learning-rate draws |
| Heterogeneity per parameter | `learning_rate -> Uniform(0.1, 0.4)` |
| Cross-agent correlation | none |
| Identity persistence | belief persists within episode |

## Worked Numerical Examples

### Case 1 - Sell overvaluation
```text
Market state: P=105, F=100, prior belief=102, beta=0.2.
Calculation: belief=102+0.2*(100-102)=101.6; dev=(105-101.6)/101.6=0.033.
Decision: sell 20.
State update: belief=101.6; position -20; cash +2100.
```

### Case 2 - Buy undervaluation
```text
Market state: P=97, F=100, prior belief=101.
Calculation: belief=100.8; dev=(97-100.8)/100.8=-0.038.
Decision: buy 20.
State update: belief=100.8; position +20; cash -1940.
```

### Case 3 - Hold
```text
Market state: P=101, F=100, prior belief=101.5.
Calculation: belief=101.2; dev=-0.002.
Decision: hold.
State update: belief=101.2.
```

### Edge Case - Initial belief
```text
Market state: P=100, F=100, belief unset.
Calculation: initialize belief=100; dev=0.
Decision: hold.
State update: belief persists as 100.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `learning_rate` <- Barberis, Shleifer & Vishny (1998).

**Expected stylized facts** when this agent dominates the population:
- Gradual price correction toward fundamentals.
- Slower response than RationalUpdater.
- Bounded sustained mispricing.

**Sanity bounds (red flags during simulation)**:
- IF the agent exhibits the behaviour described (Belief ignores fundamental forever) THEN the implementation is broken because belief ignores fundamental forever.
- IF the agent exhibits the behaviour described (Belief jumps instantly when `learning_rate < 1`) THEN the implementation is broken because belief jumps instantly when `learning_rate < 1`.
- IF the agent exhibits the behaviour described (Agent trades on momentum rather than belief deviation) THEN the implementation is broken because agent trades on momentum rather than belief deviation.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `instant_learning` | `learning_rate = 1.0` | Turns the agent into a rational updater. |
| `very_slow_learning` | `learning_rate = 0.02` | Strong conservatism increases deviation persistence. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Conservative updating |
| 2 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Limits to arbitrage and slow convergence |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AGenticFinLab |
| Reviewed by | audit_agent_handbook.py v1 |
| Created | 2026-06-27 |
| Version | 1.0.3 |
| Change log  | 1.0.0 - Created from AnchoringEffect Agent Design Summary row 4.8; 1.0.1 - Structural conformance upgrade (added Behavioral Tendency, Behavioral Adaptation, Environmental Dependencies, §3.6.0 I/O Contract, IF-THEN sanity bounds, Author/Change log provenance rows); 1.0.2 - Structural conformance upgrade (added Behavioral Tendency, Behavioral Adaptation, Environmental Dependencies, §3.6.0 I/O Contract, IF-THEN sanity bounds, Author/Change log provenance rows); 1.0.3 - Structural conformance upgrade (added Behavioral Tendency, Behavioral Adaptation, Environmental Dependencies, §3.6.0 I/O Contract, IF-THEN sanity bounds, Author/Change log provenance rows) |
| Status | conformant |
| Icon        | ![](../agent_images/icons/finance-fundamental-analyst.png) |
