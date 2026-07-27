# Speculative attacker

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Currency speculator attacking weak fixed exchange-rate pegs |
| Theory Family         | International Macro / Speculative Attack Theory |
| Behavioral Tendency   | **Diverging** - destabilises pegged exchange rates by shorting the currency when fundamentals are inconsistent with the peg |
| Time Horizon          | short |
| Risk Tolerance        | very high |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a macro hedge fund or currency speculator who identifies weak currency pegs and attacks them by shorting the pegged currency, exhausting central bank reserves, and forcing a devaluation. The real-world counterpart is the speculative attacker described by Obstfeld (1996) and the first-generation crisis model of Krugman (1979). The agent monitors reserve levels and fundamental misalignment, then launches large short positions when collapse appears imminent.

The decision goal is to profit from the forced devaluation of a weak currency peg by building short positions before the peg breaks. It is not a carry trader and does not seek yield. Non-goals: it must not attack currencies with strong fundamentals and ample reserves, and it must not hold positions passively without monitoring reserve depletion.

## Theoretical Foundation

**Self-fulfilling currency crises (second generation)**:
- Theory / Study: The logic of currency crises.
- Citation: Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3-5), 1037-1047. https://doi.org/10.1016/0014-2921(95)00110-7
- Core Insight: In the presence of multiple equilibria, coordinated speculative pressure can force a currency devaluation even when the peg might otherwise survive. The attack is self-fulfilling: it succeeds because enough speculators participate.
- Mathematical Formulation: Attack condition: `reserves / GDP < critical_ratio` AND `fundamental_misalignment > attack_threshold`. Position: `q = attack_size * (misalignment / attack_threshold)`.
- Empirical Evidence: Obstfeld models the 1992 ERM crisis and shows multiple equilibria where speculator coordination determines outcomes.
- Relevance to This Agent: The agent monitors reserve adequacy and fundamental misalignment to time attacks.
- Calibration Source: `reserve_ratio_critical` 0.05-0.15, `attack_threshold` 0.03-0.10.
- Falsification Conditions: If the agent attacks currencies with reserves above critical ratio and no fundamental misalignment, the design is falsified.
- Alternative Theories: First-generation models (deterministic collapse); third-generation models (balance-sheet crises).

**First-generation crisis model**:
- Theory / Study: A model of balance-of-payments crises.
- Citation: Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311-325. https://doi.org/10.2307/1991793
- Core Insight: When a government runs persistent fiscal deficits financed by credit creation, reserves deplete at a predictable rate and rational speculators attack the peg in a discrete jump before reserves hit zero, earning the remaining reserves as profit.
- Mathematical Formulation: `shadow_rate = exchange_rate + credit_growth * t`. Attack occurs when `shadow_rate > peg_rate`, i.e., when maintaining the peg requires reserves that will be exhausted.
- Empirical Evidence: Krugman's model explains the timing of speculative attacks in Latin American crises of the 1980s.
- Relevance to This Agent: The agent detects reserve depletion trajectories and attacks before the final collapse.
- Calibration Source: `reserve_depletion_rate` as observable signal.
- Falsification Conditions: If the agent attacks when reserves are rising or stable with no credit expansion, the design is falsified.
- Alternative Theories: Random-walk exchange rates; purchasing-power-parity gradual adjustment.

## Design Purpose and Activation Triggers

Purpose: Identify and exploit weak currency pegs by building large short positions when reserves are depleted and fundamentals are misaligned, profiting from forced devaluation.

Call Frequency: every-tick.

Prerequisite Signals:
- `exchange_rate` available (current pegged rate)
- `reserves` available (central bank foreign reserves)
- `fundamental_misalignment` available (deviation of real exchange rate from equilibrium)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `reserves / initial_reserves < reserve_ratio_critical` AND `fundamental_misalignment > attack_threshold`: attack (sell currency / short), sized by `attack_size * (misalignment / attack_threshold)`.
- `reserves / initial_reserves >= reserve_ratio_critical`: hold (peg still defensible).
- Peg breaks (price drops below peg by `devaluation_target`): cover short / take profit.
- `<Default>`: hold.

Deactivation Conditions:
- peg breaks and profit is taken.
- reserves recover above critical threshold.
- cash insufficient to maintain short.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| low reserves + misalignment | aggressive short selling | speculative attack |
| peg collapse | profit-taking (cover short) | objective achieved |
| adequate reserves | holds, monitors | peg still defensible |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `exchange_rate` | environment | float | yes | current exchange rate |
| `reserves` | environment | float | yes | central bank reserves level |
| `fundamental_misalignment` | environment | float | yes | real exchange rate overvaluation (0-1) |
| `cash` | own state | float | yes | available capital for margin |
| `position` | own state | float | yes | current short position (negative = short) |
| `initial_reserves` | environment | float | yes | starting reserve level for ratio |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction (sell = short currency) |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash (margin) or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `exchange_rate` | Continuous | 1 tick | execution reference |
| `reserves` | Continuous | 1 tick | attack feasibility |
| `fundamental_misalignment` | Continuous | 1 tick | attack signal |
| `cash` | State | persistent | margin capacity |
| `position` | State | persistent | current exposure |

Does NOT use: domestic interest rates, retail sentiment, equity indices.

#### Core Behavioral Mechanism

1. Read `exchange_rate`, `reserves`, `fundamental_misalignment`, `cash`, `position`, and `initial_reserves`.
2. Compute `reserve_ratio = reserves / initial_reserves`.
3. If `reserve_ratio < reserve_ratio_critical` AND `fundamental_misalignment > attack_threshold`:
   - Compute `q = attack_size * (fundamental_misalignment / attack_threshold)`.
   - Sell (short) `min(q, cash / margin_rate)`.
4. If peg has broken (price dropped significantly): buy to cover short, `q = min(|position|, cover_size)`.
5. Otherwise hold and monitor.
6. Emit decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy (cover), sell (short), hold |
| Action parameter rule | market order at current rate |
| Sizing rule | `attack_size * (misalignment / threshold)`, capped by margin capacity |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | short position limited by margin / cash |
| Resource cap | short size limited by `cash / margin_rate` |
| Exit rule | cover short when peg breaks or reserves recover |

#### Mathematical Model

`q_attack = min(cash / margin_rate, attack_size * (fundamental_misalignment / attack_threshold))` if `reserve_ratio < reserve_ratio_critical` and `fundamental_misalignment > attack_threshold`; `q_cover = min(|position|, cover_size)` if peg broken; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `reserve_ratio_critical` | reserve threshold triggering attack | 0.10 | Obstfeld (1996) |
| `attack_threshold` | minimum misalignment to justify attack | 0.05 | Krugman (1979) |
| `attack_size` | base short position size | 2000.0 | scenario calibration |
| `margin_rate` | margin requirement per unit short | 0.10 | broker margin |
| `cover_size` | units covered per tick when taking profit | 1000.0 | gradual exit |

#### Behavioral Properties

- Time horizon: short, because speculative attacks unfold over days to weeks.
- Risk tolerance: very high, because attacking a central bank carries tail risk of intervention.
- Information asymmetry: partial, because reserve levels may be published with delay.
- Psychological profile: aggressive macro speculator betting against unsustainable policy.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `reserve_ratio_critical` | float | 0.10 | [0.05, 0.15] | high | reserve depletion level triggering attack | Lower -> later attack, more certain | Obstfeld (1996) |
| `attack_threshold` | float | 0.05 | [0.03, 0.10] | high | minimum fundamental misalignment to attack | Higher -> fewer attacks, more selective | Krugman (1979) |
| `attack_size` | float | 2000.0 | [1000, 5000] | high | base short position per attack tick | Higher -> more pressure on peg | scenario calibration |
| `margin_rate` | float | 0.10 | [0.05, 0.20] | medium | margin required per unit of short exposure | Higher -> smaller positions per cash | broker rules |
| `cover_size` | float | 1000.0 | [500, 2000] | low | units covered per tick during profit-taking | Higher -> faster exit | scenario calibration |

## Worked Numerical Examples

### Case 1 - Attack Initiation

System state: exchange_rate 1.0 (peg), reserves 800, initial_reserves 10000, fundamental_misalignment 0.08, cash 100000, position 0.
Calculation: `reserve_ratio = 800/10000 = 0.08 < 0.10`. `misalignment (0.08) > attack_threshold (0.05)`.
`q = 2000 * (0.08/0.05) = 3200`. `min(3200, 100000/0.10) = min(3200, 1000000) = 3200`.
Decision: sell 3200 (initiate short).
State update: position becomes -3200; cash provides margin.

### Case 2 - Peg Breaks (Profit Taking)

System state: exchange_rate 0.75 (peg broke, devalued), reserves 200, position -3200, cash 100000.
Calculation: peg has broken (rate dropped >10% from peg). Cover short.
`q = min(3200, 1000) = 1000`.
Decision: buy 1000 (cover partial short at devalued rate).
State update: position moves toward zero; profit realised.

### Case 3 - Reserves Adequate (No Attack)

System state: exchange_rate 1.0, reserves 5000, initial_reserves 10000, fundamental_misalignment 0.12, cash 100000, position 0.
Calculation: `reserve_ratio = 5000/10000 = 0.50 > 0.10` -> reserves still adequate.
Decision: hold.
State update: unchanged (wait for further reserve depletion).

### Edge Case - Misalignment Below Threshold

System state: exchange_rate 1.0, reserves 500, initial_reserves 10000, fundamental_misalignment 0.03, cash 100000, position 0.
Calculation: `reserve_ratio = 0.05 < 0.10` BUT `misalignment (0.03) < attack_threshold (0.05)`.
Decision: hold (insufficient misalignment despite low reserves).
State update: unchanged.

## Behavioral Verification and Calibration

- Given low reserves AND high misalignment, agent must initiate short position.
- Given adequate reserves, agent must hold regardless of misalignment.
- Given peg break with existing short, agent must cover (buy).
- Agent must never attack when both reserves are adequate and misalignment is below threshold.
- Attack size must scale with misalignment magnitude.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| early-attacker | `reserve_ratio_critical = 0.20` | earlier attacks test peg resilience | increase | attack frequency |
| small-attack | `attack_size = 500` | smaller attacks fail to break peg | decrease | peg-break probability |
| no-misalignment-check | `attack_threshold = 0.0` | attacks without fundamental basis waste capital | decrease | attack profitability |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3-5), 1037-1047. https://doi.org/10.1016/0014-2921(95)00110-7 | Second-generation crisis model |
| 2 | Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311-325. https://doi.org/10.2307/1991793 | First-generation crisis model |
| 3 | Morris, S., & Shin, H. S. (1998). Unique equilibrium in a model of self-fulfilling currency attacks. *American Economic Review*, 88(3), 587-597. https://www.jstor.org/stable/116850 | Global games approach to attack coordination |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-speculative-attacker.png) |
| Status | draft |
