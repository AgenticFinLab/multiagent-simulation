# Liquidation-signal information trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | liquidation-signal information trader |
| Theory Family         | Microstructure |
| Behavioral Tendency   | **Converging — trades on fundamental information about the crisis; converges on the post-crisis fair value** |
| Market Role           | **Context-dependent** - front-runs distress and later covers, amplifying early decline but aiding price discovery |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | partial |
| Determinism           | stochastic-given-seed |
## Definition and Goals

This agent models a proprietary trading desk or informed hedge fund reading order-flow stress in a finance liquidation setting, using the market-trading domain palette from `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1`. It is intentionally intrinsic: it defines the participant's signals, decision discipline, state, and self-imposed trading constraints, not matching-engine rules or message topology. The real-world counterpart and role are evidenced by the references in the theoretical foundation.

The decision goal is to emit one order per decision call: `buy`, `sell`, or `hold`, with a numeric `bid_price` and `quantity`. The agent optimizes the role-specific criterion shown in the mathematical model: trade ahead of expected liquidation when a distress signal is detected, then cover after recovery signal appears.

Inside a market simulation this agent adds early informed selling and later covering around the forced-liquidation episode. It contributes to stylized facts from the finance catalogue: liquidity black holes, capitulation tail, volume spikes around news, co-movement in factor returns, and price-impact concavity where applicable. Non-goals: it must not quote two-sided market-making liquidity unless explicitly listed in Action Space, and it must not use hidden peer-network topology or environment-imposed rules as part of its intrinsic design.

## Theoretical Foundation

**Informed trading**:
- Theory / Study: Continuous auctions and insider trading.
- Citation: Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210
- Core Insight: Informed traders infer or possess signals about future order flow and trade before prices fully reveal that information. Their trades move prices toward the information but can worsen short-run impact.
- Mathematical Formulation: `sell_signal = 1[deviation_t < theta_detect] * Bernoulli(p_detect)`.
- Empirical Evidence: Kyle (1985) formalizes informed order splitting and price impact; market microstructure evidence links informed flow to price discovery.
- Relevance to This Agent: The detection threshold and probability encode partial information about forced liquidation.
- Calibration Source: Kyle (1985); scenario §6.
- Falsification Conditions: If the agent never sells after a detected distress signal, informed trading is absent.
- Alternative Theories: noise trading; passive liquidity provision.

**Predatory trading around distressed liquidation**:
- Theory / Study: Predatory trading.
- Citation: Brunnermeier, M. K., & Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825-1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x
- Core Insight: Traders who anticipate another trader's need to liquidate can sell ahead of that liquidation and later repurchase after prices are depressed. This behaviour amplifies temporary price pressure.
- Mathematical Formulation: `q_sell = min(front_run_size, position)` before liquidation; `q_cover = min(cover_size, short_position, cash/price)` after recovery signal.
- Empirical Evidence: Brunnermeier & Pedersen (2005) show predatory trading can increase liquidation costs.
- Relevance to This Agent: The sell-and-cover branches are the direct operationalization.
- Calibration Source: Brunnermeier & Pedersen (2005), normalized to scenario order size.
- Falsification Conditions: If short covering does not reduce `short_position`, the predatory cycle is incomplete.
- Alternative Theories: market making; fundamental value investing.

## Design Purpose and Activation Triggers

Purpose: Exploit partial order-flow information about imminent liquidation pressure.

Call Frequency: every-tick after receiving a fresh market broadcast.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available
- `prev_price` available for change detection
- seeded random source available for detection success

Missing-Signal Policy: hold and emit zero quantity if any prerequisite signal is missing, NaN, or stale; do not infer unavailable values.

Activation Triggers:
- `deviation < detection_threshold` and detection draw succeeds: submit sell order sized by `front_run_size`.
- `deviation > cover_threshold` and `short_position > 0`: submit buy order sized by `cover_size`.
- `<Default>`: hold.

Deactivation Conditions:
- No long position and no short inventory: hold.
- Detection draw fails: hold.


Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|---|---|---|
| Fundamental signal indicates post-crisis value | Trades toward the new fundamental | Signal-driven order |
| No information update | Holds | No-trade default |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm market | Hold | No distress signal. |
| Liquidity stress / drought | Destabilising | Sells ahead of expected forced liquidation. |
| Post-shock recovery | Stabilising | Covers short exposure through buy orders. |

Environmental Dependencies: none beyond the declared market broadcast signals and the agent's own cash, position, and state variables.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|---|---|---|---|---|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. |
| `fundamental` | environment | `float` | yes | Maps to §3.6.1 `fundamental`. |
| `deviation` | environment | `float` | yes | Maps to §3.6.1 `deviation`. |
| `prev_price` | environment | `float` | yes | Maps to §3.6.1 `prev_price`. |
| `short_position` | environment | `float` | yes | Maps to §3.6.1 `short_position`. |
| `rng_state` | agent state | `float` | yes | Persistent state; see §3.6.4. |
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

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference and portfolio valuation [Ref 9]. |
| `fundamental` | Continuous | 1 tick | Anchor for collateral-value deviation and discount calculations [Ref 1]. |
| `deviation` | Continuous | 1 tick | Primary trigger signal for distress, discount, or information advantage [Ref 1; Ref 3]. |
| `prev_price` | Continuous | 1 tick | Supports local order-flow stress inference [Ref 5]. |
| `short_position` | State | persistent | Determines whether cover branch can activate [Ref 7]. |
| `rng_state` | State | persistent | Makes partial detection stochastic but seed-reproducible. |

Does NOT use: social-network topology, undocumented peer thresholds, fee schedules, latency, or matching-engine implementation details.

#### Core Behavioral Mechanism

1. Read: `deviation`, `price`, `position`, `short_position`, and seeded random source.
2. If `deviation < detection_threshold`, draw detection success with probability `detection_ability` [Ref 5].
3. On successful detection, sell `min(front_run_size, position)` and increase `short_position` post-fill [Ref 7].
4. Else if `deviation > cover_threshold` and `short_position > 0`, buy `min(cover_size, short_position, cash / price)` to cover.
5. If neither branch fires, hold.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | `buy`, `sell`, `hold` as specified by the trigger function. |
| Price level rule | Use current `price` unless an intrinsic haircut/penalty parameter is declared; hold uses current `price`. |
| Order quantity rule | Sell `min(front_run_size, position)` on detection; buy `min(cover_size, short_position, cash / price)` on cover; otherwise zero. |
| Order lifetime | One decision round; replace on next fresh broadcast. |
| Cancellation policy | Cancel prior intent when the current trigger evaluates to hold or the opposite side. |
| Inventory constraint | Never sell more than internally available long position plus declared short inventory discipline. |
| Wealth / leverage cap | Never buy more than available cash divided by current price; leveraged liquidation agents only reduce exposure after trigger. |
| Stop-loss / kill rule | Stop selling when no long inventory remains; stop covering when short_position reaches zero. |

#### Mathematical Model

Decision output: `a_t in {buy, sell, hold}`, `q_t >= 0`, and `b_t > 0`.

Decision logic formalization:
```
if delta_t < theta_detect and Bernoulli(p_detect)=1:
    a_t = sell; q_t = min(front_run_size, position_t); b_t = price_t
elif delta_t > theta_cover and short_position_t > 0:
    a_t = buy; q_t = min(cover_size, short_position_t, cash_t / price_t); b_t = price_t
else:
    a_t = hold; q_t = 0; b_t = price_t
```

State variables:
| State | Initial value | Update phase | Evolution |
|-------|---------------|--------------|-----------|
| `cash` | scenario config | post-fill | cash decreases on buy and increases on sell. |
| `position` | scenario config | post-fill | position increases on buy and decreases on sell. |
| `short_position` | 0.0 | post-fill | increases after sell branch and decreases after cover branch. |

Determinism contract: stochastic-given-seed because detection uses a Bernoulli draw with configured probability.

Parameter symbol table:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `p_detect` | Probability of detecting liquidation signal | 0.50 | Ref 5; Ref 7 |
| `theta_detect` | Distress-detection deviation threshold | -0.05 | Ref 5; Ref 7 |
| `front_run_size` | Maximum sell size on detected signal | 1000 | Ref 7 |
| `theta_cover` | Recovery threshold for cover branch | -0.03 | Ref 7 |
| `cover_size` | Maximum buy-to-cover size | 500 | Ref 7 |

#### Behavioral Properties

- Time horizon: short - information advantage decays quickly as order flow becomes public.
- Risk tolerance: high - takes directional exposure before liquidation is fully visible.
- Information asymmetry: partial - has partial noisy order-flow information, not full broker books.
- Psychological profile: predatory trading and informed order-flow inference [Ref 5; Ref 7].

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `detection_ability` | float | 0.50 | [0.00, 1.00] | high | Probability of detecting the liquidation signal. | Higher -> more early sell orders. | Kyle (1985); Brunnermeier & Pedersen (2005) |
| `detection_threshold` | float | -0.05 | [-0.20, 0.00] | high | Deviation at which distress detection is attempted. | Higher magnitude -> later signal attempts. | Kyle (1985); predatory-trading calibration |
| `front_run_size` | float | 1000 | >= 0 | high | Maximum sell quantity on successful detection. | Higher -> stronger early downward pressure. | Brunnermeier & Pedersen (2005), normalized |
| `cover_threshold` | float | -0.03 | [-0.20, 0.10] | medium | Deviation above which covering is allowed. | Higher -> later covering. | Brunnermeier & Pedersen (2005) |
| `cover_size` | float | 500 | >= 0 | medium | Maximum buy-to-cover quantity. | Higher -> faster short-position reduction. | Brunnermeier & Pedersen (2005), normalized |

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
  If the Bernoulli draw succeeds, `q = min(1000, 1000) = 1000`; sell branch fires.
Decision: `sell`, `quantity=1000`, `bid_price=84` on detection success; otherwise hold.
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
  `deviation=-0.12 < -0.05`; detection branch is eligible; expected activation probability is 0.50.
Decision: stochastic sell-or-hold according to detection draw.
State update: cash and position update only if the branch emits a non-hold order.

### Edge Case - Constraint clamp or missing signal
System state: `price` missing or position/cash insufficient.
Calculation:
  Missing signal => hold; insufficient resource => clamp quantity to the available self-imposed resource cap.
Decision: hold or clamped order according to Action Space.
State update: no state becomes negative.

## Validation and Calibration

**Calibration data sources**:
- `detection_ability` <- Kyle (1985) information advantage and Brunnermeier & Pedersen (2005) predatory-trading mechanism.
- `front_run_size`, `cover_size` <- scenario-normalized order-flow scale from §6.

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

## Behavioral Verification and Calibration

- Given deviation above detection_threshold (no distress signal), agent must hold regardless of Bernoulli draw outcome.
- Given deviation below detection_threshold with successful detection draw and positive position, agent must sell up to front_run_size.
- Given deviation above cover_threshold with positive short_position, agent must buy to cover up to cover_size.
- Given zero position and zero short_position with no active trigger, agent must hold.
- Given missing price or deviation signal, agent must hold with zero quantity.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `perfect_detection` | `detection_ability = 1.0` | Certain detection maximises early selling pressure before liquidation | increase | front-run sell volume |
| `no_cover` | `cover_threshold = 999` | Disabling cover removes post-crash stabilising buy flow | increase | recovery time after liquidation event |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 5 | Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210 | Informed order-flow trading |
| 7 | Brunnermeier, M. K., & Pedersen, L. H. (2005). Predatory trading. *Journal of Finance*, 60(4), 1825-1863. https://doi.org/10.1111/j.1540-6261.2005.00781.x | Predatory trading around forced liquidation |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Reviewed by | Codex three-pass self-check |
| Created | 2026-06-30 |
| Version | 1.0.3 |
| Status | conformant |
| Icon        | ![](../agent_images/icons/finance-information-trader.png) |
