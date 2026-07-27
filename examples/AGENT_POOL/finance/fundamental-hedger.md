# Fundamental hedger

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Fundamentals-driven hedger managing real-economy exposure |
| Theory Family         | Portfolio Theory / Hedging Demand |
| Behavioral Tendency   | **Stabilising** - reduces portfolio volatility by hedging real-economy exposure based on fundamental correlations, dampening speculative excess |
| Time Horizon          | medium |
| Risk Tolerance        | low |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a corporate treasurer, commodity producer, or institutional investor who uses financial markets to hedge real-economy exposure rather than to speculate. The real-world counterpart is Merton's (1971) hedging-demand investor who trades to offset non-financial income risk. The agent computes optimal hedge ratios from fundamental correlations and adjusts positions to maintain target hedge coverage, accepting basis risk as a cost of imperfect hedging.

The decision goal is to maintain a target hedge ratio that minimises portfolio variance arising from real-economy exposure (e.g., commodity price risk, currency risk, interest rate risk). It is not a speculator and does not seek alpha. Non-goals: it must not take unhedged directional bets, and it must not ignore basis risk when computing hedge sizes.

## Theoretical Foundation

**Intertemporal hedging demand**:
- Theory / Study: Optimum consumption and portfolio rules in a continuous-time model.
- Citation: Merton, R. C. (1971). Optimum consumption and portfolio rules in a continuous-time model. *Journal of Economic Theory*, 3(4), 373-413. https://doi.org/10.1016/0022-0531(71)90038-X
- Core Insight: Investors with non-tradeable income or state-variable risks hold "hedging portfolios" in addition to the mean-variance tangency portfolio. The hedging demand arises from the desire to offset correlated risks in non-financial wealth.
- Mathematical Formulation: `hedge_position = -beta_exposure * exposure_size * hedge_ratio`, where `hedge_ratio = correlation * (sigma_exposure / sigma_hedge_instrument)`.
- Empirical Evidence: Campbell & Viceira (2002) document substantial hedging demand in long-horizon optimal portfolios. Corporate hedging studies (Tufano 1996) show real firms actively manage exposure.
- Relevance to This Agent: The agent computes and maintains an optimal hedge ratio to offset real-economy exposure.
- Calibration Source: `hedge_ratio` 0.5-1.0 (depending on correlation), `exposure_size` scenario-dependent.
- Falsification Conditions: If the agent takes speculative positions uncorrelated with its declared exposure, the design is falsified.
- Alternative Theories: No-hedging benchmark (Modigliani-Miller); full speculation.

**Basis risk in hedging**:
- Theory / Study: Optimal hedging under basis risk.
- Citation: Anderson, R. W., & Danthine, J.-P. (1981). Cross hedging. *Journal of Political Economy*, 89(6), 1182-1196. https://doi.org/10.1086/261028
- Core Insight: When the hedging instrument does not perfectly correlate with the exposure, residual "basis risk" remains. The optimal hedge ratio minimises total variance accounting for imperfect correlation, resulting in hedge ratios below 1.0 for cross-hedges.
- Mathematical Formulation: `optimal_h = cov(exposure, instrument) / var(instrument) = rho * (sigma_e / sigma_i)`. Residual variance = `(1 - rho^2) * sigma_e^2`.
- Empirical Evidence: Anderson & Danthine show cross-hedge ratios for commodities range from 0.3 to 0.9 depending on contract specification.
- Relevance to This Agent: The agent uses `hedge_effectiveness` (rho^2) to adjust hedge ratio and accepts residual basis risk.
- Calibration Source: `hedge_effectiveness` 0.60-0.95.
- Falsification Conditions: If the agent hedges at ratio 1.0 regardless of correlation, the design is falsified.
- Alternative Theories: Perfect-hedge assumption; delta-neutral options strategies.

## Design Purpose and Activation Triggers

Purpose: Maintain target hedge coverage against real-economy exposure by adjusting financial-market positions based on fundamental correlations and basis-risk-adjusted hedge ratios.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available (hedging instrument price)
- `exposure_value` available (current real-economy exposure in currency units)
- `hedge_effectiveness` available (rho^2, or estimated correlation)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `actual_hedge_ratio < target_hedge_ratio - rebalance_band`: buy hedge instrument to increase coverage.
- `actual_hedge_ratio > target_hedge_ratio + rebalance_band`: sell hedge instrument to reduce over-hedging.
- `<Default>`: hold (hedge ratio within acceptable band).

Deactivation Conditions:
- hedge ratio within rebalance band.
- cash exhausted for increasing hedge.
- exposure eliminated (nothing to hedge).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| under-hedged | buys hedge instrument | restore target coverage |
| over-hedged | sells hedge instrument | reduce unnecessary cost |
| within band | holds | avoids transaction costs |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | hedge instrument price |
| `exposure_value` | environment | float | yes | real-economy exposure (currency units) |
| `hedge_effectiveness` | environment or model | float | yes | R-squared of hedge (0-1) |
| `cash` | own state | float | yes | available capital for hedge |
| `position` | own state | float | yes | current hedge instrument holdings |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | hedge instrument valuation |
| `exposure_value` | Continuous | 1 tick | exposure computation |
| `hedge_effectiveness` | Continuous | 1 tick | optimal ratio calculation |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | current hedge coverage |

Does NOT use: momentum, sentiment, speculative signals, peer actions.

#### Core Behavioral Mechanism

1. Read `price`, `exposure_value`, `hedge_effectiveness`, `cash`, and `position`.
2. Compute `target_position = (exposure_value / price) * target_hedge_ratio * sqrt(hedge_effectiveness)`.
3. Compute `position_gap = target_position - position`.
4. If `position_gap > rebalance_band * target_position` (under-hedged):
   - Buy `min(position_gap, cash / price, max_order_size)`.
5. If `position_gap < -rebalance_band * target_position` (over-hedged):
   - Sell `min(|position_gap|, position, max_order_size)`.
6. Otherwise hold (within band).
7. Emit decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `position_gap` capped by `max_order_size` and resource constraints |
| Action lifetime | one decision call |
| Revision policy | recompute target each tick based on current exposure |
| State constraint | position cannot fall below zero (no speculative short) |
| Resource cap | buy capped by `cash / price` |
| Exit rule | sell excess when over-hedged beyond rebalance band |

#### Mathematical Model

`target_position = (exposure_value / price) * target_hedge_ratio * sqrt(hedge_effectiveness)`; `position_gap = target_position - position`; `q_buy = min(|gap|, cash/price, max_order_size)` if `gap > rebalance_band * target`; `q_sell = min(|gap|, position, max_order_size)` if `gap < -rebalance_band * target`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `target_hedge_ratio` | desired coverage fraction | 0.80 | Merton (1971), conservative |
| `hedge_effectiveness` | R-squared of hedge relationship | 0.75 | Anderson & Danthine (1981) |
| `rebalance_band` | tolerance band (fraction of target) | 0.10 | transaction cost optimisation |
| `max_order_size` | maximum units traded per tick | 300.0 | gradual adjustment |
| `exposure_value` | real-economy exposure in currency | 100000.0 | scenario-dependent |

#### Behavioral Properties

- Time horizon: medium, because hedges are maintained over the exposure lifetime.
- Risk tolerance: low, because the purpose is variance reduction not return maximisation.
- Information asymmetry: partial, because hedge effectiveness may be estimated with error.
- Psychological profile: disciplined risk manager focused on exposure offset rather than profit.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `target_hedge_ratio` | float | 0.80 | [0.50, 1.0] | high | fraction of exposure to hedge | Higher -> more complete hedging | Merton (1971) |
| `hedge_effectiveness` | float | 0.75 | [0.60, 0.95] | high | R-squared between exposure and instrument | Higher -> larger hedge position (less basis risk adjustment) | Anderson & Danthine (1981) |
| `rebalance_band` | float | 0.10 | [0.05, 0.20] | medium | tolerance band before rebalancing | Wider -> fewer trades, more drift | transaction cost trade-off |
| `max_order_size` | float | 300.0 | [100, 500] | medium | maximum units per adjustment | Higher -> faster convergence to target | scenario calibration |
| `exposure_value` | float | 100000.0 | [50000, 500000] | low | real-economy exposure in currency units | Sets absolute hedge size | scenario-dependent |

## Worked Numerical Examples

### Case 1 - Under-Hedged (Buy to Increase Coverage)

System state: price 50.0, exposure_value 100000, hedge_effectiveness 0.75, cash 30000, position 800.
Calculation: `target_position = (100000/50) * 0.80 * sqrt(0.75) = 2000 * 0.80 * 0.866 = 1385.6`.
`position_gap = 1385.6 - 800 = 585.6`. `rebalance_band * target = 0.10 * 1385.6 = 138.6`.
`gap (585.6) > 138.6` -> under-hedged.
`q = min(585.6, 30000/50, 300) = min(585.6, 600, 300) = 300`.
Decision: buy 300.
State update: position increases to 1100; cash decreases by 15000.

### Case 2 - Over-Hedged (Sell Excess)

System state: price 50.0, exposure_value 60000, hedge_effectiveness 0.75, cash 20000, position 1200.
Calculation: `target_position = (60000/50) * 0.80 * 0.866 = 1200 * 0.693 = 831.4`.
`position_gap = 831.4 - 1200 = -368.6`. `|gap| > rebalance_band * target (83.1)` -> over-hedged.
`q = min(368.6, 1200, 300) = 300`.
Decision: sell 300.
State update: position decreases to 900.

### Case 3 - Within Band (Hold)

System state: price 50.0, exposure_value 100000, hedge_effectiveness 0.75, cash 20000, position 1350.
Calculation: `target_position = 1385.6`. `position_gap = 1385.6 - 1350 = 35.6`.
`rebalance_band * target = 138.6`. `gap (35.6) < 138.6` -> within band.
Decision: hold.
State update: unchanged.

### Edge Case - No Cash to Hedge

System state: price 50.0, exposure_value 100000, hedge_effectiveness 0.75, cash 0, position 500.
Calculation: `target_position = 1385.6`. `gap = 885.6 > 138.6` -> under-hedged.
`q = min(885.6, 0/50, 300) = 0`. Cash constraint binds.
Decision: hold (cannot increase hedge).
State update: unchanged.

## Behavioral Verification and Calibration

- Given position below target minus rebalance band, agent must buy hedge instrument.
- Given position above target plus rebalance band, agent must sell excess.
- Given position within band, agent must hold.
- Agent must never take speculative positions (position must relate to exposure offset).
- Hedge ratio must be adjusted for hedge_effectiveness (never hedge at ratio 1.0 when R^2 < 1).

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| full-hedge | `target_hedge_ratio = 1.0` | complete hedging eliminates exposure variance | decrease | portfolio variance |
| no-basis-adjustment | `hedge_effectiveness = 1.0` | ignoring basis risk leads to over-hedging | increase | basis-risk losses |
| wide-band | `rebalance_band = 0.30` | wider band reduces trading but increases drift | decrease | trade count |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Merton, R. C. (1971). Optimum consumption and portfolio rules in a continuous-time model. *Journal of Economic Theory*, 3(4), 373-413. https://doi.org/10.1016/0022-0531(71)90038-X | Hedging demand in dynamic portfolio choice |
| 2 | Anderson, R. W., & Danthine, J.-P. (1981). Cross hedging. *Journal of Political Economy*, 89(6), 1182-1196. https://doi.org/10.1086/261028 | Optimal hedge ratio under basis risk |
| 3 | Campbell, J. Y., & Viceira, L. M. (2002). *Strategic Asset Allocation: Portfolio Choice for Long-Term Investors*. Oxford University Press. https://doi.org/10.1093/0198296940.001.0001 | Long-horizon hedging demand |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-fundamental-hedger.png) |
| Status | draft |
