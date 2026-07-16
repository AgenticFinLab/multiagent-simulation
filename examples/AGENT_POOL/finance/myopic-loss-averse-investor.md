# Myopic Loss Averse Investor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Investor who evaluates portfolio too frequently and is disproportionately sensitive to losses |
| Theory Family         | Myopic Loss Aversion / Behavioral Finance |
| Behavioral Tendency   | **Underinvesting** - holds less risky assets than rational due to frequent loss evaluation combined with loss aversion |
| Time Horizon          | short (evaluation period) |
| Risk Tolerance        | low (due to loss aversion) |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an investor exhibiting myopic loss aversion (MLA) as described by Benartzi and Thaler (1995): the combination of loss aversion (losses hurt ~2.5x more than equivalent gains) with frequent portfolio evaluation (checking returns monthly rather than annually) causes the investor to perceive equities as riskier than they truly are over long horizons, leading to underinvestment in stocks (helping explain the equity premium puzzle).

The decision goal is to allocate between risky and safe assets based on prospect-theory utility evaluated at the agent's evaluation frequency. The agent sells risky assets when recent evaluated returns are negative (the pain of loss dominates) and cautiously re-enters after sustained positive performance. Non-goals: the agent does not use leverage, does not have private information, and must not behave rationally (i.e., must exhibit the MLA bias).

## Theoretical Foundation

**Myopic loss aversion and the equity premium puzzle**:
- Theory / Study: Myopic loss aversion and the equity premium puzzle.
- Citation: Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73-92. https://doi.org/10.2307/2118511
- Core Insight: An investor with Kahneman-Tversky loss aversion (lambda ≈ 2.5) who evaluates their portfolio every ~1 year would be indifferent between stocks and bonds — explaining why the equity premium must be so high to attract such investors. Shorter evaluation periods make equities even less attractive.
- Mathematical Formulation: Prospect utility `V(x) = x^alpha` if x >= 0; `V(x) = -lambda * (-x)^beta` if x < 0. Agent evaluates `V(R_eval)` where `R_eval` is the return over the evaluation window. Allocates to stocks only if `E[V(R_eval)] > 0`.
- Empirical Evidence: Benartzi & Thaler show that with annual evaluation and lambda=2.25, investors would demand roughly the observed 6% equity premium. Gneezy & Potters (1997) confirm experimentally.
- Relevance to This Agent: The agent implements the MLA investor whose frequent evaluation and loss aversion cause systematic underinvestment in equities.
- Calibration Source: `evaluation_period` 10-30 ticks, `loss_aversion` 2.0-3.0, `alpha` 0.80-0.95.
- Falsification Conditions: If the agent does not reduce equity allocation after experiencing losses within the evaluation window, the design is falsified.
- Alternative Theories: Rational expected-utility investor (no loss aversion); habit-formation preferences (Campbell & Cochrane 1999).

## Design Purpose and Activation Triggers

Purpose: Demonstrate how the interaction of loss aversion and frequent evaluation creates equity underinvestment, generating the demand side of the equity premium puzzle.

Call Frequency: every evaluation period (every `evaluation_period` ticks).

Prerequisite Signals:
- `price` available
- `price_at_last_eval` available (price at start of evaluation window)
- own `cash`, `position`, and `portfolio_value` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- End of evaluation period AND `eval_return < 0`: sell risky assets (loss aversion pain).
- End of evaluation period AND `eval_return > re_entry_threshold`: buy risky assets (cautious re-entry).
- End of evaluation period AND `0 <= eval_return <= re_entry_threshold`: hold (insufficient gain to overcome fear).
- `<Default>`: hold (not at evaluation point).

Deactivation Conditions:
- position already zero (fully de-risked after loss).
- cash exhausted (fully invested).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Loss in evaluation window | sells risky assets | loss aversion dominates, pain of loss |
| Small gain in evaluation window | holds | gain insufficient to overcome loss-aversion threshold |
| Large gain in evaluation window | buys cautiously | positive experience encourages re-entry |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current price |
| `price_at_last_eval` | own state | float | yes | price at start of evaluation window |
| `cash` | own state | float | yes | safe-asset holding |
| `position` | own state | float | yes | risky-asset holding |
| `portfolio_value` | own state | float | yes | total wealth |
| `tick_count` | environment | int | yes | evaluation timing |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Sell quantity driven by loss-aversion-weighted evaluation. Buy quantity limited by cautious re-entry sizing.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current valuation |
| `price_at_last_eval` | State | evaluation_period ticks | return calculation |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell capacity |
| `portfolio_value` | State | persistent | allocation reference |
| `tick_count` | Discrete | 1 tick | evaluation timing |

Does NOT use: fundamental value, market sentiment, peer behavior, leverage.

#### Core Behavioral Mechanism

1. Check if at evaluation point: `tick_count % evaluation_period == 0`. If not, hold.
2. Compute `eval_return = (price - price_at_last_eval) / price_at_last_eval`.
3. Compute prospect value: if `eval_return >= 0`: `V = eval_return^alpha`; if `eval_return < 0`: `V = -loss_aversion * (-eval_return)^beta`.
4. If `V < 0` (loss domain): sell `position * sell_fraction` (flee from risky asset).
5. If `V > gain_threshold` (strong gain): buy `cash * buy_fraction / price` (cautious re-entry).
6. Otherwise hold.
7. Update `price_at_last_eval = price`. Emit decision.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | fraction of position (sell) or fraction of cash (buy) |
| Action lifetime | one evaluation period |
| Revision policy | re-evaluate at next evaluation point |
| State constraint | position >= 0, cash >= 0, no leverage |
| Resource cap | sell limited by position, buy limited by cash/price |
| Exit rule | sell when prospect value is negative |

#### Mathematical Model

`R = (price - price_eval) / price_eval`

`V(R) = R^alpha` if R >= 0; `V(R) = -lambda * (-R)^beta` if R < 0

Sell: `q_sell = position * sell_fraction` when `V < 0`

Buy: `q_buy = cash * buy_fraction / price` when `V > gain_threshold`

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `evaluation_period` | ticks between evaluations | 20 | Benartzi & Thaler (1995) |
| `loss_aversion` | loss aversion coefficient (lambda) | 2.25 | Kahneman & Tversky (1992) |
| `alpha` | diminishing sensitivity for gains | 0.88 | Tversky & Kahneman (1992) |
| `beta` | diminishing sensitivity for losses | 0.88 | Tversky & Kahneman (1992) |
| `sell_fraction` | fraction of position sold on loss | 0.50 | calibration |
| `buy_fraction` | fraction of cash used on re-entry | 0.20 | calibration |
| `gain_threshold` | prospect value threshold for re-entry | 0.03 | calibration |

#### Behavioral Properties

- Time horizon: short (evaluation period), despite potentially long real horizon.
- Risk tolerance: low, because loss aversion makes losses disproportionately painful.
- Information asymmetry: none.
- Psychological profile: loss-averse, myopic evaluator, cautious, prone to selling after losses.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `evaluation_period` | int | 20 | [10, 30] | high | ticks between portfolio evaluations | Shorter -> more MLA effect, lower equity holding | Benartzi & Thaler (1995) |
| `loss_aversion` | float | 2.25 | [2.0, 3.0] | high | how much worse losses feel vs equivalent gains | Higher -> more selling on losses | Kahneman & Tversky (1992) |
| `alpha` | float | 0.88 | [0.80, 0.95] | low | diminishing sensitivity exponent | Lower -> more concavity in gains | Tversky & Kahneman (1992) |
| `sell_fraction` | float | 0.50 | [0.20, 0.80] | high | fraction of risky position sold after loss evaluation | Higher -> faster de-risking | calibration |
| `buy_fraction` | float | 0.20 | [0.10, 0.40] | medium | fraction of cash invested on positive evaluation | Higher -> faster re-entry | calibration |

## Worked Numerical Examples

### Case 1 - Sell After Loss
System state: price 95, price_at_last_eval 100, position 1000, tick at evaluation point.
Calculation: `R = (95-100)/100 = -0.05`. `V = -2.25 * (0.05)^0.88 = -2.25 * 0.063 = -0.142`. V < 0.
`q_sell = 1000 * 0.50 = 500`.
Decision: sell 500.
State update: position decreases to 500, cash increases.

### Case 2 - Buy After Strong Gain
System state: price 112, price_at_last_eval 100, cash 50000, tick at evaluation point.
Calculation: `R = 0.12`. `V = (0.12)^0.88 = 0.137`. V > 0.03.
`q_buy = 50000 * 0.20 / 112 = 89`.
Decision: buy 89.
State update: position increases, cash decreases.

### Case 3 - Hold (Small Gain, Below Threshold)
System state: price 101, price_at_last_eval 100, tick at evaluation point.
Calculation: `R = 0.01`. `V = (0.01)^0.88 = 0.013`. V > 0 but < 0.03.
Decision: hold.
State update: unchanged; reset evaluation reference.

### Edge Case - Not at Evaluation Point
System state: price 80 (sharp crash), tick_count not divisible by evaluation_period.
Calculation: not at evaluation point.
Decision: hold (myopic — does not react between evaluations).
State update: unchanged; the loss is only "realized" psychologically at next evaluation.

## Behavioral Verification and Calibration

- At evaluation point with negative return, agent must sell risky assets.
- At evaluation point with return above gain_threshold, agent must buy cautiously.
- Between evaluation points, agent must hold regardless of price movement.
- Agent must never use leverage.
- Sell quantity must be proportional to sell_fraction, not the size of the loss.
- Given missing price_at_last_eval, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-loss-aversion | `loss_aversion = 1.0` | loss aversion drives equity underinvestment | increase | average equity allocation |
| long-evaluation | `evaluation_period = 100` | less frequent evaluation reduces MLA | increase | average equity allocation |
| high-aversion | `loss_aversion = 3.0` | stronger aversion reduces equity more | decrease | average equity allocation |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73-92. https://doi.org/10.2307/2118511 | Core MLA theory |
| 2 | Tversky, A., & Kahneman, D. (1992). Advances in prospect theory: Cumulative representation of uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297-323. https://doi.org/10.1007/BF00122574 | Prospect theory parameters |
| 3 | Gneezy, U., & Potters, J. (1997). An experiment on risk taking and evaluation periods. *Quarterly Journal of Economics*, 112(2), 631-645. https://doi.org/10.1162/003355397555217 | Experimental confirmation of MLA |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-myopic-loss-averse-investor.png) |
| Status | draft |
