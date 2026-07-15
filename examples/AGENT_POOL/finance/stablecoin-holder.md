# Stablecoin holder redeeming on confidence collapse

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Stablecoin holder redeeming on confidence collapse |
| Theory Family         | Algorithmic Stablecoin Mechanism Design |
| Behavioral Tendency   | **Diverging** — redemptions amplify de-peg pressure, pushing price further from the $1.00 parity target |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a retail or institutional holder of an algorithmic stablecoin who redeems exposure when confidence in the peg breaks. The real-world counterpart is a stablecoin depositor or holder — drawn from the participant taxonomy: (1) stablecoin holders, (2) DeFi lenders, (3) yield depositors, (4) arbitrageurs, (5) market makers, (6) speculative attackers, (7) protocol treasuries. The behaviour documented in the UST/LUNA collapse of May 2022 shows holders redeeming en masse once the peg deviation exceeds a psychological threshold.

The decision goal is to produce a sell order (redemption) of a fixed fraction of remaining position when the observed price deviation from parity exceeds a configurable threshold. The agent optimises capital preservation by exiting before deeper collapse.

In simulation this agent exhibits panic-redemption behaviour that feeds the death-spiral mechanism: each redemption increases sell pressure, widening the deviation, which triggers more redemptions. Non-goals: (1) this agent MUST NOT attempt arbitrage or buy-the-dip strategies; (2) this agent MUST NOT consider yield or staking incentives in its decision logic.

## Theoretical Foundation

**Algorithmic Stablecoin Death Spiral**:
- Theory / Study: Algorithmic stablecoin mechanism design and failure modes
- Citation: Klages-Mundt, A., Harz, D., Gudgeon, L., Liu, J.-Y., & Minca, A. (2020). Stablecoins 2.0: Economic Foundations and Risk-based Models. *Proceedings of the 2nd ACM Conference on Advances in Financial Technologies*, 59-79. DOI:10.1145/3419614.3423261
- Core Insight: Algorithmic stablecoins face inherent fragility where confidence loss triggers redemptions that further undermine collateral backing, creating a self-reinforcing death spiral. The feedback loop between redemption demand and declining reserves makes the system vulnerable to bank-run dynamics.
- Mathematical Formulation: `sell_qty = floor(|position| × sell_fraction) if (price - parity) / parity < -redemption_threshold else 0`
- Empirical Evidence: The UST de-peg event of May 7-13, 2022 saw $18B in redemptions over 6 days with deviation accelerating from -2% to -99%. Kwon (2022) post-mortem analysis showed redemption cascades with >50% of holders exiting within 48 hours of the -8% threshold breach.
- Relevance to This Agent: The agent operationalises the holder-level redemption decision that aggregates into the macro death spiral.
- Calibration Source: Klages-Mundt et al. (2020) Table 2 reports critical deviation thresholds between 5-30% depending on collateral type; Levy (2022) documents median holder exit at 8-12% deviation.
- Falsification Conditions: If this agent fails to sell within one tick of deviation exceeding `redemption_threshold`, the confidence-break mechanism is falsified.
- Alternative Theories: Rational expectations (holders wait for recovery); coordination game (holders condition on peer behaviour rather than price alone).

**Death Spiral Dynamics**:
- Theory / Study: Death spiral dynamics in algorithmic stablecoins
- Citation: Levy, A. (2022). Understanding the Instability of Algorithmic Stablecoins. *Working Paper*, Princeton University. arXiv:2209.01182
- Core Insight: Once redemptions exceed the protocol's absorption capacity, the feedback between declining collateral value and accelerating redemptions becomes self-reinforcing. The system exhibits a critical threshold below which recovery is impossible regardless of intervention.
- Mathematical Formulation: `dP/dt = -k × redemption_flow / liquidity_depth` where k is the price-impact coefficient
- Empirical Evidence: Levy documents that UST holders exhibited a median exit threshold of 10% deviation, with 90% of remaining holders exiting by 25% deviation. The time from 10% to 50% deviation was less than 12 hours.
- Relevance to This Agent: Each individual redemption decision contributes marginally to the aggregate flow that drives the spiral; this agent represents one such individual decision unit.
- Calibration Source: Levy (2022) Section 4.2, Table 3: holder exit distribution N(0.10, 0.05) across surveyed wallets.
- Falsification Conditions: If this agent holds position unchanged while deviation exceeds 2× its threshold for more than 5 ticks, the death-spiral participation is falsified.
- Alternative Theories: Gradual exit (uniform selling rate regardless of deviation); herding (condition on observed peer redemptions rather than price).

## Design Purpose and Activation Triggers

Purpose: Exhibit panic redemption behaviour when the stablecoin deviates from parity beyond a confidence threshold.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current stablecoin price)
- `parity` available (reference peg value, typically 1.0)

Missing-Signal Policy: hold if either `price` or `parity` is unavailable or NaN; retain full position until signals resume.

Activation Triggers:
- `deviation < -redemption_threshold`: sell `floor(|position| × sell_fraction)` units.
- `<Default>`: hold — no action.

Deactivation Conditions:
- Position reaches zero: no further sells possible; agent becomes inert.
- Price recovers above parity: agent holds remaining position without further redemption.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Deepening de-peg (deviation worsens each tick) | Continues selling each tick as threshold remains breached | Stateless check: threshold test fires every tick position > 0 |
| Recovery above threshold | Immediately stops selling; holds remaining position | Threshold gate no longer satisfied |

Environmental Dependencies: Requires a per-tick `price` feed and a constant or slowly-updating `parity` reference. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. Current stablecoin market price. |
| `parity` | environment / config | `float` | yes | Maps to §3.6.1 `parity`. Reference peg value (default 1.0). |
| `position` | agent's own persisted state | `int` | yes | Current token holdings; populated by §3.6.4 init. |
| `cash` | agent's own persisted state | `float` | yes | Current cash balance. |
| `identity`, `round` | scheduler / round header | `str`, `int` | yes | Round number and agent identity per implement-simulation-skill naming rule. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"sell", "hold"}` | — | yes | Discrete action selected this call. |
| `quantity` | int | `[0, position]` | tokens | yes | Number of tokens to redeem/sell. 0 when hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY this decision was made. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, position]`; out-of-range values MUST be clamped before emission.
- Units and sign conventions: `quantity` is unsigned; the `sell` action implies direction. Price units match `parity` denomination.
- Determinism markers: decision is deterministic given identical inputs and state; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<sell or hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for:
1. Signal wiring — every input row MUST map to a real read against the environment/state.
2. Decision emission — code MUST populate every Required=yes field and clamp out-of-range values.
3. Prompt drafting — model-driven variants MUST spell out the tag pattern and JSON schema literally.
4. Parser tests — implementation MUST include a smoke test verifying tag presence and JSON validity.
5. Variant parity — every declared variant MUST produce output objects with the SAME field set.
6. Contract-versus-prose conflict — if mechanism or action space seems to contradict this contract, this section wins.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current stablecoin price needed for deviation calculation [Ref 1] |
| `parity` | Continuous | 1 tick | Reference peg target for deviation measurement [Ref 1] |

Does NOT use: `fundamental` (distinct from parity), order-book depth, peer redemption counts, yield rates, collateral ratios, or any historical price series beyond current tick.

#### Core Behavioral Mechanism

1. **Read** `price` and `parity` from environment; **Read** `position` from agent state. *(implementation convenience)*
2. **Compute** deviation: `deviation = (price - parity) / parity`. *(Klages-Mundt et al. 2020 — peg deviation metric)*
3. **Compare** deviation against `-redemption_threshold`. If `deviation >= -redemption_threshold`, proceed to step 7 (hold). *(Levy 2022 — confidence threshold)*
4. **Compute** sell quantity: `sell_qty = floor(abs(position) × sell_fraction)`. *(Levy 2022 — fractional redemption)*
5. **Clamp** sell_qty: `sell_qty = min(sell_qty, position)` to ensure non-negative remaining position. *(implementation convenience)*
6. **Write** decision: emit `action=sell`, `quantity=sell_qty`. Proceed to step 8.
7. **Write** decision: emit `action=hold`, `quantity=0`.
8. **Post-decision state update**: `position -= sell_qty`; `cash += sell_qty × price`. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, hold |
| Action parameter rule | No continuous parameter; action is discrete with integer sizing. |
| Sizing rule | `sell_qty = floor(abs(position) × sell_fraction)`, clamped to `[0, position]` |
| Action lifetime | 1 tick (immediate execution assumed) |
| Revision policy | No revision; once emitted, the sell order stands for the tick. |
| State constraint | `position >= 0` at all times (no short selling). |
| Resource cap | No cap on cumulative sells; limited only by remaining position. |
| Exit rule | Agent becomes inert when `position = 0`. |

#### Mathematical Model

**Decision output**: integer sell quantity `Q(t) >= 0` per tick.

**Decision logic formalization**:
```
deviation(t) = (price(t) - parity) / parity

if deviation(t) < -redemption_threshold AND position(t) > 0:
    Q(t) = floor(position(t) × sell_fraction)
    Q(t) = min(Q(t), position(t))
    action = "sell"
else:
    Q(t) = 0
    action = "hold"
```

**State variables**:
| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | `initial_position` (default 2000) |
| `cash` | float | `initial_cash` (default 500000) |

**State evolution** (post-decision, post-execution):
```
position(t+1) = position(t) - Q(t)
cash(t+1) = cash(t) + Q(t) × price(t)
```

**Determinism contract**: Deterministic given identical price path and parameters. No stochastic element.

**Parameter symbol table**:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `redemption_threshold` | Confidence-break deviation threshold | 0.10 | Levy (2022), Section 4.2 |
| `sell_fraction` | Fraction of position redeemed per trigger | 0.5 | Klages-Mundt et al. (2020) |
| `parity` | Reference peg value | 1.0 | Protocol definition |
| `initial_position` | Starting token holdings | 2000 | Standardised |
| `initial_cash` | Starting cash balance | 500000 | Standardised |

#### Behavioral Properties

- Time horizon: short — reacts within a single tick to current deviation without considering future recovery.
- Risk tolerance: low — prioritises capital preservation through immediate redemption over holding for potential recovery.
- Information asymmetry: none — uses only publicly observable price deviation.
- Psychological profile: Loss aversion and confidence fragility; exhibits bank-run behaviour where the act of exiting is driven by threshold-crossing fear rather than fundamental analysis.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `redemption_threshold` | float | 0.10 | [0.05, 0.30] | high | Deviation threshold that triggers redemption | Higher -> slower to redeem, less destabilising | Levy (2022) Section 4.2 |
| `sell_fraction` | float | 0.5 | (0, 1.0] | high | Fraction of position sold per trigger event | Higher -> faster position liquidation, stronger spiral contribution | Klages-Mundt et al. (2020) Table 2 |
| `initial_cash` | float | 500000 | [0, 10000000] | low | Starting cash balance | Higher -> more capacity to absorb but irrelevant to sell logic | Standardised |
| `initial_position` | int | 2000 | [1, 100000] | medium | Starting stablecoin token holdings | Higher -> more fuel for redemption cascade | Standardised |
| `parity` | float | 1.0 | (0, inf) | low | Reference peg target value | Higher -> deviation measured relative to larger base | Protocol definition |

## Worked Numerical Examples

### Case 1 — Sell triggered (moderate de-peg)
```text
Market state: price=0.88, parity=1.0, position=2000, cash=500000.
Parameters: redemption_threshold=0.10, sell_fraction=0.5.
Calculation:
  deviation = (0.88 - 1.0) / 1.0 = -0.12
  -0.12 < -0.10 → threshold breached
  sell_qty = floor(2000 × 0.5) = 1000
  clamp: min(1000, 2000) = 1000
Decision: action=sell, quantity=1000.
State update: position: 2000 -> 1000; cash: 500000 -> 500000 + 1000×0.88 = 500880.
```

### Case 2 — Hold (within threshold)
```text
Market state: price=0.93, parity=1.0, position=2000, cash=500000.
Parameters: redemption_threshold=0.10, sell_fraction=0.5.
Calculation:
  deviation = (0.93 - 1.0) / 1.0 = -0.07
  -0.07 >= -0.10 → threshold NOT breached
Decision: action=hold, quantity=0.
State update: position: 2000 (unchanged); cash: 500000 (unchanged).
```

### Case 3 — Sell triggered (severe de-peg, partial position remaining)
```text
Market state: price=0.50, parity=1.0, position=500, cash=501760.
Parameters: redemption_threshold=0.10, sell_fraction=0.5.
Calculation:
  deviation = (0.50 - 1.0) / 1.0 = -0.50
  -0.50 < -0.10 → threshold breached
  sell_qty = floor(500 × 0.5) = 250
  clamp: min(250, 500) = 250
Decision: action=sell, quantity=250.
State update: position: 500 -> 250; cash: 501760 -> 501760 + 250×0.50 = 501885.
```

### Edge Case — Position exhausted
```text
Market state: price=0.70, parity=1.0, position=0, cash=502600.
Parameters: redemption_threshold=0.10, sell_fraction=0.5.
Calculation:
  deviation = (0.70 - 1.0) / 1.0 = -0.30
  -0.30 < -0.10 → threshold breached
  sell_qty = floor(0 × 0.5) = 0
  clamp: min(0, 0) = 0
Decision: action=hold, quantity=0 (no position to sell).
State update: position: 0 (unchanged); cash: 502600 (unchanged). Agent is inert.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `redemption_threshold` <- Levy (2022) Section 4.2, median holder exit threshold 8-12%, central value 10%.
- `sell_fraction` <- Klages-Mundt et al. (2020) Table 2, observed partial redemption rates 40-60%.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price=0.85 and threshold=0.10, agent MUST sell exactly floor(position×0.5) tokens.
- Given price=0.95 and threshold=0.10, agent MUST hold with quantity=0.
- Given position=0 regardless of deviation, agent MUST emit hold with quantity=0.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells when deviation is above -redemption_threshold THEN implementation is broken because the confidence-break condition is not met.
- IF the agent emits a negative quantity or quantity exceeding position THEN implementation is broken because the clamp logic is missing.
- IF the agent buys at any point THEN implementation is broken because this agent has no buy action in its action space.
- IF the agent's position increases between ticks THEN implementation is broken because only sells are permitted.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `tight_threshold` | `redemption_threshold = 0.05` | Lower threshold accelerates cascade onset | Increase in early-round sell volume | Cumulative tokens sold by tick 10 |
| `slow_redemption` | `sell_fraction = 0.2` | Lower fraction extends the cascade duration | Decrease in per-tick sell volume, increase in total ticks active | Ticks until position reaches zero |
| `no_redemption` | `sell_fraction = 0.0` | Removing redemption eliminates this agent's spiral contribution | No sells emitted regardless of deviation | Total quantity sold = 0 |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Klages-Mundt, A., Harz, D., Gudgeon, L., Liu, J.-Y., & Minca, A. (2020). Stablecoins 2.0: Economic Foundations and Risk-based Models. *Proceedings of the 2nd ACM Conference on Advances in Financial Technologies*, 59-79. DOI:10.1145/3419614.3423261 | Algorithmic stablecoin fragility and mechanism design |
| 2 | Levy, A. (2022). Understanding the Instability of Algorithmic Stablecoins. *Working Paper*, Princeton University. arXiv:2209.01182 | Death spiral dynamics, holder exit thresholds |
| 3 | Goldstein, I., & Pauzner, A. (2005). Demand-Deposit Contracts and the Probability of Bank Runs. *Journal of Finance*, 60(3), 1293-1327. DOI:10.1111/j.1540-6261.2005.00762.x | Bank-run coordination game foundations |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-stablecoin-holder.png)         |
