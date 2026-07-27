# Skeptical value investor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Deep-value investor requiring extreme margin of safety |
| Theory Family         | Value Investing / Security Analysis |
| Behavioral Tendency   | **Stabilising** - provides price floor by buying only at deep discounts and holding through volatility, anchoring prices toward fundamentals |
| Time Horizon          | long |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a deep-value investor in the Graham and Dodd tradition who requires an exceptionally large discount to intrinsic value before committing capital. The real-world counterpart is the margin-of-safety practitioner described by Graham and Dodd (1934) and the value-premium harvester identified by Fama and French (1993). The agent computes intrinsic value from fundamentals and only buys when market price trades far below that estimate. It sells only when price reaches or exceeds intrinsic value.

The decision goal is to buy securities at prices far below intrinsic value (large margin of safety) and hold until price converges to fair value. It is not a momentum trader and does not trade on sentiment. Non-goals: it must not buy at small discounts, and it must not sell before reaching intrinsic value absent extreme overvaluation.

## Theoretical Foundation

**Margin of safety in security analysis**:
- Theory / Study: Margin of safety in value investing.
- Citation: Graham, B., & Dodd, D. L. (1934). *Security Analysis*. McGraw-Hill. ISBN: 978-0-07-159253-6.
- Core Insight: Investors should only purchase securities when market price is substantially below a conservatively estimated intrinsic value, providing a "margin of safety" against estimation errors, adverse events, and market irrationality.
- Mathematical Formulation: `buy_condition: price < intrinsic_value * (1 - margin_of_safety)`. Required margin: 40-60% for speculative-grade, 20-40% for investment-grade.
- Empirical Evidence: Decades of value investing outperformance documented by Lakonishok, Shleifer, & Vishny (1994) and Fama & French (1993).
- Relevance to This Agent: The agent requires a very large margin of safety (default 50%) before buying, making it extremely selective.
- Calibration Source: `margin_of_safety` 0.40-0.60, `intrinsic_value` scenario-dependent.
- Falsification Conditions: If the agent buys when price is within 20% of intrinsic value, the design is falsified.
- Alternative Theories: Efficient market hypothesis (no persistent undervaluation); momentum investing.

**Value premium and HML factor**:
- Theory / Study: Common risk factors in equity returns.
- Citation: Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3-56. https://doi.org/10.1016/0304-405X(93)90023-5
- Core Insight: High book-to-market (value) stocks earn a systematic premium over low book-to-market (growth) stocks, consistent with either risk-based or behavioural mispricing explanations.
- Mathematical Formulation: `E[R_i] = R_f + beta_MKT * MKT + beta_SMB * SMB + beta_HML * HML`. Value stocks load positively on HML.
- Empirical Evidence: Fama & French document a 5.2% annual HML premium in US equities 1963-1991, robust across subperiods.
- Relevance to This Agent: The agent systematically harvests the value premium by concentrating purchases in deeply discounted securities.
- Calibration Source: Historical HML premium justifies patient deep-value strategy.
- Falsification Conditions: If the agent holds growth (high P/B) stocks or ignores valuation ratios, the design is falsified.
- Alternative Theories: Behavioural overreaction (Lakonishok et al. 1994); risk-based value premium.

## Design Purpose and Activation Triggers

Purpose: Provide a stabilising price floor by purchasing only at extremely deep discounts to intrinsic value, and selling when price reaches or modestly exceeds intrinsic value.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `intrinsic_value` available (or computable from fundamentals)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `price < intrinsic_value * (1 - margin_of_safety)`: buy, sized by `value_allocation_size`.
- `price > intrinsic_value * (1 + sell_premium)`: sell, sized by `min(position, value_allocation_size)`.
- `<Default>`: hold.

Deactivation Conditions:
- cash exhausted during deep-discount phase.
- position exhausted during sell phase.
- price between buy threshold and sell threshold (patient holding zone).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| deep discount (price far below IV) | cautious accumulation | margin of safety triggered |
| price at or above IV | gradual distribution | value realisation |
| price between thresholds | patient holding | discipline and conviction |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `intrinsic_value` | environment or model | float | yes | estimated fundamental value |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | sell capacity |

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
| `price` | Continuous | 1 tick | valuation comparison |
| `intrinsic_value` | Continuous | 1 tick | fundamental anchor |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell capacity |

Does NOT use: momentum signals, sentiment, peer trades, technical indicators.

#### Core Behavioral Mechanism

1. Read `price`, `intrinsic_value`, `cash`, and `position`.
2. Compute `discount = (intrinsic_value - price) / intrinsic_value`.
3. If `discount > margin_of_safety` (deep value): buy `min(cash / price, value_allocation_size)`.
4. Compute `premium = (price - intrinsic_value) / intrinsic_value`.
5. If `premium > sell_premium` (overvaluation): sell `min(position, value_allocation_size)`.
6. Otherwise hold patiently.
7. Emit decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `value_allocation_size`, capped by resource constraints |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy quantity cannot exceed `cash / price` |
| Exit rule | sell when price exceeds intrinsic value by sell_premium |

#### Mathematical Model

`q_buy = min(cash / price, value_allocation_size)` if `(intrinsic_value - price) / intrinsic_value > margin_of_safety`; `q_sell = min(position, value_allocation_size)` if `(price - intrinsic_value) / intrinsic_value > sell_premium`; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `margin_of_safety` | required discount to intrinsic value | 0.50 | Graham & Dodd (1934) |
| `sell_premium` | required premium above IV to sell | 0.10 | value realisation |
| `value_allocation_size` | fixed order size per tick | 150.0 | conservative allocation |
| `intrinsic_value` | estimated fundamental worth | 100.0 | scenario-dependent |

#### Behavioral Properties

- Time horizon: long, because value investing requires patience for price convergence.
- Risk tolerance: low, because the large margin of safety protects against downside.
- Information asymmetry: none.
- Psychological profile: patient, skeptical, contrarian investor who demands extreme bargains.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `margin_of_safety` | float | 0.50 | [0.40, 0.60] | high | required discount below intrinsic value to buy | Higher -> fewer purchases, deeper value only | Graham & Dodd (1934) |
| `sell_premium` | float | 0.10 | [0.05, 0.20] | medium | required premium above intrinsic value to sell | Higher -> holds longer above IV | value realisation logic |
| `value_allocation_size` | float | 150.0 | [50, 300] | medium | units bought or sold per tick when triggered | Higher -> faster accumulation/distribution | scenario calibration |
| `intrinsic_value` | float | 100.0 | [50, 500] | low | agent's estimated intrinsic value | Sets buy/sell thresholds | scenario-dependent |

## Worked Numerical Examples

### Case 1 - Deep Value Buy

System state: price 45.0, intrinsic_value 100.0, cash 50000, position 100.
Calculation: `discount = (100 - 45) / 100 = 0.55 > margin_of_safety (0.50)` -> buy trigger.
`q = min(50000/45, 150) = min(1111, 150) = 150`.
Decision: buy 150.
State update: position increases to 250; cash decreases by 6750.

### Case 2 - Overvaluation Sell

System state: price 115.0, intrinsic_value 100.0, cash 30000, position 400.
Calculation: `premium = (115 - 100) / 100 = 0.15 > sell_premium (0.10)` -> sell trigger.
`q = min(400, 150) = 150`.
Decision: sell 150.
State update: position decreases to 250; cash increases.

### Case 3 - Patient Hold (Between Thresholds)

System state: price 70.0, intrinsic_value 100.0, cash 40000, position 200.
Calculation: `discount = (100 - 70) / 100 = 0.30 < margin_of_safety (0.50)`. `premium < 0`.
Decision: hold.
State update: unchanged.

### Edge Case - Moderate Discount (Not Deep Enough)

System state: price 55.0, intrinsic_value 100.0, cash 80000, position 100.
Calculation: `discount = 0.45 < margin_of_safety (0.50)` -> does NOT buy despite 45% discount.
Decision: hold.
State update: unchanged. The agent truly requires a 50%+ discount.

## Behavioral Verification and Calibration

- Given price discount exceeding margin_of_safety, agent must buy up to allocation size.
- Given price premium exceeding sell_premium, agent must sell up to allocation size.
- Given price between thresholds (even at 40% discount), agent must hold.
- Agent must never buy at small discounts (< margin_of_safety).
- Agent must never use momentum or sentiment to override valuation discipline.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| moderate-value | `margin_of_safety = 0.25` | lower bar increases trade frequency and market participation | increase | buy frequency |
| extreme-skeptic | `margin_of_safety = 0.60` | extreme bar reduces all buying activity | decrease | buy frequency |
| no-sell-discipline | `sell_premium = 0.0` | selling at IV captures value faster | increase | portfolio turnover |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Graham, B., & Dodd, D. L. (1934). *Security Analysis*. McGraw-Hill. ISBN: 978-0-07-159253-6. | Margin of safety framework |
| 2 | Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3-56. https://doi.org/10.1016/0304-405X(93)90023-5 | Value premium (HML factor) |
| 3 | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541-1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x | Behavioural explanation of value premium |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-skeptical-value-investor.png) |
| Status | draft |
