# Recent-event overweighter

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Recent-event overweighter |
| Theory Family         | Behavioral Finance |
| Market Role           | **Destabilising** - converts vivid recent returns into directional order flow |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an active retail trader or short-horizon discretionary investor who treats the most recent price move as disproportionately informative. The real-world counterpart is a salient-news or recent-return chasing trader whose attention is captured by the latest vivid market event.

The decision goal is to emit one bounded buy, sell, or hold order based on a salience-weighted blend of most recent return and objective price-fundamental deviation. It intentionally differs from a pure momentum trader: the recent return is overweighted because it is cognitively available, while the deviation remains in the signal to represent the base-rate information that is neglected but not fully ignored.

Inside a market simulation this agent amplifies the first leg of overreaction and can turn a random or media-driven move into temporary mispricing. Non-goals: it must not use private information, it must not update a multi-period valuation model, and it must not provide stabilising fundamental liquidity.

## Theoretical Foundation

**Availability heuristic**:
- Theory / Study: Availability heuristic in probability estimation.
- Citation: Tversky, A., & Kahneman, D. (1973). Availability: A heuristic for judging frequency and probability. *Cognitive Psychology*, 5(2), 207-232. https://doi.org/10.1016/0010-0285(73)90033-9
- Core Insight: Easily recalled events are judged as more likely than their objective frequency warrants. In markets, a recent vivid return becomes a probability cue rather than merely an observation.
- Mathematical Formulation: `perceived_signal = recency_weight * return_pct + (1 - recency_weight) * deviation`.
- Empirical Evidence: De Bondt and Thaler (1985) document return reversals after extreme prior performance, consistent with overreaction to salient prior returns.
- Relevance to This Agent: The agent places high weight on `return_pct` and trades when the blended signal crosses a salience threshold.
- Calibration Source: Tversky and Kahneman (1973); De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.2307/2327804
- Falsification Conditions: If the agent does not increase directional trading after large recent returns, the availability channel is absent.
- Alternative Theories: pure momentum trading; representativeness; rational Bayesian learning.

**Short-term momentum parent mechanism**:
- Theory / Study: Returns to buying winners and selling losers.
- Citation: Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Recent returns can predict short-horizon continuation. This agent forks the momentum-trader parent by adding an explicit base-rate/deviation component and interpreting the return channel as cognitive availability.
- Mathematical Formulation: `return_pct = (P_t - P_{t-1}) / P_{t-1}`.
- Empirical Evidence: Winner-minus-loser strategies show positive intermediate-horizon returns in U.S. equities.
- Relevance to This Agent: Recent return is the salience input, but not the only input.
- Calibration Source: Parent pool file `examples/AGENT_POOL/finance/momentum-trader.md`.
- Falsification Conditions: If the agent trades solely on `deviation` and ignores `return_pct`, it collapses into a rational updater.
- Alternative Theories: reversal trading; value investing.

## Design Purpose and Activation Triggers

Purpose: Amplify recent vivid price moves through availability-biased demand.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `prev_price` available
- `return_pct` available or computable from price history
- `deviation` available

Missing-Signal Policy: hold if any required market signal is missing, NaN, or stale.

Activation Triggers:
- `perceived_signal > salience_threshold`: submit buy order.
- `perceived_signal < -salience_threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- Cash floor breached: hibernate buy side.
- Inventory cap reached: hibernate sell side.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Mixed | Holds while recent returns are small. |
| Salient news / large return | Destabilising | Overweights the most available recent event and reinforces the move. |

Environmental Dependencies: requires broadcast `price`, `prev_price`, `return_pct`, and `deviation`; no peer-network topology required.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment broadcast | `float` | yes | execution reference |
| `prev_price` | environment broadcast | `float` | yes | computes latest return if needed |
| `return_pct` | environment broadcast | `float` | yes | primary availability signal |
| `deviation` | environment broadcast | `float` | yes | objective base-rate signal |
| `cash` | agent state | `float` | yes | buy-side constraint |
| `position` | agent state | `float` | yes | sell-side constraint |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | - | yes | selected trade direction |
| `bid_price` | float | `> 0` | price units | yes | current executable price reference |
| `quantity` | float | `[0, max_order]` | shares | yes | bounded order size |
| `reasoning` | string | 1-3 sentences | - | yes | audit trail |

##### Content Constraints

Required fields must be present on every call, extra fields are not emitted, numeric values are clamped to the declared range, and sign is represented only by `action` rather than negative quantity.

##### Serialization Format

Every implementation variant serializes decisions as `<analysis>...</analysis><decision>{"action":"buy|sell|hold","bid_price":100.0,"quantity":0.0,"reasoning":"..."}</decision>`. Retrieval-augmented variants use `"(No relevant knowledge retrieved this round.)"` when retrieval is empty.

##### Implementer Contract Reminder

Implementation must read every input from the market broadcast or agent state, must emit the exact output field set, must clamp `quantity`, and must keep Rule, LLM, RuleLLM, and Rag variants field-compatible.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `return_pct` | Continuous | 1 tick | Most recent vivid market event, availability cue. |
| `deviation` | Continuous | 1 tick | Objective price-fundamental base rate. |
| `price` | Continuous | 1 tick | Execution reference. |
| `cash` | State | persistent | Buy constraint. |
| `position` | State | persistent | Sell constraint. |

Does NOT use: private news, order book depth, multi-period valuation model, peer topology.

#### Core Behavioral Mechanism

1. Read `return_pct`, `deviation`, `price`, `cash`, and `position`.
2. Compute `perceived_signal = recency_weight * return_pct + (1 - recency_weight) * deviation`.
3. If `abs(perceived_signal) <= salience_threshold`, write no state changes and emit hold.
4. If `perceived_signal > salience_threshold`, compute candidate buy quantity.
5. If `perceived_signal < -salience_threshold`, compute candidate sell quantity.
6. Compute `quantity = min(max_order, abs(perceived_signal) * quantity_scale)`.
7. Clamp buy quantity by `cash / price`; clamp sell quantity by `position`.
8. Emit the resulting order and update cash/position only after execution feedback.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | `buy`, `sell`, `hold` |
| Action parameter rule | `bid_price = price` |
| Sizing rule | `quantity = min(max_order, abs(perceived_signal) * quantity_scale)` then portfolio clamp |
| Action lifetime | one decision interval |
| Revision policy | replaces prior intent each tick |
| State constraint | `position >= 0` unless scenario explicitly permits shorts |
| Resource cap | buy quantity cannot exceed `cash / price` |
| Exit rule | hold when required signals are missing or portfolio cap binds |

#### Mathematical Model

Decision output is `(action, bid_price, quantity)`.

`s_t = rho * r_t + (1 - rho) * d_t`

If `s_t > theta_s`, action is buy. If `s_t < -theta_s`, action is sell. Otherwise action is hold. Quantity is `q_t = min(q_max, |s_t| * k_q)` and then clamped by cash or position.

State variables: `cash` and `position`, updated after execution. Determinism contract: deterministic given identical inputs and state.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `rho` | recency weight | 0.70 | Tversky & Kahneman (1973) |
| `theta_s` | salience threshold | 0.02 | De Bondt & Thaler (1985) |
| `k_q` | quantity scale | 5000.0 | scenario normalization |
| `q_max` | max order | 300.0 | scenario normalization |

#### Behavioral Properties

- Time horizon: short, because the agent reacts to the latest return.
- Risk tolerance: high, because it reinforces salient moves before confirming fundamentals.
- Information asymmetry: none, all inputs are public.
- Psychological profile: availability-biased, recency-sensitive, overreactive.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `recency_weight` | float | 0.70 | `[0, 1]` | high | Weight on most recent return. | Higher -> more trend amplification from recent events. | Tversky & Kahneman (1973) |
| `salience_threshold` | float | 0.02 | `[0, 0.20]` | high | Absolute perceived-signal threshold. | Higher -> fewer biased trades. | De Bondt & Thaler (1985) |
| `quantity_scale` | float | 5000.0 | `> 0` | medium | Converts perceived signal to quantity. | Higher -> larger orders. | Standardised |
| `max_order` | float | 300.0 | `> 0` | medium | Upper bound on order size. | Higher -> larger maximum impact. | Standardised |

## Worked Numerical Examples

### Case 1 — Positive salience
System state: `return_pct=0.04`, `deviation=0.03`, `price=103`, `cash=10000`, `position=0`.
Calculation: `s=0.70*0.04+0.30*0.03=0.037`; `q=min(300,0.037*5000)=185`; cash clamp gives `97.09`.
Decision: buy `97.09` at `103`.
State update: cash and position update after execution.

### Case 2 — Negative salience
System state: `return_pct=-0.039`, `deviation=-0.02`, `price=98`, `cash=10000`, `position=200`.
Calculation: `s=-0.0333`; `q=166.5`.
Decision: sell `166.5` at `98`.
State update: position decreases after execution.

### Case 3 — Hold
System state: `return_pct=0.01`, `deviation=0.01`, `price=101`, `cash=10000`, `position=100`.
Calculation: `s=0.01`, below threshold.
Decision: hold with quantity `0`.
State update: no portfolio change.

### Edge Case — Missing previous price
System state: `return_pct` unavailable.
Calculation: required input missing.
Decision: hold.
State update: no portfolio change.

## Behavioral Verification and Calibration

**Calibration data sources**:
- `recency_weight` <- Tversky & Kahneman (1973) qualitative salience overweighting, scenario-calibrated.
- `salience_threshold` <- De Bondt & Thaler (1985) overreaction/reversal evidence, scenario-calibrated.

**Expected individual behaviour**:
- Given a large positive recent return, agent MUST buy unless cash-constrained.
- Given a large negative recent return and inventory, agent MUST sell.
- Given small recent return and small deviation, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF `return_pct` is large and the agent always ignores it THEN availability channel is broken.
- IF emitted `quantity > max_order` THEN action constraint is broken.
- IF the agent buys on negative `perceived_signal` THEN direction rule is inverted.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-recency-overweight | `recency_weight = 0.0` | Bias comes from recent-event availability. | decrease | biased volume and peak deviation |
| high-salience-threshold | `salience_threshold = 0.08` | Only very vivid events should trigger. | decrease | activation count |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Tversky, A., & Kahneman, D. (1973). Availability: A heuristic for judging frequency and probability. *Cognitive Psychology*, 5(2), 207-232. https://doi.org/10.1016/0010-0285(73)90033-9 | Core availability mechanism |
| 2 | De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.2307/2327804 | Overreaction and reversal calibration |
| 3 | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | Parent momentum mechanism |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Reviewed by | Codex static three-pass review |
| Created | 2026-07-06 |
| Version | 1.0.0 |
| Change log | 1.0.0 initial fork from momentum-trader for AvailabilityBias |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-recent-event-overweighter.png) |
