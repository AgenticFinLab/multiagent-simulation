# Fundamental value anchor trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Fundamental value anchor trader |
| Theory Family         | Asset Pricing / Limits of Arbitrage |
| Behavioral Tendency   | **Converging — trades against mispricing to pull price toward fundamental value; provides long-run gravitational force against overshoot** |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a value-oriented investor who trades against perceived mispricing relative to a known fundamental value. The real-world counterpart is a fundamental hedge fund, deep-value investor, or institutional asset manager who perceives intrinsic value through analysis and trades when price deviates sufficiently from that estimate. Such participants provide the corrective force that limits price overshoot in both directions.

The decision goal is to output a buy, sell, or hold market order with quantity scaled by the magnitude of mispricing. The agent optimises for convergence profit: buying when price is below fundamental and selling when price is above, with a minimum threshold to avoid excessive trading on noise.

In simulation this agent acts as the gravitational anchor that pulls price back toward fundamental value after momentum-driven excursions. It counterbalances trend-followers and noise traders. Non-goals: (1) the agent MUST NOT chase price trends or use technical indicators; (2) the agent MUST NOT provide continuous two-sided quotes like a market maker.

## Theoretical Foundation

**Limits of Arbitrage**:
- Theory / Study: The limits of arbitrage.
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Real-world arbitrageurs face capital constraints and agency problems that prevent them from fully correcting mispricing instantaneously. They trade against mispricing only when the deviation is large enough to compensate for risk and constraints, creating a threshold-based response rather than perfect correction.
- Mathematical Formulation: `mispricing = (fundamental - price) / price`; trade only when `|mispricing| > value_threshold`.
- Empirical Evidence: Shleifer & Vishny document that arbitrage capital withdraws during extreme dislocations; empirical studies of hedge fund flows confirm pro-cyclical capital allocation with an average threshold of 3-8% deviation before significant position-building (Mitchell & Pulvino, 2001).
- Relevance to This Agent: The agent operationalises the limited-arbitrageur by trading against mispricing only beyond a threshold and subject to a capacity constraint (50% of available capacity), reflecting real-world capital limitations.
- Calibration Source: Shleifer & Vishny (1997); value_threshold of 5% from empirical observation of hedge fund entry points documented in Mitchell & Pulvino (2001, JF).
- Falsification Conditions: If the agent trades in the same direction as mispricing (buys overvalued, sells undervalued), the corrective mechanism is falsified.
- Alternative Theories: Efficient markets (instant correction, no threshold); behavioural finance (permanent mispricing); noise trader risk (corrective force may be overwhelmed).

**Fundamental Value as Price Anchor**:
- Theory / Study: On the impossibility of informationally efficient markets.
- Citation: Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408. https://doi.org/10.2307/1805228
- Core Insight: Informed traders who observe fundamental value are compensated for their information-acquisition cost through profits from trading against mispricing. The equilibrium price lies between uninformed noise and full-information fundamental, with the gap proportional to information costs.
- Mathematical Formulation: `P_eq = (1 - λ) × P_uninformed + λ × V_fundamental` where λ depends on the mass of informed traders.
- Empirical Evidence: The Grossman-Stiglitz paradox implies equilibrium mispricing of 2-10% in typical markets, consistent with observed value premiums (Fama & French, 1993, value factor HML averages ~5% annually).
- Relevance to This Agent: Justifies why the agent observes fundamental value and trades proportionally against mispricing; the threshold reflects equilibrium information costs.
- Calibration Source: Fama & French (1993): HML factor ~5% annually; threshold=5% deviation.
- Falsification Conditions: If the agent holds when mispricing exceeds 3× the value_threshold (15%), the position-building response is too slow for a value trader.
- Alternative Theories: Behavioural anchoring (anchored to stale estimate); adaptive expectations.

## Design Purpose and Activation Triggers

Purpose: Provide corrective pressure against mispricing by buying undervalued assets and selling overvalued assets relative to fundamental value.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `fundamental` available (true fundamental value from environment)

Missing-Signal Policy: If `fundamental` is unavailable or stale, hold. If `price` is unavailable, hold.

Activation Triggers:
- `mispricing > value_threshold` (price below fundamental by >5%): submit buy order.
- `mispricing < -value_threshold` (price above fundamental by >5%): submit sell order.
- `<Default>`: hold (mispricing within tolerance band).

Deactivation Conditions:
- Position at `max_position`: hibernate buy side.
- Position at `-max_position`: hibernate sell side.
- Mispricing within tolerance band `[-value_threshold, +value_threshold]`: hold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Large mispricing (>3× threshold) | Trades at full 50% capacity; more aggressive correction | Sizing scales linearly with mispricing magnitude |
| Near-threshold mispricing (1-2× threshold) | Smaller positions; cautious entry | 50% capacity × mispricing yields modest size |

Environmental Dependencies: Requires a `fundamental` value signal from the environment (exogenous or scenario-defined). None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price; maps to §3.6.1. |
| `fundamental` | environment | `float` | yes | True fundamental value; maps to §3.6.1. |
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
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action` (buy=increases long exposure, sell=decreases long exposure or goes short).
- Determinism markers: decision is deterministic given identical price, fundamental, and position state; no seed emitted.

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
| `price` | Continuous | 1 tick | Current market price for mispricing calculation [Ref 1] |
| `fundamental` | Continuous | 1 tick | True value anchor for computing deviation [Ref 2] |
| `position` | Discrete | current | Required for capacity constraint [Ref 1] |

Does NOT use: `price_history`, moving averages, technical indicators, peer trades, sentiment data, volume.

#### Core Behavioral Mechanism

1. **Read** current `price`, `fundamental`, and `position`. *(implementation convenience)*
2. **Compute** `mispricing` = (`fundamental` - `price`) / `price`. *(Traces to Shleifer & Vishny 1997 — deviation from fair value.)*
3. **Evaluate** activation: if `mispricing > value_threshold`, set direction = buy (undervalued); if `mispricing < -value_threshold`, set direction = sell (overvalued); otherwise set direction = hold. *(Traces to Shleifer & Vishny 1997 — threshold-based arbitrage.)*
4. **Compute** available capacity: if buy, `capacity` = `max_position` - `position`; if sell, `capacity` = `max_position` + `position`. *(Traces to Shleifer & Vishny 1997 — capital constraints.)*
5. **Compute** raw quantity: `raw_qty` = `scale` × abs(`mispricing`) × (`capacity` × 0.5). The 0.5 factor reflects the 50% capacity constraint. *(Traces to Grossman & Stiglitz 1980 — gradual position building.)*
6. **Clamp** quantity: `quantity` = max(0, min(int(`raw_qty`), `capacity`)). *(implementation convenience)*
7. **Write** decision output with action, quantity, and reasoning. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price; no limit price. |
| Sizing rule | `quantity = int(scale × abs(mispricing) × capacity × 0.5)` clamped to [0, available_capacity] |
| Action lifetime | 1 tick (immediate execution or expiry) |
| Revision policy | No revision; each tick produces a fresh independent decision |
| State constraint | Position bounded by `[-max_position, +max_position]` (self-imposed) |
| Resource cap | Cash >= 0; 50% of available capacity per trade (self-imposed prudence) |
| Exit rule | None (agent trades whenever mispricing exceeds threshold) |

#### Mathematical Model

**Decision output:** Signed trade quantity `Q(t)` ∈ integers, and discrete action ∈ {buy, sell, hold}.

**Decision logic formalization:**

```
mispricing(t) = (V_fundamental - P(t)) / P(t)

IF mispricing(t) > θ_value:
    action = buy
    capacity = Q_max - pos(t)
    Q(t) = int(scale × mispricing(t) × capacity × 0.5)
    Q(t) = clamp(Q(t), 0, capacity)
ELIF mispricing(t) < -θ_value:
    action = sell
    capacity = Q_max + pos(t)
    Q(t) = int(scale × |mispricing(t)| × capacity × 0.5)
    Q(t) = clamp(Q(t), 0, capacity)
ELSE:
    action = hold
    Q(t) = 0
```

**State variables:**

| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | 0 |
| `cash` | float | initial_cash (scenario-defined) |

**State evolution:**
- Pre-decide: no state updates required.
- Post-execution: `position += Q(t)` if buy; `position -= Q(t)` if sell. `cash -= Q(t) × price` if buy; `cash += Q(t) × price` if sell.

**Determinism contract:** Deterministic given identical price, fundamental, and position state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `θ_value` | Value threshold for activation | 0.05 | Shleifer & Vishny (1997) |
| `scale` | Mispricing-to-quantity multiplier | 1.5 | Standardised |
| `Q_max` | Maximum absolute position | 50 | Standardised |

#### Behavioral Properties

- Time horizon: medium, because the agent responds to current-tick mispricing but builds positions gradually over multiple ticks.
- Risk tolerance: medium, because the 50% capacity constraint and threshold filter prevent extreme position-taking.
- Information asymmetry: partial; the agent observes true fundamental value which other agents may not.
- Psychological profile: rational value assessment with constraints; no cognitive biases modelled; represents the textbook informed trader.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `value_threshold` | float | 0.05 | [0.01, 0.20] | high | Minimum mispricing required to trigger a trade. | Higher -> fewer trades, larger deviations persist longer. | Shleifer & Vishny (1997); Mitchell & Pulvino (2001) |
| `scale` | float | 1.5 | [0.5, 5.0] | high | Multiplier converting mispricing magnitude to order size. | Higher -> more aggressive correction per unit mispricing. | Standardised |
| `max_position` | int | 50 | [10, 200] | medium | Maximum absolute position (long or short). | Higher -> greater corrective capacity before cap binds. | Standardised |
| `capacity_fraction` | float | 0.5 | [0.1, 1.0] | medium | Fraction of available capacity used per trade. | Higher -> faster convergence but more capital risk. | Shleifer & Vishny (1997) |

## Worked Numerical Examples

### Case 1 — Buy signal (price below fundamental)
```text
System state: price=95; fundamental=100; position=0; max_position=50; scale=1.5; value_threshold=0.05.
Calculation:
  mispricing = (100 - 95) / 95 = 5/95 = 0.0526
  mispricing > 0.05: action = buy
  capacity = 50 - 0 = 50
  raw_qty = 1.5 × 0.0526 × 50 × 0.5 = 1.5 × 0.0526 × 25 = 1.97
  quantity = int(1.97) = 1
Decision: buy, quantity=1.
State update: position: 0 -> 1; cash reduced by 1 × 95.
```

### Case 2 — Sell signal (price above fundamental)
```text
System state: price=112; fundamental=100; position=10; max_position=50; scale=1.5; value_threshold=0.05.
Calculation:
  mispricing = (100 - 112) / 112 = -12/112 = -0.1071
  mispricing < -0.05: action = sell
  capacity = 50 + 10 = 60
  raw_qty = 1.5 × 0.1071 × 60 × 0.5 = 1.5 × 0.1071 × 30 = 4.82
  quantity = int(4.82) = 4
Decision: sell, quantity=4.
State update: position: 10 -> 6; cash increased by 4 × 112.
```

### Case 3 — Hold (mispricing within threshold)
```text
System state: price=98; fundamental=100; position=5; max_position=50; scale=1.5; value_threshold=0.05.
Calculation:
  mispricing = (100 - 98) / 98 = 2/98 = 0.0204
  |mispricing| < 0.05: action = hold
  quantity = 0
Decision: hold, quantity=0.
State update: no change.
```

### Edge Case — Position cap reached
```text
System state: price=80; fundamental=100; position=50; max_position=50; scale=1.5; value_threshold=0.05.
Calculation:
  mispricing = (100 - 80) / 80 = 20/80 = 0.25
  mispricing > 0.05: action = buy
  capacity = 50 - 50 = 0
  raw_qty = 1.5 × 0.25 × 0 × 0.5 = 0
  quantity = 0
Decision: hold (capacity exhausted), quantity=0.
State update: no change. Buy side hibernated.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `value_threshold` <- Shleifer & Vishny (1997); hedge fund entry thresholds of 3-8% documented in Mitchell & Pulvino (2001).
- `scale` <- Standardised; calibrated to produce meaningful position sizes given typical mispricing magnitudes.
- `capacity_fraction` <- Shleifer & Vishny (1997): limited capital deployment per opportunity.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price 10% below fundamental and empty position, agent MUST generate a buy order within the same tick.
- Given price 10% above fundamental and positive position, agent MUST generate a sell order within the same tick.
- Given price within 5% of fundamental, agent MUST hold regardless of position.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys when price is above fundamental (mispricing negative), THEN implementation is broken because direction is inverted.
- IF the agent trades when |mispricing| < value_threshold, THEN implementation is broken because threshold filter is not applied.
- IF the agent's position exceeds max_position in absolute value, THEN implementation is broken because position cap is not enforced.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_value_anchor` | `value_threshold = 1.0` | Removing value correction allows unbounded price drift. | Increase in price deviation from fundamental. | Mean absolute mispricing over 100 ticks. |
| `aggressive_value` | `scale = 4.0` | Stronger correction force pulls price back faster. | Decrease in mispricing half-life. | Ticks to 50% mispricing reduction. |
| `tight_threshold` | `value_threshold = 0.02` | Lower threshold increases trade frequency. | Increase in agent trade count. | Trades per 100 ticks. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Primary theory: constrained arbitrage and threshold trading. |
| 2 | Grossman, S. J., & Stiglitz, J. E. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408. https://doi.org/10.2307/1805228 | Informed trader equilibrium and value anchor justification. |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
