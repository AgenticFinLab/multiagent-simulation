# Risk-averse saver

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Highly risk-averse cash-preference agent |
| Theory Family         | Behavioral Finance / Precautionary Savings |
| Behavioral Tendency   | **Stabilising** - hoards cash and avoids market exposure, dampening speculative excess |
| Time Horizon          | long |
| Risk Tolerance        | very low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a retail saver or pension participant who strongly prefers cash and risk-free deposits over equity or risky-asset exposure. The real-world counterpart is the loss-averse household documented by Kahneman and Tversky (1979) and the precautionary saver formalised by Carroll (1997). The agent emits buy, sell, or hold orders with extremely conservative sizing, selling risky assets when perceived risk rises and only buying when valuations are far below perceived fair value.

The decision goal is to preserve capital and maintain a high cash-to-portfolio ratio at all times. It is not a speculator and does not seek return maximisation. Non-goals: it must not chase momentum, and it must not increase exposure when volatility is elevated.

## Theoretical Foundation

**Loss aversion and prospect theory**:
- Theory / Study: Loss aversion in risky choice.
- Citation: Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291. https://doi.org/10.2307/1914185
- Core Insight: Losses are weighted approximately 2.25x more heavily than equivalent gains, producing extreme caution and a preference for certain outcomes over uncertain gambles with higher expected value.
- Mathematical Formulation: `U(x) = x^alpha` for gains, `U(x) = -lambda * (-x)^beta` for losses, with `lambda ≈ 2.25`, `alpha = beta ≈ 0.88`.
- Empirical Evidence: Kahneman & Tversky demonstrate S-shaped value function across hundreds of experimental lotteries.
- Relevance to This Agent: The agent's refusal to invest at fair prices and insistence on large discounts operationalises loss aversion.
- Calibration Source: `loss_aversion_lambda` 1.5-3.0, `cash_target_ratio` 0.70-0.95.
- Falsification Conditions: If the agent increases exposure during periods of rising volatility, the design is falsified.
- Alternative Theories: Rational risk aversion under CRRA utility; habit formation (Campbell & Cochrane 1999).

**Precautionary savings motive**:
- Theory / Study: Buffer-stock savings and the life-cycle / permanent-income hypothesis.
- Citation: Carroll, C. D. (1997). Buffer-stock saving and the life cycle/permanent income hypothesis. *Quarterly Journal of Economics*, 112(1), 1-55. https://doi.org/10.1162/003355397555109
- Core Insight: Agents facing income uncertainty maintain a target wealth-to-income ratio as a buffer against bad shocks, leading to excess cash holdings relative to frictionless models.
- Mathematical Formulation: Agent targets `cash_ratio >= cash_target_ratio`; deviations trigger sell orders to restore buffer.
- Empirical Evidence: Carroll shows median US household savings behaviour is consistent with buffer-stock rather than LC/PIH.
- Relevance to This Agent: The agent maintains a cash buffer target and sells risky assets whenever the ratio falls below target.
- Calibration Source: `cash_target_ratio` 0.80 (conservative household calibration).
- Falsification Conditions: If the agent holds less than 50% cash for more than 2 consecutive periods, the design is falsified.
- Alternative Theories: Rational inattention savings; mental accounting (Thaler 1999).

## Design Purpose and Activation Triggers

Purpose: Maintain high cash-to-portfolio ratio by avoiding risky-asset exposure and liquidating positions when perceived risk rises or the cash buffer is depleted.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `volatility` available (or proxy such as recent price dispersion)
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `cash_ratio < cash_target_ratio` AND `position > 0`: sell to restore cash buffer, sized by `min(position, restore_quantity)`.
- `volatility > vol_threshold`: sell entire position if any remains.
- `price < fair_value * (1 - discount_required)` AND `cash_ratio > cash_target_ratio + margin`: buy a small allocation sized by `cautious_size`.
- `<Default>`: hold.

Deactivation Conditions:
- cash_ratio restored above target.
- position already zero during sell triggers.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| low cash ratio | sells risky assets | precautionary buffer restoration |
| high volatility | exits all exposure | loss-aversion driven flight to safety |
| deep discount + excess cash | small cautious buy | value opportunity within loss-averse frame |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current asset price |
| `volatility` | environment | float | yes | annualised or rolling volatility measure |
| `cash` | own state | float | yes | current cash holdings |
| `position` | own state | float | yes | current risky-asset units |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash (for buy) or position (for sell).

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution and valuation reference |
| `volatility` | Continuous | 1 tick | risk trigger |
| `cash` | State | persistent | buffer-stock ratio |
| `position` | State | persistent | exposure and sell constraint |

Does NOT use: sentiment indicators, peer actions, private information.

#### Core Behavioral Mechanism

1. Read `price`, `volatility`, `cash`, and `position`.
2. Compute `portfolio_value = cash + position * price`.
3. Compute `cash_ratio = cash / portfolio_value`.
4. If `volatility > vol_threshold` and `position > 0`, sell all: `q = position`.
5. Else if `cash_ratio < cash_target_ratio` and `position > 0`, sell to restore: `q = min(position, restore_quantity)`.
6. Else if `price < fair_value * (1 - discount_required)` and `cash_ratio > cash_target_ratio + 0.05`, buy cautiously: `q = cautious_size`.
7. Else hold.
8. Emit decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | sell: `min(position, restore_quantity)` or full liquidation; buy: `cautious_size` |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot fall below zero |
| Resource cap | buy quantity cannot exceed `cash / price` |
| Exit rule | sell when volatility exceeds threshold or cash ratio drops below target |

#### Mathematical Model

`q_sell = position` if `volatility > vol_threshold`; `q_sell = min(position, restore_quantity)` if `cash_ratio < cash_target_ratio`; `q_buy = min(cash / price, cautious_size)` if `price < fair_value * (1 - discount_required)` and buffer is adequate; otherwise `q = 0`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `cash_target_ratio` | target cash-to-portfolio ratio | 0.80 | Carroll (1997) |
| `vol_threshold` | volatility trigger for full exit | 0.25 | Kahneman & Tversky (1979), calibrated |
| `discount_required` | required discount to fair value for buy | 0.30 | loss aversion lambda ≈ 2.25 |
| `cautious_size` | maximum buy size per tick | 50.0 | conservative allocation |
| `restore_quantity` | units sold per tick to restore buffer | 100.0 | gradual liquidation |
| `fair_value` | perceived fundamental price | 100.0 | scenario-dependent |

#### Behavioral Properties

- Time horizon: long, because the agent targets permanent wealth preservation.
- Risk tolerance: very low, because loss aversion dominates.
- Information asymmetry: none.
- Psychological profile: loss-averse precautionary saver who hoards cash as insurance.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `cash_target_ratio` | float | 0.80 | [0.70, 0.95] | high | target fraction of portfolio held in cash | Higher -> less market participation | Carroll (1997) |
| `vol_threshold` | float | 0.25 | [0.15, 0.40] | high | volatility level triggering full liquidation | Lower -> earlier panic selling | Kahneman & Tversky (1979) |
| `discount_required` | float | 0.30 | [0.20, 0.50] | medium | required price discount below fair value to buy | Higher -> rarer buying | Kahneman & Tversky (1979) |
| `cautious_size` | float | 50.0 | [10, 200] | medium | maximum units bought per tick | Higher -> faster allocation when triggered | scenario calibration |
| `restore_quantity` | float | 100.0 | [50, 500] | medium | units sold per tick to restore cash buffer | Higher -> faster liquidation | scenario calibration |
| `fair_value` | float | 100.0 | [50, 500] | low | agent's perceived fundamental price | Sets buy trigger level | scenario-dependent |

## Worked Numerical Examples

### Case 1 - Volatility Panic Sell

System state: price 95.0, volatility 0.30, cash 80000, position 400.
Calculation: `volatility (0.30) > vol_threshold (0.25)` → full liquidation. `q = 400`.
Decision: sell 400.
State update: position drops to 0; cash increases by 400 * 95 = 38000.

### Case 2 - Buffer Restoration Sell

System state: price 100.0, volatility 0.15, cash 60000, position 600.
Calculation: `portfolio_value = 60000 + 600 * 100 = 120000`. `cash_ratio = 60000 / 120000 = 0.50 < 0.80`.
`q = min(600, 100) = 100`.
Decision: sell 100.
State update: position drops to 500; cash increases by 10000.

### Case 3 - Cautious Buy on Deep Discount

System state: price 65.0, volatility 0.10, cash 90000, position 50, fair_value 100.
Calculation: `portfolio_value = 90000 + 50 * 65 = 93250`. `cash_ratio = 90000 / 93250 ≈ 0.965 > 0.85`.
`price (65) < fair_value * (1 - 0.30) = 70` → buy trigger active.
`q = min(90000 / 65, 50) = 50`.
Decision: buy 50.
State update: position increases to 100; cash decreases by 3250.

### Edge Case - Already All Cash

System state: price 100.0, volatility 0.30, cash 100000, position 0.
Calculation: `volatility > vol_threshold` but `position = 0` → nothing to sell.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `volatility > vol_threshold` and `position > 0`, agent must sell entire position.
- Given `cash_ratio < cash_target_ratio`, agent must sell to restore buffer.
- Given deep discount with adequate buffer, agent may buy up to `cautious_size`.
- Given normal conditions (no trigger), agent must hold.
- Agent must never hold less than 50% cash across two consecutive periods.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-vol-panic | `vol_threshold = 1.0` | volatility exit prevents crash losses | increase | max drawdown |
| aggressive-saver | `cash_target_ratio = 0.95` | higher buffer reduces participation | decrease | market volume |
| no-discount-buy | `discount_required = 1.0` | cautious buying provides floor support | decrease | price recovery speed |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291. https://doi.org/10.2307/1914185 | Loss aversion foundation |
| 2 | Carroll, C. D. (1997). Buffer-stock saving and the life cycle/permanent income hypothesis. *Quarterly Journal of Economics*, 112(1), 1-55. https://doi.org/10.1162/003355397555109 | Precautionary savings motive |
| 3 | Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73-92. https://doi.org/10.2307/2118511 | Loss aversion in portfolio allocation |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-risk-averse-saver.png) |
| Status | draft |
