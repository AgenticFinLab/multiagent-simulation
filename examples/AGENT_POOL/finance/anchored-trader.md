# Anchoring-bias retail trader

## Summary

| Field                 | Content                                                                                                                                                                                      |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Anchoring-bias retail trader                                                                                                                                                                 |
| Theory Family         | Behavioral Finance                                                                                                                                                                           |
| Behavioral Tendency   | **Converging** — trades toward a perceived target, but the target itself is biased toward the initial anchor, so the agent converges on an anchor-pulled level rather than fundamental value |
| Time Horizon          | medium                                                                                                                                                                                       |
| Risk Tolerance        | medium                                                                                                                                                                                       |
| Information Asymmetry | none                                                                                                                                                                                         |
| Determinism           | deterministic                                                                                                                                                                                |

## Definition and Goals

This agent models a retail trader or buy-side analyst who anchors on the first salient market price and adjusts insufficiently toward observable fundamental value. The real-world counterpart is a retail trader, individual investor, or analyst whose valuation remains pulled toward an initial quote — the canonical anchoring subject of Tversky & Kahneman (1974) and the forecast-anchoring professional of Campbell & Sharpe (2009).

The decision goal is to emit a buy, sell, or hold order with quantity determined by the perceived deviation between price and an anchor-biased target. It follows a heuristic criterion rather than expected-value optimisation: trade around `anchor + alpha * (fundamental - anchor)`, not around the true fundamental.

In simulation this agent helps produce sustained mispricing relative to fundamentals, slow price discovery, and short-run return persistence. Non-goals: it must not trade directly on momentum, provide two-sided liquidity, or fully converge to fundamental value when `alpha < 1`.

## Theoretical Foundation

**Anchoring and Insufficient Adjustment**:
- Theory / Study: Anchoring heuristic in numerical estimation.
- Citation: Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124-1131. https://doi.org/10.1126/science.185.4157.1124
- Core Insight: People start from a salient anchor and adjust too little, even when the anchor is arbitrary. In markets this creates valuations that remain biased toward first-observed prices.
- Mathematical Formulation: `target = anchor + alpha * (F - anchor)`.
- Empirical Evidence: Classic anchoring experiments show large shifts in median estimates after exposure to arbitrary anchors; financial-forecast under-revision of 30–70% with forecast-error autocorrelation around 0.4 (Campbell & Sharpe 2009).
- Relevance to This Agent: The agent operationalises insufficient adjustment by trading around an anchor-biased fair value.
- Calibration Source: Tversky & Kahneman (1974), with financial forecast underreaction interpreted as `alpha < 1`; Campbell & Sharpe (2009) 3% noise band.
- Falsification Conditions: If the agent trades as if `target = F` (i.e. `alpha = 1`), anchoring is absent — the agent's target must remain measurably displaced from `F` by at least `(1 - alpha) * |anchor - F|`.
- Alternative Theories: Rational expectations; conservatism / underreaction.

**Consensus Forecast Anchoring**:
- Theory / Study: Anchoring bias in consensus forecasts.
- Citation: Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369-390. https://doi.org/10.1017/S0022109009090127
- Core Insight: Professional forecasts revise only partially toward new information, leaving predictable forecast errors. The source scenario uses this mechanism to connect individual anchoring to market-level slow price discovery.
- Mathematical Formulation: `forecast_revision = theta * (new_information - prior_forecast)`.
- Empirical Evidence: Under-revision of roughly 30–70% and forecast-error autocorrelation around 0.4 (Campbell & Sharpe 2009, Table 2).
- Relevance to This Agent: The agent's `alpha` parameter is the trading-rule analogue of partial forecast revision.
- Calibration Source: Campbell & Sharpe (2009), as cited in `simulation-bases.md`; 3% noise band.
- Falsification Conditions: If lowering `alpha` does not increase mispricing persistence, forecast anchoring is not represented — the half-life of price deviations must monotonically increase as `alpha` decreases.
- Alternative Theories: Rational expectations.

## Design Purpose and Activation Triggers

Purpose: Generate persistent upward or downward price support around a biased reference price.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `anchor` initialized from a valid first price

Missing-Signal Policy: hold until `price` and `fundamental` are valid; initialize `anchor` from the first valid price.

Activation Triggers:
- `perceived_dev < -threshold`: submit buy order.
- `perceived_dev > threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached: hibernate the side that would increase the breach.
- Cash floor breached: hold buy side until cash recovers.

Behavioral Adaptation by Condition:
| Condition                     | Behavioral change                                                             | Mechanism                                                                              |
|-------------------------------|-------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| High volatility regime        | Widens effective no-trade band via larger `perceived_dev` for same price move | `perceived_dev` computed relative to sticky target; volatility does not enter the rule |
| Prolonged one-sided deviation | Continues to trade around the biased target without re-anchoring              | `anchor` is persistent state; no automatic reset                                       |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed from the environment, plus a one-time initialisation of `anchor` from the first valid price. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution  | Mechanism                                                               |
|--------|---------------|-------------------------------------------------------------------------|
| Calm   | Destabilising | Keeps price near the anchor-biased target instead of fundamental value. |
| Stress | Destabilising | Slows correction after shocks because the anchor remains sticky.        |

Interaction with other agents: Opposes RationalUpdater and FundamentalAnalyst; can be amplified by MomentumTrader.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape | Required? | Notes                                                                                       |
|---------------------|--------------|--------------|-----------|---------------------------------------------------------------------------------------------|
| `price`             | environment  | `float`      | yes       | Current tradable price; maps to §3.6.1 `price`.                                             |
| `fundamental`       | environment  | `float`      | yes       | True value; maps to §3.6.1 `fundamental`.                                                   |
| `anchor`            | agent state  | `float`      | yes       | Persistent state; initialised from first valid `price` per §3.6.4.                          |
| `identity`, `round` | round header | `str`, `int` | yes       | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum        | Unit     | Required?   | Meaning                                                         |
|---------------|--------|---------------------------|----------|-------------|-----------------------------------------------------------------|
| `action`      | enum   | `{"buy", "sell", "hold"}` | —        | yes         | Discrete action selected this call.                             |
| `quantity`    | float  | `[0, base_position_size]` | shares   | conditional | Order magnitude; 0 when `action = hold`.                        |
| `price_level` | float  | `= price` (market order)  | currency | conditional | Execution reference; equals observed `price` for market orders. |
| `reasoning`   | string | 1–3 sentences             | —        | yes         | Audit trail explaining WHY.                                     |

##### Content Constraints

- Required fields: every row marked `Required? = yes` in the Outputs table MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, base_position_size]`; out-of-range values MUST be clamped by the implementer before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. `price_level` uses the same currency unit as `fundamental` and `price`.
- Determinism markers: the decision is deterministic given signals, state, and parameters; no seed is emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|sell|hold>",
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

| Signal        | Type       | Memory Window | Rationale                                       |
|---------------|------------|---------------|-------------------------------------------------|
| `price`       | Continuous | 1 tick        | Current tradable price                          |
| `fundamental` | Continuous | 1 tick        | True value used only through partial adjustment |
| `anchor`      | State      | persistent    | First observed reference price                  |

Does NOT use: `prev_price`, `momentum`, order-book depth, peer flow.

#### Core Behavioral Mechanism

1. Read: `price`, `fundamental`, `anchor`. If `anchor` is unset (cold start), Write: `anchor <- price`. (§3.4 — anchoring)
2. Compute: `target = anchor + alpha * (fundamental - anchor)`. (§3.4 — insufficient adjustment)
3. Compute: `perceived_dev = (price - target) / target`. (§3.4 — biased valuation)
4. If `perceived_dev < -threshold`: emit `action = buy`, `quantity = min(base_position_size, abs(perceived_dev) * sizing_scale)`. (§3.4 — buy below target)
5. Else if `perceived_dev > threshold`: emit `action = sell`, `quantity = min(base_position_size, abs(perceived_dev) * sizing_scale)`. (§3.4 — sell above target)
6. Else: emit `action = hold`, `quantity = 0`. (§3.4 — no-trade band)
7. Post-fill: Write: `position <- position + signed(quantity)`; `cash <- cash - signed(quantity) * price`. (Implementation convenience — accounting.)

#### Action Space

| Aspect                | Specification                                                    |
|-----------------------|------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                               |
| Price level rule      | market order at current observed price                           |
| Order quantity rule   | `Q = min(base_position_size, abs(perceived_dev) * sizing_scale)` |
| Order lifetime        | 1 tick                                                           |
| Cancellation policy   | unfilled orders expire at end of tick; re-evaluate next tick     |
| Inventory constraint  | no order may increase absolute inventory above `inventory_max`   |
| Wealth / leverage cap | cash >= 0; no margin                                             |
| Stop-loss / kill rule | none                                                             |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Trigger function:
  ```
  target = anchor + alpha * (F - anchor)
  perceived_dev = (P - target) / target
  buy if perceived_dev < -theta
  sell if perceived_dev > theta
  otherwise hold
  ```
- Sizing function:
  ```
  Q = sign(-perceived_dev) * min(base_position_size, abs(perceived_dev) * sizing_scale)
  ```
- State variables: `anchor` float initialized from first valid price; `position` float; `cash` float.
- State-update rule: `anchor` updates pre-decision only at cold start; `position` and `cash` update post-fill.
- Determinism contract: deterministic given signals, state, and parameters.

| Symbol  | Meaning                                | Default Value | Source                    |
|---------|----------------------------------------|---------------|---------------------------|
| `alpha` | adjustment fraction toward fundamental | 0.30          | Tversky & Kahneman (1974) |
| `theta` | perceived deviation threshold          | 0.03          | Campbell & Sharpe (2009)  |

#### Behavioral Properties

- Time horizon: medium, because the anchor persists across many ticks.
- Risk tolerance: medium, because orders are capped and thresholded.
- Information asymmetry: none; the bias is cognitive, not informational.
- Psychological profile: anchoring and insufficient adjustment.

## Parameters

| Parameter            | Type  | Default | Valid Range | Sensitivity | Description                                                            | Impact                                                                      | Source                    |
|----------------------|-------|---------|-------------|-------------|------------------------------------------------------------------------|-----------------------------------------------------------------------------|---------------------------|
| `alpha`              | float | 0.30    | [0, 1]      | high        | Fraction of the anchor-fundamental gap incorporated into target value. | Higher -> weaker anchoring and faster correction.                           | Tversky & Kahneman (1974) |
| `threshold`          | float | 0.03    | [0, 1]      | high        | No-trade band around perceived target.                                 | Higher -> fewer trades and more persistent mispricing.                      | Campbell & Sharpe (2009)  |
| `base_position_size` | float | 20.0    | > 0         | medium      | Maximum order size.                                                    | Higher -> stronger price pressure from the biased target.                   | Standardised              |
| `sizing_scale`       | float | 1000.0  | > 0         | medium      | Converts perceived deviation into quantity.                            | Higher -> more aggressive reaction to perceived cheapness or expensiveness. | Standardised              |
| `inventory_max`      | float | 200.0   | > 0         | low         | Self-imposed inventory cap.                                            | Higher -> longer sustained biased exposure.                                 | Standardised              |

## Population and Heterogeneity

| Aspect                         | Specification                                                      |
|--------------------------------|--------------------------------------------------------------------|
| Default population size        | scenario-dependent                                                 |
| Parameter heterogeneity policy | shared point value or iid narrow draw around `alpha`               |
| Heterogeneity per parameter    | `alpha -> Uniform(0.25, 0.40)`, `threshold -> Uniform(0.02, 0.04)` |
| Cross-agent correlation        | none                                                               |
| Identity persistence           | identical across episodes unless the scenario redraws parameters   |

## Worked Numerical Examples

### Case 1 - Buy below perceived target
```text
Market state: P=98, F=100, anchor=105, alpha=0.30, theta=0.03.
Calculation: target=105+0.30*(100-105)=103.5; perceived_dev=(98-103.5)/103.5=-0.053.
Decision: buy min(20, 0.053*1000)=20 at P=98.
State update: position +20; cash -1960; anchor remains 105.
```

### Case 2 - Sell above perceived target
```text
Market state: P=108, F=100, anchor=105.
Calculation: target=103.5; perceived_dev=(108-103.5)/103.5=0.043.
Decision: sell min(20, 0.043*1000)=20 at P=108.
State update: position -20; cash +2160; anchor remains 105.
```

### Case 3 - Hold inside band
```text
Market state: P=102, F=100, anchor=105.
Calculation: target=103.5; perceived_dev=-0.0145, which is inside +/-0.03.
Decision: hold.
State update: no inventory or cash change; anchor remains 105.
```

### Edge Case - Cold start
```text
Market state: P=105, F=100, anchor unset.
Calculation: initialize anchor=105, then target=103.5 and perceived_dev=0.0145.
Decision: hold because the signal is inside the band.
State update: anchor becomes persistent state for later ticks.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `alpha` <- Tversky & Kahneman (1974).
- `threshold` <- Campbell & Sharpe (2009): 3% noise band cited in source scenario.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given `anchor = F` and `price = F`, agent MUST hold (perceived_dev = 0).
- Given `anchor > F` and `price = F`, agent MUST perceive the target above `F` and be biased toward selling less aggressively than a rational agent.
- Given `price` crossing `target + threshold`, agent MUST flip from hold to sell in a single tick.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent's target equals `fundamental` on every tick (i.e. `target == F`) THEN anchoring is absent because `alpha` is being applied as 1.0.
- IF `anchor` changes on any tick after cold-start initialisation THEN the persistent-state contract is broken because the anchor must not drift.
- IF the agent emits an order whose `quantity` exceeds `base_position_size` or violates `inventory_max` THEN the self-imposed constraint is broken because sizing must be clamped.

#### Ablation Hooks

| Ablation name    | Setting       | Hypothesis tested                                   | Expected direction | Metric                                |
|------------------|---------------|-----------------------------------------------------|--------------------|---------------------------------------|
| `no_anchor_bias` | `alpha = 1.0` | Removing anchoring collapses persistent mispricing. | decrease           | half-life of price deviation from `F` |
| `strong_anchor`  | `alpha = 0.1` | Stronger anchoring increases deviation half-life.   | increase           | half-life of price deviation from `F` |

## Academic References

| # | Citation                                                                                                                                                                                                                    | Notes                                                   |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| 1 | Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124-1131. https://doi.org/10.1126/science.185.4157.1124                                                       | Anchoring foundation                                    |
| 2 | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369-390. https://doi.org/10.1017/S0022109009090127 | Financial forecast anchoring                            |
| 3 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185                                                                    | Reference-point psychology cited in source scenario     |
| 4 | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0                                             | Conservatism and underreaction cited in source scenario |

## Design Provenance and Versioning

| Field       | Content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Author      | AGenticFinLab                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Reviewed by | QoderWork three-pass self-check |
| Created     | 2026-06-27                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Version     | 1.1.2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Status      | conformant                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Icon        | ![](../agent_images/icons/finance-anchored-trader.png)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
