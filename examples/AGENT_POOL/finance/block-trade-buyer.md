# Opportunistic block-trade buyer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | opportunistic block-trade buyer |
| Theory Family         | Liquidity / Funding |
| Market Role           | **Stabilising** - absorbs distressed supply after a sufficient discount |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a asset manager, family office, or proprietary desk buying large blocks in distressed markets in a finance liquidation setting, using the market-trading domain palette from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. It is intentionally intrinsic: it defines the participant's signals, decision discipline, state, and self-imposed trading constraints, not matching-engine rules or message topology. The real-world counterpart and role are evidenced by the references in the theoretical foundation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `bid_price` and `quantity`. The agent optimizes the role-specific criterion shown in the mathematical model: deploy a bounded fraction of cash when price discount compensates inventory risk.

Inside a market simulation this agent provides stabilising demand and a partial price floor during forced liquidation. It contributes to stylized facts from the finance catalogue: liquidity black holes, capitulation tail, volume spikes around news, co-movement in factor returns, and price-impact concavity where applicable. Non-goals: it must not quote two-sided market-making liquidity unless explicitly listed in Action Space, and it must not use hidden peer-network topology or environment-imposed rules as part of its intrinsic design.

## Theoretical Foundation

**Block liquidity provision**:
- Theory / Study: Liquidity and market structure.
- Citation: Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617-633. https://doi.org/10.1111/j.1540-6261.1988.tb04591.x
- Core Insight: Large urgent sellers require immediacy from buyers who must be compensated for inventory risk. Distressed block buyers activate only when discounts exceed expected holding costs and risk premia.
- Mathematical Formulation: `q_buy = phi_buy * cash_t / price_t` if `deviation_t < theta_discount`.
- Empirical Evidence: Grossman & Miller (1988) model block liquidity compensation; Archegos block sales traded at sharp discounts during stress.
- Relevance to This Agent: The agent turns fire-sale discounts into bounded stabilising demand.
- Calibration Source: Grossman & Miller (1988), distressed-discount range 5-15% in scenario §2.
- Falsification Conditions: If this agent buys without a discount or sells into the discount, it is not a block buyer.
- Alternative Theories: market-maker spread provision; passive value investing.

**Limits to arbitrage**:
- Theory / Study: Capital-constrained arbitrage.
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Corrective capital is limited and must be rationed under stress. The buyer therefore deploys a fraction of cash rather than eliminating all mispricing immediately.
- Mathematical Formulation: `q_t <= cash_t / price_t` and `q_t = phi_buy * cash_t / price_t`.
- Empirical Evidence: Limits-to-arbitrage literature documents slow correction when risk-bearing capital is constrained.
- Relevance to This Agent: `buy_ratio` prevents unrealistic infinite stabilisation.
- Calibration Source: Shleifer & Vishny (1997); scenario §6.
- Falsification Conditions: If the agent removes all mispricing in one step despite low `buy_ratio`, the cap is not represented.
- Alternative Theories: fully elastic arbitrage.

## Design Purpose and Activation Triggers

Purpose: Absorb supply when distressed discount exceeds the required compensation threshold.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `cash` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation < discount_threshold`: submit buy order sized by `cash * buy_ratio / price`.
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted: hold.
- Deviation above discount threshold: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Hold | Waits for adequate discount. |
| Liquidity stress / drought | Stabilising | Absorbs shares that forced sellers unload. |
| Post-shock recovery | Stabilising | Continued bids support convergence toward fundamental value. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash, position, and state variables.

## Behavioral Framework

#### I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Row of Decision Information Set                                                                          |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Row of Decision Information Set                                                                          |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Row of Decision Information Set                                                                          |
| `cash`                  | agent state (Mathematical Model state variables)    | `float`      | yes                     | Capital available for distressed block absorption                                                        |
| `position`              | agent state (Mathematical Model state variables)    | `float`      | yes                     | Cumulative inventory accumulated so far                                                                  |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                             |
| `retrieved_knowledge`   | retrieval store (retrieval-augmented variants only) | `list[str]`  | retrieval variants only | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty    |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action (matches Action Space Order types)            |
| `bid_price` | float  | > 0                        | same units as `price`      | yes       | Order price (Action Space Price level rule; buy uses current `price`) |
| `quantity`  | float  | ≥ 0, ≤ cash / price        | shares / units of position | yes       | Order magnitude (Action Space Order quantity rule)            |
| `reasoning` | string | 1–3 sentences              | —                          | yes       | Audit trail explaining WHY; also consumed by `analysis.py`    |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped so that `quantity * bid_price ≤ cash`.
- `bid_price` MUST be strictly positive; if computed non-positive, floor to `price`.
- Sign convention: `action = "buy"` corresponds to positive net demand; `quantity` is always non-negative.
- Determinism marker: deterministic — same inputs and state MUST produce byte-identical outputs across variants.

**Serialization Format.**

```
<analysis>...free-form reasoning, 1–3 sentences...</analysis>
<decision>{"action": "buy", "bid_price": 88.0, "quantity": 3409.09, "reasoning": "Deviation -0.12 exceeds discount_threshold=-0.10; deploying 30% of cash to absorb forced supply."}</decision>
```

Every implementation variant declared for this agent (rule-driven, model-driven, hybrid, retrieval-augmented) MUST honour this tag pattern. Rule-driven variants MAY populate `<analysis>` from a deterministic template. Model-driven variants MUST include this tag + JSON schema literally in the system or user prompt. Retrieval-augmented variants MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity * bid_price` MUST NOT exceed `cash`.
3. **Prompt drafting** — every model-driven variant's prompt MUST spell out the tag pattern and JSON schema verbatim with a worked example emitting a `buy` at the current `price`.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts every required field is present and inside its valid range.
5. **Variant parity** — every declared variant MUST produce the same field set; do not add variant-only fields without extending this contract first.
6. **Contract-versus-prose** — on any conflict with Core Behavioral Mechanism, Action Space, or Mathematical Model, this I/O Contract wins.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and portfolio valuation [Ref 9]. |
| `fundamental` | Continuous | 1 tick | Anchor for collateral-value deviation and discount calculations [Ref 1]. |
| `deviation` | Continuous | 1 tick | Primary trigger signal for distress, discount, or information advantage [Ref 1; Ref 3]. |
| `cash` | State | persistent | Capital available for distressed block absorption [Ref 4]. |

Does NOT use: social-network topology, undocumented peer thresholds, fee schedules, latency, or matching-engine implementation details.

#### Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `cash`; Write: no state before decision.
2. Compare `deviation` with `discount_threshold` [Ref 4; Ref 8].
3. If price is sufficiently below fundamental, compute deployment `cash * buy_ratio`.
4. Convert deployment to quantity using current `price`; emit buy if affordable.
5. Post-fill, reduce cash and increase position.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` as specified by the trigger function. |
| Price level rule | Use current `price` unless an intrinsic haircut/penalty parameter is declared; hold uses current `price`. |
| Order quantity rule | `q = (cash * buy_ratio) / price` for buy, clamped by available cash; otherwise zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more than internally available long position plus declared short inventory discipline. |
| Wealth / leverage cap | Never buy more than available cash divided by current price; leveraged liquidation agents only reduce exposure after trigger. |
| Stop-loss / kill rule | Stop buying when cash is exhausted or discount no longer exceeds threshold. |

#### Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`, and `b_t > 0`.

Decision logic formalization:
```
if delta_t < theta_discount:
    a_t = buy; q_t = (cash_t * phi_buy) / price_t; b_t = price_t
else:
    a_t = hold; q_t = 0; b_t = price_t
```

State variables:
| State | Initial value | Update phase | Evolution |
|-------|---------------|--------------|-----------|
| `cash` | scenario config | post-fill | cash decreases on buy and increases on sell. |
| `position` | scenario config | post-fill | position increases on buy and decreases on sell. |
| `deployed_capital` | 0.0 | post-fill | cumulative cash spent on block purchases. |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_discount` | Required discount threshold | -0.10 | Ref 4; Ref 8 |
| `phi_buy` | Cash deployment fraction | 0.30 | Ref 4; Ref 8 |

#### Behavioral Properties

- Time horizon: medium - block buyers expect recovery over multiple rounds rather than immediate resale.
- Risk tolerance: medium - takes inventory risk but only after a margin-of-safety discount.
- Information asymmetry: partial - observes public price discount but not every seller exposure.
- Psychological profile: patient value/liquidity provision under limits to arbitrage [Ref 8].

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `discount_threshold` | float | -0.10 | [-0.30, -0.01] | high | Discount from fundamental required before buying. | Higher magnitude -> fewer stabilising buys. | Grossman & Miller (1988); Shleifer & Vishny (1997) |
| `buy_ratio` | float | 0.30 | [0.01, 1.00] | high | Fraction of cash deployed per trigger. | Higher -> larger stabilising demand. | Grossman & Miller (1988) distressed liquidity calibration |
| `initial_cash` | float | 1000000.0 | >= 0 | high | Starting capital available for block purchases. | Higher -> stronger price floor. | Scenario normalization from block-trade capacity |

## Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 1 instance in ArchegosCollapse configs. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level +/-10% sweep around listed defaults. |
| Heterogeneity per parameter | Threshold and size parameters may vary within the Valid Range; cash/position scale the agent's market impact. |
| Cross-agent correlation | Same archetype instances share theory and trigger sign; cash and position levels may differ. |
| Identity persistence | Persistent identity and state across rounds; no type switching. |

## Worked Numerical Examples

### Case 1 - Primary non-hold branch
System state: `price=84`, `fundamental=100`, `deviation=-0.16`, plus default parameters.
Calculation:
  `q = 1000000 * 0.30 / 84 = 3571.43`; buy branch fires.
Decision: `buy`, `quantity=3571.43`, `bid_price=84`.
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
  `deviation=-0.12 < -0.10`; buy branch fires with smaller quantity because price is 88.
Decision: `buy`, `quantity=3409.09`, `bid_price=88`.
State update: cash and position update only if the branch emits a non-hold order.

### Edge Case - Constraint clamp or missing signal
System state: `price` missing or position/cash insufficient.
Calculation:
  Missing signal => hold; insufficient resource => clamp quantity to the available self-imposed resource cap.
Decision: hold or clamped order according to Action Space.
State update: no state becomes negative.

## Validation and Calibration

**Calibration data sources**:
- `discount_threshold` <- Grossman & Miller (1988), block liquidity premium; stressed-market calibration in scenario §2.
- `buy_ratio` <- Grossman & Miller (1988), inventory-risk capital deployment logic.

**Expected individual behaviour**:
- Given the primary trigger condition, the agent MUST emit the trigger-specified action with positive quantity.
- Given a non-trigger condition, the agent MUST hold.
- Given insufficient cash, position, or signal availability, the agent MUST hold or clamp quantity without violating self-imposed constraints.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent emits the opposite sign from its trigger branch THEN the mechanism is inverted.
- IF quantity exceeds declared cash/position discipline THEN the implementation violates Action Space.
- IF any listed parameter has no effect on the mathematical model THEN the design has an orphan parameter.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `threshold_strict` | Increase trigger threshold magnitude by 50% | Fewer activations weaken this agent's individual trading intensity. | decrease | number of non-hold orders |
| `size_half` | Halve the size parameter | Same timing with lower impact. | decrease | average order quantity |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 4 | Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617-633. https://doi.org/10.1111/j.1540-6261.1988.tb04591.x | Block liquidity provision and inventory-risk compensation |
| 8 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x | Limits to arbitrage and capital constraints |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Reviewed by | Codex three-pass self-check |
| Created | 2026-06-30 |
| Version | 1.0.0 |
| Change log | 1.0.0 - normalized existing ArchegosCollapse agent into standalone AGENT_POOL form. / 1.0.1 - Polish audit 2026-07-01: inserted §3.6.0 I/O Contract as first sub-block of Behavioral Framework, verified against agent-design-skill.md v2.3.1 §3.6.0. |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-block-trade-buyer.png) |
