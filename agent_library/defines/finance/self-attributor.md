# Self-attributing confidence-reinforcing trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Self-attributing confidence-reinforcing trader |
| Theory Family         | Behavioral Finance (Biased Self-Attribution) |
| Behavioral Tendency   | **Diverging — escalates position size after gains by attributing success to skill, while ignoring losses; amplifies exposure asymmetrically** |
| Time Horizon          | medium |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models an investor who exhibits biased self-attribution: attributing favorable outcomes to personal skill (boosting confidence and position size) while attributing unfavorable outcomes to bad luck (maintaining confidence). The real-world counterpart is an individual investor, active fund manager, or day-trader who escalates bet sizes after winning streaks while failing to reduce exposure after losses. Such behavior is documented in hedge fund flows and retail investor account data.

The decision goal is to output a buy, sell, or hold order with quantity that escalates after profitable positions and reduces moderately after large losses. The agent starts with an initial long position and systematically increases exposure when the market confirms its view (price rises while long), creating an escalating commitment pattern.

In simulation this agent amplifies bubbles by adding to positions during upswings and resisting liquidation during early downswings. It demonstrates how biased self-attribution leads to concentration risk and eventual large losses. Non-goals: (1) the agent MUST NOT trade based on fundamental value analysis; (2) the agent MUST NOT update confidence symmetrically for gains and losses (that would be rational Bayesian updating).

## Theoretical Foundation

**Biased Self-Attribution and Overconfidence Dynamics**:
- Theory / Study: Investor psychology and security market under- and overreactions.
- Citation: Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839-1885. https://doi.org/10.1111/0022-1082.00077
- Core Insight: Biased self-attribution causes investors to increase confidence after confirming signals (gains) and maintain or only slightly decrease confidence after disconfirming signals (losses). This asymmetric updating creates a ratchet effect where confidence grows over time, leading to increasing position sizes and eventual overexposure.
- Mathematical Formulation: `effective_size = base_size × (1 + confidence_boost)` after gains; `effective_size = base_size` after non-extreme losses. Confidence ratchets upward asymmetrically.
- Empirical Evidence: Daniel et al. predict that self-attribution creates momentum in the short run and reversal in the long run. Empirically, Gervais & Odean (2001) show that learning models with self-attribution generate increasing overconfidence with experience; early success leads to 50-100% larger positions than warranted.
- Relevance to This Agent: The agent directly implements the confidence ratchet: after gains (position > 0 AND deviation > 0), it buys more at boosted size. After moderate losses, it holds rather than sells. Only extreme losses trigger partial liquidation.
- Calibration Source: Daniel et al. (1998); confidence_boost=0.5 means a 50% increase in position size after confirming outcomes, calibrated to Gervais & Odean (2001) learning model predictions.
- Falsification Conditions: If the agent reduces position size after gains (position > 0 AND price rise), the self-attribution mechanism is falsified. Confidence MUST ratchet up after gains.
- Alternative Theories: Rational Bayesian updating (symmetric); disposition effect (sells winners too early — opposite); house-money effect (related but not asymmetric attribution).

**Learning, Self-Attribution, and Overconfidence Over Time**:
- Theory / Study: Learning to be overconfident.
- Citation: Gervais, S., & Odean, T. (2001). Learning to be overconfident. *Review of Financial Studies*, 14(1), 1-27. https://doi.org/10.1093/rfs/14.1.1
- Core Insight: Traders learn about their ability through a biased attribution process. Success is attributed to skill (boosting perceived ability) while failure is attributed to noise (preserving perceived ability). Over time, this generates increasing overconfidence even among rational Bayesian updaters if the updating is biased.
- Mathematical Formulation: `confidence(t+1) = confidence(t) + boost × I(gain) - discount × I(loss)` where boost >> discount for biased attributors; in the extreme case discount=0.
- Empirical Evidence: Gervais & Odean show that after 10 successful trades, the median biased-attribution trader has confidence 50-80% higher than warranted; early bull market experience creates persistent overconfidence. Statman, Thorley & Vorkink (2006, RFS) document that market-wide turnover rises following positive returns, consistent with self-attribution at the population level.
- Relevance to This Agent: The agent models the early-experience phase where confirmed gains ratchet confidence upward but losses do not reduce it proportionally. The confidence_boost=0.5 represents the asymmetric update documented in Gervais & Odean's model.
- Calibration Source: Gervais & Odean (2001), Figure 3: confidence inflation of 50% after a sequence of confirming trades; confidence_boost range of [0.2, 1.5] covers moderate to extreme attribution bias.
- Falsification Conditions: If the agent's average position size does not increase over time during a sustained uptrend, the learning-to-be-overconfident mechanism is absent.
- Alternative Theories: Experience-weighted attraction; reinforcement learning without bias; constant-confidence models.

## Design Purpose and Activation Triggers

Purpose: Demonstrate asymmetric confidence updating by escalating positions after gains while resisting liquidation after small losses, creating bubble-amplifying escalation.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `fundamental` available (for computing deviation)

Missing-Signal Policy: If `fundamental` is unavailable, hold. If `price` is unavailable, hold.

Activation Triggers:
- `position > 0 AND deviation > 0` (long AND price rising above fundamental): submit boosted buy order (confidence reinforced).
- `deviation < sell_threshold` (deviation < -0.02): submit sell order (partial liquidation under stress).
- `<Default>`: hold (maintain current position without action).

Deactivation Conditions:
- All cash deployed and position at maximum: hibernate buy side.
- Deviation positive but position=0 and no initial position: hold (no entry signal without existing position).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Confirming market (position>0, deviation>0) | Escalating buy size with confidence boost | Self-attribution: success attributed to skill, position grows |
| Disconfirming market (deviation < sell_threshold) | Partial liquidation at 1.5× base_size | Only extreme losses overcome attribution bias; moderate losses ignored |

Environmental Dependencies: Requires `price` and `fundamental` from environment. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Current market price; maps to §3.6.1. |
| `fundamental` | environment | `float` | yes | True fundamental value; maps to §3.6.1. |
| `position` | agent's own persisted state | `int` | yes | Current net position; from §3.6.4 state. |
| `cash` | agent's own persisted state | `float` | yes | Available cash; from §3.6.4 state. |
| `round` | scheduler / round header | `int` | yes | Current simulation round. |
| `identity` | scheduler / round header | `str` | yes | Agent identity string. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|-------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action selected this call. |
| `quantity` | int | `[0, int(base_size × (1 + confidence_boost))]` | shares | yes | Order magnitude; 0 when action=hold. Max is 600 at default params. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, int(base_size × (1 + confidence_boost))]`; out-of-range values MUST be clamped before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. Buy = increase long position; sell = reduce long position.
- Determinism markers: decision is deterministic given identical inputs and state; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy|sell|hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel: `"(No relevant knowledge retrieved this round.)"` and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution. On conflict with prose elsewhere in this specification, this section wins.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current market price for deviation calculation [Ref 1, 2] |
| `fundamental` | Continuous | 1 tick | Reference for computing deviation [Ref 1] |
| `position` | Discrete | current | Determines whether gains confirm existing view [Ref 1, 2] |
| `cash` | Continuous | current | Required for buy-side feasibility check [Ref 2] |

Does NOT use: `price_history`, moving averages, momentum indicators, peer trades, P&L history (agent uses position+deviation as proxy for gain confirmation).

#### Core Behavioral Mechanism

1. **Read** current `price`, `fundamental`, `position`, and `cash`. *(implementation convenience)*
2. **Compute** `deviation` = (`fundamental` - `price`) / `price`. *(Traces to Daniel et al. 1998 — signal for gain/loss assessment.)*
3. **Evaluate** confirmation: check if `position > 0` AND `deviation > 0`. If true, the market is confirming the agent's long position (price below fundamental means long is justified), triggering self-attribution. *(Traces to Daniel et al. 1998 — biased self-attribution on confirming outcomes.)*
4. **If confirmed** (position > 0 AND deviation > 0): compute boosted quantity: `boosted_qty` = int(`base_size` × (1 + `confidence_boost`)). Set action = buy. *(Traces to Gervais & Odean 2001 — confidence escalation after success.)*
5. **If disconfirming with extreme loss** (`deviation < sell_threshold`): compute liquidation quantity: `sell_qty` = int(`base_size` × 1.5). Set action = sell. Clamp to current position. *(Traces to Daniel et al. 1998 — only extreme disconfirmation overcomes attribution bias.)*
6. **Otherwise** (moderate loss or neutral): action = hold, quantity = 0. The agent ignores moderate losses. *(Traces to Gervais & Odean 2001 — losses attributed to noise, no action.)*
7. **Constrain** buy side: if action = buy, `quantity` = min(`boosted_qty`, floor(`cash` / `price`)). **Write** decision output. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | Market order at current price; no limit price. |
| Sizing rule | Buy: `quantity = int(base_size × (1 + confidence_boost))`. Sell: `quantity = min(int(base_size × 1.5), position)`. |
| Action lifetime | 1 tick (immediate execution or expiry) |
| Revision policy | No revision; each tick produces a fresh independent decision |
| State constraint | No explicit position cap (bounded by cash and base_size formula) |
| Resource cap | Cash >= 0; `initial_cash` = 1,000,000 |
| Exit rule | Partial exit only on extreme loss (deviation < sell_threshold); no voluntary full exit |

#### Mathematical Model

**Decision output:** Unsigned trade quantity `Q(t)` ∈ integers, and discrete action ∈ {buy, sell, hold}.

**Decision logic formalization:**

```
deviation(t) = (V_fundamental - P(t)) / P(t)

IF position(t) > 0 AND deviation(t) > 0:
    action = buy                          [SELF-ATTRIBUTION: confidence boosted]
    Q(t) = int(base_size × (1 + m_conf))
    Q(t) = min(Q(t), floor(cash / P(t)))

ELIF deviation(t) < θ_sell:
    action = sell                         [EXTREME LOSS: partial liquidation]
    Q(t) = min(int(base_size × 1.5), position(t))

ELSE:
    action = hold                         [MODERATE LOSS / NEUTRAL: ignore]
    Q(t) = 0
```

**State variables:**

| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | 200 (initial_position) |
| `cash` | float | 1,000,000 |

**State evolution:**
- Pre-decide: no state updates.
- Post-execution: if buy: `position += Q(t)`, `cash -= Q(t) × price`. If sell: `position -= Q(t)`, `cash += Q(t) × price`.

**Determinism contract:** Deterministic given identical price, fundamental, position, and cash state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `m_conf` | Confidence boost after confirming outcomes | 0.5 | Gervais & Odean (2001) |
| `base_size` | Base trade quantity | 400 | Standardised |
| `θ_sell` | Sell threshold (deviation below which agent liquidates) | -0.02 | Daniel et al. (1998) |
| `initial_position` | Starting long position | 200 | Scenario-dependent |

#### Behavioral Properties

- Time horizon: medium, because the agent accumulates positions over multiple ticks during uptrends and only liquidates under sustained stress.
- Risk tolerance: high, because confidence escalation leads to ever-larger positions without proportional risk reduction.
- Information asymmetry: none; observes the same fundamental and price as other agents.
- Psychological profile: biased self-attribution (gains = skill, losses = luck); asymmetric confidence updating; escalation of commitment; represents the core DHS (1998) attribution mechanism.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `confidence_boost` | float | 0.5 | [0.2, 1.5] | high | Fractional increase in trade size after confirming outcomes. | Higher -> faster position escalation, greater bubble amplification. | Gervais & Odean (2001), Figure 3 |
| `base_size` | int | 400 | [100, 1000] | medium | Base trade quantity before confidence adjustment. | Higher -> larger trades per decision, faster capital deployment. | Standardised |
| `sell_threshold` | float | -0.02 | [-0.10, -0.005] | high | Deviation below which agent partially liquidates. | More negative -> agent tolerates larger losses before selling (more stubborn). | Daniel et al. (1998) |
| `initial_cash` | float | 1000000 | [100000, 10000000] | low | Starting capital. | Higher -> longer escalation runway. | Standardised |
| `initial_position` | int | 200 | [0, 1000] | medium | Starting long position (agent begins invested). | Higher -> earlier exposure to self-attribution loop. | Scenario-dependent |

## Worked Numerical Examples

### Case 1 — Buy with confidence boost (confirming market)
```text
System state: price=95; fundamental=100; position=200; cash=1000000; confidence_boost=0.5; base_size=400; sell_threshold=-0.02.
Calculation:
  deviation = (100 - 95) / 95 = 5/95 = 0.0526
  position=200 > 0 AND deviation=0.0526 > 0: SELF-ATTRIBUTION triggered
  boosted_qty = int(400 × (1 + 0.5)) = int(600) = 600
  cash check: 600 × 95 = 57000 <= 1000000: OK
  quantity = 600
Decision: buy, quantity=600.
State update: position: 200 -> 800; cash: 1000000 -> 943000.
```

### Case 2 — Sell under extreme loss (disconfirming market)
```text
System state: price=105; fundamental=100; position=500; cash=500000; confidence_boost=0.5; base_size=400; sell_threshold=-0.02.
Calculation:
  deviation = (100 - 105) / 105 = -5/105 = -0.0476
  deviation = -0.0476 < sell_threshold = -0.02: PARTIAL LIQUIDATION
  sell_qty = min(int(400 × 1.5), 500) = min(600, 500) = 500
  quantity = 500
Decision: sell, quantity=500.
State update: position: 500 -> 0; cash: 500000 -> 552500.
```

### Case 3 — Hold (moderate loss, attribution bias prevents action)
```text
System state: price=101; fundamental=100; position=300; cash=700000; confidence_boost=0.5; base_size=400; sell_threshold=-0.02.
Calculation:
  deviation = (100 - 101) / 101 = -1/101 = -0.0099
  position=300 > 0 but deviation=-0.0099 < 0: NOT confirming (no buy)
  deviation=-0.0099 > sell_threshold=-0.02: NOT extreme loss (no sell)
  action = hold
  quantity = 0
Decision: hold, quantity=0.
State update: no change. Agent ignores moderate loss (attributes to noise).
```

### Edge Case — Cash exhausted during escalation
```text
System state: price=90; fundamental=100; position=400; cash=30000; confidence_boost=0.5; base_size=400; sell_threshold=-0.02.
Calculation:
  deviation = (100 - 90) / 90 = 10/90 = 0.1111
  position=400 > 0 AND deviation=0.1111 > 0: SELF-ATTRIBUTION triggered
  boosted_qty = int(400 × 1.5) = 600
  cash check: 600 × 90 = 54000 > 30000: constrain
  max affordable = floor(30000 / 90) = 333
  quantity = 333
Decision: buy, quantity=333.
State update: position: 400 -> 733; cash: 30000 -> 30.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `confidence_boost` <- Gervais & Odean (2001), Figure 3: 50% confidence inflation after sequences of confirming trades.
- `sell_threshold` <- Daniel et al. (1998): only extreme disconfirmation (-2% or worse) overcomes self-attribution bias and triggers position reduction.
- `initial_position` <- Scenario-dependent: agent starts invested to create self-attribution context.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given position>0 AND deviation>0 (confirming market), agent MUST buy at boosted size (base_size × 1.5 = 600 shares).
- Given deviation < -0.02 (extreme loss), agent MUST sell at 1.5× base_size clamped to position.
- Given moderate loss (deviation between -0.02 and 0), agent MUST hold (ignore the loss).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells when position>0 AND deviation>0 (confirming market), THEN implementation is broken because self-attribution should trigger buying, not selling.
- IF the agent buys during extreme loss (deviation < sell_threshold), THEN implementation is broken because extreme disconfirmation should trigger liquidation.
- IF the agent's position decreases monotonically during a sustained uptrend, THEN implementation is broken because self-attribution should escalate exposure.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_attribution` | `confidence_boost = 0.0` | Removing attribution bias reduces to flat trading. | Decrease in position escalation and bubble contribution. | Max position reached and buy-side volume. |
| `extreme_attribution` | `confidence_boost = 1.5` | Higher boost accelerates position escalation. | Faster position growth and larger eventual drawdown. | Time to max position and peak-to-trough P&L. |
| `quick_exit` | `sell_threshold = -0.005` | Lower sell threshold makes agent more responsive to losses. | Faster liquidation, less bubble amplification. | Time to full liquidation after regime shift. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839-1885. https://doi.org/10.1111/0022-1082.00077 | Primary theory: biased self-attribution and asymmetric confidence updating. |
| 2 | Gervais, S., & Odean, T. (2001). Learning to be overconfident. *Review of Financial Studies*, 14(1), 1-27. https://doi.org/10.1093/rfs/14.1.1 | Learning model: how self-attribution creates escalating overconfidence. |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon | ![](../agent_images/icons/finance-self-attributor.png) |
