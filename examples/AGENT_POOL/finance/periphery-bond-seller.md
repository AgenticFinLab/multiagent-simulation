# Periphery Bond Seller

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Sovereign debt holder who sells peripheral bonds during stress |
| Theory Family         | Sovereign Risk Contagion / Flight from Risk |
| Behavioral Tendency   | **Diverging** - sells peripheral sovereign debt during stress, amplifying spread widening |
| Time Horizon          | medium |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models an institutional investor (bank, asset manager, or sovereign wealth fund) that holds peripheral eurozone sovereign bonds and sells them when sovereign stress indicators breach critical thresholds. The real-world counterpart is the institutional flight-from-risk participant documented by Arghyrou and Kontonikas (2012) during the European debt crisis. The agent emits sell or hold orders based on spread levels and contagion signals.

The decision goal is to reduce peripheral bond exposure when sovereign spreads widen beyond a stress threshold, reflecting credit risk repricing and regulatory pressure. It does not provide liquidity during stress and it does not buy during crises. Non-goals: it must not buy peripheral bonds during elevated stress, and it must not ignore contagion signals from other periphery countries.

## Theoretical Foundation

**Sovereign risk contagion and flight from risk**:
- Theory / Study: The EMU sovereign-debt crisis: Fundamentals, expectations, and contagion.
- Citation: Arghyrou, M. G., & Kontonikas, A. (2012). The EMU sovereign-debt crisis: Fundamentals, expectations and contagion. *Journal of International Financial Markets, Institutions and Money*, 22(4), 658-677. https://doi.org/10.1016/j.intfin.2012.03.003
- Citation: Forbes, K. J., & Rigobon, R. (2002). No contagion, only interdependence: Measuring stock market comovements. *Journal of Finance*, 57(5), 2223-2261. https://doi.org/10.1111/0022-1082.00494
- Core Insight: Sovereign spreads widen sharply during stress due to fundamental repricing and contagion across periphery countries. Institutional investors face mark-to-market losses and regulatory capital charges that force sales, creating self-reinforcing sell pressure.
- Mathematical Formulation: `Q_sell = sell_fraction * position * stress_intensity` when `spread > stress_threshold`.
- Empirical Evidence: Arghyrou & Kontonikas show spread dynamics shift from fundamentals-driven to crisis-contagion regime; Forbes & Rigobon document interdependence in stress periods.
- Relevance to This Agent: The agent operationalizes forced selling under sovereign stress.
- Calibration Source: `stress_threshold` 100-400 bps, `sell_fraction` 0.05-0.25, `contagion_weight` 0.1-0.5.
- Falsification Conditions: If the agent buys peripheral bonds when spreads exceed the stress threshold, the design is falsified.
- Alternative Theories: Self-fulfilling crisis models (Calvo 1988); pure fundamental-based repricing without contagion.

## Design Purpose and Activation Triggers

Purpose: Model the institutional sell pressure on peripheral sovereign bonds during stress episodes, contributing to spread widening and potential self-fulfilling crises.

Call Frequency: every-tick.

Prerequisite Signals:
- `spread` available (peripheral bond spread over benchmark, in basis points)
- `contagion_signal` available (average spread of other periphery bonds, bps)
- `price` available (bond price)
- own `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `effective_spread > stress_threshold` AND `position > 0`: sell `sell_fraction * position * stress_intensity`.
- `effective_spread <= calm_threshold` AND `cash > 0`: buy `recovery_fraction * cash / price` (re-accumulation in calm).
- `<Default>`: hold.

Where `effective_spread = spread + contagion_weight * contagion_signal` and `stress_intensity = min((effective_spread - stress_threshold) / stress_threshold, 1.0)`.

Deactivation Conditions:
- position fully liquidated during stress.
- spreads return below calm threshold.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| spread above stress threshold | sells peripheral bonds | credit risk repricing, regulatory pressure |
| contagion from other periphery | accelerates selling | correlated sovereign risk |
| calm conditions | re-accumulates slowly | yield-seeking in stable environment |

Environmental Dependencies: requires sovereign spread data and contagion signal from peer periphery bonds.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | bond price, execution reference |
| `spread` | environment | float (bps) | yes | own-country sovereign spread |
| `contagion_signal` | environment | float (bps) | yes | average other-periphery spread |
| `cash` | own state | float | yes | re-accumulation capacity |
| `position` | own state | float | yes | sell capacity |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity is clamped to available position or cash/price.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `spread` | Continuous | 1 tick | own-country stress measure |
| `contagion_signal` | Continuous | 1 tick | peer-country stress |
| `cash` | State | persistent | buy constraint |
| `position` | State | persistent | sell constraint |

Does NOT use: equity markets, private policy information, central bank forward guidance.

#### Core Behavioral Mechanism

1. Read `price`, `spread`, `contagion_signal`, `cash`, and `position`.
2. Compute `effective_spread = spread + contagion_weight * contagion_signal`.
3. If `effective_spread > stress_threshold` and `position > 0`:
   - `stress_intensity = min((effective_spread - stress_threshold) / stress_threshold, 1.0)`.
   - `q = sell_fraction * position * stress_intensity`. Sell `min(position, q)`.
4. If `effective_spread <= calm_threshold` and `cash > 0`:
   - `q = recovery_fraction * cash / price`. Buy.
5. Otherwise, hold.
6. Emit the decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `sell_fraction * position * stress_intensity` for sells; `recovery_fraction * cash / price` for buys |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot go negative |
| Resource cap | sell capped by position; buy capped by cash / price |
| Exit rule | sell accelerates with spread widening |

#### Mathematical Model

`q_sell = min(position, sell_fraction * position * min((eff_spread - theta_stress) / theta_stress, 1))` if `eff_spread > theta_stress`; `q_buy = min(cash / price, recovery_fraction * cash / price)` if `eff_spread <= theta_calm`; otherwise `q = 0`. Where `eff_spread = spread + contagion_weight * contagion_signal`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_stress` | stress threshold (bps) | 200 | Arghyrou & Kontonikas (2012) |
| `theta_calm` | calm re-entry threshold (bps) | 80 | calibration |
| `sell_fraction` | max fraction of position to sell per tick | 0.10 | calibration |
| `recovery_fraction` | fraction of cash to redeploy in calm | 0.05 | calibration |
| `contagion_weight` | weight on peer-periphery spreads | 0.30 | Arghyrou & Kontonikas (2012) |

#### Behavioral Properties

- Time horizon: medium, because institutional mandates allow gradual de-risking.
- Risk tolerance: low, because regulatory capital and mark-to-market losses force action.
- Information asymmetry: partial, observes public spread data.
- Psychological profile: risk-averse institutional mandate; sells into stress, re-accumulates in calm.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `stress_threshold` | float | 200 | [100, 400] | high | spread level triggering sells (bps) | Higher -> later sell onset | Arghyrou & Kontonikas (2012) |
| `calm_threshold` | float | 80 | [30, 120] | medium | spread level for re-accumulation (bps) | Lower -> earlier re-entry | calibration |
| `sell_fraction` | float | 0.10 | [0.05, 0.25] | high | max position fraction sold per tick | Higher -> faster liquidation | calibration |
| `recovery_fraction` | float | 0.05 | [0.02, 0.10] | low | cash fraction redeployed in calm | Higher -> faster re-accumulation | calibration |
| `contagion_weight` | float | 0.30 | [0.10, 0.50] | high | sensitivity to peer-periphery stress | Higher -> more contagion amplification | Arghyrou & Kontonikas (2012) |

## Worked Numerical Examples

### Case 1 - Stress Sell

System state: price 95.0, spread 300 bps, contagion_signal 250 bps, position 1000, cash 10000.
Calculation: `eff_spread = 300 + 0.30*250 = 375`. `stress_intensity = min((375-200)/200, 1) = min(0.875, 1) = 0.875`. `q = 0.10 * 1000 * 0.875 = 87.5 -> 87`.
Decision: sell 87.
State update: position decreases by 87, cash increases by 8265.

### Case 2 - Calm Re-accumulation

System state: price 100.0, spread 50 bps, contagion_signal 40 bps, position 500, cash 50000.
Calculation: `eff_spread = 50 + 0.30*40 = 62`. `62 <= 80` calm threshold. `q = 0.05 * 50000 / 100 = 25`.
Decision: buy 25.
State update: cash decreases by 2500, position increases by 25.

### Case 3 - Moderate Spread, Hold

System state: price 98.0, spread 150 bps, contagion_signal 100 bps, position 800, cash 20000.
Calculation: `eff_spread = 150 + 0.30*100 = 180`. `180 < 200` (below stress) and `180 > 80` (above calm).
Decision: hold.
State update: unchanged.

### Edge Case - Stress but No Position

System state: price 90.0, spread 400 bps, contagion_signal 300 bps, position 0, cash 30000.
Calculation: `eff_spread = 400 + 90 = 490 > 200`, sell triggered but position is 0.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `effective_spread > stress_threshold` and `position > 0`, agent must sell.
- Given `effective_spread <= calm_threshold` and `cash > 0`, agent must buy.
- Agent must never buy when effective spread exceeds stress threshold.
- Given missing spread data, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-contagion | `contagion_weight = 0` | contagion amplifies crisis | decrease | spread widening speed |
| low-stress-threshold | `stress_threshold = 100` | lower threshold -> earlier selling | increase | sell volume in early stress |
| no-recovery | `recovery_fraction = 0` | re-accumulation stabilises calm periods | decrease | calm-period bond demand |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Arghyrou, M. G., & Kontonikas, A. (2012). The EMU sovereign-debt crisis. https://doi.org/10.1016/j.intfin.2012.03.003 | Sovereign contagion dynamics |
| 2 | Forbes, K. J., & Rigobon, R. (2002). No contagion, only interdependence. https://doi.org/10.1111/0022-1082.00494 | Measuring contagion vs interdependence |
| 3 | Calvo, G. A. (1988). Servicing the public debt: The role of expectations. https://doi.org/10.2307/1827423 | Self-fulfilling crisis alternative |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-periphery-bond-seller.png) |
| Status | draft |
