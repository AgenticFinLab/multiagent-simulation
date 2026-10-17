# DeFi lending protocol liquidation participant

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | DeFi lending protocol liquidation participant |
| Theory Family         | DeFi Contagion and Liquidation Mechanics |
| Behavioral Tendency   | **Diverging** — forced liquidations push collateral prices lower, triggering further liquidations in a cascade |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a participant in a DeFi lending protocol whose collateral is subject to forced liquidation when the collateral asset falls below a maintenance threshold. The real-world counterpart is a DeFi borrower facing liquidation — drawn from the participant taxonomy: (1) stablecoin holders, (2) DeFi lenders/borrowers, (3) yield depositors, (4) arbitrageurs, (5) market makers, (6) speculative attackers, (7) protocol treasuries. During the LUNA/UST collapse, cascading liquidations on Anchor and Mirror protocols amplified selling pressure as collateral was force-sold into declining markets.

The decision goal is to produce a sell order representing forced liquidation of a configurable fraction of collateral position when the observed price deviation from parity exceeds the liquidation threshold. The agent models the protocol-enforced mechanics of margin calls.

In simulation this agent exhibits liquidation cascade behaviour: each forced sale increases supply pressure, driving the price further below liquidation thresholds of other participants. Non-goals: (1) this agent MUST NOT voluntarily add collateral or top-up positions; (2) this agent MUST NOT perform arbitrage or buy-back strategies.

## Theoretical Foundation

**DeFi Liquidation Cascades**:
- Theory / Study: Decentralized finance contagion through liquidation spirals
- Citation: Werner, S. M., Perez, D., Gudgeon, L., Klages-Mundt, A., Harz, D., & Knottenbelt, W. J. (2022). SoK: Decentralized Finance (DeFi). *Proceedings of the 4th ACM Conference on Advances in Financial Technologies*. DOI:10.1145/3558535.3559780
- Core Insight: DeFi protocols enforce automated liquidations when collateral ratios breach thresholds. Unlike traditional finance where margin calls allow time for response, smart-contract liquidations execute atomically, creating concentrated sell pressure that propagates across interconnected protocols.
- Mathematical Formulation: `sell_qty = floor(|position| × liquidation_fraction) if deviation < -liquidation_threshold else 0`
- Empirical Evidence: Werner et al. document that during the May 2022 crash, Ethereum DeFi protocols liquidated over $1.2B in collateral within 48 hours, with cascading effects between Aave, Compound, and Maker. Liquidation events clustered at discrete price levels with >60% of volume occurring within 2-hour windows.
- Relevance to This Agent: The agent operationalises a single borrower's liquidation event as a forced-sell decision triggered by collateral-value decline.
- Calibration Source: Werner et al. (2022) Section 5.3 reports typical liquidation thresholds of 5-20% below maintenance margin, with liquidation fractions of 50-100% depending on protocol.
- Falsification Conditions: If this agent fails to sell when deviation crosses its liquidation threshold, the forced-liquidation mechanism is falsified.
- Alternative Theories: Voluntary de-leveraging (borrower sells before forced liquidation); partial liquidation with recovery (protocol allows gradual unwinding).

**Liquidation Efficiency and MEV**:
- Theory / Study: Empirical study of DeFi liquidation mechanisms
- Citation: Perez, D., Werner, S. M., Xu, J., & Livshits, B. (2021). Liquidations: DeFi on a Knife-Edge. *Financial Cryptography and Data Security*, 457-476. DOI:10.1007/978-3-662-64331-0_24
- Core Insight: Liquidation bots compete to execute forced sales, creating immediate market impact. The efficiency of liquidation depends on available liquidity; in thin markets, large liquidations produce outsized price impact that triggers adjacent liquidation thresholds.
- Mathematical Formulation: `price_impact = -liquidation_volume / market_depth`
- Empirical Evidence: Perez et al. analyse 28,138 liquidation events on Aave and Compound, finding that average liquidation discount is 3-8% and that 73% of liquidation value is concentrated in the top 10% of events by size.
- Relevance to This Agent: Represents the borrower side of the liquidation — the forced seller whose collateral is seized and dumped.
- Calibration Source: Perez et al. (2021) Table 4: median liquidation fraction 50-60% of collateral; typical threshold breach at 5-15% deviation.
- Falsification Conditions: If this agent's sell volume does not monotonically increase as deviation deepens beyond threshold (given constant position), the cascade intensification is falsified.
- Alternative Theories: Orderly liquidation queues (price impact smoothed over time); self-liquidation (borrower voluntarily unwinds before protocol forces).

## Design Purpose and Activation Triggers

Purpose: Exhibit forced-liquidation selling behaviour when collateral value drops below the protocol's maintenance threshold.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current collateral asset price)
- `parity` available (reference value for collateral)

Missing-Signal Policy: hold if either `price` or `parity` is unavailable or NaN; no liquidation without confirmed price data.

Activation Triggers:
- `deviation < -liquidation_threshold`: sell `floor(|position| × liquidation_fraction)` units (forced liquidation).
- `<Default>`: hold — collateral remains sufficient.

Deactivation Conditions:
- Position reaches zero: all collateral liquidated; agent becomes inert.
- Price recovers above threshold: collateral ratio restored; no liquidation.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Accelerating decline (deviation worsens) | Continues forced selling each tick | Threshold test fires every tick while breached and position > 0 |
| Recovery above threshold | Immediately ceases selling; holds remaining collateral | Liquidation condition no longer met |

Environmental Dependencies: Requires a per-tick `price` feed and a `parity` reference for computing collateral ratio. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. Current collateral asset price. |
| `parity` | environment / config | `float` | yes | Maps to §3.6.1 `parity`. Reference value for the collateral. |
| `position` | agent's own persisted state | `int` | yes | Current collateral holdings; populated by §3.6.4 init. |
| `cash` | agent's own persisted state | `float` | yes | Current cash balance. |
| `identity`, `round` | scheduler / round header | `str`, `int` | yes | Round number and agent identity. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"sell", "hold"}` | — | yes | Discrete action: forced liquidation or maintain position. |
| `quantity` | int | `[0, position]` | tokens | yes | Number of tokens force-sold. 0 when hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, position]`; out-of-range values MUST be clamped before emission.
- Units and sign conventions: `quantity` is unsigned; `sell` action implies direction. Price units match `parity`.
- Determinism markers: decision is deterministic; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<sell or hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this exact tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare fallback sentinel `"(No relevant knowledge retrieved this round.)"` and inject verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for:
1. Signal wiring — every input row MUST map to a real read against environment/state.
2. Decision emission — code MUST populate every Required=yes field and clamp out-of-range values.
3. Prompt drafting — model-driven variants MUST spell out the tag pattern and JSON schema literally.
4. Parser tests — implementation MUST include a smoke test verifying tags and JSON validity.
5. Variant parity — every declared variant MUST produce the SAME field set.
6. Contract-versus-prose conflict — this section wins on any disagreement.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current collateral price for liquidation threshold check [Ref 1] |
| `parity` | Continuous | 1 tick | Reference value for computing collateral ratio deviation [Ref 1] |

Does NOT use: order-book depth, peer liquidation events, protocol TVL, yield rates, gas prices, or historical price series beyond current tick.

#### Core Behavioral Mechanism

1. **Read** `price` and `parity` from environment; **Read** `position` and `cash` from agent state. *(implementation convenience)*
2. **Compute** deviation: `deviation = (price - parity) / parity`. *(Werner et al. 2022 — collateral ratio metric)*
3. **Compare** deviation against `-liquidation_threshold`. If `deviation >= -liquidation_threshold`, proceed to step 7 (hold). *(Perez et al. 2021 — liquidation trigger)*
4. **Compute** liquidation quantity: `sell_qty = floor(abs(position) × liquidation_fraction)`. *(Werner et al. 2022 — forced liquidation fraction)*
5. **Clamp** sell_qty: `sell_qty = min(sell_qty, position)` to prevent over-selling. *(implementation convenience)*
6. **Write** decision: emit `action=sell`, `quantity=sell_qty`. Proceed to step 8.
7. **Write** decision: emit `action=hold`, `quantity=0`.
8. **Post-decision state update**: `position -= sell_qty`; `cash += sell_qty × price`. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, hold |
| Action parameter rule | No continuous parameter; discrete action with integer sizing. |
| Sizing rule | `sell_qty = floor(abs(position) × liquidation_fraction)`, clamped to `[0, position]` |
| Action lifetime | 1 tick (immediate forced execution) |
| Revision policy | No revision; forced liquidation is irrevocable once triggered. |
| State constraint | `position >= 0` at all times (no short selling). |
| Resource cap | Limited only by remaining position; no cash cap on sells. |
| Exit rule | Agent becomes inert when `position = 0`. |

#### Mathematical Model

**Decision output**: integer sell quantity `Q(t) >= 0` per tick.

**Decision logic formalization**:
```
deviation(t) = (price(t) - parity) / parity

if deviation(t) < -liquidation_threshold AND position(t) > 0:
    Q(t) = floor(position(t) × liquidation_fraction)
    Q(t) = min(Q(t), position(t))
    action = "sell"
else:
    Q(t) = 0
    action = "hold"
```

**State variables**:
| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | `initial_position` (default 3000) |
| `cash` | float | `initial_cash` (default 800000) |

**State evolution** (post-decision, post-execution):
```
position(t+1) = position(t) - Q(t)
cash(t+1) = cash(t) + Q(t) × price(t)
```

**Determinism contract**: Deterministic given identical price path and parameters. No stochastic element.

**Parameter symbol table**:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `liquidation_threshold` | Deviation triggering forced liquidation | 0.08 | Perez et al. (2021) Table 4 |
| `liquidation_fraction` | Fraction of position force-sold | 0.6 | Werner et al. (2022) Section 5.3 |
| `parity` | Reference collateral value | 1.0 | Protocol definition |
| `initial_position` | Starting collateral holdings | 3000 | Standardised |
| `initial_cash` | Starting cash balance | 800000 | Standardised |

#### Behavioral Properties

- Time horizon: short — reacts within one tick to current deviation; no anticipation of recovery.
- Risk tolerance: medium — entered a leveraged position (implying some risk appetite) but faces forced exit on decline.
- Information asymmetry: none — uses only publicly observable price deviation.
- Psychological profile: Mechanistic protocol enforcement; no behavioural bias — liquidation is protocol-imposed, not psychologically motivated.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `liquidation_threshold` | float | 0.08 | [0.05, 0.20] | high | Deviation at which forced liquidation triggers | Higher -> fewer liquidations, weaker cascades | Perez et al. (2021) Table 4 |
| `liquidation_fraction` | float | 0.6 | (0, 1.0] | high | Fraction of collateral liquidated per trigger | Higher -> faster position depletion, stronger impact | Werner et al. (2022) Section 5.3 |
| `initial_cash` | float | 800000 | [0, 10000000] | low | Starting cash balance | Higher -> irrelevant to sell logic | Standardised |
| `initial_position` | int | 3000 | [1, 100000] | medium | Starting collateral token holdings | Higher -> more liquidation volume available | Standardised |
| `parity` | float | 1.0 | (0, inf) | low | Reference value for collateral | Higher -> deviation measured relative to larger base | Protocol definition |

## Worked Numerical Examples

### Case 1 — Liquidation triggered (moderate decline)
```text
Market state: price=0.90, parity=1.0, position=3000, cash=800000.
Parameters: liquidation_threshold=0.08, liquidation_fraction=0.6.
Calculation:
  deviation = (0.90 - 1.0) / 1.0 = -0.10
  -0.10 < -0.08 → liquidation threshold breached
  sell_qty = floor(3000 × 0.6) = 1800
  clamp: min(1800, 3000) = 1800
Decision: action=sell, quantity=1800.
State update: position: 3000 -> 1200; cash: 800000 -> 800000 + 1800×0.90 = 801620.
```

### Case 2 — Hold (within safe zone)
```text
Market state: price=0.95, parity=1.0, position=3000, cash=800000.
Parameters: liquidation_threshold=0.08, liquidation_fraction=0.6.
Calculation:
  deviation = (0.95 - 1.0) / 1.0 = -0.05
  -0.05 >= -0.08 → threshold NOT breached
Decision: action=hold, quantity=0.
State update: position: 3000 (unchanged); cash: 800000 (unchanged).
```

### Case 3 — Second-round liquidation (reduced position)
```text
Market state: price=0.80, parity=1.0, position=1200, cash=801620.
Parameters: liquidation_threshold=0.08, liquidation_fraction=0.6.
Calculation:
  deviation = (0.80 - 1.0) / 1.0 = -0.20
  -0.20 < -0.08 → threshold breached
  sell_qty = floor(1200 × 0.6) = 720
  clamp: min(720, 1200) = 720
Decision: action=sell, quantity=720.
State update: position: 1200 -> 480; cash: 801620 -> 801620 + 720×0.80 = 802196.
```

### Edge Case — Position exhausted
```text
Market state: price=0.60, parity=1.0, position=0, cash=802500.
Parameters: liquidation_threshold=0.08, liquidation_fraction=0.6.
Calculation:
  deviation = (0.60 - 1.0) / 1.0 = -0.40
  -0.40 < -0.08 → threshold breached
  sell_qty = floor(0 × 0.6) = 0
  clamp: min(0, 0) = 0
Decision: action=hold, quantity=0 (no position to liquidate).
State update: position: 0 (unchanged); cash: 802500 (unchanged). Agent is inert.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `liquidation_threshold` <- Perez et al. (2021) Table 4, typical DeFi liquidation thresholds 5-15%.
- `liquidation_fraction` <- Werner et al. (2022) Section 5.3, observed liquidation fractions 50-100%.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price=0.90 (deviation=-0.10) and threshold=0.08, agent MUST sell exactly floor(position×0.6) tokens.
- Given price=0.95 (deviation=-0.05) and threshold=0.08, agent MUST hold with quantity=0.
- Given position=0 regardless of deviation, agent MUST emit hold with quantity=0.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells when deviation is above -liquidation_threshold THEN implementation is broken because liquidation condition is not met.
- IF the agent emits quantity > position THEN implementation is broken because clamping logic is missing.
- IF the agent buys at any point THEN implementation is broken because buy is not in this agent's action space.
- IF the agent sells a fraction other than liquidation_fraction (within rounding) THEN implementation is broken because the sizing formula is incorrect.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `tight_liquidation` | `liquidation_threshold = 0.05` | Tighter threshold triggers earlier cascades | Increase in first-tick sell volume | Tokens sold in first 5 ticks |
| `full_liquidation` | `liquidation_fraction = 1.0` | Full liquidation creates maximal single-tick impact | Increase in single-tick sell pressure | Maximum per-tick sell volume |
| `no_liquidation` | `liquidation_fraction = 0.0` | Removing liquidation eliminates cascade contribution | Zero sells regardless of deviation | Total quantity sold = 0 |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Werner, S. M., Perez, D., Gudgeon, L., Klages-Mundt, A., Harz, D., & Knottenbelt, W. J. (2022). SoK: Decentralized Finance (DeFi). *Proceedings of the 4th ACM Conference on Advances in Financial Technologies*. DOI:10.1145/3558535.3559780 | DeFi contagion and liquidation mechanics |
| 2 | Perez, D., Werner, S. M., Xu, J., & Livshits, B. (2021). Liquidations: DeFi on a Knife-Edge. *Financial Cryptography and Data Security*, 457-476. DOI:10.1007/978-3-662-64331-0_24 | Empirical liquidation data, thresholds, and efficiency |
| 3 | Klages-Mundt, A., Harz, D., Gudgeon, L., Liu, J.-Y., & Minca, A. (2020). Stablecoins 2.0: Economic Foundations and Risk-based Models. *Proceedings of the 2nd ACM Conference on Advances in Financial Technologies*, 59-79. DOI:10.1145/3419614.3423261 | Stablecoin fragility framework |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-de-fi-lender.png)         |
| Change log | 2026-07-20: handbook provenance audit; reused by LUNACollapse with no profile-mechanism change. |
