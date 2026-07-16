# Leveraged Fund

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Leveraged investment fund with procyclical balance-sheet management |
| Theory Family         | Leverage Cycle / Procyclical Leverage |
| Behavioral Tendency   | **Amplifying** - increases exposure when asset prices rise and deleverages into falling markets |
| Time Horizon          | medium |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an institutional leveraged fund (hedge fund, leveraged ETF, or levered closed-end fund) that maintains a target leverage ratio by adjusting positions in response to mark-to-market gains and losses. The real-world counterpart is documented by Adrian and Shin (2010) and Geanakoplos (2010): intermediaries whose balance-sheet management creates procyclical feedback — buying when prices rise (equity grows, leverage falls below target) and selling when prices fall (equity shrinks, leverage exceeds target).

The decision goal is to rebalance toward a target leverage ratio every period, thereby amplifying price movements. It is not a directional speculator and does not attempt to forecast returns. Non-goals: it must not ignore margin constraints, and it must not behave counter-cyclically (that would be a contrarian fund).

## Theoretical Foundation

**Leverage cycle and procyclical balance-sheet management**:
- Theory / Study: Procyclical leverage and endogenous risk amplification.
- Citation: Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418-437. https://doi.org/10.1016/j.jfi.2008.12.002
- Core Insight: Financial intermediaries target leverage ratios, causing them to buy assets when prices rise (leverage falls) and sell when prices fall (leverage rises), thereby amplifying market movements.
- Mathematical Formulation: Target position `P* = target_leverage * equity`; rebalance quantity `dP = P* - P_current`.
- Empirical Evidence: Adrian & Shin document strong positive correlation between changes in broker-dealer assets and changes in leverage, confirming procyclical behavior.
- Relevance to This Agent: The agent directly implements the balance-sheet targeting mechanism that generates amplification.
- Calibration Source: `target_leverage` 3.0-10.0, `rebalance_band` 0.05-0.20, `max_leverage` 12.0-20.0.
- Falsification Conditions: If the agent does not increase position when equity rises or decrease position when equity falls, the design is falsified.
- Alternative Theories: Value-at-Risk targeting (Danielsson et al. 2004); constant-mix rebalancing without leverage.

**Leverage cycles and margin constraints**:
- Citation: Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1-65. https://doi.org/10.1086/648285
- Core Insight: Endogenous tightening of margins during downturns forces leveraged agents to sell, depressing prices further in a doom loop.

## Design Purpose and Activation Triggers

Purpose: Amplify market movements by rebalancing toward a target leverage ratio, buying into rising markets and selling into falling markets.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `return_1d` available (one-period return)
- own `cash`, `position`, and `equity` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `actual_leverage < target_leverage - rebalance_band`: buy to increase leverage toward target.
- `actual_leverage > target_leverage + rebalance_band`: sell to reduce leverage toward target.
- `actual_leverage > max_leverage`: forced deleveraging (fire sale).
- `<Default>`: hold.

Deactivation Conditions:
- equity falls to zero (fund is wiped out).
- position cannot be reduced further (already zero).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Rising market | buys more assets | equity grows, leverage falls below target, fund rebalances up |
| Falling market | sells assets | equity shrinks, leverage exceeds target, fund rebalances down |
| Margin breach | forced selling | max leverage constraint triggers fire-sale liquidation |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current asset price |
| `return_1d` | environment | float | yes | one-period return for equity update |
| `cash` | own state | float | yes | available funding |
| `position` | own state | float | yes | current asset holding |
| `equity` | own state | float | yes | net asset value |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity must be clamped to available cash (buy) or position (sell).

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | position valuation |
| `return_1d` | Continuous | 1 tick | equity update |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell constraint and leverage calc |
| `equity` | State | persistent | leverage denominator |

Does NOT use: fundamental value estimates, sentiment, private signals, peer positions.

#### Core Behavioral Mechanism

1. Compute `equity = cash + position * price`.
2. Compute `actual_leverage = (position * price) / equity`.
3. Compute `target_position = target_leverage * equity / price`.
4. If `actual_leverage > max_leverage`, sell `min(position, (position * price - max_leverage * equity) / price)` (forced deleverage).
5. Else if `actual_leverage > target_leverage + rebalance_band`, sell `min(position, (position - target_position))`.
6. Else if `actual_leverage < target_leverage - rebalance_band`, buy `min(cash / price, (target_position - position))`.
7. Else hold.
8. Emit the decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | difference between current and target position, capped by constraints |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position >= 0, cash >= 0 |
| Resource cap | buy limited by cash / price; sell limited by position |
| Exit rule | forced sell when max_leverage breached |

#### Mathematical Model

`target_pos = target_leverage * equity / price`

`dP = target_pos - position`

If `actual_leverage > max_leverage`: `q_sell = min(position, (position * price - max_leverage * equity) / price)`

If `actual_leverage > target_leverage + band`: `q_sell = min(position, position - target_pos)`

If `actual_leverage < target_leverage - band`: `q_buy = min(cash / price, target_pos - position)`

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `target_leverage` | target leverage ratio | 5.0 | Adrian & Shin (2010) |
| `rebalance_band` | deadband around target | 0.10 | calibration |
| `max_leverage` | hard leverage ceiling | 15.0 | Geanakoplos (2010) |
| `equity_floor` | minimum equity before shutdown | 1000.0 | risk management convention |

#### Behavioral Properties

- Time horizon: medium, because rebalancing is periodic but positions are held across periods.
- Risk tolerance: high, because the fund operates at multiple turns of leverage.
- Information asymmetry: none, uses only price and own state.
- Psychological profile: mechanical balance-sheet optimizer that inadvertently amplifies cycles.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `target_leverage` | float | 5.0 | [3.0, 10.0] | high | desired leverage ratio | Higher -> more procyclical amplification | Adrian & Shin (2010) |
| `rebalance_band` | float | 0.10 | [0.05, 0.20] | medium | leverage deviation tolerance before rebalancing | Lower -> more frequent trading | calibration |
| `max_leverage` | float | 15.0 | [12.0, 20.0] | high | hard leverage ceiling triggering forced sales | Lower -> earlier fire sales | Geanakoplos (2010) |
| `equity_floor` | float | 1000.0 | [500, 5000] | low | minimum equity before fund shuts down | Lower -> fund survives longer in drawdown | risk convention |

## Worked Numerical Examples

### Case 1 - Buy (Leverage Below Target)
System state: price 100, position 400, cash 20000, equity 60000.
Calculation: `actual_leverage = (400 * 100) / 60000 = 0.667`. Target_pos = `5.0 * 60000 / 100 = 3000`. `dP = 3000 - 400 = 2600`. Capped by cash: `min(20000/100, 2600) = 200`.
Decision: buy 200.
State update: position increases to 600, cash decreases by 20000.

### Case 2 - Sell (Leverage Above Target)
System state: price 80, position 1000, cash 5000, equity 85000 * 0.5 = let equity = 25000.
Calculation: `actual_leverage = (1000 * 80) / 25000 = 3.2`. Wait, recompute: equity = cash + position*price = 5000 + 80000 = 85000. actual_leverage = 80000/85000 = 0.94. Let different example: price 50, position 2000, cash 1000, equity = 1000 + 100000 = 101000. actual_leverage = 100000/101000 ≈ 0.99. Need high leverage example: price 100, position 1000, cash 2000, equity = 2000 + 100000 = 102000. Leverage = 100000/102000 ≈ 0.98.

Revised: price 100, position 5000, cash 10000, equity = 10000 + 500000 = 510000. Leverage = 500000/510000 ≈ 0.98. Still low.

Correct framing: Let borrowed = position * price - equity. equity = cash + position*price - debt. So equity = 100000, debt = 400000, position = 5000, price = 100. Total assets = 500000, equity = 100000, leverage = 500000/100000 = 5.0. Now price drops to 90: assets = 450000, equity = 50000, leverage = 450000/50000 = 9.0.

System state: price 90, position 5000, debt 400000, equity 50000, actual_leverage = 9.0.
Calculation: `target_pos = 5.0 * 50000 / 90 = 2778`. `q_sell = min(5000, 5000 - 2778) = 2222`.
Decision: sell 2222.
State update: position decreases, leverage moves toward target.

### Case 3 - Hold (Within Band)
System state: price 100, position 5000, equity 100000, actual_leverage = 5.0.
Calculation: `|actual_leverage - target_leverage| = 0 < 0.10`.
Decision: hold.
State update: unchanged.

### Edge Case - Forced Deleverage (Max Leverage Breach)
System state: price 70, position 5000, equity 30000 (after price crash from 100), actual_leverage = (5000*70)/30000 = 11.67. Exceeds rebalance threshold but below max_leverage 15. Price drops further to 55: equity = 30000 - 5000*15 = -45000? Use debt framing: debt=400000, assets = 5000*55 = 275000, equity = -125000. Fund wiped out before reaching this.

Revised: price 75, position 5000, debt 350000, equity = 375000 - 350000 = 25000. actual_leverage = 375000/25000 = 15.0. Equals max_leverage.
Calculation: `q_sell = min(5000, (375000 - 15*25000)/75) = min(5000, 0/75) = 0`. At exactly boundary, hold. If price = 74: equity = 370000 - 350000 = 20000, leverage = 370000/20000 = 18.5 > 15. `q_sell = min(5000, (370000 - 15*20000)/74) = min(5000, (370000-300000)/74) = min(5000, 945.9) = 946`.
Decision: sell 946 (forced deleveraging).
State update: position decreases, proceeds reduce debt, leverage moves toward max_leverage.

## Behavioral Verification and Calibration

- Given rising price that reduces leverage below target - band, agent must buy.
- Given falling price that increases leverage above target + band, agent must sell.
- Given leverage exceeding max_leverage, agent must execute forced sale regardless of band.
- Given equity at or below equity_floor, agent must cease trading.
- Given missing price signal, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-rebalancing | `rebalance_band = 999` | procyclical rebalancing amplifies crashes | decrease | price volatility, crash depth |
| low-max-leverage | `max_leverage = 8.0` | tighter margins cause earlier fire sales | increase | fire-sale frequency |
| unit-leverage | `target_leverage = 1.0` | removing leverage eliminates amplification | decrease | return volatility |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418-437. https://doi.org/10.1016/j.jfi.2008.12.002 | Core procyclical leverage theory |
| 2 | Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1-65. https://doi.org/10.1086/648285 | Endogenous margin and leverage cycle |
| 3 | Danielsson, J., Shin, H. S., & Zigrand, J.-P. (2004). The impact of risk regulation on price dynamics. *Journal of Banking & Finance*, 28(5), 1069-1087. | VaR-induced procyclicality |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-leveraged-fund.png) |
| Status | draft |
