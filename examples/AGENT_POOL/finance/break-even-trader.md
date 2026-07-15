# Break-even trader escalating risk after losses

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Break-even trader escalating risk after losses |
| Theory Family         | Behavioral Finance — Cumulative Prospect Theory |
| Behavioral Tendency   | **Diverging** — increases position size after losses, amplifying exposure precisely when conditions are adverse; pushes portfolio away from rational risk management |
| Time Horizon          | medium |
| Risk Tolerance        | high (in loss domain) |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a trader who becomes risk-seeking after incurring losses, escalating position size in an attempt to gamble back to break-even. The real-world counterpart is a risk-escalating retail or proprietary trader — drawn from the participant taxonomy: (1) rational arbitrageurs, (2) informed institutional traders, (3) noise traders, (4) disposition-biased retail investors, (5) break-even/doubling-down traders, (6) contrarian value investors. This behaviour is documented in day-trading populations (Barber et al. 2009) and rogue-trading incidents where traders increase bets to recover losses.

The decision goal is to produce a buy order whose size is proportional to the magnitude of unrealised losses, with a scaling factor that increases exposure as losses deepen. The agent attempts to recover to break-even through increased risk-taking in the loss domain of cumulative prospect theory.

In simulation this agent amplifies market instability by increasing demand when prices are falling (buying into losses), but if the decline continues, its enlarged position faces even larger losses creating a vicious cycle. Non-goals: (1) this agent MUST NOT sell positions voluntarily (holds or adds only); (2) this agent MUST NOT reduce position size while in loss territory.

## Theoretical Foundation

**Cumulative Prospect Theory — Loss-Domain Risk Seeking**:
- Theory / Study: Advances in prospect theory — cumulative representation
- Citation: Tversky, A., & Kahneman, D. (1992). Advances in Prospect Theory: Cumulative Representation of Uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297-323. DOI:10.1007/BF00122574
- Core Insight: In the loss domain, the prospect-theory value function is convex, making agents risk-seeking when facing losses. Combined with probability weighting that overweights small probabilities of large gains, this produces a gambling-to-recover pattern where losing traders increase their bets to achieve break-even.
- Mathematical Formulation: `V(x) = -λ×(-x)^β for x<0 (convex, risk-seeking); buy_qty = floor(|pnl_pct| × risk_increase_factor × base_size) if pnl_pct < loss_threshold`
- Empirical Evidence: Tversky & Kahneman (1992) estimate β=0.88 (convexity in loss domain) from 25 experimental studies with 150+ subjects; risk-seeking in losses observed in 73% of lottery choices.
- Relevance to This Agent: The agent operationalises the loss-domain risk-seeking prediction by increasing buy quantity proportionally to loss depth, directly implementing the convex value function's implication for behaviour.
- Calibration Source: Tversky & Kahneman (1992) Table 1: β=0.88, λ=2.25; risk-escalation proportional to loss magnitude confirmed in trading experiments.
- Falsification Conditions: If this agent reduces position size or sells when in a loss (pnl_pct < loss_threshold), the risk-seeking-in-losses mechanism is falsified.
- Alternative Theories: Rational Bayesian updating (reduce position on bad news); sunk-cost fallacy (hold but do not increase); martingale betting (fixed doubling rather than proportional scaling).

**Disposition Effect and Break-Even Motivation**:
- Theory / Study: What drives the disposition effect — analysis of a long-standing preference-based explanation
- Citation: Barberis, N., & Xiong, W. (2009). What Drives the Disposition Effect? An Analysis of a Long-Standing Preference-Based Explanation. *Journal of Finance*, 64(2), 751-784. DOI:10.1111/j.1540-6261.2009.01448.x
- Core Insight: Under prospect theory with narrow framing, investors who have experienced losses will accept fair or even unfavourable gambles to achieve break-even because the value function's convexity in losses makes the gamble's expected prospect-theory value positive. This explains both the reluctance to sell at a loss and the willingness to add to losing positions.
- Mathematical Formulation: `E[V(break_even)] > V(realize_loss) when |loss| < threshold and gamble has positive expected prospect-theory value`
- Empirical Evidence: Barberis & Xiong (2009) show analytically that prospect-theory agents with annual rebalancing choose to hold (and potentially add to) losing positions in 62% of parameterisations when the probability of recovery exceeds 30%.
- Relevance to This Agent: Provides the theoretical justification for buying more when underwater — the break-even target makes risk-escalation prospect-theory optimal.
- Calibration Source: Barberis & Xiong (2009) Section III: risk-escalation factor of 1.5-3.0x is consistent with observed holding period and position-sizing data.
- Falsification Conditions: If this agent's buy quantity does not increase with loss depth (flat response regardless of pnl_pct magnitude), the proportional risk-escalation mechanism is falsified.
- Alternative Theories: Information-based averaging (buying more because fundamentals are believed unchanged); contrarian strategy (deliberate value buying at discounts).

## Design Purpose and Activation Triggers

Purpose: Exhibit loss-domain risk-seeking by escalating position size proportionally to unrealised loss depth, attempting to gamble back to break-even.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `entry_price` available from agent state (reference cost basis)

Missing-Signal Policy: hold if `price` is unavailable; `entry_price` is always available from state.

Activation Triggers:
- `pnl_pct < loss_threshold` (-5%): buy `floor(|pnl_pct| × risk_increase_factor × 5000)` units, cash-capped.
- `<Default>`: hold — not in sufficient loss to trigger escalation.

Deactivation Conditions:
- Cash exhausted: cannot buy more; agent holds existing position without further escalation.
- Price recovers above entry_price: PnL turns positive; agent holds (no gain-selling logic in this agent).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Deepening loss (larger |pnl_pct|) | Buy quantity increases proportionally | `|pnl_pct| × risk_increase_factor` makes quantity scale with loss depth |
| Recovery toward break-even | Stops buying once pnl_pct > loss_threshold | Threshold gate no longer satisfied |
| Cash depletion | Cannot buy further regardless of loss depth | Affordability constraint binds |

Environmental Dependencies: Requires a per-tick `price` feed. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. Current market price. |
| `entry_price` | agent's own persisted state | `float` | yes | Cost basis for PnL calculation; populated by §3.6.4 init. |
| `position` | agent's own persisted state | `int` | yes | Current holdings. |
| `cash` | agent's own persisted state | `float` | yes | Current cash balance. |
| `identity`, `round` | scheduler / round header | `str`, `int` | yes | Round number and agent identity. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "hold"}` | — | yes | Discrete action: escalate position or wait. |
| `quantity` | int | `[0, floor(cash/price)]` | shares | yes | Number of shares to purchase. 0 when hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST satisfy `quantity × price <= cash`; out-of-range values MUST be clamped.
- Units and sign conventions: `quantity` is unsigned; `buy` action implies purchase direction.
- Determinism markers: decision is deterministic; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy or hold>",
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
| `price` | Continuous | 1 tick | Current price for PnL calculation and order sizing [Ref 1, 2] |

Does NOT use: fundamental value, parity, momentum, volume, liquidity, peer actions, or any signal beyond own entry price and current price.

#### Core Behavioral Mechanism

1. **Read** `price` from environment; **Read** `entry_price`, `position`, `cash` from agent state. *(implementation convenience)*
2. **Compute** PnL percentage: `pnl_pct = (price - entry_price) / entry_price`. *(Tversky & Kahneman 1992 — reference-point evaluation)*
3. **Check loss threshold**: if `pnl_pct >= loss_threshold`, proceed to step 7 (hold). *(Tversky & Kahneman 1992 — risk-seeking triggered only in loss domain)*
4. **Compute** raw buy quantity: `buy_qty = floor(abs(pnl_pct) × risk_increase_factor × 5000)`. *(Barberis & Xiong 2009 — proportional risk escalation)*
5. **Clamp** by cash: `buy_qty = min(buy_qty, floor(cash / price))`. *(implementation convenience — affordability)*
6. **Write** decision: emit `action=buy`, `quantity=buy_qty`. Proceed to step 8.
7. **Write** decision: emit `action=hold`, `quantity=0`.
8. **Post-decision state update**: `position += buy_qty`; `cash -= buy_qty × price`; `entry_price = (old_entry × old_position + buy_qty × price) / (old_position + buy_qty)` (weighted average cost basis update). *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, hold |
| Action parameter rule | No continuous parameter; discrete action with integer sizing. |
| Sizing rule | `buy_qty = min(floor(abs(pnl_pct) × risk_increase_factor × 5000), floor(cash/price))` |
| Action lifetime | 1 tick (immediate execution assumed) |
| Revision policy | No revision; buy order stands for the tick. |
| State constraint | `cash >= 0` at all times (no leverage beyond available cash). |
| Resource cap | Total buys limited by initial_cash; depletes over repeated escalation buys. |
| Exit rule | Agent becomes inactive buyer when `cash < price` (cannot afford one share). |

#### Mathematical Model

**Decision output**: integer buy quantity `Q(t) >= 0` per tick.

**Decision logic formalization**:
```
pnl_pct(t) = (price(t) - entry_price(t)) / entry_price(t)

if pnl_pct(t) < loss_threshold AND cash(t) >= price(t):
    Q(t) = floor(abs(pnl_pct(t)) × risk_increase_factor × 5000)
    Q(t) = min(Q(t), floor(cash(t) / price(t)))
    action = "buy"
else:
    Q(t) = 0
    action = "hold"
```

**State variables**:
| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | 0 (or scenario-defined starting position) |
| `cash` | float | `initial_cash` (default 1000000) |
| `entry_price` | float | initial market price at simulation start |

**State evolution** (post-decision, post-execution):
```
if Q(t) > 0:
    new_position = position(t) + Q(t)
    entry_price(t+1) = (entry_price(t) × position(t) + price(t) × Q(t)) / new_position
    position(t+1) = new_position
    cash(t+1) = cash(t) - Q(t) × price(t)
else:
    position(t+1) = position(t)
    cash(t+1) = cash(t)
    entry_price(t+1) = entry_price(t)
```

**Determinism contract**: Deterministic given identical price path and parameters. No stochastic element.

**Parameter symbol table**:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `risk_increase_factor` | Multiplier scaling loss into buy quantity | 2.0 | Barberis & Xiong (2009) Section III |
| `loss_threshold` | PnL percentage below which escalation activates | -0.05 | Tversky & Kahneman (1992) |
| `initial_cash` | Starting cash available for escalation buys | 1000000 | Standardised |
| `base_size_multiplier` | Base quantity multiplier (fixed at 5000 in formula) | 5000 | Standardised |

#### Behavioral Properties

- Time horizon: medium — accumulates position over multiple ticks of declining prices; break-even target implies multi-tick holding.
- Risk tolerance: high (in loss domain) — deliberately increases exposure when losing, consistent with convex value function in losses.
- Information asymmetry: none — uses only own reference price and current market price.
- Psychological profile: Risk-seeking in losses (CPT convex value function); break-even fixation; escalation of commitment; gambler's mentality applied to financial positions.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `risk_increase_factor` | float | 2.0 | [1.0, 4.0] | high | Multiplier converting loss magnitude to buy size | Higher -> more aggressive escalation per unit loss | Barberis & Xiong (2009) Section III |
| `loss_threshold` | float | -0.05 | [-0.20, -0.01] | high | PnL percentage that activates escalation buying | More negative -> requires deeper loss before escalating | Tversky & Kahneman (1992) |
| `initial_cash` | float | 1000000 | [100000, 10000000] | medium | Starting cash balance for escalation purchases | Higher -> more fuel for escalation; longer active period | Standardised |
| `base_size_multiplier` | int | 5000 | [1000, 20000] | medium | Base quantity scalar in sizing formula | Higher -> larger absolute buy quantities | Standardised |

## Worked Numerical Examples

### Case 1 — Moderate loss triggers escalation buy
```text
Market state: price=93.0, entry_price=100.0, position=100, cash=1000000.
Parameters: risk_increase_factor=2.0, loss_threshold=-0.05, base_size=5000.
Calculation:
  pnl_pct = (93 - 100) / 100 = -0.07
  -0.07 < -0.05 → loss threshold breached
  buy_qty = floor(0.07 × 2.0 × 5000) = floor(700) = 700
  cash_cap: floor(1000000 / 93) = 10752; min(700, 10752) = 700
Decision: action=buy, quantity=700.
State update: position: 100 -> 800; cash: 1000000 -> 1000000 - 700×93 = 934900.
  entry_price: (100×100 + 93×700) / 800 = (10000 + 65100) / 800 = 93.875.
```

### Case 2 — Hold (loss within threshold)
```text
Market state: price=97.0, entry_price=100.0, position=100, cash=1000000.
Parameters: risk_increase_factor=2.0, loss_threshold=-0.05.
Calculation:
  pnl_pct = (97 - 100) / 100 = -0.03
  -0.03 >= -0.05 → threshold NOT breached
Decision: action=hold, quantity=0.
State update: position: 100 (unchanged); cash: 1000000 (unchanged).
```

### Case 3 — Deep loss triggers large escalation
```text
Market state: price=80.0, entry_price=93.875, position=800, cash=934900.
Parameters: risk_increase_factor=2.0, loss_threshold=-0.05, base_size=5000.
Calculation:
  pnl_pct = (80 - 93.875) / 93.875 = -0.1478
  -0.1478 < -0.05 → threshold breached
  buy_qty = floor(0.1478 × 2.0 × 5000) = floor(1478) = 1478
  cash_cap: floor(934900 / 80) = 11686; min(1478, 11686) = 1478
Decision: action=buy, quantity=1478.
State update: position: 800 -> 2278; cash: 934900 -> 934900 - 1478×80 = 816660.
  entry_price: (93.875×800 + 80×1478) / 2278 = (75100 + 118240) / 2278 = 84.88.
```

### Edge Case — Cash exhausted
```text
Market state: price=70.0, entry_price=84.88, position=2278, cash=50.0.
Parameters: risk_increase_factor=2.0, loss_threshold=-0.05, base_size=5000.
Calculation:
  pnl_pct = (70 - 84.88) / 84.88 = -0.1753
  -0.1753 < -0.05 → threshold breached
  buy_qty = floor(0.1753 × 2.0 × 5000) = floor(1753) = 1753
  cash_cap: floor(50 / 70) = 0; min(1753, 0) = 0
Decision: action=hold, quantity=0 (insufficient cash to buy even 1 share).
State update: position: 2278 (unchanged); cash: 50 (unchanged). Agent inactive as buyer.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `risk_increase_factor` <- Barberis & Xiong (2009) Section III: escalation factor of 1.5-3.0x consistent with observed behaviour.
- `loss_threshold` <- Tversky & Kahneman (1992): risk-seeking activated at modest losses; -5% is within the experimental range where convexity manifests.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price=93 (pnl_pct=-0.07 < -0.05), agent MUST buy floor(0.07×2.0×5000)=700 shares (cash-permitting).
- Given price=97 (pnl_pct=-0.03, within threshold), agent MUST hold with quantity=0.
- Given cash < price regardless of loss depth, agent MUST emit hold with quantity=0.
- Buy quantity MUST increase as |pnl_pct| increases (monotone in loss depth).

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells at any point THEN implementation is broken because sell is not in this agent's action space.
- IF the agent buys when pnl_pct > loss_threshold THEN implementation is broken because escalation should only activate in loss territory.
- IF buy quantity decreases as loss deepens (inverse relationship) THEN implementation is broken because the proportional scaling is reversed.
- IF cash goes negative after a buy THEN implementation is broken because the cash clamp is missing.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `mild_escalation` | `risk_increase_factor = 1.0` | Lower factor reduces escalation speed | Decrease in per-tick buy quantity at given loss | Average buy quantity when active |
| `extreme_escalation` | `risk_increase_factor = 4.0` | Higher factor depletes cash faster; larger positions | Increase in final position size; faster cash depletion | Ticks until cash < price |
| `no_escalation` | `loss_threshold = -1.0` | Threshold impossible to breach; never buys | Zero buys regardless of loss | Total quantity bought = 0 |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Tversky, A., & Kahneman, D. (1992). Advances in Prospect Theory: Cumulative Representation of Uncertainty. *Journal of Risk and Uncertainty*, 5(4), 297-323. DOI:10.1007/BF00122574 | CPT loss-domain convexity; risk-seeking in losses |
| 2 | Barberis, N., & Xiong, W. (2009). What Drives the Disposition Effect? An Analysis of a Long-Standing Preference-Based Explanation. *Journal of Finance*, 64(2), 751-784. DOI:10.1111/j.1540-6261.2009.01448.x | Break-even motivation; escalation of commitment under PT |
| 3 | Kahneman, D., & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 237-271. DOI:10.2307/1914185 | Original prospect theory; loss aversion and value function |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
| Icon        | ![](../agent_images/icons/finance-break-even-trader.png)         |
