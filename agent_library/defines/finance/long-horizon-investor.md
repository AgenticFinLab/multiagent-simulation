# Long Horizon Investor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Patient strategic investor with multi-year horizon exploiting short-term noise |
| Theory Family         | Strategic Asset Allocation / Time Diversification |
| Behavioral Tendency   | **Stabilising** - buys during temporary dislocations and holds through volatility, providing a stabilising anchor |
| Time Horizon          | long |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a long-horizon institutional investor (endowment, sovereign wealth fund, or pension plan) that exploits the mean-reverting component of asset returns by maintaining strategic allocations and rebalancing into dislocations. The real-world counterpart is documented by Campbell and Viceira (2002): investors with multi-period horizons can tolerate short-term volatility because mean reversion reduces long-horizon variance, enabling them to hold riskier portfolios than myopic investors.

The decision goal is to maintain a target allocation to risky assets and opportunistically increase exposure when prices deviate significantly below fundamental value (perceived mispricing). Non-goals: the agent does not chase momentum, does not use leverage, and does not trade frequently.

## Theoretical Foundation

**Strategic asset allocation for long-horizon investors**:
- Theory / Study: Strategic asset allocation.
- Citation: Campbell, J. Y., & Viceira, L. M. (2002). *Strategic Asset Allocation: Portfolio Choice for Long-Term Investors*. Oxford University Press. https://doi.org/10.1093/0198296940.001.0001
- Core Insight: When returns are mean-reverting, long-horizon investors optimally hold more risky assets than myopic investors because time diversification reduces effective risk.
- Mathematical Formulation: Target weight `w* = (mu - r) / (gamma * sigma^2) + hedging_demand`. Rebalance when `|w_actual - w*| > rebalance_threshold`.
- Empirical Evidence: Campbell & Viceira show that horizon-dependent optimal portfolios have higher equity allocations for long horizons under mean reversion.
- Relevance to This Agent: The agent implements the patient rebalancer who buys dips and sells rallies, anchoring prices toward fundamentals.
- Calibration Source: `target_weight` 0.60-0.80, `rebalance_threshold` 0.05-0.15, `mean_reversion_belief` 0.10-0.30.
- Falsification Conditions: If the agent trades at high frequency or chases momentum rather than reverting to target, the design is falsified.
- Alternative Theories: Myopic portfolio choice (no mean-reversion belief); constant-proportion portfolio insurance (CPPI).

## Design Purpose and Activation Triggers

Purpose: Provide a stabilising force by buying into market dips and selling into market rallies, anchoring prices toward fundamental value through patient rebalancing.

Call Frequency: low-frequency (every N ticks, simulating quarterly or annual rebalancing).

Prerequisite Signals:
- `price` available
- `fundamental_value` available (or long-run moving average as proxy)
- own `cash`, `position`, and `portfolio_value` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `actual_weight < target_weight - rebalance_threshold`: buy to rebalance toward target.
- `actual_weight > target_weight + rebalance_threshold`: sell to rebalance toward target.
- `price / fundamental_value < discount_threshold`: opportunistic buy (larger than normal rebalance).
- `<Default>`: hold.

Deactivation Conditions:
- portfolio already at target weight within threshold band.
- no rebalancing event scheduled this period.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Market crash | buys more aggressively | mean-reversion belief implies higher expected return |
| Market rally | trims position | overweight triggers rebalance sell |
| Normal conditions | holds steady | within rebalancing band |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `fundamental_value` | environment | float | yes | long-run value anchor |
| `cash` | own state | float | yes | buy capacity |
| `position` | own state | float | yes | current risky-asset holding |
| `portfolio_value` | own state | float | yes | total wealth (cash + position * price) |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity reflects rebalancing need, capped by cash or position.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current valuation |
| `fundamental_value` | Continuous | persistent | mean-reversion anchor |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | current allocation |
| `portfolio_value` | State | persistent | weight denominator |

Does NOT use: short-term momentum, sentiment, leverage, order flow.

#### Core Behavioral Mechanism

1. Compute `actual_weight = (position * price) / portfolio_value`.
2. If `actual_weight < target_weight - rebalance_threshold`:
   a. Compute `target_position = target_weight * portfolio_value / price`.
   b. `q_buy = min(cash / price, target_position - position)`.
   c. If `price / fundamental_value < discount_threshold`: scale q_buy by `opportunistic_multiplier`.
3. If `actual_weight > target_weight + rebalance_threshold`:
   a. `q_sell = min(position, position - target_weight * portfolio_value / price)`.
4. Else hold.
5. Emit decision.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | difference between current and target allocation |
| Action lifetime | one rebalancing period |
| Revision policy | re-evaluate each rebalancing period |
| State constraint | position >= 0, no leverage |
| Resource cap | buy limited by cash/price, sell limited by position |
| Exit rule | none — perpetual investor |

#### Mathematical Model

`w_actual = (position * price) / (cash + position * price)`

`target_pos = target_weight * portfolio_value / price`

`q = |target_pos - position|`, capped by constraints

If `price / fundamental_value < discount_threshold`: `q = q * opportunistic_multiplier`

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `target_weight` | target allocation to risky asset | 0.70 | Campbell & Viceira (2002) |
| `rebalance_threshold` | deadband for rebalancing trigger | 0.10 | calibration |
| `discount_threshold` | price/fundamental ratio for opportunistic buy | 0.85 | calibration |
| `opportunistic_multiplier` | scaling factor for discounted buys | 1.5 | calibration |
| `mean_reversion_belief` | subjective mean-reversion speed | 0.20 | Campbell & Viceira (2002) |

#### Behavioral Properties

- Time horizon: long, because the agent rebalances infrequently and holds for years.
- Risk tolerance: medium, because allocation is strategic, not speculative.
- Information asymmetry: none, uses only public price and fundamental estimate.
- Psychological profile: patient, disciplined, contrarian during stress.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `target_weight` | float | 0.70 | [0.60, 0.80] | medium | target allocation to risky asset | Higher -> more equity exposure | Campbell & Viceira (2002) |
| `rebalance_threshold` | float | 0.10 | [0.05, 0.15] | medium | minimum deviation to trigger rebalancing | Lower -> more frequent rebalancing | calibration |
| `discount_threshold` | float | 0.85 | [0.75, 0.95] | high | price/fundamental ratio for opportunistic buying | Lower -> only buys deeper dips | calibration |
| `opportunistic_multiplier` | float | 1.5 | [1.0, 3.0] | medium | scale factor for discount buys | Higher -> more aggressive dip buying | calibration |
| `mean_reversion_belief` | float | 0.20 | [0.10, 0.30] | low | subjective speed of mean reversion | Higher -> more confidence in reversion | Campbell & Viceira (2002) |

## Worked Numerical Examples

### Case 1 - Rebalance Buy (Underweight After Crash)
System state: price 80, fundamental_value 100, position 500, cash 60000, portfolio_value = 60000 + 500*80 = 100000.
Calculation: `actual_weight = 40000/100000 = 0.40`. Target_pos = `0.70 * 100000 / 80 = 875`. `q = min(60000/80, 875 - 500) = min(750, 375) = 375`. Price/FV = 0.80 < 0.85, so `q = 375 * 1.5 = 562.5 -> 562`. Capped: `min(750, 562) = 562`.
Decision: buy 562.
State update: position increases to 1062, cash decreases.

### Case 2 - Rebalance Sell (Overweight After Rally)
System state: price 150, position 800, cash 20000, portfolio_value = 20000 + 800*150 = 140000.
Calculation: `actual_weight = 120000/140000 = 0.857`. Target_pos = `0.70 * 140000 / 150 = 653`. `q_sell = min(800, 800 - 653) = 147`.
Decision: sell 147.
State update: position decreases, cash increases.

### Case 3 - Hold (Within Band)
System state: price 100, position 700, cash 30000, portfolio_value = 100000.
Calculation: `actual_weight = 70000/100000 = 0.70`. `|0.70 - 0.70| = 0 < 0.10`.
Decision: hold.
State update: unchanged.

### Edge Case - Deep Discount With Limited Cash
System state: price 50, fundamental_value 100, position 200, cash 5000, portfolio_value = 15000.
Calculation: `actual_weight = 10000/15000 = 0.667`. Target_pos = `0.70 * 15000 / 50 = 210`. `q = 10`. Price/FV = 0.50 < 0.85, `q = 10 * 1.5 = 15`. Capped: `min(5000/50, 15) = min(100, 15) = 15`.
Decision: buy 15.
State update: small opportunistic purchase limited by cash.

## Behavioral Verification and Calibration

- Given actual_weight below target - threshold, agent must buy.
- Given actual_weight above target + threshold, agent must sell.
- Given price significantly below fundamental, agent must buy more aggressively (opportunistic multiplier).
- Agent must never trade within the rebalance band.
- Agent must never use leverage.
- Given missing fundamental_value, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-rebalancing | `rebalance_threshold = 999` | rebalancing stabilises prices | increase | price volatility |
| no-opportunistic | `opportunistic_multiplier = 1.0` | aggressive dip-buying dampens crashes | increase | max drawdown |
| myopic-weight | `target_weight = 0.40` | lower allocation reduces stabilisation | increase | crash depth |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Campbell, J. Y., & Viceira, L. M. (2002). *Strategic Asset Allocation*. Oxford University Press. https://doi.org/10.1093/0198296940.001.0001 | Core strategic allocation theory |
| 2 | Barberis, N. (2000). Investing for the long run when returns are predictable. *Journal of Finance*, 55(1), 225-264. https://doi.org/10.1111/0022-1082.00205 | Long-horizon portfolio choice under predictability |
| 3 | Campbell, J. Y., & Shiller, R. J. (1988). The dividend-price ratio and expectations of future dividends and discount factors. *Review of Financial Studies*, 1(3), 195-228. | Mean reversion in stock prices |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-long-horizon-investor.png) |
| Status | draft |
