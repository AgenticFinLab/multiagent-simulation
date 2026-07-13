# Leveraged Buyer

## Summary

| Field                 | Content                                                                                                        |
|-----------------------|----------------------------------------------------------------------------------------------------------------|
| Archetype             | Leveraged buyer                                                                                                |
| Theory Family         | Procyclical Leverage / Balance-Sheet Amplification                                                             |
| Behavioral Tendency   | **Diverging — uses leverage to chase bubble gains; diverges from fundamental value and amplifies the upswing** |
| Market Role           | **Destabilising** — procyclical leverage amplifies bubble formation and crash severity                         |
| Time Horizon          | short-medium                                                                                                   |
| Risk Tolerance        | high                                                                                                           |
| Information Asymmetry | none                                                                                                           |
| Determinism           | deterministic                                                                                                  |

## Definition and Goals

This agent models a leveraged investor who borrows against rising asset values to amplify positions. The real-world counterpart is a margin-financed retail investor or a leveraged hedge fund.

The decision goal is to buy when momentum is positive, using leverage proportional to current equity. When prices fall, the agent de-leverages under margin pressure.

In simulation this agent amplifies the bubble through procyclical borrowing and accelerates the crash through forced de-leveraging. Non-goals: it must not use fundamental valuation or act as a patient holder.

## Theoretical Foundation

**Procyclical leverage and balance-sheet amplification**:
- Theory / Study: Balance-sheet channel of financial amplification.
- Citation: Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002
- Core Insight: Financial intermediaries manage balance sheets procyclically: when asset prices rise, mark-to-market equity increases, loosening leverage constraints and enabling additional borrowing. When prices fall, equity declines, tightening constraints and forcing sales.
- Mathematical Formulation: `leverage_t = equity_t / margin_requirement`; `buy_capacity = leverage_t * equity_t / price`.
- Empirical Evidence: Adrian & Shin (2010) document that broker-dealer leverage is positively correlated with asset values, confirming procyclical balance-sheet management.
- Relevance to This Agent: The agent's leverage scales with `equity / price`, amplifying buys during the bubble and forcing sells during the crash.
- Calibration Source: Adrian & Shin (2010); scenario normalization.
- Falsification Conditions: If leverage does not increase with rising equity, the procyclical channel is absent.
- Alternative Theories: constant leverage; fundamental valuation; risk-parity allocation.

## Design Purpose and Activation Triggers

Purpose: Amplify bubble demand through procyclical leverage.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `price_history` for momentum computation

Missing-Signal Policy: hold if signals are missing.

Activation Triggers:
- `momentum > buy_threshold` and `equity > 0`: buy with leveraged quantity.
- `equity < margin_call_threshold`: de-leverage (sell).
- `<Default>`: hold.

Deactivation Conditions:
- Equity is zero or negative: forced liquidation.
- Leverage at maximum: cap position.

Behavioral Adaptation by Condition:
| Condition                | Behavioral change                                | Mechanism                       |
|--------------------------|--------------------------------------------------|---------------------------------|
| Bubble momentum positive | Borrows up to `leverage_max` to amplify position | Leverage scales with `momentum` |
| Margin call              | De-leverages to `leverage_min`                   | Binary de-risk rule             |

Environmental Dependencies: Requires a per-tick `price` feed and a margin-call signal. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime         | Contribution  | Mechanism                                 |
|----------------|---------------|-------------------------------------------|
| Bubble upswing | Destabilising | Leverage amplifies momentum demand.       |
| Crash          | Destabilising | Forced de-leveraging accelerates selling. |
| Calm           | Neutral       | Low momentum; minimal leverage.           |

Interaction with other agents: Amplifies the same feedback loop as momentum speculators; rational arbitrageurs trade against this agent's leveraged demand.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape  | Required? | Notes                 |
|---------------------|--------------|---------------|-----------|-----------------------|
| `price`             | environment  | `float`       | yes       | Execution reference.  |
| `price_history`     | environment  | `list[float]` | yes       | Momentum computation. |
| `cash`              | agent state  | `float`       | yes       | Equity.               |
| `position`          | agent state  | `float`       | yes       | Current holdings.     |
| `identity`, `round` | round header | `str`, `int`  | yes       | Scheduler metadata.   |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum                       | Unit     | Required?   | Meaning              |
|---------------|--------|------------------------------------------|----------|-------------|----------------------|
| `action`      | enum   | {"buy", "sell", "hold"}                  | —        | yes         | Discrete action.     |
| `quantity`    | float  | `[0, base_position_size * leverage_max]` | shares   | conditional | Order magnitude.     |
| `price_level` | float  | `= price`                                | currency | conditional | Execution reference. |
| `reasoning`   | string | 1–3 sentences                            | —        | yes         | Audit trail.         |

##### Content Constraints

- Required fields MUST be present; forbidden fields MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, base_position_size * leverage_max]`.

##### Serialization Format

    <analysis>...free-form reasoning...</analysis>
    <decision>{"action": "<enum>", "quantity": <float>, "price_level": <float>, "reasoning": "<text>"}</decision>

Rules: Tags literal ASCII; JSON keys match Outputs; rule variants may template; model variants MUST include in prompt; retrieval variants MUST declare fallback sentinel.

##### Implementer Contract Reminder

Implementers MUST re-open this §3.6.0 I/O Contract during every coding pass.

#### Decision Information Set

| Signal          | Type       | Memory Window    | Rationale            |
|-----------------|------------|------------------|----------------------|
| `price`         | Continuous | 1 tick           | Execution reference. |
| `price_history` | Continuous | `lookback` ticks | Momentum signal.     |
| `cash`          | State      | persistent       | Equity for leverage. |
| `position`      | State      | persistent       | Current exposure.    |

Does NOT use: `fundamental`, `anchor`, `cost_basis`.

#### Core Behavioral Mechanism

1. Read `price`, `price_history`, `cash`, `position`.
2. Compute `momentum = (price - MA_k) / MA_k`.
3. Compute `equity = cash + position * price`.
4. If `momentum > buy_threshold` and `equity > 0`, compute leveraged buy: `q = min(base_position_size * leverage, momentum * sizing_scale)`, clamped by `equity * leverage / price`.
5. If `equity < margin_call_threshold`, de-leverage: sell `q = min(position, position * deleverage_ratio)`.
6. Otherwise hold.
7. Emit decision and update state.

#### Action Space

| Aspect                | Specification                            |
|-----------------------|------------------------------------------|
| Order types allowed   | market, hold-no-op                       |
| Price level rule      | market order at current price            |
| Order quantity rule   | leveraged buy or forced de-leverage sell |
| Order lifetime        | 1 tick                                   |
| Cancellation policy   | unfilled orders expire                   |
| Inventory constraint  | `position >= 0`                          |
| Wealth / leverage cap | `leverage <= leverage_max`               |
| Stop-loss / kill rule | margin call triggers forced de-leverage  |

#### Mathematical Model

```
m_t = (P_t - MA_k) / MA_k
equity_t = cash_t + position_t * P_t
if m_t > theta_buy and equity_t > 0:
    L = min(leverage_max, equity_t / margin_base)
    a_t = buy; q_t = min(Q_max * L, m_t * k_q)
elif equity_t < margin_call:
    a_t = sell; q_t = position_t * deleverage_ratio
else:
    a_t = hold; q_t = 0
```

| Symbol               | Meaning                      | Default Value | Source                 |
|----------------------|------------------------------|---------------|------------------------|
| `lookback`           | MA window                    | 5             | Scenario calibration   |
| `buy_threshold`      | momentum trigger             | 0.02          | Scenario calibration   |
| `leverage_max`       | max leverage                 | 3.0           | Adrian & Shin (2010)   |
| `margin_call`        | forced de-leverage trigger   | 100.0         | Scenario normalization |
| `deleverage_ratio`   | fraction sold on margin call | 0.50          | Scenario calibration   |
| `sizing_scale`       | quantity scale               | 3000.0        | Scenario normalization |
| `base_position_size` | max base order               | 200.0         | Scenario normalization |

#### Behavioral Properties

- Time horizon: short-medium, because leverage decisions are tactical.
- Risk tolerance: high, because the agent uses procyclical leverage.
- Information asymmetry: none, all inputs are public.
- Psychological profile: leverage-amplified momentum chaser.

## Parameters

| Parameter            | Type  | Default | Valid Range | Sensitivity | Description                                  | Impact                                 | Source                 |
|----------------------|-------|---------|-------------|-------------|----------------------------------------------|----------------------------------------|------------------------|
| `lookback`           | int   | 5       | [2, 15]     | high        | Momentum window.                             | Shorter -> more reactive.              | Scenario calibration   |
| `buy_threshold`      | float | 0.02    | [0, 0.10]   | high        | Momentum trigger for leveraged buy.          | Higher -> fewer trades.                | Scenario calibration   |
| `leverage_max`       | float | 3.0     | [1, 5]      | high        | Maximum leverage multiplier.                 | Higher -> larger bubble amplification. | Adrian & Shin (2010)   |
| `margin_call`        | float | 100.0   | [10, 500]   | high        | Equity below which forced de-leverage fires. | Higher -> earlier forced selling.      | Scenario normalization |
| `deleverage_ratio`   | float | 0.50    | [0.1, 1.0]  | medium      | Fraction of position sold on margin call.    | Higher -> faster de-leveraging.        | Scenario calibration   |
| `sizing_scale`       | float | 3000.0  | [500, 8000] | medium      | Converts momentum to quantity.               | Higher -> larger orders.               | Scenario normalization |
| `base_position_size` | float | 200.0   | [50, 500]   | medium      | Maximum base order quantity.                 | Higher -> larger per-tick impact.      | Scenario normalization |

## Population and Heterogeneity

| Aspect                         | Specification           |
|--------------------------------|-------------------------|
| Default population size        | scenario-dependent      |
| Parameter heterogeneity policy | identical parameters    |
| Cross-agent correlation        | none                    |
| Identity persistence           | persistent across ticks |

## Worked Numerical Examples

### Case 1 — Leveraged buy
System state: `price=110`, `MA_5=100`, `cash=10000`, `position=50`, `leverage_max=3.0`.
Calculation: `momentum = 0.10`; `equity = 10000 + 50*110 = 15500`; `L = min(3.0, 15500/5000) = 3.0`; `q = min(200*3, 0.10*3000) = min(600, 300) = 300`.
Decision: buy 300 at 110.
State update: position +300; cash -33000 (financed by leverage).

### Case 2 — Margin call de-leverage
System state: `price=80`, `cash=500`, `position=100`, `margin_call=100`.
Calculation: `equity = 500 + 100*80 = 8500`; `8500 > 100` — no margin call; but `momentum < 0` — hold.
Decision: hold.

### Case 3 — Forced liquidation
System state: `price=50`, `cash=100`, `position=100`, `margin_call=6000`.
Calculation: `equity = 100 + 100*50 = 5100`; `5100 < 6000` triggers de-leverage; `q = 100 * 0.50 = 50`.
Decision: sell 50 at 50.
State update: position -50; cash +2500.

### Edge Case — Zero equity
System state: `cash=0`, `position=0`.
Decision: hold.

## Validation and Calibration

**Calibration data sources**:
- `leverage_max` <- Adrian & Shin (2010) broker-dealer leverage ranges.
- `margin_call` <- scenario normalization for forced liquidation threshold.

**Expected individual behaviour**:
- Given positive momentum and positive equity, agent MUST buy with leverage.
- Given equity below margin_call, agent MUST de-leverage.
- Given no momentum and adequate equity, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF leverage does not amplify buy quantity THEN the procyclical channel is broken because leveraged buyers borrow against equity.
- IF the agent does not de-leverage when equity falls below margin_call THEN the forced-liquidation rule is absent.
- IF `quantity > base_position_size * leverage_max` THEN the leverage cap is violated.

#### Ablation Hooks

| Ablation name | Setting              | Hypothesis tested                         | Expected direction | Metric               |
|---------------|----------------------|-------------------------------------------|--------------------|----------------------|
| no-leverage   | `leverage_max = 1.0` | Leverage amplifies the bubble.            | smaller bubble     | peak price deviation |
| early-margin  | `margin_call = 500`  | Earlier margin calls limit bubble height. | smaller bubble     | peak price deviation |

## Academic References

| # | Citation                                                                                                                                                   | Notes                            |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------|
| 1 | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002 | Procyclical leverage calibration |

## Design Provenance and Versioning

| Field       | Content                                                                          |
|-------------|----------------------------------------------------------------------------------|
| Author      | AGenticFinLab                                                                    |
| Reviewed by | audit_agent_handbook.py v1                                                       |
| Created     | 2026-07-11                                                                       |
| Version     | 1.1.0                                                                            |
| Change log  | 0.1.0 - Stub created for AssetBubble; 1.1.0 - Full §3 conformance authoring pass |
| Status      | conformant                                                                       |
| Icon        | ![](../agent_images/icons/finance-leveraged-buyer.png)                           |
