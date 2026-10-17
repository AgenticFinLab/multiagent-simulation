# Disposition-effect retail trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Disposition-effect retail trader |
| Theory Family         | Behavioral Finance |
| Behavioral Tendency   | **Diverging — holds losers too long and sells winners too early relative to fundamentals; diverges from the frictionless rebalancing path** |
| Market Role           | **Context-dependent** - sells winners early and withholds or adds to losers |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |
## Definition and Goals

This agent models an individual investor whose reference point is personal cost basis. The real-world counterpart is a retail trader / individual investor exhibiting the disposition effect.

The decision goal is to emit buy, sell, or hold orders from unrealized gain or loss relative to cost basis. It sells winners after a gain threshold and holds or averages down losers because losses are psychologically harder to realize.

In simulation this agent helps produce asymmetric liquidity, momentum-then-reversal patterns, and sustained mispricing around personal reference points. Non-goals: it must not trade on fundamental value, trend signals, or dealer inventory.

## Theoretical Foundation

**Disposition Effect**:
- Theory / Study: Selling winners too early and holding losers too long.
- Citation: Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777-790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Core Insight: Investors prefer realizing gains and avoid realizing losses, causing asymmetric sell decisions around cost basis. This behavior follows reference-dependent preferences.
- Mathematical Formulation: `gain = (P - cost_basis) / cost_basis`.
- Empirical Evidence: Brokerage-account studies show gains are realized more readily than losses.
- Relevance to This Agent: Cost basis is the behavioral anchor for trade direction.
- Calibration Source: Shefrin & Statman (1985).
- Falsification Conditions: If gains and losses trigger symmetric selling, the disposition effect is absent.
- Alternative Theories: Prospect Theory; mental accounting.

**Prospect Theory Reference Dependence**:
- Theory / Study: Prospect Theory value function.
- Citation: Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185
- Core Insight: Outcomes are evaluated relative to a reference point, with losses weighted more heavily than gains. This asymmetry makes realizing losses more aversive than realizing gains.
- Mathematical Formulation: `V(x) = x^alpha if x >= 0; -lambda * (-x)^beta if x < 0`.
- Empirical Evidence: The source scenario uses `lambda` around 2.25 and cites realized gain/loss asymmetry.
- Relevance to This Agent: The cost basis is the reference point that determines gain and loss regions.
- Calibration Source: Kahneman & Tversky (1979); Odean (1998).
- Falsification Conditions: If the agent treats equal gains and losses symmetrically, reference dependence is absent.
- Alternative Theories: disposition effect.

## Design Purpose and Activation Triggers

Purpose: Generate asymmetric order flow from private purchase-price reference points.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `cost_basis` available
- `position` available

Missing-Signal Policy: hold if cost basis is unavailable; initialize cost basis only on a confirmed buy fill.

Activation Triggers:
- `gain_pct > gain_threshold`: submit sell order.
- `gain_pct < -loss_threshold`: submit buy order to average down, if cash allows.
- `<Default>`: hold.

Deactivation Conditions:
- No position and no cash: hibernate.
- Inventory cap reached: hibernate buy side.


Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|---|---|---|
| Large unrealised gain | Becomes more eager to sell (realise the gain) | `gain` exceeds `reference` by a wide margin; selling pressure rises |
| Large unrealised loss | Becomes reluctant to sell (holds the loser) | `gain` is negative; the agent stays in the position hoping to recover `reference` |

Environmental Dependencies: Requires a per-tick `price` feed and a persistent `cost_basis` state initialised from the first fill. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Bull | Stabilising | Profit-taking supplies sell flow into rallies. |
| Bear | Destabilising | Loss realization avoidance reduces sell liquidity or adds averaging-down demand. |

Interaction with other agents: Can offset AnchoredTrader during rallies and reinforce sticky prices during declines.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|---|---|---|---|---|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. |
| `cost_basis` | agent state | `float` | yes | Persistent state; see §3.6.4. |
| `position` | agent state | `float` | yes | Persistent state; see §3.6.4. |
| `cash` | agent state | `float` | yes | Persistent state; see §3.6.4. |
| `identity`, `round` | round header | `str`, `int` | yes | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|---|---|---|---|---|---|
| `action` | enum | {"market", "hold-no-op"} | — | yes | Discrete action selected this call. |
| `quantity` | float | `[0, base_position_size]` | shares | conditional | Order magnitude; 0 when `action = hold`. |
| `price_level` | float | `= price` (market order) | currency | conditional | Execution reference; equals observed `price` for market orders. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

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

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current mark-to-market price |
| `cost_basis` | State | persistent | Reference point for gains and losses |
| `position` | State | persistent | Quantity available to sell |
| `cash` | State | persistent | Constraint on averaging down |

Does NOT use: `fundamental`, `momentum`, `anchor`, peer flow.

#### Core Behavioral Mechanism

1. Maintain weighted-average cost basis after buys.
2. Compute unrealized gain percentage.
3. Sell if gain exceeds `gain_threshold`.
4. Buy additional units if loss exceeds `loss_threshold` and cash is available.
5. Hold inside the asymmetric inaction band.
6. Clip sells by current position.
7. Update cost basis only after buy fills.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current price |
| Order quantity rule | `Q = min(base_position_size, abs(gain_pct) * sizing_scale)` |
| Order lifetime | 1 tick |
| Cancellation policy | unfilled orders expire at end of tick |
| Inventory constraint | no shorting; inventory <= `inventory_max` |
| Wealth / leverage cap | cash >= 0; no margin |
| Stop-loss / kill rule | none |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Trigger function:
  ```
  gain_pct = (P - cost_basis) / cost_basis
  sell if gain_pct > gain_threshold
  buy if gain_pct < -loss_threshold
  otherwise hold
  ```
- Sizing function:
  ```
  Q = min(base_position_size, abs(gain_pct) * sizing_scale)
  ```
- State variables: `cost_basis`; `position`; `cash`.
- State-update rule: update cost basis post-fill on buys; update position and cash post-fill.
- Determinism contract: deterministic given state and parameters.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `theta_g` | gain sale threshold | 0.04 | Shefrin & Statman (1985) |
| `theta_l` | loss averaging-down threshold | 0.016 | Prospect-theory loss aversion calibration |

#### Behavioral Properties

- Time horizon: medium, because cost basis persists.
- Risk tolerance: asymmetric; low in gains and higher in losses.
- Information asymmetry: none.
- Psychological profile: disposition effect and reference dependence.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `gain_threshold` | float | 0.04 | [0, 1] | high | Gain needed to sell. | Higher -> later profit-taking. | Shefrin & Statman (1985) |
| `loss_aversion_mult` | float | 2.5 | > 0 | high | Loss-aversion asymmetry multiplier; derived loss threshold = `gain_threshold / loss_aversion_mult`. | Higher -> less averaging down. | Kahneman & Tversky (1979) |
| `base_position_size` | float | 15.0 | > 0 | medium | Maximum order size. | Higher -> stronger asymmetric liquidity. | Standardised |
| `sizing_scale` | float | 500.0 | > 0 | medium | Converts gain/loss to order size. | Higher -> larger response to P&L. | Standardised |
| `inventory_max` | float | 200.0 | > 0 | low | Maximum long inventory. | Higher -> more averaging-down capacity. | Standardised |

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | iid cost-basis and threshold draws |
| Heterogeneity per parameter | `cost_basis -> entry price`, `gain_threshold -> Uniform(0.03, 0.08)` |
| Cross-agent correlation | none |
| Identity persistence | cost basis persists within episode |

## Worked Numerical Examples

### Case 1 - Sell winner
```text
Market state: P=108, cost_basis=103, gain_threshold=0.04.
Calculation: gain_pct=(108-103)/103=0.049.
Decision: sell min(15, 0.049*500)=15.
State update: position -15; cash +1620; cost_basis unchanged for remaining shares.
```

### Case 2 - Average down loser
```text
Market state: P=97, cost_basis=105, loss_threshold=0.016.
Calculation: gain_pct=-0.076.
Decision: buy 15.
State update: position +15; cash -1455; cost_basis moves toward 97.
```

### Case 3 - Hold near basis
```text
Market state: P=104, cost_basis=103.
Calculation: gain_pct=0.0097.
Decision: hold.
State update: unchanged.
```

### Edge Case - Missing cost basis
```text
Market state: P=100, position=0, cost_basis missing.
Calculation: reference point unavailable.
Decision: hold.
State update: no cost basis until a buy fill occurs.
```

## Behavioral Verification and Calibration

- Given unrealized gain exceeds `gain_threshold`, agent must emit a sell order to realize the profit.
- Given unrealized loss exceeds `loss_threshold`, agent must emit a buy order to average down (if cash permits).
- Given unrealized P&L within the asymmetric inaction band (gain < threshold, loss < threshold), agent must hold.
- Given no position and no cost basis, agent must hold until a buy fill establishes a reference point.
- Given the sell threshold is lower than the loss threshold (in magnitude), agent must sell winners more readily than losers, demonstrating disposition asymmetry.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `symmetric_thresholds` | `loss_aversion_mult = 1.0` | Symmetry removes disposition asymmetry. | decrease | ratio of gain-realizations to loss-realizations |
| `no_average_down` | disable loss buy branch | Loss-domain demand supports price less. | increase | max drawdown during selloffs |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777-790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x | Disposition effect |
| 2 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185 | Reference-point foundation |
| 3 | Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775-1798. https://doi.org/10.1111/0022-1082.00072 | Empirical gain/loss realization asymmetry |
| 4 | Weber, M., & Camerer, C. F. (1998). The disposition effect in securities trading. *Journal of Economic Behavior and Organization*, 33(2), 167-184. https://doi.org/10.1016/S0167-2681(97)00089-9 | Controlled disposition-effect evidence |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AGenticFinLab |
| Reviewed by | QoderWork three-pass self-check |
| Created | 2026-06-27 |
| Version | 1.0.3 |
| Status | conformant |
| Icon        | ![](../agent_images/icons/finance-disposition-trader.png) |
