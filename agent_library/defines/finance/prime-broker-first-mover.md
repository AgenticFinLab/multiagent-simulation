# First-mover prime-broker liquidator

## Summary

| Field                 | Content                                                                                            |
|-----------------------|----------------------------------------------------------------------------------------------------|
| Archetype             | first-mover prime-broker liquidator                                                                |
| Theory Family         | Leverage / Risk-On-Risk-Off                                                                        |
| Behavioral Tendency   | **Diverging — leads the margin-call liquidation cascade; pushes price away from pre-crisis equilibrium** |
| Market Role           | **Destabilising** - early liquidation protects collateral value but accelerates fire-sale pressure |
| Time Horizon          | short                                                                                              |
| Risk Tolerance        | medium                                                                                             |
| Information Asymmetry | partial                                                                                            |
| Determinism           | deterministic                                                                                      |
## Definition and Goals

This agent models a prime broker / dealer liquidating client collateral in a finance liquidation setting, using the market-trading domain palette from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. It is intentionally intrinsic: it defines the participant's signals, decision discipline, state, and self-imposed trading constraints, not matching-engine rules or message topology. The real-world counterpart and role are evidenced by the references in the theoretical foundation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `bid_price` and `quantity`. The agent optimizes the role-specific criterion shown in the mathematical model: maximize private collateral recovery by selling when collateral-quality deviation breaches the broker threshold.

Inside a market simulation this agent transmits borrower distress into market-wide selling through creditor-run incentives. It contributes to stylized facts from the finance catalogue: liquidity black holes, capitulation tail, volume spikes around news, co-movement in factor returns, and price-impact concavity where applicable. Non-goals: it must not quote two-sided market-making liquidity unless explicitly listed in Action Space, and it must not use hidden peer-network topology or environment-imposed rules as part of its intrinsic design.

## Theoretical Foundation

**Creditor run and first-mover liquidation**:
- Theory / Study: Run incentives among collateralised creditors.
- Citation: Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016
- Core Insight: When several creditors can liquidate similar collateral, earlier sellers receive better prices because later sellers face price impact from prior liquidation. The private incentive to run can dominate collective value preservation.
- Mathematical Formulation: `payoff_i = q_i * P(t_i)`, with `P(t_i) > P(t_j)` when `t_i < t_j` during liquidation pressure.
- Empirical Evidence: Gorton & Metrick (2012) document run-like rollover behaviour when collateral quality deteriorates; Archegos post-mortems show first movers lost less than late movers.
- Relevance to This Agent: The liquidation threshold and sell fraction encode the broker's private recovery race.
- Calibration Source: Gorton & Metrick (2012); Archegos broker-loss comparisons reported in regulatory and bank post-mortems.
- Falsification Conditions: If earlier threshold settings do not improve selling price, first-mover advantage is not represented.
- Alternative Theories: coordinated workout; patient liquidation.

## Design Purpose and Activation Triggers

Purpose: Liquidate client collateral when collateral-value deterioration crosses the broker threshold.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `position` available as internal collateral inventory

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation < liquidation_threshold`: submit sell order sized by `position * liquidation_sell_ratio`.
- `<Default>`: hold.

Deactivation Conditions:
- Collateral inventory exhausted: hold.
- Deviation above threshold: hold.


Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|---|---|---|
| Counterparty leverage above `trigger_level` | Leads the liquidation cascade by selling first | Binary liquidation rule fires on first-mover signal |
| Market depth thin | Sells in smaller clips to avoid self-impact | Order size is clipped by `max_clip` |

Environmental Dependencies: Requires a per-tick `price` feed and a counterparty-leverage signal. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime                     | Contribution  | Mechanism                                                       |
|----------------------------|---------------|-----------------------------------------------------------------|
| Calm market                | Hold          | No liquidation while collateral value remains inside threshold. |
| Liquidity stress / drought | Destabilising | Sells collateral into weakening demand.                         |
| Crash / cascade            | Destabilising | Repeated sell decisions reinforce price impact.                 |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash, position, and state variables.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|---|---|---|---|---|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. |
| `fundamental` | environment | `float` | yes | Maps to §3.6.1 `fundamental`. |
| `deviation` | environment | `float` | yes | Maps to §3.6.1 `deviation`. |
| `position` | agent state | `float` | yes | Persistent state; see §3.6.4. |
| `identity`, `round` | round header | `str`, `int` | yes | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|---|---|---|---|---|---|
| `action` | enum | {"buy", "sell", "hold", "as", "specified", "by", "the", "trigger", "function"} | — | yes | Discrete action selected this call. |
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

| Signal        | Type       | Memory Window | Rationale                                                                               |
|---------------|------------|---------------|-----------------------------------------------------------------------------------------|
| `price`       | Continuous | 1 tick        | Execution reference and portfolio valuation [Ref 9].                                    |
| `fundamental` | Continuous | 1 tick        | Anchor for collateral-value deviation and discount calculations [Ref 1].                |
| `deviation`   | Continuous | 1 tick        | Primary trigger signal for distress, discount, or information advantage [Ref 1; Ref 3]. |
| `position`    | State      | persistent    | Collateral inventory available to liquidate [Ref 3].                                    |

Does NOT use: social-network topology, undocumented peer thresholds, fee schedules, latency, or matching-engine implementation details.

#### Core Behavioral Mechanism

1. Read: `deviation`, `price`, and `position`; Write: no state before decision.
2. Compare `deviation` with `liquidation_threshold=-0.10` [Ref 3].
3. If threshold is breached, compute `q = min(position, position * liquidation_sell_ratio)` [Ref 3].
4. Emit sell at current price; otherwise hold.
5. Post-fill, reduce collateral position and increase cash by proceeds.

#### Action Space

| Aspect                | Specification                                                                                                                 |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | `buy`, `sell`, `hold` as specified by the trigger function.                                                                   |
| Price level rule      | Use current `price` unless an intrinsic haircut/penalty parameter is declared; hold uses current `price`.                     |
| Order quantity rule   | `q = min(position, position * liquidation_sell_ratio)` for sell; otherwise zero.                                              |
| Order lifetime        | One decision round; replace on next fresh broadcast.                                                                          |
| Cancellation policy   | Cancel prior intent when the current trigger evaluates to hold or the opposite side.                                          |
| Inventory constraint  | Never sell more than internally available long position plus declared short inventory discipline.                             |
| Wealth / leverage cap | Never buy more than available cash divided by current price; leveraged liquidation agents only reduce exposure after trigger. |
| Stop-loss / kill rule | Stop selling when position is exhausted or collateral deviation no longer breaches the threshold.                             |

#### Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`, and `b_t > 0`.

Decision logic formalization:
```
if delta_t < theta_liq:
    a_t = sell; q_t = min(position_t, position_t * phi_liq); b_t = price_t
else:
    a_t = hold; q_t = 0; b_t = price_t
```

State variables:
| State             | Initial value   | Update phase | Evolution                                        |
|-------------------|-----------------|--------------|--------------------------------------------------|
| `cash`            | scenario config | post-fill    | cash decreases on buy and increases on sell.     |
| `position`        | scenario config | post-fill    | position increases on buy and decreases on sell. |
| `liquidated_once` | false           | post-decide  | true after first sell activation.                |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol      | Meaning                                 | Default Value | Source |
|-------------|-----------------------------------------|---------------|--------|
| `theta_liq` | Liquidation deviation threshold         | -0.10         | Ref 3  |
| `phi_liq`   | Fraction of collateral sold per trigger | 0.40          | Ref 3  |

#### Behavioral Properties

- Time horizon: short - prime-broker risk decisions are short-horizon once collateral deteriorates.
- Risk tolerance: medium - risk discipline is balance-sheet protective, not speculative.
- Information asymmetry: partial - observes own client exposure but not all competitor actions.
- Psychological profile: competitive first-mover risk management under run incentives [Ref 3].

## Parameters

| Parameter                | Type  | Default | Valid Range    | Sensitivity | Description                                     | Impact                                       | Source                                                      |
|--------------------------|-------|---------|----------------|-------------|-------------------------------------------------|----------------------------------------------|-------------------------------------------------------------|
| `liquidation_threshold`  | float | -0.10   | [-0.30, -0.03] | high        | Deviation that triggers collateral liquidation. | Higher magnitude -> later liquidation.       | Gorton & Metrick (2012); Archegos broker timing calibration |
| `liquidation_sell_ratio` | float | 0.40    | [0.05, 1.00]   | high        | Fraction of collateral sold per activation.     | Higher -> larger immediate selling pressure. | Gorton & Metrick (2012); post-event broker calibration      |
| `initial_position`       | float | 4000.0  | > 0            | high        | Starting collateral inventory.                  | Higher -> larger liquidation supply.         | Scenario normalization from Archegos exposure reports       |

## Population and Heterogeneity

| Dimension                      | Specification                                                                                                 |
|--------------------------------|---------------------------------------------------------------------------------------------------------------|
| Default population size        | 1 instance in ArchegosCollapse configs.                                                                       |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level +/-10% sweep around listed defaults.                    |
| Heterogeneity per parameter    | Threshold and size parameters may vary within the Valid Range; cash/position scale the agent's market impact. |
| Cross-agent correlation        | Same archetype instances share theory and trigger sign; cash and position levels may differ.                  |
| Identity persistence           | Persistent identity and state across rounds; no type switching.                                               |

## Worked Numerical Examples

### Case 1 - Primary non-hold branch
System state: `price=84`, `fundamental=100`, `deviation=-0.16`, plus default parameters.
Calculation:
  `q = position * 0.40`; sell branch fires because `-0.16 < -0.10`.
Decision: `sell`, positive quantity, `bid_price` determined by price-level rule.
State update: cash and position update post-fill if the order executes.

### Case 2 - Hold branch
System state: `price=96`, `fundamental=100`, `deviation=-0.04`, plus default parameters.
Calculation:
  Trigger conditions are not met under the default threshold set.
Decision: `hold`, `quantity=0`, `bid_price=96`.
State update: no cash or position change.

### Case 3 - Stress branch
System state: `price=88`, `fundamental=100`, `deviation=-0.12`, plus default parameters.
Calculation:
  At `deviation=-0.12`, branch fires for this threshold.
Decision: sell for PrimeBrokerFirstMover-style early threshold; hold for delayed threshold until deeper stress.
State update: cash and position update only if the branch emits a non-hold order.

### Edge Case - Constraint clamp or missing signal
System state: `price` missing or position/cash insufficient.
Calculation:
  Missing signal => hold; insufficient resource => clamp quantity to the available self-imposed resource cap.
Decision: hold or clamped order according to Action Space.
State update: no state becomes negative.

## Validation and Calibration

**Calibration data sources**:
- `liquidation_threshold` <- Gorton & Metrick (2012) run threshold logic and Archegos broker timing.
- `liquidation_sell_ratio` <- liquidation-race payoff calibration from scenario §2 and §8.

**Expected individual behaviour**:
- Given the primary trigger condition, the agent MUST emit the trigger-specified action with positive quantity.
- Given a non-trigger condition, the agent MUST hold.
- Given insufficient cash, position, or signal availability, the agent MUST hold or clamp quantity without violating self-imposed constraints.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits the opposite sign from its trigger branch THEN the mechanism is inverted.
- IF quantity exceeds declared cash/position discipline THEN the implementation violates Action Space.
- IF any listed parameter has no effect on the mathematical model THEN the design has an orphan parameter.

#### Ablation Hooks

| Ablation name      | Setting                                     | Hypothesis tested                                                   | Expected direction | Metric                    |
|--------------------|---------------------------------------------|---------------------------------------------------------------------|--------------------|---------------------------|
| `threshold_strict` | Increase trigger threshold magnitude by 50% | Fewer activations weaken this agent's individual trading intensity. | decrease           | number of non-hold orders |
| `size_half`        | Halve the size parameter                    | Same timing with lower impact.                                      | decrease           | average order quantity    |

## Behavioral Verification and Calibration

- Given deviation = -0.16 (below `liquidation_threshold` of -0.10), agent must emit a sell order with quantity = position * 0.40.
- Given deviation = -0.04 (above `liquidation_threshold` of -0.10), agent must hold with zero quantity.
- Given position is zero (collateral exhausted), agent must hold regardless of deviation magnitude.
- Given a sell is triggered, agent must execute at current price without penalty (distinguishing it from the delayed archetype).
- Given any prerequisite signal is missing or NaN, agent must hold and emit zero quantity without inferring unavailable values.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `threshold_strict` | `liquidation_threshold = -0.15` (50% deeper) | Fewer activations weaken first-mover cascade initiation | decrease | number of non-hold orders per episode |
| `size_half` | `liquidation_sell_ratio = 0.20` | Same timing with lower per-activation impact | decrease | average sell quantity per activation |

## Academic References

| # | Citation                                                                                                                                                                    | Notes                                         |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 3 | Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016 | Creditor run and first-mover liquidation race |
| 9 | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179-207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x           | Price impact and execution-price relevance    |

## Design Provenance and Versioning

| Field   | Content                                                             |
|---------|---------------------------------------------------------------------|
| Author  | Codex                                                               |
| Created | 2026-07-16                                                          |
| Version | 1.0.0                                                               |
| Icon    | ![](../agent_images/icons/finance-prime-broker-first-mover.png)     |
| Status  | draft                                                               |
