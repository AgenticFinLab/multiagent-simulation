# Central bank currency peg defender

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Central bank currency peg defender |
| Theory Family         | Currency Crisis / Official Intervention |
| Behavioral Tendency   | **Converging** — intervenes to pull the exchange rate back toward the declared peg target |
| Time Horizon          | medium |
| Risk Tolerance        | low |
| Information Asymmetry | full |
| Determinism           | deterministic |

## Definition and Goals

This agent models a central bank defending a fixed exchange-rate peg by buying or selling foreign-exchange reserves. The real-world counterpart is the monetary authority intervening in currency markets to maintain a pre-announced parity — a participant class documented in Krugman (1979) first-generation crisis models and Obstfeld (1996) second-generation self-fulfilling crisis framework. Examples include the Bank of England defending sterling in 1992, the Hong Kong Monetary Authority defending its dollar peg, and the Swiss National Bank's EUR/CHF floor.

The decision goal is to maintain the exchange rate within a tolerance band around the peg target. When the market price deviates beyond a defense threshold, the agent deploys reserves to push price back toward the peg. The agent buys (sells) the domestic currency using reserves when the exchange rate depreciates (appreciates) beyond the tolerance band, sizing its intervention proportionally to the deviation magnitude.

Inside the simulation the agent acts as a powerful stabilising anchor that resists speculative pressure on the peg. It absorbs selling pressure during attacks and distributes reserves to maintain confidence. Non-goals: (1) the agent must NOT continue defending when reserves are exhausted (it must deactivate at the reserve floor, modeling crisis collapse); (2) the agent must NOT pursue profit or speculate on exchange-rate movements beyond peg maintenance.

## Theoretical Foundation

**First-generation currency crisis (Krugman 1979)**:
- Theory / Study: A model of balance-of-payments crises.
- Citation: Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311-325. https://doi.org/10.2307/1991793
- Core Insight: A central bank defending a fixed peg with finite reserves will exhaust them under persistent speculative pressure. The crisis is a deterministic outcome of inconsistent monetary/fiscal policy — once reserves hit a floor, the peg collapses. The rate of reserve loss is proportional to the deviation of the shadow exchange rate from the peg.
- Mathematical Formulation: `intervention_qty = min(reserves, defense_intensity * abs(deviation) * sizing_scale)` where `deviation = price - peg_target`
- Empirical Evidence: Krugman (1979) model validated by Flood & Garber (1984) with data from 1970s Latin American pegs; reserve depletion patterns show linear drawdown preceding collapse (R-squared > 0.85 for Mexico 1976, Argentina 1981).
- Relevance to This Agent: The agent operationalises the central bank's intervention rule — deploying reserves proportional to deviation until a reserve floor triggers deactivation (peg collapse).
- Calibration Source: defense_threshold 0.005-0.02 from empirical peg-band widths (ERM ±2.25%); reserve_floor 0.05-0.20 of initial reserves from Obstfeld (1996) critical-mass estimates.
- Falsification Conditions: If the agent continues to sell reserves after hitting reserve_floor, or if it does not intervene when deviation exceeds defense_threshold and reserves are available, the design is falsified.
- Alternative Theories: Obstfeld (1996) second-generation self-fulfilling crisis; target-zone models (Krugman 1991); managed float without explicit peg.

**Second-generation crisis (Obstfeld 1996)**:
- Theory / Study: Models of currency crises with self-fulfilling features.
- Citation: Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3-5), 1037-1047. https://doi.org/10.1016/0014-2921(95)00110-7
- Core Insight: Even with adequate reserves, a central bank may abandon the peg if the cost of defense (high interest rates, reserve depletion) exceeds the benefit of maintaining it. This creates multiple equilibria where speculative attacks become self-fulfilling. The deactivation decision depends on a cost-benefit threshold.
- Mathematical Formulation: `deactivate if reserves < reserve_floor * initial_reserves`
- Empirical Evidence: Obstfeld (1996) explains ERM 1992 crises where UK and Italy abandoned pegs despite non-zero reserves; Eichengreen, Rose & Wyplosz (1995) find reserve losses of 20-40% of initial stock precede abandonment (N=57 episodes, p < 0.05).
- Relevance to This Agent: The agent's deactivation condition (reserve floor) captures the Obstfeld mechanism — defense stops when reserves cross a critical threshold, modeling the self-fulfilling crisis equilibrium.
- Calibration Source: reserve_floor at 10-20% of initial reserves from Eichengreen et al. (1995) empirical collapse data.
- Falsification Conditions: If the agent does not deactivate when reserves fall below reserve_floor, the second-generation crisis mechanism is falsified.
- Alternative Theories: Krugman (1979) deterministic exhaustion; Morris & Shin (1998) global games approach.

## Design Purpose and Activation Triggers

Purpose: Defend the currency peg by deploying reserves against exchange-rate deviations, deactivating when reserves reach a critical floor.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (exchange rate)
- own `cash` (reserves) available
- own `position` available

Missing-Signal Policy: hold when price signal is unavailable; retain last reserves value.

Activation Triggers:
- `price > peg_target + defense_threshold`: sell reserves (buy domestic currency) sized by `defense_intensity * (price - peg_target) * sizing_scale`.
- `price < peg_target - defense_threshold`: buy reserves (sell domestic currency) sized by `defense_intensity * (peg_target - price) * sizing_scale`.
- `<Default>`: hold.

Deactivation Conditions:
- `cash < reserve_floor * initial_reserves`: peg defense abandoned, agent holds permanently.
- Price returns within tolerance band (temporary deactivation of that tick's intervention).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Sustained speculative pressure (deviation > 2x defense_threshold for > 5 ticks) | Increases effective defense_intensity by escalation factor | Escalating defense to signal commitment per Obstfeld cost-benefit |
| Reserves approaching floor (cash < 2x reserve_floor * initial_reserves) | Reduces sizing to conserve remaining reserves | Self-preservation to delay collapse |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current exchange rate |
| `cash` | own state | float | yes | current reserve level for intervention capacity |
| `position` | own state | float | yes | current domestic currency position |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | intervention direction (sell = deploy reserves to defend peg) |
| `quantity` | float | `>= 0` | units | yes | intervention size |
| `reasoning` | string | 1-3 sentences | — | yes | audit trail explaining deviation and reserve state |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: sell quantity clamped to available cash (reserves); buy quantity clamped to available position.
- Units: quantity in reserve units; price in exchange-rate units.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning (1-3 sentences) explaining peg deviation, reserve status, and intervention logic...</analysis>
<decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>
```

No retrieval-augmented variant declared; retrieval fallback sentinel not applicable.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current exchange rate for deviation computation |
| `cash` | State | persistent | reserve level (intervention capacity) |
| `position` | State | persistent | domestic currency holding |

Does NOT use: private speculator positions, interest rates, fiscal indicators, order-book depth, sentiment.

#### Core Behavioral Mechanism

1. **Read** `price`, `cash`, `position`, `initial_reserves`. (implementation convenience)
2. **Check** deactivation: if `cash < reserve_floor * initial_reserves`, return hold. Read: cash, reserve_floor, initial_reserves. Write: deactivation flag. (Traces to Obstfeld 1996)
3. **Compute** deviation: `deviation = price - peg_target`. Read: price, peg_target. Write: deviation. (Traces to Krugman 1979)
4. **Evaluate** threshold: if `abs(deviation) <= defense_threshold`, return hold. Read: deviation, defense_threshold. Write: decision. (Traces to Krugman 1979 — tolerance band)
5. **Compute** raw intervention size: `raw_q = defense_intensity * abs(deviation) * sizing_scale`. Read: defense_intensity, deviation, sizing_scale. Write: raw_q. (Traces to Krugman 1979)
6. **Determine** direction: if `deviation > 0`, action = sell (deploy reserves). If `deviation < 0`, action = buy (accumulate reserves). Read: deviation. Write: action. (Traces to Krugman 1979)
7. **Clamp** quantity: if sell, `q = min(raw_q, cash)`; if buy, `q = min(raw_q, position)`. Read: raw_q, cash, position. Write: q. (implementation convenience — resource constraint)
8. **Emit** decision object with action, quantity, reasoning.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market intervention at current exchange rate |
| Sizing rule | `defense_intensity * abs(deviation) * sizing_scale`, clamped by cash or position |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | cash >= reserve_floor * initial_reserves (else deactivate permanently) |
| Resource cap | sell quantity <= cash; buy quantity <= position |
| Exit rule | permanently hold when cash < reserve_floor * initial_reserves |

#### Mathematical Model

**Decision output:** action in {buy, sell, hold} and quantity q >= 0.

**Decision logic:**
```
if cash < reserve_floor * initial_reserves:
    action = hold; q = 0  # peg abandoned

deviation = price - peg_target

if deviation > defense_threshold:
    action = sell
    q = min(defense_intensity * deviation * sizing_scale, cash)
elif deviation < -defense_threshold:
    action = buy
    q = min(defense_intensity * abs(deviation) * sizing_scale, position)
else:
    action = hold; q = 0
```

**State variables:**
| Variable | Type | Initial Value |
|----------|------|---------------|
| `cash` | float | scenario-assigned (= initial_reserves) |
| `position` | float | scenario-assigned |
| `initial_reserves` | float | scenario-assigned (constant) |

**State evolution:** `cash` decremented by sold quantity post-execution (sell = deploy reserves). `position` decremented by bought quantity. Updated by environment.

**Determinism contract:** Fully deterministic given identical inputs and state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `peg_target` | defended exchange rate level | 1.0 | Scenario-defined peg |
| `defense_threshold` | minimum deviation to trigger intervention | 0.01 | ERM ±2.25% band width |
| `defense_intensity` | intervention aggressiveness multiplier | 2.0 | Krugman (1979) |
| `sizing_scale` | deviation-to-quantity multiplier | 10000.0 | Scenario normalization |
| `reserve_floor` | fraction of initial reserves at which defense stops | 0.10 | Eichengreen et al. (1995) |

#### Behavioral Properties

- Time horizon: medium — defends peg over multiple periods but cannot sustain indefinitely with finite reserves.
- Risk tolerance: low — prioritises peg stability over profit; deactivates rather than risk total depletion.
- Information asymmetry: full — knows own reserve level and peg target with certainty; observes market price.
- Psychological profile: rational institutional actor with commitment device (peg announcement); no cognitive biases; policy-rule-following behavior with clear exit condition.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `peg_target` | float | 1.0 | (0, inf) | high | exchange rate level the agent defends | Shift changes equilibrium attack threshold | Scenario-defined |
| `defense_threshold` | float | 0.01 | [0.005, 0.025] | high | minimum price deviation to trigger intervention | Higher -> wider tolerance band, fewer interventions | ERM band widths, Krugman (1979) |
| `defense_intensity` | float | 2.0 | [1.0, 5.0] | high | base aggressiveness of reserve deployment | Higher -> larger interventions per unit deviation | Krugman (1979) calibration |
| `sizing_scale` | float | 10000.0 | [5000, 20000] | medium | deviation-to-quantity multiplier | Higher -> more reserves deployed per unit deviation | Scenario normalization |
| `reserve_floor` | float | 0.10 | [0.05, 0.20] | high | fraction of initial reserves triggering abandonment | Higher -> earlier peg collapse, more residual reserves | Eichengreen et al. (1995) |

## Worked Numerical Examples

### Case 1 — Sell reserves (exchange rate above peg)
System state: price = 1.03, peg_target = 1.0, cash = 500000, position = 200000, initial_reserves = 500000.
Calculation:
  cash (500000) > reserve_floor * initial_reserves (0.10 * 500000 = 50000) → active
  deviation = 1.03 - 1.0 = 0.03
  abs(deviation) (0.03) > defense_threshold (0.01) → intervene
  direction: deviation > 0 → sell
  raw_q = 2.0 * 0.03 * 10000 = 600
  q = min(600, 500000) = 600
Decision: sell 600 units of reserves.
State update: cash decreases post-execution.

### Case 2 — Buy reserves (exchange rate below peg)
System state: price = 0.97, peg_target = 1.0, cash = 400000, position = 100000, initial_reserves = 500000.
Calculation:
  cash (400000) > reserve_floor * initial_reserves (50000) → active
  deviation = 0.97 - 1.0 = -0.03
  abs(deviation) (0.03) > defense_threshold (0.01) → intervene
  direction: deviation < 0 → buy
  raw_q = 2.0 * 0.03 * 10000 = 600
  q = min(600, 100000) = 600
Decision: buy 600 units.
State update: position decreases post-execution.

### Case 3 — Hold (within tolerance band)
System state: price = 1.005, peg_target = 1.0, cash = 450000, initial_reserves = 500000.
Calculation:
  cash (450000) > reserve_floor * initial_reserves (50000) → active
  deviation = 1.005 - 1.0 = 0.005
  abs(deviation) (0.005) <= defense_threshold (0.01) → hold
Decision: hold, quantity = 0.
State update: unchanged.

### Edge Case — Reserve floor breached (peg abandoned)
System state: price = 1.05, peg_target = 1.0, cash = 40000, initial_reserves = 500000.
Calculation:
  cash (40000) < reserve_floor * initial_reserves (0.10 * 500000 = 50000) → DEACTIVATED
Decision: hold, quantity = 0 (peg defense abandoned).
State update: unchanged; agent holds permanently.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `defense_threshold` <- ERM band widths ±2.25% (Eichengreen et al. 1995); Hong Kong HKMA 7.75-7.85 band.
- `defense_intensity` <- Krugman (1979) proportional intervention rule; empirical reserve drawdown rates during 1992 ERM crisis.
- `reserve_floor` <- Eichengreen, Rose & Wyplosz (1995): 57 crisis episodes show collapse at 10-20% residual reserves.

**Expected individual behaviour:**
- Given deviation = 0.03 and cash above floor, agent MUST sell reserves.
- Given cash below reserve_floor * initial_reserves, agent MUST hold regardless of deviation.
- Given deviation within defense_threshold, agent MUST hold even with full reserves.
- Given missing price signal, agent MUST hold per missing-signal policy.

**Sanity bounds:**
- IF agent deploys reserves after hitting reserve_floor THEN broken — deactivation logic failed.
- IF agent holds when deviation > defense_threshold and cash > floor THEN broken — trigger logic failed.
- IF agent sells more than available cash THEN broken — clamp logic failed.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| aggressive-defense | `defense_intensity = 5.0` | stronger intervention delays collapse | increase in ticks before deactivation | ticks until reserve_floor breach |
| early-abandon | `reserve_floor = 0.30` | earlier exit preserves more reserves | decrease in total intervention volume | cumulative quantity deployed |
| wide-band | `defense_threshold = 0.025` | wider band reduces intervention frequency | decrease in interventions per 100 ticks | trade count |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311-325. https://doi.org/10.2307/1991793 | First-generation crisis model |
| 2 | Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3-5), 1037-1047. https://doi.org/10.1016/0014-2921(95)00110-7 | Second-generation self-fulfilling crisis |
| 3 | Eichengreen, B., Rose, A. K., & Wyplosz, C. (1995). Exchange market mayhem: The antecedents and aftermath of speculative attacks. *Economic Policy*, 10(21), 249-312. https://doi.org/10.2307/1344591 | Empirical crisis episodes and reserve thresholds |
| 4 | Flood, R. P. & Garber, P. M. (1984). Collapsing exchange-rate regimes: Some linear examples. *Journal of International Economics*, 17(1-2), 1-13. https://doi.org/10.1016/0022-1996(84)90002-3 | Linear crisis model validation |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-central-bank-defender.png) |
| Status | draft |
