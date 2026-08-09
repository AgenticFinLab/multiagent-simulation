# Value Trader

## Summary

| Field                 | Content                                                                                                         |
|-----------------------|-----------------------------------------------------------------------------------------------------------------|
| Archetype             | Value trader                                                                                                    |
| Theory Family         | Value Investing / Margin of Safety                                                                              |
| Behavioral Tendency   | **Converging — trades strictly on the gap between price and fundamental value; converges on fundamental value** |
| Market Role           | **Stabilising** — provides fundamental-anchored trading pressure that counteracts availability-bias mispricing  |
| Time Horizon          | medium-long                                                                                                     |
| Risk Tolerance        | low                                                                                                             |
| Information Asymmetry | none                                                                                                            |
| Determinism           | deterministic                                                                                                   |

## Definition and Goals

This agent models a patient value investor who trades only when the price-fundamental gap is large enough to represent a clear margin of safety. The real-world counterpart is a Graham-style value investor who ignores noisy or salient information and trades strictly on the deviation between price and intrinsic value.

The decision goal is to buy when `deviation = (fundamental - price) / price` exceeds a threshold representing a sufficient margin of safety, and to sell when the premium is large enough to take profits. The agent does not short-sell.

In simulation this agent provides stabilising fundamental-anchored demand that counteracts availability-bias overreaction. Non-goals: it must not chase momentum, overweight recent events, or trade on salience cues.

## Theoretical Foundation

**Margin of safety and intrinsic value**:
- Theory / Study: Fundamental value investing with explicit margin-of-safety discipline.
- Citation: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill. Also: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.
- Core Insight: Every security has an intrinsic value determinable from earnings capacity and future cash flows. The rational investor buys only when market price is substantially below intrinsic value, ensuring a margin of safety that protects against estimation error and adverse outcomes.
- Mathematical Formulation: `trade_signal = (F(t) - P(t)) / P(t)`; buy when signal > `theta_buy` (typically 5%).
- Empirical Evidence: Value strategies (low P/B, high dividend yield) earn long-run excess returns (Fama & French 1992); Graham's net-net portfolio earned 20%+ annual returns over 30 years.
- Relevance to This Agent: The agent buys only at a significant discount and holds patiently until the gap closes or reverses.
- Calibration Source: Graham & Dodd (1934); Graham (1949); Fama & French (1992).
- Falsification Conditions: If the agent sells when price is below fundamental, the value mechanism is inverted.
- Alternative Theories: momentum trading; noise-trader risk; rational inattention.

**Contrast with availability-biased trading**:
- Theory / Study: Availability heuristic vs. disciplined value investing.
- Citation: Tversky, A., & Kahneman, D. (1973). Availability: A heuristic for judging frequency and probability. *Cognitive Psychology*, 5(2), 207–232. https://doi.org/10.1016/0010-0285(73)90033-9
- Core Insight: Availability-biased agents overweight recent or vivid events. The value trader represents the antithesis — an agent that ignores recency and salience, trading only on the objective price-fundamental gap.
- Mathematical Formulation: `decision = f(F - P)` only; `decision != f(recent_events, media_salience)`.
- Empirical Evidence: Value investors systematically outperform heuristic-driven traders over long horizons because they buy when others panic and hold when others chase (Fama & French 1992).
- Relevance to This Agent: Provides the theoretical contrast defining the AvailabilityBias scenario — value trader vs. availability-biased agents.
- Calibration Source: Tversky & Kahneman (1973); used as theoretical contrast.
- Falsification Conditions: If the agent's trading frequency correlates with recent event salience rather than price-fundamental deviation, the value discipline is contaminated.
- Alternative Theories: Availability heuristic; recency bias; representativeness.

## Design Purpose and Activation Triggers

Purpose: Provide patient fundamental-anchored trading that counteracts availability-bias mispricing.

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
| Condition                   | Behavioral change                      | Mechanism                               |
|-----------------------------|----------------------------------------|-----------------------------------------|
| Large fundamental deviation | Trades aggressively toward fundamental | Sizing proportional to `abs(deviation)` |
| Small deviation             | Holds inside the discipline band       | `abs(deviation) < threshold`            |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime                         | Contribution | Mechanism                                   |
|--------------------------------|--------------|---------------------------------------------|
| Availability-bias overreaction | Stabilising  | Buys when biased agents oversell.           |
| Crash                          | Stabilising  | Provides fundamental-anchored demand floor. |
| Calm                           | Neutral      | Price near fundamental; minimal trading.    |

Interaction with other agents: Trades against availability-biased agents (recent-event-overweighter, media-influenced-trader); complements the systematic analyst.

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

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim into the `<analysis>` block when retrieval returns empty.

##### Implementer Contract Reminder

Implementers MUST re-open this §3.6.0 I/O Contract during every coding pass as the single source of truth.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale               |
|---------------|------------|---------------|-------------------------|
| `price`       | Continuous | 1 tick        | Execution reference.    |
| `fundamental` | Continuous | 1 tick        | Intrinsic value anchor. |
| `cash`        | State      | persistent    | Buy constraint.         |
| `position`    | State      | persistent    | Sell constraint.        |

Does NOT use: recent_events, media_salience, anchor, momentum, peer flow.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `cash`, `position`.
2. Compute `deviation = (fundamental - price) / price`.
3. If `deviation > buy_threshold`, compute buy quantity: `q = min(base_position_size, deviation * sizing_scale)`, clamped by `cash / price`.
4. If `deviation < -sell_threshold` and `position > 0`, sell: `q = min(position, base_position_size)`.
5. Otherwise hold.
6. Emit decision and update state post-fill.

#### Action Space

| Aspect                | Specification                                                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                                                |
| Price level rule      | market order at current price                                                                     |
| Order quantity rule   | buy: `min(base_size, deviation * sizing_scale)` clamped by cash; sell: `min(position, base_size)` |
| Order lifetime        | 1 tick                                                                                            |
| Cancellation policy   | unfilled orders expire                                                                            |
| Inventory constraint  | `position >= 0`; no short-selling                                                                 |
| Wealth / leverage cap | `cash >= 0`; no margin                                                                            |
| Stop-loss / kill rule | none — patient value holder                                                                       |

#### Mathematical Model

```
dev_t = (F_t - P_t) / P_t
if dev_t > theta_buy:
    a_t = buy;  q_t = min(Q_max, dev_t * k_q); clamped by cash/P_t
elif dev_t < -theta_sell and position_t > 0:
    a_t = sell; q_t = min(position_t, Q_max)
else:
    a_t = hold; q_t = 0
```

| Symbol               | Meaning                  | Default Value | Source                 |
|----------------------|--------------------------|---------------|------------------------|
| `theta_buy`          | buy deviation threshold  | 0.05          | Graham & Dodd (1934)   |
| `theta_sell`         | sell deviation threshold | 0.10          | Scenario calibration   |
| `sizing_scale`       | quantity scale           | 3500.0        | Scenario normalization |
| `base_position_size` | max order                | 200.0         | Scenario normalization |

#### Behavioral Properties

- Time horizon: medium-long, because value takes time to be reflected in price.
- Risk tolerance: low, because the agent avoids leverage and short-selling.
- Information asymmetry: none, all inputs are public.
- Psychological profile: patient, disciplined, fundamental-anchored.

## Parameters

| Parameter            | Type  | Default | Valid Range  | Sensitivity | Description                                         | Impact                            | Source                 |
|----------------------|-------|---------|--------------|-------------|-----------------------------------------------------|-----------------------------------|------------------------|
| `buy_threshold`      | float | 0.05    | [0.02, 0.15] | high        | Discount required before buying (margin of safety). | Higher -> fewer but deeper buys.  | Graham & Dodd (1934)   |
| `sell_threshold`     | float | 0.10    | [0.03, 0.20] | medium      | Premium required before selling.                    | Higher -> more patient holding.   | Scenario calibration   |
| `sizing_scale`       | float | 3500.0  | [500, 8000]  | medium      | Converts deviation to quantity.                     | Higher -> larger orders.          | Scenario normalization |
| `base_position_size` | float | 200.0   | [50, 500]    | medium      | Maximum order quantity.                             | Higher -> larger per-tick impact. | Scenario normalization |

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
Calculation: `deviation = (100-90)/90 = 0.111`; `0.111 > 0.05` triggers buy; `q = min(200, 0.111*3500) = min(200, 388.9) = 200`; cash clamp: `min(200, 50000/90) = 200`.
Decision: buy 200 at 90.
State update: position +200; cash -18000.

### Case 2 — Hold at fair value
System state: `price=100`, `fundamental=100`.
Calculation: `deviation = 0`; inside no-trade band.
Decision: hold.

### Case 3 — Sell overvalued
System state: `price=115`, `fundamental=100`, `position=100`.
Calculation: `deviation = (100-115)/115 = -0.130`; `-0.130 < -0.10` triggers sell; `q = min(100, 200) = 100`.
Decision: sell 100 at 115.
State update: position -100; cash +11500.

### Edge Case — Missing fundamental
Decision: hold.

## Validation and Calibration

**Calibration data sources**:
- `buy_threshold` <- Graham & Dodd (1934) margin-of-safety ranges; 5% is the canonical minimum discount.
- `sell_threshold` <- scenario calibration for profit-taking timing.

**Expected individual behaviour**:
- Given price below fundamental by >5%, agent MUST buy.
- Given price above fundamental by >10% with position, agent MUST sell.
- Given price near fundamental, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells when price is below fundamental THEN the value mechanism is inverted because value investors buy undervaluation.
- IF the agent trades on recent event salience rather than price-fundamental deviation THEN availability bias is contaminating the value discipline.
- IF `quantity > base_position_size` THEN the sizing constraint is broken.

#### Ablation Hooks

| Ablation name   | Setting                 | Hypothesis tested                                                            | Expected direction           | Metric                         |
|-----------------|-------------------------|------------------------------------------------------------------------------|------------------------------|--------------------------------|
| no-value-trader | `buy_threshold = 999`   | Removing value-trader demand allows availability-bias mispricing to persist. | larger mispricing            | mean absolute deviation from F |
| patient-value   | `sell_threshold = 0.50` | More patient holding stabilises post-crash recovery.                         | slower but steadier recovery | recovery time                  |

## Behavioral Verification and Calibration

- Given price more than 5% below fundamental (deviation > buy_threshold), agent must emit a buy order with quantity proportional to deviation * sizing_scale, capped at base_position_size.
- Given price more than 10% above fundamental (deviation < -sell_threshold) with positive position, agent must emit a sell order capped at min(position, base_position_size).
- Given price near fundamental (deviation inside the no-trade band), agent must hold with zero quantity regardless of recent event salience or media signals.
- Given identical price-fundamental deviations but differing recent-event histories, agent must produce byte-identical outputs because it ignores availability cues.
- Given missing fundamental signal, agent must hold and emit no order.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| tight-entry | `buy_threshold = 0.02` | Lower buy threshold increases value-demand frequency, reducing availability-bias mispricing duration. | decrease | mean absolute deviation from fundamental |
| low-sizing | `sizing_scale = 1000` | Reducing sizing aggressiveness weakens fundamental-anchored demand, allowing mispricing to persist. | increase | half-life of price-fundamental deviation |

## Academic References

| # | Citation                                                                                                                                                                                 | Notes                                |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| 1 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                                                                                         | Intrinsic value and margin of safety |
| 2 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                                                                                                                        | Disciplined value investing          |
| 3 | Fama, E. F., & French, K. R. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427–465. https://doi.org/10.1111/j.1540-6261.1992.tb04299.x               | Value premium empirical evidence     |
| 4 | Tversky, A., & Kahneman, D. (1973). Availability: A heuristic for judging frequency and probability. *Cognitive Psychology*, 5(2), 207–232. https://doi.org/10.1016/0010-0285(73)90033-9 | Availability heuristic contrast      |

## Design Provenance and Versioning

| Field       | Content                                                                               |
|-------------|---------------------------------------------------------------------------------------|
| Author      | AGenticFinLab                                                                         |
| Reviewed by | QoderWork three-pass self-check |
| Created     | 2026-07-11                                                                            |
| Version     | 1.1.0                                                                                 |
| Status      | conformant                                                                            |
| Icon        | ![](../agent_images/icons/finance-value-trader.png)                                   |
