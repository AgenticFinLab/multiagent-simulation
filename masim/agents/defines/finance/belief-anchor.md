# Belief-anchoring conservative updater

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Belief-anchoring conservative updater |
| Theory Family         | Behavioral Bias / Bayesian Underweighting |
| Behavioral Tendency   | **Converging** — slowly adjusts belief toward new information, anchoring to prior and dampening price swings |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models an institutional investor or pension fund portfolio manager who anchors beliefs to a prior distribution and updates slowly in response to new information. The real-world counterpart is the conservative institutional allocator documented in Edwards (1968) and Barberis, Shleifer, and Vishny (1998) — participants who underweight new evidence relative to Bayesian optimality, leading to under-reaction in price discovery.

The decision goal is to produce buy, sell, or hold actions based on a slowly-updated belief about fair value. The agent maintains an internal belief estimate that moves toward the fundamental signal at a rate governed by an update weight (alpha), which is deliberately set below Bayesian-optimal to capture conservatism bias. Trade direction and size are determined by deviation between current price and the agent's anchored belief.

Inside the simulation the agent acts as a stabilising force that dampens overreaction to news by absorbing short-term mispricings slowly. Its sluggish updating means it under-reacts to regime changes but provides inertia against noise-driven volatility. Non-goals: (1) the agent must NOT update beliefs instantaneously to new fundamental signals (that would violate conservatism); (2) the agent must NOT engage in momentum-chasing behaviour by extrapolating price trends.

## Theoretical Foundation

**Conservatism bias (Edwards 1968)**:
- Theory / Study: Conservatism in human information processing.
- Citation: Edwards, W. (1968). Conservatism in human information processing. In B. Kleinmuntz (Ed.), *Formal Representation of Human Judgment*, 17-52. Wiley. https://doi.org/10.1017/CBO9780511809477.026
- Core Insight: When presented with new diagnostic evidence, humans update their posterior beliefs by a factor of 2-5x less than Bayes' theorem prescribes. This conservatism causes under-reaction to news and generates predictable return patterns as beliefs slowly catch up to reality.
- Mathematical Formulation: `belief_new = (1 - alpha) * belief_old + alpha * fundamental` where `alpha < alpha_bayes`
- Empirical Evidence: Edwards (1968) showed subjects updated posterior probabilities at 50-75% of the Bayesian rate across multiple experiments (N=40, p < 0.01). Phillips & Edwards (1966) replicate with alpha_effective / alpha_bayes ratios of 0.3-0.7.
- Relevance to This Agent: The agent operationalises conservatism by setting `alpha = 0.1`, far below the Bayesian-optimal rate, making belief updates sluggish and anchored to prior estimates.
- Calibration Source: alpha in [0.05, 0.30] based on Edwards (1968) finding of 30-70% Bayesian efficiency; belief_threshold 0.01-0.05 from typical transaction cost bands.
- Falsification Conditions: If the agent's belief converges to the true fundamental within 5 ticks of a signal change (faster than alpha = 0.30 would allow), the conservatism mechanism is falsified.
- Alternative Theories: Rational inattention (Sims 2003); Bayesian learning with correct priors; anchoring-and-adjustment (Tversky & Kahneman 1974).

## Design Purpose and Activation Triggers

Purpose: Maintain an anchored belief about fair value and trade slowly toward it, embodying conservatism bias in information processing.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `fundamental` available
- own `cash` and `position` available

Missing-Signal Policy: hold and do not update belief when fundamental signal is unavailable; retain last belief value.

Activation Triggers:
- `price < belief - belief_threshold`: buy sized by `base_size * (belief - price) * sizing_scale / price`.
- `price > belief + belief_threshold`: sell sized by `min(position, base_size * (price - belief) * sizing_scale / price)`.
- `<Default>`: hold.

Deactivation Conditions:
- cash insufficient for minimum buy order.
- position is zero and price > belief (no short selling).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Large fundamental jump (> 3x belief_threshold in one tick) | Caps belief update to max_step to prevent over-reaction | Anchoring cap on single-step belief revision |
| Prolonged signal agreement (fundamental stable for > 10 ticks) | Belief converges closer to fundamental as residual shrinks | Exponential decay of prior anchor weight over time |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `fundamental` | environment | float | yes | new information signal for belief update |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell constraint |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | trade direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | — | yes | audit trail explaining belief update and gap |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: quantity clamped to `[0, cash/price]` for buys and `[0, position]` for sells.
- Units: quantity in asset units; price and belief in same currency units.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning (1-3 sentences) showing belief update and price-belief gap evaluation...</analysis>
<decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>
```

No retrieval-augmented variant declared; retrieval fallback sentinel not applicable.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current market price for gap computation |
| `fundamental` | Continuous | 1 tick | new information for belief updating |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell constraint |
| `belief` | State | persistent | anchored internal fair-value estimate |

Does NOT use: technical momentum indicators, peer positions, order-book data, sentiment feeds.

#### Core Behavioral Mechanism

1. **Read** `price`, `fundamental`, `cash`, `position`, `belief`. (implementation convenience)
2. **Compute** belief update: `belief_new = (1 - alpha) * belief + alpha * fundamental`. Read: belief, alpha, fundamental. Write: belief_candidate. (Traces to Conservatism bias — Edwards 1968)
3. **Clamp** belief step: if `abs(belief_candidate - belief) > max_step`, set `belief_new = belief + sign(belief_candidate - belief) * max_step`. Read: belief_candidate, belief, max_step. Write: belief_new. (Traces to Conservatism bias — anchoring cap)
4. **Update** internal belief state: `belief = belief_new`. Write: belief.
5. **Compute** gap: `gap = belief - price`. Read: belief, price. Write: gap. (Traces to Conservatism bias — deviation from anchored estimate)
6. **Evaluate** threshold: if `abs(gap) <= belief_threshold * price`, hold. Read: gap, belief_threshold, price. Write: decision direction. (implementation convenience — transaction cost filter)
7. **Compute** quantity: if buy, `q = min(base_size * gap * sizing_scale / price, cash / price)`; if sell, `q = min(base_size * abs(gap) * sizing_scale / price, position)`. Read: base_size, gap, sizing_scale, price, cash, position. Write: q. (Traces to Conservatism bias — position proportional to anchored belief gap)
8. **Emit** decision object with action, quantity, reasoning.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `base_size * abs(gap) * sizing_scale / price`, clamped by resource constraints |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position >= 0 (no short selling) |
| Resource cap | buy quantity <= cash / price |
| Exit rule | none — agent continuously evaluates price-belief gap |

#### Mathematical Model

**Decision output:** action in {buy, sell, hold} and quantity q >= 0.

**Decision logic:**
```
belief_candidate = (1 - alpha) * belief + alpha * fundamental
if abs(belief_candidate - belief) > max_step:
    belief = belief + sign(belief_candidate - belief) * max_step
else:
    belief = belief_candidate

gap = belief - price

if gap > belief_threshold * price:
    action = buy
    q = min(base_size * gap * sizing_scale / price, cash / price)
elif gap < -belief_threshold * price:
    action = sell
    q = min(base_size * abs(gap) * sizing_scale / price, position)
else:
    action = hold
    q = 0
```

**State variables:**
| Variable | Type | Initial Value |
|----------|------|---------------|
| `belief` | float | fundamental at first tick |
| `cash` | float | scenario-assigned |
| `position` | float | scenario-assigned |

**State evolution:** `belief` updated pre-decision (steps 2-4). `cash` and `position` updated post-execution by environment.

**Determinism contract:** Fully deterministic given identical inputs and state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `alpha` | belief update weight | 0.1 | Edwards (1968), 30-70% Bayesian efficiency |
| `belief_threshold` | minimum price-belief gap ratio to trade | 0.02 | Transaction cost band calibration |
| `base_size` | base order quantity | 400.0 | Scenario normalization |
| `sizing_scale` | gap-to-quantity multiplier | 5000.0 | Scenario normalization |
| `max_step` | maximum single-tick belief revision | 2.0 | Anchoring cap from Edwards (1968) |

#### Behavioral Properties

- Time horizon: long — belief updates slowly, implying multi-period convergence to true value.
- Risk tolerance: low — small alpha and threshold filtering produce conservative, small trades.
- Information asymmetry: partial — observes fundamental signal but underweights it.
- Psychological profile: embodiment of conservatism bias (Edwards 1968); anchoring to prior beliefs; systematic under-reaction to new information.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `alpha` | float | 0.1 | [0.05, 0.30] | high | belief update rate per tick | Higher -> faster convergence to fundamental, less conservatism | Edwards (1968) |
| `belief_threshold` | float | 0.02 | [0.005, 0.05] | high | minimum gap/price ratio to trigger trade | Higher -> fewer trades, requires larger mispricing | Transaction cost calibration |
| `base_size` | float | 400.0 | [100, 1000] | medium | base order quantity | Higher -> larger individual trades | Scenario normalization |
| `sizing_scale` | float | 5000.0 | [2000, 10000] | medium | gap-to-quantity multiplier | Higher -> more aggressive response to belief-price gap | Scenario normalization |
| `max_step` | float | 2.0 | [0.5, 5.0] | medium | maximum single-tick belief change (absolute) | Higher -> allows larger belief jumps, less anchoring | Edwards (1968) anchoring literature |

## Worked Numerical Examples

### Case 1 — Buy (price below anchored belief)
System state: price = 98.0, fundamental = 105.0, belief = 100.0, cash = 50000, position = 200.
Calculation:
  belief_candidate = (1 - 0.1) * 100.0 + 0.1 * 105.0 = 90.0 + 10.5 = 100.5
  abs(100.5 - 100.0) = 0.5 <= max_step (2.0), so belief = 100.5
  gap = 100.5 - 98.0 = 2.5
  gap (2.5) > belief_threshold * price (0.02 * 98 = 1.96) → buy
  raw_q = 400 * 2.5 * 5000 / 98.0 = 51020.4 → clamped: min(51020.4, 50000/98) = min(51020.4, 510.2) = 510.2
Decision: buy 510.2 units.
State update: belief = 100.5.

### Case 2 — Sell (price above anchored belief)
System state: price = 104.0, fundamental = 99.0, belief = 100.0, cash = 30000, position = 600.
Calculation:
  belief_candidate = 0.9 * 100.0 + 0.1 * 99.0 = 90.0 + 9.9 = 99.9
  abs(99.9 - 100.0) = 0.1 <= max_step (2.0), so belief = 99.9
  gap = 99.9 - 104.0 = -4.1
  abs(gap) (4.1) > belief_threshold * price (0.02 * 104 = 2.08) → sell
  raw_q = 400 * 4.1 * 5000 / 104.0 = 78846.2 → clamped: min(78846.2, 600) = 600
Decision: sell 600 units.
State update: belief = 99.9.

### Case 3 — Hold (gap below threshold)
System state: price = 100.0, fundamental = 101.0, belief = 100.0, cash = 40000, position = 300.
Calculation:
  belief_candidate = 0.9 * 100.0 + 0.1 * 101.0 = 90.0 + 10.1 = 100.1
  abs(100.1 - 100.0) = 0.1 <= max_step, so belief = 100.1
  gap = 100.1 - 100.0 = 0.1
  abs(gap) (0.1) < belief_threshold * price (0.02 * 100 = 2.0) → hold
Decision: hold, quantity = 0.
State update: belief = 100.1.

### Edge Case — Large fundamental jump (max_step clamp)
System state: price = 100.0, fundamental = 150.0, belief = 100.0, cash = 50000, position = 300.
Calculation:
  belief_candidate = 0.9 * 100.0 + 0.1 * 150.0 = 90.0 + 15.0 = 105.0
  abs(105.0 - 100.0) = 5.0 > max_step (2.0), so belief = 100.0 + 2.0 = 102.0
  gap = 102.0 - 100.0 = 2.0
  abs(gap) (2.0) = belief_threshold * price (0.02 * 100 = 2.0) → hold (not strictly greater)
Decision: hold, quantity = 0.
State update: belief = 102.0 (clamped from 105.0).

## Behavioral Verification and Calibration

**Calibration data sources:**
- `alpha` <- Edwards (1968): humans update at 30-70% Bayesian rate; alpha = 0.1 represents ~33% efficiency for a base rate of 0.3.
- `belief_threshold` <- typical equity transaction cost band 1-5% (Chordia et al. 2001).
- `max_step` <- anchoring literature: single-period revision cap prevents sudden belief jumps inconsistent with conservatism.

**Expected individual behaviour:**
- Given a step change in fundamental from 100 to 110, belief should reach 105 only after ~7 ticks (not immediately).
- Given price well below belief (gap > threshold), agent MUST buy.
- Given missing fundamental signal, agent MUST hold and retain prior belief.
- Given fundamental stable at belief level, agent MUST hold (gap ≈ 0).

**Sanity bounds:**
- IF agent's belief jumps more than max_step in a single tick THEN broken — clamping logic failed.
- IF agent trades when abs(gap) < belief_threshold * price THEN broken — threshold logic violated.
- IF agent produces negative quantity THEN broken — valid range violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| fast-update | `alpha = 0.5` | conservatism dampens overreaction | increase in trade frequency and belief volatility | belief variance per 50 ticks |
| no-anchoring-cap | `max_step = 100.0` | anchoring cap prevents belief jumps | increase in single-tick belief changes | max single-tick belief delta |
| tight-threshold | `belief_threshold = 0.005` | threshold filters noise trades | increase in trade count | trades per 100 ticks |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Edwards, W. (1968). Conservatism in human information processing. In B. Kleinmuntz (Ed.), *Formal Representation of Human Judgment*, 17-52. https://doi.org/10.1017/CBO9780511809477.026 | Core theory — conservatism bias |
| 2 | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Under-reaction model integrating conservatism |
| 3 | Tversky, A. & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124-1131. https://doi.org/10.1126/science.185.4157.1124 | Anchoring heuristic foundation |
| 4 | Chordia, T., Roll, R., & Subrahmanyam, A. (2001). Market liquidity and trading activity. *Journal of Finance*, 56(2), 501-530. https://doi.org/10.1111/0022-1082.00335 | Transaction cost band calibration |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-belief-anchor.png) |
| Status | draft |
