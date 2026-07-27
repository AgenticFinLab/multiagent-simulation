# Yield depositor exiting on ecosystem confidence collapse

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Yield depositor exiting on ecosystem confidence collapse |
| Theory Family         | DeFi Bank-Run Dynamics |
| Behavioral Tendency   | **Diverging** — rapid withdrawals collapse total value locked, undermining yield sustainability and triggering further exits |
| Time Horizon          | short |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a yield-seeking depositor in a DeFi protocol (such as Anchor Protocol on Terra) who withdraws deposits when confidence in the yield ecosystem deteriorates. The real-world counterpart is a yield depositor — drawn from the participant taxonomy: (1) stablecoin holders, (2) DeFi lenders/borrowers, (3) yield depositors, (4) arbitrageurs, (5) market makers, (6) speculative attackers, (7) protocol treasuries. During the Terra collapse, Anchor Protocol saw its TVL drop from $17.5B to near zero as depositors raced to exit once the 19.5% APY became unsustainable.

The decision goal is to produce a sell order (withdrawal) of a configurable fraction of deposited position when the observed price deviation from parity exceeds a yield-confidence threshold. The agent optimises capital preservation by withdrawing before protocol insolvency.

In simulation this agent exhibits bank-run withdrawal behaviour specific to yield protocols: each withdrawal reduces TVL which undermines protocol sustainability, which reduces confidence, which triggers more withdrawals. Non-goals: (1) this agent MUST NOT consider re-depositing or yield-chasing once the threshold is breached; (2) this agent MUST NOT perform any form of trading or arbitrage beyond simple withdrawal.

## Theoretical Foundation

**DeFi Bank-Run Dynamics**:
- Theory / Study: Demand-deposit contracts and bank-run probability
- Citation: Goldstein, I., & Pauzner, A. (2005). Demand-Deposit Contracts and the Probability of Bank Runs. *Journal of Finance*, 60(3), 1293-1327. DOI:10.1111/j.1540-6261.2005.00741.x
- Core Insight: Demand-deposit contracts create strategic complementarities where each depositor's optimal action depends on expectations about other depositors' actions. When a sufficient fraction withdraws, the remaining assets cannot cover all deposits, making early withdrawal individually rational — the classic bank-run coordination failure.
- Mathematical Formulation: `withdraw_qty = floor(position × withdrawal_fraction) if deviation < -yield_threshold else 0`
- Empirical Evidence: Goldstein & Pauzner prove existence of a unique equilibrium in their global-games model; empirically, Anchor Protocol lost 99%+ of TVL ($17.5B to <$100M) in 7 days (May 7-14, 2022), consistent with a pure-strategy run equilibrium.
- Relevance to This Agent: The agent operationalises the individual depositor's withdrawal decision that, in aggregate, constitutes the bank run on the yield protocol.
- Calibration Source: Goldstein & Pauzner (2005) Proposition 3 implies run probability increases discontinuously above a critical signal threshold; Terra/Anchor data shows median depositor exit at 10-15% de-peg.
- Falsification Conditions: If this agent fails to withdraw within one tick of deviation exceeding `yield_threshold`, the bank-run participation mechanism is falsified.
- Alternative Theories: Patient waiting (depositors believe protocol will recover); gradual wind-down (depositors exit uniformly over time regardless of signal).

**Terra/Anchor Collapse Mechanism**:
- Theory / Study: Algorithmic stablecoin and yield protocol collapse dynamics
- Citation: Klages-Mundt, A., Harz, D., Gudgeon, L., Liu, J.-Y., & Minca, A. (2020). Stablecoins 2.0: Economic Foundations and Risk-based Models. *Proceedings of the 2nd ACM Conference on Advances in Financial Technologies*, 59-79. DOI:10.1145/3419614.3423261
- Core Insight: Yield protocols backed by algorithmic stablecoins face double fragility: the yield depends on stablecoin stability, and the stablecoin depends on confidence maintained partly by yield incentives. Breaking either link triggers a reflexive collapse.
- Mathematical Formulation: `d(TVL)/dt = -withdrawal_rate × TVL × I(deviation < -threshold)`
- Empirical Evidence: Anchor TVL dropped from $17.5B to $1.2B within 72 hours of the initial UST de-peg, implying a per-day withdrawal rate of approximately 70% of remaining TVL once the threshold was crossed.
- Relevance to This Agent: Represents the individual depositor whose withdrawal contributes to TVL decline, which further destabilises the protocol.
- Calibration Source: Klages-Mundt et al. (2020) Section 3; Terra post-mortem data: depositor exit rates of 30-50% per day during acute phase.
- Falsification Conditions: If this agent holds position unchanged while deviation exceeds 2× its threshold for more than 3 ticks, the yield-run participation is falsified.
- Alternative Theories: Protocol rescue (yield reduction rather than collapse); deposit insurance (external backstop prevents runs).

## Design Purpose and Activation Triggers

Purpose: Exhibit yield-protocol bank-run withdrawal behaviour when the stablecoin deviates from parity beyond a confidence threshold.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current stablecoin/yield-token price)
- `parity` available (reference peg value, typically 1.0)

Missing-Signal Policy: hold if either `price` or `parity` is unavailable or NaN; retain full deposit until signals resume.

Activation Triggers:
- `deviation < -yield_threshold`: sell `floor(position × withdrawal_fraction)` units (withdrawal).
- `<Default>`: hold — confidence maintained; continue earning yield.

Deactivation Conditions:
- Position reaches zero: fully withdrawn; agent becomes inert.
- Price recovers above parity minus threshold: confidence restored; holds remaining deposit.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Deepening de-peg (worsening deviation) | Continues withdrawing each tick while threshold is breached | Stateless threshold check fires each tick |
| Recovery above threshold | Ceases withdrawal; holds remaining position | Threshold gate no longer satisfied |

Environmental Dependencies: Requires a per-tick `price` feed and a `parity` reference. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. Current yield-token/stablecoin price. |
| `parity` | environment / config | `float` | yes | Maps to §3.6.1 `parity`. Reference peg value (default 1.0). |
| `position` | agent's own persisted state | `int` | yes | Current deposited holdings; populated by §3.6.4 init. |
| `cash` | agent's own persisted state | `float` | yes | Current cash balance. |
| `identity`, `round` | scheduler / round header | `str`, `int` | yes | Round number and agent identity. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"sell", "hold"}` | — | yes | Discrete action: withdraw deposit or maintain. |
| `quantity` | int | `[0, position]` | tokens | yes | Number of tokens withdrawn. 0 when hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, position]`; out-of-range values MUST be clamped before emission.
- Units and sign conventions: `quantity` is unsigned; `sell` action implies withdrawal direction. Price units match `parity`.
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
| `price` | Continuous | 1 tick | Current price for deviation calculation [Ref 1, 2] |
| `parity` | Continuous | 1 tick | Reference peg target for deviation measurement [Ref 2] |

Does NOT use: yield APY, TVL data, peer withdrawal counts, protocol reserve ratios, gas prices, or historical price series.

#### Core Behavioral Mechanism

1. **Read** `price` and `parity` from environment; **Read** `position` and `cash` from agent state. *(implementation convenience)*
2. **Compute** deviation: `deviation = (price - parity) / parity`. *(Klages-Mundt et al. 2020 — peg deviation metric)*
3. **Compare** deviation against `-yield_threshold`. If `deviation >= -yield_threshold`, proceed to step 7 (hold). *(Goldstein & Pauzner 2005 — critical signal threshold)*
4. **Compute** withdrawal quantity: `sell_qty = floor(position × withdrawal_fraction)`. *(Goldstein & Pauzner 2005 — partial withdrawal in run equilibrium)*
5. **Clamp** sell_qty: `sell_qty = min(sell_qty, position)` to ensure non-negative remaining deposit. *(implementation convenience)*
6. **Write** decision: emit `action=sell`, `quantity=sell_qty`. Proceed to step 8.
7. **Write** decision: emit `action=hold`, `quantity=0`.
8. **Post-decision state update**: `position -= sell_qty`; `cash += sell_qty × price`. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, hold |
| Action parameter rule | No continuous parameter; discrete action with integer sizing. |
| Sizing rule | `sell_qty = floor(position × withdrawal_fraction)`, clamped to `[0, position]` |
| Action lifetime | 1 tick (immediate withdrawal assumed) |
| Revision policy | No revision; once withdrawal is submitted, it stands. |
| State constraint | `position >= 0` at all times (no negative deposits). |
| Resource cap | Limited only by remaining deposit; no cap on number of withdrawals. |
| Exit rule | Agent becomes inert when `position = 0`. |

#### Mathematical Model

**Decision output**: integer withdrawal quantity `Q(t) >= 0` per tick.

**Decision logic formalization**:
```
deviation(t) = (price(t) - parity) / parity

if deviation(t) < -yield_threshold AND position(t) > 0:
    Q(t) = floor(position(t) × withdrawal_fraction)
    Q(t) = min(Q(t), position(t))
    action = "sell"
else:
    Q(t) = 0
    action = "hold"
```

**State variables**:
| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | `initial_position` (default 2500) |
| `cash` | float | `initial_cash` (default 400000) |

**State evolution** (post-decision, post-execution):
```
position(t+1) = position(t) - Q(t)
cash(t+1) = cash(t) + Q(t) × price(t)
```

**Determinism contract**: Deterministic given identical price path and parameters. No stochastic element.

**Parameter symbol table**:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `yield_threshold` | Deviation triggering confidence-based withdrawal | 0.12 | Goldstein & Pauzner (2005); Terra post-mortem data |
| `withdrawal_fraction` | Fraction of deposit withdrawn per trigger | 0.4 | Klages-Mundt et al. (2020) Section 3 |
| `parity` | Reference peg value | 1.0 | Protocol definition |
| `initial_position` | Starting deposit holdings | 2500 | Standardised |
| `initial_cash` | Starting cash balance | 400000 | Standardised |

#### Behavioral Properties

- Time horizon: short — reacts within one tick to current deviation without modelling protocol recovery dynamics.
- Risk tolerance: low — deposited for yield but exits at the first sign of systemic stress; prioritises capital over continued yield.
- Information asymmetry: none — uses only publicly observable price deviation.
- Psychological profile: Safety-first preference with bank-run coordination failure; exhibits herd-following withdrawal behaviour triggered by observable market stress signal.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `yield_threshold` | float | 0.12 | [0.05, 0.25] | high | Deviation at which yield-confidence breaks and withdrawal triggers | Higher -> more patient depositor, later withdrawal | Goldstein & Pauzner (2005) Proposition 3 |
| `withdrawal_fraction` | float | 0.4 | (0, 1.0] | high | Fraction of remaining deposit withdrawn per trigger | Higher -> faster TVL drain per tick | Klages-Mundt et al. (2020) Section 3 |
| `initial_cash` | float | 400000 | [0, 10000000] | low | Starting cash balance | Higher -> irrelevant to withdrawal logic | Standardised |
| `initial_position` | int | 2500 | [1, 100000] | medium | Starting deposit token holdings | Higher -> more withdrawal volume fuelling run | Standardised |
| `parity` | float | 1.0 | (0, inf) | low | Reference peg target value | Higher -> deviation measured relative to larger base | Protocol definition |

## Worked Numerical Examples

### Case 1 — Withdrawal triggered (moderate de-peg)
```text
Market state: price=0.85, parity=1.0, position=2500, cash=400000.
Parameters: yield_threshold=0.12, withdrawal_fraction=0.4.
Calculation:
  deviation = (0.85 - 1.0) / 1.0 = -0.15
  -0.15 < -0.12 → yield-confidence threshold breached
  sell_qty = floor(2500 × 0.4) = 1000
  clamp: min(1000, 2500) = 1000
Decision: action=sell, quantity=1000.
State update: position: 2500 -> 1500; cash: 400000 -> 400000 + 1000×0.85 = 400850.
```

### Case 2 — Hold (within confidence zone)
```text
Market state: price=0.92, parity=1.0, position=2500, cash=400000.
Parameters: yield_threshold=0.12, withdrawal_fraction=0.4.
Calculation:
  deviation = (0.92 - 1.0) / 1.0 = -0.08
  -0.08 >= -0.12 → threshold NOT breached
Decision: action=hold, quantity=0.
State update: position: 2500 (unchanged); cash: 400000 (unchanged).
```

### Case 3 — Second-round withdrawal (reduced position)
```text
Market state: price=0.70, parity=1.0, position=1500, cash=400850.
Parameters: yield_threshold=0.12, withdrawal_fraction=0.4.
Calculation:
  deviation = (0.70 - 1.0) / 1.0 = -0.30
  -0.30 < -0.12 → threshold breached
  sell_qty = floor(1500 × 0.4) = 600
  clamp: min(600, 1500) = 600
Decision: action=sell, quantity=600.
State update: position: 1500 -> 900; cash: 400850 -> 400850 + 600×0.70 = 401270.
```

### Edge Case — Position exhausted
```text
Market state: price=0.50, parity=1.0, position=0, cash=401800.
Parameters: yield_threshold=0.12, withdrawal_fraction=0.4.
Calculation:
  deviation = (0.50 - 1.0) / 1.0 = -0.50
  -0.50 < -0.12 → threshold breached
  sell_qty = floor(0 × 0.4) = 0
  clamp: min(0, 0) = 0
Decision: action=hold, quantity=0 (no position to withdraw).
State update: position: 0 (unchanged); cash: 401800 (unchanged). Agent is inert.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `yield_threshold` <- Goldstein & Pauzner (2005) critical threshold concept; Terra/Anchor empirical data showing median exit at 10-15% de-peg.
- `withdrawal_fraction` <- Klages-Mundt et al. (2020) Section 3; Anchor per-day withdrawal rates 30-50% during acute phase.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price=0.85 (deviation=-0.15) and threshold=0.12, agent MUST sell exactly floor(position×0.4) tokens.
- Given price=0.92 (deviation=-0.08) and threshold=0.12, agent MUST hold with quantity=0.
- Given position=0 regardless of deviation, agent MUST emit hold with quantity=0.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent withdraws when deviation is above -yield_threshold THEN implementation is broken because confidence condition is not met.
- IF the agent emits quantity > position THEN implementation is broken because clamping logic is missing.
- IF the agent buys or re-deposits at any point THEN implementation is broken because buy/deposit is not in this agent's action space.
- IF the agent's position increases between ticks THEN implementation is broken because only withdrawals are permitted.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `sensitive_depositor` | `yield_threshold = 0.05` | Lower threshold triggers earlier run onset | Increase in early-round withdrawal volume | Tokens withdrawn by tick 5 |
| `aggressive_withdrawal` | `withdrawal_fraction = 0.8` | Higher fraction accelerates TVL collapse | Increase in per-tick outflow | Ticks until position < 10% of initial |
| `no_withdrawal` | `withdrawal_fraction = 0.0` | Removing withdrawal eliminates run contribution | No sells emitted | Total quantity sold = 0 |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Goldstein, I., & Pauzner, A. (2005). Demand-Deposit Contracts and the Probability of Bank Runs. *Journal of Finance*, 60(3), 1293-1327. DOI:10.1111/j.1540-6261.2005.00741.x | Bank-run coordination game, critical threshold |
| 2 | Klages-Mundt, A., Harz, D., Gudgeon, L., Liu, J.-Y., & Minca, A. (2020). Stablecoins 2.0: Economic Foundations and Risk-based Models. *Proceedings of the 2nd ACM Conference on Advances in Financial Technologies*, 59-79. DOI:10.1145/3419614.3423261 | Algorithmic stablecoin fragility, yield-protocol feedback |
| 3 | Levy, A. (2022). Understanding the Instability of Algorithmic Stablecoins. *Working Paper*, Princeton University. arXiv:2209.01182 | Death spiral empirical analysis, Terra/Anchor data |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-anchor-depositor.png)         |
| Change log | 2026-07-20: handbook provenance audit; reused by LUNACollapse with no profile-mechanism change. |
