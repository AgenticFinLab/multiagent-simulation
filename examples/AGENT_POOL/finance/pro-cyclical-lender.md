# Pro-Cyclical Lender

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Lender who expands credit in booms and contracts in busts |
| Theory Family         | Pro-cyclical Leverage / Financial Accelerator |
| Behavioral Tendency   | **Amplifying** - expands lending in booms and contracts in busts, reinforcing the cycle |
| Time Horizon          | medium |
| Risk Tolerance        | variable (high in booms, low in busts) |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a bank or financial intermediary whose lending behavior is pro-cyclical: it expands credit when asset prices rise (improving collateral values and measured risk) and contracts credit when prices fall (deteriorating balance sheets and rising measured risk). The real-world counterpart is the leveraged financial intermediary documented by Adrian and Shin (2010) and the financial accelerator of Bernanke, Gertler, and Gilchrist (1999).

The decision goal is to adjust credit supply (modeled as buy/sell of a credit asset) in proportion to the credit cycle indicator. It is not a central bank and it does not set policy rates. Non-goals: it must not lend counter-cyclically (that would be a macro-prudential stabilizer), and it must not ignore its own capital constraint.

## Theoretical Foundation

**Pro-cyclical leverage and the financial accelerator**:
- Theory / Study: Liquidity and leverage; The financial accelerator in a quantitative business cycle framework.
- Citation: Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418-437. https://doi.org/10.1016/j.jfi.2008.12.002
- Citation: Bernanke, B. S., Gertler, M., & Gilchrist, S. (1999). The financial accelerator in a quantitative business cycle framework. *Handbook of Macroeconomics*, 1, 1341-1393. https://doi.org/10.1016/S1574-0048(99)10034-X
- Core Insight: Financial intermediaries target leverage ratios; when asset values rise, they have slack capital and expand balance sheets (buy more assets/extend more credit). When values fall, capital is eroded and they deleverage, amplifying the downturn.
- Mathematical Formulation: `Q = lending_rate * capital * cycle_indicator` when `cycle_indicator > 0` (expansion); `Q_sell = contraction_rate * position * abs(cycle_indicator)` when `cycle_indicator < 0` (contraction).
- Empirical Evidence: Adrian & Shin show investment bank leverage is pro-cyclical; BGG show the external finance premium amplifies shocks through net worth.
- Relevance to This Agent: The agent operationalizes pro-cyclical balance sheet expansion and contraction.
- Calibration Source: `lending_rate` 0.05-0.20, `contraction_rate` 0.05-0.25, `cycle_sensitivity` 1.0-3.0.
- Falsification Conditions: If the agent contracts credit during booms or expands during busts, the design is falsified.
- Alternative Theories: Counter-cyclical macro-prudential policy (Basel III buffers); constant-leverage models.

## Design Purpose and Activation Triggers

Purpose: Model the amplifying effect of pro-cyclical financial intermediation on credit cycles, demonstrating how bank lending behavior can turn mild shocks into severe booms and busts.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `cycle_indicator` available (positive = expansion, negative = contraction; normalized [-1, 1])
- own `cash` (capital) and `position` (outstanding credit) available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- `cycle_indicator > expansion_threshold` AND `cash > 0`: buy (extend credit) with `lending_rate * cash / price * cycle_intensity`.
- `cycle_indicator < -contraction_threshold` AND `position > 0`: sell (contract credit) with `contraction_rate * position * contraction_intensity`.
- `<Default>`: hold.

Where `cycle_intensity = min(cycle_indicator / expansion_threshold, cycle_sensitivity)` and `contraction_intensity = min(abs(cycle_indicator) / contraction_threshold, cycle_sensitivity)`.

Deactivation Conditions:
- capital exhausted during expansion.
- position fully unwound during contraction.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| boom (positive cycle) | expands credit aggressively | rising collateral, low measured risk |
| bust (negative cycle) | contracts credit sharply | falling collateral, capital erosion |
| neutral cycle | maintains position | no pressure to adjust |

Environmental Dependencies: requires cycle indicator (can be derived from asset prices, credit spreads, or GDP growth).

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | credit asset price reference |
| `cycle_indicator` | environment | float [-1, 1] | yes | business/credit cycle state |
| `cash` | own state | float | yes | capital/lending capacity |
| `position` | own state | float | yes | outstanding credit exposure |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | none | yes | order direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | none | yes | audit trail |

##### Content Constraints

Required fields are `action`, `quantity`, and `reasoning`. Quantity is clamped to available resources.

##### Serialization Format

`<analysis>...</analysis><decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>`

##### Implementer Contract Reminder

Every implementation variant must consume the same inputs and emit the same decision fields.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | execution reference |
| `cycle_indicator` | Continuous | 1 tick | credit cycle state |
| `cash` | State | persistent | capital constraint |
| `position` | State | persistent | exposure tracking |

Does NOT use: individual borrower information, monetary policy signals, peer bank behavior.

#### Core Behavioral Mechanism

1. Read `price`, `cycle_indicator`, `cash`, and `position`.
2. If `cycle_indicator > expansion_threshold` and `cash > 0`:
   - `cycle_intensity = min(cycle_indicator / expansion_threshold, cycle_sensitivity)`.
   - `q = lending_rate * cash / price * cycle_intensity`. Buy (extend credit).
3. If `cycle_indicator < -contraction_threshold` and `position > 0`:
   - `contraction_intensity = min(abs(cycle_indicator) / contraction_threshold, cycle_sensitivity)`.
   - `q = contraction_rate * position * contraction_intensity`. Sell (contract credit).
4. Otherwise, hold.
5. Emit the decision object.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `lending_rate * cash / price * intensity` for buys; `contraction_rate * position * intensity` for sells |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position cannot go negative |
| Resource cap | buy capped by cash / price; sell capped by position |
| Exit rule | contracts credit when cycle turns negative |

#### Mathematical Model

`q_buy = min(cash/price, lending_rate * cash/price * min(C/theta_exp, S))` if `C > theta_exp`; `q_sell = min(position, contraction_rate * position * min(|C|/theta_con, S))` if `C < -theta_con`; otherwise `q = 0`. Where `C = cycle_indicator`, `S = cycle_sensitivity`.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_exp` | expansion threshold | 0.10 | Adrian & Shin (2010) |
| `theta_con` | contraction threshold | 0.10 | Adrian & Shin (2010) |
| `lending_rate` | fraction of capital to lend per tick | 0.10 | calibration |
| `contraction_rate` | fraction of position to recall per tick | 0.15 | calibration |
| `cycle_sensitivity` | max intensity multiplier | 2.0 | BGG (1999) |

#### Behavioral Properties

- Time horizon: medium, because credit cycles develop over multiple periods.
- Risk tolerance: variable (high in booms, low in busts), driven by measured risk perception.
- Information asymmetry: partial, observes public cycle indicators.
- Psychological profile: risk-perception-driven; overconfident in booms, panic in busts.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `expansion_threshold` | float | 0.10 | [0.05, 0.20] | high | cycle level to trigger lending | Higher -> less pro-cyclical in mild booms | Adrian & Shin (2010) |
| `contraction_threshold` | float | 0.10 | [0.05, 0.20] | high | cycle level to trigger contraction | Higher -> less pro-cyclical in mild busts | Adrian & Shin (2010) |
| `lending_rate` | float | 0.10 | [0.05, 0.20] | high | capital fraction lent per tick | Higher -> faster credit expansion | calibration |
| `contraction_rate` | float | 0.15 | [0.05, 0.25] | high | position fraction recalled per tick | Higher -> faster credit crunch | calibration |
| `cycle_sensitivity` | float | 2.0 | [1.0, 3.0] | medium | max intensity scaling factor | Higher -> more amplification at extremes | BGG (1999) |

## Worked Numerical Examples

### Case 1 - Boom Expansion

System state: price 100.0, cycle_indicator 0.40, cash 100000, position 500.
Calculation: `cycle_intensity = min(0.40/0.10, 2.0) = min(4.0, 2.0) = 2.0`. `q = 0.10 * 100000/100 * 2.0 = 200`.
Decision: buy 200.
State update: cash decreases by 20000, position increases by 200.

### Case 2 - Bust Contraction

System state: price 80.0, cycle_indicator -0.30, cash 20000, position 800.
Calculation: `contraction_intensity = min(0.30/0.10, 2.0) = min(3.0, 2.0) = 2.0`. `q = 0.15 * 800 * 2.0 = 240`.
Decision: sell 240.
State update: position decreases by 240, cash increases by 19200.

### Case 3 - Neutral Hold

System state: price 100.0, cycle_indicator 0.05, cash 100000, position 500.
Calculation: `0.05 < 0.10` expansion threshold not met; `0.05 > -0.10` contraction threshold not met.
Decision: hold.
State update: unchanged.

### Edge Case - Boom but No Capital

System state: price 100.0, cycle_indicator 0.50, cash 0, position 1000.
Calculation: expansion triggered but cash is 0.
Decision: hold.
State update: unchanged.

## Behavioral Verification and Calibration

- Given `cycle_indicator > expansion_threshold` and `cash > 0`, agent must buy (extend credit).
- Given `cycle_indicator < -contraction_threshold` and `position > 0`, agent must sell (contract credit).
- Agent must never extend credit during contraction or contract during expansion.
- Given missing `cycle_indicator`, agent must hold.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-procyclicality | `lending_rate = 0, contraction_rate = 0` | pro-cyclical lending amplifies cycles | decrease | cycle amplitude |
| high-sensitivity | `cycle_sensitivity = 3.0` | stronger amplification -> deeper busts | increase | peak-to-trough price change |
| symmetric-rates | `lending_rate = contraction_rate = 0.10` | asymmetry matters for cycle shape | change | cycle skewness |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. https://doi.org/10.1016/j.jfi.2008.12.002 | Pro-cyclical leverage in intermediaries |
| 2 | Bernanke, B. S., Gertler, M., & Gilchrist, S. (1999). The financial accelerator. https://doi.org/10.1016/S1574-0048(99)10034-X | External finance premium amplification |
| 3 | Brunnermeier, M. K., & Sannikov, Y. (2014). A macroeconomic model with a financial sector. https://doi.org/10.1257/aer.104.2.379 | Endogenous risk amplification |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-pro-cyclical-lender.png) |
| Status | draft |
