# Delayed prime-broker liquidator

> **Base archetype:** This file inherits its structure and shared prose from [prime-broker-first-mover.md](./prime-broker-first-mover.md). Sections marked *"identical to base"* are unchanged and link back to the base for the shared content; sections with a **Delta vs. first-mover** callout list what is different. Each archetype keeps its own file and its own generated icon.

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | delayed prime-broker liquidator |
| Theory Family         | Leverage / Risk-On-Risk-Off |
| Market Role           | **Destabilising** - later liquidation amplifies the cascade and receives worse execution |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

**Delta vs. first-mover:** Market Role wording emphasises *later* liquidation and *worse execution* (vs. the first-mover's *early liquidation / fire-sale acceleration*). All other Summary rows are identical.

## Definition and Goals

Identical to base — see [Definition and Goals](./prime-broker-first-mover.md#definition-and-goals). The same three paragraphs apply: intrinsic prime-broker liquidator, single decision object per call, transmits borrower distress into market-wide selling via creditor-run incentives.

## Theoretical Foundation

Identical to base — see [Theoretical Foundation](./prime-broker-first-mover.md#theoretical-foundation) (Gorton & Metrick 2012, creditor run and first-mover liquidation). Both archetypes are two positions in the *same* run game — the base file's Theoretical Foundation applies verbatim.

## Design Purpose and Activation Triggers

Identical to base — see [Design Purpose and Activation Triggers](./prime-broker-first-mover.md#design-purpose-and-activation-triggers). Purpose, Call Frequency, Prerequisite Signals, Missing-Signal Policy, Activation Triggers, Deactivation Conditions, Market Contribution by Regime, and Environmental Dependencies are all unchanged; only the numeric value of `liquidation_threshold` differs (see Parameters below).

## Behavioral Framework

#### I/O Contract

Identical to base — see [I/O Contract](./prime-broker-first-mover.md#io-contract).

**Delta vs. first-mover:**

- `bid_price` valid-range Meaning: `sell uses price * price_penalty` (base uses `price` directly).
- Content Constraint: "if the haircut product `price * price_penalty` is non-positive, floor to `price`" (base floors non-positive raw `price` computations).
- Serialization example uses the delayed calibration: `{"action": "sell", "bid_price": 82.45, "quantity": 1225.0, "reasoning": "Deviation crossed liquidation_threshold=-0.15 after first-mover selling; liquidating 35% of collateral at delayed haircut."}`
- Implementer Contract Reminder item 3 reads *"…with a worked example using the later `liquidation_threshold=-0.15` calibration."*

Inputs table, Outputs table columns/enum, and Reminder items 1/2/4/5/6 are unchanged.

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

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_liq` | Liquidation deviation threshold | **-0.15** (base: -0.10) | Ref 3 |
| `phi_liq` | Fraction of collateral sold per trigger | **0.35** (base: 0.40) | Ref 3 |
| `pi_penalty` | Execution haircut for delayed liquidation | **0.97** (new — not in base) | Ref 3; Ref 9 |

#### Behavioral Properties

Identical to base — see [Behavioral Properties](./prime-broker-first-mover.md#behavioral-properties). Same time horizon, risk tolerance, information asymmetry, and psychological profile.

## Parameters

**Delta vs. first-mover:** Threshold shifts deeper (-0.15 vs. -0.10), sell fraction is smaller (0.35 vs. 0.40), initial position is smaller (3500 vs. 4000), and one new parameter (`price_penalty`) is added.

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `liquidation_threshold` | float | **-0.15** | [-0.30, -0.03] | high | Deviation that triggers collateral liquidation. | Higher magnitude -> later liquidation. | Gorton & Metrick (2012); Archegos broker timing calibration |
| `liquidation_sell_ratio` | float | **0.35** | [0.05, 1.00] | high | Fraction of collateral sold per activation. | Higher -> larger immediate selling pressure. | Gorton & Metrick (2012); post-event broker calibration |
| `initial_position` | float | **3500.0** | > 0 | high | Starting collateral inventory. | Higher -> larger liquidation supply. | Scenario normalization from Archegos exposure reports |
| `price_penalty` | float | **0.97** | [0.80, 1.00] | medium | Execution haircut for delayed liquidation (new; not in base). | Higher -> smaller first-mover payoff gap. | Archegos broker-loss comparison calibration |

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

Identical to base — see [Validation and Calibration](./prime-broker-first-mover.md#validation-and-calibration). Calibration sources, expected individual behaviour bullets, and sanity bounds all apply verbatim.

#### Ablation Hooks

Identical to base — see [Ablation Hooks](./prime-broker-first-mover.md#ablation-hooks). Both `threshold_strict` and `size_half` ablations apply to this archetype's parameter set as well.

## Academic References

Identical to base — see [Academic References](./prime-broker-first-mover.md#academic-references) (Ref 3 Gorton & Metrick 2012; Ref 9 Hasbrouck 1991).

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Reviewed by | Codex three-pass self-check |
| Created | 2026-06-30 |
| Version | 1.1.0 |
| Change log | 1.0.0 - normalized existing ArchegosCollapse agent into standalone AGENT_POOL form. / 1.0.1 - Polish audit 2026-07-01: inserted §3.6.0 I/O Contract as first sub-block of Behavioral Framework, verified against agent-design-skill.md v2.3.1 §3.6.0. / 1.1.0 - Section-link + delta-callout dedup against prime-broker-first-mover.md; shared prose replaced with inline links, only deltas retained in full. |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-prime-broker-delayed-liquidator.png) |
