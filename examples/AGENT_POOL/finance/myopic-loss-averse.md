# Myopic Loss Averse

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Extremely short-evaluation-window loss-averse agent with amplified behavioral bias |
| Theory Family         | Myopic Loss Aversion / Behavioral Finance (extreme variant) |
| Behavioral Tendency   | **Destabilising** - rapid selling on small losses creates excess volatility and liquidity withdrawal |
| Time Horizon          | very short (evaluation period) |
| Risk Tolerance        | very low (heightened loss aversion) |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent is a more extreme variant of the myopic loss averse investor archetype, modeled with a very short evaluation window (daily/weekly equivalent rather than monthly) and stronger loss aversion weighting (lambda ≈ 3.0). This represents the retail day-trader or anxious saver who checks their portfolio constantly and reacts with panic to even small paper losses. The shortened evaluation horizon dramatically increases the frequency of loss-domain evaluations (since daily returns are negative roughly 45% of the time), causing near-permanent underinvestment and frequent whipsaw selling.

The decision goal is identical in mechanism to the MLA investor but with parameters calibrated to produce more extreme and frequent behavioral responses — rapid de-risking on any negative evaluation and very slow re-entry. Non-goals: the agent does not use leverage, does not have private information, and must exhibit amplified MLA bias relative to the standard variant.

## Theoretical Foundation

**Myopic loss aversion with very short evaluation period**:
- Theory / Study: Myopic loss aversion and the equity premium puzzle.
- Citation: Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73-92. https://doi.org/10.2307/2118511
- Core Insight: The MLA effect is strictly increasing in evaluation frequency. An investor checking daily rather than annually will demand an even higher equity premium and hold even less equity, because the probability of observing a loss increases sharply at shorter horizons.
- Mathematical Formulation: Same prospect utility `V(R) = R^alpha` for R>=0, `V(R) = -lambda*(-R)^beta` for R<0, but evaluated over a much shorter window (5 ticks vs 20). With daily evaluation, P(loss) ≈ 0.45 vs P(loss) ≈ 0.30 for annual.
- Empirical Evidence: Gneezy & Potters (1997) and Haigh & List (2005) show experimentally that more frequent feedback causes lower risky-asset investment.
- Relevance to This Agent: The agent pushes MLA to its behavioral extreme, showing how very frequent evaluation combined with strong loss aversion creates persistent equity aversion and excess selling.
- Calibration Source: `evaluation_period` 3-8 ticks, `loss_aversion` 2.5-3.5, `sell_fraction` 0.60-0.90.
- Falsification Conditions: If the agent does not sell more frequently than the standard MLA investor, or holds higher equity allocation, the design is falsified.
- Alternative Theories: Standard MLA investor (Benartzi & Thaler with annual evaluation); rational short-horizon trader.

**Experimental evidence on evaluation frequency**:
- Citation: Haigh, M. S., & List, J. A. (2005). Do professional traders exhibit myopic loss aversion? An experimental analysis. *Journal of Finance*, 60(1), 523-534. https://doi.org/10.1111/j.1540-6261.2005.00737.x
- Core Insight: Even professional traders exhibit MLA — more frequent feedback reduces their risky-asset allocation, confirming that the bias is robust across sophistication levels.

## Design Purpose and Activation Triggers

Purpose: Demonstrate the extreme end of MLA behavior where very frequent evaluation creates constant selling pressure, excess volatility, and persistent equity underinvestment.

Call Frequency: every evaluation period (every `evaluation_period` ticks, where period is very short).

Prerequisite Signals:
- `price` available
- `price_at_last_eval` available (price at start of evaluation window)
- own `cash`, `position`, and `portfolio_value` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- End of evaluation period AND `eval_return < 0`: sell large fraction of risky assets (amplified loss aversion).
- End of evaluation period AND `eval_return > re_entry_threshold`: buy very small amount (extreme caution on re-entry).
- End of evaluation period AND `0 <= eval_return <= re_entry_threshold`: hold.
- `<Default>`: hold (not at evaluation point).

Deactivation Conditions:
- position already zero.
- cash exhausted (rarely reached given extreme caution).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Any loss in short window | sells large fraction immediately | amplified loss aversion pain |
| Small gain in short window | holds | gain insufficient to overcome elevated threshold |
| Large gain over multiple windows | buys tiny amount | extreme caution, slow re-entry |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current price |
| `price_at_last_eval` | own state | float | yes | price at start of short evaluation window |
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

Required fields are `action`, `quantity`, and `reasoning`. Sell quantity is large fraction on any loss. Buy quantity is very small and cautious.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current valuation |
| `price_at_last_eval` | State | evaluation_period ticks (very short) | return calculation |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell capacity |
| `portfolio_value` | State | persistent | allocation reference |
| `tick_count` | Discrete | 1 tick | evaluation timing |

Does NOT use: fundamental value, market sentiment, peer behavior, leverage.

#### Core Behavioral Mechanism

1. Check if at evaluation point: `tick_count % evaluation_period == 0`. If not, hold.
2. Compute `eval_return = (price - price_at_last_eval) / price_at_last_eval`.
3. Compute prospect value: if `eval_return >= 0`: `V = eval_return^alpha`; if `eval_return < 0`: `V = -loss_aversion * (-eval_return)^beta`.
4. If `V < 0` (loss domain): sell `position * sell_fraction` (large, immediate de-risking).
5. If `V > gain_threshold` (strong gain): buy `cash * buy_fraction / price` (very small, cautious).
6. Otherwise hold.
7. Update `price_at_last_eval = price`. Emit decision.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | large sell fraction on loss; tiny buy fraction on gain |
| Action lifetime | one evaluation period (very short) |
| Revision policy | re-evaluate every few ticks |
| State constraint | position >= 0, cash >= 0, no leverage |
| Resource cap | sell limited by position, buy limited by cash/price |
| Exit rule | sell on any negative evaluation |

#### Mathematical Model

`R = (price - price_eval) / price_eval`

`V(R) = R^alpha` if R >= 0; `V(R) = -lambda * (-R)^beta` if R < 0

Sell: `q_sell = position * sell_fraction` when `V < 0`

Buy: `q_buy = cash * buy_fraction / price` when `V > gain_threshold`

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `evaluation_period` | ticks between evaluations (very short) | 5 | Gneezy & Potters (1997), extreme calibration |
| `loss_aversion` | loss aversion coefficient (lambda) | 3.00 | amplified from Tversky & Kahneman (1992) |
| `alpha` | diminishing sensitivity for gains | 0.88 | Tversky & Kahneman (1992) |
| `beta` | diminishing sensitivity for losses | 0.88 | Tversky & Kahneman (1992) |
| `sell_fraction` | fraction of position sold on loss | 0.70 | calibration (extreme) |
| `buy_fraction` | fraction of cash used on re-entry | 0.05 | calibration (very cautious) |
| `gain_threshold` | prospect value threshold for re-entry | 0.05 | calibration (higher than standard) |

#### Behavioral Properties

- Time horizon: very short, evaluates every few ticks.
- Risk tolerance: very low, heightened loss aversion dominates all decisions.
- Information asymmetry: none.
- Psychological profile: anxious, hyper-reactive to losses, extremely cautious about re-entry, generates excess selling.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `evaluation_period` | int | 5 | [3, 8] | high | ticks between evaluations (very short) | Shorter -> more frequent loss observations | Gneezy & Potters (1997) |
| `loss_aversion` | float | 3.00 | [2.5, 3.5] | high | amplified loss aversion coefficient | Higher -> more aggressive selling | amplified Kahneman & Tversky (1992) |
| `sell_fraction` | float | 0.70 | [0.60, 0.90] | high | fraction sold on negative evaluation | Higher -> faster de-risking | calibration |
| `buy_fraction` | float | 0.05 | [0.02, 0.10] | medium | fraction of cash invested on positive evaluation | Lower -> slower re-entry | calibration |
| `gain_threshold` | float | 0.05 | [0.03, 0.08] | medium | minimum prospect value for re-entry | Higher -> rarer buying | calibration |

## Worked Numerical Examples

### Case 1 - Sell After Tiny Loss (Frequent Evaluation)
System state: price 99.5, price_at_last_eval 100, position 1000, tick at evaluation point.
Calculation: `R = -0.005`. `V = -3.0 * (0.005)^0.88 = -3.0 * 0.0072 = -0.022`. V < 0.
`q_sell = 1000 * 0.70 = 700`.
Decision: sell 700.
State update: position decreases to 300.

### Case 2 - Hold (Small Gain Below Threshold)
System state: price 101, price_at_last_eval 100, tick at evaluation point.
Calculation: `R = 0.01`. `V = (0.01)^0.88 = 0.013`. V > 0 but < 0.05.
Decision: hold.
State update: unchanged.

### Case 3 - Tiny Buy After Strong Gain
System state: price 108, price_at_last_eval 100, cash 100000, tick at evaluation point.
Calculation: `R = 0.08`. `V = (0.08)^0.88 = 0.098`. V > 0.05.
`q_buy = 100000 * 0.05 / 108 = 46`.
Decision: buy 46.
State update: small cautious re-entry.

### Edge Case - Position Already Zero
System state: price 98, price_at_last_eval 100, position 0, tick at evaluation point.
Calculation: `R = -0.02`. V < 0. But `q_sell = 0 * 0.70 = 0`.
Decision: hold (nothing to sell).
State update: remains fully de-risked; cannot act on loss aversion.

## Behavioral Verification and Calibration

- At evaluation point with any negative return, agent must sell large fraction.
- Agent must sell more frequently than standard MLA investor (shorter evaluation window).
- Agent's average equity allocation must be lower than standard MLA investor.
- Re-entry must be very slow (small buy_fraction, high gain_threshold).
- Between evaluation points, agent must hold regardless of price movement.
- Agent must never use leverage.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| standard-eval-period | `evaluation_period = 20` | shorter window amplifies MLA | decrease | sell frequency |
| standard-aversion | `loss_aversion = 2.25` | higher lambda amplifies de-risking | decrease | sell volume |
| fast-reentry | `buy_fraction = 0.30` | slow re-entry keeps equity low | increase | average equity allocation |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73-92. https://doi.org/10.2307/2118511 | Core MLA theory |
| 2 | Gneezy, U., & Potters, J. (1997). An experiment on risk taking and evaluation periods. *Quarterly Journal of Economics*, 112(2), 631-645. https://doi.org/10.1162/003355397555217 | Experimental evidence: frequent feedback reduces risk-taking |
| 3 | Haigh, M. S., & List, J. A. (2005). Do professional traders exhibit myopic loss aversion? *Journal of Finance*, 60(1), 523-534. https://doi.org/10.1111/j.1540-6261.2005.00737.x | MLA in professional traders |
| 4 | Tversky, A., & Kahneman, D. (1992). Advances in prospect theory. *Journal of Risk and Uncertainty*, 5(4), 297-323. https://doi.org/10.1007/BF00122574 | Prospect theory parameters |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-myopic-loss-averse.png) |
| Status | draft |
