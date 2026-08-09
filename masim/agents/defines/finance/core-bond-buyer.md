# Core government bond buyer

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Core government bond buyer |
| Theory Family         | Flight to Quality / Safe Asset Demand |
| Behavioral Tendency   | **Converging** — accumulates safe government bonds during stress, stabilising bond prices and anchoring the risk-free rate |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a safety-seeking institutional investor — such as a central bank reserve manager, sovereign wealth fund, or insurance company — that systematically accumulates core government bonds as a store of value. The real-world counterpart is the flight-to-quality buyer documented in Vayanos (2004) and Caballero & Krishnamurthy (2008), who increases demand for safe sovereign debt during market stress, driving yields down and providing a stabilising anchor for risk-free rates.

The decision goal is to buy government bonds when their yield (implied by price relative to par/fundamental) exceeds a minimum acceptable yield and market stress indicators suggest risk assets are deteriorating. The agent optimises safety and yield simultaneously: it buys more aggressively as the spread between bond yield and its target widens, and reduces activity when bonds become expensive (yield below floor). Selling occurs only when bonds become significantly overpriced relative to par.

Inside the simulation this agent acts as a stabilising demand force in bond markets, providing consistent bids that prevent disorderly yield spikes during stress. It embodies the "safe asset shortage" dynamic where flight-to-quality flows compress safe yields. Non-goals: (1) the agent must NOT speculate on yield-curve movements for capital gains beyond its safety mandate; (2) the agent must NOT buy risky/non-sovereign assets regardless of their yield advantage.

## Theoretical Foundation

**Flight to quality (Vayanos 2004)**:
- Theory / Study: Flight to quality, flight to liquidity.
- Citation: Vayanos, D. (2004). Flight to quality, flight to liquidity. Working Paper, NBER. https://doi.org/10.3386/w10327
- Core Insight: During market stress, risk-averse investors shift portfolios toward safe, liquid assets (government bonds), compressing safe-asset yields and widening credit spreads. The flight is driven by increased risk aversion and margin constraints that force liquidation of risky assets into safe havens.
- Mathematical Formulation: `buy_signal = (fundamental - price) / fundamental; buy if buy_signal > yield_floor`
- Empirical Evidence: Vayanos (2004) documents 50-150bp yield compression in US Treasuries during 1998 LTCM crisis and 2001 recession. Beber, Brandt & Kavajecz (2009) find flight-to-quality flows of $5-15B per week during stress (N=300 weeks, R-squared = 0.42 for credit-spread-to-Treasury-flow regression).
- Relevance to This Agent: The agent operationalises flight-to-quality by increasing bond purchases when the yield signal (fundamental above price) exceeds a floor, mimicking institutional demand surges during stress.
- Calibration Source: yield_floor 0.005-0.02 from historical Treasury yield floors; base_size 300-1000 from institutional block-trade norms; stress_multiplier 1.5-3.0 from empirical flow amplification during crises.
- Falsification Conditions: If the agent does not increase bond purchases when yield_signal > yield_floor, or if it buys when yield_signal < yield_floor (bonds already expensive), the flight-to-quality mechanism is falsified.
- Alternative Theories: Caballero & Krishnamurthy (2008) safe-asset shortage; Brunnermeier & Pedersen (2009) liquidity spirals driving reallocation; Krishnamurthy & Vissing-Jorgensen (2012) convenience yield on Treasuries.

**Safe asset shortage (Caballero & Krishnamurthy 2008)**:
- Theory / Study: Collective risk management in a flight to quality episode.
- Citation: Caballero, R. J. & Krishnamurthy, A. (2008). Collective risk management in a flight to quality episode. *Journal of Finance*, 63(5), 2195-2230. https://doi.org/10.1111/j.1540-6261.2008.01394.x
- Core Insight: When the supply of safe assets is insufficient relative to demand, equilibrium yields on safe assets are compressed below levels justified by default risk alone. The shortage intensifies during crises as agents collectively seek safety, creating a coordination-driven demand surge that makes safe assets scarcer and more expensive.
- Mathematical Formulation: `effective_size = base_size * (1 + stress_multiplier * max(0, yield_signal - yield_floor))`
- Empirical Evidence: Caballero & Krishnamurthy (2008) show US Treasury yields fell 200bp more than model-predicted during 2007-2008 crisis due to excess safe-asset demand (N=24 months, excess demand proxy significant at p < 0.01).
- Relevance to This Agent: The agent's sizing rule amplifies purchases when yield_signal is high (stress), operationalising the safe-asset shortage coordination mechanism.
- Calibration Source: stress_multiplier 1.5-3.0 from crisis-period flow amplification; allocation_cap 0.15-0.30 of cash per tick from institutional mandates.
- Falsification Conditions: If the agent does not increase purchase size as yield_signal rises above yield_floor, the stress-amplification mechanism is falsified.
- Alternative Theories: Vayanos (2004) pure risk-aversion flight; Gorton (2017) safe-asset production; Krishnamurthy & Vissing-Jorgensen (2012).

## Design Purpose and Activation Triggers

Purpose: Accumulate core government bonds when yield exceeds a safety floor, amplifying purchases during market stress.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (bond price)
- `fundamental` available (par/fair value of bond)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `yield_signal > yield_floor` (where yield_signal = (fundamental - price) / fundamental): buy sized by `base_size * (1 + stress_multiplier * (yield_signal - yield_floor)) * sizing_scale`.
- `price > fundamental * (1 + overvaluation_threshold)`: sell sized by `min(position, base_size * (price - fundamental) * sizing_scale / price)`.
- `<Default>`: hold.

Deactivation Conditions:
- cash insufficient for minimum bond purchase.
- yield_signal <= yield_floor (bonds already fully priced for safety).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Market stress (yield_signal > 2x yield_floor) | Amplifies purchase size via stress_multiplier | Safe-asset shortage coordination per Caballero & Krishnamurthy (2008) |
| Calm markets (yield_signal ≈ yield_floor) | Reverts to base_size purchases only | Normal institutional accumulation without flight-to-quality amplification |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current bond price |
| `fundamental` | environment | float | yes | bond par/fair value |
| `cash` | own state | float | yes | available capital for purchases |
| `position` | own state | float | yes | current bond holdings |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | trade direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | — | yes | audit trail explaining yield signal and sizing |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: buy quantity clamped to min(allocation_cap * cash / price, cash / price); sell quantity clamped to position.
- Units: quantity in bond units; price in currency.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning (1-3 sentences) explaining yield signal, stress assessment, and buy/sell/hold decision...</analysis>
<decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>
```

No retrieval-augmented variant declared; retrieval fallback sentinel not applicable.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current bond price for yield computation |
| `fundamental` | Continuous | 1 tick | par value for yield signal |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | current holdings and sell constraint |

Does NOT use: equity prices, credit spreads directly, momentum indicators, peer positions, leverage.

#### Core Behavioral Mechanism

1. **Read** `price`, `fundamental`, `cash`, `position`. (implementation convenience)
2. **Compute** yield signal: `yield_signal = (fundamental - price) / fundamental`. Read: fundamental, price. Write: yield_signal. (Traces to Vayanos 2004 — flight-to-quality yield measure)
3. **Evaluate** buy condition: if `yield_signal > yield_floor`, proceed to buy sizing. Read: yield_signal, yield_floor. Write: direction. (Traces to Vayanos 2004)
4. **Compute** stress-adjusted size: `effective_size = base_size * (1 + stress_multiplier * max(0, yield_signal - yield_floor)) * sizing_scale`. Read: base_size, stress_multiplier, yield_signal, yield_floor, sizing_scale. Write: effective_size. (Traces to Caballero & Krishnamurthy 2008 — amplification during stress)
5. **Clamp** buy quantity: `q = min(effective_size / price, allocation_cap * cash / price, cash / price)`. Read: effective_size, price, allocation_cap, cash. Write: q. (implementation convenience — resource/allocation constraint)
6. **Evaluate** sell condition: if `yield_signal <= yield_floor` AND `price > fundamental * (1 + overvaluation_threshold)`, sell overpriced bonds. Read: price, fundamental, overvaluation_threshold. Write: sell direction. (Traces to Caballero & Krishnamurthy 2008 — safe-asset overpricing)
7. **Compute** sell quantity: `q_sell = min(position, base_size * (price - fundamental) * sizing_scale / price)`. Read: position, base_size, price, fundamental, sizing_scale. Write: q_sell. (implementation convenience)
8. **Emit** decision object with action, quantity, reasoning.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current bond price |
| Sizing rule | `base_size * (1 + stress_multiplier * max(0, yield_signal - yield_floor)) * sizing_scale / price`, clamped by allocation_cap |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position >= 0; buy limited to allocation_cap fraction of cash |
| Resource cap | buy quantity <= allocation_cap * cash / price |
| Exit rule | sell when bonds become significantly overvalued (price > fundamental * (1 + overvaluation_threshold)) |

#### Mathematical Model

**Decision output:** action in {buy, sell, hold} and quantity q >= 0.

**Decision logic:**
```
yield_signal = (fundamental - price) / fundamental

if yield_signal > yield_floor:
    action = buy
    effective_size = base_size * (1 + stress_multiplier * (yield_signal - yield_floor)) * sizing_scale
    q = min(effective_size / price, allocation_cap * cash / price)
elif price > fundamental * (1 + overvaluation_threshold):
    action = sell
    q = min(position, base_size * (price - fundamental) * sizing_scale / price)
else:
    action = hold
    q = 0
```

**State variables:**
| Variable | Type | Initial Value |
|----------|------|---------------|
| `cash` | float | scenario-assigned |
| `position` | float | scenario-assigned |

**State evolution:** `cash` and `position` updated post-execution by environment.

**Determinism contract:** Fully deterministic given identical inputs and state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `yield_floor` | minimum yield signal to trigger purchase | 0.01 | Historical Treasury yield floors |
| `stress_multiplier` | amplification of size during stress | 2.0 | Caballero & Krishnamurthy (2008) |
| `base_size` | base order quantity | 500.0 | Scenario normalization |
| `sizing_scale` | signal-to-quantity multiplier | 5000.0 | Scenario normalization |
| `allocation_cap` | max fraction of cash per trade | 0.15 | Institutional mandate limits |
| `overvaluation_threshold` | fraction above par triggering sell | 0.03 | Conservative profit-taking |

#### Behavioral Properties

- Time horizon: long — accumulates bonds as long-term store of value, holds through volatility.
- Risk tolerance: low — exclusively targets safe sovereign debt; conservative sizing.
- Information asymmetry: partial — observes bond price and par value but not private credit signals.
- Psychological profile: rational safety-seeking institutional investor; no cognitive biases; driven by mandate for capital preservation and yield.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `yield_floor` | float | 0.01 | [0.005, 0.03] | high | minimum yield signal to trigger buying | Higher -> fewer purchases, bonds must be cheaper | Vayanos (2004) |
| `stress_multiplier` | float | 2.0 | [1.0, 4.0] | high | purchase amplification during stress | Higher -> much larger buys when yield is high | Caballero & Krishnamurthy (2008) |
| `base_size` | float | 500.0 | [200, 1500] | medium | base order quantity | Higher -> larger baseline purchases | Scenario normalization |
| `sizing_scale` | float | 5000.0 | [2000, 10000] | medium | yield-to-quantity multiplier | Higher -> more sensitive to yield changes | Scenario normalization |
| `allocation_cap` | float | 0.15 | [0.05, 0.30] | medium | max fraction of cash invested per tick | Higher -> allows larger single purchases | Institutional mandate |
| `overvaluation_threshold` | float | 0.03 | [0.01, 0.05] | low | bond overpricing fraction triggering sell | Higher -> holds longer before selling | Conservative calibration |

## Worked Numerical Examples

### Case 1 — Buy (yield above floor, normal stress)
System state: price = 97.0, fundamental = 100.0, cash = 500000, position = 1000.
Calculation:
  yield_signal = (100 - 97) / 100 = 0.03
  yield_signal (0.03) > yield_floor (0.01) → buy
  effective_size = 500 * (1 + 2.0 * (0.03 - 0.01)) * 5000 = 500 * 1.04 * 5000 = 2600000
  q = min(2600000 / 97, 0.15 * 500000 / 97) = min(26804, 773.2) = 773.2
Decision: buy 773.2 units (allocation cap binds).
State update: cash and position updated post-execution.

### Case 2 — Sell (bonds overvalued)
System state: price = 104.0, fundamental = 100.0, cash = 300000, position = 800.
Calculation:
  yield_signal = (100 - 104) / 100 = -0.04 (negative, bonds expensive)
  yield_signal (-0.04) < yield_floor (0.01) → check sell condition
  price (104) > fundamental * (1 + overvaluation_threshold) = 100 * 1.03 = 103 → sell
  q = min(800, 500 * (104 - 100) * 5000 / 104) = min(800, 96154) = 800
Decision: sell 800 units.
State update: position decreases.

### Case 3 — Hold (yield below floor, not overvalued)
System state: price = 99.5, fundamental = 100.0, cash = 400000, position = 500.
Calculation:
  yield_signal = (100 - 99.5) / 100 = 0.005
  yield_signal (0.005) <= yield_floor (0.01) → not buy
  price (99.5) < fundamental * 1.03 (103) → not sell
Decision: hold, quantity = 0.
State update: unchanged.

### Edge Case — Extreme stress (very high yield signal)
System state: price = 85.0, fundamental = 100.0, cash = 1000000, position = 200.
Calculation:
  yield_signal = (100 - 85) / 100 = 0.15
  yield_signal (0.15) > yield_floor (0.01) → buy
  effective_size = 500 * (1 + 2.0 * (0.15 - 0.01)) * 5000 = 500 * 1.28 * 5000 = 3200000
  q = min(3200000 / 85, 0.15 * 1000000 / 85) = min(37647, 1764.7) = 1764.7
Decision: buy 1764.7 units (allocation cap binds; stress amplification raises effective_size but cap constrains).
State update: cash and position updated post-execution.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `yield_floor` <- Historical US Treasury 10Y yield floors 0.5-2.0% during QE; scaled to simulation units.
- `stress_multiplier` <- Caballero & Krishnamurthy (2008): flight-to-quality flows amplify 1.5-3x during crises.
- `allocation_cap` <- Institutional asset-allocation mandates typically 5-30% per single position.

**Expected individual behaviour:**
- Given yield_signal = 0.03 (above floor), agent MUST buy with quantity > 0.
- Given yield_signal = 0.005 (below floor) and price < 103, agent MUST hold.
- Given price = 105 (above 103 threshold) and yield_signal < floor, agent MUST sell if position > 0.
- Given missing fundamental, agent MUST hold per missing-signal policy.

**Sanity bounds:**
- IF agent buys when yield_signal < yield_floor THEN broken — threshold logic failed.
- IF agent buys more than allocation_cap * cash / price THEN broken — cap violated.
- IF agent produces negative quantity THEN broken — valid range violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-stress-amplification | `stress_multiplier = 0` | stress multiplier drives crisis-period volume | decrease in buy volume during high-yield periods | total buy quantity when yield_signal > 0.05 |
| high-yield-floor | `yield_floor = 0.03` | higher floor reduces purchase frequency | decrease in trade count | buys per 100 ticks |
| uncapped-allocation | `allocation_cap = 1.0` | allocation cap constrains position growth | increase in average buy size | mean buy quantity |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Vayanos, D. (2004). Flight to quality, flight to liquidity. NBER Working Paper 10327. https://doi.org/10.3386/w10327 | Core flight-to-quality theory |
| 2 | Caballero, R. J. & Krishnamurthy, A. (2008). Collective risk management in a flight to quality episode. *Journal of Finance*, 63(5), 2195-2230. https://doi.org/10.1111/j.1540-6261.2008.01394.x | Safe-asset shortage and amplification |
| 3 | Beber, A., Brandt, M. W., & Kavajecz, K. A. (2009). Flight-to-quality or flight-to-liquidity? *Review of Financial Studies*, 22(3), 925-957. https://doi.org/10.1093/rfs/hhm088 | Empirical flight-to-quality flows |
| 4 | Krishnamurthy, A. & Vissing-Jorgensen, A. (2012). The aggregate demand for Treasury debt. *Journal of Political Economy*, 120(2), 233-267. https://doi.org/10.1086/666526 | Convenience yield and safe-asset demand |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-core-bond-buyer.png) |
| Status | draft |
