# Historical-price anchoring trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Historical-price anchoring trader |
| Theory Family         | Behavioral Finance |
| Behavioral Tendency   | **Converging — trades toward a rolling historical average; converges on a backward-looking reference that lags fundamental regime changes** |
| Market Role           | **Destabilising** - slows adaptation by anchoring on moving historical prices |
| Time Horizon          | long |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |
## Definition and Goals

This agent models an institutional investor or analyst who uses a historical average as the reference value for current price judgments. The real-world counterpart is a fundamentalist or value-oriented analyst who overweights prior comparable prices.

The decision goal is to output buy, sell, or hold orders from the deviation between current price and a rolling historical anchor. It interprets departures from the moving average as mispricing, but adjusts slowly because the average itself embeds past regimes.

In simulation this agent helps produce sustained mispricing relative to fundamentals, long-run reversal, and slow regime transitions. Non-goals: it must not use first-observation anchoring, full Bayesian updating, or short-term momentum as its primary decision rule.

## Theoretical Foundation

**Historical Anchoring and Mean-Reversion Belief**:
- Theory / Study: Expert anchoring and mean-reversion expectations.
- Citation: Kahneman (2011); De Bondt (1993). Citation coverage is limited to references explicitly present in the source scenario file.
- Core Insight: Experts remain influenced by salient historical comparables and often expect prices to revert toward past levels. This can delay adaptation after a genuine fundamental regime change.
- Mathematical Formulation: `perceived_dev = ((P - hist_avg) / hist_avg) * (1 - anchor_weight)`.
- Empirical Evidence: Financial forecast and valuation studies document underreaction to new information when prior values remain salient.
- Relevance to This Agent: The rolling average is the agent's reference point and dampens the perceived size of current deviations.
- Calibration Source: Kahneman (2011); De Bondt (1993).
- Falsification Conditions: If the agent reacts identically to a RationalUpdater, historical anchoring is absent.
- Alternative Theories: Expert anchoring to listed prices (Northcraft & Neale, 1987); overreaction correction (De Bondt & Thaler, 1985).

**Expert Anchoring to Historical Prices**:
- Theory / Study: Expert anchoring in valuation.
- Citation: Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate: An anchoring-and-adjustment perspective on property pricing decisions. *Organizational Behavior and Human Decision Processes*, 39(1), 84-97. https://doi.org/10.1016/0749-5978(87)90046-X
- Core Insight: Professional valuers remain pulled toward prior listed or comparable prices. Expertise reduces but does not eliminate anchoring.
- Mathematical Formulation: `perceived_dev = raw_dev * (1 - anchor_weight)`.
- Empirical Evidence: The source scenario reports expert appraisers anchored toward the listed price.
- Relevance to This Agent: `price_history` acts as the listed/comparable-price reference.
- Calibration Source: Northcraft & Neale (1987); Campbell & Sharpe (2009).
- Falsification Conditions: If longer history does not slow regime adaptation, historical anchoring is not active.
- Alternative Theories: RationalUpdater's immediate use of `fundamental`.

## Design Purpose and Activation Triggers

Purpose: Create path-dependent price support or resistance around a rolling historical anchor.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `price_history` available

Missing-Signal Policy: use available history during warm-up; hold if no price history exists.

Activation Triggers:
- `perceived_dev < -threshold`: submit buy order.
- `perceived_dev > threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- History unavailable or stale: hold.
- Inventory cap reached: hibernate the constrained side.


Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|---|---|---|
| Regime shift in `fundamental` | Perceived deviation remains anchored to stale `hist_avg` until the rolling window catches up | `lookback` window is fixed; older observations dominate until they fall out |
| Extended low-volatility | Tightens `hist_avg` around the current price range, amplifying reaction to small moves | Rolling mean narrows; same `anchor_weight` produces larger perceived deviation |

Environmental Dependencies: Requires a per-tick `price` feed and a `price_history` series of at least one observation. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Context-dependent | Pulls price toward recent history. |
| Stress | Destabilising | Resists fast convergence to a new fundamental regime. |

Interaction with other agents: Overlaps with AnchoredTrader, opposes RationalUpdater, and can conflict with MomentumTrader after reversals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|---|---|---|---|---|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. |
| `price_history` | agent state | `list[float]` | yes | Persistent state; see §3.6.4. |
| `hist_avg` | agent state | `float` | yes | Persistent state; see §3.6.4. |
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
| `price` | Continuous | 1 tick | Current tradable price |
| `price_history` | Series | `lookback` ticks | Rolling reference value |
| `hist_avg` | State | `lookback` ticks | Historical anchor |

Does NOT use: `fundamental`, `deviation`, peer flow.

#### Core Behavioral Mechanism

1. Maintain a rolling price history.
2. Compute `hist_avg` over the last `lookback` ticks.
3. Compute raw deviation from the historical average.
4. Damp the raw deviation by `1 - anchor_weight`.
5. Buy if damped deviation is sufficiently negative.
6. Sell if damped deviation is sufficiently positive.
7. Hold inside the no-trade band.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current observed price |
| Order quantity rule | `Q = min(base_position_size, abs(perceived_dev) * sizing_scale)` |
| Order lifetime | 1 tick |
| Cancellation policy | unfilled orders expire at end of tick |
| Inventory constraint | inventory bounded by `inventory_max` |
| Wealth / leverage cap | cash >= 0; no margin |
| Stop-loss / kill rule | none |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Trigger function:
  ```
  hist_avg = mean(price_history[-lookback:])
  perceived_dev = ((P - hist_avg) / hist_avg) * (1 - anchor_weight)
  buy if perceived_dev < -theta
  sell if perceived_dev > theta
  otherwise hold
  ```
- Sizing function:
  ```
  Q = sign(-perceived_dev) * min(base_position_size, abs(perceived_dev) * sizing_scale)
  ```
- State variables: `price_history` list; `position`; `cash`.
- State-update rule: append price pre-decision; update position and cash post-fill.
- Determinism contract: deterministic given history and parameters.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `w` | historical anchor weight | 0.50 | Kahneman (2011); De Bondt (1993) |
| `L` | rolling lookback | 60 | Standardised |

#### Behavioral Properties

- Time horizon: long, because the rolling history moves slowly.
- Risk tolerance: medium, due to thresholded capped trades.
- Information asymmetry: none.
- Psychological profile: historical anchoring and mean-reversion belief.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `anchor_weight` | float | 0.50 | [0, 1] | high | Weight placed on historical average. | Higher -> weaker perceived deviations and slower adaptation. | Kahneman (2011); De Bondt (1993) |
| `lookback` | int | 60 | int >= 1 | high | Rolling window for historical average. | Higher -> more persistent historical anchor. | Standardised |
| `threshold` | float | 0.03 | [0, 1] | medium | Damped deviation needed to trade. | Higher -> fewer trades. | Standardised |
| `base_position_size` | float | 20.0 | > 0 | medium | Maximum order quantity. | Higher -> stronger historical-anchor pressure. | Standardised |
| `sizing_scale` | float | 1000.0 | > 0 | low | Converts perceived deviation into quantity. | Higher -> larger orders. | Standardised |

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | iid narrow draws |
| Heterogeneity per parameter | `anchor_weight -> Uniform(0.4, 0.6)`, `lookback -> {40, 60, 80}` |
| Cross-agent correlation | none |
| Identity persistence | identical across episodes unless redrawn |

## Worked Numerical Examples

### Case 1 - Buy below history
```text
Market state: P=98, hist_avg=103, anchor_weight=0.5, theta=0.03.
Calculation: perceived_dev=((98-103)/103)*0.5=-0.024.
Decision: hold because -0.024 is inside threshold.
State update: append P=98 to price_history.
```

### Case 2 - Sell above history
```text
Market state: P=110, hist_avg=103.
Calculation: perceived_dev=((110-103)/103)*0.5=0.034.
Decision: sell min(20, 0.034*1000)=20.
State update: position decreases by 20; cash increases by 2200.
```

### Case 3 - Buy after deeper decline
```text
Market state: P=95, hist_avg=103.
Calculation: perceived_dev=((95-103)/103)*0.5=-0.039.
Decision: buy 20 at P=95.
State update: position increases by 20; cash decreases by 1900.
```

### Edge Case - Warm-up history
```text
Market state: P=105, price_history has 3 observations and lookback=60.
Calculation: hist_avg uses the available observations only.
Decision: trade only if damped deviation crosses threshold; otherwise hold.
State update: append P=105.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `anchor_weight` <- expert anchoring and underreaction literature.
- `lookback` <- scenario time-scale calibration.

**Expected stylized facts** when this agent dominates the population:
- Slow regime adaptation.
- Long-run reversal around historical price levels.
- Sustained mispricing when history is stale relative to fundamentals.

**Sanity bounds (red flags during simulation)**:
- IF the agent exhibits the behaviour described (Agent ignores history and trades only on `fundamental`) THEN the implementation is broken because agent ignores history and trades only on `fundamental`.
- IF the agent exhibits the behaviour described (`hist_avg` is recomputed from future prices) THEN the implementation is broken because `hist_avg` is recomputed from future prices.
- IF the agent exhibits the behaviour described (Damped deviation has the wrong sign) THEN the implementation is broken because damped deviation has the wrong sign.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `short_memory` | `lookback = 5` | Short history reduces persistence. |
| `no_dampening` | `anchor_weight = 0` | Removing dampening makes the agent more reactive. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux. | Anchoring synthesis |
| 2 | De Bondt (1993) | Moving-average anchoring; only short citation available in source file |
| 3 | Northcraft, G. B., & Neale, M. A. (1987). Experts, amateurs, and real estate: An anchoring-and-adjustment perspective on property pricing decisions. *Organizational Behavior and Human Decision Processes*, 39(1), 84-97. https://doi.org/10.1016/0749-5978(87)90046-X | Expert anchoring evidence |
| 4 | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369-390. https://doi.org/10.1017/S0022109009090127 | Forecast anchoring and calibration |
| 5 | De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x | Mean-reversion belief |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AGenticFinLab |
| Reviewed by | audit_agent_handbook.py v1 |
| Created | 2026-06-27 |
| Version | 1.0.3 |
| Change log  | 1.0.0 - Created from AnchoringEffect Agent Design Summary row 4.2; 1.0.1 - Structural conformance upgrade (added Behavioral Tendency, Behavioral Adaptation, Environmental Dependencies, §3.6.0 I/O Contract, IF-THEN sanity bounds, Author/Change log provenance rows); 1.0.2 - Structural conformance upgrade (added Behavioral Tendency, Behavioral Adaptation, Environmental Dependencies, §3.6.0 I/O Contract, IF-THEN sanity bounds, Author/Change log provenance rows); 1.0.3 - Structural conformance upgrade (added Behavioral Tendency, Behavioral Adaptation, Environmental Dependencies, §3.6.0 I/O Contract, IF-THEN sanity bounds, Author/Change log provenance rows) |
| Status | conformant |
| Icon        | ![](../agent_images/icons/finance-historical-anchor.png) |
