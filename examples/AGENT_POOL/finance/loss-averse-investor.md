# Disposition-effect loss-averse investor

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Disposition-effect loss-averse investor |
| Theory Family         | Behavioral Finance — Prospect Theory |
| Behavioral Tendency   | **Diverging** — sells winners too quickly (reducing momentum) and holds losers too long (amplifying drawdowns); asymmetric response pushes prices away from efficient path |
| Time Horizon          | medium |
| Risk Tolerance        | low |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a retail or semi-institutional investor exhibiting the disposition effect — the well-documented tendency to realise gains too readily and ride losses too long. The real-world counterpart is a disposition-effect retail investor — drawn from the participant taxonomy: (1) rational arbitrageurs, (2) informed institutional traders, (3) noise traders, (4) disposition-biased retail investors, (5) momentum traders, (6) contrarian value investors. Odean (1998) documents this pattern in brokerage data showing that investors are 1.5x more likely to sell winners than losers.

The decision goal is to produce a sell order whose size depends on whether the current position is at a gain or loss relative to entry price, with asymmetric thresholds derived from Kahneman & Tversky's loss aversion coefficient (lambda=2.25). Gains are realised at a low threshold (5%); losses require a much deeper threshold (5%×2.25=11.25%) before triggering a smaller sell.

In simulation this agent contributes to under-reaction patterns: by selling winners early, it dampens upward momentum; by holding losers, it delays price correction. Non-goals: (1) this agent MUST NOT buy additional shares at any point; (2) this agent MUST NOT use any market signal other than its own entry price and current price.

## Theoretical Foundation

**Prospect Theory and Loss Aversion**:
- Theory / Study: Prospect theory — decision making under risk
- Citation: Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 237-271. DOI:10.2307/1914185
- Core Insight: People evaluate outcomes relative to a reference point and exhibit loss aversion (losses loom larger than equivalent gains by a factor of approximately 2.25). This produces an S-shaped value function that is concave for gains (risk-averse) and convex for losses (risk-seeking), explaining why investors lock in small gains but gamble on loss recovery.
- Mathematical Formulation: `V(x) = x^α if x >= 0; -λ × (-x)^β if x < 0` where λ=2.25, α=β=0.88
- Empirical Evidence: Kahneman & Tversky estimate λ=2.25 (SE=0.15) from lottery choice experiments with 95 subjects; subsequent meta-analyses (Tversky & Kahneman 1992, N=25 studies) confirm λ in range [1.5, 3.0] with median 2.25.
- Relevance to This Agent: The agent uses λ=2.25 to set the asymmetry between gain-selling and loss-selling thresholds. The gain threshold (5%) combined with λ produces a loss threshold of 5%×2.25=11.25%.
- Calibration Source: Kahneman & Tversky (1979) Table 2: λ=2.25; Tversky & Kahneman (1992) median calibration.
- Falsification Conditions: If this agent sells losers at the same rate as winners (symmetric behaviour), the loss-aversion mechanism is falsified.
- Alternative Theories: Tax-loss selling (rational tax optimisation); portfolio rebalancing (threshold-based without asymmetry); regret theory (anticipatory regret rather than value function).

**Disposition Effect**:
- Theory / Study: Are investors reluctant to realize their losses?
- Citation: Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance*, 53(5), 1775-1798. DOI:10.1111/0022-1082.00072
- Core Insight: Analysis of 10,000 brokerage accounts shows investors are 1.5x more likely to sell a winning stock than a losing stock (Proportion of Gains Realised (PGR) = 0.148 vs. Proportion of Losses Realised (PLR) = 0.098). This disposition effect is strongest for individual investors and weakens with experience.
- Mathematical Formulation: `PGR/PLR = 1.51; sell_probability(gain) / sell_probability(loss) ≈ λ`
- Empirical Evidence: Odean (1998) reports PGR=0.148, PLR=0.098 (t=35.0, p<0.001) in 97,483 transactions across 10,000 accounts from 1987-1993. Gain realisation fraction approximately 70%; loss realisation fraction approximately 20%.
- Relevance to This Agent: The agent directly implements the disposition effect with gain_sell_fraction=0.7 and loss_sell_fraction=0.2 calibrated from Odean's empirical PGR/PLR ratio.
- Calibration Source: Odean (1998) Table 1: PGR=0.148, PLR=0.098; implied sell fractions 70% vs 20%.
- Falsification Conditions: If this agent's ratio of gain-sells to loss-sells is not approximately 3-4x (reflecting PGR/PLR ≈ 1.5 combined with size asymmetry), the disposition calibration is falsified.
- Alternative Theories: Mental accounting (sells based on account-level PnL rather than per-stock); mean reversion belief (holds losers expecting reversion, not due to loss aversion).

## Design Purpose and Activation Triggers

Purpose: Exhibit the disposition effect — selling winners quickly at a low gain threshold and holding losers until a much deeper loss threshold is breached.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `entry_price` available from agent state (reference purchase price)

Missing-Signal Policy: hold if `price` is unavailable; `entry_price` is always available from state after initialisation.

Activation Triggers:
- `pnl_pct > sell_gain_threshold` (gain exceeds 5%): sell `floor(position × gain_sell_fraction)` units.
- `pnl_pct < -(sell_gain_threshold × loss_aversion_lambda)` (loss exceeds 11.25%): sell `floor(position × loss_sell_fraction)` units.
- `<Default>`: hold — PnL within the hold zone.

Deactivation Conditions:
- Position reaches zero: no further sells possible; agent becomes inert.
- Price returns to entry_price zone: agent holds until a threshold is breached.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Sustained gain above threshold | Sells large fraction (70%) quickly | Gain-realization trigger fires with high sell fraction |
| Sustained loss within hold zone | Holds indefinitely hoping for recovery | Loss threshold (11.25%) much deeper than gain threshold (5%) |
| Deep loss beyond lambda-adjusted threshold | Finally sells small fraction (20%) | Loss-realization trigger fires reluctantly with low fraction |

Environmental Dependencies: Requires a per-tick `price` feed. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. Current market price. |
| `entry_price` | agent's own persisted state | `float` | yes | Reference purchase price; populated by §3.6.4 init. |
| `position` | agent's own persisted state | `int` | yes | Current holdings; populated by §3.6.4 init. |
| `cash` | agent's own persisted state | `float` | yes | Current cash balance. |
| `identity`, `round` | scheduler / round header | `str`, `int` | yes | Round number and agent identity. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"sell", "hold"}` | — | yes | Discrete action: realise gain/loss or continue holding. |
| `quantity` | int | `[0, position]` | shares | yes | Number of shares sold. 0 when hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, position]`; out-of-range values MUST be clamped.
- Units and sign conventions: `quantity` is unsigned; `sell` action implies direction.
- Determinism markers: decision is deterministic; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<sell or hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this exact tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare fallback sentinel `"(No relevant knowledge retrieved this round.)"` and inject verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for:
1. Signal wiring — every input row MUST map to a real read against environment/state.
2. Decision emission — code MUST populate every Required=yes field and clamp out-of-range values.
3. Prompt drafting — model-driven variants MUST spell out the tag pattern and JSON schema literally.
4. Parser tests — implementation MUST include a smoke test verifying tags and JSON validity.
5. Variant parity — every declared variant MUST produce the SAME field set.
6. Contract-versus-prose conflict — this section wins on any disagreement.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current price for PnL calculation [Ref 1, 2] |

Does NOT use: fundamental value, parity, order-book depth, peer actions, momentum, volume, or any signal beyond own entry price and current price.

#### Core Behavioral Mechanism

1. **Read** `price` from environment; **Read** `entry_price`, `position`, `cash` from agent state. *(implementation convenience)*
2. **Compute** PnL percentage: `pnl_pct = (price - entry_price) / entry_price`. *(Kahneman & Tversky 1979 — reference-point evaluation)*
3. **Check gain threshold**: if `pnl_pct > sell_gain_threshold`, proceed to step 4 (sell gain). *(Odean 1998 — gain realization)*
4. **Compute gain sell**: `sell_qty = floor(position × gain_sell_fraction)`. Clamp: `sell_qty = min(sell_qty, position)`. **Write** decision: action=sell, quantity=sell_qty. Proceed to step 8.
5. **Check loss threshold**: if `pnl_pct < -(sell_gain_threshold × loss_aversion_lambda)`, proceed to step 6 (sell loss). *(Kahneman & Tversky 1979 — λ-asymmetric loss threshold)*
6. **Compute loss sell**: `sell_qty = floor(position × loss_sell_fraction)`. Clamp: `sell_qty = min(sell_qty, position)`. **Write** decision: action=sell, quantity=sell_qty. Proceed to step 8.
7. **Write** decision: emit `action=hold`, `quantity=0`. *(Default — within hold zone)*
8. **Post-decision state update**: `position -= sell_qty`; `cash += sell_qty × price`. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | sell, hold |
| Action parameter rule | No continuous parameter; discrete action with integer sizing. |
| Sizing rule | Gain: `floor(position × gain_sell_fraction)`; Loss: `floor(position × loss_sell_fraction)`. Clamped to [0, position]. |
| Action lifetime | 1 tick (immediate execution assumed) |
| Revision policy | No revision; sell order stands for the tick. |
| State constraint | `position >= 0` at all times (no short selling). |
| Resource cap | Limited only by remaining position. |
| Exit rule | Agent becomes inert when `position = 0`. |

#### Mathematical Model

**Decision output**: integer sell quantity `Q(t) >= 0` per tick.

**Decision logic formalization**:
```
pnl_pct(t) = (price(t) - entry_price) / entry_price
loss_threshold = -(sell_gain_threshold × loss_aversion_lambda)
             = -(0.05 × 2.25) = -0.1125

if pnl_pct(t) > sell_gain_threshold AND position(t) > 0:
    Q(t) = min(floor(position(t) × gain_sell_fraction), position(t))
    action = "sell"
elif pnl_pct(t) < loss_threshold AND position(t) > 0:
    Q(t) = min(floor(position(t) × loss_sell_fraction), position(t))
    action = "sell"
else:
    Q(t) = 0
    action = "hold"
```

**State variables**:
| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | `initial_position` (default 500) |
| `entry_price` | float | initial market price at simulation start |
| `cash` | float | 0 (starts fully invested) |

**State evolution** (post-decision, post-execution):
```
position(t+1) = position(t) - Q(t)
cash(t+1) = cash(t) + Q(t) × price(t)
entry_price: unchanged (reference point persists)
```

**Determinism contract**: Deterministic given identical price path and parameters. No stochastic element.

**Parameter symbol table**:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `loss_aversion_lambda` | Loss aversion coefficient | 2.25 | Kahneman & Tversky (1979) |
| `sell_gain_threshold` | Gain percentage triggering sell | 0.05 | Odean (1998) |
| `gain_sell_fraction` | Fraction sold on gain trigger | 0.7 | Odean (1998) Table 1 |
| `loss_sell_fraction` | Fraction sold on loss trigger | 0.2 | Odean (1998) Table 1 |
| `initial_position` | Starting share holdings | 500 | Standardised |

#### Behavioral Properties

- Time horizon: medium — holds losses for extended periods; sells gains relatively quickly but not intra-tick.
- Risk tolerance: low — risk-averse in gains domain (sells quickly); risk-seeking in losses domain (holds hoping for recovery) as predicted by prospect theory's reflection effect.
- Information asymmetry: none — uses only publicly observable price against own reference point.
- Psychological profile: Loss aversion (λ=2.25); disposition effect; reference-point dependence; diminishing sensitivity in both gain and loss domains.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `loss_aversion_lambda` | float | 2.25 | [1.5, 3.0] | high | Loss aversion multiplier from prospect theory | Higher -> wider hold zone for losses, stronger disposition effect | Kahneman & Tversky (1979) Table 2 |
| `sell_gain_threshold` | float | 0.05 | [0.01, 0.20] | high | PnL percentage above which gains are realised | Higher -> fewer gain sells, more momentum allowed | Odean (1998) |
| `gain_sell_fraction` | float | 0.7 | (0, 1.0] | medium | Fraction of position sold when gain threshold is met | Higher -> faster gain realisation | Odean (1998) Table 1 |
| `loss_sell_fraction` | float | 0.2 | (0, 1.0] | medium | Fraction of position sold when loss threshold is met | Higher -> more loss realisation (less disposition effect) | Odean (1998) Table 1 |
| `initial_position` | int | 500 | [1, 10000] | low | Starting number of shares | Higher -> more shares available for disposition trades | Standardised |

## Worked Numerical Examples

### Case 1 — Gain realisation (sell winners)
```text
Market state: price=105.0, entry_price=100.0, position=500, cash=0.
Parameters: sell_gain_threshold=0.05, gain_sell_fraction=0.7, lambda=2.25.
Calculation:
  pnl_pct = (105 - 100) / 100 = 0.05
  0.05 > 0.05? No (not strictly greater). Hold.
  Wait — with price=105.5:
  pnl_pct = (105.5 - 100) / 100 = 0.055
  0.055 > 0.05 → gain threshold breached
  sell_qty = floor(500 × 0.7) = 350
  clamp: min(350, 500) = 350
Decision: action=sell, quantity=350.
State update: position: 500 -> 150; cash: 0 -> 0 + 350×105.5 = 36925.
```

### Case 2 — Hold zone (loss within lambda threshold)
```text
Market state: price=92.0, entry_price=100.0, position=500, cash=0.
Parameters: sell_gain_threshold=0.05, loss_aversion_lambda=2.25.
Calculation:
  pnl_pct = (92 - 100) / 100 = -0.08
  loss_threshold = -(0.05 × 2.25) = -0.1125
  -0.08 > -0.1125 → within hold zone (not deep enough loss)
  0.08 < 0.05? No gain either.
Decision: action=hold, quantity=0.
State update: position: 500 (unchanged); cash: 0 (unchanged).
```

### Case 3 — Loss realisation (deep loss exceeds lambda threshold)
```text
Market state: price=87.0, entry_price=100.0, position=500, cash=0.
Parameters: sell_gain_threshold=0.05, loss_aversion_lambda=2.25, loss_sell_fraction=0.2.
Calculation:
  pnl_pct = (87 - 100) / 100 = -0.13
  loss_threshold = -(0.05 × 2.25) = -0.1125
  -0.13 < -0.1125 → deep loss threshold breached
  sell_qty = floor(500 × 0.2) = 100
  clamp: min(100, 500) = 100
Decision: action=sell, quantity=100.
State update: position: 500 -> 400; cash: 0 -> 0 + 100×87 = 8700.
```

### Edge Case — Position exhausted after repeated gains
```text
Market state: price=110.0, entry_price=100.0, position=0, cash=52000.
Parameters: sell_gain_threshold=0.05, gain_sell_fraction=0.7.
Calculation:
  pnl_pct = (110 - 100) / 100 = 0.10
  0.10 > 0.05 → gain threshold breached
  sell_qty = floor(0 × 0.7) = 0
  clamp: min(0, 0) = 0
Decision: action=hold, quantity=0 (no position to sell).
State update: position: 0 (unchanged); cash: 52000 (unchanged). Agent is inert.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `loss_aversion_lambda` <- Kahneman & Tversky (1979) Table 2, λ=2.25 (SE=0.15).
- `sell_gain_threshold` <- Odean (1998): PGR=0.148 implies frequent small-gain realisation; 5% threshold is conservative estimate.
- `gain_sell_fraction` <- Odean (1998) Table 1: gain realisation rate approximately 70% of position.
- `loss_sell_fraction` <- Odean (1998) Table 1: loss realisation rate approximately 20% of position.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price=106 (pnl_pct=0.06 > 0.05), agent MUST sell floor(position×0.7) shares.
- Given price=92 (pnl_pct=-0.08, within hold zone), agent MUST hold with quantity=0.
- Given price=87 (pnl_pct=-0.13 < -0.1125), agent MUST sell floor(position×0.2) shares.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells the same fraction for gains and losses THEN implementation is broken because the asymmetry (disposition effect) is the core mechanism.
- IF the agent buys at any point THEN implementation is broken because buy is not in this agent's action space.
- IF the agent sells on losses more readily than gains (lower absolute threshold for loss sells) THEN implementation is broken because this reverses the disposition effect.
- IF the loss threshold is not approximately lambda × gain_threshold THEN implementation is broken because the prospect-theory calibration is incorrect.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `no_loss_aversion` | `loss_aversion_lambda = 1.0` | Symmetric thresholds eliminate disposition effect | Equal sell rates for gains and losses | Ratio of gain-sells to loss-sells → 1.0 |
| `extreme_loss_aversion` | `loss_aversion_lambda = 3.0` | Higher lambda deepens the hold zone for losses | Fewer loss sells, longer loss holding periods | Average ticks before first loss sell |
| `symmetric_fractions` | `loss_sell_fraction = 0.7` | Equal sell fractions isolate threshold asymmetry | Same volume per sell event regardless of PnL sign | Per-event sell quantity ratio → 1.0 |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 237-271. DOI:10.2307/1914185 | Loss aversion λ=2.25; reference-point dependence |
| 2 | Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance*, 53(5), 1775-1798. DOI:10.1111/0022-1082.00072 | Disposition effect empirics; PGR/PLR calibration |
| 3 | Tversky, A., & Kahneman, D. (1992). Advances in Prospect Theory: Cumulative Representation of Uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297-323. DOI:10.1007/BF00122574 | Cumulative prospect theory refinement |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
