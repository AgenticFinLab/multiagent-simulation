# TRS-leveraged concentrated fund

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | TRS-leveraged concentrated fund |
| Theory Family         | Leverage / Risk-On-Risk-Off |
| Market Role           | **Destabilising** - forced deleveraging creates the first large negative demand shock |
| Time Horizon          | medium |
| Risk Tolerance        | high |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a family office or hedge fund using total return swaps for concentrated equity exposure in a finance liquidation setting, using the market-trading domain palette from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. It is intentionally intrinsic: it defines the participant's signals, decision discipline, state, and self-imposed trading constraints, not matching-engine rules or message topology. The real-world counterpart and role are evidenced by the references in the theoretical foundation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `bid_price` and `quantity`. The agent optimizes the role-specific criterion shown in the mathematical model: minimize margin-breach pressure by selling a fixed fraction of exposure once collateral deterioration crosses the trigger.

Inside a market simulation this agent initiates a liquidation cascade through forced selling after a margin breach. It contributes to stylized facts from the finance catalogue: liquidity black holes, capitulation tail, volume spikes around news, co-movement in factor returns, and price-impact concavity where applicable. Non-goals: it must not quote two-sided market-making liquidity unless explicitly listed in Action Space, and it must not use hidden peer-network topology or environment-imposed rules as part of its intrinsic design.

## Theoretical Foundation

**TRS hidden leverage and forced close-out**:
- Theory / Study: Hidden leverage through total return swaps.
- Citation: Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, Federal Reserve Bank of Kansas City, 2021-Q3, 1-12. https://doi.org/10.18651/ER/v106n3Becketti
- Core Insight: TRS exposure can accumulate outside public equity filings, leaving counterparties with incomplete aggregate exposure information. When collateral value falls, a margin breach converts discretionary holding into forced close-out.
- Mathematical Formulation: `equity_ratio_t = equity_t / (abs(position_t) * price_t)`; forced sell when `deviation_t < theta_margin`.
- Empirical Evidence: FSB (2022) reports roughly $35-40B Archegos notional exposure and 5-8x leverage.
- Relevance to This Agent: The agent operationalises the forced close-out channel with `margin_threshold` and `trs_sell_ratio`.
- Calibration Source: Becketti (2021) and FSB (2022), margin range about 10-25% and leverage 5-8x.
- Falsification Conditions: If this agent does not sell when `deviation < margin_threshold`, the mechanism is absent.
- Alternative Theories: voluntary portfolio rebalancing; rational deleveraging.

**Overconfidence and concentration risk**:
- Theory / Study: Overconfidence and excessive trading.
- Citation: Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261-292. https://doi.org/10.1162/003355301556400
- Core Insight: Overconfident investors overestimate private information quality and accept concentrated exposures. This explains the pre-trigger accumulation phase without making it an environment rule.
- Mathematical Formulation: `Q_actual = Q_prudent * (1 + overconfidence_multiplier)`.
- Empirical Evidence: Barber & Odean (2001) report lower net returns and higher trading among overconfident investor groups.
- Relevance to This Agent: Supports high `initial_position` and delayed voluntary de-risking.
- Calibration Source: Barber & Odean (2001), with position scale normalized to scenario units.
- Falsification Conditions: If reducing initial exposure has no impact on forced-sale quantity, concentration is not represented.
- Alternative Theories: rational concentrated alpha strategy.

## Design Purpose and Activation Triggers

Purpose: Generate forced selling after a TRS-style margin breach.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `position` available as internal state

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation < margin_threshold`: submit sell order sized by `position * trs_sell_ratio`.
- `<Default>`: hold.

Deactivation Conditions:
- Position exhausted: hold.
- Deviation recovers above threshold: hold reduced position.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Hold / latent destabilising | Large exposure is present but inactive. |
| Liquidity stress / drought | Destabilising | Forced sale adds concentrated supply. |
| Crash / cascade | Destabilising | Remaining exposure can continue to liquidate after repeated trigger rounds. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash, position, and state variables.

## Behavioral Framework

#### I/O Contract

**Inputs (per decision call).**

| Input                   | Source                                              | Type / Shape | Required?               | Notes                                                                                                    |
|-------------------------|-----------------------------------------------------|--------------|-------------------------|----------------------------------------------------------------------------------------------------------|
| `price`                 | environment broadcast                               | `float`      | yes                     | Row of Decision Information Set                                                                          |
| `fundamental`           | environment broadcast                               | `float`      | yes                     | Row of Decision Information Set                                                                          |
| `deviation`             | environment broadcast                               | `float`      | yes                     | Row of Decision Information Set                                                                          |
| `position`              | agent state (Mathematical Model state variables)    | `float`      | yes                     | Persistent long exposure remaining                                                                       |
| `cash`                  | agent state (Mathematical Model state variables)    | `float`      | yes                     | Populated by init from Parameters                                                                        |
| `round`                 | round header                                        | `int`        | yes                     | Round number                                                                                             |
| `retrieved_knowledge`   | retrieval store (retrieval-augmented variants only) | `list[str]`  | retrieval variants only | Falls back to sentinel `"(No relevant knowledge retrieved this round.)"` when retrieval returns empty    |

**Outputs (per decision call).** The agent emits exactly one decision object.

| Field       | Type   | Valid Range / Enum         | Unit                       | Required? | Meaning                                                       |
|-------------|--------|----------------------------|----------------------------|-----------|---------------------------------------------------------------|
| `action`    | enum   | `{"buy","sell","hold"}`    | —                          | yes       | Discrete action (matches Action Space Order types)            |
| `bid_price` | float  | > 0                        | same units as `price`      | yes       | Order price (Action Space Price level rule)                   |
| `quantity`  | float  | ≥ 0, ≤ available position  | shares / units of position | yes       | Order magnitude (Action Space Order quantity rule)            |
| `reasoning` | string | 1–3 sentences              | —                          | yes       | Audit trail explaining WHY; also consumed by `analysis.py`    |

**Content Constraints.**

- Every `Required? = yes` field MUST be present on every call.
- Extra fields not in the Outputs table MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, position]` before emission.
- `bid_price` MUST be strictly positive; if computed non-positive, floor to `price`.
- Sign convention: `action = "sell"` corresponds to negative net demand; `action = "buy"` to positive; `quantity` is always non-negative.
- Determinism marker: deterministic — same inputs and state MUST produce byte-identical outputs across variants.

**Serialization Format.**

```
<analysis>...free-form reasoning, 1–3 sentences...</analysis>
<decision>{"action": "sell", "bid_price": 84.0, "quantity": 2500.0, "reasoning": "Deviation crossed margin_threshold, forced close-out of 50% of position."}</decision>
```

Every implementation variant declared for this agent (rule-driven, model-driven, hybrid, retrieval-augmented) MUST honour this tag pattern. Rule-driven variants MAY populate `<analysis>` from a deterministic template. Model-driven variants MUST include this tag + JSON schema literally in the system or user prompt. Retrieval-augmented variants MUST inject `"(No relevant knowledge retrieved this round.)"` verbatim into `retrieved_knowledge` when retrieval returns empty.

**Implementer Contract Reminder.**

1. **Signal wiring** — every Input row MUST resolve to a real read of the environment broadcast, the agent's persisted state, or the round header.
2. **Decision emission** — every `Required? = yes` field MUST be populated; `quantity` MUST be clamped to `[0, position]`.
3. **Prompt drafting** — every model-driven variant's prompt MUST spell out the tag pattern and JSON schema verbatim with a worked example.
4. **Parser tests** — implementation MUST include a smoke test that (i) verifies both tags present, (ii) parses `<decision>` JSON, (iii) asserts every required field is present and inside its valid range.
5. **Variant parity** — every declared variant MUST produce the same field set; do not add variant-only fields without extending this contract first.
6. **Contract-versus-prose** — on any conflict with Core Behavioral Mechanism, Action Space, or Mathematical Model, this I/O Contract wins.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and portfolio valuation [Ref 9]. |
| `fundamental` | Continuous | 1 tick | Anchor for collateral-value deviation and discount calculations [Ref 1]. |
| `deviation` | Continuous | 1 tick | Primary trigger signal for distress, discount, or information advantage [Ref 1; Ref 3]. |
| `position` | State | persistent | Remaining synthetic long exposure available to liquidate [Ref 1]. |

Does NOT use: social-network topology, undocumented peer thresholds, fee schedules, latency, or matching-engine implementation details.

#### Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `deviation`, `position`; Write: no state before decision.
2. Compare `deviation` with `margin_threshold` [Ref 1].
3. If `deviation < margin_threshold`, compute `q = min(position, position * trs_sell_ratio)` [Ref 1; Ref 2].
4. If `q > 0`, emit `sell`; otherwise hold.
5. Post-fill, reduce `position` and increase `cash` by executed proceeds.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` as specified by the trigger function. |
| Price level rule | Use current `price` unless an intrinsic haircut/penalty parameter is declared; hold uses current `price`. |
| Order quantity rule | `q = min(position, position * trs_sell_ratio)` for sell; otherwise zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more than internally available long position plus declared short inventory discipline. |
| Wealth / leverage cap | Never buy more than available cash divided by current price; leveraged liquidation agents only reduce exposure after trigger. |
| Stop-loss / kill rule | Stop selling only when position reaches zero or deviation no longer breaches `margin_threshold`. |

#### Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`, and `b_t > 0`.

Decision logic formalization:
```
if delta_t < theta_margin:
    a_t = sell; q_t = min(position_t, position_t * phi_trs); b_t = price_t
else:
    a_t = hold; q_t = 0; b_t = price_t
```

State variables:
| State | Initial value | Update phase | Evolution |
|-------|---------------|--------------|-----------|
| `cash` | scenario config | post-fill | cash decreases on buy and increases on sell. |
| `position` | scenario config | post-fill | position increases on buy and decreases on sell. |
| `margin_triggered` | false | post-decide | true after the first margin-breach sell. |

Determinism contract: deterministic given identical market signals and state.

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_margin` | Margin-breach deviation threshold | -0.15 | Ref 1; Ref 2 |
| `phi_trs` | Fraction of position liquidated per trigger | 0.50 | Ref 1; Ref 2 |

#### Behavioral Properties

- Time horizon: medium - TRS exposure is built over weeks/months but forced close-out is immediate.
- Risk tolerance: high - 5-8x leverage implies high tolerance until forced liquidation.
- Information asymmetry: partial - knows own leverage but not all broker reactions.
- Psychological profile: overconfidence and concentration-risk underestimation [Ref 6].

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `margin_threshold` | float | -0.15 | [-0.25, -0.05] | high | Deviation at which margin pressure forces sale. | Higher magnitude -> fewer and later forced sales. | Becketti (2021); FSB (2022) |
| `trs_sell_ratio` | float | 0.50 | [0.10, 1.00] | high | Fraction of current position sold per trigger. | Higher -> larger negative order flow per activation. | FSB (2022); prime-broker post-mortem calibration |
| `initial_position` | float | 5000.0 | > 0 | high | Starting synthetic long exposure. | Higher -> larger cascade seed order. | FSB (2022) notional exposure scale, normalized |
| `initial_cash` | float | 500000.0 | >= 0 | medium | Initial liquidity buffer. | Higher -> more ability to absorb losses before state exhaustion. | Scenario normalization from §6 |

## Population and Heterogeneity

| Dimension | Specification |
|-----------|---------------|
| Default population size | 2 instances in ArchegosCollapse configs. |
| Parameter heterogeneity policy | Deterministic base value with optional scenario-level +/-10% sweep around listed defaults. |
| Heterogeneity per parameter | Threshold and size parameters may vary within the Valid Range; cash/position scale the agent's market impact. |
| Cross-agent correlation | Same archetype instances share theory and trigger sign; cash and position levels may differ. |
| Identity persistence | Persistent identity and state across rounds; no type switching. |

## Worked Numerical Examples

### Case 1 - Primary non-hold branch
System state: `price=84`, `fundamental=100`, `deviation=-0.16`, plus default parameters.
Calculation:
  `q = min(5000, 5000 * 0.50) = 2500`; sell branch fires.
Decision: `sell`, `quantity=2500`, `bid_price=84`.
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
  `deviation=-0.12` is above `margin_threshold=-0.15`; margin branch does not fire.
Decision: `hold`, `quantity=0`, `bid_price=88`.
State update: cash and position update only if the branch emits a non-hold order.

### Edge Case - Constraint clamp or missing signal
System state: `price` missing or position/cash insufficient.
Calculation:
  Missing signal => hold; insufficient resource => clamp quantity to the available self-imposed resource cap.
Decision: hold or clamped order according to Action Space.
State update: no state becomes negative.

## Validation and Calibration

**Calibration data sources**:
- `margin_threshold` <- Becketti (2021) and FSB (2022), 10-25% margin range.
- `trs_sell_ratio` <- FSB (2022) and Archegos post-event liquidation scale.

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
| 1 | Becketti, S. (2021). "Hidden leverage and the Archegos collapse." *Economic Review*, Federal Reserve Bank of Kansas City, 2021-Q3, 1-12. https://doi.org/10.18651/ER/v106n3Becketti | TRS leverage and margin breach mechanism |
| 2 | Financial Stability Board. (2022). *US dollar funding and emerging market economy vulnerabilities*. FSB non-bank financial intermediation analysis, Archegos discussion, pp. 47-51. https://www.fsb.org/ | Archegos notional exposure and leverage scale |
| 6 | Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261-292. https://doi.org/10.1162/003355301556400 | Overconfidence and concentrated risk taking |
| 9 | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179-207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x | Price and order-flow signal relevance |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Reviewed by | Codex three-pass self-check |
| Created | 2026-06-30 |
| Version | 1.0.0 |
| Change log | 1.0.0 - normalized existing ArchegosCollapse agent into standalone AGENT_POOL form. / 1.0.1 - Polish audit 2026-07-01: inserted §3.6.0 I/O Contract as first sub-block of Behavioral Framework, verified against agent-design-skill.md v2.3.1 §3.6.0. |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-concentrated-fund.png) |
