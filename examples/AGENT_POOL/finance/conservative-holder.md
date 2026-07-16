# Conservative Holder

## Summary

| Field                 | Content                                                                                                                      |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Conservative holder                                                                                                          |
| Theory Family         | Value Investing / Buy-and-Hold                                                                                               |
| Behavioral Tendency   | **Converging — holds a steady, low-leverage portfolio and ignores bubble momentum; converges on long-run fundamental value** |
| Market Role           | **Stabilising** — provides passive fundamental-anchored demand that does not amplify bubble dynamics                         |
| Time Horizon          | long                                                                                                                         |
| Risk Tolerance        | low                                                                                                                          |
| Information Asymmetry | none                                                                                                                         |
| Determinism           | deterministic                                                                                                                |

## Definition and Goals

This agent models a passive long-term investor who holds a fundamental-anchored portfolio and ignores short-term bubble dynamics. The real-world counterpart is a pension fund, endowment, or buy-and-hold retail investor.

The decision goal is to buy modestly when price is below fundamental and hold otherwise. The agent does not use leverage, does not short-sell, and does not trade on momentum.

In simulation this agent provides a stable demand floor that does not amplify bubble or crash dynamics. Non-goals: it must not chase momentum, use leverage, or time the market.

## Theoretical Foundation

**Buy-and-hold and passive investing**:
- Theory / Study: Passive fundamental investing with low turnover.
- Citation: Malkiel, B. G. (2003). *A Random Walk Down Wall Street*. W.W. Norton. Also: Fama, E. F. (1970). Efficient capital markets. *Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486
- Core Insight: In efficient markets, the optimal strategy for a long-horizon investor is to hold a diversified portfolio and rebalance only when price deviates significantly from fundamental value. Active trading destroys value through transaction costs.
- Mathematical Formulation: `buy if (F - P) / P > theta; hold otherwise`.
- Empirical Evidence: Long-term buy-and-hold strategies outperform active trading after transaction costs (Fama, 1970; Malkiel, 2003).
- Relevance to This Agent: The agent buys only at significant discounts and holds patiently.
- Calibration Source: Fama (1970); Malkiel (2003).
- Falsification Conditions: If the agent trades on momentum, the passive design is violated.
- Alternative Theories: momentum trading; leveraged speculation; market timing.

## Design Purpose and Activation Triggers

Purpose: Provide stable, non-amplifying fundamental demand.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available

Missing-Signal Policy: hold when either signal is missing.

Activation Triggers:
- `price < fundamental * (1 - buy_threshold)`: buy modest quantity.
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted: hibernate.
- Position at target: hold.

Behavioral Adaptation by Condition:
| Condition                | Behavioral change                     | Mechanism                             |
|--------------------------|---------------------------------------|---------------------------------------|
| Bubble momentum positive | Ignores; maintains long-run portfolio | No momentum signal in decision rule   |
| Price below fundamental  | Adds modestly to position             | Sizing capped at `base_position_size` |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution | Mechanism                                        |
|--------|--------------|--------------------------------------------------|
| Bubble | Stabilising  | Ignores overvaluation; does not amplify.         |
| Crash  | Stabilising  | Holds through volatility; buys modest discounts. |
| Calm   | Neutral      | Price near fundamental; minimal trading.         |

Interaction with other agents: Does not interact strategically with other agents; provides passive demand floor.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape | Required? | Notes                      |
|---------------------|--------------|--------------|-----------|----------------------------|
| `price`             | environment  | `float`      | yes       | Execution reference.       |
| `fundamental`       | environment  | `float`      | yes       | Intrinsic value reference. |
| `cash`              | agent state  | `float`      | yes       | Buy capacity.              |
| `position`          | agent state  | `float`      | yes       | Current holdings.          |
| `identity`, `round` | round header | `str`, `int` | yes       | Scheduler metadata.        |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum        | Unit     | Required?   | Meaning                       |
|---------------|--------|---------------------------|----------|-------------|-------------------------------|
| `action`      | enum   | {"buy", "hold"}           | —        | yes         | Discrete action (no selling). |
| `quantity`    | float  | `[0, base_position_size]` | shares   | conditional | Order magnitude; 0 when hold. |
| `price_level` | float  | `= price`                 | currency | conditional | Execution reference.          |
| `reasoning`   | string | 1–3 sentences             | —        | yes         | Audit trail.                  |

##### Content Constraints

- Required fields MUST be present; forbidden fields MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, base_position_size]`.
- Agent MUST NOT sell — action is limited to buy or hold.

##### Serialization Format

    <analysis>...free-form reasoning...</analysis>
    <decision>{"action": "<enum>", "quantity": <float>, "price_level": <float>, "reasoning": "<text>"}</decision>

Rules: Tags literal ASCII; JSON keys match Outputs; rule variants may template; model variants MUST include in prompt; retrieval variants MUST declare fallback sentinel.

##### Implementer Contract Reminder

Implementers MUST re-open this §3.6.0 I/O Contract during every coding pass.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale               |
|---------------|------------|---------------|-------------------------|
| `price`       | Continuous | 1 tick        | Execution reference.    |
| `fundamental` | Continuous | 1 tick        | Intrinsic value anchor. |
| `cash`        | State      | persistent    | Buy constraint.         |

Does NOT use: momentum, price_history, anchor, cost_basis, peer flow.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `cash`.
2. Compute `discount = (fundamental - price) / price`.
3. If `discount > buy_threshold` and `cash > 0`, compute buy: `q = min(base_position_size, cash / price)`.
4. Otherwise hold.
5. Emit decision and update state post-fill.

#### Action Space

| Aspect                | Specification                       |
|-----------------------|-------------------------------------|
| Order types allowed   | market, hold-no-op                  |
| Price level rule      | market order at current price       |
| Order quantity rule   | buy: `min(base_size, cash / price)` |
| Order lifetime        | 1 tick                              |
| Cancellation policy   | unfilled orders expire              |
| Inventory constraint  | `position >= 0`; no selling         |
| Wealth / leverage cap | `cash >= 0`; no margin              |
| Stop-loss / kill rule | none — permanent holder             |

#### Mathematical Model

```
disc_t = (F_t - P_t) / P_t
if disc_t > theta_buy and cash_t > 0:
    a_t = buy; q_t = min(Q_max, cash_t / P_t)
else:
    a_t = hold; q_t = 0
```

| Symbol               | Meaning                | Default Value | Source                 |
|----------------------|------------------------|---------------|------------------------|
| `theta_buy`          | buy discount threshold | 0.05          | Fama (1970)            |
| `base_position_size` | max order              | 100.0         | Scenario normalization |

#### Behavioral Properties

- Time horizon: long, because the agent holds permanently.
- Risk tolerance: low, because the agent avoids leverage and short-selling.
- Information asymmetry: none, all inputs are public.
- Psychological profile: patient, passive, fundamental-anchored.

## Parameters

| Parameter            | Type  | Default | Valid Range  | Sensitivity | Description                      | Impact                               | Source                 |
|----------------------|-------|---------|--------------|-------------|----------------------------------|--------------------------------------|------------------------|
| `buy_threshold`      | float | 0.05    | [0.02, 0.15] | medium      | Discount required before buying. | Higher -> fewer purchases.           | Fama (1970)            |
| `sizing_scale`       | float | 2000.0  | [500, 5000]  | low         | Converts discount to quantity.   | Higher -> larger orders at discount. | Scenario normalization |
| `base_position_size` | float | 100.0   | [20, 300]    | low         | Maximum order quantity.          | Higher -> larger per-tick demand.    | Scenario normalization |

## Population and Heterogeneity

| Aspect                         | Specification           |
|--------------------------------|-------------------------|
| Default population size        | scenario-dependent      |
| Parameter heterogeneity policy | identical parameters    |
| Cross-agent correlation        | none                    |
| Identity persistence           | persistent across ticks |

## Worked Numerical Examples

### Case 1 — Buy at discount
System state: `price=90`, `fundamental=100`, `cash=20000`.
Calculation: `discount = (100-90)/90 = 0.111`; `0.111 > 0.05` triggers buy; `q = min(100, 20000/90) = min(100, 222) = 100`.
Decision: buy 100 at 90.
State update: position +100; cash -9000.

### Case 2 — Hold at fair value
System state: `price=100`, `fundamental=100`.
Calculation: `discount = 0`; below threshold.
Decision: hold.

### Case 3 — Ignore bubble
System state: `price=150`, `fundamental=100`.
Calculation: `discount = (100-150)/150 = -0.333`; negative — no buy trigger.
Decision: hold.

### Edge Case — No cash
System state: `cash=0`, `price=90`, `fundamental=100`.
Decision: hold (no capacity).

## Behavioral Verification and Calibration

**Calibration data sources**:
- `buy_threshold` <- Fama (1970) efficient-market discount ranges.

**Expected individual behaviour**:
- Given price below fundamental by >5% and positive cash, agent MUST buy.
- Given price at or above fundamental, agent MUST hold.
- Agent MUST NOT sell under any condition.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells THEN the design is violated because conservative holders do not sell.
- IF the agent uses leverage THEN the design is violated because conservative holders do not borrow.
- IF the agent trades on momentum THEN the passive design is contaminated.

#### Ablation Hooks

| Ablation name  | Setting               | Hypothesis tested                    | Expected direction | Metric       |
|----------------|-----------------------|--------------------------------------|--------------------|--------------|
| no-passive-buy | `buy_threshold = 999` | Passive demand provides price floor. | deeper crash       | max drawdown |

## Academic References

| # | Citation                                                                                                             | Notes                                   |
|---|----------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| 1 | Fama, E. F. (1970). Efficient capital markets. *Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486 | Efficient markets and passive investing |
| 2 | Malkiel, B. G. (2003). *A Random Walk Down Wall Street*. W.W. Norton.                                                | Buy-and-hold strategy                   |

## Design Provenance and Versioning

| Field       | Content                                                                          |
|-------------|----------------------------------------------------------------------------------|
| Author      | AGenticFinLab                                                                    |
| Reviewed by | audit_agent_handbook.py v1                                                       |
| Created     | 2026-07-11                                                                       |
| Version     | 1.1.0                                                                            |
| Status      | conformant                                                                       |
| Icon        | ![](../agent_images/icons/finance-conservative-holder.png)                       |
