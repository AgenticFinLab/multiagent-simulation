# Value contrarian investor

## Summary

| Field                 | Content                                                                                          |
|-----------------------|--------------------------------------------------------------------------------------------------|
| Archetype             | Value contrarian investor                                                                        |
| Theory Family         | Value Investing / Crisis Arbitrage                                                               |
| Behavioral Tendency   | **Converging — buys oversold currencies and assets after panic; converges on fundamental value** |
| Market Role           | **Stabilising** — buys when others panic-sell, sells into over-bullish rallies                   |
| Time Horizon          | long                                                                                             |
| Risk Tolerance        | medium-high                                                                                      |
| Information Asymmetry | none                                                                                             |
| Determinism           | deterministic                                                                                    |

## Definition and Goals

This agent models a disciplined long-horizon value investor who buys assets trading below intrinsic value during crisis-driven selloffs and sells when sentiment-driven premiums appear. Real-world counterparts include deep-value hedge funds, sovereign wealth funds, and Buffett-style contrarian capital allocators.

The decision goal is to submit buy orders when `deviation = (P − F) / F` is materially negative (below `oversold_threshold`), and sell orders when the deviation is materially positive (above `overbought_threshold`), while sizing trades proportionally to the magnitude of mispricing.

In simulation this agent provides counter-cyclical liquidity — buying into contagion selloffs and taking profits into hot-money-driven rallies. It forms the second layer of price floor support after the IMF rescuer. Non-goals: it must not chase momentum, follow crowds, or trade on short-horizon noise.

## Theoretical Foundation

**Crisis investing and fundamental value recovery**:
- Theory / Study: Contrarian investing and mean reversion in liquidity crises.
- Citation: Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch 2007–2008. *Journal of Economic Perspectives*, 23(1), 77–100. https://doi.org/10.1257/jep.23.1.77
- Core Insight: In severe liquidity crises, assets trade far below fundamental values due to fire-sale dynamics. Investors with long time horizons and adequate liquidity can earn substantial returns by absorbing forced sales, but they require deep discounts to compensate for execution risk and uncertainty about when prices will recover.
- Mathematical Formulation: `Buy when deviation < -0.08; sell when deviation > +0.10`. Asymmetric thresholds reflect the recovery premium that contrarian investors require.
- Empirical Evidence: Post-crisis studies of 1997 Asian markets show that investors who entered Thai, Korean, and Indonesian equity markets at 40–60% discounts in Q1 1998 earned returns of 100–200% over the following 3 years.
- Relevance to This Agent: `oversold_threshold = -0.08` (8% below F) represents the minimum discount before entry; `overbought_threshold = +0.10` (+10% above F) is the exit point capturing the post-crisis recovery premium.
- Calibration Source: Brunnermeier (2009); Shleifer & Vishny (1997) for limits-to-arbitrage deployment constraints.
- Falsification Conditions: If the agent buys overvaluation or sells undervaluation, the mechanism is inverted.
- Alternative Theories: momentum trading; noise-trader risk; rational inattention.

**Limits to arbitrage and patient capital**:
- Theory / Study: Patient capital and crisis arbitrage under capital constraints.
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Fundamental-value investors face capital constraints that prevent unlimited deployment into deep discounts. Conservative per-round deployment ensures the agent does not exhaust buying power before prices bottom.
- Mathematical Formulation: `q_buy = min(base_position_size, abs(deviation) * sizing_scale)` with `buy_ratio = 0.20` capping per-round cash deployment.
- Empirical Evidence: During the 1997 Asian crisis, even well-capitalised funds deployed capital gradually across multiple rounds rather than in a single decisive entry.
- Relevance to This Agent: The `sizing_scale` and `base_position_size` parameters encode cautious deployment under uncertainty.
- Calibration Source: Shleifer & Vishny (1997); scenario normalization.
- Falsification Conditions: If the agent deploys all cash in a single round, capital constraint is not represented.
- Alternative Theories: unlimited arbitrage; risk-neutral valuation.

## Design Purpose and Activation Triggers

Purpose: Provide long-horizon corrective flow during crisis-driven mispricing episodes.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available
- own `cash` and `position` available

Missing-Signal Policy: hold when either `price` or `fundamental` is missing.

Activation Triggers:
- `deviation < -oversold_threshold`: buy with sized quantity (contrarian entry).
- `deviation > overbought_threshold`: sell (take profit).
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted: hibernate buy side.
- Position is zero and deviation is inside the no-trade band: hold.

Behavioral Adaptation by Condition:
| Condition                                                    | Behavioral change | Mechanism                             |
|--------------------------------------------------------------|-------------------|---------------------------------------|
| Currency oversold beyond `fundamental * (1 - deep_discount)` | Buys aggressively | Sizing proportional to discount depth |
| Currency near fundamental                                    | Holds             | No-trade band                         |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed for the crisis-affected currency. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime             | Contribution | Mechanism                                 |
|--------------------|--------------|-------------------------------------------|
| Contagion selloff  | Stabilising  | Absorbs forced selling at deep discounts. |
| Recovery overshoot | Stabilising  | Sells into over-bullish rallies.          |
| Calm               | Neutral      | Inside no-trade band.                     |

Interaction with other agents: Trades against hot-money sellers during contagion; provides exit liquidity for panic sellers; takes profits from momentum buyers during recovery.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape | Required? | Notes                                                                                       |
|---------------------|--------------|--------------|-----------|---------------------------------------------------------------------------------------------|
| `price`             | environment  | `float`      | yes       | Execution reference and valuation.                                                          |
| `fundamental`       | environment  | `float`      | yes       | Intrinsic value reference.                                                                  |
| `cash`              | agent state  | `float`      | yes       | Buy capacity.                                                                               |
| `position`          | agent state  | `float`      | yes       | Sell capacity.                                                                              |
| `identity`, `round` | round header | `str`, `int` | yes       | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum        | Unit     | Required?   | Meaning                                                         |
|---------------|--------|---------------------------|----------|-------------|-----------------------------------------------------------------|
| `action`      | enum   | {"buy", "sell", "hold"}   | —        | yes         | Discrete action selected this call.                             |
| `quantity`    | float  | `[0, base_position_size]` | shares   | conditional | Order magnitude; 0 when `action = hold`.                        |
| `price_level` | float  | `= price` (market order)  | currency | conditional | Execution reference; equals observed `price` for market orders. |
| `reasoning`   | string | 1–3 sentences             | —        | yes         | Audit trail explaining WHY.                                     |

##### Content Constraints

- Required fields: every row marked `Required? = yes` in the Outputs table MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, base_position_size]`; out-of-range values MUST be clamped by the implementer before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. `price_level` uses the same currency unit as `fundamental` and `price`.
- Determinism markers: the decision determinism class is declared in §3.2 Summary; no seed is emitted unless the decision is `stochastic-given-seed`.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<one of the declared enum values>",
                "quantity": <float>,
                "price_level": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel for `retrieved_knowledge` (e.g. `"(No relevant knowledge retrieved this round.)"`) and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this §3.6.0 I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                                         |
|---------------|------------|---------------|---------------------------------------------------|
| `price`       | Continuous | 1 tick        | Execution reference and valuation input.          |
| `fundamental` | Continuous | 1 tick        | Intrinsic value anchor for deviation computation. |
| `cash`        | State      | persistent    | Buy-side capacity constraint.                     |
| `position`    | State      | persistent    | Sell-side capacity constraint.                    |

Does NOT use: momentum, anchor, cost_basis, peer flow, or private information.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `cash`, and `position`.
2. Compute `deviation = (price - fundamental) / fundamental`.
3. If `deviation < -oversold_threshold`, compute buy quantity: `q = min(base_position_size, abs(deviation) * sizing_scale)`, clamped by `cash / price`.
4. If `deviation > overbought_threshold`, compute sell quantity: `q = min(position, base_position_size)`.
5. Otherwise, hold with `q = 0`.
6. Emit `(action, quantity, price_level, reasoning)`.
7. Update cash and position after execution feedback.

#### Action Space

| Aspect                | Specification                                                                                                            |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                                                                       |
| Price level rule      | market order at current price                                                                                            |
| Order quantity rule   | buy: `min(base_position_size, abs(deviation) * sizing_scale)` clamped by cash; sell: `min(position, base_position_size)` |
| Order lifetime        | 1 tick                                                                                                                   |
| Cancellation policy   | unfilled orders expire at end of tick                                                                                    |
| Inventory constraint  | `position >= 0`; `position <= inventory_max`                                                                             |
| Wealth / leverage cap | `cash >= 0`; no margin                                                                                                   |
| Stop-loss / kill rule | none — patient capital, no forced exit                                                                                   |

#### Mathematical Model

Decision output is `(action, quantity)`.

```
d_t = (P_t - F_t) / F_t
if d_t < -theta_oversold:
    a_t = buy;  q_t = min(Q_max, |d_t| * k_q); clamped by cash/P_t
elif d_t > theta_overbought:
    a_t = sell; q_t = min(position_t, Q_max)
else:
    a_t = hold; q_t = 0
```

State variables: `cash`, `position`, updated post-fill.
Determinism contract: deterministic — same inputs and state produce byte-identical outputs.

| Symbol             | Meaning                               | Default Value | Source                 |
|--------------------|---------------------------------------|---------------|------------------------|
| `theta_oversold`   | buy threshold                         | 0.08          | Brunnermeier (2009)    |
| `theta_overbought` | sell threshold                        | 0.10          | Brunnermeier (2009)    |
| `Q_max`            | max order size (`base_position_size`) | 25.0          | Scenario normalization |
| `k_q`              | sizing scale (`sizing_scale`)         | 800.0         | Scenario normalization |

#### Behavioral Properties

- Time horizon: long, because the agent waits for deep discounts and patient recovery.
- Risk tolerance: medium-high, because the agent buys into crisis but with bounded position sizes.
- Information asymmetry: none, all inputs are public.
- Psychological profile: disciplined, patient, contrarian — buys when others panic.

## Parameters

| Parameter              | Type  | Default | Valid Range  | Sensitivity | Description                                   | Impact                                    | Source                 |
|------------------------|-------|---------|--------------|-------------|-----------------------------------------------|-------------------------------------------|------------------------|
| `oversold_threshold`   | float | 0.08    | [0.03, 0.20] | high        | Deviation below which the agent buys.         | Higher -> deeper entry discount required. | Brunnermeier (2009)    |
| `overbought_threshold` | float | 0.10    | [0.03, 0.25] | high        | Deviation above which the agent sells.        | Higher -> later profit-taking.            | Brunnermeier (2009)    |
| `base_position_size`   | float | 25.0    | [5, 100]     | medium      | Maximum order quantity per tick.              | Higher -> larger per-round deployment.    | Scenario normalization |
| `sizing_scale`         | float | 800.0   | [100, 2000]  | medium      | Converts deviation magnitude into order size. | Higher -> more aggressive sizing.         | Scenario normalization |
| `inventory_max`        | float | 300.0   | [50, 1000]   | low         | Long inventory cap.                           | Higher -> more cumulative exposure.       | Scenario normalization |

## Population and Heterogeneity

| Aspect                         | Specification                             |
|--------------------------------|-------------------------------------------|
| Default population size        | scenario-dependent (typically 1–3)        |
| Parameter heterogeneity policy | identical parameters across instances     |
| Heterogeneity per parameter    | none — representative agent               |
| Cross-agent correlation        | none                                      |
| Identity persistence           | persistent across ticks within an episode |

## Worked Numerical Examples

### Case 1 — Contagion buy
System state: `price=82`, `fundamental=100`, `cash=50000`, `position=0`.
Calculation: `deviation = (82-100)/100 = -0.18`; `-0.18 < -0.08` triggers buy; `q = min(25, 0.18*800) = min(25, 144) = 25`; cash clamp: `min(25, 50000/82) = 25`.
Decision: buy 25 at 82.
State update: position +25; cash -2050.

### Case 2 — Recovery sell
System state: `price=112`, `fundamental=100`, `position=100`.
Calculation: `deviation = (112-100)/100 = +0.12`; `+0.12 > +0.10` triggers sell; `q = min(100, 25) = 25`.
Decision: sell 25 at 112.
State update: position -25; cash +2800.

### Case 3 — Hold in no-trade band
System state: `price=96`, `fundamental=100`.
Calculation: `deviation = -0.04`; `-0.08 < -0.04 < +0.10` — inside the no-trade band.
Decision: hold with quantity 0.
State update: no portfolio change.

### Edge Case — Missing fundamental
System state: `fundamental` unavailable.
Calculation: required signal missing.
Decision: hold.
State update: unchanged.

## Validation and Calibration

**Calibration data sources**:
- `oversold_threshold` <- Brunnermeier (2009) crisis-entry discount ranges (8% below fundamental).
- `overbought_threshold` <- Brunnermeier (2009) recovery-exit premium ranges (10% above fundamental).
- `sizing_scale` <- Shleifer & Vishny (1997) limits-to-arbitrage gradual deployment.

**Expected individual behaviour**:
- Given deviation below -0.08 and sufficient cash, agent MUST buy with positive quantity.
- Given deviation above +0.10 and positive position, agent MUST sell.
- Given deviation inside the band, agent MUST hold.
- Given missing `fundamental`, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys when deviation is positive THEN the value mechanism is inverted because contrarians buy undervaluation.
- IF the agent sells when deviation is below -oversold_threshold THEN the trigger logic is inverted.
- IF `quantity > base_position_size` THEN the sizing constraint is broken because orders must be clamped.

#### Ablation Hooks

| Ablation name     | Setting                                     | Hypothesis tested                        | Expected direction | Metric        |
|-------------------|---------------------------------------------|------------------------------------------|--------------------|---------------|
| no-contrarian-buy | `oversold_threshold = 999` (never triggers) | Contrarian buying provides price floor.  | deeper drawdown    | max drawdown  |
| aggressive-sizing | `sizing_scale = 5000`                       | Larger orders accelerate price recovery. | faster recovery    | recovery time |

## Academic References

| # | Citation                                                                                                                                                                  | Notes                                      |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| 1 | Brunnermeier, M. K. (2009). Deciphering the liquidity and credit crunch 2007–2008. *Journal of Economic Perspectives*, 23(1), 77–100. https://doi.org/10.1257/jep.23.1.77 | Crisis investing and mean reversion        |
| 2 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                     | Capital constraints and gradual deployment |
| 3 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                                                                          | Foundational value-investing framework     |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | AGenticFinLab                                                                                                                                                                                                                          |
| Reviewed by | audit_agent_handbook.py v1                                                                                                                                                                                                             |
| Created     | 2026-06-11                                                                                                                                                                                                                             |
| Version     | 1.1.0                                                                                                                                                                                                                                  |
| Status      | conformant                                                                                                                                                                                                                             |
| Icon        | ![](../agent_images/icons/finance-value-contrarian.png)                                                                                                                                                                                |
