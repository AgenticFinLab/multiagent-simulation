# ECB intervenor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | European Central Bank sovereign debt intervener |
| Theory Family         | Central Bank Intervention / Lender of Last Resort |
| Behavioral Tendency   | **Stabilising** - intervenes to suppress sovereign spreads and restore orderly market conditions |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | full |
| Determinism           | deterministic |

## Definition and Goals

This agent models the European Central Bank acting in sovereign debt markets through outright purchases (OMT/QE-style interventions) to compress spreads and prevent self-fulfilling debt crises. The real-world counterpart is the ECB's Securities Markets Programme, Outright Monetary Transactions framework, and Public Sector Purchase Programme documented by De Grauwe (2012) and Krishnamurthy et al. (2018). The agent emits buy or hold orders with quantity tied to spread deviation and intervention capacity.

The decision goal is to act as a credible backstop that prevents sovereign spreads from exceeding a threshold that would trigger a self-fulfilling liquidity crisis. The agent purchases bonds when spreads widen beyond its intervention threshold and holds otherwise, mimicking the "whatever it takes" commitment. Non-goals: it must not trade for profit maximization, and it must not intervene in equities or corporate credit markets.

The agent is designed for scenarios exploring multiple equilibria in sovereign debt markets, where the mere credibility of intervention can prevent bad equilibria from materializing.

## Theoretical Foundation

**Self-fulfilling debt crises and central bank backstop**:
- Theory / Study: The governance of a fragile Eurozone.
- Citation: De Grauwe, P. (2012). The governance of a fragile Eurozone. *Australian Economic Review*, 45(3), 255-268. https://doi.org/10.1111/j.1467-8462.2012.00684.x
- Core Insight: In a monetary union without a lender of last resort, sovereign debt markets are subject to self-fulfilling crises where rising spreads cause the very insolvency they price in. A credible central bank backstop eliminates the bad equilibrium.
- Mathematical Formulation: `Q = intervention_size * (spread - spread_threshold) / spread_threshold` when `spread > spread_threshold`.
- Empirical Evidence: De Grauwe shows that Eurozone countries with identical fundamentals faced different spreads depending on ECB commitment credibility.
- Relevance to This Agent: The agent operationalises the threshold-based intervention that collapses the bad equilibrium.
- Calibration Source: `spread_threshold` 200-500 bps, `intervention_size` 5000-50000, `max_holdings` 100000-500000.
- Falsification Conditions: If the agent fails to intervene when spreads exceed threshold and capacity remains, the design is falsified.
- Alternative Theories: Fiscal dominance (Sargent & Wallace 1981); moral hazard of bailouts (Tirole 2012).

**Quantitative easing transmission**:
- Theory / Study: ECB policies involving government bond purchases: Transmission channels and risks.
- Citation: Krishnamurthy, A., Nagel, S., & Vissing-Jorgensen, A. (2018). ECB policies involving government bond purchases: Transmission channels and risks. *Review of Finance*, 22(1), 1-44. https://doi.org/10.1093/rof/rfx053
- Core Insight: Central bank bond purchases reduce yields through portfolio balance, signalling, and default risk channels. Duration extraction compresses term premia.
- Mathematical Formulation: Yield impact proportional to purchase share of outstanding debt.
- Empirical Evidence: Krishnamurthy et al. document 10-50 bps compression per percentage of GDP purchased.
- Relevance to This Agent: Calibrates the agent's purchase impact on spreads.
- Calibration Source: Purchase share of outstanding sovereign debt 10-33%.
- Falsification Conditions: If purchases produce no spread compression in the simulation, calibration is off.
- Alternative Theories: Pure expectations hypothesis; fiscal theory of the price level.

## Design Purpose and Activation Triggers

Purpose: Suppress sovereign spreads by purchasing bonds when spreads exceed the intervention threshold, acting as lender of last resort.

Call Frequency: every-tick.

Prerequisite Signals:
- `spread` available (sovereign yield minus risk-free rate, in bps)
- `price` available (bond price)
- own `capacity` available (remaining intervention budget)

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `spread > spread_threshold`: buy bonds sized by `intervention_size * (spread - spread_threshold) / spread_threshold`, capped by capacity.
- `<Default>`: hold.

Deactivation Conditions:
- intervention capacity exhausted.
- spread falls below threshold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| spread above threshold | buys sovereign bonds proportionally | lender of last resort backstop |
| spread moderately above threshold | smaller proportional purchases | graduated response |
| spread below threshold | holds, preserves capacity | credible but dormant backstop |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `spread` | environment | float (bps) | yes | sovereign spread trigger |
| `price` | environment | float | yes | bond execution price |
| `capacity` | own state | float | yes | remaining intervention budget |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "hold"}` | none | yes | order direction (never sells) |
| `quantity` | float | `>= 0` | units | yes | purchase size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. The ECB intervenor never sells; action is restricted to buy or hold. Quantity must be clamped to remaining capacity.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `spread` | Continuous | 1 tick | intervention trigger |
| `price` | Continuous | 1 tick | execution reference |
| `capacity` | State | persistent | budget constraint |

Does NOT use: private fiscal data, political signals, profit targets.

#### Core Behavioral Mechanism

1. Read `spread`, `price`, and `capacity`.
2. If `spread > spread_threshold`, compute purchase quantity as `min(capacity / price, intervention_size * (spread - spread_threshold) / spread_threshold)`.
3. If `spread <= spread_threshold`, hold.
4. Emit the decision object and reduce capacity after execution.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, hold (never sells) |
| Action parameter rule | market order at current bond price |
| Sizing rule | `intervention_size * (spread - spread_threshold) / spread_threshold`, capped by capacity |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | cumulative holdings cannot exceed max_holdings |
| Resource cap | purchase cannot exceed remaining capacity / price |
| Exit rule | no active exit; holds to maturity |

#### Mathematical Model

`q_buy = min(capacity / price, intervention_size * (spread - theta) / theta)` if `spread > theta`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta` | spread intervention threshold (bps) | 300.0 | De Grauwe (2012) |
| `intervention_size` | base purchase size | 20000.0 | Krishnamurthy et al. (2018), scenario normalization |
| `max_holdings` | maximum cumulative bond holdings | 250000.0 | ECB capital key proportions |
| `capacity` | remaining budget | 250000.0 | initialized to max_holdings |

#### Behavioral Properties

- Time horizon: long, because central bank holds bonds to maturity.
- Risk tolerance: low, because the agent does not seek profit and is constrained by mandate.
- Information asymmetry: full, because the ECB has superior information on policy commitment and fiscal sustainability.
- Psychological profile: institutional mandate-driven, non-profit-seeking stabiliser.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `spread_threshold` | float | 300.0 | [200, 500] | high | spread level (bps) that triggers intervention | Higher -> later intervention, more spread overshoot | De Grauwe (2012) |
| `intervention_size` | float | 20000.0 | [5000, 50000] | high | base purchase quantity per intervention | Higher -> faster spread compression | Krishnamurthy et al. (2018) |
| `max_holdings` | float | 250000.0 | [100000, 500000] | medium | maximum cumulative bond holdings | Higher -> more sustained intervention capacity | ECB capital key |
| `gradualism` | float | 1.0 | [0.5, 2.0] | medium | scaling exponent for spread-proportional sizing | Higher -> more aggressive response to wide spreads | calibration |

## Worked Numerical Examples

### Case 1 - Intervention Triggered
System state: spread 450 bps, price 95.0, capacity 250000.
Calculation: spread (450) > threshold (300). `q = min(250000/95, 20000 * (450-300)/300) = min(2631, 10000) = 2631`.
Decision: buy 2631.
State update: capacity decreases by 2631 * 95 = 249945; capacity remaining ~ 55.

### Case 2 - Moderate Intervention
System state: spread 350 bps, price 98.0, capacity 200000.
Calculation: spread (350) > threshold (300). `q = min(200000/98, 20000 * (350-300)/300) = min(2040, 3333) = 2040`.
Decision: buy 2040.
State update: capacity decreases by 2040 * 98 = 199920; capacity remaining ~ 80.

### Case 3 - Hold (Spread Below Threshold)
System state: spread 250 bps, price 99.0, capacity 200000.
Calculation: spread (250) < threshold (300).
Decision: hold.
State update: unchanged.

### Edge Case - Capacity Exhausted
System state: spread 500 bps, price 90.0, capacity 100.
Calculation: spread > threshold but `capacity / price = 100/90 = 1.1`. `q = min(1.1, 20000 * 200/300) = 1.1`, rounds to 1.
Decision: buy 1.
State update: capacity effectively exhausted.

## Behavioral Verification and Calibration

- Given `spread > spread_threshold` and positive capacity, agent must buy.
- Given `spread <= spread_threshold`, agent must hold regardless of capacity.
- Given capacity exhausted, agent must hold regardless of spread.
- Agent must never sell sovereign bonds.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-backstop | `spread_threshold = infinity` | backstop prevents self-fulfilling crisis | increase | spread overshoot |
| unlimited-capacity | `max_holdings = infinity` | credibility of unlimited backstop | decrease | equilibrium spread |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | De Grauwe, P. (2012). The governance of a fragile Eurozone. https://doi.org/10.1111/j.1467-8462.2012.00684.x | Self-fulfilling sovereign crises and backstop |
| 2 | Krishnamurthy, A., Nagel, S., & Vissing-Jorgensen, A. (2018). ECB policies involving government bond purchases. https://doi.org/10.1093/rof/rfx053 | QE transmission channels |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-ecb-intervenor.png) |
| Status | draft |
