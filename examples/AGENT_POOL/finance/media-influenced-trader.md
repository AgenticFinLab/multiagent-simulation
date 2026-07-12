# Media-influenced trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Media-influenced trader |
| Theory Family         | Behavioral Finance / Media Sentiment |
| Market Role           | **Destabilising** - amplifies public narratives into directional trading |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a retail or discretionary trader whose belief formation is shaped by repeated public narratives, headlines, and social amplification. The real-world counterpart is an attention-sensitive investor who treats heavily publicized information as more likely or more important than a low-coverage base-rate signal.

The decision goal is to emit one bounded buy, sell, or hold order based on a media-amplified deviation signal. It forks the broad information-trader family but uses public salience instead of private liquidation or informed-flow signals.

Inside a market simulation this agent increases order flow when an objective deviation is made vivid by coverage or social repetition. Non-goals: it must not possess private information, must not infer hidden order flow, and must not trade on a pure fundamental model.

## Theoretical Foundation

**Ease of retrieval and media salience**:
- Theory / Study: Ease of retrieval as information; media content and investor sentiment.
- Citation: Schwarz, N., Bless, H., Strack, F., Klumpp, G., Rittenauer-Schatka, H., & Simons, A. (1991). Ease of retrieval as information. *Journal of Personality and Social Psychology*, 61(2), 195-202. https://doi.org/10.1037/0022-3514.61.2.195; Tetlock, P. C. (2007). Giving content to investor sentiment. *Journal of Finance*, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
- Core Insight: Information that is easy to retrieve because it is repeated or vivid is judged as more diagnostic. Market media can therefore create temporary price pressure followed by reversal.
- Mathematical Formulation: `amplified_signal = media_weight * deviation * social_amplification`.
- Empirical Evidence: Tetlock (2007) links media pessimism to short-horizon return pressure and reversal.
- Relevance to This Agent: The agent transforms public deviation into a stronger subjective signal when media salience is high.
- Calibration Source: Tetlock (2007); Schwarz et al. (1991).
- Falsification Conditions: If the agent's trading intensity is unchanged by `media_weight` or `social_amplification`, the media-salience mechanism is absent.
- Alternative Theories: private information trading; liquidity provision; fundamental analysis.

**Investor sentiment**:
- Theory / Study: Investor sentiment in the stock market.
- Citation: Baker, M., & Wurgler, J. (2007). Investor sentiment in the stock market. *Journal of Economic Perspectives*, 21(2), 129-151. https://doi.org/10.1257/jep.21.2.129
- Core Insight: Sentiment can produce measurable mispricing when attention and limits to arbitrage prevent immediate correction.
- Mathematical Formulation: `sentiment_pressure = sign(deviation) * abs(amplified_signal)`.
- Empirical Evidence: Sentiment proxies forecast cross-sectional return patterns, especially in harder-to-arbitrage stocks.
- Relevance to This Agent: The agent supplies the sentiment-sensitive demand channel.
- Calibration Source: Baker & Wurgler (2007).
- Falsification Conditions: If media-sensitive trading never contributes to biased volume, the sentiment channel is inactive.
- Alternative Theories: rational public-information processing.

## Design Purpose and Activation Triggers

Purpose: Convert repeated public narratives and headline salience into bounded directional order flow.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `deviation` available
- `return_pct` available
- `news_salience` or scenario-level salience proxy available

Missing-Signal Policy: hold if price or deviation is missing; use neutral salience only if the scenario explicitly declares no media proxy.

Activation Triggers:
- `amplified_signal > media_threshold`: submit buy order.
- `amplified_signal < -media_threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- Cash floor breached: hibernate buy side.
- Inventory cap reached: hibernate sell side.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Low coverage | Mixed | Media multiplier stays below threshold. |
| High coverage / narrative episode | Destabilising | Public repetition magnifies perceived event probability. |

Environmental Dependencies: requires market broadcast fields and a public salience proxy; no private information feed.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment broadcast | `float` | yes | execution reference |
| `deviation` | environment broadcast | `float` | yes | objective signal being amplified |
| `return_pct` | environment broadcast | `float` | yes | narrative context |
| `news_salience` | environment or scenario proxy | `float` | no | defaults only if declared by scenario |
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

Every output must carry the required fields, no undeclared fields may be emitted, and `quantity` must be non-negative and bounded.

##### Serialization Format

Every implementation variant serializes decisions as `<analysis>...</analysis><decision>{"action":"buy|sell|hold","bid_price":100.0,"quantity":0.0,"reasoning":"..."}</decision>`. Retrieval-augmented variants use `"(No relevant knowledge retrieved this round.)"` when retrieval is empty.

##### Implementer Contract Reminder

Implementation must map all inputs to real environment/state reads, keep the same output schema across variants, and treat invalid or missing required data as a design error rather than silently substituting a trade.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `deviation` | Continuous | 1 tick | Objective price-fundamental gap made salient by narratives. |
| `return_pct` | Continuous | 1 tick | Recent return context for public attention. |
| `news_salience` | Continuous | 1 tick | Public salience or coverage proxy when available. |
| `price` | Continuous | 1 tick | Execution reference. |
| `cash` | State | persistent | Buy constraint. |
| `position` | State | persistent | Sell constraint. |

Does NOT use: private liquidation signals, insider information, order book depth, peer-network topology.

#### Core Behavioral Mechanism

1. Read `deviation`, `return_pct`, `news_salience`, `price`, `cash`, and `position`.
2. Set `salience_multiplier = social_amplification` when coverage is high, otherwise use the scenario-declared neutral multiplier.
3. Compute `amplified_signal = media_weight * deviation * salience_multiplier`.
4. If `abs(amplified_signal) <= media_threshold`, emit hold.
5. If `amplified_signal > media_threshold`, compute buy quantity.
6. If `amplified_signal < -media_threshold`, compute sell quantity.
7. Compute `quantity = min(max_order, abs(amplified_signal) * quantity_scale)` and apply portfolio clamps.
8. Emit the order with reasoning that names media or narrative salience.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | `buy`, `sell`, `hold` |
| Action parameter rule | `bid_price = price` |
| Sizing rule | `quantity = min(max_order, abs(amplified_signal) * quantity_scale)` then portfolio clamp |
| Action lifetime | one decision interval |
| Revision policy | replaces prior intent each tick |
| State constraint | `position >= 0` unless scenario explicitly permits shorts |
| Resource cap | buy quantity cannot exceed `cash / price` |
| Exit rule | hold when amplified signal is inside threshold or required signals are unavailable |

#### Mathematical Model

Decision output is `(action, bid_price, quantity)`.

`m_t = media_weight * deviation_t * social_amplification_t`

If `m_t > theta_m`, action is buy. If `m_t < -theta_m`, action is sell. Otherwise action is hold. Quantity is `q_t = min(q_max, |m_t| * k_q)` and then clamped by cash or position.

State variables: `cash` and `position`, updated after execution. Determinism contract: deterministic given identical inputs and declared salience state.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `media_weight` | weight on narrative-amplified deviation | 0.80 | Tetlock (2007) |
| `social_amplification` | public repetition multiplier | 1.50 | Schwarz et al. (1991) |
| `theta_m` | media threshold | 0.03 | Tetlock (2007) |
| `k_q` | quantity scale | 5000.0 | scenario normalization |
| `q_max` | max order | 300.0 | scenario normalization |

#### Behavioral Properties

- Time horizon: short, because public narratives are evaluated each tick.
- Risk tolerance: high, because the agent trades on salience-amplified perceptions.
- Information asymmetry: none, because media signals are public.
- Psychological profile: narrative-sensitive, attention-driven, prone to public-salience overreaction.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `media_weight` | float | 0.80 | `[0, 1]` | high | Weight on media-highlighted deviation. | Higher -> stronger narrative-driven trading. | Tetlock (2007) |
| `social_amplification` | float | 1.50 | `[1, 3]` | high | Multiplier for repeated public salience. | Higher -> larger perceived signal. | Schwarz et al. (1991) |
| `media_threshold` | float | 0.03 | `[0, 0.20]` | high | Absolute threshold for media-driven action. | Higher -> fewer trades. | Tetlock (2007) |
| `quantity_scale` | float | 5000.0 | `> 0` | medium | Converts amplified signal to quantity. | Higher -> larger orders. | Standardised |
| `max_order` | float | 300.0 | `> 0` | medium | Upper bound on order size. | Higher -> larger maximum impact. | Standardised |

## Worked Numerical Examples

### Case 1 — Positive media salience
System state: `deviation=0.04`, `social_amplification=1.50`, `price=104`, `cash=10000`, `position=0`.
Calculation: `m=0.80*0.04*1.50=0.048`; `q=min(300,0.048*5000)=240`; cash clamp gives `96.15`.
Decision: buy `96.15` at `104`.
State update: cash and position update after execution.

### Case 2 — Negative media salience
System state: `deviation=-0.04`, `social_amplification=1.50`, `price=96`, `cash=10000`, `position=200`.
Calculation: `m=-0.048`; `q=240`, position clamp gives `200`.
Decision: sell `200` at `96`.
State update: position decreases after execution.

### Case 3 — Hold
System state: `deviation=0.01`, `social_amplification=1.50`, `price=101`.
Calculation: `m=0.012`, below threshold.
Decision: hold with quantity `0`.
State update: no portfolio change.

### Edge Case — Missing deviation
System state: `deviation` unavailable.
Calculation: required input missing.
Decision: hold or raise according to scenario missing-signal policy.
State update: no portfolio change.

## Behavioral Verification and Calibration

**Calibration data sources**:
- `media_weight` <- Tetlock (2007) media sentiment evidence.
- `social_amplification` <- Schwarz et al. (1991) ease-of-retrieval evidence.

**Expected individual behaviour**:
- Given high positive amplified signal, agent MUST buy unless cash-constrained.
- Given high negative amplified signal and inventory, agent MUST sell.
- Given low amplified signal, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF changing `media_weight` has no effect on quantity THEN media channel is broken.
- IF emitted `quantity > max_order` THEN action constraint is broken.
- IF the agent claims private information in reasoning THEN the design is contaminated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| no-media-amplification | `social_amplification = 1.0` | Public repetition drives excess trading. | decrease | media-channel volume |
| high-media-threshold | `media_threshold = 0.08` | Only highly salient narratives trigger orders. | decrease | activation count |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Schwarz, N., Bless, H., Strack, F., Klumpp, G., Rittenauer-Schatka, H., & Simons, A. (1991). Ease of retrieval as information. *Journal of Personality and Social Psychology*, 61(2), 195-202. https://doi.org/10.1037/0022-3514.61.2.195 | Ease-of-retrieval mechanism |
| 2 | Tetlock, P. C. (2007). Giving content to investor sentiment. *Journal of Finance*, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x | Media sentiment calibration |
| 3 | Baker, M., & Wurgler, J. (2007). Investor sentiment in the stock market. *Journal of Economic Perspectives*, 21(2), 129-151. https://doi.org/10.1257/jep.21.2.129 | Sentiment and mispricing |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Reviewed by | Codex static three-pass review |
| Created | 2026-07-06 |
| Version | 1.0.0 |
| Change log | 1.0.0 initial fork from information-trader for AvailabilityBias |
| Status | experimental |
| Icon        | ![](../agent_images/icons/finance-media-influenced-trader.png) |
