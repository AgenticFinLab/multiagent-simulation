# Minsky Borrower

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Debt-driven borrower whose leverage escalates from hedge to speculative to Ponzi financing during booms |
| Theory Family         | Financial Instability Hypothesis / Minsky Cycle |
| Behavioral Tendency   | **Destabilising** - increases leverage during calm periods, creating systemic fragility that erupts in crisis |
| Time Horizon          | medium |
| Risk Tolerance        | escalating (low -> high over cycle) |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a borrower (corporate, bank, or household) whose financing structure deteriorates during prolonged booms, transitioning from hedge finance (income covers principal and interest) to speculative finance (income covers only interest) to Ponzi finance (income covers neither, requiring asset appreciation or refinancing). The real-world counterpart is documented by Minsky (1986, 1992): stability itself is destabilising because calm conditions encourage progressively riskier debt structures.

The decision goal is to borrow and invest during booms (leveraging up as confidence grows), then face forced asset sales when refinancing fails. Non-goals: the agent does not proactively de-risk, does not anticipate the crisis, and must not behave as a contrarian.

## Theoretical Foundation

**Financial Instability Hypothesis**:
- Theory / Study: Stabilizing an unstable economy; The financial instability hypothesis.
- Citation: Minsky, H. P. (1986). *Stabilizing an Unstable Economy*. Yale University Press. / Minsky, H. P. (1992). The financial instability hypothesis. *Levy Economics Institute Working Paper No. 74*. https://doi.org/10.2139/ssrn.161024
- Core Insight: In periods of stability, borrowers and lenders become complacent, credit standards deteriorate, and financial structures become increasingly fragile until a "Minsky moment" triggers crisis.
- Mathematical Formulation: `leverage_target = base_leverage * (1 + boom_duration * escalation_rate)`. When `debt_service_ratio > income`, financing shifts from hedge to speculative to Ponzi. At Ponzi stage, if `asset_return < refinancing_cost`, forced liquidation.
- Empirical Evidence: Documented in pre-2008 housing boom, 1998 LTCM crisis, and numerous historical episodes where debt-to-income ratios escalated before collapse.
- Relevance to This Agent: The agent directly implements the Minsky borrower cycle, building leverage during calm and collapsing when refinancing fails.
- Calibration Source: `base_leverage` 2.0-4.0, `escalation_rate` 0.05-0.15, `ponzi_threshold` 0.80-1.20.
- Falsification Conditions: If the agent de-leverages during booms or does not face forced selling when in Ponzi stage with negative returns, the design is falsified.
- Alternative Theories: Rational leverage targeting (Modigliani-Miller); Adrian & Shin procyclical leverage without Minsky stages.

## Design Purpose and Activation Triggers

Purpose: Demonstrate endogenous financial fragility by progressively increasing leverage during booms and triggering cascading asset sales when the Ponzi financing stage collapses.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `asset_return` available (recent return on invested assets)
- `refinancing_cost` available (current cost of rolling debt)
- `boom_duration` available (consecutive periods of positive returns)
- own `cash`, `position`, `debt`, and `income` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `boom_duration > 0` AND `financing_stage != "ponzi"`: borrow and buy (leverage up).
- `financing_stage == "ponzi"` AND `asset_return < refinancing_cost`: forced liquidation.
- `financing_stage == "ponzi"` AND `asset_return >= refinancing_cost`: hold (surviving on appreciation).
- `<Default>`: hold.

Deactivation Conditions:
- equity wiped out (bankruptcy).
- forced liquidation complete (no position remaining).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Early boom (hedge stage) | borrows conservatively | income covers all debt service |
| Mid boom (speculative stage) | borrows more aggressively | income covers interest only |
| Late boom (Ponzi stage) | maximum leverage | relies on appreciation to service debt |
| Crisis (Ponzi collapse) | forced selling | cannot refinance, must liquidate |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | asset price |
| `asset_return` | environment | float | yes | recent return on assets |
| `refinancing_cost` | environment | float | yes | cost of rolling debt |
| `boom_duration` | environment | int | yes | consecutive positive-return periods |
| `cash` | own state | float | yes | liquid reserves |
| `position` | own state | float | yes | asset holding |
| `debt` | own state | float | yes | outstanding borrowing |
| `income` | own state | float | yes | periodic cash flow from operations |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Buy quantity depends on additional borrowing capacity. Sell quantity driven by forced liquidation needs.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution and valuation |
| `asset_return` | Continuous | 1 tick | Ponzi viability check |
| `refinancing_cost` | Continuous | 1 tick | debt rollover feasibility |
| `boom_duration` | Discrete | persistent | escalation trigger |
| `cash` | State | persistent | liquidity buffer |
| `position` | State | persistent | asset holding |
| `debt` | State | persistent | leverage numerator |
| `income` | State | persistent | debt-service capacity |

Does NOT use: market sentiment, peer leverage, regulatory signals.

#### Core Behavioral Mechanism

1. Compute `debt_service_ratio = (debt * refinancing_cost) / income`.
2. Classify financing stage:
   - Hedge: `debt_service_ratio < hedge_threshold` (income covers P+I).
   - Speculative: `hedge_threshold <= debt_service_ratio < ponzi_threshold`.
   - Ponzi: `debt_service_ratio >= ponzi_threshold`.
3. If in Ponzi stage AND `asset_return < refinancing_cost`: force sell `min(position, debt_to_cover / price)`.
4. If boom_duration > 0 AND not in Ponzi collapse: compute new borrowing = `escalation_rate * boom_duration * base_leverage * equity / price`. Buy that quantity.
5. Otherwise hold.
6. Emit decision.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | borrowing-funded purchase during boom; forced liquidation during collapse |
| Action lifetime | one decision call |
| Revision policy | reassess each tick |
| State constraint | debt cannot be negative; position >= 0 |
| Resource cap | buy limited by borrowing capacity; sell limited by position |
| Exit rule | forced sell in Ponzi stage when returns < refinancing cost |

#### Mathematical Model

`equity = cash + position * price - debt`

`leverage = (position * price) / equity`

`leverage_target = base_leverage * (1 + boom_duration * escalation_rate)`

`q_buy = (leverage_target * equity - position * price) / price` (clamped >= 0)

`q_sell_forced = min(position, (debt * refinancing_cost - income) / price)` in Ponzi collapse

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `base_leverage` | starting leverage ratio | 3.0 | Minsky (1986) |
| `escalation_rate` | leverage increase per boom period | 0.10 | calibration |
| `hedge_threshold` | DSR below which financing is hedge | 0.50 | Minsky (1992) |
| `ponzi_threshold` | DSR above which financing is Ponzi | 1.00 | Minsky (1992) |
| `max_leverage` | hard ceiling on leverage | 20.0 | risk management |

#### Behavioral Properties

- Time horizon: medium, because borrowing is accumulated over the cycle.
- Risk tolerance: escalating, starting low and rising to very high during booms.
- Information asymmetry: none, the agent does not anticipate collapse.
- Psychological profile: overconfident during booms, panicked during busts, procyclical.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `base_leverage` | float | 3.0 | [2.0, 4.0] | medium | initial leverage ratio in hedge stage | Higher -> faster progression to Ponzi | Minsky (1986) |
| `escalation_rate` | float | 0.10 | [0.05, 0.15] | high | leverage increase per boom period | Higher -> faster fragility buildup | calibration |
| `hedge_threshold` | float | 0.50 | [0.30, 0.60] | medium | DSR boundary between hedge and speculative | Lower -> earlier speculative classification | Minsky (1992) |
| `ponzi_threshold` | float | 1.00 | [0.80, 1.20] | high | DSR boundary triggering Ponzi classification | Lower -> earlier Ponzi stage, earlier collapse | Minsky (1992) |
| `max_leverage` | float | 20.0 | [15.0, 30.0] | low | hard leverage ceiling | Lower -> constrains boom buildup | risk management |

## Worked Numerical Examples

### Case 1 - Hedge Stage Borrowing (Early Boom)
System state: price 100, boom_duration 3, income 50000, debt 100000, refinancing_cost 0.05, equity 200000.
Calculation: `DSR = (100000 * 0.05) / 50000 = 0.10 < 0.50` -> hedge stage. `leverage_target = 3.0 * (1 + 3*0.10) = 3.9`. Current leverage = (position*100)/200000. If position = 4000: leverage = 2.0. Target_position = 3.9 * 200000 / 100 = 7800. `q_buy = 7800 - 4000 = 3800`.
Decision: buy 3800 (funded by new borrowing).
State update: position and debt increase.

### Case 2 - Speculative Stage (Mid Boom)
System state: price 120, boom_duration 8, income 50000, debt 400000, refinancing_cost 0.06.
Calculation: `DSR = (400000 * 0.06) / 50000 = 0.48`. Just below 0.50, still hedge. At boom_duration 10: `leverage_target = 3.0 * (1 + 10*0.10) = 6.0`. Continue buying.
Decision: buy (escalating leverage).
State update: debt and position continue growing.

### Case 3 - Ponzi Stage Survival
System state: price 150, debt 900000, income 50000, refinancing_cost 0.08, asset_return 0.10.
Calculation: `DSR = (900000 * 0.08) / 50000 = 1.44 > 1.00` -> Ponzi stage. But `asset_return (0.10) > refinancing_cost (0.08)`, so surviving on appreciation.
Decision: hold (relying on appreciation to cover shortfall).
State update: unchanged but fragile.

### Edge Case - Ponzi Collapse (Forced Liquidation)
System state: price 80 (crash), debt 900000, income 50000, refinancing_cost 0.10, asset_return -0.20, position 8000.
Calculation: `DSR = (900000 * 0.10) / 50000 = 1.80 > 1.00` -> Ponzi. `asset_return (-0.20) < refinancing_cost (0.10)`. Forced sell: `q = min(8000, (90000 - 50000) / 80) = min(8000, 500) = 500`.
Decision: sell 500 (forced liquidation to meet debt service).
State update: position decreases, proceeds used to cover debt service gap.

## Behavioral Verification and Calibration

- Given boom_duration > 0 and hedge/speculative stage, agent must increase leverage.
- Given Ponzi stage with asset_return < refinancing_cost, agent must force-sell.
- Given Ponzi stage with asset_return >= refinancing_cost, agent must hold (survive on appreciation).
- Agent must never voluntarily de-leverage during a boom.
- Leverage must escalate monotonically with boom_duration (until Ponzi collapse).
- Given missing asset_return, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-escalation | `escalation_rate = 0` | leverage escalation drives fragility | decrease | crisis severity |
| early-ponzi | `ponzi_threshold = 0.60` | earlier Ponzi triggers earlier crash | increase | crash frequency |
| low-base | `base_leverage = 1.5` | lower starting leverage delays Minsky moment | decrease | crisis severity |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Minsky, H. P. (1986). *Stabilizing an Unstable Economy*. Yale University Press. | Core Financial Instability Hypothesis |
| 2 | Minsky, H. P. (1992). The financial instability hypothesis. *Levy Economics Institute Working Paper No. 74*. https://doi.org/10.2139/ssrn.161024 | Formal statement of hedge/speculative/Ponzi taxonomy |
| 3 | Kindleberger, C. P., & Aliber, R. Z. (2005). *Manias, Panics, and Crashes*. 5th ed. Wiley. | Historical evidence of Minsky cycles |
| 4 | Keen, S. (1995). Finance and economic breakdown: Modeling Minsky's financial instability hypothesis. *Journal of Post Keynesian Economics*, 17(4), 607-635. | Formal Minsky cycle modeling |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-minsky-borrower.png) |
| Status | draft |
