# Long Term Investor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Buy-and-hold fundamentalist with minimal turnover |
| Theory Family         | Passive Investing Efficiency / Transaction Cost Minimization |
| Behavioral Tendency   | **Stabilising** - absorbs selling pressure during downturns by not selling, and does not chase rallies |
| Time Horizon          | very long |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a long-term buy-and-hold investor (index fund, retirement saver, or Warren Buffett archetype) who acquires assets at a steady rate and rarely sells. The real-world counterpart is grounded in Sharpe (1991): the average actively managed dollar must underperform the average passively managed dollar after costs, making low-turnover investing the rational default for uninformed investors.

The decision goal is to steadily accumulate a position over time with minimal trading and hold indefinitely, only selling under extreme duress or when a hard valuation ceiling is hit. Non-goals: the agent does not time the market, does not use leverage, and does not react to short-term price movements.

## Theoretical Foundation

**Arithmetic of active management and passive superiority**:
- Theory / Study: The arithmetic of active management.
- Citation: Sharpe, W. F. (1991). The arithmetic of active management. *Financial Analysts Journal*, 47(1), 7-9. https://doi.org/10.2469/faj.v47.n1.7
- Core Insight: Before costs, the return on the average actively managed dollar equals the return on the average passively managed dollar. After costs, passive wins. Low turnover minimizes transaction costs and tax drag.
- Mathematical Formulation: `q_buy = periodic_investment / price` each investment period. Sell only if `price / entry_price > sell_ceiling` or forced.
- Empirical Evidence: Decades of S&P SPIVA reports show majority of active funds underperform passive benchmarks after fees.
- Relevance to This Agent: The agent embodies the passive, low-turnover approach that serves as a stabilising anchor.
- Calibration Source: `periodic_investment` 1000-10000, `investment_interval` 10-50 ticks, `sell_ceiling` 3.0-10.0.
- Falsification Conditions: If the agent trades frequently or reacts to short-term signals, the design is falsified.
- Alternative Theories: Active value investing (Graham & Dodd); factor-based smart beta.

**Transaction cost economics**:
- Citation: Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. *Journal of Finance*, 55(2), 773-806. https://doi.org/10.1111/0022-1082.00226
- Core Insight: Individual investors who trade more earn lower returns due to transaction costs and behavioral errors.

## Design Purpose and Activation Triggers

Purpose: Demonstrate the stabilising and wealth-accumulating effect of patient, low-turnover investing that resists panic selling and momentum chasing.

Call Frequency: periodic (every `investment_interval` ticks).

Prerequisite Signals:
- `price` available
- `tick_count` or period marker available
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `tick_count % investment_interval == 0` AND `cash >= periodic_investment`: buy (dollar-cost averaging).
- `price / avg_entry_price > sell_ceiling`: sell small fraction (profit-taking at extreme overvaluation only).
- `<Default>`: hold.

Deactivation Conditions:
- cash exhausted (no more periodic investments possible).
- simulation ends.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Investment period arrives | buys fixed dollar amount | dollar-cost averaging |
| Extreme overvaluation | sells small fraction | hard ceiling profit-taking |
| Market crash | continues holding | does not panic sell |
| Between investment periods | holds | no action |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price |
| `tick_count` | environment | int | yes | current simulation tick |
| `cash` | own state | float | yes | available funds for investment |
| `position` | own state | float | yes | accumulated holdings |
| `avg_entry_price` | own state | float | yes | average cost basis |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Buy quantity is fixed periodic amount. Sell is rare and small.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `tick_count` | Discrete | 1 tick | investment timing |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | accumulated holding |
| `avg_entry_price` | State | persistent | cost basis for sell ceiling |

Does NOT use: momentum, sentiment, volatility, fundamental models, leverage.

#### Core Behavioral Mechanism

1. If not on investment period (`tick_count % investment_interval != 0`), check sell ceiling.
2. If `price / avg_entry_price > sell_ceiling` and position > 0: sell `position * sell_fraction`.
3. If on investment period and `cash >= periodic_investment`: buy `periodic_investment / price` units.
4. Otherwise hold.
5. Emit decision.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | fixed dollar amount for buy; small fraction for rare sells |
| Action lifetime | one decision call |
| Revision policy | next decision at next investment period |
| State constraint | position >= 0, cash >= 0, no leverage |
| Resource cap | buy limited by periodic_investment and cash |
| Exit rule | sell only at extreme overvaluation ceiling |

#### Mathematical Model

`q_buy = periodic_investment / price` when on investment period

`q_sell = position * sell_fraction` when `price / avg_entry_price > sell_ceiling`

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `periodic_investment` | dollar amount per investment period | 5000.0 | calibration |
| `investment_interval` | ticks between investments | 20 | calibration (quarterly proxy) |
| `sell_ceiling` | price/cost ratio triggering profit-taking | 5.0 | calibration |
| `sell_fraction` | fraction of position sold at ceiling | 0.10 | calibration |

#### Behavioral Properties

- Time horizon: very long, because the agent holds indefinitely.
- Risk tolerance: low, because the agent avoids active risk-taking.
- Information asymmetry: none, no private information.
- Psychological profile: patient, unemotional, disciplined accumulator.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `periodic_investment` | float | 5000.0 | [1000, 10000] | medium | dollar amount invested each period | Higher -> faster accumulation | calibration |
| `investment_interval` | int | 20 | [10, 50] | low | ticks between investment events | Higher -> less frequent buying | calibration |
| `sell_ceiling` | float | 5.0 | [3.0, 10.0] | low | price/cost multiple triggering sell | Higher -> rarer profit-taking | calibration |
| `sell_fraction` | float | 0.10 | [0.05, 0.25] | low | fraction of position sold at ceiling | Higher -> larger profit-taking | calibration |

## Worked Numerical Examples

### Case 1 - Periodic Buy
System state: price 100, tick_count 20 (== investment_interval), cash 500000.
Calculation: `q = 5000 / 100 = 50`.
Decision: buy 50.
State update: position increases by 50, cash decreases by 5000.

### Case 2 - Hold (Not Investment Period)
System state: price 110, tick_count 15, cash 500000.
Calculation: not on investment period, price/avg_entry < sell_ceiling.
Decision: hold.
State update: unchanged.

### Case 3 - Hold During Crash
System state: price 50 (crash from 100), tick_count 13, position 500.
Calculation: not on investment period; no panic sell rule exists.
Decision: hold.
State update: unchanged (paper loss, no action).

### Edge Case - Sell at Extreme Overvaluation
System state: price 600, avg_entry_price 100, position 1000, tick_count 25.
Calculation: `price / avg_entry = 6.0 > 5.0 = sell_ceiling`. `q_sell = 1000 * 0.10 = 100`.
Decision: sell 100.
State update: position decreases by 100.

## Behavioral Verification and Calibration

- On investment period with sufficient cash, agent must buy fixed dollar amount.
- Between investment periods, agent must hold unless sell ceiling is breached.
- During market crashes, agent must not sell (no panic selling).
- Given price/cost > sell_ceiling, agent must sell small fraction.
- Agent must never use leverage or short-sell.
- Given missing price, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-DCA | `investment_interval = 999` | periodic buying stabilises prices | increase | price volatility |
| panic-enabled | add panic sell rule | calm holding prevents crash amplification | increase | crash depth |
| aggressive-profit | `sell_ceiling = 2.0` | low ceiling causes more selling, less stabilisation | increase | price volatility |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Sharpe, W. F. (1991). The arithmetic of active management. *Financial Analysts Journal*, 47(1), 7-9. https://doi.org/10.2469/faj.v47.n1.7 | Core passive investing argument |
| 2 | Barber, B. M., & Odean, T. (2000). Trading is hazardous to your wealth. *Journal of Finance*, 55(2), 773-806. https://doi.org/10.1111/0022-1082.00226 | Transaction cost harm from overtrading |
| 3 | Fama, E. F., & French, K. R. (2010). Luck versus skill in the cross-section of mutual fund returns. *Journal of Finance*, 65(5), 1915-1947. | Active management underperformance |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-long-term-investor.png) |
| Status | draft |
