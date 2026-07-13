# Momentum Speculator

## Summary

| Field                 | Content                                                                                                             |
|-----------------------|---------------------------------------------------------------------------------------------------------------------|
| Archetype             | Momentum speculator (greater-fool participant)                                                                      |
| Theory Family         | Behavioral Finance / Positive Feedback Trading                                                                      |
| Behavioral Tendency   | **Diverging — chases bubble momentum and amplifies the upswing; diverges from fundamental value during the bubble** |
| Market Role           | **Destabilising** — primary driver of bubble formation through positive-feedback demand                             |
| Time Horizon          | short                                                                                                               |
| Risk Tolerance        | high                                                                                                                |
| Information Asymmetry | none                                                                                                                |
| Determinism           | deterministic                                                                                                       |

## Definition and Goals

This agent models the retail momentum investor or trend-following fund that ignores fundamental value, buying when prices are rising because past gains predict short-term continuation. The real-world counterpart is a greater-fool speculator or positive-feedback trader.

The decision goal is to emit buy orders when `momentum = (price - MA_k) / MA_k` is positive and above a threshold, and sell orders when momentum turns negative. Leverage amplifies both positions and losses.

In simulation this agent is the primary bubble driver — its positive-feedback demand pushes prices above fundamental value. Non-goals: it must not use fundamental valuation, mean-reversion logic, or long-horizon discipline.

## Theoretical Foundation

**Greater fool / momentum theory**:
- Theory / Study: Momentum premium in equities and positive feedback trading.
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Stocks that performed well over 3–12 months continue to outperform, generating approximately 1% per month excess return. This momentum premium arises from underreaction and positive feedback trading.
- Mathematical Formulation: `momentum(t) = (P(t) - MA_k(t)) / MA_k(t)`.
- Empirical Evidence: Jegadeesh & Titman (1993) find 12.01% annualised momentum return in US equities.
- Relevance to This Agent: Buy/sell thresholds calibrated to produce meaningful but not extreme demand shocks.
- Calibration Source: Jegadeesh & Titman (1993); De Long et al. (1990).
- Falsification Conditions: If the agent sells during positive momentum, the feedback mechanism is absent.
- Alternative Theories: reversal trading; rational bubble; fundamental analysis.

**Positive feedback trading**:
- Theory / Study: Noise trader and positive feedback strategies.
- Citation: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379–395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x
- Core Insight: Positive feedback traders who buy when prices rise can destabilise markets when aggregate demand is large enough relative to corrective arbitrage.
- Mathematical Formulation: `D_feedback(t) = alpha * [P(t) - P(t-1)] / P(t-1)`.
- Empirical Evidence: Feedback trading documented in retail flow data and trend-following fund returns.
- Relevance to This Agent: The leverage amplification mechanism encodes procyclical balance-sheet expansion.
- Calibration Source: De Long et al. (1990); Adrian & Shin (2010).
- Falsification Conditions: If leverage does not amplify the position during positive momentum, the feedback loop is broken.
- Alternative Theories: rational arbitrage; fundamental valuation.

## Design Purpose and Activation Triggers

Purpose: Generate positive-feedback demand that drives bubble formation.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `price_history` of at least `lookback` observations available

Missing-Signal Policy: hold if price history is insufficient to compute momentum.

Activation Triggers:
- `momentum > buy_threshold`: submit buy order with leverage.
- `momentum < sell_threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- Cash floor breached: hibernate buy side.
- Leverage limit reached: cap position.

Behavioral Adaptation by Condition:
| Condition                | Behavioral change                      | Mechanism                                                  |
|--------------------------|----------------------------------------|------------------------------------------------------------|
| Positive bubble momentum | Chases the upswing with leveraged buys | Sizing proportional to `momentum`; amplified by `leverage` |
| Momentum reversal        | Exits or flips position                | Sign of `momentum` flips                                   |

Environmental Dependencies: Requires a per-tick `price` feed and a `price_history` series of at least `lookback` observations. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime           | Contribution  | Mechanism                                            |
|------------------|---------------|------------------------------------------------------|
| Bubble upswing   | Destabilising | Positive feedback amplifies price above fundamental. |
| Post-burst crash | Destabilising | Leverage unwind accelerates the decline.             |
| Calm             | Neutral       | Momentum near zero; minimal trading.                 |

Interaction with other agents: Rational arbitrageurs trade against this agent's bubble demand; fundamental investors ignore it; leveraged buyers amplify the same feedback loop.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape  | Required? | Notes                                          |
|---------------------|--------------|---------------|-----------|------------------------------------------------|
| `price`             | environment  | `float`       | yes       | Execution reference.                           |
| `price_history`     | environment  | `list[float]` | yes       | At least `lookback` observations for momentum. |
| `cash`              | agent state  | `float`       | yes       | Buy capacity.                                  |
| `position`          | agent state  | `float`       | yes       | Sell capacity.                                 |
| `identity`, `round` | round header | `str`, `int`  | yes       | Scheduler metadata.                            |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum                   | Unit     | Required?   | Meaning                                  |
|---------------|--------|--------------------------------------|----------|-------------|------------------------------------------|
| `action`      | enum   | {"buy", "sell", "hold"}              | —        | yes         | Discrete action selected this call.      |
| `quantity`    | float  | `[0, base_position_size * leverage]` | shares   | conditional | Order magnitude; 0 when `action = hold`. |
| `price_level` | float  | `= price` (market order)             | currency | conditional | Execution reference.                     |
| `reasoning`   | string | 1–3 sentences                        | —        | yes         | Audit trail explaining WHY.              |

##### Content Constraints

- Required fields: every row marked `Required? = yes` MUST be present on every call.
- Forbidden fields: undeclared fields MUST NOT be emitted.
- Value ranges: `quantity` MUST be clamped to `[0, base_position_size * leverage]`.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<enum value>",
                "quantity": <float>,
                "price_level": <float>,
                "reasoning": "<explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel for `retrieved_knowledge`.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this §3.6.0 I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal          | Type       | Memory Window    | Rationale             |
|-----------------|------------|------------------|-----------------------|
| `price`         | Continuous | 1 tick           | Execution reference.  |
| `price_history` | Continuous | `lookback` ticks | Momentum computation. |
| `cash`          | State      | persistent       | Buy constraint.       |
| `position`      | State      | persistent       | Sell constraint.      |

Does NOT use: `fundamental`, `anchor`, `cost_basis`, peer flow.

#### Core Behavioral Mechanism

1. Read `price`, `price_history`, `cash`, and `position`.
2. Compute `MA_k = mean(price_history[-lookback:])`.
3. Compute `momentum = (price - MA_k) / MA_k`.
4. If `momentum > buy_threshold`, compute buy quantity: `q = min(base_position_size * leverage, momentum * sizing_scale)`, clamped by `cash / price`.
5. If `momentum < sell_threshold`, compute sell quantity: `q = min(position, base_position_size)`.
6. Otherwise hold.
7. Emit decision and update state post-fill.

#### Action Space

| Aspect                | Specification                                                                                               |
|-----------------------|-------------------------------------------------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                                                          |
| Price level rule      | market order at current price                                                                               |
| Order quantity rule   | buy: `min(base_size * leverage, momentum * sizing_scale)` clamped by cash; sell: `min(position, base_size)` |
| Order lifetime        | 1 tick                                                                                                      |
| Cancellation policy   | unfilled orders expire                                                                                      |
| Inventory constraint  | `position >= 0`                                                                                             |
| Wealth / leverage cap | `leverage` amplifies buy capacity up to `leverage_max`                                                      |
| Stop-loss / kill rule | none — rides momentum until reversal                                                                        |

#### Mathematical Model

```
MA_k = mean(P_{t-k} ... P_{t-1})
m_t = (P_t - MA_k) / MA_k
if m_t > theta_buy:
    a_t = buy;  q_t = min(Q_max * L, m_t * k_q); clamped by cash/P_t
elif m_t < theta_sell:
    a_t = sell; q_t = min(position_t, Q_max)
else:
    a_t = hold; q_t = 0
```

State variables: `cash`, `position`, updated post-fill.
Determinism contract: deterministic given identical inputs and state.

| Symbol               | Meaning             | Default Value | Source                    |
|----------------------|---------------------|---------------|---------------------------|
| `lookback`           | MA window           | 5             | Jegadeesh & Titman (1993) |
| `theta_buy`          | buy threshold       | 0.01          | Scenario calibration      |
| `theta_sell`         | sell threshold      | -0.02         | Scenario calibration      |
| `leverage`           | leverage multiplier | 2.0           | Adrian & Shin (2010)      |
| `sizing_scale`       | quantity scale      | 5000.0        | Scenario normalization    |
| `base_position_size` | max base order      | 300.0         | Scenario normalization    |

#### Behavioral Properties

- Time horizon: short, because momentum signals are evaluated each tick.
- Risk tolerance: high, because the agent uses leverage and ignores fundamental value.
- Information asymmetry: none, all inputs are public.
- Psychological profile: trend-chasing, feedback-driven, leverage-amplified.

## Parameters

| Parameter            | Type  | Default | Valid Range  | Sensitivity | Description                         | Impact                                        | Source                    |
|----------------------|-------|---------|--------------|-------------|-------------------------------------|-----------------------------------------------|---------------------------|
| `lookback`           | int   | 5       | [2, 20]      | high        | Moving-average window for momentum. | Shorter -> more reactive; longer -> smoother. | Jegadeesh & Titman (1993) |
| `buy_threshold`      | float | 0.01    | [0, 0.10]    | high        | Momentum above which agent buys.    | Higher -> fewer bubble trades.                | Scenario calibration      |
| `sell_threshold`     | float | -0.02   | [-0.10, 0]   | high        | Momentum below which agent sells.   | Lower -> later exit.                          | Scenario calibration      |
| `leverage`           | float | 2.0     | [1, 5]       | high        | Amplifies buy position size.        | Higher -> larger bubble amplification.        | Adrian & Shin (2010)      |
| `sizing_scale`       | float | 5000.0  | [100, 10000] | medium      | Converts momentum to quantity.      | Higher -> larger orders.                      | Scenario normalization    |
| `base_position_size` | float | 300.0   | [50, 1000]   | medium      | Maximum base order quantity.        | Higher -> larger per-tick impact.             | Scenario normalization    |

## Population and Heterogeneity

| Aspect                         | Specification                                              |
|--------------------------------|------------------------------------------------------------|
| Default population size        | scenario-dependent                                         |
| Parameter heterogeneity policy | iid draws for `lookback` and `leverage`                    |
| Heterogeneity per parameter    | `lookback ~ Uniform(3, 8)`; `leverage ~ Uniform(1.5, 3.0)` |
| Cross-agent correlation        | none                                                       |
| Identity persistence           | persistent across ticks                                    |

## Worked Numerical Examples

### Case 1 — Bubble buy
System state: `price=110`, `MA_5=100`, `cash=50000`, `position=0`, `leverage=2.0`.
Calculation: `momentum = (110-100)/100 = 0.10`; `0.10 > 0.01` triggers buy; `q = min(300*2, 0.10*5000) = min(600, 500) = 500`; cash clamp: `min(500, 50000/110) = 454`.
Decision: buy 454 at 110.
State update: position +454; cash -49940.

### Case 2 — Momentum reversal sell
System state: `price=95`, `MA_5=105`, `position=200`.
Calculation: `momentum = (95-105)/105 = -0.095`; `-0.095 < -0.02` triggers sell; `q = min(200, 300) = 200`.
Decision: sell 200 at 95.
State update: position -200; cash +19000.

### Case 3 — Hold
System state: `price=101`, `MA_5=100`.
Calculation: `momentum = 0.01`; at threshold boundary — hold.
Decision: hold with quantity 0.
State update: no portfolio change.

### Edge Case — Insufficient history
System state: `price_history` has only 2 observations; `lookback=5`.
Calculation: momentum cannot be computed.
Decision: hold.
State update: unchanged.

## Validation and Calibration

**Calibration data sources**:
- `lookback` <- Jegadeesh & Titman (1993) 3–12 month momentum window, scaled to tick frequency.
- `buy_threshold`, `sell_threshold` <- scenario calibration for bubble onset timing.
- `leverage` <- Adrian & Shin (2010) procyclical leverage ranges.

**Expected individual behaviour**:
- Given positive momentum above threshold and sufficient cash, agent MUST buy.
- Given negative momentum below sell threshold and positive position, agent MUST sell.
- Given momentum inside the band, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells during positive momentum above `buy_threshold` THEN the feedback mechanism is inverted because momentum chasers buy winners.
- IF `leverage` has no effect on buy quantity THEN the leverage amplification channel is broken.
- IF `quantity > base_position_size * leverage` THEN the sizing constraint is broken because orders must be clamped.

#### Ablation Hooks

| Ablation name | Setting                                | Hypothesis tested                        | Expected direction | Metric               |
|---------------|----------------------------------------|------------------------------------------|--------------------|----------------------|
| no-momentum   | `buy_threshold = 999` (never triggers) | Momentum demand drives bubble formation. | no bubble          | peak price deviation |
| no-leverage   | `leverage = 1.0`                       | Leverage amplifies the bubble.           | smaller bubble     | peak price deviation |

## Academic References

| # | Citation                                                                                                                                                                                                  | Notes                             |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| 1 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65–91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                                  | Momentum premium calibration      |
| 2 | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies. *Journal of Finance*, 45(2), 379–395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x | Positive feedback destabilisation |
| 3 | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418–437. https://doi.org/10.1016/j.jfi.2008.12.002                                                | Procyclical leverage calibration  |

## Design Provenance and Versioning

| Field       | Content                                                                          |
|-------------|----------------------------------------------------------------------------------|
| Author      | AGenticFinLab                                                                    |
| Reviewed by | audit_agent_handbook.py v1                                                       |
| Created     | 2026-07-11                                                                       |
| Version     | 1.1.0                                                                            |
| Status      | conformant                                                                       |
| Icon        | ![](../agent_images/icons/finance-momentum-speculator.png)                       |
