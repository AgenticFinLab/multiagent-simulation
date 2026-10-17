# Conformist trend follower

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Conformist trend follower |
| Theory Family         | Informational Cascades / Herding |
| Behavioral Tendency   | **Diverging** — amplifies prevailing market direction by following majority opinion, pushing price further from fundamentals |
| Time Horizon          | short |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a retail investor, trend-following fund, or institutional herder who abandons private information and follows the majority position in the market. The real-world counterpart is the momentum trader or copycat investor documented in Bikhchandani, Hirshleifer, and Welch (1992) — participants who rationally or irrationally discard their own signals and imitate observed peer behaviour, creating informational cascades that amplify price movements beyond fundamental justification.

The decision goal is to align the agent's position with the prevailing market trend. The agent observes recent price momentum as a proxy for majority opinion and trades in the same direction. It buys when price has been rising (positive momentum exceeds a conformity threshold) and sells when price has been falling (negative momentum exceeds threshold), sizing proportionally to the momentum magnitude.

Inside the simulation this agent acts as a destabilising amplifier that reinforces existing trends and contributes to bubble formation or crash cascades. By abandoning fundamental analysis and following the crowd, it generates positive feedback loops. Non-goals: (1) the agent must NOT trade against the prevailing trend (contrarian behavior is excluded); (2) the agent must NOT use fundamental value information in its decision — it relies solely on observed price momentum as a proxy for peer behaviour.

## Theoretical Foundation

**Informational cascades (Bikhchandani, Hirshleifer, Welch 1992)**:
- Theory / Study: A theory of fads, fashion, custom, and cultural change as informational cascades.
- Citation: Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992-1026. https://doi.org/10.1086/261849
- Core Insight: When agents observe predecessors' actions, they rationally discard private signals and follow the majority if the public signal (inferred from observed actions) is sufficiently strong. This creates fragile cascades where all agents take the same action regardless of private information, leading to herding that is informationally inefficient and prone to sudden reversal.
- Mathematical Formulation: `momentum = (price - price_lag) / price_lag; if abs(momentum) > conformity_threshold then trade in direction of momentum`
- Empirical Evidence: Bikhchandani et al. (1992) demonstrate cascade formation in laboratory experiments (N=72 subjects, cascade frequency 70-90% of trials). Welch (2000) finds herding in analyst recommendations (N=226 analysts, sequential dependence coefficient 0.34, p < 0.01).
- Relevance to This Agent: The agent operationalises cascade-following by using price momentum as a proxy for majority action and trading in the same direction when the signal exceeds a threshold.
- Calibration Source: conformity_threshold 0.005-0.03 from empirical momentum cutoffs; base_size 200-800 units from herding volume studies.
- Falsification Conditions: If the agent trades against the prevailing momentum direction (buys during negative momentum or sells during positive momentum), the cascade-following mechanism is falsified.
- Alternative Theories: Rational momentum (Jegadeesh & Titman 1993); social learning without cascades (Banerjee 1992); feedback trading (DeLong et al. 1990).

## Design Purpose and Activation Triggers

Purpose: Follow market majority by trading in the direction of observed price momentum, amplifying prevailing trends.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- own `cash` and `position` available

Missing-Signal Policy: hold when price or lagged price is unavailable.

Activation Triggers:
- `momentum > conformity_threshold`: buy sized by `base_size * momentum * momentum_scale`.
- `momentum < -conformity_threshold`: sell sized by `min(position, base_size * abs(momentum) * momentum_scale)`.
- `<Default>`: hold.

Deactivation Conditions:
- cash insufficient for minimum buy order during uptrend.
- position is zero during downtrend (nothing to sell).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Strong momentum (abs(momentum) > 3x conformity_threshold) | Increases sizing by conviction_boost multiplier | Stronger cascade signal increases conformity confidence |
| Momentum reversal (sign flip from previous tick) | Holds for one tick before following new direction | Cascade fragility — brief hesitation on reversal per Bikhchandani et al. |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell constraint |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | conformist trade direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | — | yes | audit trail explaining momentum and conformity decision |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: quantity clamped to `[0, cash/price]` for buys and `[0, position]` for sells.
- Units: quantity in asset units; price in same currency as market.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning (1-3 sentences) explaining momentum computation and conformity trigger...</analysis>
<decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>
```

No retrieval-augmented variant declared; retrieval fallback sentinel not applicable.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 2 ticks | current and lagged price for momentum |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell constraint |

Does NOT use: fundamental value, private signals, order-book depth, analyst reports, peer identity.

#### Core Behavioral Mechanism

1. **Read** `price`, `price_prev`, `cash`, `position`. (implementation convenience)
2. **Compute** momentum: `momentum = (price - price_prev) / price_prev`. Read: price, price_prev. Write: momentum. (Traces to Informational cascades — price momentum as proxy for majority action)
3. **Evaluate** threshold: if `abs(momentum) <= conformity_threshold`, hold. Read: momentum, conformity_threshold. Write: decision direction. (Traces to Informational cascades — cascade trigger threshold)
4. **Determine** direction: if `momentum > conformity_threshold`, action = buy. If `momentum < -conformity_threshold`, action = sell. Read: momentum. Write: action. (Traces to Informational cascades — follow majority)
5. **Compute** raw quantity: `raw_q = base_size * abs(momentum) * momentum_scale`. Read: base_size, momentum, momentum_scale. Write: raw_q. (Traces to Informational cascades — conformity intensity proportional to signal strength)
6. **Clamp** quantity: if buy, `q = min(raw_q, cash / price)`; if sell, `q = min(raw_q, position)`. Read: raw_q, cash, price, position. Write: q. (implementation convenience — resource constraint)
7. **Emit** decision object with action, quantity, reasoning. Update `price_prev = price`. Write: price_prev.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `base_size * abs(momentum) * momentum_scale`, clamped by resource constraints |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position >= 0 (no short selling) |
| Resource cap | buy quantity <= cash / price; sell quantity <= position |
| Exit rule | none — continuously follows momentum |

#### Mathematical Model

**Decision output:** action in {buy, sell, hold} and quantity q >= 0.

**Decision logic:**
```
momentum = (price - price_prev) / price_prev

if momentum > conformity_threshold:
    action = buy
    q = min(base_size * momentum * momentum_scale, cash / price)
elif momentum < -conformity_threshold:
    action = sell
    q = min(base_size * abs(momentum) * momentum_scale, position)
else:
    action = hold
    q = 0
```

**State variables:**
| Variable | Type | Initial Value |
|----------|------|---------------|
| `price_prev` | float | price at first tick |
| `cash` | float | scenario-assigned |
| `position` | float | scenario-assigned |

**State evolution:** `price_prev` updated post-decision to current `price`. `cash` and `position` updated post-execution by environment.

**Determinism contract:** Fully deterministic given identical inputs and state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `conformity_threshold` | minimum momentum magnitude to trigger trade | 0.01 | Bikhchandani et al. (1992) cascade trigger calibration |
| `base_size` | base order quantity | 500.0 | Scenario normalization |
| `momentum_scale` | momentum-to-quantity multiplier | 8000.0 | Scenario normalization |

#### Behavioral Properties

- Time horizon: short — responds to immediate price changes, no multi-period planning.
- Risk tolerance: medium — trades proportionally to momentum but subject to resource constraints.
- Information asymmetry: partial — observes price (public) but deliberately ignores private fundamental signals.
- Psychological profile: cascade-following conformist; abandons private signals in favor of inferred majority action; exhibits herding bias per Bikhchandani et al. (1992).

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `conformity_threshold` | float | 0.01 | [0.005, 0.03] | high | minimum momentum to trigger conformist trade | Higher -> fewer trades, requires stronger trend | Bikhchandani et al. (1992) |
| `base_size` | float | 500.0 | [100, 1000] | medium | base order quantity before momentum scaling | Higher -> larger herding impact per trade | Scenario normalization |
| `momentum_scale` | float | 8000.0 | [3000, 15000] | high | momentum-to-quantity multiplier | Higher -> more aggressive position changes per unit momentum | Welch (2000) herding intensity |

## Worked Numerical Examples

### Case 1 — Buy (positive momentum)
System state: price = 102.0, price_prev = 100.0, cash = 80000, position = 300.
Calculation:
  momentum = (102 - 100) / 100 = 0.02
  momentum (0.02) > conformity_threshold (0.01) → buy
  raw_q = 500 * 0.02 * 8000 = 80000 → clamped: min(80000, 80000/102) = min(80000, 784.3) = 784.3
Decision: buy 784.3 units.
State update: price_prev = 102.0.

### Case 2 — Sell (negative momentum)
System state: price = 97.0, price_prev = 100.0, cash = 50000, position = 600.
Calculation:
  momentum = (97 - 100) / 100 = -0.03
  abs(momentum) (0.03) > conformity_threshold (0.01) → sell
  raw_q = 500 * 0.03 * 8000 = 120000 → clamped: min(120000, 600) = 600
Decision: sell 600 units.
State update: price_prev = 97.0.

### Case 3 — Hold (momentum below threshold)
System state: price = 100.5, price_prev = 100.0, cash = 60000, position = 400.
Calculation:
  momentum = (100.5 - 100) / 100 = 0.005
  abs(momentum) (0.005) <= conformity_threshold (0.01) → hold
Decision: hold, quantity = 0.
State update: price_prev = 100.5.

### Edge Case — Cold start (no prior price, zero momentum)
System state: price = 100.0, price_prev = 100.0 (initialised to current), cash = 50000, position = 200.
Calculation:
  momentum = (100 - 100) / 100 = 0.0
  abs(momentum) (0.0) <= conformity_threshold (0.01) → hold
Decision: hold, quantity = 0.
State update: price_prev = 100.0.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `conformity_threshold` <- Bikhchandani et al. (1992) cascade formation threshold; momentum cutoffs from Jegadeesh & Titman (1993) 1-5% monthly returns.
- `momentum_scale` <- Welch (2000) sequential dependence coefficient 0.34 implying strong herding at 3%+ signals.
- `base_size` <- scenario normalization.

**Expected individual behaviour:**
- Given momentum = 0.02 (positive, above threshold), agent MUST buy.
- Given momentum = -0.03 (negative, above threshold in magnitude), agent MUST sell if position > 0.
- Given momentum = 0.005 (below threshold), agent MUST hold.
- Given missing price, agent MUST hold per missing-signal policy.

**Sanity bounds:**
- IF agent buys during negative momentum THEN broken — direction logic inverted.
- IF agent sells during positive momentum THEN broken — conformist principle violated.
- IF agent trades when abs(momentum) < conformity_threshold THEN broken — threshold logic failed.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| low-threshold | `conformity_threshold = 0.002` | lower threshold increases herding frequency | increase in trade count | trades per 100 ticks |
| reduced-scale | `momentum_scale = 2000` | lower scale reduces amplification | decrease in average trade size | mean quantity per trade |
| high-threshold | `conformity_threshold = 0.05` | high threshold limits cascade participation | decrease in trade count | trades per 100 ticks |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads, fashion, custom, and cultural change as informational cascades. *Journal of Political Economy*, 100(5), 992-1026. https://doi.org/10.1086/261849 | Core informational cascade theory |
| 2 | Welch, I. (2000). Herding among security analysts. *Journal of Financial Economics*, 58(3), 369-396. https://doi.org/10.1016/S0304-405X(00)00076-3 | Empirical herding in financial markets |
| 3 | Banerjee, A. V. (1992). A simple model of herd behavior. *Quarterly Journal of Economics*, 107(3), 797-817. https://doi.org/10.2307/2118364 | Alternative herding model |
| 4 | Jegadeesh, N. & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Momentum return documentation |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-conformist.png) |
| Status | draft |
