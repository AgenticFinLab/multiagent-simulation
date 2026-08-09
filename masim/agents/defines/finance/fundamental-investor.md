# Fundamental Investor

## Summary

| Field                 | Content                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------|
| Archetype             | Fundamental investor                                                                                             |
| Theory Family         | Value Investing                                                                                                  |
| Behavioral Tendency   | **Converging — holds assets valued by fundamentals and ignores bubble momentum; converges on fundamental value** |
| Market Role           | **Stabilising** — provides fundamental-anchored demand that counters bubble overvaluation                        |
| Time Horizon          | long                                                                                                             |
| Risk Tolerance        | low-medium                                                                                                       |
| Information Asymmetry | none                                                                                                             |
| Determinism           | deterministic                                                                                                    |

## Definition and Goals

This agent models a patient fundamental investor who buys when price is below intrinsic value and holds when price is above. The real-world counterpart is a Graham-style value investor or long-term institutional holder.

The decision goal is to buy when `deviation = (fundamental - price) / price` is positive (price below fundamental) and hold otherwise. The agent does not short-sell.

In simulation this agent provides a stabilising floor — buying undervalued assets and ignoring bubble momentum. Non-goals: it must not chase momentum, use leverage, or sell short.

## Theoretical Foundation

**Intrinsic value and margin of safety**:
- Theory / Study: Fundamental value investing with margin of safety.
- Citation: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.
- Core Insight: Every security has an intrinsic value determinable from earnings capacity and future cash flows. When market price deviates substantially from intrinsic value, the rational investor buys with a margin of safety.
- Mathematical Formulation: `trade_signal = (F(t) - P(t)) / P(t)`; buy when signal > threshold.
- Empirical Evidence: Value strategies (low P/B, high dividend yield) earn long-run excess returns (Fama & French, 1992).
- Relevance to This Agent: The agent buys when price is below fundamental and holds patiently.
- Calibration Source: Graham & Dodd (1934); Fama & French (1992).
- Falsification Conditions: If the agent sells when price is below fundamental, the value mechanism is inverted.
- Alternative Theories: momentum trading; noise-trader risk; rational inattention.

## Design Purpose and Activation Triggers

Purpose: Provide long-horizon fundamental-anchored demand.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available

Missing-Signal Policy: hold when either signal is missing.

Activation Triggers:
- `price < fundamental * (1 - buy_threshold)`: buy with sized quantity.
- `price > fundamental * (1 + sell_threshold)`: sell (if position allows).
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted: hibernate buy side.
- Position is zero and price is above fundamental: hold.

Behavioral Adaptation by Condition:
| Condition               | Behavioral change     | Mechanism                       |
|-------------------------|-----------------------|---------------------------------|
| Price below fundamental | Buys and holds        | Sizing proportional to discount |
| Price above fundamental | Holds; does not chase | No short-selling                |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution | Mechanism                                |
|--------|--------------|------------------------------------------|
| Bubble | Stabilising  | Ignores overvaluation; does not amplify. |
| Crash  | Stabilising  | Buys undervalued assets.                 |
| Calm   | Neutral      | Price near fundamental; minimal trading. |

Interaction with other agents: Provides counter-cyclical demand against momentum speculators; does not trade against rational arbitrageurs.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape | Required? | Notes                      |
|---------------------|--------------|--------------|-----------|----------------------------|
| `price`             | environment  | `float`      | yes       | Execution reference.       |
| `fundamental`       | environment  | `float`      | yes       | Intrinsic value reference. |
| `cash`              | agent state  | `float`      | yes       | Buy capacity.              |
| `position`          | agent state  | `float`      | yes       | Sell capacity.             |
| `identity`, `round` | round header | `str`, `int` | yes       | Scheduler metadata.        |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum        | Unit     | Required?   | Meaning                       |
|---------------|--------|---------------------------|----------|-------------|-------------------------------|
| `action`      | enum   | {"buy", "sell", "hold"}   | —        | yes         | Discrete action.              |
| `quantity`    | float  | `[0, base_position_size]` | shares   | conditional | Order magnitude; 0 when hold. |
| `price_level` | float  | `= price`                 | currency | conditional | Execution reference.          |
| `reasoning`   | string | 1–3 sentences             | —        | yes         | Audit trail.                  |

##### Content Constraints

- Required fields MUST be present; forbidden fields MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, base_position_size]`.
- `quantity` is unsigned; direction is carried by `action`.

##### Serialization Format

    <analysis>...free-form reasoning...</analysis>
    <decision>{"action": "<enum>", "quantity": <float>, "price_level": <float>, "reasoning": "<text>"}</decision>

Rules: Tags are literal ASCII; JSON keys match Outputs table; rule variants may template analysis; model variants MUST include in prompt; retrieval variants MUST declare fallback sentinel.

##### Implementer Contract Reminder

Implementers MUST re-open this §3.6.0 I/O Contract during every coding pass as the single source of truth.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale               |
|---------------|------------|---------------|-------------------------|
| `price`       | Continuous | 1 tick        | Execution reference.    |
| `fundamental` | Continuous | 1 tick        | Intrinsic value anchor. |
| `cash`        | State      | persistent    | Buy constraint.         |
| `position`    | State      | persistent    | Sell constraint.        |

Does NOT use: momentum, anchor, cost_basis, peer flow.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `cash`, `position`.
2. Compute `discount = (fundamental - price) / price`.
3. If `discount > buy_threshold`, compute buy quantity: `q = min(base_position_size, discount * sizing_scale)`, clamped by `cash / price`.
4. If `discount < -sell_threshold` and `position > 0`, sell: `q = min(position, base_position_size)`.
5. Otherwise hold.
6. Emit decision and update state post-fill.

#### Action Space

| Aspect                | Specification                                                                                    |
|-----------------------|--------------------------------------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                                               |
| Price level rule      | market order at current price                                                                    |
| Order quantity rule   | buy: `min(base_size, discount * sizing_scale)` clamped by cash; sell: `min(position, base_size)` |
| Order lifetime        | 1 tick                                                                                           |
| Cancellation policy   | unfilled orders expire                                                                           |
| Inventory constraint  | `position >= 0`; no short-selling                                                                |
| Wealth / leverage cap | `cash >= 0`; no margin                                                                           |
| Stop-loss / kill rule | none — patient holder                                                                            |

#### Mathematical Model

```
disc_t = (F_t - P_t) / P_t
if disc_t > theta_buy:
    a_t = buy;  q_t = min(Q_max, disc_t * k_q); clamped by cash/P_t
elif disc_t < -theta_sell and position_t > 0:
    a_t = sell; q_t = min(position_t, Q_max)
else:
    a_t = hold; q_t = 0
```

| Symbol               | Meaning                | Default Value | Source                 |
|----------------------|------------------------|---------------|------------------------|
| `theta_buy`          | buy discount threshold | 0.05          | Graham & Dodd (1934)   |
| `theta_sell`         | sell premium threshold | 0.10          | Scenario calibration   |
| `sizing_scale`       | quantity scale         | 4000.0        | Scenario normalization |
| `base_position_size` | max order              | 200.0         | Scenario normalization |

#### Behavioral Properties

- Time horizon: long, because fundamental value takes time to be reflected in price.
- Risk tolerance: low-medium, because the agent avoids leverage and short-selling.
- Information asymmetry: none, all inputs are public.
- Psychological profile: patient, disciplined, fundamental-anchored.

## Parameters

| Parameter            | Type  | Default | Valid Range  | Sensitivity | Description                      | Impact                            | Source                 |
|----------------------|-------|---------|--------------|-------------|----------------------------------|-----------------------------------|------------------------|
| `buy_threshold`      | float | 0.05    | [0.02, 0.15] | high        | Discount required before buying. | Higher -> fewer but deeper buys.  | Graham & Dodd (1934)   |
| `sell_threshold`     | float | 0.10    | [0.03, 0.20] | medium      | Premium required before selling. | Higher -> more patient holding.   | Scenario calibration   |
| `sizing_scale`       | float | 4000.0  | [500, 10000] | medium      | Converts discount to quantity.   | Higher -> larger orders.          | Scenario normalization |
| `base_position_size` | float | 200.0   | [50, 500]    | medium      | Maximum order quantity.          | Higher -> larger per-tick impact. | Scenario normalization |

## Population and Heterogeneity

| Aspect                         | Specification           |
|--------------------------------|-------------------------|
| Default population size        | scenario-dependent      |
| Parameter heterogeneity policy | identical parameters    |
| Cross-agent correlation        | none                    |
| Identity persistence           | persistent across ticks |

## Worked Numerical Examples

### Case 1 — Buy undervalued
System state: `price=90`, `fundamental=100`, `cash=50000`, `position=0`.
Calculation: `discount = (100-90)/90 = 0.111`; `0.111 > 0.05` triggers buy; `q = min(200, 0.111*4000) = min(200, 444) = 200`; cash clamp: `min(200, 50000/90) = 200`.
Decision: buy 200 at 90.
State update: position +200; cash -18000.

### Case 2 — Hold at fair value
System state: `price=100`, `fundamental=100`.
Calculation: `discount = 0`; inside no-trade band.
Decision: hold.

### Case 3 — Sell overvalued
System state: `price=115`, `fundamental=100`, `position=100`.
Calculation: `discount = (100-115)/115 = -0.130`; `-0.130 < -0.10` triggers sell; `q = min(100, 200) = 100`.
Decision: sell 100 at 115.
State update: position -100; cash +11500.

### Edge Case — Missing fundamental
Decision: hold.

## Validation and Calibration

**Calibration data sources**:
- `buy_threshold` <- Graham & Dodd (1934) margin-of-safety ranges.
- `sell_threshold` <- scenario calibration for profit-taking timing.

**Expected individual behaviour**:
- Given price below fundamental by >5%, agent MUST buy.
- Given price above fundamental by >10% with position, agent MUST sell.
- Given price near fundamental, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells when price is below fundamental THEN the value mechanism is inverted because fundamental investors buy undervaluation.
- IF the agent uses leverage THEN the design constraint is violated because fundamental investors do not borrow.
- IF `quantity > base_position_size` THEN the sizing constraint is broken.

#### Ablation Hooks

| Ablation name      | Setting                 | Hypothesis tested                        | Expected direction | Metric        |
|--------------------|-------------------------|------------------------------------------|--------------------|---------------|
| no-fundamental-buy | `buy_threshold = 999`   | Fundamental buying provides price floor. | deeper crash       | max drawdown  |
| patient-holder     | `sell_threshold = 0.50` | Patient holding stabilises post-bubble.  | slower recovery    | recovery time |

## Behavioral Verification and Calibration

- Given price exactly at fundamental (discount = 0), agent must hold with zero quantity.
- Given price 10% below fundamental with sufficient cash, agent must buy with quantity proportional to the discount magnitude.
- Given price 15% above fundamental with non-zero position, agent must sell up to base_position_size.
- Given zero cash and discount exceeding buy_threshold, agent must hold despite the buy signal (cash constraint binds).
- Given missing fundamental signal, agent must hold without error.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `wide_band` | `buy_threshold = 0.15, sell_threshold = 0.30` | Wider no-trade band reduces stabilising trade frequency | decrease | trades per episode |
| `aggressive_sizing` | `sizing_scale = 8000` | Larger orders strengthen the fundamental-anchored price floor | decrease | max drawdown from fundamental |

## Academic References

| # | Citation                                                                                                                                                                   | Notes                                |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| 1 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                                                                           | Intrinsic value and margin of safety |
| 2 | Fama, E. F., & French, K. R. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427–465. https://doi.org/10.1111/j.1540-6261.1992.tb04299.x | Value premium empirical evidence     |

## Design Provenance and Versioning

| Field       | Content                                                                          |
|-------------|----------------------------------------------------------------------------------|
| Author      | AGenticFinLab                                                                    |
| Reviewed by | QoderWork three-pass self-check |
| Created     | 2026-07-11                                                                       |
| Version     | 1.1.0                                                                            |
| Status      | conformant                                                                       |
| Icon        | ![](../agent_images/icons/finance-fundamental-investor.png)                      |
