# Delayed prime-broker liquidator

> **Base archetype:** This file inherits its structure and shared prose from [prime-broker-first-mover.md](./prime-broker-first-mover.md). Sections marked *"identical to base"* are unchanged and link back to the base for the shared content; sections with a **Delta vs. first-mover** callout list what is different. Each archetype keeps its own file and its own generated icon.

## Summary

| Field                 | Content                                                                                                                   |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------|
| Archetype             | delayed prime-broker liquidator                                                                                           |
| Theory Family         | Leverage / Risk-On-Risk-Off                                                                                               |
| Behavioral Tendency   | **Diverging — lags the liquidation wave and then dumps into an already-thin book; diverges from orderly price discovery** |
| Market Role           | **Destabilising** - later liquidation amplifies the cascade and receives worse execution                                  |
| Time Horizon          | short                                                                                                                     |
| Risk Tolerance        | medium                                                                                                                    |
| Information Asymmetry | partial                                                                                                                   |
| Determinism           | deterministic                                                                                                             |

**Delta vs. first-mover:** Market Role wording emphasises *later* liquidation and *worse execution* (vs. the first-mover's *early liquidation / fire-sale acceleration*). All other Summary rows are identical.
## Definition and Goals

Identical to base — see [Definition and Goals](./prime-broker-first-mover.md#definition-and-goals). The same three paragraphs apply: intrinsic prime-broker liquidator, single decision object per call, transmits borrower distress into market-wide selling via creditor-run incentives.

## Theoretical Foundation

**Creditor run and delayed liquidation**:
- Theory / Study: Run incentives among collateralised creditors; delayed liquidation amplifies price impact.
- Citation: Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016
- Core Insight: When several creditors can liquidate similar collateral, earlier sellers receive better prices because later sellers face price impact from prior liquidation. The delayed liquidator arrives after the first-mover cascade and receives worse execution.
- Mathematical Formulation: `payoff_i = q_i * P(t_i) * pi_penalty`, with `pi_penalty < 1` for the delayed archetype.
- Empirical Evidence: Gorton & Metrick (2012) document run-like rollover behaviour; Archegos post-mortems show late movers lost significantly more than first movers.
- Relevance to This Agent: The `price_penalty` parameter encodes the execution haircut for arriving late to the liquidation cascade.
- Calibration Source: Gorton & Metrick (2012); Archegos broker-loss comparisons reported in regulatory and bank post-mortems.
- Falsification Conditions: If the delayed archetype receives the same execution price as the first-mover, the penalty mechanism is absent.
- Alternative Theories: coordinated workout; patient liquidation.

## Design Purpose and Activation Triggers

Identical to base — see [Design Purpose and Activation Triggers](./prime-broker-first-mover.md#design-purpose-and-activation-triggers). Purpose, Call Frequency, Prerequisite Signals, Missing-Signal Policy, Activation Triggers, Deactivation Conditions, Market Contribution by Regime, and Environmental Dependencies are all unchanged; only the numeric value of `liquidation_threshold` differs (see Parameters below).

Behavioral Adaptation by Condition:
| Condition                    | Behavioral change                          | Mechanism                                        |
|------------------------------|--------------------------------------------|--------------------------------------------------|
| First-mover has already sold | Dumps remaining inventory into a thin book | Delay parameter `delay_ticks` defers liquidation |
| Post-crisis normalisation    | Returns to normal prime-broker behaviour   | Liquidation flag resets                          |

Environmental Dependencies: Requires a per-tick `price` feed and a first-mover liquidation indicator. None beyond §3.6.1 signals.
## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape | Required? | Notes                                                                                       |
|---------------------|--------------|--------------|-----------|---------------------------------------------------------------------------------------------|
| `price`             | environment  | `float`      | yes       | Maps to §3.6.1 `price`.                                                                     |
| `fundamental`       | environment  | `float`      | yes       | Maps to §3.6.1 `fundamental`.                                                               |
| `identity`, `round` | round header | `str`, `int` | yes       | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum        | Unit     | Required?   | Meaning                                                         |
|---------------|--------|---------------------------|----------|-------------|-----------------------------------------------------------------|
| `action`      | enum   | {"buy", "sell", "hold"}   | —        | yes         | Discrete action selected this call.                             |
| `quantity`    | float  | `[0, base_position_size]` | shares   | conditional | Order magnitude; 0 when `action = hold`.                        |
| `price_level` | float  | `= price` (market order)  | currency | conditional | Execution reference; equals observed `price` for market orders. |
| `reasoning`   | string | 1–3 sentences             | —        | yes         | Audit trail explaining WHY.                                     |

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

Identical to base — see [Decision Information Set](./prime-broker-first-mover.md#decision-information-set). Same four signals (`price`, `fundamental`, `deviation`, `position`) with the same memory windows and rationale references.

#### Core Behavioral Mechanism

**Delta vs. first-mover:**

1. Read/Write: identical to base.
2. Threshold: compare `deviation` with `liquidation_threshold=-0.15` [Ref 3] (base uses `-0.10`).
3. Sizing: identical to base — `q = min(position, position * liquidation_sell_ratio)`.
4. Emission: emit sell at `current price × price_penalty`; otherwise hold (base emits at raw current price; no penalty).
5. Post-fill: identical to base.

#### Action Space

Identical to base — see [Action Space](./prime-broker-first-mover.md#action-space). All nine rows (Order types, Price level rule, Order quantity rule, Order lifetime, Cancellation policy, Inventory constraint, Wealth / leverage cap, Stop-loss / kill rule) are unchanged. The Price level rule's phrase *"unless an intrinsic haircut/penalty parameter is declared"* is the extension point this archetype activates via `price_penalty`.

#### Mathematical Model

**Delta vs. first-mover:**

Decision logic — sell branch multiplies `b_t` by `pi_penalty`:
```
if delta_t < theta_liq:
    a_t = sell; q_t = min(position_t, position_t * phi_liq); b_t = price_t * pi_penalty
else:
    a_t = hold; q_t = 0; b_t = price_t
```
(Base uses `b_t = price_t` in the sell branch.)

State variables: identical to base.

Determinism contract: identical to base.

Parameter symbol table (delta values in **bold**):

| Symbol       | Meaning                                   | Default Value                | Source       |
|--------------|-------------------------------------------|------------------------------|--------------|
| `theta_liq`  | Liquidation deviation threshold           | **-0.15** (base: -0.10)      | Ref 3        |
| `phi_liq`    | Fraction of collateral sold per trigger   | **0.35** (base: 0.40)        | Ref 3        |
| `pi_penalty` | Execution haircut for delayed liquidation | **0.97** (new — not in base) | Ref 3; Ref 9 |

#### Behavioral Properties

Identical to base — see [Behavioral Properties](./prime-broker-first-mover.md#behavioral-properties). Same time horizon, risk tolerance, information asymmetry, and psychological profile.

## Parameters

**Delta vs. first-mover:** Threshold shifts deeper (-0.15 vs. -0.10), sell fraction is smaller (0.35 vs. 0.40), initial position is smaller (3500 vs. 4000), and one new parameter (`price_penalty`) is added.

| Parameter                | Type  | Default    | Valid Range    | Sensitivity | Description                                                   | Impact                                       | Source                                                      |
|--------------------------|-------|------------|----------------|-------------|---------------------------------------------------------------|----------------------------------------------|-------------------------------------------------------------|
| `liquidation_threshold`  | float | **-0.15**  | [-0.30, -0.03] | high        | Deviation that triggers collateral liquidation.               | Higher magnitude -> later liquidation.       | Gorton & Metrick (2012); Archegos broker timing calibration |
| `liquidation_sell_ratio` | float | **0.35**   | [0.05, 1.00]   | high        | Fraction of collateral sold per activation.                   | Higher -> larger immediate selling pressure. | Gorton & Metrick (2012); post-event broker calibration      |
| `initial_position`       | float | **3500.0** | > 0            | high        | Starting collateral inventory.                                | Higher -> larger liquidation supply.         | Scenario normalization from Archegos exposure reports       |
| `price_penalty`          | float | **0.97**   | [0.80, 1.00]   | medium      | Execution haircut for delayed liquidation (new; not in base). | Higher -> smaller first-mover payoff gap.    | Archegos broker-loss comparison calibration                 |

## Population and Heterogeneity

Identical to base — see [Population and Heterogeneity](./prime-broker-first-mover.md#population-and-heterogeneity).

## Worked Numerical Examples

Structure identical to base ([Worked Numerical Examples](./prime-broker-first-mover.md#worked-numerical-examples)); numeric outcomes differ per the threshold and sell-fraction deltas.

### Case 1 - Primary non-hold branch
System state: `price=84`, `fundamental=100`, `deviation=-0.16`, plus default parameters.
Calculation: `q = position * 0.35`; sell branch fires because `-0.16 < -0.15`.
Decision: `sell`, positive quantity, `bid_price = price * price_penalty`.
State update: cash and position update post-fill if the order executes.

### Case 2 - Hold branch
Identical to base — see [Case 2](./prime-broker-first-mover.md#case-2---hold-branch). `deviation=-0.04` fails the trigger under both archetypes' thresholds.

### Case 3 - Stress branch (**diverges from base**)
System state: `price=88`, `fundamental=100`, `deviation=-0.12`, plus default parameters.
Calculation: at `deviation=-0.12`, branch does **not** fire for this threshold (`-0.12 > -0.15`).
Decision: `hold` for this delayed archetype. (Base fires `sell` at this state because `-0.12 < -0.10`.)
State update: no cash or position change.

### Edge Case - Constraint clamp or missing signal
Identical to base — see [Edge Case](./prime-broker-first-mover.md#edge-case---constraint-clamp-or-missing-signal).

## Validation and Calibration

**Calibration data sources**:
- `liquidation_threshold` <- Gorton & Metrick (2012) run threshold logic and Archegos broker timing.
- `liquidation_sell_ratio` <- liquidation-race payoff calibration from scenario §2 and §8.
- `price_penalty` <- Archegos broker-loss comparison between first-mover and delayed-liquidator execution prices.

**Expected individual behaviour**:
- Given deviation below -0.15 (the delayed threshold), agent MUST sell with positive quantity.
- Given deviation above -0.15, agent MUST hold.
- Given position is zero, agent MUST hold with zero quantity.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits the opposite sign from its trigger branch THEN the mechanism is inverted.
- IF quantity exceeds declared position discipline THEN the implementation violates Action Space.
- IF `price_penalty` has no effect on execution price THEN the delayed-liquidator penalty is absent.

#### Ablation Hooks

| Ablation name      | Setting                                     | Hypothesis tested                                                   | Expected direction | Metric                    |
|--------------------|---------------------------------------------|---------------------------------------------------------------------|--------------------|---------------------------|
| `threshold_strict` | Increase trigger threshold magnitude by 50% | Fewer activations weaken this agent's individual trading intensity. | decrease           | number of non-hold orders |
| `size_half`        | Halve the size parameter                    | Same timing with lower impact.                                      | decrease           | average order quantity    |

## Academic References

| # | Citation                                                                                                                                                                    | Notes                                         |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 3 | Gorton, G., & Metrick, A. (2012). Securitized banking and the run on repo. *Journal of Financial Economics*, 104(3), 425-451. https://doi.org/10.1016/j.jfineco.2011.03.016 | Creditor run and first-mover liquidation race |
| 9 | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179-207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x           | Price impact and execution-price relevance    |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | Codex                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Reviewed by | Codex three-pass self-check                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Created     | 2026-06-30                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Version     | 1.1.3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Status      | conformant                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Icon        | ![](../agent_images/icons/finance-prime-broker-delayed-liquidator.png)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
